"""Add workout_log table

Revision ID: 003
Revises: 002
Create Date: 2025-11-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create workout_log table."""
    op.create_table(
        'workout_log',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('workout_date', sa.Date(), nullable=False),
        sa.Column('workout_name', sa.String(length=100), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('calories_burned', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workout_log_user_id', 'workout_log', ['user_id'])
    op.create_index('ix_workout_log_workout_date', 'workout_log', ['workout_date'])


def downgrade() -> None:
    """Drop workout_log table."""
    op.drop_index('ix_workout_log_workout_date', 'workout_log')
    op.drop_index('ix_workout_log_user_id', 'workout_log')
    op.drop_table('workout_log')
