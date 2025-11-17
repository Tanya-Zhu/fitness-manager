"""Pydantic schemas for reminder API requests and responses."""
from datetime import datetime, time
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ReminderFrequency(str, Enum):
    """Reminder frequency options."""

    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class ReminderCreate(BaseModel):
    """Schema for creating a new reminder."""

    reminder_time: time = Field(..., description="Time to send reminder (HH:MM:SS)")
    frequency: ReminderFrequency = Field(
        default=ReminderFrequency.WEEKLY, description="Reminder frequency"
    )
    days_of_week: Optional[List[int]] = Field(
        None, description="Days of week for reminder (1=Monday, 7=Sunday)"
    )
    is_enabled: bool = Field(default=True, description="Whether reminder is enabled")

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v: Optional[List[int]], info) -> Optional[List[int]]:
        """Validate days_of_week values are between 1 and 7."""
        if v is None:
            return v

        if not v:
            raise ValueError("days_of_week must not be empty if provided")

        for day in v:
            if day < 1 or day > 7:
                raise ValueError("days_of_week must contain values between 1 and 7")

        # Remove duplicates and sort
        return sorted(list(set(v)))

    @field_validator("frequency")
    @classmethod
    def validate_frequency_with_days(cls, v: ReminderFrequency) -> ReminderFrequency:
        """Validate frequency value."""
        return v


class ReminderUpdate(BaseModel):
    """Schema for updating an existing reminder."""

    reminder_time: Optional[time] = Field(None, description="Time to send reminder")
    frequency: Optional[ReminderFrequency] = Field(None, description="Reminder frequency")
    days_of_week: Optional[List[int]] = Field(
        None, description="Days of week for reminder"
    )
    is_enabled: Optional[bool] = Field(None, description="Whether reminder is enabled")

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validate days_of_week values are between 1 and 7."""
        if v is None:
            return v

        if not v:
            raise ValueError("days_of_week must not be empty if provided")

        for day in v:
            if day < 1 or day > 7:
                raise ValueError("days_of_week must contain values between 1 and 7")

        # Remove duplicates and sort
        return sorted(list(set(v)))


class ReminderResponse(BaseModel):
    """Schema for reminder response."""

    id: UUID
    plan_id: UUID
    reminder_time: str  # Returned as string in HH:MM:SS format
    frequency: str
    days_of_week: Optional[List[int]] = None
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, reminder):
        """Convert ORM model to response schema."""
        return cls(
            id=reminder.id,
            plan_id=reminder.plan_id,
            reminder_time=str(reminder.reminder_time),
            frequency=reminder.frequency.value if hasattr(reminder.frequency, "value") else reminder.frequency,
            days_of_week=reminder.days_of_week,
            is_enabled=reminder.is_enabled,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at,
        )
