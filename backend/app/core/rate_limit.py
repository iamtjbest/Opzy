"""Fixed-window rate limiting, counted in Postgres so it holds across worker processes."""

import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.config import Settings
from app.models import RateLimitHit

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


@dataclass(frozen=True)
class Limit:
    max_hits: int
    window_seconds: int


MINUTES_15 = 15 * 60
HOUR = 60 * 60

LOGIN_PER_IP = Limit(max_hits=30, window_seconds=MINUTES_15)
LOGIN_PER_EMAIL = Limit(max_hits=10, window_seconds=MINUTES_15)
SIGNUP_PER_IP = Limit(max_hits=5, window_seconds=HOUR)
# Signup mails the address whether or not it has an account, so without a per-email budget
# it can be pointed at one inbox as a mail cannon.
SIGNUP_PER_EMAIL = Limit(max_hits=3, window_seconds=HOUR)
RESET_REQUEST_PER_IP = Limit(max_hits=10, window_seconds=HOUR)
RESET_REQUEST_PER_EMAIL = Limit(max_hits=3, window_seconds=HOUR)
RESET_CONFIRM_PER_IP = Limit(max_hits=10, window_seconds=HOUR)
VERIFY_RESEND_PER_IP = Limit(max_hits=10, window_seconds=HOUR)
VERIFY_RESEND_PER_EMAIL = Limit(max_hits=3, window_seconds=HOUR)
VERIFY_CONFIRM_PER_IP = Limit(max_hits=10, window_seconds=HOUR)
ACCOUNT_DELETE_PER_IP = Limit(max_hits=10, window_seconds=HOUR)

# Nothing is counted in a window longer than this, so older rows can never affect a decision.
LONGEST_WINDOW_SECONDS = HOUR


def window_start(now: datetime, window_seconds: int) -> datetime:
    """Floor `now` to the start of its fixed window."""
    epoch_seconds = int(now.timestamp())
    return datetime.fromtimestamp(epoch_seconds - epoch_seconds % window_seconds, tz=UTC)


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
