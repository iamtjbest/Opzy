import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity, UserOpportunityAction
from tests.test_profile import auth_headers

pytestmark = pytest.mark.usefixtures("empty_opportunities")


async def _add(db_session: AsyncSession, **fields) -> Opportunity:
    opportunity = Opportunity(**{"title": "Untitled", "category": "job", **fields})
    db_session.add(opportunity)
    await db_session.flush()
    return opportunity


async def _act(client: AsyncClient, headers: dict, opportunity: Opportunity, action: str, **extra):
    return await client.post(
        f"/opportunities/{opportunity.id}/actions",
        json={"action": action, **extra},
        headers=headers,
    )


async def _log(db_session: AsyncSession, opportunity: Opportunity) -> list[str]:
    rows = await db_session.scalars(
        select(UserOpportunityAction.action)
        .where(UserOpportunityAction.opportunity_id == opportunity.id)
        .order_by(UserOpportunityAction.created_at)
    )
    return list(rows)


async def test_action_routes_require_auth(client: AsyncClient):
    resp = await client.post(f"/opportunities/{uuid.uuid4()}/actions", json={"action": "saved"})
    assert resp.status_code == 401


async def test_save_returns_the_new_state(client: AsyncClient, db_session: AsyncSession):
    opportunity = await _add(db_session)
    headers = await auth_headers(client)

    resp = await _act(client, headers, opportunity, "saved")

    assert resp.status_code == 200
    body = resp.json()
    assert body["opportunity_id"] == str(opportunity.id)
    assert (body["action"], body["dismiss_reason"]) == ("saved", None)
    assert body["actioned_at"] is not None


async def test_every_change_is_logged_and_latest_wins(
    client: AsyncClient, db_session: AsyncSession
):
    opportunity = await _add(db_session)
    headers = await auth_headers(client)

    states = [
        (await _act(client, headers, opportunity, action)).json()["action"]
        for action in ["saved", "unsaved", "saved", "applied", "dismissed", "saved"]
    ]

    assert states == ["saved", None, "saved", "applied", "dismissed", "saved"]
    assert await _log(db_session, opportunity) == [
        "saved", "unsaved", "saved", "applied", "dismissed", "saved"
    ]


async def test_unsaved_clears_any_state(client: AsyncClient, db_session: AsyncSession):
    opportunity = await _add(db_session)
    headers = await auth_headers(client)
    await _act(client, headers, opportunity, "applied")

    resp = await _act(client, headers, opportunity, "unsaved")

    assert resp.json() == {
        "opportunity_id": str(opportunity.id),
        "action": None,
        "dismiss_reason": None,
        "actioned_at": None,
    }


async def test_repeating_the_current_state_writes_nothing(
    client: AsyncClient, db_session: AsyncSession
):
    opportunity = await _add(db_session)
    headers = await auth_headers(client)

    first = await _act(client, headers, opportunity, "saved")
    second = await _act(client, headers, opportunity, "saved")

    assert second.status_code == 200
    assert second.json() == first.json()
    assert await _log(db_session, opportunity) == ["saved"]


async def test_unsaving_with_no_state_writes_nothing(
    client: AsyncClient, db_session: AsyncSession
):
    opportunity = await _add(db_session)
    headers = await auth_headers(client)

    resp = await _act(client, headers, opportunity, "unsaved")

    assert resp.status_code == 200
    assert resp.json()["action"] is None
    assert await _log(db_session, opportunity) == []


async def test_dismiss_reason_is_optional_and_a_new_reason_is_recorded(
    client: AsyncClient, db_session: AsyncSession
):
    opportunity = await _add(db_session)
    headers = await auth_headers(client)

    plain = await _act(client, headers, opportunity, "dismissed")
    same = await _act(client, headers, opportunity, "dismissed")
    reasoned = await _act(client, headers, opportunity, "dismissed", dismiss_reason="not_eligible")

    assert plain.json()["dismiss_reason"] is None
    assert same.json() == plain.json()
    assert reasoned.json()["dismiss_reason"] == "not_eligible"
    assert await _log(db_session, opportunity) == ["dismissed", "dismissed"]


@pytest.mark.parametrize(
    "body",
    [
        {"action": "liked"},
        {"action": "dismissed", "dismiss_reason": "meh"},
        {"action": "saved", "dismiss_reason": "other"},
        {},
    ],
)
async def test_invalid_bodies_are_rejected(
    client: AsyncClient, db_session: AsyncSession, body: dict
):
    opportunity = await _add(db_session)
    headers = await auth_headers(client)

    resp = await client.post(f"/opportunities/{opportunity.id}/actions", json=body, headers=headers)

    assert resp.status_code == 422
    assert await _log(db_session, opportunity) == []


async def test_missing_or_removed_opportunity_is_404(
    client: AsyncClient, db_session: AsyncSession
):
    removed = await _add(db_session, status="removed")
    headers = await auth_headers(client)

    for opportunity_id in [uuid.uuid4(), removed.id]:
        resp = await client.post(
            f"/opportunities/{opportunity_id}/actions", json={"action": "saved"}, headers=headers
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Opportunity not found"


async def test_expired_opportunity_can_be_acted_on(
    client: AsyncClient, db_session: AsyncSession
):
    opportunity = await _add(db_session, status="expired")
    headers = await auth_headers(client)

    resp = await _act(client, headers, opportunity, "applied")

    assert resp.status_code == 200
    assert resp.json()["action"] == "applied"


def _titles(resp) -> list[str]:
    return [item["opportunity"]["title"] for item in resp.json()["items"]]


async def test_lists_require_auth(client: AsyncClient):
    assert (await client.get("/saved")).status_code == 401
    assert (await client.get("/applications")).status_code == 401


async def test_lists_hold_current_state_only(client: AsyncClient, db_session: AsyncSession):
    saved = await _add(db_session, title="saved")
    applied = await _add(db_session, title="saved then applied")
    dismissed = await _add(db_session, title="dismissed")
    unsaved = await _add(db_session, title="saved then unsaved")
    headers = await auth_headers(client)
    for opportunity, actions in [
        (saved, ["saved"]),
        (applied, ["saved", "applied"]),
        (dismissed, ["dismissed"]),
        (unsaved, ["saved", "unsaved"]),
    ]:
        for action in actions:
            assert (await _act(client, headers, opportunity, action)).status_code == 200

    saved_resp = await client.get("/saved", headers=headers)
    applied_resp = await client.get("/applications", headers=headers)

    assert _titles(saved_resp) == ["saved"]
    assert _titles(applied_resp) == ["saved then applied"]


async def test_list_items_carry_when_they_were_actioned(
    client: AsyncClient, db_session: AsyncSession
):
    opportunity = await _add(db_session)
    headers = await auth_headers(client)
    posted = await _act(client, headers, opportunity, "saved")

    [item] = (await client.get("/saved", headers=headers)).json()["items"]

    assert item["actioned_at"] == posted.json()["actioned_at"]
    assert item["opportunity"]["id"] == str(opportunity.id)


async def test_lists_are_newest_first_and_paginate(
    client: AsyncClient, db_session: AsyncSession
):
    headers = await auth_headers(client)
    for title in ["first", "second", "third"]:
        await _act(client, headers, await _add(db_session, title=title), "saved")

    page1 = await client.get("/saved", params={"limit": 2}, headers=headers)
    page2 = await client.get("/saved", params={"limit": 2, "offset": 2}, headers=headers)

    assert _titles(page1) == ["third", "second"]
    assert _titles(page2) == ["first"]
    assert (page1.json()["total"], page1.json()["limit"], page1.json()["offset"]) == (3, 2, 0)


async def test_lists_keep_expired_and_drop_removed(
    client: AsyncClient, db_session: AsyncSession
):
    expired = await _add(db_session, title="expired", status="expired")
    later_removed = await _add(db_session, title="later removed")
    headers = await auth_headers(client)
    await _act(client, headers, expired, "applied")
    await _act(client, headers, later_removed, "applied")
    later_removed.status = "removed"
    await db_session.flush()

    resp = await client.get("/applications", headers=headers)

    assert _titles(resp) == ["expired"]
    assert resp.json()["total"] == 1


async def test_lists_are_empty_before_any_action_or_profile(client: AsyncClient):
    headers = await auth_headers(client)

    resp = await client.get("/saved", headers=headers)

    assert resp.status_code == 200
    assert resp.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}


async def test_lists_are_per_user(client: AsyncClient, db_session: AsyncSession):
    opportunity = await _add(db_session)
    ada = await auth_headers(client)
    bea = await auth_headers(client, "bea@example.com")
    await _act(client, ada, opportunity, "saved")

    assert _titles(await client.get("/saved", headers=bea)) == []
    assert _titles(await client.get("/saved", headers=ada)) == ["Untitled"]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
async def test_list_pagination_bounds(client: AsyncClient, params: dict):
    headers = await auth_headers(client)

    assert (await client.get("/saved", params=params, headers=headers)).status_code == 422
