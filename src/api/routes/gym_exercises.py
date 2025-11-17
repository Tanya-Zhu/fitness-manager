"""API routes for gym exercise logs."""
from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import math

from src.core.database import get_db
from src.api.middleware.auth import get_current_user
from src.services.gym_exercise_service import GymExerciseService
from src.api.schemas.gym_exercise_schemas import (
    GymExerciseLogCreate,
    GymExerciseLogUpdate,
    GymExerciseLogResponse,
    PaginatedGymExerciseLogsResponse,
    PaginationMeta,
)
from src.core.config import settings


router = APIRouter(prefix="/gym-exercises", tags=["gym-exercises"])


@router.post("/", response_model=GymExerciseLogResponse, status_code=status.HTTP_201_CREATED)
async def create_gym_exercise_log(
    exercise_data: GymExerciseLogCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new gym exercise log with sets.

    Args:
        exercise_data: Gym exercise log creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created gym exercise log with sets
    """
    service = GymExerciseService(db)
    exercise_log = await service.create_gym_exercise_log(
        UUID(current_user["user_id"]), exercise_data
    )

    return GymExerciseLogResponse.model_validate(exercise_log)


@router.get("/", response_model=PaginatedGymExerciseLogsResponse)
async def list_gym_exercise_logs(
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
    """Get paginated list of user's gym exercise logs.

    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        page: Page number (1-based)
        page_size: Number of items per page
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of gym exercise logs with summary data
    """
    service = GymExerciseService(db)

    # Get gym exercise logs with summary
    gym_exercise_logs, total_count = await service.get_gym_exercise_logs(
        UUID(current_user["user_id"]),
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    # Calculate pagination metadata
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

    return PaginatedGymExerciseLogsResponse(
        gym_exercise_logs=gym_exercise_logs,
        pagination=PaginationMeta(
            page=page, page_size=page_size, total_items=total_count, total_pages=total_pages
        ),
    )


@router.get("/{exercise_log_id}", response_model=GymExerciseLogResponse)
async def get_gym_exercise_log(
    exercise_log_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific gym exercise log.

    Args:
        exercise_log_id: ID of the gym exercise log
        current_user: Current authenticated user
        db: Database session

    Returns:
        Gym exercise log details with all sets
    """
    service = GymExerciseService(db)
    exercise_log = await service.get_gym_exercise_log_by_id(
        UUID(current_user["user_id"]), exercise_log_id
    )

    return GymExerciseLogResponse.model_validate(exercise_log)


@router.put("/{exercise_log_id}", response_model=GymExerciseLogResponse)
async def update_gym_exercise_log(
    exercise_log_id: UUID,
    exercise_data: GymExerciseLogUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a gym exercise log.

    Args:
        exercise_log_id: ID of the gym exercise log
        exercise_data: Updated gym exercise log data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated gym exercise log
    """
    service = GymExerciseService(db)
    exercise_log = await service.update_gym_exercise_log(
        UUID(current_user["user_id"]), exercise_log_id, exercise_data
    )

    return GymExerciseLogResponse.model_validate(exercise_log)


@router.delete("/{exercise_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gym_exercise_log(
    exercise_log_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a gym exercise log.

    Args:
        exercise_log_id: ID of the gym exercise log
        current_user: Current authenticated user
        db: Database session
    """
    service = GymExerciseService(db)
    await service.delete_gym_exercise_log(UUID(current_user["user_id"]), exercise_log_id)


@router.get("/stats/exercise-names")
async def get_exercise_names(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of all unique exercise names user has trained.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of unique exercise names
    """
    service = GymExerciseService(db)
    exercise_names = await service.get_exercise_names(UUID(current_user["user_id"]))

    return {"exercise_names": exercise_names}


@router.get("/trends/{exercise_name}")
async def get_exercise_trends(
    exercise_name: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get historical trend data for a specific exercise.

    Args:
        exercise_name: Name of the exercise
        current_user: Current authenticated user
        db: Database session

    Returns:
        Historical trend data including dates, max weight, avg weight, and total reps
    """
    service = GymExerciseService(db)
    trend_data = await service.get_exercise_trends(
        UUID(current_user["user_id"]), exercise_name
    )

    return trend_data
