"""Pure matching logic: no database, so Opportunity objects are built in memory."""

from dataclasses import replace
from datetime import date

import pytest

from app.matching.engine import UserFacts, Relevance, Weights, is_eligible, relevance
from app.models import Opportunity

TODAY = date(2026, 9, 18)

FACTS = UserFacts(
    nationality="NG",
    education_level="undergraduate",
    field_of_study="Computer Engineering",
    skills=frozenset({"python", "figma"}),
    interests=frozenset({"job", "internship"}),
)

UNKNOWN = UserFacts(
    nationality=None, education_level=None, field_of_study=None,
    skills=frozenset(), interests=frozenset(),
)


def _opp(**fields) -> Opportunity:
    # In-memory objects don't get server defaults, so set every field matching reads.
    return Opportunity(
        **{
            "title": "Untitled",
            "category": "grant",
            "status": "active",
            "deadline": None,
            "eligible_countries": [],
            "education_levels": [],
            "fields_of_study": [],
            "skills": [],
            **fields,
        }
    )


# --- hard eligibility ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fields", "eligible"),
    [
        ({}, True),
        ({"eligible_countries": ["GH", "NG"]}, True),
        ({"eligible_countries": ["GH"]}, False),
        ({"education_levels": ["undergraduate", "graduate"]}, True),
        ({"education_levels": ["postgraduate"]}, False),
        ({"deadline": TODAY}, True),  # open through its last day
        ({"deadline": date(2026, 9, 17)}, False),
        ({"status": "expired"}, False),
        ({"status": "removed"}, False),
    ],
)
def test_hard_eligibility(fields: dict, eligible: bool):
    assert is_eligible(FACTS, _opp(**fields), TODAY) is eligible


def test_unknown_profile_facts_never_block():
    opp = _opp(eligible_countries=["GH"], education_levels=["postgraduate"])

    assert is_eligible(UNKNOWN, opp, TODAY)


# --- relevance -------------------------------------------------------------------------


def test_every_signal_matching_scores_100():
    opp = _opp(category="job", fields_of_study=["Computer Engineering"], skills=["Python"])

    assert relevance(FACTS, opp) == Relevance(
        field_matched=True, matched_skills=("Python",), category_wanted=True, score=100
    )


def test_no_signals_scores_0():
    assert relevance(FACTS, _opp()) == Relevance(
        field_matched=False, matched_skills=(), category_wanted=False, score=0
    )


def test_skill_overlap_is_a_share_of_the_opportunitys_skills():
    rel = relevance(FACTS, _opp(skills=["PYTHON", "Go", "SQL"]))

    assert rel.matched_skills == ("PYTHON",)  # the opportunity's spelling
    assert rel.score == 13  # 40 × 1/3


@pytest.mark.parametrize(
    ("field", "wanted", "matched"),
    [
        ("Computer Engineering", "engineering", True),
        ("Computer Engineering", "Computer  Engineering", True),
        ("Electrical/Electronic Engineering", "electronic engineering", True),
        ("Computer Engineering", "Computer Science", False),
        ("Martial Arts Studies", "art", False),  # whole words only
        (None, "Engineering", False),
    ],
)
def test_field_match_is_whole_words_ignoring_case(field, wanted, matched):
    facts = replace(FACTS, field_of_study=field)

    assert relevance(facts, _opp(fields_of_study=[wanted])).field_matched is matched


def test_weights_are_tunable():
    opp = _opp(category="job", skills=["Python", "Go"])

    assert relevance(FACTS, opp).score == 40  # 40 × 1/2 + 20
    assert relevance(FACTS, opp, Weights(field=0, skills=100, interest=0)).score == 50


def test_weights_must_total_100():
    with pytest.raises(ValueError, match="100"):
        Weights(field=50, skills=50, interest=50)
