import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.models._common import optional_timestamp_field, required_timestamp_field


class TransactionShareStatus(StrEnum):
    PENDING = "pending"
    SETTLED = "settled"


class TransactionShare(SQLModel, table=True):
    __tablename__ = "transaction_shares"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    transaction_id: uuid.UUID = Field(foreign_key="transactions.id", nullable=False, index=True, ondelete="CASCADE")
    shared_with_user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    share_amount: Decimal
    # Plain string, not enum_field's native Postgres ENUM -- same rationale as
    # Transaction.reimbursement_status (only two fixed values, avoids the
    # ALTER TYPE ADD VALUE migration class of bug).
    status: str = Field(default=TransactionShareStatus.PENDING.value)
    # Only meaningful once status == "settled". Free-text "who" (may differ
    # from the recipient, e.g. paid in cash to someone else in the household)
    # plus "when", same pattern as Transaction.reimbursement_paid_by/_at.
    settled_by: str | None = None
    settled_at: datetime | None = optional_timestamp_field()
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
