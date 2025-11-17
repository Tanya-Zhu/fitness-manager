"""Service for managing workout logs."""
from typing import Tuple, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from src.models.workout_log import WorkoutLog
from src.api.schemas.workout_log_schemas import (
    WorkoutLogCreate,
    WorkoutLogUpdate,
    WorkoutStats,
)
from src.api.middleware.error_handler import NotFoundException


class WorkoutLogService:
    """Service for managing workout logs."""

    def __init__(self, db: AsyncSession):
        """Initialize workout log service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_workout_log(
        self, user_id: UUID, workout_data: WorkoutLogCreate
    ) -> WorkoutLog:
        """Create a new workout log.

        Args:
            user_id: User ID
            workout_data: Workout log creation data

        Returns:
            Created workout log
        """
        workout_log = WorkoutLog(
            user_id=user_id,
            workout_date=workout_data.workout_date,
            workout_name=workout_data.workout_name,
            duration_minutes=workout_data.duration_minutes,
            calories_burned=workout_data.calories_burned,
            notes=workout_data.notes,
        )

        self.db.add(workout_log)
        await self.db.commit()
        await self.db.refresh(workout_log)

        return workout_log

    async def get_workout_logs(
        self,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[list[WorkoutLog], int]:
        """Get paginated workout logs for a user.

        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            page: Page number (1-based)
            page_size: Items per page

        Returns:
            Tuple of (workout logs list, total count)
        """
        # Build query with filters
        query = select(WorkoutLog).where(WorkoutLog.user_id == user_id)

        if start_date:
            query = query.where(WorkoutLog.workout_date >= start_date)
        if end_date:
            query = query.where(WorkoutLog.workout_date <= end_date)

        # Order by date descending (most recent first)
        query = query.order_by(desc(WorkoutLog.workout_date), desc(WorkoutLog.created_at))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await self.db.execute(query)
        workout_logs = list(result.scalars().all())

        return workout_logs, total_count

    async def get_workout_log_by_id(
        self, user_id: UUID, workout_log_id: UUID
    ) -> WorkoutLog:
        """Get a specific workout log.

        Args:
            user_id: User ID (for ownership verification)
            workout_log_id: Workout log ID

        Returns:
            Workout log

        Raises:
            NotFoundException: If workout log not found or not owned by user
        """
        result = await self.db.execute(
            select(WorkoutLog).where(
                and_(
                    WorkoutLog.id == workout_log_id,
                    WorkoutLog.user_id == user_id,
                )
            )
        )
        workout_log = result.scalar_one_or_none()

        if workout_log is None:
            raise NotFoundException("Workout log not found")

        return workout_log

    async def update_workout_log(
        self, user_id: UUID, workout_log_id: UUID, workout_data: WorkoutLogUpdate
    ) -> WorkoutLog:
        """Update a workout log.

        Args:
            user_id: User ID (for ownership verification)
            workout_log_id: Workout log ID
            workout_data: Updated workout log data

        Returns:
            Updated workout log

        Raises:
            NotFoundException: If workout log not found or not owned by user
        """
        workout_log = await self.get_workout_log_by_id(user_id, workout_log_id)

        # Update fields
        update_data = workout_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workout_log, field, value)

        await self.db.commit()
        await self.db.refresh(workout_log)

        return workout_log

    async def delete_workout_log(
        self, user_id: UUID, workout_log_id: UUID
    ) -> None:
        """Delete a workout log.

        Args:
            user_id: User ID (for ownership verification)
            workout_log_id: Workout log ID

        Raises:
            NotFoundException: If workout log not found or not owned by user
        """
        workout_log = await self.get_workout_log_by_id(user_id, workout_log_id)

        await self.db.delete(workout_log)
        await self.db.commit()

    async def get_workout_stats(
        self,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> WorkoutStats:
        """Get workout statistics for a user.

        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Workout statistics
        """
        # Build query with filters
        query = select(
            func.count(WorkoutLog.id).label("total_workouts"),
            func.sum(WorkoutLog.duration_minutes).label("total_duration"),
            func.sum(WorkoutLog.calories_burned).label("total_calories"),
            func.avg(WorkoutLog.duration_minutes).label("avg_duration"),
            func.avg(WorkoutLog.calories_burned).label("avg_calories"),
        ).where(WorkoutLog.user_id == user_id)

        if start_date:
            query = query.where(WorkoutLog.workout_date >= start_date)
        if end_date:
            query = query.where(WorkoutLog.workout_date <= end_date)

        result = await self.db.execute(query)
        row = result.one()

        return WorkoutStats(
            total_workouts=row.total_workouts or 0,
            total_duration_minutes=int(row.total_duration or 0),
            total_calories=float(row.total_calories or 0),
            avg_duration_minutes=float(row.avg_duration or 0),
            avg_calories=float(row.avg_calories or 0),
        )

    async def get_chart_data(
        self, user_id: UUID, period_type: str = "week", limit: int = 12
    ) -> list[dict]:
        """Get aggregated workout data for charts.

        Args:
            user_id: User ID
            period_type: "week" or "month"
            limit: Number of periods to return

        Returns:
            List of aggregated data points
        """
        from sqlalchemy import text

        if period_type == "week":
            # SQLite uses strftime for date formatting
            # %Y-W%W gives year and week number
            query = text("""
                SELECT
                    strftime('%Y-W%W', workout_date) as period,
                    COUNT(*) as workouts,
                    SUM(duration_minutes) as duration_minutes,
                    SUM(COALESCE(calories_burned, 0)) as calories
                FROM workout_log
                WHERE user_id = :user_id
                GROUP BY period
                ORDER BY period DESC
                LIMIT :limit
            """)
        else:  # month
            # %Y-%m gives year and month
            query = text("""
                SELECT
                    strftime('%Y-%m', workout_date) as period,
                    COUNT(*) as workouts,
                    SUM(duration_minutes) as duration_minutes,
                    SUM(COALESCE(calories_burned, 0)) as calories
                FROM workout_log
                WHERE user_id = :user_id
                GROUP BY period
                ORDER BY period DESC
                LIMIT :limit
            """)

        result = await self.db.execute(
            query, {"user_id": str(user_id), "limit": limit}
        )
        rows = result.fetchall()

        # Reverse to show oldest to newest
        data_points = []
        for row in reversed(rows):
            period = row[0]

            # Generate label
            if period_type == "week":
                # Convert "2024-W45" to "Week 45"
                week_num = period.split('-W')[1]
                label = f"第 {week_num} 周"
            else:
                # Convert "2024-11" to "November 2024"
                year, month = period.split('-')
                month_names = {
                    '01': '1月', '02': '2月', '03': '3月', '04': '4月',
                    '05': '5月', '06': '6月', '07': '7月', '08': '8月',
                    '09': '9月', '10': '10月', '11': '11月', '12': '12月'
                }
                label = f"{year}年{month_names[month]}"

            data_points.append({
                "period": period,
                "label": label,
                "workouts": int(row[1] or 0),
                "duration_minutes": int(row[2] or 0),
                "calories": float(row[3] or 0),
            })

        return data_points
