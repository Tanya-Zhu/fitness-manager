"""Service layer for exercise management."""
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from src.models.exercise import Exercise
from src.models.fitness_plan import FitnessPlan
from src.api.schemas.plan_schemas import ExerciseCreate, ExerciseUpdate
from src.api.middleware.error_handler import NotFoundException, BusinessRuleViolationException


class ExerciseService:
    """Service for managing exercises within fitness plans."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_exercise(
        self, user_id: UUID, plan_id: UUID, exercise_data: ExerciseCreate
    ) -> Exercise:
        """Add a new exercise to a fitness plan.

        Args:
            user_id: ID of the user (for ownership verification)
            plan_id: ID of the plan
            exercise_data: Exercise data

        Returns:
            Created exercise

        Raises:
            NotFoundException: If plan not found or user doesn't own it
        """
        # Verify plan exists and belongs to user
        result = await self.db.execute(
            select(FitnessPlan).where(
                and_(
                    FitnessPlan.id == plan_id,
                    FitnessPlan.user_id == user_id,
                    FitnessPlan.deleted_at.is_(None),
                )
            )
        )
        plan = result.scalar_one_or_none()

        if plan is None:
            raise NotFoundException("Fitness plan not found")

        # Create exercise
        exercise = Exercise(
            plan_id=plan_id,
            name=exercise_data.name,
            duration_minutes=exercise_data.duration_minutes,
            repetitions=exercise_data.repetitions,
            intensity=exercise_data.intensity,
            order_index=exercise_data.order_index,
        )

        self.db.add(exercise)
        await self.db.commit()
        await self.db.refresh(exercise)

        return exercise

    async def update_exercise(
        self, user_id: UUID, plan_id: UUID, exercise_id: UUID, exercise_data: ExerciseUpdate
    ) -> Exercise:
        """Update an existing exercise.

        Args:
            user_id: ID of the user (for ownership verification)
            plan_id: ID of the plan
            exercise_id: ID of the exercise
            exercise_data: Updated exercise data

        Returns:
            Updated exercise

        Raises:
            NotFoundException: If exercise not found or user doesn't own the plan
        """
        # Fetch exercise with plan ownership verification
        result = await self.db.execute(
            select(Exercise)
            .join(FitnessPlan, Exercise.plan_id == FitnessPlan.id)
            .where(
                and_(
                    Exercise.id == exercise_id,
                    Exercise.plan_id == plan_id,
                    FitnessPlan.user_id == user_id,
                    FitnessPlan.deleted_at.is_(None),
                )
            )
        )
        exercise = result.scalar_one_or_none()

        if exercise is None:
            raise NotFoundException("Exercise not found")

        # Update fields
        update_data = exercise_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(exercise, field, value)

        await self.db.commit()
        await self.db.refresh(exercise)

        return exercise

    async def delete_exercise(
        self, user_id: UUID, plan_id: UUID, exercise_id: UUID
    ) -> None:
        """Delete an exercise from a fitness plan.

        Args:
            user_id: ID of the user (for ownership verification)
            plan_id: ID of the plan
            exercise_id: ID of the exercise

        Raises:
            NotFoundException: If exercise not found or user doesn't own the plan
            BusinessRuleViolationException: If trying to delete the last exercise
        """
        # Fetch exercise with plan ownership verification
        result = await self.db.execute(
            select(Exercise)
            .join(FitnessPlan, Exercise.plan_id == FitnessPlan.id)
            .where(
                and_(
                    Exercise.id == exercise_id,
                    Exercise.plan_id == plan_id,
                    FitnessPlan.user_id == user_id,
                    FitnessPlan.deleted_at.is_(None),
                )
            )
        )
        exercise = result.scalar_one_or_none()

        if exercise is None:
            raise NotFoundException("Exercise not found")

        # Check if this is the last exercise in the plan
        count_result = await self.db.execute(
            select(func.count()).select_from(Exercise).where(Exercise.plan_id == plan_id)
        )
        exercise_count = count_result.scalar()

        if exercise_count <= 1:
            raise BusinessRuleViolationException(
                "Cannot delete the last exercise from a plan. A plan must have at least one exercise."
            )

        # Delete exercise
        await self.db.delete(exercise)
        await self.db.commit()

    async def get_exercise_by_id(
        self, user_id: UUID, plan_id: UUID, exercise_id: UUID
    ) -> Exercise:
        """Get a specific exercise by ID.

        Args:
            user_id: ID of the user (for ownership verification)
            plan_id: ID of the plan
            exercise_id: ID of the exercise

        Returns:
            Exercise

        Raises:
            NotFoundException: If exercise not found or user doesn't own the plan
        """
        result = await self.db.execute(
            select(Exercise)
            .join(FitnessPlan, Exercise.plan_id == FitnessPlan.id)
            .where(
                and_(
                    Exercise.id == exercise_id,
                    Exercise.plan_id == plan_id,
                    FitnessPlan.user_id == user_id,
                    FitnessPlan.deleted_at.is_(None),
                )
            )
        )
        exercise = result.scalar_one_or_none()

        if exercise is None:
            raise NotFoundException("Exercise not found")

        return exercise
