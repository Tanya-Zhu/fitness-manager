"""API routes for plan member management and leaderboards."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.api.middleware.auth import get_current_user
from src.services.plan_member_service import PlanMemberService
from src.api.schemas.plan_member_schemas import (
    PlanMemberInvite,
    PlanMemberResponse,
    LeaderboardEntry,
    PlanLeaderboardResponse,
)
from src.api.middleware.error_handler import NotFoundException, AppException
from src.models.fitness_plan import FitnessPlan
from src.models.plan_member import PlanMember
from sqlalchemy import select

router = APIRouter(prefix="/api/v1/plans", tags=["plan-members"])


@router.post(
    "/{plan_id}/members",
    response_model=PlanMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a user to join a plan",
)
async def invite_member(
    plan_id: UUID,
    invite: PlanMemberInvite,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invite a user to join a fitness plan by email.

    Args:
        plan_id: Plan ID to invite user to
        invite: Invitation details including user email
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created plan member

    Raises:
        404: Plan or user not found
        400: User already a member
    """
    service = PlanMemberService(db)

    try:
        member = await service.invite_member(
            plan_id=plan_id,
            inviter_user_id=UUID(current_user["user_id"]),
            invitee_email=invite.user_email,
        )

        # Construct response
        return PlanMemberResponse(
            id=member.id,
            plan_id=member.plan_id,
            user_id=member.user_id,
            user_email=member.user.email,
            user_name=member.user.full_name or member.user.email,
            invited_by=member.invited_by,
            joined_at=member.joined_at,
        )
    except (NotFoundException, AppException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/{plan_id}/members",
    response_model=List[PlanMemberResponse],
    summary="Get all members of a plan",
)
async def get_plan_members(
    plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all members of a fitness plan.

    Args:
        plan_id: Plan ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of plan members
    """
    service = PlanMemberService(db)
    members = await service.get_plan_members(plan_id)

    return [
        PlanMemberResponse(
            id=member.id,
            plan_id=member.plan_id,
            user_id=member.user_id,
            user_email=member.user.email,
            user_name=member.user.full_name or member.user.email,
            invited_by=member.invited_by,
            joined_at=member.joined_at,
        )
        for member in members
    ]


@router.get(
    "/{plan_id}/leaderboard",
    response_model=PlanLeaderboardResponse,
    summary="Get plan leaderboard",
)
async def get_plan_leaderboard(
    plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get leaderboard showing all members' completion statistics.

    The leaderboard is sorted by average completion rate (descending),
    then by total executions (descending).

    Args:
        plan_id: Plan ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Leaderboard with rankings and stats for all members

    Raises:
        404: Plan not found or user doesn't have access
    """
    from sqlalchemy import and_, or_

    user_id = UUID(current_user["user_id"])

    # Verify plan exists and user has access (owner or member)
    result = await db.execute(
        select(FitnessPlan).where(
            and_(
                FitnessPlan.id == plan_id,
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
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    service = PlanMemberService(db)
    leaderboard = await service.get_plan_leaderboard(plan_id)

    return PlanLeaderboardResponse(
        plan_id=plan_id,
        plan_name=plan.name,
        leaderboard=leaderboard,
    )


@router.delete(
    "/{plan_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member from a plan",
)
async def remove_member(
    plan_id: UUID,
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user from a fitness plan.

    Args:
        plan_id: Plan ID
        user_id: User ID to remove
        current_user: Current authenticated user
        db: Database session

    Raises:
        404: Membership not found
    """
    service = PlanMemberService(db)

    try:
        await service.remove_member(plan_id, user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
