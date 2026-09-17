from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.db import _build_engine_args, get_db
from app.main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # A fresh engine per test: asyncpg connections are bound to the event loop that opened
    # them, and pytest-asyncio gives each test its own loop.
    url, connect_args, engine_kwargs = _build_engine_args(get_settings().database_url)
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
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()
