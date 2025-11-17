"""Pydantic schemas for plan member/sharing API."""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# Plan Member Schemas
class PlanMemberInvite(BaseModel):
    """Schema for inviting a user to a plan."""

    user_email: EmailStr = Field(..., description="Email of the user to invite")


class PlanMemberResponse(BaseModel):
    """Schema for plan member response."""

    id: UUID
    plan_id: UUID
    user_id: UUID
    user_email: str
    user_name: str
    invited_by: Optional[UUID] = None
    joined_at: datetime

    model_config = {"from_attributes": True}


# Leaderboard Schemas
class LeaderboardEntry(BaseModel):
    """Schema for a single leaderboard entry."""

    user_id: UUID
    user_name: str
    user_email: str
    total_executions: int
    avg_completion_rate: float
    last_execution_date: Optional[str] = None  # ISO date string
    completion_rate_rank: int = Field(..., description="Rank by completion rate")
    execution_count_rank: int = Field(..., description="Rank by execution count")


class PlanLeaderboardResponse(BaseModel):
    """Schema for plan leaderboard response."""

    plan_id: UUID
    plan_name: str
    leaderboard: list[LeaderboardEntry]
