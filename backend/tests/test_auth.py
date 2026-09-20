import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import LOGIN_PER_EMAIL, SIGNUP_PER_IP
from app.core.security import create_access_token
from app.models import User

PASSWORD = "correct horse battery"


async def signup(client: AsyncClient, email: str = "ada@example.com", password: str = PASSWORD):
    return await client.post("/auth/signup", json={"email": email, "password": password})


async def login(client: AsyncClient, email: str = "ada@example.com", password: str = PASSWORD):
    return await client.post("/auth/login", data={"username": email, "password": password})


# --- signup ---------------------------------------------------------------------------


async def test_signup_creates_user_and_logs_in(client: AsyncClient, db_session: AsyncSession):
    resp = await signup(client)

    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "ada@example.com"
    assert body["user"]["notification_cadence"] == "daily"
    assert body["user"]["notification_channel"] == "email"

    me = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["id"] == body["user"]["id"]

    user = await db_session.scalar(select(User).where(User.email == "ada@example.com"))
    assert user is not None


async def test_signup_never_stores_or_returns_plaintext(
    client: AsyncClient, db_session: AsyncSession
):
    resp = await signup(client)

    assert PASSWORD not in resp.text
    assert "password" not in resp.json()["user"]
    user = await db_session.scalar(select(User).where(User.email == "ada@example.com"))
    assert user.password_hash != PASSWORD
    assert PASSWORD not in user.password_hash


async def test_signup_normalizes_email(client: AsyncClient):
    resp = await signup(client, email="  Ada@Example.COM ")
    assert resp.status_code == 201
    assert resp.json()["user"]["email"] == "ada@example.com"


async def test_signup_duplicate_email_conflicts(client: AsyncClient):
    assert (await signup(client)).status_code == 201

    resp = await signup(client, email="ADA@example.com")
    assert resp.status_code == 409


async def test_signup_does_not_report_other_constraints_as_conflict(
    client: AsyncClient, db_session: AsyncSession, monkeypatch
):
    """A CHECK violation is a bug, not a taken email — it must not surface as a 409."""

    class CheckViolation(Exception):
        sqlstate = "23514"

    async def fail(*args, **kwargs):
        raise IntegrityError("insert", None, CheckViolation())

    monkeypatch.setattr(type(db_session), "commit", fail)

    with pytest.raises(IntegrityError):
        await signup(client)


async def test_signup_rejects_invalid_email(client: AsyncClient):
    assert (await signup(client, email="not-an-email")).status_code == 422


async def test_signup_rejects_short_password(client: AsyncClient):
    assert (await signup(client, password="short")).status_code == 422


async def test_signup_rejects_overlong_password(client: AsyncClient):
    assert (await signup(client, password="x" * 129)).status_code == 422


# --- login ----------------------------------------------------------------------------


async def test_login_returns_working_token(client: AsyncClient):
    await signup(client)

    resp = await login(client)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert resp.json()["token_type"] == "bearer"

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ada@example.com"


async def test_login_is_case_insensitive_on_email(client: AsyncClient):
    await signup(client)
    assert (await login(client, email=" ADA@example.com")).status_code == 200


async def test_login_wrong_password_and_unknown_email_look_identical(client: AsyncClient):
    await signup(client)

    wrong_password = await login(client, password="not the password")
    unknown_email = await login(client, email="nobody@example.com")

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


async def test_login_rejects_overlong_password(client: AsyncClient):
    await signup(client)
    assert (await login(client, password="x" * 10_000)).status_code == 401


# --- protected route ------------------------------------------------------------------


async def test_me_requires_token(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401
    assert resp.headers["www-authenticate"] == "Bearer"


async def test_me_rejects_garbage_token(client: AsyncClient):
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert resp.status_code == 401


async def test_me_rejects_token_for_missing_user(client: AsyncClient):
    token = create_access_token(uuid.uuid4())
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


async def test_me_never_returns_password_hash(client: AsyncClient):
    token = (await signup(client)).json()["access_token"]
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert "password" not in resp.text


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


# --- token invalidation ---------------------------------------------------------------


async def test_token_issued_before_a_password_change_is_rejected(
    client: AsyncClient, db_session: AsyncSession, clean_rate_limits: None
):
    body = (await signup(client)).json()
    headers = {"Authorization": f"Bearer {body['access_token']}"}
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
