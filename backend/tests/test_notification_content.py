import uuid
from datetime import date

import pytest

from app.matching.feed import Match
from app.models import Opportunity
from app.notifications.content import MAX_ITEMS_PER_EMAIL, compose_match_email

FRONTEND = "http://app.test"


def _match(title: str = "Backend Intern", **fields) -> Match:
    opportunity = Opportunity(
        id=uuid.uuid4(), title=title, category="internship", **{"organization": "Acme", **fields}
    )
    return Match(opportunity, 80, "Fits your field of study.")


def test_one_match_names_it_in_the_subject():
    match = _match(deadline=date(2026, 9, 30))

    email = compose_match_email("ada@example.com", [match], "instant", FRONTEND)

    assert email.to == "ada@example.com"
    assert email.subject == "New match: Backend Intern"
    assert "Backend Intern — Acme" in email.text
    assert "Deadline: 30 Sep 2026" in email.text
    assert "Fits your field of study." in email.text
    assert f"http://app.test/opportunities/{match.opportunity.id}" in email.text
    assert f'href="http://app.test/opportunities/{match.opportunity.id}"' in email.html


def test_several_matches_are_counted_in_the_subject_and_listed_in_order():
    matches = [_match("First"), _match("Second")]

    email = compose_match_email("ada@example.com", matches, "weekly", FRONTEND)

    assert email.subject == "2 new opportunities picked for you"
    assert email.text.index("First") < email.text.index("Second")


def test_rolling_deadline_and_no_organization():
    email = compose_match_email(
        "ada@example.com", [_match(organization=None)], "instant", FRONTEND
    )

    assert "Rolling deadline" in email.text
    assert "—" not in email.text


def test_trailing_slash_on_the_frontend_url_is_ignored():
    match = _match()

    email = compose_match_email("ada@example.com", [match], "instant", "http://app.test/")

    assert f"http://app.test/opportunities/{match.opportunity.id}" in email.text


def test_html_is_escaped():
    email = compose_match_email("ada@example.com", [_match("R&D <Intern>")], "instant", FRONTEND)

    assert "R&amp;D &lt;Intern&gt;" in email.html
    assert "<Intern>" not in email.html
    assert "R&D <Intern>" in email.text


def test_long_lists_are_cut_short_with_a_link_to_the_feed():
    matches = [_match(f"Opportunity {i:02}") for i in range(MAX_ITEMS_PER_EMAIL + 2)]

    email = compose_match_email("ada@example.com", matches, "weekly", FRONTEND)

    assert email.subject == "12 new opportunities picked for you"
    assert email.text.count("/opportunities/") == MAX_ITEMS_PER_EMAIL
    assert "Opportunity 10" not in email.text
    assert "And 2 more on your feed: http://app.test/feed" in email.text


@pytest.mark.parametrize(
    ("cadence", "wording"),
    [
        ("instant", "as soon as we find a strong match"),
        ("daily", "at most once a day"),
        ("weekly", "at most once a week"),
    ],
)
def test_footer_says_how_often_and_where_to_change_it(cadence, wording):
    email = compose_match_email("ada@example.com", [_match()], cadence, FRONTEND)

    assert wording in email.text
    assert "turn them off: http://app.test/settings" in email.text
    assert "http://app.test/settings" in email.html
