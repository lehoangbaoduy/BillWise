from datetime import date

from sqlmodel import select

from app.core.security import hash_password
from app.models._common import utcnow
from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.user import User, UserRole
from app.services.budget_renewal_service import renew_monthly_budgets

VALID_PASSWORD = "StrongPass123"


async def _create_verified_owner(session, email):
    user = User(
        email=email,
        password_hash=hash_password(VALID_PASSWORD),
        display_name="Jamie Owner",
        role=UserRole.OWNER,
        email_verified_at=utcnow(),
    )
    session.add(user)
    await session.flush()
    await session.commit()
    await session.refresh(user)
    return user


async def _make_category(session, user, name="Grocery"):
    category = Category(user_id=user.id, name=name, category_type=CategoryType.EXPENSE)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _budgets_for(session, user_id, month, year):
    statement = select(Budget).where(Budget.user_id == user_id, Budget.month == month, Budget.year == year)
    return (await session.exec(statement)).all()


class TestRenewMonthlyBudgets:
    async def test_creates_zero_dollar_row_for_prior_month_category(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        category = await _make_category(session, owner)
        session.add(Budget(user_id=owner.id, category_id=category.id, month=6, year=2026, budget_amount="250.00"))
        await session.commit()

        created_count = await renew_monthly_budgets(session, today=date(2026, 7, 1))

        assert created_count == 1
        rows = await _budgets_for(session, owner.id, 7, 2026)
        assert len(rows) == 1
        assert rows[0].budget_amount == 0
        assert rows[0].category_id == category.id

    async def test_does_not_affect_source_month(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        category = await _make_category(session, owner)
        session.add(Budget(user_id=owner.id, category_id=category.id, month=6, year=2026, budget_amount="250.00"))
        await session.commit()

        await renew_monthly_budgets(session, today=date(2026, 7, 1))

        source_rows = await _budgets_for(session, owner.id, 6, 2026)
        assert len(source_rows) == 1
        assert source_rows[0].budget_amount == 250

    async def test_idempotent_when_current_month_row_already_exists(self, session, unique_email):
        # Guards against the exact race the old lazy rollover was vulnerable to
        # (PRD v2 §8.2's "household opens Budgets before 00:05 UTC" case): a
        # row for the target month that already exists (whatever its amount)
        # must never be duplicated or overwritten by a re-run.
        owner = await _create_verified_owner(session, unique_email)
        category = await _make_category(session, owner)
        session.add(Budget(user_id=owner.id, category_id=category.id, month=6, year=2026, budget_amount="250.00"))
        session.add(Budget(user_id=owner.id, category_id=category.id, month=7, year=2026, budget_amount="80.00"))
        await session.commit()

        created_count = await renew_monthly_budgets(session, today=date(2026, 7, 1))

        assert created_count == 0
        rows = await _budgets_for(session, owner.id, 7, 2026)
        assert len(rows) == 1
        assert rows[0].budget_amount == 80

    async def test_running_twice_does_not_duplicate(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        category = await _make_category(session, owner)
        session.add(Budget(user_id=owner.id, category_id=category.id, month=6, year=2026, budget_amount="250.00"))
        await session.commit()

        first_run = await renew_monthly_budgets(session, today=date(2026, 7, 1))
        second_run = await renew_monthly_budgets(session, today=date(2026, 7, 1))

        assert first_run == 1
        assert second_run == 0
        rows = await _budgets_for(session, owner.id, 7, 2026)
        assert len(rows) == 1

    async def test_preserves_is_shared_and_creator(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        co_owner = await _create_verified_owner(session, f"co-owner-{unique_email}")
        category = await _make_category(session, owner)
        session.add(
            Budget(
                user_id=owner.id,
                created_by_user_id=co_owner.id,
                category_id=category.id,
                month=6,
                year=2026,
                budget_amount="150.00",
                is_shared=True,
            )
        )
        await session.commit()

        await renew_monthly_budgets(session, today=date(2026, 7, 1))

        rows = await _budgets_for(session, owner.id, 7, 2026)
        assert len(rows) == 1
        assert rows[0].created_by_user_id == co_owner.id
        assert rows[0].is_shared is True
        assert rows[0].budget_amount == 0

    async def test_across_year_boundary(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        category = await _make_category(session, owner)
        session.add(Budget(user_id=owner.id, category_id=category.id, month=12, year=2026, budget_amount="275.00"))
        await session.commit()

        created_count = await renew_monthly_budgets(session, today=date(2027, 1, 1))

        assert created_count == 1
        rows = await _budgets_for(session, owner.id, 1, 2027)
        assert len(rows) == 1
        assert rows[0].budget_amount == 0

    async def test_no_op_when_no_prior_month_budgets(self, session, unique_email):
        await _create_verified_owner(session, unique_email)
        created_count = await renew_monthly_budgets(session, today=date(2026, 7, 1))
        assert created_count == 0

    async def test_independent_across_households(self, session, unique_email):
        owner_a = await _create_verified_owner(session, unique_email)
        owner_b = await _create_verified_owner(session, f"other-{unique_email}")
        category_a = await _make_category(session, owner_a)
        category_b = await _make_category(session, owner_b)
        session.add(Budget(user_id=owner_a.id, category_id=category_a.id, month=6, year=2026, budget_amount="100.00"))
        session.add(Budget(user_id=owner_b.id, category_id=category_b.id, month=6, year=2026, budget_amount="200.00"))
        await session.commit()

        created_count = await renew_monthly_budgets(session, today=date(2026, 7, 1))

        assert created_count == 2
        assert len(await _budgets_for(session, owner_a.id, 7, 2026)) == 1
        assert len(await _budgets_for(session, owner_b.id, 7, 2026)) == 1
