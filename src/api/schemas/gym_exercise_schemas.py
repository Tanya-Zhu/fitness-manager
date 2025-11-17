"""Pydantic schemas for gym exercise API."""
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field


# Gym Exercise Set Schemas
class GymExerciseSetBase(BaseModel):
    """Base schema for gym exercise set."""

    set_number: int = Field(..., ge=1, description="Set number (1, 2, 3, ...)")
    reps: int = Field(..., ge=1, description="Number of repetitions")
    weight: Optional[float] = Field(None, ge=0, description="Weight in kg (optional)")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes for this set")


class GymExerciseSetCreate(GymExerciseSetBase):
    """Schema for creating a gym exercise set."""
    pass


class GymExerciseSetUpdate(BaseModel):
    """Schema for updating a gym exercise set."""

    reps: Optional[int] = Field(None, ge=1)
    weight: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class GymExerciseSetResponse(GymExerciseSetBase):
    """Schema for gym exercise set response."""

    id: UUID
    gym_exercise_log_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# Gym Exercise Log Schemas
class GymExerciseLogCreate(BaseModel):
    """Schema for creating a gym exercise log."""

    workout_date: date = Field(..., description="Date of the workout")
    exercise_name: str = Field(..., min_length=1, max_length=100, description="Exercise or equipment name")
    notes: Optional[str] = Field(None, description="Optional notes")
    sets: list[GymExerciseSetCreate] = Field(..., min_items=1, description="List of sets")


class GymExerciseLogUpdate(BaseModel):
    """Schema for updating a gym exercise log."""

    workout_date: Optional[date] = None
    exercise_name: Optional[str] = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = None
    sets: Optional[list[GymExerciseSetCreate]] = Field(None, min_items=1)


class GymExerciseLogResponse(BaseModel):
    """Schema for gym exercise log response."""

    id: UUID
    user_id: UUID
    workout_date: date
    exercise_name: str
    notes: Optional[str] = None
    sets: list[GymExerciseSetResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Summary Schema
class GymExerciseLogSummary(BaseModel):
    """Schema for gym exercise log summary."""

    id: UUID
    workout_date: date
    exercise_name: str
    total_sets: int
    total_reps: int
    total_volume: float  # total weight * reps
    created_at: datetime


# Pagination Schema
class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedGymExerciseLogsResponse(BaseModel):
    """Paginated gym exercise logs response."""

    gym_exercise_logs: list[GymExerciseLogSummary]
    pagination: PaginationMeta
