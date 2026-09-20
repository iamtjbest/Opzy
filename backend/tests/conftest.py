import os
from collections.abc import AsyncGenerator
from urllib.parse import urlsplit

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.deps import get_sender
from app.core.config import get_settings
from app.core.db import build_engine_args, get_db
from app.email import EmailMessage
from app.main import app
from app.models import (
    Opportunity,
    OpportunityMatch,
    RateLimitHit,
    UserOpportunityAction,
)


LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "db"}


def _test_database_url() -> str:
    """The database tests may use — a local one, unless explicitly overridden.

    Tests write real rows (rolled back afterwards), so pointing `.env` at Supabase would
    aim the suite at production data. Refuse rather than trust the rollback.
    """
    url = os.getenv("TEST_DATABASE_URL") or get_settings().database_url
    host = urlsplit(url).hostname
    if host not in LOCAL_HOSTS and os.getenv("ALLOW_NONLOCAL_TEST_DB") != "1":
        pytest.exit(
            f"Refusing to run tests against non-local database host {host!r}. "
            "Point DATABASE_URL at the local Docker Postgres, set TEST_DATABASE_URL, "
            "or set ALLOW_NONLOCAL_TEST_DB=1 if you really mean it.",
            returncode=1,
        )
    return url


class FakeSender:
    """Collects emails instead of sending them."""

    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> None:
        self.sent.append(message)


@pytest.fixture
async def fake_sender() -> FakeSender:
    return FakeSender()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # A fresh engine per test: asyncpg connections are bound to the event loop that opened
    # them, and pytest-asyncio gives each test its own loop.
    url, connect_args, engine_kwargs = build_engine_args(_test_database_url())
    engine = create_async_engine(
        url, poolclass=NullPool, connect_args=connect_args, **engine_kwargs
    )

    # Everything a test writes lives inside this outer transaction and is rolled back, so
    # the seeded database is left untouched. App-level commits become savepoint releases.
    async with engine.connect() as conn:
        outer = await conn.begin()
        session = AsyncSession(
            bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        try:
            yield session
        finally:
            await session.close()
            await outer.rollback()

    await engine.dispose()


@pytest.fixture
async def client(
    db_session: AsyncSession, fake_sender: FakeSender
) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    # The app's httpx client is created in `lifespan`, which ASGITransport doesn't run, so
    # routes that send email get this instead.
    app.dependency_overrides[get_sender] = lambda: fake_sender
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
async def clean_rate_limits(db_session: AsyncSession) -> None:
    """Rate limit rows outlive the per-test rollback if an earlier test committed them."""
    await db_session.execute(delete(RateLimitHit))


@pytest.fixture
async def empty_opportunities(db_session: AsyncSession) -> None:
    # The dev database is seeded with opportunities; clear them (inside the rolled-back test
    # transaction) so each test sees only the rows it creates.
    await db_session.execute(delete(OpportunityMatch))
    await db_session.execute(delete(UserOpportunityAction))
    await db_session.execute(delete(Opportunity))
