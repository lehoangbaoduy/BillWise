"""backfill categories is_shared to true

Revision ID: 02295b08cdbd
Revises: 6f1a9d3c5e27
Create Date: 2026-08-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '02295b08cdbd'
down_revision: Union[str, None] = '6f1a9d3c5e27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Categories are now always shared across the household -- the
    # private/shared distinction that Wallets/Budgets/Goals/RecurringBills
    # keep no longer applies to Category. Backfill any rows still marked
    # private from before this change (the column itself stays, so existing
    # rows/migrations aren't disturbed).
    op.execute("UPDATE categories SET is_shared = true WHERE is_shared = false")


def downgrade() -> None:
    # Not reversible -- which rows were private before the backfill is lost.
    pass
