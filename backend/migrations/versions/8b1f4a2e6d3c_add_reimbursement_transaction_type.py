"""add reimbursement transaction type

Revision ID: 8b1f4a2e6d3c
Revises: 4c2f6187bef9
Create Date: 2026-08-04 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8b1f4a2e6d3c'
down_revision: Union[str, None] = '4c2f6187bef9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS 'Reimbursement'")
    op.add_column(
        'transactions',
        sa.Column('reimbursement_status', sa.String(), nullable=False, server_default='unpaid'),
    )
    op.add_column('transactions', sa.Column('reimbursement_paid_by', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('reimbursement_paid_at', sa.DateTime(timezone=True), nullable=True))
    # PRD §7.4 naming decision: the old labeling-only "Reimbursement" category
    # (predates this real transaction-type workflow) is retired in favor of
    # the new type. Soft-delete rather than hard-delete, matching this
    # table's existing is_active convention -- preserves category_id
    # references on any pre-existing transaction line items.
    op.execute("UPDATE categories SET is_active = false WHERE name = 'Reimbursement' AND is_default = true")


def downgrade() -> None:
    op.drop_column('transactions', 'reimbursement_paid_at')
    op.drop_column('transactions', 'reimbursement_paid_by')
    op.drop_column('transactions', 'reimbursement_status')
    # Postgres cannot remove a value from an existing enum type; the
    # 'Reimbursement' TransactionType member is left in place on downgrade,
    # consistent with how a6a0180f26cb handles the same limitation.
