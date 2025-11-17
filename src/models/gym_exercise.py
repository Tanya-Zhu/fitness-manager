"""Database models for gym exercise tracking."""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, Text, Date, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.types import GUID


class GymExerciseLog(Base):
    """Gym exercise log model for tracking strength training."""
    __tablename__ = "gym_exercise_log"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    workout_date = Column(Date, nullable=False, index=True, default=date.today)
    exercise_name = Column(String(100), nullable=False)  # 器械名称或动作名称
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="gym_exercise_logs")
    sets = relationship("GymExerciseSet", back_populates="exercise", cascade="all, delete-orphan", order_by="GymExerciseSet.set_number")

    def __repr__(self):
        return f"<GymExerciseLog {self.exercise_name} on {self.workout_date}>"


class GymExerciseSet(Base):
    """Gym exercise set model for tracking individual sets."""
    __tablename__ = "gym_exercise_set"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    gym_exercise_log_id = Column(GUID(), ForeignKey("gym_exercise_log.id", ondelete="CASCADE"), nullable=False, index=True)
    set_number = Column(Integer, nullable=False)  # 第几组 (1, 2, 3, ...)
    reps = Column(Integer, nullable=False)  # 次数
    weight = Column(Float, nullable=True)  # 重量（kg）- 可选
    notes = Column(Text, nullable=True)  # 备注 - 可选
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    exercise = relationship("GymExerciseLog", back_populates="sets")

    def __repr__(self):
        return f"<GymExerciseSet {self.set_number}: {self.reps} reps @ {self.weight}kg>"
