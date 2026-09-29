from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import (
    Limit,
    client_ip,
    hit,
    prune,
    refund,
    window_start,
)
from app.models import RateLimitHit


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
    internal_api_secret: str | None = None


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


# --- the frontend vouching for a browser's address -------------------------------------

SECRET = "f" * 40
FRONTEND = FakeSettings(internal_api_secret=SECRET)


def vouched(ip: str, secret: str = SECRET) -> dict[str, str]:
    return {"x-opzy-client-ip": ip, "x-opzy-internal-secret": secret}


def test_frontend_can_say_which_browser_a_request_is_for():
    # Every call from Next.js arrives from the Next.js server. Without this, one person's
    # failed logins lock out the whole site.
    request = FakeRequest("10.0.0.2", vouched("203.0.113.7"))

    assert client_ip(request, FRONTEND) == "203.0.113.7"


def test_client_ip_header_is_ignored_without_the_secret():
    # Anyone can send the header; only the frontend knows the secret.
    request = FakeRequest("198.51.100.1", {"x-opzy-client-ip": "1.1.1.1"})

    assert client_ip(request, FRONTEND) == "198.51.100.1"


def test_client_ip_header_is_ignored_with_a_wrong_secret():
    request = FakeRequest("198.51.100.1", vouched("1.1.1.1", secret="g" * 40))

    assert client_ip(request, FRONTEND) == "198.51.100.1"


def test_client_ip_header_is_ignored_when_no_secret_is_configured():
    # An unset secret must not match an empty header.
    request = FakeRequest("198.51.100.1", vouched("1.1.1.1", secret=""))

    assert client_ip(request, FakeSettings()) == "198.51.100.1"


def test_vouched_value_must_be_an_ip_address():
    # Free text would let a compromised or buggy caller mint unlimited distinct keys.
    request = FakeRequest("10.0.0.2", vouched("not-an-ip"))

    assert client_ip(request, FRONTEND) == "10.0.0.2"


def test_vouched_ipv6_is_normalised():
    request = FakeRequest("10.0.0.2", vouched("2001:DB8:0:0::1"))

    assert client_ip(request, FRONTEND) == "2001:db8::1"


NOW = datetime(2026, 9, 20, 12, 7, 30, tzinfo=UTC)
TEN_PER_MINUTE = Limit(max_hits=10, window_seconds=60)


def test_window_start_floors_to_the_window():
    assert window_start(NOW, 60) == datetime(2026, 9, 20, 12, 7, tzinfo=UTC)
    assert window_start(NOW, 900) == datetime(2026, 9, 20, 12, 0, tzinfo=UTC)
    assert window_start(NOW, 3600) == datetime(2026, 9, 20, 12, 0, tzinfo=UTC)


async def test_hit_counts_up_within_a_window(db_session: AsyncSession):
    first = await hit(db_session, "login:ip:1.2.3.4", TEN_PER_MINUTE, now=NOW)
    second = await hit(
        db_session, "login:ip:1.2.3.4", TEN_PER_MINUTE, now=NOW + timedelta(seconds=5)
    )

    assert (first, second) == (1, 2)


async def test_hit_starts_over_in_the_next_window(db_session: AsyncSession):
    await hit(db_session, "login:ip:1.2.3.4", TEN_PER_MINUTE, now=NOW)
    later = await hit(
        db_session, "login:ip:1.2.3.4", TEN_PER_MINUTE, now=NOW + timedelta(minutes=1)
    )

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

    rows = (
        await db_session.scalars(
            select(RateLimitHit).where(RateLimitHit.key == "login:ip:9.9.9.9")
        )
    ).all()
    assert len(rows) == 1
    assert rows[0].window_start == window_start(NOW, 60)
