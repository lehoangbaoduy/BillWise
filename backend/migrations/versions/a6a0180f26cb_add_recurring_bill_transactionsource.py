"""add 'Recurring Bill' value to transactionsource enum

Revision ID: a6a0180f26cb
Revises: c3d8f6a9e2b1
Create Date: 2026-08-04 20:56:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'a6a0180f26cb'
down_revision: Union[str, None] = 'c3d8f6a9e2b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # app.models.transaction.TransactionSource.RECURRING_BILL = "Recurring Bill"
    # was added to the model without a matching migration -- mark-paid's
    # auto-created transaction (app/api/recurring_bills.py) has been failing
    # with `invalid input value for enum transactionsource` ever since.
    op.execute("ALTER TYPE transactionsource ADD VALUE IF NOT EXISTS 'Recurring Bill'")


def downgrade() -> None:
    # Postgres has no DROP VALUE for enum types; removing one requires
    # rebuilding the type (create new type, cast column, drop old type,
    # rename) -- not worth the risk for a downgrade path. No-op.
    pass
