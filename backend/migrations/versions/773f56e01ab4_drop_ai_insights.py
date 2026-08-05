"""drop ai insights (PRD v2 Phase 4: feature removed entirely)

Revision ID: 773f56e01ab4
Revises: f3a7c9e2d5b8
Create Date: 2026-08-05 01:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '773f56e01ab4'
down_revision: Union[str, None] = 'f3a7c9e2d5b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f('ix_ai_insights_user_id'), table_name='ai_insights')
    op.drop_table('ai_insights')
    sa.Enum(name='aiinsighttype').drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    aiinsighttype = sa.Enum(
        'category_spending_change', 'over_budget_alert', 'multi_month_trend', 'top_cashback_card',
        'recurring_bill_share', 'cash_flow_change', 'goal_progress', name='aiinsighttype',
    )
    aiinsighttype.create(op.get_bind(), checkfirst=True)
    op.create_table(
        'ai_insights',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('insight_type', aiinsighttype, nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('supporting_data', sa.JSON(), nullable=False),
        sa.Column('is_dismissed', sa.Boolean(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ai_insights_user_id'), 'ai_insights', ['user_id'], unique=False)
