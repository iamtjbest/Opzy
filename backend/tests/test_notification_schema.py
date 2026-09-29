from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MatchNotification, Opportunity, User

NOW = datetime(2026, 9, 18, 9, 0, tzinfo=UTC)


async def _user(db_session: AsyncSession, cadence: str = "daily") -> User:
    user = User(email=f"{cadence}@example.com", password_hash="x", notification_cadence=cadence)
    db_session.add(user)
    await db_session.flush()
    return user


async def test_off_is_a_valid_cadence(db_session: AsyncSession):
    user = await _user(db_session, "off")
    assert user.notification_cadence == "off"


async def test_unknown_cadence_is_rejected(db_session: AsyncSession):
    with pytest.raises(IntegrityError):
        await _user(db_session, "monthly")


async def test_an_opportunity_is_recorded_once_per_user(db_session: AsyncSession):
    user = await _user(db_session)
    opportunity = Opportunity(title="Untitled", category="job")
    db_session.add(opportunity)
    await db_session.flush()

    for _ in range(2):
        db_session.add(
            MatchNotification(
                user_id=user.id, opportunity_id=opportunity.id, score=80, sent_at=NOW
            )
        )
    with pytest.raises(IntegrityError):
        await db_session.flush()
