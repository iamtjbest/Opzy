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
