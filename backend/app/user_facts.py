"""What matching knows about a user, loaded from their profile."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.matching.engine import UserFacts
from app.models import Profile, ProfileInterest, ProfileSkill


async def load_user_facts(db: AsyncSession, user_id: uuid.UUID) -> UserFacts | None:
    """None if the user hasn't onboarded yet (has no profile)."""
    profile = await db.scalar(select(Profile).where(Profile.user_id == user_id))
    if profile is None:
        return None
    skills = await db.scalars(select(ProfileSkill.skill).where(ProfileSkill.profile_id == profile.id))
    interests = await db.scalars(
        select(ProfileInterest.opportunity_type).where(ProfileInterest.profile_id == profile.id)
    )
    return UserFacts(
        nationality=profile.nationality,
        education_level=profile.education_level,
        field_of_study=profile.field_of_study,
        skills=frozenset(skills),
        interests=frozenset(interests),
    )
