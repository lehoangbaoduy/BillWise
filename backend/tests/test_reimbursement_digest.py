from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from app.core.security import hash_password
from app.models._common import utcnow
from app.models.category import Category, CategoryType
from app.models.payment_method import PaymentMethod, PaymentMethodType
from app.models.transaction import Transaction, TransactionSource, TransactionType
from app.models.user import User, UserRole
from app.services.reimbursement_digest_service import send_unpaid_reimbursement_digest

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


async def _make_reimbursement(session, owner, tx_date, status="unpaid"):
    pm = PaymentMethod(user_id=owner.id, name="Cash", type=PaymentMethodType.CASH)
    session.add(pm)
    await session.flush()
    category = Category(user_id=owner.id, name="Grocery", category_type=CategoryType.EXPENSE)
    session.add(category)
    await session.flush()
    transaction = Transaction(
        user_id=owner.id,
        payment_method_id=pm.id,
        date=tx_date,
        merchant="Costco",
        total_amount="45.50",
        transaction_type=TransactionType.REIMBURSEMENT,
        source=TransactionSource.MANUAL,
        reimbursement_status=status,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


def _prior_month(today: date) -> date:
    return today.replace(day=1) - timedelta(days=1)


class TestSendUnpaidReimbursementDigest:
    async def test_emails_owner_with_unpaid_reimbursements_from_the_closed_month(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        today = date.today()
        await _make_reimbursement(session, owner, _prior_month(today))

        mock_sender = MagicMock()
        with patch("app.services.reimbursement_digest_service.get_email_sender", return_value=mock_sender):
            sent_count = await send_unpaid_reimbursement_digest(session, today=today)

        assert sent_count == 1
        mock_sender.send.assert_called_once()
        _, kwargs = mock_sender.send.call_args
        assert kwargs["to"] == owner.email
        assert "45.50" in kwargs["body"]

    async def test_ignores_already_paid_reimbursements(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        today = date.today()
        await _make_reimbursement(session, owner, _prior_month(today), status="paid")

        mock_sender = MagicMock()
        with patch("app.services.reimbursement_digest_service.get_email_sender", return_value=mock_sender):
            sent_count = await send_unpaid_reimbursement_digest(session, today=today)

        assert sent_count == 0
        mock_sender.send.assert_not_called()

    async def test_ignores_reimbursements_outside_the_closed_month(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        today = date.today()
        await _make_reimbursement(session, owner, today)

        mock_sender = MagicMock()
        with patch("app.services.reimbursement_digest_service.get_email_sender", return_value=mock_sender):
            sent_count = await send_unpaid_reimbursement_digest(session, today=today)

        assert sent_count == 0
        mock_sender.send.assert_not_called()
