from pydantic import BaseModel

from app.schemas.opportunity import OpportunityRead


class FeedItem(BaseModel):
    opportunity: OpportunityRead
    # 0–100: how well it fits the profile. Every item already passed the hard eligibility checks.
    score: int
    # Why it's in the feed, in plain language. Never empty.
    explanation: str


class FeedList(BaseModel):
    items: list[FeedItem]
    # Matches across all pages, so the client can paginate.
    total: int
    limit: int
    offset: int
