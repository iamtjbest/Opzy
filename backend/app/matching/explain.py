"""Plain-language reasons for a match.

Interview data showed a confident match with no reason reads as suspicious, so every match
gets one. A sentence only claims what was actually checked: an eligibility clause appears
only when the opportunity restricts that thing and the profile says the user meets it.
"""

from app.core.countries import country_name
from app.matching.engine import Relevance, UserFacts
from app.models import Opportunity

EDUCATION_PLURALS = {
    "secondary": "secondary school students",
    "undergraduate": "undergraduates",
    "graduate": "graduates",
    "postgraduate": "postgraduates",
}

NO_RELEVANCE = "though it doesn't match your field, skills or interests"


def _join(parts: list[str] | tuple[str, ...]) -> str:
    if len(parts) == 1:
        return parts[0]
    separator = ", and " if len(parts) > 2 else " and "
    return ", ".join(parts[:-1]) + separator + parts[-1]


def _eligibility(facts: UserFacts, opportunity: Opportunity) -> str | None:
    who = (
        EDUCATION_PLURALS[facts.education_level]
        if facts.education_level and opportunity.education_levels
        else None
    )
    where = (
        country_name(facts.nationality)
        if facts.nationality and opportunity.eligible_countries
        else None
    )
    if who and where:
        return f"it's open to {who} from {where}"
    if who:
        return f"it's open to {who}"
    if where:
        return f"it's open to applicants from {where}"
    return None


def explain(facts: UserFacts, opportunity: Opportunity, rel: Relevance) -> str:
    """Why this eligible opportunity is in the user's feed. Never empty."""
    reasons = []
    if rel.field_matched:
        reasons.append(f"you study {facts.field_of_study}")
    if rel.matched_skills:
        reasons.append(f"you know {_join(rel.matched_skills)}")
    if rel.category_wanted:
        # Every OPPORTUNITY_TYPES value pluralises with a plain "s".
        reasons.append(f"you're looking for {opportunity.category}s")
    eligibility = _eligibility(facts, opportunity)

    if reasons:
        sentence = f"Recommended because {_join(reasons)}."
        if eligibility:
            sentence += f" {eligibility[0].upper()}{eligibility[1:]}."
        return sentence
    if eligibility:
        return f"Shown because {eligibility}, {NO_RELEVANCE}."
    return f"Shown because nothing in its listed requirements rules you out, {NO_RELEVANCE}."
