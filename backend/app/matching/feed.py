from dataclasses import dataclass
from datetime import date

from app.matching.engine import DEFAULT_WEIGHTS, UserFacts, Weights, is_eligible, relevance
from app.matching.explain import explain
from app.models import Opportunity


@dataclass(frozen=True)
class Match:
    opportunity: Opportunity
    score: int
    explanation: str


def build_feed(
    facts: UserFacts,
    opportunities: list[Opportunity],
    today: date,
    weights: Weights = DEFAULT_WEIGHTS,
) -> list[Match]:
    """The eligible opportunities, best match first."""
    matches = []
    for opportunity in opportunities:
        if not is_eligible(facts, opportunity, today):
            continue
        rel = relevance(facts, opportunity, weights)
        matches.append(Match(opportunity, rel.score, explain(facts, opportunity, rel)))
    # Equal scores: the most urgent first (rolling deadlines last), then title, so the order
    # never depends on how the database returned the rows.
    matches.sort(
        key=lambda m: (
            -m.score,
            m.opportunity.deadline is None,
            m.opportunity.deadline or date.max,
            m.opportunity.title,
        )
    )
    return matches
