"""add cashback_rule_id to cashback_records

Revision ID: 4c2f6187bef9
Revises: ca8ff57bed45
Create Date: 2026-08-04 22:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4c2f6187bef9'
down_revision: Union[str, None] = 'ca8ff57bed45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('cashback_records', sa.Column('cashback_rule_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_cashback_records_cashback_rule_id', 'cashback_records', 'cashback_rules',
        ['cashback_rule_id'], ['id'], ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_cashback_records_cashback_rule_id', 'cashback_records', type_='foreignkey')
    op.drop_column('cashback_records', 'cashback_rule_id')
