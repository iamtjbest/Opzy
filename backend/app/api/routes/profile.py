from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession
from app.models import Profile, ProfileInterest, ProfileSkill
from app.models.base import OPPORTUNITY_TYPES
from app.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


def _build_read(profile: Profile, skills: list[str], interests: list[str]) -> ProfileRead:
    return ProfileRead(
        nationality=profile.nationality,
        education_level=profile.education_level,
        field_of_study=profile.field_of_study,
        location=profile.location,
        # Sorted in Python, not via ORDER BY: SQL collation (e.g. en_US.utf8 locally) can order
        # strings differently from Python's, so the API's "alphabetical" contract must not depend
        # on which DB it's running against.
        skills=sorted(skills),
        # Canonical order, so the response doesn't depend on insertion order.
        interests=sorted(interests, key=OPPORTUNITY_TYPES.index),
        updated_at=profile.updated_at,
    )


async def _to_read(db: AsyncSession, profile: Profile) -> ProfileRead:
    skills = await db.scalars(
        select(ProfileSkill.skill).where(ProfileSkill.profile_id == profile.id)
    )
    interests = await db.scalars(
        select(ProfileInterest.opportunity_type).where(ProfileInterest.profile_id == profile.id)
    )
    return _build_read(profile, list(skills), list(interests))


@router.get("", response_model=ProfileRead)
async def get_profile(user: CurrentUser, db: DbSession) -> ProfileRead:
    profile = await db.scalar(select(Profile).where(Profile.user_id == user.id))
    if profile is None:
        # Not onboarded yet; the frontend sends the user to /onboarding on this.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return await _to_read(db, profile)


@router.put("", response_model=ProfileRead)
async def put_profile(body: ProfileUpdate, user: CurrentUser, db: DbSession) -> ProfileRead:
    fields = {
        "nationality": body.nationality,
        "education_level": body.education_level,
        "field_of_study": body.field_of_study,
        "location": body.location,
        # Set here, not left to now(): the column has no update trigger, and now() is fixed
        # for the whole transaction.
        "updated_at": datetime.now(UTC),
    }
    # Upsert on the one-profile-per-user unique index, so two first saves racing each other
    # can't both insert. The row lock it takes also serialises concurrent saves for the same
    # user, so the tag replacement below can't interleave with another request's.
    stmt = (
        insert(Profile)
        .values(user_id=user.id, **fields)
        .on_conflict_do_update(index_elements=[Profile.user_id], set_=fields)
        .returning(Profile)
    )
    profile = await db.scalar(stmt, execution_options={"populate_existing": True})

    await db.execute(delete(ProfileSkill).where(ProfileSkill.profile_id == profile.id))
    await db.execute(delete(ProfileInterest).where(ProfileInterest.profile_id == profile.id))
    db.add_all([ProfileSkill(profile_id=profile.id, skill=skill) for skill in body.skills])
    db.add_all(
        [ProfileInterest(profile_id=profile.id, opportunity_type=t) for t in body.interests]
    )
    await db.commit()

    # Built from the request body's already-normalized lists, not re-queried: the commit above
    # releases the row lock, so a re-query could race a concurrent PUT for the same user and mix
    # this request's text fields with another request's tags. It also saves two SELECTs.
    return _build_read(profile, body.skills, body.interests)
