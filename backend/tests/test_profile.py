import pytest
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
