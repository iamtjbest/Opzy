from datetime import date, datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select

from app.actions import current_actions
from app.api.deps import CurrentUser, DbSession
from app.api.routes.opportunities import MAX_PAGE_SIZE
from app.matching.engine import UserFacts
from app.matching.feed import build_feed
from app.models import Opportunity, Profile, ProfileInterest, ProfileSkill
from app.models.base import ACTIVE_STATUS, SAVED
from app.schemas.feed import FeedItem, FeedList
from app.schemas.opportunity import OpportunityRead
from app.schemas.profile import OpportunityType

# Deadlines are Nigerian dates: one stays open through that whole day in Lagos.
DEADLINE_TIMEZONE = ZoneInfo("Africa/Lagos")

router = APIRouter(prefix="/feed", tags=["feed"])


def get_today() -> date:
    return datetime.now(DEADLINE_TIMEZONE).date()


@router.get("", response_model=FeedList)
async def get_feed(
    user: CurrentUser,
    db: DbSession,
    today: Annotated[date, Depends(get_today)],
    category: Annotated[list[OpportunityType] | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> FeedList:
    profile = await db.scalar(select(Profile).where(Profile.user_id == user.id))
    if profile is None:
        # Not onboarded yet; same signal as GET /profile.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    skills = await db.scalars(select(ProfileSkill.skill).where(ProfileSkill.profile_id == profile.id))
    interests = await db.scalars(
        select(ProfileInterest.opportunity_type).where(ProfileInterest.profile_id == profile.id)
    )
    facts = UserFacts(
        nationality=profile.nationality,
        education_level=profile.education_level,
        field_of_study=profile.field_of_study,
        skills=frozenset(skills),
        interests=frozenset(interests),
    )

    # Cheap filters in SQL; the matching engine applies the rest (and re-checks these).
    filters = [
        Opportunity.status == ACTIVE_STATUS,
        or_(Opportunity.deadline >= today, Opportunity.deadline.is_(None)),
    ]
    if category:
        filters.append(Opportunity.category.in_(category))
    opportunities = list(await db.scalars(select(Opportunity).where(*filters)))

    # Dismissed and applied ones aren't recommendations any more. Drop them before ranking
    # so `total` and the pages only count what's shown. Saved ones stay, flagged.
    actions = await current_actions(db, user.id, [o.id for o in opportunities])
    opportunities = [
        o for o in opportunities if o.id not in actions or actions[o.id].action == SAVED
    ]

    # Ranked and paginated in memory: fine at tens or hundreds of opportunities. Revisit
    # (store scores in opportunity_matches) once that stops being true.
    matches = build_feed(facts, opportunities, today)
    return FeedList(
        items=[
            FeedItem(
                opportunity=OpportunityRead.model_validate(m.opportunity),
                score=m.score,
                explanation=m.explanation,
                user_action=SAVED if m.opportunity.id in actions else None,
            )
            for m in matches[offset : offset + limit]
        ],
        total=len(matches),
        limit=limit,
        offset=offset,
    )
