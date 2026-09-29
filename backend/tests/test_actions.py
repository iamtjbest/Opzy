from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import current_actions
from app.models import Opportunity, User, UserOpportunityAction
from app.models.base import APPLIED, DISMISSED, SAVED, UNSAVED

pytestmark = pytest.mark.usefixtures("empty_opportunities")


async def _user(db_session: AsyncSession, email: str = "ada@example.com") -> User:
    user = User(email=email, password_hash="not-a-real-hash")
    db_session.add(user)
    await db_session.flush()
    return user


async def _opportunity(db_session: AsyncSession, **fields) -> Opportunity:
    opportunity = Opportunity(**{"title": "Untitled", "category": "job", **fields})
    db_session.add(opportunity)
    await db_session.flush()
    return opportunity


# The literals below are deliberate: these tests check the database constraint itself.
async def test_database_accepts_unsaved(db_session: AsyncSession):
    user = await _user(db_session)
    opportunity = await _opportunity(db_session)

    db_session.add(
        UserOpportunityAction(user_id=user.id, opportunity_id=opportunity.id, action="unsaved")
    )
    await db_session.flush()


async def test_database_rejects_unknown_actions(db_session: AsyncSession):
    user = await _user(db_session)
    opportunity = await _opportunity(db_session)

    with pytest.raises(IntegrityError):
        async with db_session.begin_nested():
            db_session.add(
                UserOpportunityAction(
                    user_id=user.id, opportunity_id=opportunity.id, action="liked"
                )
            )


T0 = datetime(2026, 9, 19, 9, 0, tzinfo=UTC)


async def _act(
    db_session: AsyncSession, user: User, opportunity: Opportunity, action: str,
    minute: int, reason: str | None = None,
) -> None:
    db_session.add(
        UserOpportunityAction(
            user_id=user.id, opportunity_id=opportunity.id, action=action,
            dismiss_reason=reason, created_at=T0 + timedelta(minutes=minute),
        )
    )
    await db_session.flush()


def _states(actions: dict) -> dict:
    return {opportunity_id: row.action for opportunity_id, row in actions.items()}


async def test_latest_action_wins(db_session: AsyncSession):
    user = await _user(db_session)
    a = await _opportunity(db_session, title="a")
    b = await _opportunity(db_session, title="b")
    await _act(db_session, user, a, SAVED, 0)
    await _act(db_session, user, a, APPLIED, 1)
    await _act(db_session, user, b, DISMISSED, 0, "not_eligible")
    await _act(db_session, user, b, SAVED, 2)

    actions = await current_actions(db_session, user.id)

    assert _states(actions) == {a.id: APPLIED, b.id: SAVED}


async def test_latest_is_by_time_not_insert_order(db_session: AsyncSession):
    user = await _user(db_session)
    a = await _opportunity(db_session)
    await _act(db_session, user, a, DISMISSED, 5, "other")
    await _act(db_session, user, a, SAVED, 1)

    actions = await current_actions(db_session, user.id)

    assert _states(actions) == {a.id: DISMISSED}
    assert actions[a.id].dismiss_reason == "other"


async def test_unsaved_leaves_no_state(db_session: AsyncSession):
    user = await _user(db_session)
    a = await _opportunity(db_session)
    await _act(db_session, user, a, SAVED, 0)
    await _act(db_session, user, a, UNSAVED, 1)

    assert await current_actions(db_session, user.id) == {}


async def test_can_limit_to_some_opportunities(db_session: AsyncSession):
    user = await _user(db_session)
    a = await _opportunity(db_session)
    b = await _opportunity(db_session)
    await _act(db_session, user, a, SAVED, 0)
    await _act(db_session, user, b, SAVED, 0)

    assert _states(await current_actions(db_session, user.id, [b.id])) == {b.id: SAVED}
    assert await current_actions(db_session, user.id, []) == {}


async def test_actions_are_per_user(db_session: AsyncSession):
    ada = await _user(db_session)
    bea = await _user(db_session, "bea@example.com")
    a = await _opportunity(db_session)
    await _act(db_session, ada, a, SAVED, 0)

    assert await current_actions(db_session, bea.id) == {}
