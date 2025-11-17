"""Service for managing plan members and leaderboards."""
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from src.models.plan_member import PlanMember
from src.models.fitness_plan import FitnessPlan
from src.models.user import User
from src.models.plan_execution import PlanExecution, ExerciseExecution
from src.api.schemas.plan_member_schemas import LeaderboardEntry
from src.api.middleware.error_handler import NotFoundException, AppException


class PlanMemberService:
    """Service for managing plan members and leaderboards."""

    def __init__(self, db: AsyncSession):
        """Initialize plan member service.

        Args:
            db: Database session
        """
        self.db = db

    async def invite_member(
        self, plan_id: UUID, inviter_user_id: UUID, invitee_email: str
    ) -> PlanMember:
        """Invite a user to join a plan.

        Args:
            plan_id: Plan ID
            inviter_user_id: ID of user sending the invitation
            invitee_email: Email of user to invite

        Returns:
            Created plan member

        Raises:
            NotFoundException: If plan or invitee not found
            AppException: If user already a member
        """
        # Verify plan exists and inviter is the owner or a member
        result = await self.db.execute(
            select(FitnessPlan).where(FitnessPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()
        if plan is None:
            raise NotFoundException("Plan not found")

        # Find invitee by email
        result = await self.db.execute(
            select(User).where(User.email == invitee_email)
        )
        invitee = result.scalar_one_or_none()
        if invitee is None:
            raise NotFoundException(f"User with email {invitee_email} not found")

        # Check if already a member
        result = await self.db.execute(
            select(PlanMember).where(
                and_(
                    PlanMember.plan_id == plan_id,
                    PlanMember.user_id == invitee.id,
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise AppException("User is already a member of this plan", "ALREADY_MEMBER", 400)

        # Create plan member
        member = PlanMember(
            plan_id=plan_id,
            user_id=invitee.id,
            invited_by=inviter_user_id,
        )

        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)

        # Reload with user relationship
        result = await self.db.execute(
            select(PlanMember)
            .where(PlanMember.id == member.id)
            .options(selectinload(PlanMember.user))
        )
        member = result.scalar_one()

        return member

    async def get_plan_members(self, plan_id: UUID) -> List[PlanMember]:
        """Get all members of a plan.

        Args:
            plan_id: Plan ID

        Returns:
            List of plan members
        """
        result = await self.db.execute(
            select(PlanMember)
            .where(PlanMember.plan_id == plan_id)
            .options(selectinload(PlanMember.user))
        )
        return list(result.scalars().all())

    async def get_plan_leaderboard(self, plan_id: UUID) -> List[LeaderboardEntry]:
        """Get leaderboard for a plan showing all members' stats.

        Args:
            plan_id: Plan ID

        Returns:
            List of leaderboard entries sorted by avg completion rate
        """
        # Get plan with owner info and exercises
        result = await self.db.execute(
            select(FitnessPlan)
            .where(FitnessPlan.id == plan_id)
            .options(
                selectinload(FitnessPlan.exercises),
                selectinload(FitnessPlan.user)  # Load plan owner
            )
        )
        plan = result.scalar_one()

        # Get all invited members
        members = await self.get_plan_members(plan_id)

        # Build a list of all participants (owner + invited members)
        # Create a dict to avoid duplicates and store user info
        participants = {}

        # Add plan owner
        participants[plan.user_id] = {
            'user_id': plan.user_id,
            'user_name': plan.user.full_name or plan.user.email,
            'user_email': plan.user.email
        }

        # Add invited members
        for member in members:
            participants[member.user_id] = {
                'user_id': member.user_id,
                'user_name': member.user.full_name or member.user.email,
                'user_email': member.user.email
            }

        if not participants:
            return []

        leaderboard = []

        # Iterate through all participants (owner + members)
        for user_id, user_info in participants.items():
            # Get all executions for this user and plan
            result = await self.db.execute(
                select(PlanExecution)
                .where(
                    and_(
                        PlanExecution.plan_id == plan_id,
                        PlanExecution.user_id == user_id,
                    )
                )
                .options(selectinload(PlanExecution.exercise_executions))
                .order_by(desc(PlanExecution.execution_date))
            )
            executions = list(result.scalars().all())

            total_executions = len(executions)

            if total_executions == 0:
                # No executions yet
                leaderboard.append(LeaderboardEntry(
                    user_id=user_info['user_id'],
                    user_name=user_info['user_name'],
                    user_email=user_info['user_email'],
                    total_executions=0,
                    avg_completion_rate=0.0,
                    last_execution_date=None,
                    completion_rate_rank=0,
                    execution_count_rank=0
                ))
                continue

            # Calculate average completion rate
            completion_rates = []
            for execution in executions:
                # Calculate completion rate for this execution
                exercise_rates = []
                for ex_exec in execution.exercise_executions:
                    if not ex_exec.completed:
                        exercise_rates.append(0)
                    else:
                        exercise = next((e for e in plan.exercises if e.id == ex_exec.exercise_id), None)
                        if exercise:
                            if exercise.duration_minutes and ex_exec.actual_duration_minutes:
                                rate = min((ex_exec.actual_duration_minutes / exercise.duration_minutes) * 100, 100)
                                exercise_rates.append(rate)
                            elif exercise.repetitions and ex_exec.actual_repetitions:
                                rate = min((ex_exec.actual_repetitions / exercise.repetitions) * 100, 100)
                                exercise_rates.append(rate)
                            else:
                                exercise_rates.append(100)
                        else:
                            exercise_rates.append(100)

                if exercise_rates:
                    completion_rates.append(sum(exercise_rates) / len(exercise_rates))

            avg_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0

            leaderboard.append(LeaderboardEntry(
                user_id=user_info['user_id'],
                user_name=user_info['user_name'],
                user_email=user_info['user_email'],
                total_executions=total_executions,
                avg_completion_rate=round(avg_rate, 1),
                last_execution_date=executions[0].execution_date.isoformat() if executions else None,
                completion_rate_rank=0,  # Will be set next
                execution_count_rank=0   # Will be set next
            ))

        # Calculate completion rate ranking
        leaderboard_by_rate = sorted(leaderboard, key=lambda x: x.avg_completion_rate, reverse=True)
        for i, entry in enumerate(leaderboard_by_rate, start=1):
            entry.completion_rate_rank = i

        # Calculate execution count ranking
        leaderboard_by_count = sorted(leaderboard, key=lambda x: x.total_executions, reverse=True)
        for i, entry in enumerate(leaderboard_by_count, start=1):
            entry.execution_count_rank = i

        # Return sorted by completion rate (primary) as default display order
        return leaderboard_by_rate

    async def remove_member(self, plan_id: UUID, user_id: UUID) -> None:
        """Remove a user from a plan.

        Args:
            plan_id: Plan ID
            user_id: User ID to remove

        Raises:
            NotFoundException: If membership not found
        """
        result = await self.db.execute(
            select(PlanMember).where(
                and_(
                    PlanMember.plan_id == plan_id,
                    PlanMember.user_id == user_id,
                )
            )
        )
        member = result.scalar_one_or_none()

        if member is None:
            raise NotFoundException("Plan membership not found")

        await self.db.delete(member)
        await self.db.commit()
