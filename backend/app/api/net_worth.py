import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, require_owner_or_co_owner
from app.core.db import get_session
from app.models._common import utcnow
from app.models.net_worth import NetWorthAccount, NetWorthAccountType, NetWorthBalance, NetWorthSnapshot
from app.models.user import User
from app.schemas.net_worth import (
    NetWorthAccountCreate,
    NetWorthAccountPublic,
    NetWorthAccountUpdate,
    NetWorthBalancePublic,
    NetWorthSnapshotCreate,
    NetWorthSnapshotPublic,
)

router = APIRouter(tags=["net-worth"])

_ZERO = Decimal("0")


async def _get_owned_active_account_or_404(session: AsyncSession, user: User, account_id: uuid.UUID) -> NetWorthAccount:
    account = await session.get(NetWorthAccount, account_id)
    if account is None or account.user_id != household_owner_id(user) or not account.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Net worth account not found")
    return account


@router.get("/net-worth-accounts", response_model=list[NetWorthAccountPublic])
async def list_net_worth_accounts(
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> list[NetWorthAccount]:
    statement = select(NetWorthAccount).where(
        NetWorthAccount.user_id == household_owner_id(user), NetWorthAccount.is_active == True  # noqa: E712
    )
    return (await session.exec(statement)).all()


@router.post("/net-worth-accounts", response_model=NetWorthAccountPublic, status_code=status.HTTP_201_CREATED)
async def create_net_worth_account(
    body: NetWorthAccountCreate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> NetWorthAccount:
    account = NetWorthAccount(user_id=household_owner_id(user), name=body.name, type=body.type)
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account


@router.patch("/net-worth-accounts/{account_id}", response_model=NetWorthAccountPublic)
async def update_net_worth_account(
    account_id: uuid.UUID,
    body: NetWorthAccountUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> NetWorthAccount:
    account = await _get_owned_active_account_or_404(session, user, account_id)
    updates = body.model_dump(exclude_unset=True)
    nulled_fields = {field for field, value in updates.items() if value is None}
    if nulled_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"These fields cannot be cleared: {', '.join(sorted(nulled_fields))}",
        )
    for field, value in updates.items():
        setattr(account, field, value)
    account.updated_at = utcnow()
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account


@router.delete("/net-worth-accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_net_worth_account(
    account_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    account = await _get_owned_active_account_or_404(session, user, account_id)
    account.is_active = False
    account.updated_at = utcnow()
    session.add(account)
    await session.commit()


def _to_balance_public(balance: NetWorthBalance, account: NetWorthAccount) -> NetWorthBalancePublic:
    return NetWorthBalancePublic(
        account_id=account.id,
        account_name=account.name,
        account_type=account.type,
        balance=balance.balance,
    )


async def _load_snapshot_balances(session: AsyncSession, snapshot_id: uuid.UUID) -> list[NetWorthBalancePublic]:
    balances_by_snapshot = await load_balances_by_snapshot(session, [snapshot_id])
    return balances_by_snapshot[snapshot_id]


async def load_balances_by_snapshot(
    session: AsyncSession, snapshot_ids: list[uuid.UUID]
) -> dict[uuid.UUID, list[NetWorthBalancePublic]]:
    balances_by_snapshot: dict[uuid.UUID, list[NetWorthBalancePublic]] = {sid: [] for sid in snapshot_ids}
    if not snapshot_ids:
        return balances_by_snapshot
    statement = (
        select(NetWorthBalance, NetWorthAccount)
        .join(NetWorthAccount, NetWorthAccount.id == NetWorthBalance.account_id)
        .where(NetWorthBalance.snapshot_id.in_(snapshot_ids))  # type: ignore[union-attr]
    )
    rows = (await session.exec(statement)).all()
    for balance, account in rows:
        balances_by_snapshot[balance.snapshot_id].append(_to_balance_public(balance, account))
    return balances_by_snapshot


def to_snapshot_public(snapshot: NetWorthSnapshot, balances: list[NetWorthBalancePublic]) -> NetWorthSnapshotPublic:
    return NetWorthSnapshotPublic(
        id=snapshot.id,
        snapshot_date=snapshot.snapshot_date,
        total_assets=snapshot.total_assets,
        total_liabilities=snapshot.total_liabilities,
        net_worth=snapshot.net_worth,
        notes=snapshot.notes,
        balances=balances,
    )


@router.post("/net-worth-snapshots", response_model=NetWorthSnapshotPublic, status_code=status.HTTP_201_CREATED)
async def create_net_worth_snapshot(
    body: NetWorthSnapshotCreate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> NetWorthSnapshotPublic:
    """PRD §24.11: 'manual asset/liability entry, monthly snapshot'. A snapshot
    must cover every active account — a partial snapshot would silently
    understate net worth, which the PRD's total-based framing (§18.7:
    Net Worth = Total Assets − Total Liabilities) doesn't intend."""
    owner_id = household_owner_id(user)
    accounts = (
        await session.exec(select(NetWorthAccount).where(NetWorthAccount.user_id == owner_id, NetWorthAccount.is_active == True))  # noqa: E712
    ).all()
    if not accounts:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No active net worth accounts to snapshot")
    accounts_by_id = {account.id: account for account in accounts}

    submitted_ids = {entry.account_id for entry in body.balances}
    active_ids = set(accounts_by_id)
    if submitted_ids != active_ids:
        missing = active_ids - submitted_ids
        unknown = submitted_ids - active_ids
        detail = []
        if missing:
            detail.append(f"missing balances for accounts: {', '.join(str(i) for i in missing)}")
        if unknown:
            detail.append(f"unknown or inactive accounts: {', '.join(str(i) for i in unknown)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="; ".join(detail))

    total_assets = _ZERO
    total_liabilities = _ZERO
    for entry in body.balances:
        account = accounts_by_id[entry.account_id]
        if account.type == NetWorthAccountType.ASSET:
            total_assets += entry.balance
        else:
            total_liabilities += entry.balance

    snapshot = NetWorthSnapshot(
        user_id=owner_id,
        snapshot_date=body.snapshot_date,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=total_assets - total_liabilities,
        notes=body.notes,
    )
    session.add(snapshot)
    await session.flush()
    for entry in body.balances:
        session.add(NetWorthBalance(account_id=entry.account_id, snapshot_id=snapshot.id, balance=entry.balance))
    await session.commit()
    await session.refresh(snapshot)

    balances = await _load_snapshot_balances(session, snapshot.id)
    return to_snapshot_public(snapshot, balances)


@router.get("/net-worth-snapshots", response_model=list[NetWorthSnapshotPublic])
async def list_net_worth_snapshots(
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> list[NetWorthSnapshotPublic]:
    snapshots = (
        await session.exec(
            select(NetWorthSnapshot)
            .where(NetWorthSnapshot.user_id == household_owner_id(user))
            .order_by(NetWorthSnapshot.snapshot_date)
        )
    ).all()
    if not snapshots:
        return []

    balances_by_snapshot = await load_balances_by_snapshot(session, [snapshot.id for snapshot in snapshots])
    return [to_snapshot_public(snapshot, balances_by_snapshot[snapshot.id]) for snapshot in snapshots]
