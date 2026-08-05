"""add transaction_shares table

Revision ID: f3a7c9e2d5b8
Revises: 8b1f4a2e6d3c
Create Date: 2026-08-04 23:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f3a7c9e2d5b8'
down_revision: Union[str, None] = '8b1f4a2e6d3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'transaction_shares',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('transaction_id', sa.Uuid(), nullable=False),
        sa.Column('shared_with_user_id', sa.Uuid(), nullable=False),
        sa.Column('share_amount', sa.Numeric(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('settled_by', sa.String(), nullable=True),
        sa.Column('settled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_transaction_shares_transaction_id'), 'transaction_shares', ['transaction_id'])
    op.create_index(op.f('ix_transaction_shares_shared_with_user_id'), 'transaction_shares', ['shared_with_user_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_transaction_shares_shared_with_user_id'), table_name='transaction_shares')
    op.drop_index(op.f('ix_transaction_shares_transaction_id'), table_name='transaction_shares')
    op.drop_table('transaction_shares')
