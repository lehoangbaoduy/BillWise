"""add receipt_image_key to transactions (PRD v2 §7.2)

Revision ID: 0030e1b6182d
Revises: 773f56e01ab4
Create Date: 2026-08-05 02:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0030e1b6182d'
down_revision: Union[str, None] = '773f56e01ab4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('transactions', sa.Column('receipt_image_key', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('transactions', 'receipt_image_key')
