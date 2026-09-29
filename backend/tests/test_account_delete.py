import uuid

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import ACCOUNT_DELETE_PER_IP
from app.models import (
    EmailVerificationToken,
    PasswordResetToken,
    Profile,
    ProfileInterest,
    ProfileSkill,
    User,
    UserOpportunityAction,
)

EMAIL = "ada@example.com"
PASSWORD = "correct horse battery"

ONBOARDING = {
    "nationality": "NG",
    "education_level": "undergraduate",
    "field_of_study": "Computer Engineering",
    "location": "Zaria, Kaduna",
    "skills": ["Python", "Figma"],
    "interests": ["job", "internship"],
}


async def count_of(db: AsyncSession, model, condition) -> int:
    return await db.scalar(select(func.count()).select_from(model).where(condition))


async def signed_up(client: AsyncClient, email: str = EMAIL) -> dict[str, str]:
    """Create an account and log in, returning auth headers."""
    resp = await client.post("/auth/signup", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 202
    login = await client.post("/auth/login", data={"username": email, "password": PASSWORD})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def test_delete_requires_auth(client: AsyncClient):
    resp = await client.request("DELETE", "/account", json={"password": PASSWORD})

    assert resp.status_code == 401


async def test_delete_requires_the_right_password(
    client: AsyncClient, db_session: AsyncSession, clean_rate_limits: None
):
    headers = await signed_up(client)

    resp = await client.request(
        "DELETE", "/account", json={"password": "not the password"}, headers=headers
    )

    # 403, not 401: the session is fine, the password isn't. A 401 here would be read as an
    # expired token and log the user out over a typo.
    assert resp.status_code == 403
    assert await db_session.scalar(select(User).where(User.email == EMAIL)) is not None


async def test_delete_removes_the_account(
    client: AsyncClient, db_session: AsyncSession, clean_rate_limits: None
):
    headers = await signed_up(client)

    resp = await client.request(
        "DELETE", "/account", json={"password": PASSWORD}, headers=headers
    )

    assert resp.status_code == 204
    assert await db_session.scalar(select(User).where(User.email == EMAIL)) is None


async def test_the_deleted_users_token_stops_working(
    client: AsyncClient, clean_rate_limits: None
):
    headers = await signed_up(client)
    await client.request("DELETE", "/account", json={"password": PASSWORD}, headers=headers)

    assert (await client.get("/auth/me", headers=headers)).status_code == 401


async def test_delete_takes_the_profile_and_actions_with_it(
    client: AsyncClient, db_session: AsyncSession, clean_rate_limits: None
):
    headers = await signed_up(client)
    user_id = uuid.UUID((await client.get("/auth/me", headers=headers)).json()["id"])
    assert (await client.put("/profile", json=ONBOARDING, headers=headers)).status_code == 200
    profile_id = await db_session.scalar(
        select(Profile.id).where(Profile.user_id == user_id)
    )
    listing = await client.get("/opportunities", headers=headers)
    opportunity_id = listing.json()["items"][0]["id"]
    acted = await client.post(
        f"/opportunities/{opportunity_id}/actions",
        json={"action": "saved"},
        headers=headers,
    )
    assert acted.status_code == 200

    await client.request("DELETE", "/account", json={"password": PASSWORD}, headers=headers)

    # Scoped to this user rather than whole-table counts: the dev database is seeded.
    assert await count_of(db_session, Profile, Profile.user_id == user_id) == 0
    assert await count_of(db_session, ProfileSkill, ProfileSkill.profile_id == profile_id) == 0
    assert (
        await count_of(db_session, ProfileInterest, ProfileInterest.profile_id == profile_id)
        == 0
    )
    assert (
        await count_of(
            db_session, UserOpportunityAction, UserOpportunityAction.user_id == user_id
        )
        == 0
    )


async def test_delete_takes_the_reset_and_verification_tokens_with_it(
    client: AsyncClient, db_session: AsyncSession, clean_rate_limits: None
):
    headers = await signed_up(client)  # signup minted a verification token
    user_id = uuid.UUID((await client.get("/auth/me", headers=headers)).json()["id"])
    await client.post("/auth/password-reset/request", json={"email": EMAIL})
    assert (
        await count_of(
            db_session, EmailVerificationToken, EmailVerificationToken.user_id == user_id
        )
        == 1
    )

    await client.request("DELETE", "/account", json={"password": PASSWORD}, headers=headers)

    assert (
        await count_of(
            db_session, EmailVerificationToken, EmailVerificationToken.user_id == user_id
        )
        == 0
    )
    assert (
        await count_of(db_session, PasswordResetToken, PasswordResetToken.user_id == user_id)
        == 0
    )


async def test_the_email_is_free_to_sign_up_again(
    client: AsyncClient, clean_rate_limits: None
):
    headers = await signed_up(client)
    original_id = (await client.get("/auth/me", headers=headers)).json()["id"]
    await client.request("DELETE", "/account", json={"password": PASSWORD}, headers=headers)

    resp = await client.post("/auth/signup", json={"email": EMAIL, "password": PASSWORD})

    assert resp.status_code == 202
    again = await client.post("/auth/login", data={"username": EMAIL, "password": PASSWORD})
    assert again.status_code == 200
    fresh = {"Authorization": f"Bearer {again.json()['access_token']}"}
    me = (await client.get("/auth/me", headers=fresh)).json()
    # A brand-new account, not the old one resurrected: new id, and unverified again.
    assert me["id"] != original_id
    assert me["email_verified_at"] is None


async def test_delete_is_throttled_per_ip(client: AsyncClient, clean_rate_limits: None):
    headers = await signed_up(client)

    for _ in range(ACCOUNT_DELETE_PER_IP.max_hits):
        resp = await client.request(
            "DELETE", "/account", json={"password": "wrong"}, headers=headers
        )
        assert resp.status_code == 403

    throttled = await client.request(
        "DELETE", "/account", json={"password": "wrong"}, headers=headers
    )
    assert throttled.status_code == 429
