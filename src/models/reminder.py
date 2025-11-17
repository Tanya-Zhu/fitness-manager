"""Reminder model (placeholder for Phase 4 - User Story 3)."""
import uuid
from datetime import datetime, time
from sqlalchemy import Column, Boolean, Time, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.types import GUID, JSON
import enum


class ReminderFrequency(str, enum.Enum):
    """Reminder frequency enumeration."""

    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class Reminder(Base):
    """Reminder model."""

    __tablename__ = "reminder"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    plan_id = Column(
        GUID(), ForeignKey("fitness_plan.id"), nullable=False, index=True
    )
    reminder_time = Column(Time, nullable=False)
    frequency = Column(
        Enum(ReminderFrequency, native_enum=False, length=20),
        nullable=False,
        default=ReminderFrequency.WEEKLY,
    )
    days_of_week = Column(JSON(), nullable=True)  # Array of integers [1-7]
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    plan = relationship("FitnessPlan", back_populates="reminders")

    def __repr__(self) -> str:
        return f"<Reminder(id={self.id}, plan_id={self.plan_id}, time={self.reminder_time})>"
