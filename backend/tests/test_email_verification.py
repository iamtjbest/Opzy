from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import (
    SIGNUP_PER_EMAIL,
    VERIFY_CONFIRM_PER_IP,
    VERIFY_RESEND_PER_EMAIL,
)
from app.core.security import VERIFICATION_TOKEN_TTL, hash_url_token
from app.email_verification import (
    compose_account_exists_email,
    compose_verification_email,
)
from app.models import EmailVerificationToken, User
from tests.conftest import FakeSender

EMAIL = "ada@example.com"
PASSWORD = "correct horse battery"


async def signup(client: AsyncClient, email: str = EMAIL, password: str = PASSWORD):
    return await client.post("/auth/signup", json={"email": email, "password": password})


def token_from(sender: FakeSender) -> str:
    """The verification token out of the most recent email."""
    link = sender.sent[-1].text.split("?token=")[1]
    return link.split()[0].strip()


# --- composing ---------------------------------------------------------------------------


def test_verification_email_carries_a_working_link():
    message = compose_verification_email("ada@example.com", "tok-123", "https://opzy.app/")

    assert message.to == "ada@example.com"
    link = "https://opzy.app/verify-email?token=tok-123"
    assert link in message.text
    assert link in message.html


def test_verification_email_percent_encodes_the_token():
    # A raw "&" would end the query parameter early and truncate the token.
    message = compose_verification_email("ada@example.com", "a&b", "https://opzy.app")

    assert "token=a%26b" in message.text
    assert "token=a%26b" in message.html
    assert "token=a&b" not in message.html


def test_account_exists_email_carries_no_token():
    message = compose_account_exists_email("ada@example.com", "https://opzy.app")

    assert message.to == "ada@example.com"
    assert "token=" not in message.text
    assert "token=" not in message.html
    assert "https://opzy.app/forgot-password" in message.text


def test_verification_token_lives_for_a_day():
    assert VERIFICATION_TOKEN_TTL.total_seconds() == 24 * 3600


# --- signup no longer distinguishes a taken address ---------------------------------------


async def test_signup_accepts_without_logging_anyone_in(client: AsyncClient):
    resp = await signup(client)

    assert resp.status_code == 202
    assert "access_token" not in resp.json()


async def test_signup_is_identical_for_new_and_existing_addresses(
    client: AsyncClient, clean_rate_limits: None
):
    first = await signup(client)
    second = await signup(client, email="ADA@example.com")

    assert first.status_code == second.status_code == 202
    assert first.json() == second.json()


async def test_signup_emails_a_verification_link_to_a_new_address(
    client: AsyncClient, fake_sender: FakeSender, db_session: AsyncSession
):
    await signup(client)

    assert len(fake_sender.sent) == 1
    assert fake_sender.sent[0].to == EMAIL
    row = await db_session.scalar(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == hash_url_token(token_from(fake_sender))
        )
    )
    assert row is not None


async def test_signup_on_a_taken_address_emails_a_notice_and_makes_no_token(
    client: AsyncClient, fake_sender: FakeSender, db_session: AsyncSession
):
    await signup(client)
    fake_sender.sent.clear()

    await signup(client, password="a completely different one")

    assert len(fake_sender.sent) == 1
    assert "token=" not in fake_sender.sent[0].text
    tokens = (
        await db_session.scalars(select(EmailVerificationToken))
    ).all()
    assert len(tokens) == 1  # still only the one from the first signup


async def test_signup_on_a_taken_address_does_not_change_the_password(
    client: AsyncClient, clean_rate_limits: None
):
    await signup(client)
    await signup(client, password="an attacker's password")

    form = {"username": EMAIL, "password": "an attacker's password"}
    assert (await client.post("/auth/login", data=form)).status_code == 401


async def test_signup_is_throttled_per_email(
    client: AsyncClient, clean_rate_limits: None
):
    for _ in range(SIGNUP_PER_EMAIL.max_hits):
        assert (await signup(client)).status_code == 202

    assert (await signup(client)).status_code == 429


# --- confirming --------------------------------------------------------------------------


async def test_confirm_verifies_the_account_and_logs_the_user_in(
    client: AsyncClient, fake_sender: FakeSender, db_session: AsyncSession
):
    await signup(client)

    resp = await client.post(
        "/auth/verify-email/confirm", json={"token": token_from(fake_sender)}
    )

    assert resp.status_code == 200
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    me = await client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == EMAIL
    assert me.json()["email_verified_at"] is not None

    user = await db_session.scalar(select(User).where(User.email == EMAIL))
    assert user.email_verified_at is not None


async def test_a_verification_token_works_only_once(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    await signup(client)
    token = token_from(fake_sender)
    assert (
        await client.post("/auth/verify-email/confirm", json={"token": token})
    ).status_code == 200

    second = await client.post("/auth/verify-email/confirm", json={"token": token})

    assert second.status_code == 400


async def test_unknown_spent_and_expired_tokens_are_indistinguishable(
    client: AsyncClient,
    fake_sender: FakeSender,
    db_session: AsyncSession,
    clean_rate_limits: None,
):
    await signup(client)
    spent = token_from(fake_sender)
    await client.post("/auth/verify-email/confirm", json={"token": spent})

    # A second, still-unverified account supplies the expired token: the first one is
    # verified now, so asking it to resend correctly yields a note with no token in it.
    await signup(client, email="grace@example.com")
    expired_token = token_from(fake_sender)
    row = await db_session.scalar(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == hash_url_token(expired_token)
        )
    )
    row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.commit()

    answers = [
        await client.post("/auth/verify-email/confirm", json={"token": token})
        for token in ("never-existed", spent, expired_token)
    ]

    assert {resp.status_code for resp in answers} == {400}
    assert len({resp.text for resp in answers}) == 1


async def test_confirm_is_throttled_per_ip(client: AsyncClient, clean_rate_limits: None):
    for _ in range(VERIFY_CONFIRM_PER_IP.max_hits):
        resp = await client.post("/auth/verify-email/confirm", json={"token": "nope"})
        assert resp.status_code == 400

    throttled = await client.post("/auth/verify-email/confirm", json={"token": "nope"})
    assert throttled.status_code == 429


# --- resending ---------------------------------------------------------------------------


async def test_resend_is_identical_for_known_and_unknown_addresses(
    client: AsyncClient, clean_rate_limits: None
):
    await signup(client)

    known = await client.post("/auth/verify-email/resend", json={"email": EMAIL})
    unknown = await client.post(
        "/auth/verify-email/resend", json={"email": "nobody@example.com"}
    )

    assert known.status_code == unknown.status_code == 202
    assert known.json() == unknown.json()


async def test_resend_emails_a_fresh_link_that_works(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    await signup(client)
    first_token = token_from(fake_sender)

    await client.post("/auth/verify-email/resend", json={"email": EMAIL})
    second_token = token_from(fake_sender)

    assert second_token != first_token
    resp = await client.post("/auth/verify-email/confirm", json={"token": second_token})
    assert resp.status_code == 200


async def test_resending_retires_the_previous_link(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    await signup(client)
    first_token = token_from(fake_sender)
    await client.post("/auth/verify-email/resend", json={"email": EMAIL})

    resp = await client.post("/auth/verify-email/confirm", json={"token": first_token})

    assert resp.status_code == 400


async def test_resend_to_an_unknown_address_sends_nothing(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    await client.post("/auth/verify-email/resend", json={"email": "nobody@example.com"})

    assert fake_sender.sent == []


async def test_resend_to_a_verified_account_sends_no_new_link(
    client: AsyncClient, fake_sender: FakeSender, clean_rate_limits: None
):
    await signup(client)
    await client.post(
        "/auth/verify-email/confirm", json={"token": token_from(fake_sender)}
    )
    fake_sender.sent.clear()

    await client.post("/auth/verify-email/resend", json={"email": EMAIL})

    assert len(fake_sender.sent) == 1
    assert "token=" not in fake_sender.sent[0].text


async def test_resend_is_throttled_per_email(client: AsyncClient, clean_rate_limits: None):
    for _ in range(VERIFY_RESEND_PER_EMAIL.max_hits):
        resp = await client.post("/auth/verify-email/resend", json={"email": EMAIL})
        assert resp.status_code == 202

    throttled = await client.post("/auth/verify-email/resend", json={"email": EMAIL})
    assert throttled.status_code == 429


# --- an unverified account is still a usable account --------------------------------------


async def test_an_unverified_account_can_log_in(client: AsyncClient):
    await signup(client)

    resp = await client.post(
        "/auth/login", data={"username": EMAIL, "password": PASSWORD}
    )

    assert resp.status_code == 200
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    me = await client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email_verified_at"] is None
