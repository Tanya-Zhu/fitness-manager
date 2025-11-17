"""User model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.types import GUID


class User(Base):
    """User model for authentication."""

    __tablename__ = "user"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    workout_logs = relationship("WorkoutLog", back_populates="user", lazy="select")
    gym_exercise_logs = relationship("GymExerciseLog", back_populates="user", lazy="select")
    plans = relationship("FitnessPlan", back_populates="user", lazy="select")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
