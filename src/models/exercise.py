"""Exercise model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Enum, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.types import GUID
import enum


class ExerciseIntensity(str, enum.Enum):
    """Exercise intensity enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Exercise(Base):
    """Exercise model."""

    __tablename__ = "exercise"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    plan_id = Column(
        GUID(), ForeignKey("fitness_plan.id"), nullable=False, index=True
    )
    name = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    repetitions = Column(Integer, nullable=True)
    intensity = Column(
        Enum(ExerciseIntensity, native_enum=False, length=20),
        nullable=False,
        default=ExerciseIntensity.MEDIUM,
    )
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        CheckConstraint("duration_minutes IS NULL OR duration_minutes > 0", name="check_duration_positive"),
        CheckConstraint("repetitions IS NULL OR repetitions > 0", name="check_repetitions_positive"),
    )

    # Relationships
    plan = relationship("FitnessPlan", back_populates="exercises")

    def __repr__(self) -> str:
        return f"<Exercise(id={self.id}, name={self.name}, intensity={self.intensity})>"
