import os
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

os.environ.setdefault("DATABASE_URL", os.environ.get("TEST_DATABASE_URL", ""))
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("COOKIE_SECURE", "false")

from app.core.db import get_session  # noqa: E402
from app.core.rate_limit import limiter  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

# Schema setup/teardown uses a plain sync engine (psycopg3 supports both sync and
# async under the same "+psycopg" dialect) — DDL is a one-time bootstrap concern,
# kept separate from the per-test async engine so it doesn't need a session-scoped
# event loop.
_sync_engine = create_engine(TEST_DATABASE_URL)
async_engine = create_async_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    SQLModel.metadata.create_all(_sync_engine)
    yield
    SQLModel.metadata.drop_all(_sync_engine)


@pytest_asyncio.fixture
async def session():
    async with async_engine.connect() as connection:
        transaction = await connection.begin()
        db_session = AsyncSession(bind=connection, expire_on_commit=False)

        async def _get_session_override():
            yield db_session

        app.dependency_overrides[get_session] = _get_session_override
        yield db_session

        await db_session.close()
        await transaction.rollback()
        app.dependency_overrides.pop(get_session, None)


@pytest_asyncio.fixture
async def client(session):
    limiter.reset()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client


@pytest.fixture
def unique_email():
    return f"user-{uuid.uuid4().hex[:10]}@example.com"
