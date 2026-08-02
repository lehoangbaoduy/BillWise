from datetime import date as date_type
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id
from app.models.category import Category, CategoryType
from app.models.goal import SavingsGoal
from app.models.payment_method import PaymentMethod
from app.models.transaction import Transaction, TransactionLineItem, TransactionSource, TransactionType
from app.models.user import User, UserRole
from app.schemas.transaction import TransactionCreate, TransactionLineItemPublic, TransactionPublic

_CENTS = Decimal("0.01")
EXPENSE_LIKE_TYPES = {TransactionType.EXPENSE, TransactionType.SAVING_EXPENSE}
GOAL_ELIGIBLE_TYPES = {TransactionType.SAVING_EXPENSE, TransactionType.ADJUSTMENT}


def quantize(amount: Decimal) -> Decimal:
    return amount.quantize(_CENTS, rounding=ROUND_HALF_UP)


async def validate_payment_method(session: AsyncSession, user: User, payment_method_id: UUID) -> None:
    """Payment methods stay owner-managed regardless of household sharing (PRD
    §21.4), but a partner permitted to add transactions still selects from the
    household's existing payment methods — scoped by household_owner_id, not
    the acting user's own id, so this check passes identically for owner and
    partner callers."""
    owner_id = household_owner_id(user)
    payment_method = await session.get(PaymentMethod, payment_method_id)
    if payment_method is None or payment_method.user_id != owner_id or not payment_method.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid payment method")


async def validate_goal(
    session: AsyncSession, user: User, transaction_type: TransactionType, goal_id: UUID | None
) -> None:
    """Shared by the Transactions router and the OCR confirm-transaction endpoint.
    A partner may only contribute to a goal shared with them (PRD §21.4: goals
    follow the same is_shared pattern as categories)."""
    if goal_id is None:
        return
    if transaction_type not in GOAL_ELIGIBLE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="goal_id is only valid for Saving expense or Adjustment transactions",
        )
    owner_id = household_owner_id(user)
    goal = await session.get(SavingsGoal, goal_id)
    if goal is None or goal.user_id != owner_id or not goal.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid goal")
    if user.role == UserRole.PARTNER and not goal.is_shared:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid goal")


async def detect_duplicate(
    session: AsyncSession,
    user: User,
    merchant: str,
    date: date_type,
    total_amount: Decimal,
    payment_method_id: UUID,
    exclude_id: UUID | None = None,
) -> bool:
    """Shared by the Transactions router and the OCR confirm-transaction endpoint.
    Scoped to the whole household's ledger, not just the acting user's own
    entries, since a partner and owner share one transaction list."""
    owner_id = household_owner_id(user)
    conditions = [
        Transaction.user_id == owner_id,
        Transaction.merchant == merchant,
        Transaction.date == date,
        Transaction.total_amount == total_amount,
        Transaction.payment_method_id == payment_method_id,
    ]
    if exclude_id is not None:
        conditions.append(Transaction.id != exclude_id)
    statement = select(Transaction).where(and_(*conditions))
    result = await session.exec(statement)
    return result.first() is not None


async def validate_line_items(
    session: AsyncSession,
    user: User,
    transaction_type: TransactionType,
    total_amount: Decimal,
    line_items: list,
) -> None:
    """Shared by the Transactions router (manual entry/edit) and the Goals router's
    add-funds endpoint, which synthesizes a single-line-item transaction. A
    partner permitted to add transactions may only use categories shared with
    them (PRD §21.4)."""
    owner_id = household_owner_id(user)
    line_item_sum = sum((item.amount for item in line_items), Decimal("0"))
    if quantize(line_item_sum) != quantize(total_amount):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Line item amounts must sum to the transaction total",
        )

    if transaction_type != TransactionType.ADJUSTMENT and total_amount < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only Adjustment transactions may have a negative amount",
        )

    expected_category_type = (
        CategoryType.EXPENSE
        if transaction_type in EXPENSE_LIKE_TYPES
        else CategoryType.INCOME
        if transaction_type == TransactionType.INCOME
        else None
    )
    for item in line_items:
        category = await session.get(Category, item.category_id)
        if category is None or category.user_id != owner_id or not category.is_active:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid category")
        if user.role == UserRole.PARTNER and not category.is_shared:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid category")
        if expected_category_type is not None and category.category_type != expected_category_type:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Category type must be {expected_category_type.value} for this transaction type",
            )


async def load_line_items(session: AsyncSession, transaction_id: UUID) -> list[TransactionLineItem]:
    """Shared by the Transactions router and the OCR confirm-transaction endpoint."""
    statement = select(TransactionLineItem).where(TransactionLineItem.transaction_id == transaction_id)
    return (await session.exec(statement)).all()


async def to_transaction_public(
    session: AsyncSession, transaction: Transaction, possible_duplicate: bool = False
) -> TransactionPublic:
    """Shared by the Transactions router and the OCR confirm-transaction endpoint."""
    line_items = await load_line_items(session, transaction.id)
    return TransactionPublic(
        id=transaction.id,
        payment_method_id=transaction.payment_method_id,
        goal_id=transaction.goal_id,
        date=transaction.date,
        merchant=transaction.merchant,
        description=transaction.description,
        total_amount=transaction.total_amount,
        transaction_type=transaction.transaction_type,
        source=transaction.source,
        notes=transaction.notes,
        line_items=[TransactionLineItemPublic.model_validate(item) for item in line_items],
        possible_duplicate=possible_duplicate,
        created_by_user_id=transaction.created_by_user_id,
    )


async def create_transaction_record(
    session: AsyncSession, user: User, body: TransactionCreate, source: TransactionSource
) -> tuple[Transaction, bool]:
    """Validates and persists a Transaction plus its TransactionLineItems. Shared by manual
    entry (POST /transactions), OCR confirmation (POST /ocr/confirm-transaction, owner-only),
    and now a permitted partner's manual entry — the only difference between call sites is
    which `source` value gets recorded. `Transaction.user_id` is always the household owner's
    id (see household_owner_id); `created_by_user_id` separately records a partner creator."""
    await validate_payment_method(session, user, body.payment_method_id)
    await validate_line_items(session, user, body.transaction_type, body.total_amount, body.line_items)
    await validate_goal(session, user, body.transaction_type, body.goal_id)

    owner_id = household_owner_id(user)
    possible_duplicate = await detect_duplicate(
        session, user, body.merchant, body.date, body.total_amount, body.payment_method_id
    )

    transaction = Transaction(
        user_id=owner_id,
        created_by_user_id=user.id if user.id != owner_id else None,
        payment_method_id=body.payment_method_id,
        goal_id=body.goal_id,
        date=body.date,
        merchant=body.merchant,
        description=body.description,
        total_amount=body.total_amount,
        transaction_type=body.transaction_type,
        source=source,
        notes=body.notes,
    )
    session.add(transaction)
    await session.flush()

    for item in body.line_items:
        session.add(
            TransactionLineItem(
                transaction_id=transaction.id,
                category_id=item.category_id,
                item_name=item.item_name,
                amount=item.amount,
                quantity=item.quantity,
                notes=item.notes,
            )
        )
    await session.commit()
    await session.refresh(transaction)
    return transaction, possible_duplicate
