"""Service for managing gym exercise logs."""
from typing import Tuple, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from src.models.gym_exercise import GymExerciseLog, GymExerciseSet
from src.api.schemas.gym_exercise_schemas import (
    GymExerciseLogCreate,
    GymExerciseLogUpdate,
    GymExerciseLogSummary,
)
from src.api.middleware.error_handler import NotFoundException


class GymExerciseService:
    """Service for managing gym exercise logs."""

    def __init__(self, db: AsyncSession):
        """Initialize gym exercise service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_gym_exercise_log(
        self, user_id: UUID, exercise_data: GymExerciseLogCreate
    ) -> GymExerciseLog:
        """Create a new gym exercise log with sets.

        Args:
            user_id: User ID
            exercise_data: Gym exercise log creation data

        Returns:
            Created gym exercise log
        """
        # Create exercise log
        exercise_log = GymExerciseLog(
            user_id=user_id,
            workout_date=exercise_data.workout_date,
            exercise_name=exercise_data.exercise_name,
            notes=exercise_data.notes,
        )

        self.db.add(exercise_log)
        await self.db.flush()  # Flush to get the ID

        # Create sets
        for set_data in exercise_data.sets:
            exercise_set = GymExerciseSet(
                gym_exercise_log_id=exercise_log.id,
                set_number=set_data.set_number,
                reps=set_data.reps,
                weight=set_data.weight,
                notes=set_data.notes,
            )
            self.db.add(exercise_set)

        await self.db.commit()
        await self.db.refresh(exercise_log)

        # Load sets relationship
        result = await self.db.execute(
            select(GymExerciseLog)
            .where(GymExerciseLog.id == exercise_log.id)
            .options(selectinload(GymExerciseLog.sets))
        )
        exercise_log = result.scalar_one()

        return exercise_log

    async def get_gym_exercise_logs(
        self,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[list[GymExerciseLogSummary], int]:
        """Get paginated gym exercise logs for a user with summary data.

        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            page: Page number (1-based)
            page_size: Items per page

        Returns:
            Tuple of (gym exercise logs list with summary, total count)
        """
        # Build query with filters
        query = (
            select(GymExerciseLog)
            .where(GymExerciseLog.user_id == user_id)
            .options(selectinload(GymExerciseLog.sets))
        )

        if start_date:
            query = query.where(GymExerciseLog.workout_date >= start_date)
        if end_date:
            query = query.where(GymExerciseLog.workout_date <= end_date)

        # Order by date descending (most recent first)
        query = query.order_by(desc(GymExerciseLog.workout_date), desc(GymExerciseLog.created_at))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await self.db.execute(query)
        exercise_logs = list(result.scalars().all())

        # Create summary objects
        summaries = []
        for log in exercise_logs:
            total_sets = len(log.sets)
            total_reps = sum(s.reps for s in log.sets)
            total_volume = sum(s.reps * (s.weight or 0) for s in log.sets)

            summaries.append(
                GymExerciseLogSummary(
                    id=log.id,
                    workout_date=log.workout_date,
                    exercise_name=log.exercise_name,
                    total_sets=total_sets,
                    total_reps=total_reps,
                    total_volume=total_volume,
                    created_at=log.created_at,
                )
            )

        return summaries, total_count

    async def get_gym_exercise_log_by_id(
        self, user_id: UUID, exercise_log_id: UUID
    ) -> GymExerciseLog:
        """Get a specific gym exercise log with sets.

        Args:
            user_id: User ID (for ownership verification)
            exercise_log_id: Gym exercise log ID

        Returns:
            Gym exercise log with sets

        Raises:
            NotFoundException: If gym exercise log not found or not owned by user
        """
        result = await self.db.execute(
            select(GymExerciseLog)
            .where(
                and_(
                    GymExerciseLog.id == exercise_log_id,
                    GymExerciseLog.user_id == user_id,
                )
            )
            .options(selectinload(GymExerciseLog.sets))
        )
        exercise_log = result.scalar_one_or_none()

        if exercise_log is None:
            raise NotFoundException("Gym exercise log not found")

        return exercise_log

    async def update_gym_exercise_log(
        self, user_id: UUID, exercise_log_id: UUID, exercise_data: GymExerciseLogUpdate
    ) -> GymExerciseLog:
        """Update a gym exercise log.

        Args:
            user_id: User ID (for ownership verification)
            exercise_log_id: Gym exercise log ID
            exercise_data: Updated gym exercise log data

        Returns:
            Updated gym exercise log

        Raises:
            NotFoundException: If gym exercise log not found or not owned by user
        """
        exercise_log = await self.get_gym_exercise_log_by_id(user_id, exercise_log_id)

        # Update basic fields
        if exercise_data.workout_date is not None:
            exercise_log.workout_date = exercise_data.workout_date
        if exercise_data.exercise_name is not None:
            exercise_log.exercise_name = exercise_data.exercise_name
        if exercise_data.notes is not None:
            exercise_log.notes = exercise_data.notes

        # Update sets if provided
        if exercise_data.sets is not None:
            # Delete existing sets
            for existing_set in exercise_log.sets:
                await self.db.delete(existing_set)
            await self.db.flush()

            # Create new sets
            for set_data in exercise_data.sets:
                exercise_set = GymExerciseSet(
                    gym_exercise_log_id=exercise_log.id,
                    set_number=set_data.set_number,
                    reps=set_data.reps,
                    weight=set_data.weight,
                    notes=set_data.notes,
                )
                self.db.add(exercise_set)

        await self.db.commit()
        await self.db.refresh(exercise_log)

        # Load sets relationship
        result = await self.db.execute(
            select(GymExerciseLog)
            .where(GymExerciseLog.id == exercise_log.id)
            .options(selectinload(GymExerciseLog.sets))
        )
        exercise_log = result.scalar_one()

        return exercise_log

    async def delete_gym_exercise_log(
        self, user_id: UUID, exercise_log_id: UUID
    ) -> None:
        """Delete a gym exercise log.

        Args:
            user_id: User ID (for ownership verification)
            exercise_log_id: Gym exercise log ID

        Raises:
            NotFoundException: If gym exercise log not found or not owned by user
        """
        exercise_log = await self.get_gym_exercise_log_by_id(user_id, exercise_log_id)

        await self.db.delete(exercise_log)
        await self.db.commit()

    async def get_exercise_names(self, user_id: UUID) -> list[str]:
        """Get list of all unique exercise names for a user.

        Args:
            user_id: User ID

        Returns:
            List of unique exercise names sorted alphabetically
        """
        result = await self.db.execute(
            select(GymExerciseLog.exercise_name)
            .where(GymExerciseLog.user_id == user_id)
            .distinct()
            .order_by(GymExerciseLog.exercise_name)
        )
        exercise_names = [name for name in result.scalars().all()]

        return exercise_names

    async def get_exercise_trends(self, user_id: UUID, exercise_name: str) -> dict:
        """Get historical trend data for a specific exercise.

        Args:
            user_id: User ID
            exercise_name: Name of the exercise

        Returns:
            Dictionary containing trend data with dates and metrics
        """
        # Query all logs for this exercise
        result = await self.db.execute(
            select(GymExerciseLog)
            .where(
                and_(
                    GymExerciseLog.user_id == user_id,
                    GymExerciseLog.exercise_name == exercise_name,
                )
            )
            .options(selectinload(GymExerciseLog.sets))
            .order_by(GymExerciseLog.workout_date)
        )
        exercise_logs = list(result.scalars().all())

        # Process data for each workout date
        dates = []
        max_weights = []
        avg_weights = []
        total_reps_list = []

        for log in exercise_logs:
            if not log.sets:
                continue

            date_str = log.workout_date.isoformat()
            dates.append(date_str)

            # Calculate max weight for this session
            weights = [s.weight for s in log.sets if s.weight is not None]
            max_weight = max(weights) if weights else 0
            max_weights.append(max_weight)

            # Calculate average weight for this session
            avg_weight = sum(weights) / len(weights) if weights else 0
            avg_weights.append(round(avg_weight, 1))

            # Calculate total reps for this session
            total_reps = sum(s.reps for s in log.sets)
            total_reps_list.append(total_reps)

        return {
            "exercise_name": exercise_name,
            "dates": dates,
            "max_weights": max_weights,
            "avg_weights": avg_weights,
            "total_reps": total_reps_list,
        }
