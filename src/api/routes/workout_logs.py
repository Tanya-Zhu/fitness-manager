"""API routes for workout logs."""
from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import math

from src.core.database import get_db
from src.api.middleware.auth import get_current_user
from src.services.workout_log_service import WorkoutLogService
from src.api.schemas.workout_log_schemas import (
    WorkoutLogCreate,
    WorkoutLogUpdate,
    WorkoutLogResponse,
    PaginatedWorkoutLogsResponse,
    PaginationMeta,
    ChartData,
    ChartDataPoint,
)
from src.core.config import settings


router = APIRouter(prefix="/workout-logs", tags=["workout-logs"])


@router.post("/", response_model=WorkoutLogResponse, status_code=status.HTTP_201_CREATED)
async def create_workout_log(
    workout_data: WorkoutLogCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workout log.

    Args:
        workout_data: Workout log creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created workout log
    """
    service = WorkoutLogService(db)
    workout_log = await service.create_workout_log(
        UUID(current_user["user_id"]), workout_data
    )

    return WorkoutLogResponse.model_validate(workout_log)


@router.get("/chart-data", response_model=ChartData)
async def get_workout_chart_data(
    period_type: str = Query("week", regex="^(week|month)$", description="Chart period type"),
    limit: int = Query(12, ge=1, le=24, description="Number of periods"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated workout data for charts.

    Args:
        period_type: "week" or "month"
        limit: Number of periods to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        Chart data with aggregated statistics
    """
    service = WorkoutLogService(db)
    data_points_dict = await service.get_chart_data(
        UUID(current_user["user_id"]), period_type=period_type, limit=limit
    )

    # Convert dict to ChartDataPoint objects
    data_points = [ChartDataPoint(**dp) for dp in data_points_dict]

    return ChartData(data_points=data_points, period_type=period_type)


@router.get("/", response_model=PaginatedWorkoutLogsResponse)
async def list_workout_logs(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Items per page",
    ),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of user's workout logs.

    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        page: Page number (1-based)
        page_size: Number of items per page
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of workout logs with statistics
    """
    service = WorkoutLogService(db)

    # Get workout logs
    workout_logs, total_count = await service.get_workout_logs(
        UUID(current_user["user_id"]),
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    # Get statistics
    stats = await service.get_workout_stats(
        UUID(current_user["user_id"]), start_date=start_date, end_date=end_date
    )

    # Calculate pagination metadata
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

    return PaginatedWorkoutLogsResponse(
        workout_logs=[WorkoutLogResponse.model_validate(log) for log in workout_logs],
        pagination=PaginationMeta(
            page=page, page_size=page_size, total_items=total_count, total_pages=total_pages
        ),
        stats=stats,
    )


@router.get("/{workout_log_id}", response_model=WorkoutLogResponse)
async def get_workout_log(
    workout_log_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific workout log.

    Args:
        workout_log_id: ID of the workout log
        current_user: Current authenticated user
        db: Database session

    Returns:
        Workout log details
    """
    service = WorkoutLogService(db)
    workout_log = await service.get_workout_log_by_id(
        UUID(current_user["user_id"]), workout_log_id
    )

    return WorkoutLogResponse.model_validate(workout_log)


@router.put("/{workout_log_id}", response_model=WorkoutLogResponse)
async def update_workout_log(
    workout_log_id: UUID,
    workout_data: WorkoutLogUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a workout log.

    Args:
        workout_log_id: ID of the workout log
        workout_data: Updated workout log data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated workout log
    """
    service = WorkoutLogService(db)
    workout_log = await service.update_workout_log(
        UUID(current_user["user_id"]), workout_log_id, workout_data
    )

    return WorkoutLogResponse.model_validate(workout_log)


@router.delete("/{workout_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_log(
    workout_log_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a workout log.

    Args:
        workout_log_id: ID of the workout log
        current_user: Current authenticated user
        db: Database session
    """
    service = WorkoutLogService(db)
    await service.delete_workout_log(UUID(current_user["user_id"]), workout_log_id)
