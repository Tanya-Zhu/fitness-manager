"""Add gym exercise tables

Revision ID: 004
Revises: 003
Create Date: 2025-11-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create gym_exercise_log and gym_exercise_set tables."""
    # Create gym_exercise_log table
    op.create_table(
        'gym_exercise_log',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('workout_date', sa.Date(), nullable=False),
        sa.Column('exercise_name', sa.String(length=100), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_gym_exercise_log_user_id', 'gym_exercise_log', ['user_id'])
    op.create_index('ix_gym_exercise_log_workout_date', 'gym_exercise_log', ['workout_date'])

    # Create gym_exercise_set table
    op.create_table(
        'gym_exercise_set',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('gym_exercise_log_id', sa.String(length=36), nullable=False),
        sa.Column('set_number', sa.Integer(), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['gym_exercise_log_id'], ['gym_exercise_log.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_gym_exercise_set_gym_exercise_log_id', 'gym_exercise_set', ['gym_exercise_log_id'])


def downgrade() -> None:
    """Drop gym_exercise_log and gym_exercise_set tables."""
    op.drop_index('ix_gym_exercise_set_gym_exercise_log_id', table_name='gym_exercise_set')
    op.drop_table('gym_exercise_set')
    op.drop_index('ix_gym_exercise_log_workout_date', table_name='gym_exercise_log')
    op.drop_index('ix_gym_exercise_log_user_id', table_name='gym_exercise_log')
    op.drop_table('gym_exercise_log')
