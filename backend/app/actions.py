"""A user's current state per opportunity, from the append-only actions log."""

import uuid
from collections.abc import Collection

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserOpportunityAction
from app.models.base import UNSAVED


def latest_actions(user_id: uuid.UUID) -> Select[tuple[UserOpportunityAction]]:
    """Each opportunity's most recent action by this user, `unsaved` included.

    The one place the "latest row wins" rule lives; use it as a subquery to join on.
    """
    return (
        select(UserOpportunityAction)
        .where(UserOpportunityAction.user_id == user_id)
        .distinct(UserOpportunityAction.opportunity_id)
        .order_by(
            UserOpportunityAction.opportunity_id,
            UserOpportunityAction.created_at.desc(),
            UserOpportunityAction.id.desc(),
        )
    )


async def current_actions(
    db: AsyncSession,
    user_id: uuid.UUID,
    opportunity_ids: Collection[uuid.UUID] | None = None,
) -> dict[uuid.UUID, UserOpportunityAction]:
    """The user's current state per opportunity. Unsaved ones have no state, so they're left out."""
    query = latest_actions(user_id)
    if opportunity_ids is not None:
        query = query.where(UserOpportunityAction.opportunity_id.in_(opportunity_ids))
    rows = await db.scalars(query)
    return {row.opportunity_id: row for row in rows if row.action != UNSAVED}
