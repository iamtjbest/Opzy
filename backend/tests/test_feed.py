from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.feed import get_today
from app.main import app
from app.models import Opportunity
from scripts.seed_opportunities import DEFAULT_SHEET, parse_sheet, seed
from tests.test_profile import ONBOARDING, auth_headers

TODAY = date(2026, 9, 18)

pytestmark = pytest.mark.usefixtures("empty_opportunities")


@pytest.fixture(autouse=True)
def frozen_today(client: AsyncClient) -> None:
    # The client fixture clears every override on teardown.
    app.dependency_overrides[get_today] = lambda: TODAY


async def _add(db_session: AsyncSession, **fields) -> Opportunity:
    opportunity = Opportunity(**{"title": "Untitled", "category": "job", **fields})
    db_session.add(opportunity)
    await db_session.flush()
    return opportunity


async def _onboard(client: AsyncClient, **changes) -> dict[str, str]:
    headers = await auth_headers(client)
    resp = await client.put("/profile", json={**ONBOARDING, **changes}, headers=headers)
    assert resp.status_code == 200
    return headers


def _titles(resp) -> list[str]:
    return [item["opportunity"]["title"] for item in resp.json()["items"]]


async def test_feed_requires_auth(client: AsyncClient):
    assert (await client.get("/feed")).status_code == 401


async def test_feed_before_onboarding_is_404(client: AsyncClient):
    headers = await auth_headers(client)

    resp = await client.get("/feed", headers=headers)

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Profile not found"


async def test_feed_applies_hard_eligibility_filters(
    client: AsyncClient, db_session: AsyncSession
):
    await _add(db_session, title="open to all")
    await _add(db_session, title="nigerians", eligible_countries=["NG"])
    await _add(db_session, title="ghanaians", eligible_countries=["GH"])
    await _add(db_session, title="undergrads", education_levels=["undergraduate"])
    await _add(db_session, title="postgrads", education_levels=["postgraduate"])
    await _add(db_session, title="closes today", deadline=TODAY)
    await _add(db_session, title="closed yesterday", deadline=TODAY - timedelta(days=1))
    await _add(db_session, title="expired", status="expired")
    await _add(db_session, title="removed", status="removed")
    headers = await _onboard(client)

    resp = await client.get("/feed", headers=headers)

    assert resp.status_code == 200
    assert sorted(_titles(resp)) == ["closes today", "nigerians", "open to all", "undergrads"]


async def test_missing_profile_data_does_not_block(client: AsyncClient, db_session: AsyncSession):
    await _add(db_session, title="nigerian undergrads", eligible_countries=["NG"],
               education_levels=["undergraduate"])
    headers = await _onboard(client, nationality=None, education_level=None)

    resp = await client.get("/feed", headers=headers)

    [item] = resp.json()["items"]
    assert item["opportunity"]["title"] == "nigerian undergrads"
    assert item["explanation"] == "Recommended because you're looking for jobs."


async def test_feed_ranks_by_score_then_deadline(client: AsyncClient, db_session: AsyncSession):
    await _add(db_session, title="weak, soon", category="grant", deadline=date(2026, 9, 20))
    await _add(db_session, title="medium, later", deadline=date(2026, 12, 1))
    await _add(db_session, title="medium, sooner", deadline=date(2026, 10, 1))
    await _add(db_session, title="strong", category="internship", eligible_countries=["NG"],
               fields_of_study=["Computer Engineering"], skills=["Python"])
    headers = await _onboard(client)

    resp = await client.get("/feed", headers=headers)

    assert _titles(resp) == ["strong", "medium, sooner", "medium, later", "weak, soon"]
    items = resp.json()["items"]
    assert [item["score"] for item in items] == [100, 20, 20, 0]
    assert items[0]["explanation"] == (
        "Recommended because you study Computer Engineering, you know Python, and you're "
        "looking for internships. It's open to applicants from Nigeria."
    )


async def test_feed_filters_by_category_and_paginates(
    client: AsyncClient, db_session: AsyncSession
):
    for i in range(3):
        await _add(db_session, title=f"job {i}", deadline=date(2026, 10, 1 + i))
    await _add(db_session, title="grant", category="grant")
    headers = await _onboard(client)

    resp = await client.get(
        "/feed", params={"category": "job", "limit": 2, "offset": 1}, headers=headers
    )

    assert _titles(resp) == ["job 1", "job 2"]
    assert (resp.json()["total"], resp.json()["limit"], resp.json()["offset"]) == (3, 2, 1)


async def test_feed_on_the_seeded_sheet(client: AsyncClient, db_session: AsyncSession):
    # Sprint 4's exit criterion: the seeded profile against the seeded opportunities.
    # If the sheet's eligibility values change, update this list to match.
    await seed(db_session, parse_sheet(DEFAULT_SHEET))
    headers = await _onboard(client)

    resp = await client.get("/feed", params={"limit": 100}, headers=headers)

    items = resp.json()["items"]
    assert [(i["opportunity"]["title"], i["score"]) for i in items] == [
        ("Software Engineering Internship (Summer 2027)", 73),
        ("FinTech Build Weekend", 40),
        ("Product Design Intern", 33),
        ("Wetech x Nexascale AI Hackathon", 20),
        ("Civic Tech Fellowship", 20),
        ("Pan-African Pitch Competition", 20),
        ("Future Leaders Undergraduate Scholarship", 0),
        ("Early-Stage Founder Grant", 0),
        ("Creative Arts Micro-Grant", 0),
        ("National Essay Competition", 0),
    ]
    assert all(i["explanation"] for i in items)
    assert items[0]["explanation"] == (
        "Recommended because you study Computer Engineering, you know Python, and you're "
        "looking for internships. It's open to undergraduates."
    )
    assert items[6]["explanation"] == (
        "Shown because it's open to undergraduates from Nigeria, though it doesn't match your "
        "field, skills or interests."
    )


async def _act(client: AsyncClient, headers: dict, opportunity: Opportunity, action: str):
    resp = await client.post(
        f"/opportunities/{opportunity.id}/actions", json={"action": action}, headers=headers
    )
    assert resp.status_code == 200


async def test_feed_hides_dismissed_and_applied_and_flags_saved(
    client: AsyncClient, db_session: AsyncSession
):
    await _add(db_session, title="untouched")
    saved = await _add(db_session, title="saved")
    dismissed = await _add(db_session, title="dismissed")
    applied = await _add(db_session, title="applied")
    headers = await _onboard(client)
    await _act(client, headers, saved, "saved")
    await _act(client, headers, dismissed, "dismissed")
    await _act(client, headers, applied, "applied")

    resp = await client.get("/feed", headers=headers)

    body = resp.json()
    assert body["total"] == 2
    assert {i["opportunity"]["title"]: i["user_action"] for i in body["items"]} == {
        "untouched": None,
        "saved": "saved",
    }


async def test_feed_total_and_pages_count_only_shown_items(
    client: AsyncClient, db_session: AsyncSession
):
    first = await _add(db_session, title="a", deadline=date(2026, 10, 1))
    await _add(db_session, title="b", deadline=date(2026, 10, 2))
    await _add(db_session, title="c", deadline=date(2026, 10, 3))
    headers = await _onboard(client)
    await _act(client, headers, first, "dismissed")

    resp = await client.get("/feed", params={"limit": 1, "offset": 1}, headers=headers)

    assert _titles(resp) == ["c"]
    assert resp.json()["total"] == 2


async def test_undoing_a_dismiss_brings_it_back(client: AsyncClient, db_session: AsyncSession):
    opportunity = await _add(db_session, title="second thoughts")
    headers = await _onboard(client)
    await _act(client, headers, opportunity, "dismissed")
    await _act(client, headers, opportunity, "saved")

    resp = await client.get("/feed", headers=headers)

    assert [(i["opportunity"]["title"], i["user_action"]) for i in resp.json()["items"]] == [
        ("second thoughts", "saved")
    ]


async def test_another_users_actions_dont_touch_my_feed(
    client: AsyncClient, db_session: AsyncSession
):
    opportunity = await _add(db_session, title="shared")
    ada = await _onboard(client)
    bea = await auth_headers(client, "bea@example.com")
    assert (await client.put("/profile", json=ONBOARDING, headers=bea)).status_code == 200
    await _act(client, ada, opportunity, "dismissed")

    resp = await client.get("/feed", headers=bea)

    assert [(i["opportunity"]["title"], i["user_action"]) for i in resp.json()["items"]] == [
        ("shared", None)
    ]


async def test_category_filter_still_applies_alongside_actions(
    client: AsyncClient, db_session: AsyncSession
):
    await _add(db_session, title="job kept")
    dismissed_job = await _add(db_session, title="job dismissed")
    saved_grant = await _add(db_session, title="grant saved", category="grant")
    headers = await _onboard(client)
    await _act(client, headers, dismissed_job, "dismissed")
    await _act(client, headers, saved_grant, "saved")

    jobs = await client.get("/feed", params={"category": "job"}, headers=headers)
    grants = await client.get("/feed", params={"category": "grant"}, headers=headers)

    assert _titles(jobs) == ["job kept"]
    assert jobs.json()["total"] == 1
    assert [(i["opportunity"]["title"], i["user_action"]) for i in grants.json()["items"]] == [
        ("grant saved", "saved")
    ]
