import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.base import OPPORTUNITY_STATUSES
from app.schemas.profile import OpportunityType

OpportunityStatus = Literal[OPPORTUNITY_STATUSES]  # type: ignore[valid-type]

# Statuses a client may list by. `removed` means pulled from the product, so it's never
# served, not even on request.
ListableStatus = Literal["active", "expired"]


class OpportunityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    organization: str | None
    category: OpportunityType
    geography: str | None
    description: str | None
    # Null means rolling or unconfirmed.
    deadline: date | None
    eligibility_notes: str | None
    application_url: str | None
    source_url: str | None
    quality_rating: int | None
    verified: bool
    status: OpportunityStatus
    created_at: datetime
    updated_at: datetime


class OpportunityList(BaseModel):
    items: list[OpportunityRead]
    # Rows matching the filters across all pages, so the client can paginate.
    total: int
    limit: int
    offset: int
