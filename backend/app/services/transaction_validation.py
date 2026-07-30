from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.category import Category, CategoryType
from app.models.payment_method import PaymentMethod
from app.models.transaction import TransactionType
from app.models.user import User

_CENTS = Decimal("0.01")
EXPENSE_LIKE_TYPES = {TransactionType.EXPENSE, TransactionType.SAVING_EXPENSE}


def quantize(amount: Decimal) -> Decimal:
    return amount.quantize(_CENTS, rounding=ROUND_HALF_UP)


async def validate_payment_method(session: AsyncSession, user: User, payment_method_id: UUID) -> None:
    payment_method = await session.get(PaymentMethod, payment_method_id)
    if payment_method is None or payment_method.user_id != user.id or not payment_method.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid payment method")


async def validate_line_items(
    session: AsyncSession,
    user: User,
    transaction_type: TransactionType,
    total_amount: Decimal,
    line_items: list,
) -> None:
    """Shared by the Transactions router (manual entry/edit) and the Goals router's
    add-funds endpoint, which synthesizes a single-line-item transaction."""
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
        if category is None or category.user_id != user.id or not category.is_active:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid category")
        if expected_category_type is not None and category.category_type != expected_category_type:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Category type must be {expected_category_type.value} for this transaction type",
            )
