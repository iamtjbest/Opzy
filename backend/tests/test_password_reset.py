from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import RESET_REQUEST_PER_EMAIL
from app.core.security import RESET_TOKEN_TTL, generate_reset_token, hash_reset_token
from app.email import EmailError
from app.models import PasswordResetToken
from app.password_reset import compose_password_reset_email
from tests.conftest import FakeSender


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


def test_reset_email_percent_encodes_the_token():
    # A raw "&" would end the query parameter early and truncate the token.
    message = compose_password_reset_email("ada@example.com", "a&b", "https://opzy.app")

    assert "token=a%26b" in message.text
    assert "token=a%26b" in message.html
    assert "token=a&b" not in message.html


EMAIL = "ada@example.com"
PASSWORD = "correct horse battery"


async def signup(client: AsyncClient, email: str = EMAIL) -> None:
    resp = await client.post("/auth/signup", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 201


def token_from(sender: FakeSender) -> str:
    link = sender.sent[-1].text.split("?token=")[1]
    return link.split()[0].strip()


async def test_request_emails_a_link(
    client: AsyncClient,
    fake_sender: FakeSender,
    db_session: AsyncSession,
    clean_rate_limits: None,
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
    client: AsyncClient,
    fake_sender: FakeSender,
    db_session: AsyncSession,
    clean_rate_limits: None,
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
