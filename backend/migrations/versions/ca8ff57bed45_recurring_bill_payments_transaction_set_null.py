"""recurring_bill_payments.transaction_id FK: RESTRICT -> SET NULL on delete

Revision ID: ca8ff57bed45
Revises: a6a0180f26cb
Create Date: 2026-08-04 22:40:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'ca8ff57bed45'
down_revision: Union[str, None] = 'a6a0180f26cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Defense-in-depth: app/api/transactions.py's delete_transaction now
    # explicitly reopens any linked recurring_bill_payments row before
    # deleting (see reopen_payments_for_deleted_transaction), so this
    # constraint is no longer hit through that path. But the FK had no ON
    # DELETE behavior at all (implicit RESTRICT), which raised a raw
    # ForeignKeyViolation -- a 500 that looks like CORS in the browser, since
    # a failed response never gets the CORS middleware's
    # Access-Control-Allow-Origin header -- for any other deletion path that
    # doesn't go through that endpoint.
    op.drop_constraint(
        'recurring_bill_payments_transaction_id_fkey', 'recurring_bill_payments', type_='foreignkey'
    )
    op.create_foreign_key(
        'recurring_bill_payments_transaction_id_fkey',
        'recurring_bill_payments', 'transactions', ['transaction_id'], ['id'], ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint(
        'recurring_bill_payments_transaction_id_fkey', 'recurring_bill_payments', type_='foreignkey'
    )
    op.create_foreign_key(
        'recurring_bill_payments_transaction_id_fkey',
        'recurring_bill_payments', 'transactions', ['transaction_id'], ['id'],
    )
