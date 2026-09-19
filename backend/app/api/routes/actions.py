import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.actions import current_actions, latest_actions, lock_actions
from app.api.deps import CurrentUser, DbSession
from app.api.routes.opportunities import MAX_PAGE_SIZE
from app.models import Opportunity, UserOpportunityAction
from app.models.base import APPLIED, REMOVED_STATUS, SAVED, UNSAVED
from app.schemas.action import ActionCreate, ActionList, ActionListItem, ActionState
from app.schemas.opportunity import OpportunityRead

router = APIRouter(tags=["actions"])


def _state(opportunity_id: uuid.UUID, row: UserOpportunityAction | None) -> ActionState:
    if row is None:
        return ActionState(
            opportunity_id=opportunity_id, action=None, dismiss_reason=None, actioned_at=None
        )
    return ActionState(
        opportunity_id=opportunity_id,
        action=row.action,
        dismiss_reason=row.dismiss_reason,
        actioned_at=row.created_at,
    )


@router.post("/opportunities/{opportunity_id}/actions", response_model=ActionState)
async def act_on_opportunity(
    opportunity_id: uuid.UUID, body: ActionCreate, user: CurrentUser, db: DbSession
) -> ActionState:
    opportunity = await db.get(Opportunity, opportunity_id)
    if opportunity is None or opportunity.status == REMOVED_STATUS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    await lock_actions(db, user.id, opportunity_id)
    current = (await current_actions(db, user.id, [opportunity_id])).get(opportunity_id)
    # A repeat (double-click, retry) changes nothing, so it isn't logged. Dismissing again
    # without a reason is a repeat too: it keeps the reason already given.
    if body.action == UNSAVED:
        unchanged = current is None
    else:
        unchanged = (
            current is not None
            and current.action == body.action
            and body.dismiss_reason in (None, current.dismiss_reason)
        )
    if unchanged:
        return _state(opportunity_id, current)

    row = UserOpportunityAction(
        user_id=user.id,
        opportunity_id=opportunity_id,
        action=body.action,
        dismiss_reason=body.dismiss_reason,
        # Not the column's now() default: now() is fixed per transaction, so two actions in
        # one transaction would tie and "latest wins" couldn't tell them apart.
        created_at=func.clock_timestamp(),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return _state(opportunity_id, None if body.action == UNSAVED else row)


async def _list_by_state(
    db: AsyncSession, user_id: uuid.UUID, action: str, limit: int, offset: int
) -> ActionList:
    latest = aliased(UserOpportunityAction, latest_actions(user_id).subquery())
    on = latest.opportunity_id == Opportunity.id
    # Expired ones stay: this is the user's own history, not recommendations.
    filters = (latest.action == action, Opportunity.status != REMOVED_STATUS)

    total = await db.scalar(
        select(func.count()).select_from(Opportunity).join(latest, on).where(*filters)
    )
    rows = await db.execute(
        select(Opportunity, latest.created_at)
        .join(latest, on)
        .where(*filters)
        # Newest first; id breaks ties so pages don't shuffle between requests.
        .order_by(latest.created_at.desc(), Opportunity.id)
        .limit(limit)
        .offset(offset)
    )
    return ActionList(
        items=[
            ActionListItem(opportunity=OpportunityRead.model_validate(opportunity), actioned_at=at)
            for opportunity, at in rows
        ],
        total=total or 0,
        limit=limit,
        offset=offset,
    )


@router.get("/saved", response_model=ActionList)
async def list_saved(
    user: CurrentUser,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ActionList:
    return await _list_by_state(db, user.id, SAVED, limit, offset)


@router.get("/applications", response_model=ActionList)
async def list_applications(
    user: CurrentUser,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ActionList:
    return await _list_by_state(db, user.id, APPLIED, limit, offset)
