"""add is_shared to payment_methods and recurring_bills

Revision ID: 9a2e7c4f1b6d
Revises: 7f3c9a1d2b4e
Create Date: 2026-08-04 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9a2e7c4f1b6d'
down_revision: Union[str, None] = '7f3c9a1d2b4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'payment_methods',
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        'recurring_bills',
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # The server_default above only governs future INSERTs that omit the column --
    # it also backfills every row that already existed when this migration ran.
    # Before this feature, every wallet/bill was implicitly visible to the whole
    # household, so leaving pre-existing rows at the new-row default (private)
    # would silently hide them from a co-owner/partner who could already see
    # them. Flip existing rows to shared to preserve current behavior; only
    # rows created after this migration get the private-by-default treatment,
    # via the application layer (schemas default is_shared to False).
    op.execute("UPDATE payment_methods SET is_shared = true")
    op.execute("UPDATE recurring_bills SET is_shared = true")


def downgrade() -> None:
    op.drop_column('recurring_bills', 'is_shared')
    op.drop_column('payment_methods', 'is_shared')
