"""Service for managing plan executions."""
from typing import Tuple, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from src.models.plan_execution import PlanExecution, ExerciseExecution
from src.models.fitness_plan import FitnessPlan
from src.api.schemas.plan_execution_schemas import (
    PlanExecutionCreate,
    PlanExecutionUpdate,
    PlanExecutionSummary,
)
from src.api.middleware.error_handler import NotFoundException


class PlanExecutionService:
    """Service for managing plan executions."""

    def __init__(self, db: AsyncSession):
        """Initialize plan execution service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_plan_execution(
        self, user_id: UUID, execution_data: PlanExecutionCreate
    ) -> PlanExecution:
        """Create a new plan execution with exercise executions.

        Args:
            user_id: User ID
            execution_data: Plan execution creation data

        Returns:
            Created plan execution

        Raises:
            NotFoundException: If plan not found or user doesn't have access
        """
        from src.models.plan_member import PlanMember
        from sqlalchemy import or_

        # Verify plan exists and user has access (owner or member)
        result = await self.db.execute(
            select(FitnessPlan).where(
                and_(
                    FitnessPlan.id == execution_data.plan_id,
                    or_(
                        FitnessPlan.user_id == user_id,  # User is owner
                        FitnessPlan.id.in_(  # User is member
                            select(PlanMember.plan_id).where(PlanMember.user_id == user_id)
                        )
                    ),
                )
            )
        )
        plan = result.scalar_one_or_none()
        if plan is None:
            raise NotFoundException("Fitness plan not found")

        # Create plan execution
        plan_execution = PlanExecution(
            user_id=user_id,
            plan_id=execution_data.plan_id,
            execution_date=execution_data.execution_date,
            notes=execution_data.notes,
        )

        self.db.add(plan_execution)
        await self.db.flush()  # Flush to get the ID

        # Create exercise executions
        for exercise_exec_data in execution_data.exercise_executions:
            exercise_execution = ExerciseExecution(
                plan_execution_id=plan_execution.id,
                exercise_id=exercise_exec_data.exercise_id,
                completed=exercise_exec_data.completed,
                actual_duration_minutes=exercise_exec_data.actual_duration_minutes,
                actual_repetitions=exercise_exec_data.actual_repetitions,
                notes=exercise_exec_data.notes,
            )
            self.db.add(exercise_execution)

        await self.db.commit()
        await self.db.refresh(plan_execution)

        # Load relationships
        result = await self.db.execute(
            select(PlanExecution)
            .where(PlanExecution.id == plan_execution.id)
            .options(selectinload(PlanExecution.exercise_executions))
        )
        plan_execution = result.scalar_one()

        return plan_execution

    async def get_plan_executions(
        self,
        user_id: UUID,
        plan_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[list[PlanExecutionSummary], int]:
        """Get paginated plan executions for a user with summary data.

        Args:
            user_id: User ID
            plan_id: Optional plan ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            page: Page number (1-based)
            page_size: Items per page

        Returns:
            Tuple of (plan execution summaries list, total count)
        """
        # Build query with filters
        query = (
            select(PlanExecution)
            .where(PlanExecution.user_id == user_id)
            .options(
                selectinload(PlanExecution.exercise_executions),
                selectinload(PlanExecution.plan),
            )
        )

        if plan_id:
            query = query.where(PlanExecution.plan_id == plan_id)
        if start_date:
            query = query.where(PlanExecution.execution_date >= start_date)
        if end_date:
            query = query.where(PlanExecution.execution_date <= end_date)

        # Order by date descending (most recent first)
        query = query.order_by(desc(PlanExecution.execution_date), desc(PlanExecution.created_at))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await self.db.execute(query)
        plan_executions = list(result.scalars().all())

        # Create summary objects
        summaries = []
        for execution in plan_executions:
            total_exercises = len(execution.exercise_executions)

            # Calculate completion rate for each exercise based on actual vs planned
            exercise_completion_rates = []
            completed_count = 0

            for ex_exec in execution.exercise_executions:
                if not ex_exec.completed:
                    # Not completed at all = 0%
                    exercise_completion_rates.append(0)
                else:
                    completed_count += 1
                    # Find the corresponding exercise from the plan
                    exercise = next((e for e in execution.plan.exercises if e.id == ex_exec.exercise_id), None)

                    if exercise:
                        # Calculate based on actual vs planned
                        if exercise.duration_minutes and ex_exec.actual_duration_minutes:
                            # For duration-based exercises
                            rate = min((ex_exec.actual_duration_minutes / exercise.duration_minutes) * 100, 100)
                            exercise_completion_rates.append(rate)
                        elif exercise.repetitions and ex_exec.actual_repetitions:
                            # For repetition-based exercises
                            rate = min((ex_exec.actual_repetitions / exercise.repetitions) * 100, 100)
                            exercise_completion_rates.append(rate)
                        else:
                            # Completed but no actual data provided = 100%
                            exercise_completion_rates.append(100)
                    else:
                        # Exercise not found in plan = 100% (assume completed)
                        exercise_completion_rates.append(100)

            # Overall completion rate is the average of all exercise completion rates
            completion_rate = (
                sum(exercise_completion_rates) / len(exercise_completion_rates)
                if exercise_completion_rates else 0
            )

            summaries.append(
                PlanExecutionSummary(
                    id=execution.id,
                    plan_id=execution.plan_id,
                    plan_name=execution.plan.name,
                    execution_date=execution.execution_date,
                    total_exercises=total_exercises,
                    completed_exercises=completed_count,
                    completion_rate=round(completion_rate, 1),
                    created_at=execution.created_at,
                )
            )

        return summaries, total_count

    async def get_plan_execution_by_id(
        self, user_id: UUID, execution_id: UUID
    ) -> PlanExecution:
        """Get a specific plan execution with exercise executions.

        Args:
            user_id: User ID (for ownership verification)
            execution_id: Plan execution ID

        Returns:
            Plan execution with exercise executions

        Raises:
            NotFoundException: If plan execution not found or not owned by user
        """
        result = await self.db.execute(
            select(PlanExecution)
            .where(
                and_(
                    PlanExecution.id == execution_id,
                    PlanExecution.user_id == user_id,
                )
            )
            .options(selectinload(PlanExecution.exercise_executions))
        )
        plan_execution = result.scalar_one_or_none()

        if plan_execution is None:
            raise NotFoundException("Plan execution not found")

        return plan_execution

    async def update_plan_execution(
        self, user_id: UUID, execution_id: UUID, execution_data: PlanExecutionUpdate
    ) -> PlanExecution:
        """Update a plan execution.

        Args:
            user_id: User ID (for ownership verification)
            execution_id: Plan execution ID
            execution_data: Updated plan execution data

        Returns:
            Updated plan execution

        Raises:
            NotFoundException: If plan execution not found or not owned by user
        """
        plan_execution = await self.get_plan_execution_by_id(user_id, execution_id)

        # Update basic fields
        if execution_data.execution_date is not None:
            plan_execution.execution_date = execution_data.execution_date
        if execution_data.notes is not None:
            plan_execution.notes = execution_data.notes

        # Update exercise executions if provided
        if execution_data.exercise_executions is not None:
            # Delete existing exercise executions
            for existing_exec in plan_execution.exercise_executions:
                await self.db.delete(existing_exec)
            await self.db.flush()

            # Create new exercise executions
            for exercise_exec_data in execution_data.exercise_executions:
                exercise_execution = ExerciseExecution(
                    plan_execution_id=plan_execution.id,
                    exercise_id=exercise_exec_data.exercise_id,
                    completed=exercise_exec_data.completed,
                    actual_duration_minutes=exercise_exec_data.actual_duration_minutes,
                    actual_repetitions=exercise_exec_data.actual_repetitions,
                    notes=exercise_exec_data.notes,
                )
                self.db.add(exercise_execution)

        await self.db.commit()
        await self.db.refresh(plan_execution)

        # Load relationships
        result = await self.db.execute(
            select(PlanExecution)
            .where(PlanExecution.id == plan_execution.id)
            .options(selectinload(PlanExecution.exercise_executions))
        )
        plan_execution = result.scalar_one()

        return plan_execution

    async def delete_plan_execution(
        self, user_id: UUID, execution_id: UUID
    ) -> None:
        """Delete a plan execution.

        Args:
            user_id: User ID (for ownership verification)
            execution_id: Plan execution ID

        Raises:
            NotFoundException: If plan execution not found or not owned by user
        """
        plan_execution = await self.get_plan_execution_by_id(user_id, execution_id)

        await self.db.delete(plan_execution)
        await self.db.commit()
