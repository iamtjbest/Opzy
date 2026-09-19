import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity, User, UserOpportunityAction

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
