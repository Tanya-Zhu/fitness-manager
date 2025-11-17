"""Plan execution models for tracking workout completion."""
import uuid
from datetime import date, datetime
from sqlalchemy import Column, String, Boolean, Integer, Date, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.types import GUID


class PlanExecution(Base):
    """Plan execution model for tracking when a plan was performed."""

    __tablename__ = "plan_execution"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    plan_id = Column(GUID(), ForeignKey("fitness_plan.id"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("user.id"), nullable=False, index=True)
    execution_date = Column(Date, nullable=False, default=date.today, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    plan = relationship("FitnessPlan")
    user = relationship("User")
    exercise_executions = relationship(
        "ExerciseExecution", back_populates="plan_execution", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PlanExecution(id={self.id}, plan_id={self.plan_id}, date={self.execution_date})>"


class ExerciseExecution(Base):
    """Exercise execution model for tracking individual exercise completion."""

    __tablename__ = "exercise_execution"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    plan_execution_id = Column(
        GUID(), ForeignKey("plan_execution.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exercise_id = Column(GUID(), ForeignKey("exercise.id"), nullable=False, index=True)
    completed = Column(Boolean, nullable=False, default=True)
    actual_duration_minutes = Column(Integer, nullable=True)
    actual_repetitions = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    plan_execution = relationship("PlanExecution", back_populates="exercise_executions")
    exercise = relationship("Exercise")

    def __repr__(self) -> str:
        return f"<ExerciseExecution(id={self.id}, exercise_id={self.exercise_id}, completed={self.completed})>"
