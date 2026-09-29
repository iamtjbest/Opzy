"""Sending email: one interface, with a console backend for development and Resend for real."""

import logging
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"
EMAIL_TIMEOUT_SECONDS = 10


class EmailError(Exception):
    """The provider didn't accept the email. Safe to retry later."""


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    text: str
    html: str


class EmailSender(Protocol):
    async def send(self, message: EmailMessage) -> None: ...


class ConsoleSender:
    """Logs each email instead of sending it."""

    async def send(self, message: EmailMessage) -> None:
        logger.info("Email to %s: %s\n%s", message.to, message.subject, message.text)


class ResendSender:
    def __init__(self, api_key: str, sender: str, client: httpx.AsyncClient) -> None:
        self._api_key = api_key
        self._sender = sender
        self._client = client

    async def send(self, message: EmailMessage) -> None:
        try:
            resp = await self._client.post(
                RESEND_URL,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "from": self._sender,
                    "to": [message.to],
                    "subject": message.subject,
                    "text": message.text,
                    "html": message.html,
                },
            )
        except httpx.HTTPError as exc:
            raise EmailError(f"Couldn't reach Resend: {exc}") from exc
        if resp.is_error:
            raise EmailError(f"Resend refused the email ({resp.status_code}): {resp.text}")


def get_email_sender(settings: Settings, http: httpx.AsyncClient) -> EmailSender:
    """The configured backend. The caller owns `http` and closes it."""
    if settings.email_backend == "resend":
        # Settings refuses to load resend without both of these.
        assert settings.resend_api_key and settings.email_from
        return ResendSender(settings.resend_api_key, settings.email_from, http)
    return ConsoleSender()
