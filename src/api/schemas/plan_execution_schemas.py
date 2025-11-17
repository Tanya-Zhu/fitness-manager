"""Pydantic schemas for plan execution API."""
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field


# Exercise Execution Schemas
class ExerciseExecutionBase(BaseModel):
    """Base schema for exercise execution."""

    exercise_id: UUID = Field(..., description="ID of the exercise from the plan")
    completed: bool = Field(default=True, description="Whether the exercise was completed")
    actual_duration_minutes: Optional[int] = Field(None, ge=1, description="Actual duration in minutes")
    actual_repetitions: Optional[int] = Field(None, ge=1, description="Actual number of repetitions")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class ExerciseExecutionCreate(ExerciseExecutionBase):
    """Schema for creating an exercise execution."""
    pass


class ExerciseExecutionUpdate(BaseModel):
    """Schema for updating an exercise execution."""

    completed: Optional[bool] = None
    actual_duration_minutes: Optional[int] = Field(None, ge=1)
    actual_repetitions: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = Field(None, max_length=500)


class ExerciseExecutionResponse(ExerciseExecutionBase):
    """Schema for exercise execution response."""

    id: UUID
    plan_execution_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# Plan Execution Schemas
class PlanExecutionCreate(BaseModel):
    """Schema for creating a plan execution."""

    plan_id: UUID = Field(..., description="ID of the fitness plan")
    execution_date: date = Field(default_factory=date.today, description="Date when plan was executed")
    notes: Optional[str] = Field(None, description="Optional notes about the workout session")
    exercise_executions: list[ExerciseExecutionCreate] = Field(
        ..., min_items=1, description="List of exercise executions"
    )


class PlanExecutionUpdate(BaseModel):
    """Schema for updating a plan execution."""

    execution_date: Optional[date] = None
    notes: Optional[str] = None
    exercise_executions: Optional[list[ExerciseExecutionCreate]] = Field(None, min_items=1)


class PlanExecutionResponse(BaseModel):
    """Schema for plan execution response."""

    id: UUID
    plan_id: UUID
    user_id: UUID
    execution_date: date
    notes: Optional[str] = None
    exercise_executions: list[ExerciseExecutionResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Summary Schema
class PlanExecutionSummary(BaseModel):
    """Schema for plan execution summary."""

    id: UUID
    plan_id: UUID
    plan_name: str  # Will be populated from the related plan
    execution_date: date
    total_exercises: int
    completed_exercises: int
    completion_rate: float  # Percentage of completed exercises
    created_at: datetime


# Pagination Schema (reuse from existing)
class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedPlanExecutionsResponse(BaseModel):
    """Paginated plan executions response."""

    plan_executions: list[PlanExecutionSummary]
    pagination: PaginationMeta
