import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Profile, ProfileInterest, ProfileSkill, User


async def _make_profile(db_session: AsyncSession) -> Profile:
    user = User(email="constraints@example.com", password_hash="not-a-real-hash")
    db_session.add(user)
    await db_session.flush()
    profile = Profile(user_id=user.id)
    db_session.add(profile)
    await db_session.flush()
    return profile


# --- database constraints --------------------------------------------------------------


async def test_database_rejects_duplicate_skill(db_session: AsyncSession):
    profile = await _make_profile(db_session)
    db_session.add_all(
        [
            ProfileSkill(profile_id=profile.id, skill="python"),
            ProfileSkill(profile_id=profile.id, skill="python"),
        ]
    )
    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_database_rejects_duplicate_interest(db_session: AsyncSession):
    profile = await _make_profile(db_session)
    db_session.add_all(
        [
            ProfileInterest(profile_id=profile.id, opportunity_type="job"),
            ProfileInterest(profile_id=profile.id, opportunity_type="job"),
        ]
    )
    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_database_rejects_unknown_education_level(db_session: AsyncSession):
    profile = await _make_profile(db_session)
    profile.education_level = "University student"
    with pytest.raises(IntegrityError):
        await db_session.flush()


# --- API -------------------------------------------------------------------------------

PASSWORD = "correct horse battery"

# What the onboarding form sends, using the stored values (not display labels).
ONBOARDING = {
    "nationality": "NG",
    "education_level": "undergraduate",
    "field_of_study": "Computer Engineering",
    "location": "Zaria, Kaduna",
    "skills": ["Python", "Public speaking", "Figma"],
    "interests": ["job", "internship", "hackathon"],
}


async def auth_headers(client: AsyncClient, email: str = "ada@example.com") -> dict[str, str]:
    """Create an account and log in.

    Two calls, not one: since Sprint 9 signup answers 202 with no access token, so that it
    reads the same whether or not the address was already registered. The account is left
    unverified, which is a usable account everywhere except notification email — tests that
    care about that verify it explicitly.
    """
    resp = await client.post("/auth/signup", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 202
    login = await client.post(
        "/auth/login", data={"username": email, "password": PASSWORD}
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def test_profile_routes_require_auth(client: AsyncClient):
    assert (await client.get("/profile")).status_code == 401
    assert (await client.put("/profile", json=ONBOARDING)).status_code == 401


async def test_get_profile_before_onboarding_is_404(client: AsyncClient):
    headers = await auth_headers(client)

    resp = await client.get("/profile", headers=headers)

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Profile not found"


async def test_put_creates_profile_and_get_returns_it(client: AsyncClient):
    headers = await auth_headers(client)

    put = await client.put("/profile", json=ONBOARDING, headers=headers)

    assert put.status_code == 200
    body = put.json()
    assert body["nationality"] == "NG"
    assert body["education_level"] == "undergraduate"
    assert body["field_of_study"] == "Computer Engineering"
    assert body["location"] == "Zaria, Kaduna"
    assert body["skills"] == ["figma", "public speaking", "python"]
    assert body["interests"] == ["job", "internship", "hackathon"]
    assert body["updated_at"]

    get = await client.get("/profile", headers=headers)
    assert get.status_code == 200
    assert get.json() == body


async def test_put_replaces_the_whole_profile(client: AsyncClient, db_session: AsyncSession):
    headers = await auth_headers(client)
    await client.put("/profile", json=ONBOARDING, headers=headers)

    resp = await client.put(
        "/profile",
        json={
            "nationality": None,
            "education_level": None,
            "field_of_study": "Mathematics",
            "location": "Lagos",
            "skills": ["Excel"],
            "interests": ["scholarship"],
        },
        headers=headers,
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["nationality"] is None
    assert body["education_level"] is None
    assert body["field_of_study"] == "Mathematics"
    assert body["location"] == "Lagos"
    assert body["skills"] == ["excel"]
    assert body["interests"] == ["scholarship"]

    # Still one profile row, and the old tags are gone from the database, not just the response.
    user_id = uuid.UUID((await client.get("/auth/me", headers=headers)).json()["id"])
    profile_ids = list(await db_session.scalars(select(Profile.id).where(Profile.user_id == user_id)))
    assert len(profile_ids) == 1
    skills = await db_session.scalars(
        select(ProfileSkill.skill).where(ProfileSkill.profile_id == profile_ids[0])
    )
    assert list(skills) == ["excel"]
    interest_count = await db_session.scalar(
        select(func.count())
        .select_from(ProfileInterest)
        .where(ProfileInterest.profile_id == profile_ids[0])
    )
    assert interest_count == 1


async def test_put_can_clear_skills_and_interests(client: AsyncClient):
    headers = await auth_headers(client)
    await client.put("/profile", json=ONBOARDING, headers=headers)

    resp = await client.put(
        "/profile", json={**ONBOARDING, "skills": [], "interests": []}, headers=headers
    )

    assert resp.status_code == 200
    assert resp.json()["skills"] == []
    assert resp.json()["interests"] == []


async def test_put_normalizes_input(client: AsyncClient):
    headers = await auth_headers(client)

    resp = await client.put(
        "/profile",
        json={
            "nationality": " ng ",
            "education_level": "   ",
            "field_of_study": "  Computer Engineering  ",
            "location": "",
            "skills": ["  Python ", "python", "PYTHON", "Figma"],
            "interests": ["hackathon", "job", "hackathon"],
        },
        headers=headers,
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["nationality"] == "NG"
    assert body["education_level"] is None
    assert body["field_of_study"] == "Computer Engineering"
    assert body["location"] is None
    assert body["skills"] == ["figma", "python"]
    assert body["interests"] == ["job", "hackathon"]


async def test_skills_are_sorted_alphabetically_not_by_db_collation(client: AsyncClient):
    # Under the local DB's en_US.utf8 collation, ORDER BY gives ["publicity", "public speaking"];
    # Python's sort (C collation) gives ["public speaking", "publicity"]. The API contract is
    # alphabetical order, deterministic regardless of the DB's collation.
    headers = await auth_headers(client)

    put = await client.put(
        "/profile", json={**ONBOARDING, "skills": ["publicity", "Public speaking"]}, headers=headers
    )

    assert put.status_code == 200
    assert put.json()["skills"] == ["public speaking", "publicity"]

    get = await client.get("/profile", headers=headers)
    assert get.json()["skills"] == ["public speaking", "publicity"]


async def test_put_bumps_updated_at(client: AsyncClient):
    headers = await auth_headers(client)

    first = (await client.put("/profile", json=ONBOARDING, headers=headers)).json()
    second = (await client.put("/profile", json=ONBOARDING, headers=headers)).json()

    assert datetime.fromisoformat(second["updated_at"]) > datetime.fromisoformat(
        first["updated_at"]
    )


async def test_profiles_are_per_user(client: AsyncClient):
    ada = await auth_headers(client, "ada@example.com")
    bob = await auth_headers(client, "bob@example.com")
    await client.put("/profile", json=ONBOARDING, headers=ada)

    assert (await client.get("/profile", headers=bob)).status_code == 404

    await client.put(
        "/profile", json={**ONBOARDING, "skills": ["Excel"], "interests": ["grant"]}, headers=bob
    )
    ada_profile = (await client.get("/profile", headers=ada)).json()
    assert ada_profile["skills"] == ["figma", "public speaking", "python"]
    assert ada_profile["interests"] == ["job", "internship", "hackathon"]


@pytest.mark.parametrize(
    "change",
    [
        {"interests": ["Jobs"]},  # the frontend's display label, not a stored value
        {"interests": ["job"] * 8},
        {"skills": ["   "]},
        {"skills": ["x" * 51]},
        {"skills": [f"skill {i}" for i in range(31)]},
        {"location": "x" * 101},
        {"unexpected": "field"},
        {"education_level": "University student"},  # free text from before Sprint 4
        {"nationality": "Nigeria"},
        {"nationality": "XX"},
    ],
)
async def test_put_rejects_invalid_input(client: AsyncClient, change: dict):
    headers = await auth_headers(client)

    resp = await client.put("/profile", json={**ONBOARDING, **change}, headers=headers)

    assert resp.status_code == 422
    assert (await client.get("/profile", headers=headers)).status_code == 404


@pytest.mark.parametrize("missing", list(ONBOARDING))
async def test_put_requires_every_field(client: AsyncClient, missing: str):
    headers = await auth_headers(client)
    body = {k: v for k, v in ONBOARDING.items() if k != missing}

    resp = await client.put("/profile", json=body, headers=headers)

    assert resp.status_code == 422
