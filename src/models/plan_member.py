"""Plan member model for shared plans."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.types import GUID


class PlanMember(Base):
    """Plan member model for tracking shared plan participants."""

    __tablename__ = "plan_member"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    plan_id = Column(GUID(), ForeignKey("fitness_plan.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    invited_by = Column(GUID(), ForeignKey("user.id"), nullable=True)  # Who invited this user
    joined_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    plan = relationship("FitnessPlan")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    # Ensure a user can only join a plan once
    __table_args__ = (
        UniqueConstraint('plan_id', 'user_id', name='uq_plan_member'),
    )

    def __repr__(self) -> str:
        return f"<PlanMember(plan_id={self.plan_id}, user_id={self.user_id})>"
