"""Fitness plan model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Enum, TIMESTAMP, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.types import GUID
import enum


class PlanStatus(str, enum.Enum):
    """Plan status enumeration."""

    ACTIVE = "active"
    PAUSED = "paused"


class FitnessPlan(Base):
    """Fitness plan model."""

    __tablename__ = "fitness_plan"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("user.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(PlanStatus, native_enum=False, length=20),
        nullable=False,
        default=PlanStatus.ACTIVE,
    )
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="plans")
    exercises = relationship(
        "Exercise", back_populates="plan", cascade="all, delete-orphan", lazy="selectin"
    )
    reminders = relationship(
        "Reminder", back_populates="plan", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<FitnessPlan(id={self.id}, name={self.name}, status={self.status})>"
