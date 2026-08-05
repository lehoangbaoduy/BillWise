"""add merchants table, backfilled from existing transaction merchants

Revision ID: 9c2f4b7e1a83
Revises: 4d90b3913644
Create Date: 2026-08-05 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9c2f4b7e1a83'
down_revision: Union[str, None] = '4d90b3913644'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'merchants',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_merchants_user_id'), 'merchants', ['user_id'])
    op.create_index(op.f('ix_merchants_name'), 'merchants', ['name'])

    # Backfill one Merchant row per distinct (user_id, lower(merchant)) already
    # in use across existing transactions -- without this, switching the
    # merchant picker's data source from "distinct transaction.merchant
    # strings" to this new table would silently drop every merchant a
    # household has already used. DISTINCT ON with this ORDER BY keeps the
    # first-seen (earliest by date) casing when the same name appears with
    # different capitalization across transactions.
    op.execute(
        """
        INSERT INTO merchants (id, user_id, name, is_shared, is_active, created_at, updated_at)
        SELECT gen_random_uuid(), sub.user_id, sub.merchant, true, true, now(), now()
        FROM (
            SELECT DISTINCT ON (t.user_id, lower(t.merchant)) t.user_id, t.merchant
            FROM transactions t
            ORDER BY t.user_id, lower(t.merchant), t.date ASC
        ) sub
        """
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_merchants_name'), table_name='merchants')
    op.drop_index(op.f('ix_merchants_user_id'), table_name='merchants')
    op.drop_table('merchants')
