"""Pydantic schemas for fitness plan API."""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator
from src.models.fitness_plan import PlanStatus
from src.models.exercise import ExerciseIntensity
from src.api.schemas.reminder_schemas import ReminderResponse


# Exercise Schemas
class ExerciseCreate(BaseModel):
    """Schema for creating an exercise."""

    name: str = Field(..., min_length=1, max_length=100, description="Exercise name")
    duration_minutes: Optional[int] = Field(None, gt=0, description="Duration in minutes")
    repetitions: Optional[int] = Field(None, gt=0, description="Number of repetitions")
    intensity: ExerciseIntensity = Field(default=ExerciseIntensity.MEDIUM, description="Exercise intensity")
    order_index: int = Field(default=0, ge=0, description="Order in the plan")

    @model_validator(mode='after')
    def check_duration_or_reps(self):
        """Validate that at least one of duration_minutes or repetitions is provided."""
        if self.duration_minutes is None and self.repetitions is None:
            raise ValueError("Either duration_minutes or repetitions must be provided")
        return self


class ExerciseUpdate(BaseModel):
    """Schema for updating an exercise."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    duration_minutes: Optional[int] = Field(None, gt=0)
    repetitions: Optional[int] = Field(None, gt=0)
    intensity: Optional[ExerciseIntensity] = None
    order_index: Optional[int] = Field(None, ge=0)


class ExerciseResponse(BaseModel):
    """Schema for exercise response."""

    id: UUID
    name: str
    duration_minutes: Optional[int] = None
    repetitions: Optional[int] = None
    intensity: str
    order_index: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Fitness Plan Schemas
class FitnessPlanCreate(BaseModel):
    """Schema for creating a fitness plan."""

    name: str = Field(..., min_length=1, max_length=50, description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    exercises: List[ExerciseCreate] = Field(..., min_length=1, description="List of exercises")

    @field_validator('exercises')
    @classmethod
    def validate_exercises_not_empty(cls, v):
        """Validate that at least one exercise is provided."""
        if not v or len(v) == 0:
            raise ValueError("Plan must contain at least one exercise")
        return v


class FitnessPlanUpdate(BaseModel):
    """Schema for updating a fitness plan."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None


class FitnessPlanSummary(BaseModel):
    """Schema for fitness plan summary (list view)."""

    id: UUID
    name: str
    description: Optional[str] = None
    status: str
    exercise_count: int
    is_owner: bool = Field(default=True, description="Whether the current user is the plan owner")
    owner_email: Optional[str] = Field(None, description="Email of the plan owner")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FitnessPlanDetail(BaseModel):
    """Schema for fitness plan detail (full view)."""

    id: UUID
    name: str
    description: Optional[str] = None
    status: str
    exercises: List[ExerciseResponse]
    reminders: List[ReminderResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Pagination Schema
class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedPlansResponse(BaseModel):
    """Paginated plans response."""

    plans: List[FitnessPlanSummary]
    pagination: PaginationMeta
