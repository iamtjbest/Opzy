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
