"""add created_by_user_id to payment_methods/budgets/goals/recurring_bills, is_shared to budgets

Revision ID: c3d8f6a9e2b1
Revises: 9a2e7c4f1b6d
Create Date: 2026-08-04 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d8f6a9e2b1'
down_revision: Union[str, None] = '9a2e7c4f1b6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment_methods', sa.Column('created_by_user_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_payment_methods_created_by_user_id', 'payment_methods', 'users', ['created_by_user_id'], ['id']
    )

    op.add_column('budgets', sa.Column('created_by_user_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_budgets_created_by_user_id', 'budgets', 'users', ['created_by_user_id'], ['id'])
    op.add_column('budgets', sa.Column('is_shared', sa.Boolean(), nullable=False, server_default=sa.false()))
    # See the matching comment in 9a2e7c4f1b6d (payment_methods/recurring_bills):
    # every budget that existed before this feature was implicitly visible to
    # the whole household, so leaving pre-existing rows at the new-row default
    # (private) would silently hide them from a co-owner. Only rows created
    # after this migration get private-by-default, via the application layer.
    op.execute("UPDATE budgets SET is_shared = true")
    op.drop_constraint('uq_budget_category_period', 'budgets', type_='unique')
    # A plain multi-column unique constraint can't scope this: created_by_user_id
    # is NULL for the owner, and standard SQL treats every NULL as distinct from
    # every other NULL, so two owner-created rows for the same category/month
    # wouldn't collide. COALESCE-ing NULL to user_id (the owner's own id) closes
    # that gap -- see app.models.budget.Budget's docstring.
    op.execute(
        "CREATE UNIQUE INDEX uq_budget_category_period ON budgets "
        "(user_id, category_id, month, year, COALESCE(created_by_user_id, user_id))"
    )

    op.add_column('savings_goals', sa.Column('created_by_user_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_savings_goals_created_by_user_id', 'savings_goals', 'users', ['created_by_user_id'], ['id']
    )

    op.add_column('recurring_bills', sa.Column('created_by_user_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_recurring_bills_created_by_user_id', 'recurring_bills', 'users', ['created_by_user_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_recurring_bills_created_by_user_id', 'recurring_bills', type_='foreignkey')
    op.drop_column('recurring_bills', 'created_by_user_id')

    op.drop_constraint('fk_savings_goals_created_by_user_id', 'savings_goals', type_='foreignkey')
    op.drop_column('savings_goals', 'created_by_user_id')

    op.execute("DROP INDEX uq_budget_category_period")
    op.create_unique_constraint('uq_budget_category_period', 'budgets', ['user_id', 'category_id', 'month', 'year'])
    op.drop_column('budgets', 'is_shared')
    op.drop_constraint('fk_budgets_created_by_user_id', 'budgets', type_='foreignkey')
    op.drop_column('budgets', 'created_by_user_id')

    op.drop_constraint('fk_payment_methods_created_by_user_id', 'payment_methods', type_='foreignkey')
    op.drop_column('payment_methods', 'created_by_user_id')
