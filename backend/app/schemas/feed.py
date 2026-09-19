from typing import Literal

from pydantic import BaseModel

from app.models.base import SAVED
from app.schemas.opportunity import OpportunityRead


class FeedItem(BaseModel):
    opportunity: OpportunityRead
    # 0–100: how well it fits the profile. Every item already passed the hard eligibility checks.
    score: int
    # Why it's in the feed, in plain language. Never empty.
    explanation: str
    # "saved" if the user saved it. Dismissed and applied ones never reach the feed.
    user_action: Literal[SAVED] | None  # type: ignore[valid-type]


class FeedList(BaseModel):
    items: list[FeedItem]
    # Matches across all pages, so the client can paginate.
    total: int
    limit: int
    offset: int
