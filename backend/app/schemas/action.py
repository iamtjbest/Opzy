import uuid
from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, model_validator

from app.models.base import APPLIED, DISMISS_REASONS, DISMISSED, SAVED, USER_ACTIONS
from app.schemas.opportunity import OpportunityRead

UserAction = Literal[USER_ACTIONS]  # type: ignore[valid-type]
# A state an opportunity can be left in. "unsaved" never is one: it clears the state.
CurrentAction = Literal[SAVED, DISMISSED, APPLIED]  # type: ignore[valid-type]
DismissReason = Literal[DISMISS_REASONS]  # type: ignore[valid-type]


class ActionCreate(BaseModel):
    action: UserAction
    dismiss_reason: DismissReason | None = None

    @model_validator(mode="after")
    def reason_only_when_dismissing(self) -> Self:
        if self.dismiss_reason is not None and self.action != DISMISSED:
            raise ValueError(f"dismiss_reason is only allowed when action is '{DISMISSED}'")
        return self


class ActionState(BaseModel):
    opportunity_id: uuid.UUID
    # All three are null when the user has no state for it: never acted on, or unsaved.
    action: CurrentAction | None
    dismiss_reason: DismissReason | None
    actioned_at: datetime | None


class ActionListItem(BaseModel):
    opportunity: OpportunityRead
    # When the user saved or applied to it.
    actioned_at: datetime


class ActionList(BaseModel):
    items: list[ActionListItem]
    # Items in this list across all pages, so the client can paginate.
    total: int
    limit: int
    offset: int
