# Sprint 7 — Auth Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Throttle the auth endpoints and ship an end-to-end password reset, so the API can be exposed publicly.

**Architecture:** Rate limiting is a Postgres fixed-window counter table driven by an atomic `INSERT … ON CONFLICT DO UPDATE … RETURNING`, reached through a request-scoped `RateLimiter` helper that handlers call explicitly. Password reset issues a 256-bit token, stores only its SHA-256, and mails a link through the `EmailSender` abstraction Sprint 6 built. A new `users.password_changed_at` column lets `get_current_user` reject access tokens minted before a reset.

**Tech Stack:** FastAPI, SQLAlchemy 2 (async, asyncpg), Alembic, Pydantic v2 / pydantic-settings, PyJWT, pwdlib[argon2], httpx, pytest + pytest-asyncio.

**Spec:** `docs/superpowers/specs/2026-09-20-sprint-7-auth-hardening-design.md`

## Global Constraints

- All work is committed on the current branch, `sprint-1-auth`. Do not create branches, do not push, do not open a PR.
- Never add a Claude co-author or attribution line to a commit.
- Tests run against the local Docker Postgres. `docker compose up -d` in `backend/` if it isn't running. Never point the suite at a remote database.
- Run everything through the project venv: `backend/.venv/bin/python`, `backend/.venv/bin/pytest`, `backend/.venv/bin/alembic`.
- Every new table gets `alter table <name> enable row level security`, matching migration `2d6c5e3b3a6b`.
- Timestamps are `TIMESTAMP(timezone=True)` and all datetimes are timezone-aware UTC (`datetime.now(UTC)`).
- Password validation reuses `MAX_PASSWORD_LENGTH` (128) and `SignupRequest`'s `min_length=8`.
- Reset token lifetime: 1 hour. Token: `secrets.token_urlsafe(32)`, stored as SHA-256 hex. Never Argon2 for reset tokens.
- Limits: login 30/15min per IP and 10/15min per IP+email; signup 5/hr per IP; reset-request 10/hr per IP and 3/hr per email; reset-confirm 10/hr per IP.
- No new runtime dependencies. Everything below uses what is already in `requirements.txt`.

---

## Deviation from the spec (read before Task 3)

The spec says login counts *failed* attempts only. A check-then-increment implementation of
that is racy: N concurrent requests all read count=0, all pass, and all proceed to hash — which
is precisely the Argon2 memory-exhaustion vector this sprint exists to close (64 MB × N).

So the counter **always increments atomically before the password is hashed**, and a
*successful* login **refunds** its hit (`count = greatest(count - 1, 0)`). Same observable
behaviour as the spec's rule — a legitimate user's successful logins don't consume their
budget — without the race. Task 3 implements `hit()` and `refund()`; Task 4 wires the refund.

---

## File Structure

**Create:**
- `backend/app/core/rate_limit.py` — limit definitions, window arithmetic, client-IP resolution, the counter store, the `RateLimiter` helper.
- `backend/app/models/rate_limit.py` — `RateLimitHit` model.
- `backend/app/models/password_reset.py` — `PasswordResetToken` model.
- `backend/app/password_reset.py` — token issue/consume service plus the reset email composer.
- `backend/alembic/versions/<generated>_auth_hardening.py` — one migration: two tables + `users.password_changed_at`.
- `backend/tests/test_rate_limit.py` — unit tests for windows, IP resolution, the counter.
- `backend/tests/test_password_reset.py` — end-to-end tests for both endpoints.

**Modify:**
- `backend/app/core/config.py` — `TRUST_PROXY_HEADER`, `TRUSTED_PROXY_HOPS`.
- `backend/app/core/security.py` — reset-token generate/hash helpers.
- `backend/app/models/__init__.py` — export the two new models.
- `backend/app/models/user.py` — `password_changed_at`.
- `backend/app/api/deps.py` — `get_rate_limiter`, `EmailSenderDep`, the `password_changed_at` check.
- `backend/app/api/routes/auth.py` — throttle login/signup, add the two reset routes.
- `backend/app/schemas/auth.py` — reset request/confirm schemas.
- `backend/app/main.py` — app-lifetime `httpx.AsyncClient` for outbound email.
- `backend/tests/conftest.py` — `fake_sender` fixture, `clean_rate_limits` fixture.
- `backend/tests/test_auth.py` — throttling and token-invalidation cases.
- `backend/README.md`, `docs/sprints/sprint-07-auth-hardening.md`, `docs/STATUS.md` — docs.

---

### Task 1: Client IP resolution

Where the per-IP limit reads its key from. Pure function, no database — done first so later tasks can use it.

**Files:**
- Modify: `backend/app/core/config.py`
- Create: `backend/app/core/rate_limit.py`
- Test: `backend/tests/test_rate_limit.py`

**Interfaces:**
- Consumes: `Settings` from `app.core.config`.
- Produces: `client_ip(request: Request, settings: Settings) -> str`; `Settings.trust_proxy_header: bool`; `Settings.trusted_proxy_hops: int`.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_rate_limit.py`:

```python
from dataclasses import dataclass

import pytest

from app.core.rate_limit import client_ip


@dataclass
class FakeClient:
    host: str


class FakeRequest:
    """Enough of starlette's Request for client_ip."""

    def __init__(self, host: str | None, headers: dict[str, str] | None = None) -> None:
        self.client = FakeClient(host) if host is not None else None
        self.headers = headers or {}


@dataclass
class FakeSettings:
    trust_proxy_header: bool = False
    trusted_proxy_hops: int = 1


def test_uses_socket_address_by_default():
    request = FakeRequest("203.0.113.5")

    assert client_ip(request, FakeSettings()) == "203.0.113.5"


def test_ignores_forwarded_header_when_trust_is_off():
    # Without a proxy in front, X-Forwarded-For is attacker-controlled: a fresh value per
    # request would make the per-IP limit a no-op.
    request = FakeRequest("203.0.113.5", {"x-forwarded-for": "1.1.1.1"})

    assert client_ip(request, FakeSettings()) == "203.0.113.5"


def test_takes_rightmost_but_n_when_trusted():
    request = FakeRequest("10.0.0.1", {"x-forwarded-for": "1.1.1.1, 203.0.113.5, 10.0.0.9"})

    assert client_ip(request, FakeSettings(trust_proxy_header=True)) == "10.0.0.9"
    hops2 = FakeSettings(trust_proxy_header=True, trusted_proxy_hops=2)
    assert client_ip(request, hops2) == "203.0.113.5"


def test_falls_back_to_socket_when_header_is_too_short():
    request = FakeRequest("10.0.0.1", {"x-forwarded-for": "1.1.1.1"})
    settings = FakeSettings(trust_proxy_header=True, trusted_proxy_hops=3)

    assert client_ip(request, settings) == "10.0.0.1"


def test_unknown_when_there_is_no_peer():
    assert client_ip(FakeRequest(None), FakeSettings()) == "unknown"
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd backend && .venv/bin/pytest tests/test_rate_limit.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.core.rate_limit'`

- [ ] **Step 3: Add the settings**

In `backend/app/core/config.py`, after the `frontend_url` field:

```python
    # Off by default: with no proxy in front, X-Forwarded-For is attacker-controlled, and
    # trusting it would let one client spoof a fresh IP per request and skip rate limiting.
    trust_proxy_header: bool = Field(False, alias="TRUST_PROXY_HEADER")
    # How many proxies append to X-Forwarded-For before it reaches us. The last `hops`
    # entries were written by infrastructure we control; anything left of them is client input.
    trusted_proxy_hops: int = Field(1, alias="TRUSTED_PROXY_HOPS", ge=1)
```

- [ ] **Step 4: Write the resolver**

Create `backend/app/core/rate_limit.py`:

```python
"""Fixed-window rate limiting, counted in Postgres so it holds across worker processes."""

from starlette.requests import Request

from app.core.config import Settings

UNKNOWN_IP = "unknown"


def client_ip(request: Request, settings: Settings) -> str:
    """The address the per-IP limit is keyed on."""
    if settings.trust_proxy_header:
        forwarded = request.headers.get("x-forwarded-for", "")
        hops = [part.strip() for part in forwarded.split(",") if part.strip()]
        # Count from the right: our own proxy appended last, so the rightmost entries are
        # the trustworthy ones. A header shorter than the hop count didn't come through the
        # expected chain, so fall back rather than trust client-supplied text.
        if len(hops) >= settings.trusted_proxy_hops:
            return hops[-settings.trusted_proxy_hops]
    return request.client.host if request.client else UNKNOWN_IP
```

- [ ] **Step 5: Run the tests**

Run: `cd backend && .venv/bin/pytest tests/test_rate_limit.py -v`
Expected: PASS, 5 tests.

- [ ] **Step 6: Check the config tests still pass**

Run: `cd backend && .venv/bin/pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/app/core/config.py backend/app/core/rate_limit.py backend/tests/test_rate_limit.py
git commit -m "Resolve the client IP for rate limiting, ignoring forwarded headers by default"
```

---

### Task 2: Schema — counter table, reset tokens, password_changed_at

All three schema changes in one migration, so the database moves in a single step.

**Files:**
- Create: `backend/app/models/rate_limit.py`, `backend/app/models/password_reset.py`
- Modify: `backend/app/models/user.py`, `backend/app/models/__init__.py`
- Create: `backend/alembic/versions/<generated>_auth_hardening.py`

**Interfaces:**
- Produces: `RateLimitHit(key, window_start, count)`; `PasswordResetToken(id, user_id, token_hash, expires_at, used_at, created_at)`; `User.password_changed_at: datetime | None`.

- [ ] **Step 1: Add the RateLimitHit model**

Create `backend/app/models/rate_limit.py`:

```python
from datetime import datetime

from sqlalchemy import TIMESTAMP, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RateLimitHit(Base):
    """Attempts against one key inside one fixed window.

    Counted in the database rather than in memory so the limit still holds when the API
    runs as more than one worker.
    """

    __tablename__ = "rate_limit_hits"

    key: Mapped[str] = mapped_column(Text, primary_key=True)
    window_start: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), primary_key=True
    )
    count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
```

- [ ] **Step 2: Add the PasswordResetToken model**

Create `backend/app/models/password_reset.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PasswordResetToken(Base):
    """One issued reset token. Only the hash is stored, never the token itself."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # sha256 hex of the token. Unique, so a lookup is a single indexed match.
    token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    # Set the moment the token is spent, which is what makes it single-use.
    used_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
```

- [ ] **Step 3: Add password_changed_at to User**

In `backend/app/models/user.py`, add after `password_hash`:

```python
    # Null for accounts that have never changed their password. Access tokens issued before
    # this instant are rejected, so a reset locks out anyone holding a stolen token.
    password_changed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
```

- [ ] **Step 4: Export both models**

Rewrite `backend/app/models/__init__.py`:

```python
from app.models.activity import OpportunityMatch, UserOpportunityAction
from app.models.base import Base
from app.models.notification import MatchNotification
from app.models.opportunity import Opportunity
from app.models.password_reset import PasswordResetToken
from app.models.profile import Profile, ProfileInterest, ProfileSkill
from app.models.rate_limit import RateLimitHit
from app.models.user import User

__all__ = [
    "Base",
    "MatchNotification",
    "Opportunity",
    "OpportunityMatch",
    "PasswordResetToken",
    "Profile",
    "ProfileInterest",
    "ProfileSkill",
    "RateLimitHit",
    "User",
    "UserOpportunityAction",
]
```

- [ ] **Step 5: Create the empty revision**

Run: `cd backend && .venv/bin/alembic revision -m "auth hardening"`
Expected: prints `Generating .../alembic/versions/<id>_auth_hardening.py ... done`

Note the generated `<id>`; the next step replaces the file's body. Confirm the generated file already has `down_revision = 'b6c72226a5c2'`.

- [ ] **Step 6: Fill in the migration**

Replace everything below the generated `depends_on` line with:

```python
RATE_LIMIT_TABLE = "rate_limit_hits"
RESET_TABLE = "password_reset_tokens"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        RATE_LIMIT_TABLE,
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("window_start", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.PrimaryKeyConstraint("key", "window_start"),
    )
    op.create_table(
        RESET_TABLE,
        sa.Column("id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "password_reset_tokens_user_idx", RESET_TABLE, ["user_id"], unique=False
    )
    op.add_column(
        "users", sa.Column("password_changed_at", sa.TIMESTAMP(timezone=True), nullable=True)
    )
    # Same reasoning as 2d6c5e3b3a6b: RLS with no policies denies the anon/authenticated
    # roles every row, and the backend connects as the owner, which RLS doesn't apply to.
    for table in (RATE_LIMIT_TABLE, RESET_TABLE):
        op.execute(f"alter table {table} enable row level security")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "password_changed_at")
    op.drop_index("password_reset_tokens_user_idx", table_name=RESET_TABLE)
    op.drop_table(RESET_TABLE)
    op.drop_table(RATE_LIMIT_TABLE)
```

Make sure the file's imports are `import sqlalchemy as sa` and `from alembic import op`.

- [ ] **Step 7: Apply, roll back, re-apply**

Run:
```bash
cd backend && .venv/bin/alembic upgrade head && .venv/bin/alembic downgrade -1 && .venv/bin/alembic upgrade head
```
Expected: three clean runs, no error. This proves `downgrade()` actually works.

- [ ] **Step 8: Verify the schema landed**

Run:
```bash
cd backend && docker compose exec -T db psql -U postgres -d opzy -c '\d password_reset_tokens' -c '\d rate_limit_hits'
```
Expected: both tables listed, `password_reset_tokens.token_hash` unique, `rate_limit_hits` PK on `(key, window_start)`.

If the db container or role differs, read `backend/docker-compose.yml` for the right values.

- [ ] **Step 9: Run the full suite to catch model regressions**

Run: `cd backend && .venv/bin/pytest -q`
Expected: PASS, same count as before this task.

- [ ] **Step 10: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/app/models backend/alembic/versions
git commit -m "Add the rate limit counter, reset token table, and password_changed_at"
```

---

### Task 3: The counter store

Atomic increment, refund, and pruning. Tested directly against the database, no HTTP.

**Files:**
- Modify: `backend/app/core/rate_limit.py`
- Modify: `backend/tests/test_rate_limit.py`

**Interfaces:**
- Consumes: `RateLimitHit` (Task 2).
- Produces: `Limit(max_hits: int, window_seconds: int)`; `window_start(now: datetime, window_seconds: int) -> datetime`; `async hit(db, key, limit, *, now) -> int`; `async refund(db, key, limit, *, now) -> None`; `async prune(db, *, now) -> None`; the limit constants `LOGIN_PER_IP`, `LOGIN_PER_EMAIL`, `SIGNUP_PER_IP`, `RESET_REQUEST_PER_IP`, `RESET_REQUEST_PER_EMAIL`, `RESET_CONFIRM_PER_IP`.

- [ ] **Step 1: Write the failing tests**

Append to `backend/tests/test_rate_limit.py`:

```python
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import Limit, hit, prune, refund, window_start
from app.models import RateLimitHit

NOW = datetime(2026, 9, 20, 12, 7, 30, tzinfo=UTC)
TEN_PER_MINUTE = Limit(max_hits=10, window_seconds=60)


def test_window_start_floors_to_the_window():
    assert window_start(NOW, 60) == datetime(2026, 9, 20, 12, 7, tzinfo=UTC)
    assert window_start(NOW, 900) == datetime(2026, 9, 20, 12, 0, tzinfo=UTC)
    assert window_start(NOW, 3600) == datetime(2026, 9, 20, 12, 0, tzinfo=UTC)


async def test_hit_counts_up_within_a_window(db_session: AsyncSession):
    first = await hit(db_session, "login:ip:1.2.3.4", TEN_PER_MINUTE, now=NOW)
    second = await hit(db_session, "login:ip:1.2.3.4", TEN_PER_MINUTE, now=NOW + timedelta(seconds=5))

    assert (first, second) == (1, 2)


async def test_hit_starts_over_in_the_next_window(db_session: AsyncSession):
    await hit(db_session, "login:ip:1.2.3.4", TEN_PER_MINUTE, now=NOW)
    later = await hit(db_session, "login:ip:1.2.3.4", TEN_PER_MINUTE, now=NOW + timedelta(minutes=1))

    assert later == 1


async def test_keys_are_counted_separately(db_session: AsyncSession):
    await hit(db_session, "login:ip:1.2.3.4", TEN_PER_MINUTE, now=NOW)
    other = await hit(db_session, "login:ip:5.6.7.8", TEN_PER_MINUTE, now=NOW)

    assert other == 1


async def test_refund_gives_the_hit_back(db_session: AsyncSession):
    await hit(db_session, "login:email:ada@example.com", TEN_PER_MINUTE, now=NOW)
    await hit(db_session, "login:email:ada@example.com", TEN_PER_MINUTE, now=NOW)
    await refund(db_session, "login:email:ada@example.com", TEN_PER_MINUTE, now=NOW)

    again = await hit(db_session, "login:email:ada@example.com", TEN_PER_MINUTE, now=NOW)
    assert again == 2


async def test_refund_never_goes_below_zero(db_session: AsyncSession):
    await refund(db_session, "login:email:nobody@example.com", TEN_PER_MINUTE, now=NOW)

    count = await db_session.scalar(
        select(RateLimitHit.count).where(RateLimitHit.key == "login:email:nobody@example.com")
    )
    assert count in (None, 0)


async def test_prune_drops_windows_past_the_longest_limit(db_session: AsyncSession):
    await hit(db_session, "login:ip:9.9.9.9", TEN_PER_MINUTE, now=NOW - timedelta(days=1))
    await hit(db_session, "login:ip:9.9.9.9", TEN_PER_MINUTE, now=NOW)

    await prune(db_session, now=NOW)

    rows = (await db_session.scalars(select(RateLimitHit).where(RateLimitHit.key == "login:ip:9.9.9.9"))).all()
    assert len(rows) == 1
    assert rows[0].window_start == window_start(NOW, 60)
```

- [ ] **Step 2: Run them and watch them fail**

Run: `cd backend && .venv/bin/pytest tests/test_rate_limit.py -v`
Expected: FAIL — `ImportError: cannot import name 'Limit' from 'app.core.rate_limit'`

- [ ] **Step 3: Implement the store**

Append to `backend/app/core/rate_limit.py` (and extend the imports at the top of the file):

```python
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RateLimitHit


@dataclass(frozen=True)
class Limit:
    max_hits: int
    window_seconds: int


MINUTES_15 = 15 * 60
HOUR = 60 * 60

LOGIN_PER_IP = Limit(max_hits=30, window_seconds=MINUTES_15)
LOGIN_PER_EMAIL = Limit(max_hits=10, window_seconds=MINUTES_15)
SIGNUP_PER_IP = Limit(max_hits=5, window_seconds=HOUR)
RESET_REQUEST_PER_IP = Limit(max_hits=10, window_seconds=HOUR)
RESET_REQUEST_PER_EMAIL = Limit(max_hits=3, window_seconds=HOUR)
RESET_CONFIRM_PER_IP = Limit(max_hits=10, window_seconds=HOUR)

# Nothing is counted in a window longer than this, so older rows can never affect a decision.
LONGEST_WINDOW_SECONDS = HOUR


def window_start(now: datetime, window_seconds: int) -> datetime:
    """Floor `now` to the start of its fixed window."""
    epoch_seconds = int(now.timestamp())
    return datetime.fromtimestamp(
        epoch_seconds - epoch_seconds % window_seconds, tz=UTC
    )


async def hit(db: AsyncSession, key: str, limit: Limit, *, now: datetime) -> int:
    """Record one attempt against `key` and return the window's new count.

    One statement, so concurrent requests can't all read a stale count and sail past the
    limit together — which matters here because the thing being protected is an Argon2 hash
    that costs ~64 MB.
    """
    start = window_start(now, limit.window_seconds)
    stmt = (
        pg_insert(RateLimitHit)
        .values(key=key, window_start=start, count=1)
        .on_conflict_do_update(
            index_elements=["key", "window_start"],
            set_={"count": RateLimitHit.__table__.c.count + 1},
        )
        .returning(RateLimitHit.__table__.c.count)
    )
    count = await db.scalar(stmt)
    # Commit on its own: the request that follows usually ends in an exception (401, 429),
    # and an uncommitted increment would be rolled back with it — the attempt would be free.
    await db.commit()
    return int(count)


async def refund(db: AsyncSession, key: str, limit: Limit, *, now: datetime) -> None:
    """Give back one hit, for an attempt that turned out to be legitimate."""
    start = window_start(now, limit.window_seconds)
    await db.execute(
        RateLimitHit.__table__.update()
        .where(
            RateLimitHit.__table__.c.key == key,
            RateLimitHit.__table__.c.window_start == start,
        )
        .values(count=func.greatest(RateLimitHit.__table__.c.count - 1, 0))
    )
    await db.commit()


async def prune(db: AsyncSession, *, now: datetime) -> None:
    """Drop windows too old to matter. Called opportunistically, so no cron job is needed."""
    cutoff = now - timedelta(seconds=LONGEST_WINDOW_SECONDS)
    await db.execute(delete(RateLimitHit).where(RateLimitHit.window_start < cutoff))
    await db.commit()
```

- [ ] **Step 4: Run the tests**

Run: `cd backend && .venv/bin/pytest tests/test_rate_limit.py -v`
Expected: PASS, 12 tests.

- [ ] **Step 5: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/app/core/rate_limit.py backend/tests/test_rate_limit.py
git commit -m "Count rate limit hits in Postgres, atomically, with a refund for good attempts"
```

---

### Task 4: Throttle login and signup

Wire the store into the two existing endpoints through a request-scoped helper.

**Files:**
- Modify: `backend/app/core/rate_limit.py`, `backend/app/api/deps.py`, `backend/app/api/routes/auth.py`
- Modify: `backend/tests/conftest.py`, `backend/tests/test_auth.py`

**Interfaces:**
- Consumes: `hit`, `refund`, `prune`, `client_ip`, the limit constants (Tasks 1 and 3).
- Produces: `RateLimiter` with `async enforce(bucket: str, limit: Limit, *, kind: str, value: str | None = None) -> None` and `async give_back(bucket: str, limit: Limit, *, kind: str = "ip", value: str | None = None) -> None`; the dependency alias `Limiter` in `app.api.deps`. (`give_back` is the method name; the module-level function it calls is `refund`.)

- [ ] **Step 1: Write the failing tests**

Add a fixture to `backend/tests/conftest.py` (import `RateLimitHit` from `app.models` alongside the existing model imports):

```python
@pytest.fixture
async def clean_rate_limits(db_session: AsyncSession) -> None:
    """Rate limit rows outlive the per-test rollback if an earlier test committed them."""
    await db_session.execute(delete(RateLimitHit))
```

Append to `backend/tests/test_auth.py`:

```python
from app.core.rate_limit import LOGIN_PER_EMAIL, SIGNUP_PER_IP

# --- rate limiting --------------------------------------------------------------------


async def test_repeated_failed_logins_are_throttled(
    client: AsyncClient, clean_rate_limits: None
):
    await signup(client)

    for _ in range(LOGIN_PER_EMAIL.max_hits):
        resp = await login(client, password="wrong")
        assert resp.status_code == 401

    throttled = await login(client, password="wrong")
    assert throttled.status_code == 429
    assert int(throttled.headers["retry-after"]) > 0


async def test_successful_logins_do_not_burn_the_budget(
    client: AsyncClient, clean_rate_limits: None
):
    await signup(client)

    # Comfortably more successes than the per-email limit: each one refunds its own hit.
    for _ in range(LOGIN_PER_EMAIL.max_hits + 5):
        resp = await login(client)
        assert resp.status_code == 200


async def test_signup_is_throttled_per_ip(client: AsyncClient, clean_rate_limits: None):
    for index in range(SIGNUP_PER_IP.max_hits):
        resp = await signup(client, email=f"user{index}@example.com")
        assert resp.status_code == 201

    throttled = await signup(client, email="one-too-many@example.com")
    assert throttled.status_code == 429


async def test_throttling_a_login_does_not_reveal_the_account(
    client: AsyncClient, clean_rate_limits: None
):
    # An unknown email must throttle exactly like a known one.
    for _ in range(LOGIN_PER_EMAIL.max_hits):
        resp = await login(client, email="ghost@example.com", password="wrong")
        assert resp.status_code == 401

    throttled = await login(client, email="ghost@example.com", password="wrong")
    assert throttled.status_code == 429
```

- [ ] **Step 2: Run them and watch them fail**

Run: `cd backend && .venv/bin/pytest tests/test_auth.py -v -k "throttl or budget"`
Expected: FAIL — the 429 assertions get 401/201 instead.

- [ ] **Step 3: Add the RateLimiter helper**

Append to `backend/app/core/rate_limit.py`:

```python
import random

from fastapi import HTTPException, status

# Roughly one request in fifty clears out expired windows.
PRUNE_PROBABILITY = 0.02


class RateLimiter:
    """Rate limiting for one request. Handlers decide which keys to count."""

    def __init__(self, db: AsyncSession, ip: str) -> None:
        self._db = db
        self._ip = ip

    def _key(self, bucket: str, kind: str, value: str | None) -> str:
        return f"{bucket}:{kind}:{value if value is not None else self._ip}"

    async def enforce(
        self, bucket: str, limit: Limit, *, kind: str = "ip", value: str | None = None
    ) -> None:
        """Count one attempt and raise 429 if the key is over its limit."""
        now = datetime.now(UTC)
        count = await hit(self._db, self._key(bucket, kind, value), limit, now=now)
        if random.random() < PRUNE_PROBABILITY:
            await prune(self._db, now=now)
        if count > limit.max_hits:
            retry_after = int(
                (
                    window_start(now, limit.window_seconds)
                    + timedelta(seconds=limit.window_seconds)
                    - now
                ).total_seconds()
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Try again later.",
                headers={"Retry-After": str(max(retry_after, 1))},
            )

    async def give_back(
        self, bucket: str, limit: Limit, *, kind: str = "ip", value: str | None = None
    ) -> None:
        await refund(self._db, self._key(bucket, kind, value), limit, now=datetime.now(UTC))
```

- [ ] **Step 4: Add the dependency**

In `backend/app/api/deps.py`, add the imports and, after the `DbSession` alias:

```python
from starlette.requests import Request

from app.core.config import get_settings
from app.core.rate_limit import RateLimiter, client_ip


def get_rate_limiter(request: Request, db: DbSession) -> RateLimiter:
    return RateLimiter(db, client_ip(request, get_settings()))


Limiter = Annotated[RateLimiter, Depends(get_rate_limiter)]
```

- [ ] **Step 5: Throttle the two handlers**

In `backend/app/api/routes/auth.py`, import the pieces:

```python
from app.api.deps import CurrentUser, DbSession, Limiter
from app.core.rate_limit import LOGIN_PER_EMAIL, LOGIN_PER_IP, SIGNUP_PER_IP
```

Change the `signup` signature to `async def signup(body: SignupRequest, db: DbSession, limiter: Limiter) -> SignupResponse:` and make its first statement:

```python
    # Before anything hashes a password: Argon2 costs ~64 MB per call, so unthrottled
    # concurrent signups are a memory-exhaustion vector on their own.
    await limiter.enforce("signup", SIGNUP_PER_IP)
```

Change the `login` signature to include `limiter: Limiter`, and put this immediately after the `invalid` exception is built, before the `MAX_PASSWORD_LENGTH` check:

```python
    email = normalize_email(form.username)
    await limiter.enforce("login", LOGIN_PER_IP)
    await limiter.enforce("login", LOGIN_PER_EMAIL, kind="email", value=email)
```

Replace the later `select(User).where(User.email == normalize_email(form.username))` with `select(User).where(User.email == email)`, and put this just before the `return TokenResponse(...)`:

```python
    # The attempt was legitimate, so it shouldn't count against this account's budget.
    await limiter.give_back("login", LOGIN_PER_EMAIL, kind="email", value=email)
```

- [ ] **Step 6: Run the auth tests**

Run: `cd backend && .venv/bin/pytest tests/test_auth.py -v`
Expected: PASS, including the four new cases.

- [ ] **Step 7: Run the whole suite**

Run: `cd backend && .venv/bin/pytest -q`
Expected: PASS. If an unrelated test now trips a limit, add the `clean_rate_limits` fixture to it rather than raising the limits.

- [ ] **Step 8: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/app/core/rate_limit.py backend/app/api backend/tests
git commit -m "Throttle login and signup per IP, and per email for login"
```

---

### Task 5: A password change invalidates existing tokens

**Files:**
- Modify: `backend/app/api/deps.py`
- Modify: `backend/tests/test_auth.py`

**Interfaces:**
- Consumes: `User.password_changed_at` (Task 2), `decode_access_token` (existing).
- Produces: `decode_access_token_claims(token: str) -> dict` in `app.core.security`; `get_current_user` rejecting stale tokens.

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_auth.py`:

```python
from datetime import UTC, datetime, timedelta

# --- token invalidation ---------------------------------------------------------------


async def test_token_issued_before_a_password_change_is_rejected(
    client: AsyncClient, db_session: AsyncSession, clean_rate_limits: None
):
    body = (await signup(client)).json()
    token = body["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert (await client.get("/auth/me", headers=headers)).status_code == 200

    user = await db_session.get(User, uuid.UUID(body["user"]["id"]))
    user.password_changed_at = datetime.now(UTC) + timedelta(seconds=5)
    await db_session.commit()

    assert (await client.get("/auth/me", headers=headers)).status_code == 401


async def test_token_issued_after_a_password_change_still_works(
    client: AsyncClient, db_session: AsyncSession, clean_rate_limits: None
):
    body = (await signup(client)).json()
    user = await db_session.get(User, uuid.UUID(body["user"]["id"]))
    user.password_changed_at = datetime.now(UTC) - timedelta(hours=1)
    await db_session.commit()

    fresh = create_access_token(user.id)
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {fresh}"})

    assert resp.status_code == 200
```

- [ ] **Step 2: Run them and watch them fail**

Run: `cd backend && .venv/bin/pytest tests/test_auth.py -v -k password_change`
Expected: FAIL — the first test gets 200 where it wants 401.

- [ ] **Step 3: Expose the token's claims**

In `backend/app/core/security.py`, add below `decode_access_token`:

```python
def decode_access_token_claims(token: str) -> dict:
    """The full validated payload, for callers that need more than the subject."""
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["exp", "sub", "type", "iat"]},
    )
    if payload["type"] != ACCESS_TOKEN_TYPE:
        raise jwt.InvalidTokenError("Not an access token")
    return payload
```

- [ ] **Step 4: Check it in get_current_user**

In `backend/app/api/deps.py`, replace the body of `get_current_user` below the `credentials_error` definition with:

```python
    try:
        claims = decode_access_token_claims(token)
        user_id = uuid.UUID(claims["sub"])
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise credentials_error from None

    # Tokens are stateless, so a deleted user's token stays valid until expiry; this lookup
    # is what shuts them out.
    user = await db.get(User, user_id)
    if user is None:
        raise credentials_error

    # A password change retires every token minted before it, so resetting a password
    # actually locks out whoever prompted the reset.
    if user.password_changed_at is not None:
        issued_at = datetime.fromtimestamp(claims["iat"], tz=UTC)
        if issued_at < user.password_changed_at:
            raise credentials_error
    return user
```

Add the imports `import uuid` and `from datetime import UTC, datetime`, and swap `decode_access_token` for `decode_access_token_claims` in the import from `app.core.security`.

- [ ] **Step 5: Run the tests**

Run: `cd backend && .venv/bin/pytest tests/test_auth.py tests/test_security.py -v`
Expected: PASS.

- [ ] **Step 6: Run the whole suite**

Run: `cd backend && .venv/bin/pytest -q`
Expected: PASS — every authenticated route goes through `get_current_user`, so this is the real check.

- [ ] **Step 7: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/app/core/security.py backend/app/api/deps.py backend/tests/test_auth.py
git commit -m "Reject access tokens issued before the account's password changed"
```

---

### Task 6: Email sending inside a request

The notification script owns its own httpx client. Routes need one too, living as long as the app.

**Files:**
- Modify: `backend/app/main.py`, `backend/app/api/deps.py`, `backend/tests/conftest.py`

**Interfaces:**
- Consumes: `get_email_sender(settings, http)` (existing, `app/email.py`).
- Produces: `EmailSenderDep` in `app.api.deps`; `get_sender` (the override point in tests); `app.state.http`.

- [ ] **Step 1: Give the app an HTTP client**

In `backend/app/main.py`, add `import httpx` and `from app.email import EMAIL_TIMEOUT_SECONDS`, then replace `lifespan`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # One client for the app's lifetime: connection reuse, and somewhere for the email
    # backend to live that isn't rebuilt per request.
    async with httpx.AsyncClient(timeout=EMAIL_TIMEOUT_SECONDS) as http:
        app.state.http = http
        yield
    await engine.dispose()
```

- [ ] **Step 2: Add the dependency**

In `backend/app/api/deps.py`:

```python
from app.email import EmailSender, get_email_sender


def get_sender(request: Request) -> EmailSender:
    return get_email_sender(get_settings(), request.app.state.http)


EmailSenderDep = Annotated[EmailSender, Depends(get_sender)]
```

- [ ] **Step 3: Add the test fixture**

In `backend/tests/conftest.py`, add `from app.api.deps import get_sender` and `from app.email import EmailMessage`, then:

```python
class FakeSender:
    """Collects emails instead of sending them."""

    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> None:
        self.sent.append(message)


@pytest.fixture
async def fake_sender() -> FakeSender:
    return FakeSender()
```

and inside the `client` fixture, alongside the existing `get_db` override — change the fixture signature to `async def client(db_session: AsyncSession, fake_sender: FakeSender)` and add:

```python
    app.dependency_overrides[get_sender] = lambda: fake_sender
```

The existing `app.dependency_overrides.clear()` in the `finally` block already cleans both up.

- [ ] **Step 4: Verify nothing broke**

Run: `cd backend && .venv/bin/pytest -q`
Expected: PASS, unchanged count. `lifespan` doesn't run under `ASGITransport` without a lifespan manager, so `app.state.http` is unset in tests — which is exactly why the tests override `get_sender`.

- [ ] **Step 5: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/app/main.py backend/app/api/deps.py backend/tests/conftest.py
git commit -m "Give request handlers an email sender backed by an app-lifetime HTTP client"
```

---

### Task 7: Reset tokens — crypto helpers and the email

Pure functions, no HTTP and no database, so they get tested on their own.

**Files:**
- Modify: `backend/app/core/security.py`
- Create: `backend/app/password_reset.py`
- Create: `backend/tests/test_password_reset.py`

**Interfaces:**
- Consumes: `EmailMessage` from `app.email`.
- Produces: `generate_reset_token() -> str`; `hash_reset_token(token: str) -> str`; `RESET_TOKEN_TTL: timedelta`; `compose_password_reset_email(to: str, token: str, frontend_url: str) -> EmailMessage`.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_password_reset.py`:

```python
from app.core.security import RESET_TOKEN_TTL, generate_reset_token, hash_reset_token
from app.password_reset import compose_password_reset_email


def test_tokens_are_unguessable_and_distinct():
    tokens = {generate_reset_token() for _ in range(100)}

    assert len(tokens) == 100
    # token_urlsafe(32) is 32 random bytes, base64url encoded.
    assert all(len(token) >= 40 for token in tokens)


def test_hash_is_stable_and_is_not_the_token():
    token = generate_reset_token()

    assert hash_reset_token(token) == hash_reset_token(token)
    assert token not in hash_reset_token(token)
    assert len(hash_reset_token(token)) == 64


def test_token_lives_for_an_hour():
    assert RESET_TOKEN_TTL.total_seconds() == 3600


def test_reset_email_carries_a_working_link():
    message = compose_password_reset_email(
        "ada@example.com", "tok-123", "https://opzy.app/"
    )

    assert message.to == "ada@example.com"
    link = "https://opzy.app/reset-password?token=tok-123"
    assert link in message.text
    assert link in message.html
    assert "1 hour" in message.text


def test_reset_email_escapes_the_token_in_html():
    message = compose_password_reset_email("ada@example.com", "a&b", "https://opzy.app")

    assert "a&amp;b" in message.html
```

- [ ] **Step 2: Run them and watch them fail**

Run: `cd backend && .venv/bin/pytest tests/test_password_reset.py -v`
Expected: FAIL — `ImportError: cannot import name 'generate_reset_token'`

- [ ] **Step 3: Add the crypto helpers**

In `backend/app/core/security.py`, add `import hashlib` and `import secrets` to the imports, and append:

```python
RESET_TOKEN_TTL = timedelta(hours=1)
# 32 bytes of entropy. Deliberately not Argon2-hashed: there is nothing to brute-force in a
# 256-bit random token, and an Argon2 verify per attempt would be a 64 MB-per-request DoS.
RESET_TOKEN_BYTES = 32


def generate_reset_token() -> str:
    return secrets.token_urlsafe(RESET_TOKEN_BYTES)


def hash_reset_token(token: str) -> str:
    """What gets stored. A stolen database row can't be turned back into a usable link."""
    return hashlib.sha256(token.encode()).hexdigest()
```

- [ ] **Step 4: Write the composer**

Create `backend/app/password_reset.py`:

```python
"""Issuing and spending password reset tokens."""

from html import escape
from urllib.parse import quote

from app.email import EmailMessage

SUBJECT = "Reset your Opzy password"


def compose_password_reset_email(to: str, token: str, frontend_url: str) -> EmailMessage:
    link = f"{frontend_url.rstrip('/')}/reset-password?token={quote(token, safe='')}"
    text = (
        "Someone asked to reset the password for this Opzy account.\n\n"
        f"{link}\n\n"
        "The link works once and expires in 1 hour. If this wasn't you, ignore this "
        "email — your password hasn't changed."
    )
    html = (
        "<p>Someone asked to reset the password for this Opzy account.</p>"
        f'<p><a href="{escape(link, quote=True)}">Choose a new password</a></p>'
        "<p>The link works once and expires in 1 hour. If this wasn't you, ignore this "
        "email — your password hasn't changed.</p>"
    )
    return EmailMessage(to=to, subject=SUBJECT, text=text, html=html)
```

- [ ] **Step 5: Run the tests**

Run: `cd backend && .venv/bin/pytest tests/test_password_reset.py tests/test_security.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/app/core/security.py backend/app/password_reset.py backend/tests/test_password_reset.py
git commit -m "Generate, hash and email single-use password reset tokens"
```

---

### Task 8: POST /auth/password-reset/request

**Files:**
- Modify: `backend/app/password_reset.py`, `backend/app/schemas/auth.py`, `backend/app/api/routes/auth.py`
- Modify: `backend/tests/test_password_reset.py`

**Interfaces:**
- Consumes: `generate_reset_token`, `hash_reset_token`, `RESET_TOKEN_TTL`, `compose_password_reset_email` (Task 7); `EmailSenderDep` (Task 6); `Limiter` (Task 4); `PasswordResetToken` (Task 2).
- Produces: `async issue_reset_token(db, user, *, now) -> str`; `PasswordResetRequest` schema; the route.

- [ ] **Step 1: Write the failing tests**

Append to `backend/tests/test_password_reset.py`:

```python
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import RESET_REQUEST_PER_EMAIL
from app.models import PasswordResetToken, User
from tests.conftest import FakeSender

EMAIL = "ada@example.com"
PASSWORD = "correct horse battery"


async def signup(client: AsyncClient, email: str = EMAIL) -> None:
    resp = await client.post("/auth/signup", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 201


def token_from(sender: FakeSender) -> str:
    link = sender.sent[-1].text.split("?token=")[1]
    return link.split()[0].strip()


async def test_request_emails_a_link(
    client: AsyncClient, fake_sender: FakeSender, db_session: AsyncSession, clean_rate_limits: None
):
    await signup(client)

    resp = await client.post("/auth/password-reset/request", json={"email": EMAIL})

    assert resp.status_code == 202
    assert len(fake_sender.sent) == 1
    assert fake_sender.sent[0].to == EMAIL
    stored = (await db_session.scalars(select(PasswordResetToken))).all()
    assert len(stored) == 1
    # The token itself must never be in the database.
    assert token_from(fake_sender) not in stored[0].token_hash


async def test_unknown_email_looks_identical(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    await signup(client)

    known = await client.post("/auth/password-reset/request", json={"email": EMAIL})
    unknown = await client.post(
        "/auth/password-reset/request", json={"email": "ghost@example.com"}
    )

    assert known.status_code == unknown.status_code == 202
    assert known.json() == unknown.json()
    # No account, no email.
    assert [m.to for m in fake_sender.sent] == [EMAIL]


async def test_request_supersedes_earlier_tokens(
    client: AsyncClient, fake_sender: FakeSender, db_session: AsyncSession, clean_rate_limits: None
):
    await signup(client)

    await client.post("/auth/password-reset/request", json={"email": EMAIL})
    await client.post("/auth/password-reset/request", json={"email": EMAIL})

    live = (
        await db_session.scalars(
            select(PasswordResetToken).where(PasswordResetToken.used_at.is_(None))
        )
    ).all()
    assert len(live) == 1


async def test_email_failure_does_not_change_the_response(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    from app.email import EmailError

    await signup(client)

    async def refuse(message):
        raise EmailError("provider down")

    fake_sender.send = refuse

    resp = await client.post("/auth/password-reset/request", json={"email": EMAIL})
    assert resp.status_code == 202


async def test_request_is_throttled_per_email(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    await signup(client)

    for _ in range(RESET_REQUEST_PER_EMAIL.max_hits):
        resp = await client.post("/auth/password-reset/request", json={"email": EMAIL})
        assert resp.status_code == 202

    throttled = await client.post("/auth/password-reset/request", json={"email": EMAIL})
    assert throttled.status_code == 429
```

- [ ] **Step 2: Run them and watch them fail**

Run: `cd backend && .venv/bin/pytest tests/test_password_reset.py -v -k request or email`
Expected: FAIL — 404, the route doesn't exist.

- [ ] **Step 3: Add the schemas**

In `backend/app/schemas/auth.py`, append:

```python
class PasswordResetRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: object) -> object:
        return normalize_email(value) if isinstance(value, str) else value


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=8, max_length=MAX_PASSWORD_LENGTH)
```

- [ ] **Step 4: Add the issue service**

Append to `backend/app/password_reset.py` (extending the imports):

```python
from datetime import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import RESET_TOKEN_TTL, generate_reset_token, hash_reset_token
from app.models import PasswordResetToken, User


async def issue_reset_token(db: AsyncSession, user: User, *, now: datetime) -> str:
    """Retire this user's outstanding tokens, mint a new one, return the plaintext."""
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    token = generate_reset_token()
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hash_reset_token(token),
            expires_at=now + RESET_TOKEN_TTL,
        )
    )
    await db.commit()
    return token
```

- [ ] **Step 5: Add the route**

In `backend/app/api/routes/auth.py`, extend the imports:

```python
import logging
from datetime import UTC, datetime

from app.api.deps import CurrentUser, DbSession, EmailSenderDep, Limiter
from app.core.config import get_settings
from app.core.rate_limit import (
    LOGIN_PER_EMAIL,
    LOGIN_PER_IP,
    RESET_REQUEST_PER_EMAIL,
    RESET_REQUEST_PER_IP,
    SIGNUP_PER_IP,
)
from app.email import EmailError
from app.password_reset import compose_password_reset_email, issue_reset_token
from app.schemas.auth import PasswordResetRequest

logger = logging.getLogger(__name__)

# Returned whether or not the address has an account, so the endpoint can't be used to
# find out which emails are registered.
RESET_REQUESTED = {"detail": "If that email has an account, a reset link is on its way."}
```

and append the route:

```python
@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    body: PasswordResetRequest, db: DbSession, limiter: Limiter, sender: EmailSenderDep
) -> dict:
    await limiter.enforce("reset-request", RESET_REQUEST_PER_IP)
    await limiter.enforce(
        "reset-request", RESET_REQUEST_PER_EMAIL, kind="email", value=body.email
    )

    user = await db.scalar(select(User).where(User.email == body.email))
    if user is not None:
        token = await issue_reset_token(db, user, now=datetime.now(UTC))
        message = compose_password_reset_email(
            user.email, token, get_settings().frontend_url
        )
        try:
            await sender.send(message)
        except EmailError:
            # Never surfaced: a failed send must not make this response differ from the
            # unknown-email one. The user can ask again.
            logger.exception("Couldn't send a password reset email")

    return RESET_REQUESTED
```

- [ ] **Step 6: Run the tests**

Run: `cd backend && .venv/bin/pytest tests/test_password_reset.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/app/password_reset.py backend/app/schemas/auth.py backend/app/api/routes/auth.py backend/tests/test_password_reset.py
git commit -m "Email a reset link without revealing whether the account exists"
```

---

### Task 9: POST /auth/password-reset/confirm

**Files:**
- Modify: `backend/app/password_reset.py`, `backend/app/api/routes/auth.py`
- Modify: `backend/tests/test_password_reset.py`

**Interfaces:**
- Consumes: `issue_reset_token`, `hash_reset_token`, `PasswordResetConfirm`, `hash_password`, `Limiter`.
- Produces: `async consume_reset_token(db, token, new_password, *, now) -> bool`; the route.

- [ ] **Step 1: Write the failing tests**

Append to `backend/tests/test_password_reset.py`:

```python
from datetime import UTC, datetime, timedelta

from app.core.rate_limit import RESET_CONFIRM_PER_IP

NEW_PASSWORD = "a whole new passphrase"


async def request_reset(client: AsyncClient, email: str = EMAIL) -> None:
    resp = await client.post("/auth/password-reset/request", json={"email": email})
    assert resp.status_code == 202


async def test_reset_end_to_end(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    await signup(client)
    await request_reset(client)

    resp = await client.post(
        "/auth/password-reset/confirm",
        json={"token": token_from(fake_sender), "new_password": NEW_PASSWORD},
    )
    assert resp.status_code == 204

    old = await client.post("/auth/login", data={"username": EMAIL, "password": PASSWORD})
    assert old.status_code == 401
    new = await client.post(
        "/auth/login", data={"username": EMAIL, "password": NEW_PASSWORD}
    )
    assert new.status_code == 200


async def test_token_works_exactly_once(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    await signup(client)
    await request_reset(client)
    token = token_from(fake_sender)

    first = await client.post(
        "/auth/password-reset/confirm", json={"token": token, "new_password": NEW_PASSWORD}
    )
    second = await client.post(
        "/auth/password-reset/confirm", json={"token": token, "new_password": "another one entirely"}
    )

    assert first.status_code == 204
    assert second.status_code == 400


async def test_expired_token_is_rejected(
    client: AsyncClient, fake_sender: FakeSender, db_session: AsyncSession, clean_rate_limits: None
):
    await signup(client)
    await request_reset(client)

    row = (await db_session.scalars(select(PasswordResetToken))).one()
    row.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    await db_session.commit()

    resp = await client.post(
        "/auth/password-reset/confirm",
        json={"token": token_from(fake_sender), "new_password": NEW_PASSWORD},
    )
    assert resp.status_code == 400


async def test_unknown_token_is_rejected_the_same_way(
    client: AsyncClient, clean_rate_limits: None
):
    resp = await client.post(
        "/auth/password-reset/confirm",
        json={"token": "not-a-real-token", "new_password": NEW_PASSWORD},
    )

    assert resp.status_code == 400
    assert "invalid" in resp.json()["detail"].lower()


async def test_reset_invalidates_existing_access_tokens(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    signup_body = (
        await client.post("/auth/signup", json={"email": EMAIL, "password": PASSWORD})
    ).json()
    headers = {"Authorization": f"Bearer {signup_body['access_token']}"}
    assert (await client.get("/auth/me", headers=headers)).status_code == 200

    await request_reset(client)
    await client.post(
        "/auth/password-reset/confirm",
        json={"token": token_from(fake_sender), "new_password": NEW_PASSWORD},
    )

    assert (await client.get("/auth/me", headers=headers)).status_code == 401


async def test_confirm_is_throttled(client: AsyncClient, clean_rate_limits: None):
    for _ in range(RESET_CONFIRM_PER_IP.max_hits):
        resp = await client.post(
            "/auth/password-reset/confirm",
            json={"token": "wrong", "new_password": NEW_PASSWORD},
        )
        assert resp.status_code == 400

    throttled = await client.post(
        "/auth/password-reset/confirm",
        json={"token": "wrong", "new_password": NEW_PASSWORD},
    )
    assert throttled.status_code == 429
```

Note: `test_reset_invalidates_existing_access_tokens` depends on `password_changed_at` being strictly later than the signup token's `iat`. The signup and the confirm happen in the same test, potentially within one second, and JWT `iat` has one-second resolution. If this test proves flaky, make `consume_reset_token` set `password_changed_at = now + timedelta(seconds=1)` and note why — do not weaken the assertion.

- [ ] **Step 2: Run them and watch them fail**

Run: `cd backend && .venv/bin/pytest tests/test_password_reset.py -v -k confirm or reset_end or once or expired`
Expected: FAIL — 404, the route doesn't exist.

- [ ] **Step 3: Add the consume service**

Append to `backend/app/password_reset.py` (add `hash_password` to the `app.core.security` import):

```python
async def consume_reset_token(
    db: AsyncSession, token: str, new_password: str, *, now: datetime
) -> bool:
    """Spend a token and set the new password. False if the token can't be used.

    Unknown, already-spent and expired tokens all return False, so the caller can answer
    with a single message and leak nothing about which it was.
    """
    row = await db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_reset_token(token)
        )
    )
    if row is None or row.used_at is not None or row.expires_at <= now:
        return False

    user = await db.get(User, row.user_id)
    if user is None:
        return False

    user.password_hash = hash_password(new_password)
    user.password_changed_at = now
    row.used_at = now
    # Any other link already in the user's inbox dies with this one.
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == row.user_id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    await db.commit()
    return True
```

Add `select` to the `sqlalchemy` import line.

- [ ] **Step 4: Add the route**

In `backend/app/api/routes/auth.py`, add `RESET_CONFIRM_PER_IP` to the `app.core.rate_limit` import, `consume_reset_token` to the `app.password_reset` import, `PasswordResetConfirm` to the schemas import, and append:

```python
@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_password_reset(
    body: PasswordResetConfirm, db: DbSession, limiter: Limiter
) -> None:
    await limiter.enforce("reset-confirm", RESET_CONFIRM_PER_IP)

    ok = await consume_reset_token(db, body.token, body.new_password, now=datetime.now(UTC))
    if not ok:
        # One message for unknown, spent and expired alike: distinguishing them would say
        # whether a token — and so an account — exists.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That reset link is invalid or has expired. Request a new one.",
        )
```

- [ ] **Step 5: Run the tests**

Run: `cd backend && .venv/bin/pytest tests/test_password_reset.py -v`
Expected: PASS.

- [ ] **Step 6: Run the whole suite**

Run: `cd backend && .venv/bin/pytest -q`
Expected: PASS.

- [ ] **Step 7: Check the OpenAPI schema renders**

Run: `cd backend && .venv/bin/python -c "from app.main import app; import json; print(json.dumps(sorted(app.openapi()['paths']), indent=2))"`
Expected: the list includes `/auth/password-reset/request` and `/auth/password-reset/confirm`.

- [ ] **Step 8: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/app/password_reset.py backend/app/api/routes/auth.py backend/tests/test_password_reset.py
git commit -m "Spend a reset token to set a new password, once and only once"
```

---

### Task 10: Documentation and sprint close-out

**Files:**
- Modify: `backend/README.md`, `backend/.env.example`, `docs/sprints/sprint-07-auth-hardening.md`, `docs/STATUS.md`

- [ ] **Step 1: Document the new settings**

In `backend/.env.example`, add:

```
# Rate limiting keys on the client IP. Leave TRUST_PROXY_HEADER off unless the API really
# sits behind a proxy: with nothing in front, X-Forwarded-For is attacker-controlled and
# trusting it makes the per-IP limit useless.
TRUST_PROXY_HEADER=false
# How many proxies append to X-Forwarded-For before the request reaches the API.
TRUSTED_PROXY_HOPS=1
```

- [ ] **Step 2: Document the endpoints**

In `backend/README.md`, add a short "Auth hardening" section covering: the two reset endpoints with their request bodies and status codes, the limits table from the spec, the fact that a password change invalidates older access tokens, and that reset mail goes through `EMAIL_BACKEND` (console in development — the link is printed in the log).

- [ ] **Step 3: Tick the sprint doc**

In `docs/sprints/sprint-07-auth-hardening.md`, set `**Status:** ✅ Done`, check every task box, and under the task list record the two decisions taken: signup keeps its 409 until email verification gets its own sprint, and token invalidation uses `password_changed_at`.

- [ ] **Step 4: Update STATUS.md**

Add Sprint 7 to `docs/STATUS.md` in the same shape as the other sprint entries.

- [ ] **Step 5: Full verification**

Run:
```bash
cd backend && .venv/bin/alembic upgrade head && .venv/bin/pytest -q
```
Expected: migration reports it's at head, whole suite PASSES. Record the actual test count in the commit.

- [ ] **Step 6: Commit**

```bash
cd /home/muhammadibrahim/Opzy
git add backend/README.md backend/.env.example docs
git commit -m "Document the auth hardening endpoints, limits and proxy settings"
```

- [ ] **Step 7: Report, don't push**

Report the final test count and the list of commits. Do **not** push and do **not** open a PR — the owner will say when.

---

## Verification checklist

Every exit criterion in `docs/sprints/sprint-07-auth-hardening.md`, mapped to the test that proves it:

- Repeated failed logins are throttled with a 429 → `test_repeated_failed_logins_are_throttled` (Task 4)
- A user can reset a forgotten password via email end to end → `test_reset_end_to_end` (Task 9)
- A reset token works once → `test_token_works_exactly_once` (Task 9)
- …expires → `test_expired_token_is_rejected` (Task 9)
- …and can't be used to enumerate accounts → `test_unknown_email_looks_identical`, `test_unknown_token_is_rejected_the_same_way` (Tasks 8, 9)
- Reset tokens stored hashed → `test_request_emails_a_link` asserts the token isn't in the stored hash (Task 8)
- Password change invalidates old access tokens → `test_reset_invalidates_existing_access_tokens` (Task 9)

## Known limitations, accepted

- **Fixed windows allow a 2× burst** across a window boundary. Acceptable for brute-force defence; a sliding log costs far more for no benefit at this scale.
- **The reset-request endpoint is not constant-time.** A known email does a token insert and an email send; an unknown one returns immediately. The response body and status are identical, but a determined attacker could time the difference. Closing it means sending the email out-of-band; out of scope for this sprint.
- **JWT `iat` has one-second resolution**, so a token minted in the same second as a password change survives. Irrelevant to the stolen-token case this defends against.
- **Signup still returns 409** for a taken email. Deliberate — see the spec.
