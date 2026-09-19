import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func

from app.actions import current_actions
from app.api.deps import CurrentUser, DbSession
from app.models import Opportunity, UserOpportunityAction
from app.models.base import REMOVED_STATUS, UNSAVED
from app.schemas.action import ActionCreate, ActionState

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

    current = (await current_actions(db, user.id, [opportunity_id])).get(opportunity_id)
    # A repeat (double-click, retry) changes nothing, so it isn't logged.
    if body.action == UNSAVED:
        unchanged = current is None
    else:
        unchanged = current is not None and (current.action, current.dismiss_reason) == (
            body.action,
            body.dismiss_reason,
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
