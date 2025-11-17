"""Pydantic schemas for workout log API."""
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field


# Workout Log Schemas
class WorkoutLogCreate(BaseModel):
    """Schema for creating a workout log."""

    workout_date: date = Field(..., description="Date of the workout")
    workout_name: str = Field(..., min_length=1, max_length=100, description="Workout name")
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes")
    calories_burned: Optional[float] = Field(None, ge=0, description="Calories burned")
    notes: Optional[str] = Field(None, description="Optional notes")


class WorkoutLogUpdate(BaseModel):
    """Schema for updating a workout log."""

    workout_date: Optional[date] = None
    workout_name: Optional[str] = Field(None, min_length=1, max_length=100)
    duration_minutes: Optional[int] = Field(None, gt=0)
    calories_burned: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class WorkoutLogResponse(BaseModel):
    """Schema for workout log response."""

    id: UUID
    user_id: UUID
    workout_date: date
    workout_name: str
    duration_minutes: int
    calories_burned: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Statistics Schema
class WorkoutStats(BaseModel):
    """Schema for workout statistics."""

    total_workouts: int
    total_duration_minutes: int
    total_calories: float
    avg_duration_minutes: float
    avg_calories: float


# Chart Data Schema
class ChartDataPoint(BaseModel):
    """Schema for a single chart data point."""

    period: str  # e.g., "2024-W01" or "2024-01"
    label: str  # e.g., "Week 1" or "January 2024"
    workouts: int
    duration_minutes: int
    calories: float


class ChartData(BaseModel):
    """Schema for chart data."""

    data_points: list[ChartDataPoint]
    period_type: str  # "week" or "month"


# Pagination Schema
class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedWorkoutLogsResponse(BaseModel):
    """Paginated workout logs response."""

    workout_logs: list[WorkoutLogResponse]
    pagination: PaginationMeta
    stats: Optional[WorkoutStats] = None
