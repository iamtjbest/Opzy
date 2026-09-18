import uuid
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity
from tests.test_profile import auth_headers


async def _add(db_session: AsyncSession, **fields) -> Opportunity:
    opportunity = Opportunity(**{"title": "Untitled", "category": "job", **fields})
    db_session.add(opportunity)
    await db_session.flush()
    return opportunity


def _titles(resp) -> list[str]:
    return [item["title"] for item in resp.json()["items"]]


pytestmark = pytest.mark.usefixtures("empty_opportunities")


# --- auth ------------------------------------------------------------------------------


async def test_opportunity_routes_require_auth(client: AsyncClient):
    assert (await client.get("/opportunities")).status_code == 401
    assert (await client.get(f"/opportunities/{uuid.uuid4()}")).status_code == 401


# --- list ------------------------------------------------------------------------------


async def test_list_returns_every_field(client: AsyncClient, db_session: AsyncSession):
    opportunity = await _add(
        db_session,
        title="Chevening Scholarship",
        organization="UK FCDO",
        category="scholarship",
        geography="Nigeria (study in UK)",
        description="Funds a UK master's.",
        deadline=date(2026, 10, 6),
        eligibility_notes="Nigerian nationals",
        application_url="https://example.com/apply",
        source_url="https://example.com/source",
        quality_rating=5,
        verified=True,
    )
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["limit"] == 20
    assert body["offset"] == 0
    item = body["items"][0]
    assert item["id"] == str(opportunity.id)
    assert item["title"] == "Chevening Scholarship"
    assert item["organization"] == "UK FCDO"
    assert item["category"] == "scholarship"
    assert item["geography"] == "Nigeria (study in UK)"
    assert item["description"] == "Funds a UK master's."
    assert item["deadline"] == "2026-10-06"
    assert item["eligibility_notes"] == "Nigerian nationals"
    assert item["application_url"] == "https://example.com/apply"
    assert item["source_url"] == "https://example.com/source"
    assert item["quality_rating"] == 5
    assert item["verified"] is True
    assert item["status"] == "active"
    assert item["created_at"] and item["updated_at"]


async def test_list_is_empty_when_nothing_matches(client: AsyncClient):
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", headers=headers)

    assert resp.status_code == 200
    assert resp.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}


async def test_list_orders_by_soonest_deadline_with_rolling_last(
    client: AsyncClient, db_session: AsyncSession
):
    await _add(db_session, title="rolling", deadline=None)
    await _add(db_session, title="later", deadline=date(2026, 12, 1))
    await _add(db_session, title="sooner", deadline=date(2026, 10, 1))
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", headers=headers)

    assert _titles(resp) == ["sooner", "later", "rolling"]


async def test_list_defaults_to_active_only(client: AsyncClient, db_session: AsyncSession):
    await _add(db_session, title="active")
    await _add(db_session, title="expired", status="expired")
    await _add(db_session, title="removed", status="removed")
    headers = await auth_headers(client)

    default = await client.get("/opportunities", headers=headers)
    expired = await client.get("/opportunities", params={"status": "expired"}, headers=headers)

    assert _titles(default) == ["active"]
    assert _titles(expired) == ["expired"]


async def test_list_never_exposes_removed(client: AsyncClient, db_session: AsyncSession):
    await _add(db_session, title="removed", status="removed")
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", params={"status": "removed"}, headers=headers)

    assert resp.status_code == 422


async def test_filter_by_one_or_more_categories(client: AsyncClient, db_session: AsyncSession):
    await _add(db_session, title="a job", category="job")
    await _add(db_session, title="a grant", category="grant")
    await _add(db_session, title="a hackathon", category="hackathon")
    headers = await auth_headers(client)

    one = await client.get("/opportunities", params={"category": "grant"}, headers=headers)
    two = await client.get(
        "/opportunities", params=[("category", "job"), ("category", "hackathon")], headers=headers
    )

    assert _titles(one) == ["a grant"]
    assert sorted(_titles(two)) == ["a hackathon", "a job"]
    assert two.json()["total"] == 2


async def test_unknown_category_is_rejected(client: AsyncClient):
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", params={"category": "Jobs"}, headers=headers)

    assert resp.status_code == 422


async def test_filter_by_geography_is_case_insensitive_substring(
    client: AsyncClient, db_session: AsyncSession
):
    await _add(db_session, title="lagos", geography="Lagos (in-person, University of Lagos)")
    await _add(db_session, title="abuja", geography="Abuja")
    await _add(db_session, title="unknown", geography=None)
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", params={"geography": "  LAGOS "}, headers=headers)

    assert _titles(resp) == ["lagos"]


async def test_geography_wildcards_are_matched_literally(
    client: AsyncClient, db_session: AsyncSession
):
    await _add(db_session, title="plain", geography="Lagos")
    await _add(db_session, title="percent", geography="100% remote")
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", params={"geography": "%"}, headers=headers)

    assert _titles(resp) == ["percent"]


async def test_blank_geography_is_ignored(client: AsyncClient, db_session: AsyncSession):
    await _add(db_session, title="somewhere", geography="Lagos")
    await _add(db_session, title="nowhere", geography=None)
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", params={"geography": "   "}, headers=headers)

    assert resp.json()["total"] == 2


async def test_deadline_after_is_inclusive_and_keeps_rolling_by_default(
    client: AsyncClient, db_session: AsyncSession
):
    await _add(db_session, title="past", deadline=date(2026, 9, 17))
    await _add(db_session, title="today", deadline=date(2026, 9, 18))
    await _add(db_session, title="future", deadline=date(2026, 10, 1))
    await _add(db_session, title="rolling", deadline=None)
    headers = await auth_headers(client)

    resp = await client.get(
        "/opportunities", params={"deadline_after": "2026-09-18"}, headers=headers
    )

    assert _titles(resp) == ["today", "future", "rolling"]


async def test_include_rolling_false_drops_null_deadlines(
    client: AsyncClient, db_session: AsyncSession
):
    await _add(db_session, title="dated", deadline=date(2026, 10, 1))
    await _add(db_session, title="rolling", deadline=None)
    headers = await auth_headers(client)

    plain = await client.get(
        "/opportunities", params={"include_rolling": "false"}, headers=headers
    )
    with_date = await client.get(
        "/opportunities",
        params={"include_rolling": "false", "deadline_after": "2026-09-18"},
        headers=headers,
    )

    assert _titles(plain) == ["dated"]
    assert _titles(with_date) == ["dated"]


async def test_filters_combine(client: AsyncClient, db_session: AsyncSession):
    await _add(db_session, title="match", category="grant", geography="Lagos",
               deadline=date(2026, 10, 1))
    await _add(db_session, title="wrong category", category="job", geography="Lagos",
               deadline=date(2026, 10, 1))
    await _add(db_session, title="wrong place", category="grant", geography="Abuja",
               deadline=date(2026, 10, 1))
    await _add(db_session, title="too early", category="grant", geography="Lagos",
               deadline=date(2026, 9, 1))
    headers = await auth_headers(client)

    resp = await client.get(
        "/opportunities",
        params={"category": "grant", "geography": "lagos", "deadline_after": "2026-09-18"},
        headers=headers,
    )

    assert _titles(resp) == ["match"]


async def test_pagination(client: AsyncClient, db_session: AsyncSession):
    for day in range(1, 6):
        await _add(db_session, title=f"day {day}", deadline=date(2026, 10, day))
    headers = await auth_headers(client)

    page = await client.get("/opportunities", params={"limit": 2, "offset": 2}, headers=headers)

    body = page.json()
    assert _titles(page) == ["day 3", "day 4"]
    assert body["total"] == 5
    assert body["limit"] == 2
    assert body["offset"] == 2


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
async def test_pagination_bounds(client: AsyncClient, params: dict):
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", params=params, headers=headers)

    assert resp.status_code == 422


async def test_structured_eligibility_defaults_to_empty_lists(
    client: AsyncClient, db_session: AsyncSession
):
    await _add(db_session, title="plain")
    await _add(
        db_session,
        title="structured",
        eligible_countries=["NG"],
        education_levels=["undergraduate"],
        fields_of_study=["Computer Science"],
        skills=["Python"],
    )
    headers = await auth_headers(client)

    resp = await client.get("/opportunities", headers=headers)

    by_title = {item["title"]: item for item in resp.json()["items"]}
    assert {k: by_title["plain"][k] for k in ("eligible_countries", "education_levels", "fields_of_study", "skills")} == {
        "eligible_countries": [],
        "education_levels": [],
        "fields_of_study": [],
        "skills": [],
    }
    assert by_title["structured"]["eligible_countries"] == ["NG"]
    assert by_title["structured"]["education_levels"] == ["undergraduate"]
    assert by_title["structured"]["fields_of_study"] == ["Computer Science"]
    assert by_title["structured"]["skills"] == ["Python"]


# --- detail ----------------------------------------------------------------------------


async def test_detail_returns_the_opportunity(client: AsyncClient, db_session: AsyncSession):
    opportunity = await _add(db_session, title="EBID Young Professional Programme",
                             category="fellowship")
    headers = await auth_headers(client)

    resp = await client.get(f"/opportunities/{opportunity.id}", headers=headers)

    assert resp.status_code == 200
    assert resp.json()["id"] == str(opportunity.id)
    assert resp.json()["title"] == "EBID Young Professional Programme"
    assert resp.json()["category"] == "fellowship"


async def test_detail_still_shows_expired(client: AsyncClient, db_session: AsyncSession):
    opportunity = await _add(db_session, title="closed", status="expired")
    headers = await auth_headers(client)

    resp = await client.get(f"/opportunities/{opportunity.id}", headers=headers)

    assert resp.status_code == 200
    assert resp.json()["status"] == "expired"


async def test_detail_hides_removed(client: AsyncClient, db_session: AsyncSession):
    opportunity = await _add(db_session, title="withdrawn", status="removed")
    headers = await auth_headers(client)

    resp = await client.get(f"/opportunities/{opportunity.id}", headers=headers)

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Opportunity not found"


async def test_detail_unknown_id_is_404(client: AsyncClient):
    headers = await auth_headers(client)

    resp = await client.get(f"/opportunities/{uuid.uuid4()}", headers=headers)

    assert resp.status_code == 404


async def test_detail_malformed_id_is_422(client: AsyncClient):
    headers = await auth_headers(client)

    resp = await client.get("/opportunities/not-a-uuid", headers=headers)

    assert resp.status_code == 422
