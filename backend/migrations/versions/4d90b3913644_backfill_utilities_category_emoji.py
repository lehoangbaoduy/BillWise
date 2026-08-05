"""backfill utilities category emoji

Revision ID: 4d90b3913644
Revises: 0030e1b6182d
Create Date: 2026-08-05 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '4d90b3913644'
down_revision: Union[str, None] = '0030e1b6182d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The seed tree (backend/app/seed/default_categories.py) now seeds Utilities
    # with an emoji for new accounts -- this backfills existing rows left blank
    # from before that change. Scoped to exact name + currently-NULL emoji so it
    # never touches a category the user has already customized.
    op.execute("UPDATE categories SET emoji = '🛠' WHERE name = 'Utilities' AND emoji IS NULL")


def downgrade() -> None:
    op.execute("UPDATE categories SET emoji = NULL WHERE name = 'Utilities' AND emoji = '🛠'")
