"""Add fitness_plan and exercise tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create fitness_plan and exercise tables."""
    # Create fitness_plan table
    op.create_table(
        'fitness_plan',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_fitness_plan_user_id', 'fitness_plan', ['user_id'])

    # Create exercise table
    op.create_table(
        'exercise',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('repetitions', sa.Integer(), nullable=True),
        sa.Column('intensity', sa.String(length=20), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.CheckConstraint('duration_minutes IS NULL OR duration_minutes > 0', name='check_duration_positive'),
        sa.CheckConstraint('repetitions IS NULL OR repetitions > 0', name='check_repetitions_positive'),
        sa.ForeignKeyConstraint(['plan_id'], ['fitness_plan.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exercise_plan_id', 'exercise', ['plan_id'])

    # Create reminder table (placeholder for Phase 4)
    op.create_table(
        'reminder',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('reminder_time', sa.Time(), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('days_of_week', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['fitness_plan.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reminder_plan_id', 'reminder', ['plan_id'])


def downgrade() -> None:
    """Drop fitness_plan and exercise tables."""
    op.drop_index('ix_reminder_plan_id', table_name='reminder')
    op.drop_table('reminder')
    op.drop_index('ix_exercise_plan_id', table_name='exercise')
    op.drop_table('exercise')
    op.drop_index('ix_fitness_plan_user_id', table_name='fitness_plan')
    op.drop_table('fitness_plan')
