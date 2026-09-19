import json
import logging

import httpx
import pytest

from app.email import (
    ConsoleSender,
    EmailError,
    EmailMessage,
    ResendSender,
    get_email_sender,
)
from tests.test_config import RESEND, build

MESSAGE = EmailMessage(
    to="ada@example.com", subject="Hello", text="Plain body", html="<p>HTML body</p>"
)


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_console_sender_logs_the_email(caplog):
    with caplog.at_level(logging.INFO, logger="app.email"):
        await ConsoleSender().send(MESSAGE)

    assert "ada@example.com" in caplog.text
    assert "Hello" in caplog.text
    assert "Plain body" in caplog.text


async def test_resend_sender_posts_the_email():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"id": "email_123"})

    async with _client(handler) as client:
        await ResendSender("re_key", "Opzy <hello@example.com>", client).send(MESSAGE)

    [request] = requests
    assert str(request.url) == "https://api.resend.com/emails"
    assert request.headers["Authorization"] == "Bearer re_key"
    assert json.loads(request.content) == {
        "from": "Opzy <hello@example.com>",
        "to": ["ada@example.com"],
        "subject": "Hello",
        "text": "Plain body",
        "html": "<p>HTML body</p>",
    }


@pytest.mark.parametrize("status", [400, 422, 500])
async def test_resend_sender_raises_when_refused(status):
    async with _client(lambda request: httpx.Response(status, json={"message": "no"})) as client:
        with pytest.raises(EmailError, match=str(status)):
            await ResendSender("re_key", "hello@example.com", client).send(MESSAGE)


async def test_resend_sender_raises_when_unreachable():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    async with _client(handler) as client:
        with pytest.raises(EmailError):
            await ResendSender("re_key", "hello@example.com", client).send(MESSAGE)


async def test_get_email_sender_picks_the_configured_backend():
    async with httpx.AsyncClient() as client:
        assert isinstance(get_email_sender(build(EMAIL_BACKEND="console"), client), ConsoleSender)
        assert isinstance(get_email_sender(build(**RESEND), client), ResendSender)
