import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.payment_method import PaymentMethodType


class TopCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: uuid.UUID
    name: str
    amount: Decimal


class TopPaymentMethod(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_method_id: uuid.UUID
    name: str
    amount: Decimal


class BudgetStatusItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: uuid.UUID
    category_name: str
    budget_amount: Decimal
    actual_amount: Decimal
    percentage_used: Decimal | None
    is_over_budget: bool


class PreviousMonthComparison(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    previous_month: int
    previous_year: int
    previous_total_expenses: Decimal
    change_amount: Decimal
    change_percentage: Decimal | None


class MonthlyOverview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: int
    year: int
    total_income: Decimal
    total_expenses: Decimal
    net_cash_flow: Decimal
    top_category: TopCategory | None
    top_payment_method: TopPaymentMethod | None
    budget_status: list[BudgetStatusItem]
    comparison_vs_previous_month: PreviousMonthComparison


class MonthSpend(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: int
    total: Decimal


class CategorySpend(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: uuid.UUID
    name: str
    total: Decimal


class PaymentMethodSpend(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_method_id: uuid.UUID
    name: str
    total: Decimal


class YearlyOverview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: int
    total_yearly_spending: Decimal
    spend_by_month: list[MonthSpend]
    income_by_month: list[MonthSpend]
    spend_by_category: list[CategorySpend]
    spend_by_payment_method: list[PaymentMethodSpend]
    average_month: Decimal
    highest_month: MonthSpend
    lowest_month: MonthSpend
    ytd_savings_total: Decimal


class CategoryBreakdownItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: uuid.UUID
    name: str
    parent_category_id: uuid.UUID | None
    amount: Decimal
    percentage_of_total: Decimal
    budget_amount: Decimal | None
    budget_percentage_used: Decimal | None
    is_over_budget: bool


class PaymentMethodBreakdownItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_method_id: uuid.UUID
    name: str
    type: PaymentMethodType
    amount: Decimal
    transaction_count: int
    average_transaction: Decimal
    current_balance: Decimal | None


class CashFlow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: int
    year: int
    income: Decimal
    expenses: Decimal
    net: Decimal
