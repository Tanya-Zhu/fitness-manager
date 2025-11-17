"""Add plan member table for shared plans

Revision ID: 006
Revises: 005
Create Date: 2025-11-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create plan_member table."""
    op.create_table(
        'plan_member',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('invited_by', sa.String(length=36), nullable=True),
        sa.Column('joined_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['fitness_plan.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plan_id', 'user_id', name='uq_plan_member')
    )
    op.create_index('ix_plan_member_plan_id', 'plan_member', ['plan_id'])
    op.create_index('ix_plan_member_user_id', 'plan_member', ['user_id'])


def downgrade() -> None:
    """Drop plan_member table."""
    op.drop_index('ix_plan_member_user_id', table_name='plan_member')
    op.drop_index('ix_plan_member_plan_id', table_name='plan_member')
    op.drop_table('plan_member')
