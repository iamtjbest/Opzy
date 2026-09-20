from dataclasses import dataclass

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
