"""add is_co_owner to partner permissions and invite tokens

Revision ID: 7f3c9a1d2b4e
Revises: 30bb18050e95
Create Date: 2026-08-03 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7f3c9a1d2b4e'
down_revision: Union[str, None] = '30bb18050e95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'partner_permissions',
        sa.Column('is_co_owner', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        'partner_invite_tokens',
        sa.Column('is_co_owner', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column('partner_invite_tokens', 'is_co_owner')
    op.drop_column('partner_permissions', 'is_co_owner')
