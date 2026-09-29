import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select

from app.api.deps import DbSession, get_current_user
from app.models import Opportunity
from app.models.base import REMOVED_STATUS
from app.schemas.opportunity import ListableStatus, OpportunityList, OpportunityRead
from app.schemas.profile import OpportunityType

MAX_PAGE_SIZE = 100

router = APIRouter(
    prefix="/opportunities",
    tags=["opportunities"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=OpportunityList)
async def list_opportunities(
    db: DbSession,
    category: Annotated[list[OpportunityType] | None, Query()] = None,
    geography: Annotated[str | None, Query(max_length=100)] = None,
    status_: Annotated[ListableStatus, Query(alias="status")] = "active",
    deadline_after: Annotated[
        date | None, Query(description="Keep deadlines on or after this date.")
    ] = None,
    include_rolling: Annotated[
        bool, Query(description="Keep opportunities with no (or an unconfirmed) deadline.")
    ] = True,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> OpportunityList:
    filters = [Opportunity.status == status_]
    if category:
        filters.append(Opportunity.category.in_(category))
    if geography and geography.strip():
        # Geography is free text ("Lagos (in-person, …)", "ECOWAS region incl. Nigeria"),
        # so match a substring. autoescape makes % and _ in the query literal.
        filters.append(Opportunity.geography.icontains(geography.strip(), autoescape=True))
    if deadline_after is not None:
        dated = Opportunity.deadline >= deadline_after
        filters.append(or_(dated, Opportunity.deadline.is_(None)) if include_rolling else dated)
    elif not include_rolling:
        filters.append(Opportunity.deadline.is_not(None))

    total = await db.scalar(select(func.count()).select_from(Opportunity).where(*filters))
    rows = await db.scalars(
        select(Opportunity)
        .where(*filters)
        # Soonest deadline first; rolling ones after every dated one. id breaks ties so pages
        # don't shuffle between requests.
        .order_by(Opportunity.deadline.asc().nulls_last(), Opportunity.id)
        .limit(limit)
        .offset(offset)
    )
    return OpportunityList(
        items=[OpportunityRead.model_validate(row) for row in rows],
        total=total or 0,
        limit=limit,
        offset=offset,
    )


@router.get("/{opportunity_id}", response_model=OpportunityRead)
async def get_opportunity(opportunity_id: uuid.UUID, db: DbSession) -> OpportunityRead:
    opportunity = await db.get(Opportunity, opportunity_id)
    # Removed opportunities are gone as far as users are concerned; expired ones stay
    # viewable, e.g. from a user's saved list.
    if opportunity is None or opportunity.status == REMOVED_STATUS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return OpportunityRead.model_validate(opportunity)
