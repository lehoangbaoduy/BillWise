import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models._common import optional_timestamp_field, required_timestamp_field


class PartnerPermission(SQLModel, table=True):
    __tablename__ = "partner_permissions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    partner_user_id: uuid.UUID = Field(foreign_key="users.id", unique=True, nullable=False)
    can_add_transactions: bool = False
    # Grants owner-level access to financial data (budgets, goals, categories,
    # payment methods, recurring bills, cashback, transactions, exports, net
    # worth, AI insights, receipt scanning) via require_owner_or_co_owner.
    # Deliberately does NOT extend to household administration (inviting or
    # removing partners, the audit log, account deletion), which stays gated
    # by require_owner alone.
    is_co_owner: bool = False
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)


class PartnerInviteToken(SQLModel, table=True):
    """Not in PRD §23's literal data model — the PRD's §21.3 invite flow requires a
    time-limited, token-gated pending state before a partner has a user account at
    all (they haven't chosen a password yet), which the steady-state
    partner_permissions table can't represent. Mirrors the established
    EmailVerificationToken/PasswordResetToken shape (app/models/user.py)."""

    __tablename__ = "partner_invite_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    invited_by_user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    email: str = Field(nullable=False)
    can_add_transactions: bool = False
    is_co_owner: bool = False
    token_hash: str = Field(unique=True, nullable=False)
    expires_at: datetime = required_timestamp_field()
    accepted_at: datetime | None = optional_timestamp_field()
    revoked_at: datetime | None = optional_timestamp_field()
    created_at: datetime = required_timestamp_field(default_now=True)
