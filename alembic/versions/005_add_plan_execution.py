"""Add plan execution tables

Revision ID: 005
Revises: 004
Create Date: 2025-11-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create plan_execution and exercise_execution tables."""
    # Create plan_execution table
    op.create_table(
        'plan_execution',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('execution_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['fitness_plan.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plan_execution_plan_id', 'plan_execution', ['plan_id'])
    op.create_index('ix_plan_execution_user_id', 'plan_execution', ['user_id'])
    op.create_index('ix_plan_execution_execution_date', 'plan_execution', ['execution_date'])

    # Create exercise_execution table
    op.create_table(
        'exercise_execution',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_execution_id', sa.String(length=36), nullable=False),
        sa.Column('exercise_id', sa.String(length=36), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('actual_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('actual_repetitions', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['plan_execution_id'], ['plan_execution.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercise.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exercise_execution_plan_execution_id', 'exercise_execution', ['plan_execution_id'])
    op.create_index('ix_exercise_execution_exercise_id', 'exercise_execution', ['exercise_id'])


def downgrade() -> None:
    """Drop plan_execution and exercise_execution tables."""
    op.drop_index('ix_exercise_execution_exercise_id', table_name='exercise_execution')
    op.drop_index('ix_exercise_execution_plan_execution_id', table_name='exercise_execution')
    op.drop_table('exercise_execution')
    op.drop_index('ix_plan_execution_execution_date', table_name='plan_execution')
    op.drop_index('ix_plan_execution_user_id', table_name='plan_execution')
    op.drop_index('ix_plan_execution_plan_id', table_name='plan_execution')
    op.drop_table('plan_execution')
