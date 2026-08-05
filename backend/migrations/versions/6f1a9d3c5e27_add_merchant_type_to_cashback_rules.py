"""add merchant_type to cashback_rules

Revision ID: 6f1a9d3c5e27
Revises: 9c2f4b7e1a83
Create Date: 2026-08-05 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6f1a9d3c5e27'
down_revision: Union[str, None] = '9c2f4b7e1a83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('cashback_rules', sa.Column('merchant_type', sa.String(), nullable=True))
    op.create_index(op.f('ix_cashback_rules_merchant_type'), 'cashback_rules', ['merchant_type'])


def downgrade() -> None:
    op.drop_index(op.f('ix_cashback_rules_merchant_type'), table_name='cashback_rules')
    op.drop_column('cashback_rules', 'merchant_type')
