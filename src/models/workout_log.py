"""Workout log model for tracking free-form exercise sessions."""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, Date, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.types import GUID


class WorkoutLog(Base):
    """Workout log model for tracking individual exercise sessions."""

    __tablename__ = "workout_log"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID(), ForeignKey("user.id"), nullable=False, index=True
    )
    workout_date = Column(Date, nullable=False, index=True, default=date.today)
    workout_name = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=False)  # Duration in minutes
    calories_burned = Column(Float, nullable=True)  # Calories burned (optional)
    notes = Column(Text, nullable=True)  # Optional notes about the workout
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="workout_logs")

    def __repr__(self) -> str:
        return f"<WorkoutLog(id={self.id}, user_id={self.user_id}, workout_name={self.workout_name}, date={self.workout_date})>"
