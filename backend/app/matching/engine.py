"""Deterministic matching v0: hard eligibility, then a simple relevance score.

Pure functions over in-memory objects, with no database access. The MVP spec says not to
lock weights until real usage data exists, so every number lives in `Weights`.
"""

import re
from dataclasses import dataclass
from datetime import date

from app.models import Opportunity
from app.models.base import ACTIVE_STATUS


@dataclass(frozen=True)
class UserFacts:
    """What matching knows about a user. None means unknown, which never blocks a match."""

    nationality: str | None
    education_level: str | None
    field_of_study: str | None
    skills: frozenset[str]  # lowercase, as the profile stores them
    interests: frozenset[str]


@dataclass(frozen=True)
class Weights:
    """Points for each relevance signal. They total 100, so a score reads as a percentage."""

    field: int = 40
    skills: int = 40
    interest: int = 20

    def __post_init__(self) -> None:
        if self.field < 0 or self.skills < 0 or self.interest < 0:
            raise ValueError("weights must not be negative")
        if self.field + self.skills + self.interest != 100:
            raise ValueError("weights must total 100")


DEFAULT_WEIGHTS = Weights()


@dataclass(frozen=True)
class Relevance:
    field_matched: bool
    matched_skills: tuple[str, ...]  # the opportunity's spelling, in its order
    category_wanted: bool
    score: int


def is_eligible(facts: UserFacts, opportunity: Opportunity, today: date) -> bool:
    """Hard constraints. Each blocks only when both sides are known and they conflict."""
    if opportunity.status != ACTIVE_STATUS:
        return False
    if opportunity.deadline is not None and opportunity.deadline < today:
        return False
    if (
        facts.nationality
        and opportunity.eligible_countries
        and facts.nationality not in opportunity.eligible_countries
    ):
        return False
    if (
        facts.education_level
        and opportunity.education_levels
        and facts.education_level not in opportunity.education_levels
    ):
        return False
    return True


def _words(text: str) -> str:
    # Padded with spaces, so `in` only matches whole words: " art " isn't in " martial arts ".
    return " " + " ".join(re.findall(r"[a-z0-9]+", text.lower())) + " "


def relevance(
    facts: UserFacts, opportunity: Opportunity, weights: Weights = DEFAULT_WEIGHTS
) -> Relevance:
    """Soft signals. One the opportunity doesn't list scores 0, not full marks."""
    field_matched = facts.field_of_study is not None and any(
        _words(wanted) in _words(facts.field_of_study) for wanted in opportunity.fields_of_study
    )
    matched_skills = tuple(s for s in opportunity.skills if s.lower() in facts.skills)
    category_wanted = opportunity.category in facts.interests

    score = weights.field * field_matched + weights.interest * category_wanted
    if opportunity.skills:
        score += weights.skills * len(matched_skills) / len(opportunity.skills)
    return Relevance(field_matched, matched_skills, category_wanted, round(score))
