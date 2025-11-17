"""Service layer for fitness plan business logic."""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from src.models.fitness_plan import FitnessPlan, PlanStatus
from src.models.exercise import Exercise
from src.api.schemas.plan_schemas import FitnessPlanCreate, FitnessPlanUpdate
from src.api.middleware.error_handler import NotFoundException, BusinessRuleViolationException


class PlanService:
    """Service for managing fitness plans."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_plan(self, user_id: UUID, plan_data: FitnessPlanCreate) -> FitnessPlan:
        """Create a new fitness plan with exercises.

        Args:
            user_id: ID of the user creating the plan
            plan_data: Plan creation data including exercises

        Returns:
            Created fitness plan with exercises
        """
        # Create the plan
        plan = FitnessPlan(
            user_id=user_id, name=plan_data.name, description=plan_data.description
        )
        self.db.add(plan)

        # Flush to get plan ID
        await self.db.flush()

        # Add exercises
        for exercise_data in plan_data.exercises:
            exercise = Exercise(
                plan_id=plan.id,
                name=exercise_data.name,
                duration_minutes=exercise_data.duration_minutes,
                repetitions=exercise_data.repetitions,
                intensity=exercise_data.intensity,
                order_index=exercise_data.order_index,
            )
            self.db.add(exercise)

        await self.db.commit()
        await self.db.refresh(plan)

        return plan

    async def get_user_plans(
        self,
        user_id: UUID,
        status: Optional[PlanStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[FitnessPlan], int]:
        """Get paginated list of user's fitness plans (created by user or joined as member).

        Args:
            user_id: ID of the user
            status: Optional filter by plan status
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Tuple of (list of plans, total count)
        """
        from src.models.plan_member import PlanMember
        from src.models.user import User
        from sqlalchemy import or_

        # Build base query - include plans created by user OR where user is a member
        query = select(FitnessPlan).where(
            and_(
                or_(
                    FitnessPlan.user_id == user_id,  # Plans created by user
                    FitnessPlan.id.in_(  # Plans where user is a member
                        select(PlanMember.plan_id).where(PlanMember.user_id == user_id)
                    )
                ),
                FitnessPlan.deleted_at.is_(None)
            )
        )

        # Filter by status if provided
        if status:
            query = query.where(FitnessPlan.status == status)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.db.execute(count_query)
        total_count = total_count_result.scalar()

        # Apply pagination and eager load user (owner) relationship
        offset = (page - 1) * page_size
        query = (
            query.options(
                selectinload(FitnessPlan.exercises),
                selectinload(FitnessPlan.user)
            )
            .order_by(FitnessPlan.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        plans = result.scalars().all()

        return plans, total_count

    async def get_plan_by_id(self, user_id: UUID, plan_id: UUID) -> FitnessPlan:
        """Get a specific fitness plan by ID.

        Args:
            user_id: ID of the user (for ownership/membership verification)
            plan_id: ID of the plan

        Returns:
            Fitness plan with exercises

        Raises:
            NotFoundException: If plan not found or user doesn't have access
        """
        from src.models.plan_member import PlanMember
        from sqlalchemy import or_

        query = (
            select(FitnessPlan)
            .where(
                and_(
                    FitnessPlan.id == plan_id,
                    or_(
                        FitnessPlan.user_id == user_id,  # User is the owner
                        FitnessPlan.id.in_(  # User is a member
                            select(PlanMember.plan_id).where(PlanMember.user_id == user_id)
                        )
                    ),
                    FitnessPlan.deleted_at.is_(None),
                )
            )
            .options(selectinload(FitnessPlan.exercises), selectinload(FitnessPlan.reminders))
        )

        result = await self.db.execute(query)
        plan = result.scalar_one_or_none()

        if plan is None:
            raise NotFoundException("Fitness plan not found")

        return plan

    async def update_plan(
        self, user_id: UUID, plan_id: UUID, plan_data: FitnessPlanUpdate
    ) -> FitnessPlan:
        """Update a fitness plan's basic information.

        Args:
            user_id: ID of the user (for ownership verification)
            plan_id: ID of the plan
            plan_data: Updated plan data

        Returns:
            Updated fitness plan

        Raises:
            NotFoundException: If plan not found or user doesn't own it
        """
        # Get existing plan
        plan = await self.get_plan_by_id(user_id, plan_id)

        # Update only provided fields
        update_data = plan_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plan, field, value)

        await self.db.commit()
        await self.db.refresh(plan)

        return plan

    async def delete_plan(self, user_id: UUID, plan_id: UUID, scheduler=None) -> None:
        """Soft delete a fitness plan and cancel all its reminders.

        Args:
            user_id: ID of the user (for ownership verification)
            plan_id: ID of the plan
            scheduler: Optional APScheduler instance to cancel reminder jobs

        Raises:
            NotFoundException: If plan not found or user doesn't own it
        """
        from datetime import datetime

        # Get existing plan with reminders
        plan = await self.get_plan_by_id(user_id, plan_id)

        # Cancel all scheduled reminder jobs if scheduler is provided
        if scheduler and plan.reminders:
            for reminder in plan.reminders:
                job_id = f"reminder_{plan_id}_{reminder.id}"
                if scheduler.get_job(job_id):
                    scheduler.remove_job(job_id)

        # Soft delete the plan (reminders will be cascade deleted by the database)
        plan.deleted_at = datetime.utcnow()

        await self.db.commit()
