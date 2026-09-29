from datetime import UTC, date, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.db import build_engine_args
from app.email import EmailError, EmailMessage
from app.models import MatchNotification, Opportunity, User
from app.notifications.run import RUN_LOCK_KEY, RunResult, run_notifications
from tests.conftest import _test_database_url
from tests.test_profile import ONBOARDING, auth_headers

NOW = datetime(2026, 9, 18, 9, 0, tzinfo=UTC)
TODAY = date(2026, 9, 18)
FRONTEND = "http://app.test"
ADA, BOLA = "ada@example.com", "bola@example.com"

# Scores against ONBOARDING: field 40 + skills 40 + category 20.
STRONG = {"category": "job", "fields_of_study": ["Computer Engineering"], "skills": ["Python"]}
AT_THRESHOLD = {"category": "job", "fields_of_study": ["Computer Engineering"]}  # 60
BELOW = {"category": "grant", "fields_of_study": ["Computer Engineering"]}  # 40

pytestmark = pytest.mark.usefixtures("empty_opportunities")


@pytest.fixture(autouse=True)
async def quiet_seeded_users(db_session: AsyncSession) -> None:
    # The dev database has seeded users; turn theirs off (inside the rolled-back test
    # transaction) so only the users a test creates get emails.
    await db_session.execute(update(User).values(notification_cadence="off"))


class FakeSender:
    def __init__(self, refuse: tuple[str, ...] = ()) -> None:
        self.sent: list[EmailMessage] = []
        self.refuse = refuse

    async def send(self, message: EmailMessage) -> None:
        if message.to in self.refuse:
            raise EmailError("refused")
        self.sent.append(message)


async def _onboard(
    client: AsyncClient,
    db_session: AsyncSession,
    email: str = ADA,
    cadence: str = "instant",
) -> dict:
    headers = await auth_headers(client, email)
    assert (await client.put("/profile", json=ONBOARDING, headers=headers)).status_code == 200
    resp = await client.put("/settings/notifications", json={"cadence": cadence}, headers=headers)
    assert resp.status_code == 200
    # Verified, because an unverified account is never emailed (Sprint 9) and these tests
    # are about who gets email and when, not about verification.
    await db_session.execute(
        update(User).where(User.email == email).values(email_verified_at=NOW)
    )
    return headers


async def _add(db_session: AsyncSession, title: str, **fields) -> Opportunity:
    opportunity = Opportunity(title=title, **fields)
    db_session.add(opportunity)
    # Committed, not just flushed: the runner rolls back a failed user's savepoint, and that
    # must not take this row with it.
    await db_session.commit()
    return opportunity


async def _run(db_session: AsyncSession, sender: FakeSender, now: datetime = NOW) -> RunResult:
    return await run_notifications(db_session, sender, now, TODAY, FRONTEND)


async def _logged(db_session: AsyncSession, email: str) -> list[str]:
    rows = await db_session.scalars(
        select(Opportunity.title)
        .join(MatchNotification, MatchNotification.opportunity_id == Opportunity.id)
        .join(User, User.id == MatchNotification.user_id)
        .where(User.email == email)
        .order_by(Opportunity.title)
    )
    return list(rows)


async def test_new_strong_matches_are_emailed_and_recorded(
    client: AsyncClient, db_session: AsyncSession
):
    await _onboard(client, db_session)
    await _add(db_session, "Strong", **STRONG)
    await _add(db_session, "Weak", **BELOW)
    sender = FakeSender()

    result = await _run(db_session, sender)

    assert (result.emailed, result.refused, result.errored, result.locked) == (1, 0, 0, False)
    [email] = sender.sent
    assert (email.to, email.subject) == (ADA, "New match: Strong")
    assert "Weak" not in email.text
    assert await _logged(db_session, ADA) == ["Strong"]
    sent_at = await db_session.scalar(select(MatchNotification.sent_at))
    assert sent_at == NOW


async def test_the_threshold_is_inclusive(client: AsyncClient, db_session: AsyncSession):
    await _onboard(client, db_session)
    await _add(db_session, "At threshold", **AT_THRESHOLD)
    await _add(db_session, "Below", **BELOW)

    await _run(db_session, FakeSender())

    assert await _logged(db_session, ADA) == ["At threshold"]


async def test_a_match_is_emailed_once(client: AsyncClient, db_session: AsyncSession):
    await _onboard(client, db_session)
    await _add(db_session, "First", **STRONG)
    sender = FakeSender()

    await _run(db_session, sender)
    second = await _run(db_session, sender, NOW + timedelta(minutes=15))
    await _add(db_session, "Second", **STRONG)
    await _run(db_session, sender, NOW + timedelta(minutes=30))

    assert (second.emailed, second.locked) == (0, False)
    assert [e.subject for e in sender.sent] == ["New match: First", "New match: Second"]


async def test_opportunities_from_before_signup_are_skipped(
    client: AsyncClient, db_session: AsyncSession
):
    await _onboard(client, db_session)
    await _add(db_session, "Old", created_at=datetime(2020, 1, 1, tzinfo=UTC), **STRONG)
    sender = FakeSender()

    await _run(db_session, sender)

    assert sender.sent == []


@pytest.mark.parametrize("action", ["saved", "dismissed", "applied"])
async def test_matches_the_user_acted_on_are_skipped(
    client: AsyncClient, db_session: AsyncSession, action: str
):
    headers = await _onboard(client, db_session)
    opportunity = await _add(db_session, "Seen", **STRONG)
    resp = await client.post(
        f"/opportunities/{opportunity.id}/actions", json={"action": action}, headers=headers
    )
    assert resp.status_code == 200
    sender = FakeSender()

    await _run(db_session, sender)

    assert sender.sent == []


async def test_expired_and_past_deadline_are_skipped(
    client: AsyncClient, db_session: AsyncSession
):
    await _onboard(client, db_session)
    await _add(db_session, "Expired", status="expired", **STRONG)
    await _add(db_session, "Closed", deadline=TODAY - timedelta(days=1), **STRONG)
    await _add(db_session, "Closes today", deadline=TODAY, **STRONG)

    await _run(db_session, FakeSender())

    assert await _logged(db_session, ADA) == ["Closes today"]


async def test_users_without_a_profile_are_skipped(client: AsyncClient, db_session: AsyncSession):
    headers = await auth_headers(client, ADA)
    await client.put("/settings/notifications", json={"cadence": "instant"}, headers=headers)
    await _add(db_session, "Strong", **STRONG)
    sender = FakeSender()

    await _run(db_session, sender)

    assert sender.sent == []


async def test_unverified_users_are_never_emailed(
    client: AsyncClient, db_session: AsyncSession
):
    """Nobody is mailed until they've proved the address is theirs (Sprint 9)."""
    await _onboard(client, db_session)
    await db_session.execute(
        update(User).where(User.email == ADA).values(email_verified_at=None)
    )
    await _add(db_session, "Strong", **STRONG)
    sender = FakeSender()

    result = await _run(db_session, sender)

    assert sender.sent == []
    assert result.emailed == 0


async def test_verifying_lets_the_emails_through(
    client: AsyncClient, db_session: AsyncSession
):
    await _onboard(client, db_session)
    await db_session.execute(
        update(User).where(User.email == ADA).values(email_verified_at=None)
    )
    await _add(db_session, "Strong", **STRONG)
    sender = FakeSender()
    await _run(db_session, sender)

    await db_session.execute(
        update(User).where(User.email == ADA).values(email_verified_at=NOW)
    )
    await _run(db_session, sender, NOW + timedelta(minutes=15))

    assert [e.subject for e in sender.sent] == ["New match: Strong"]


async def test_off_users_are_never_emailed(client: AsyncClient, db_session: AsyncSession):
    await _onboard(client, db_session, cadence="off")
    await _add(db_session, "Strong", **STRONG)
    sender = FakeSender()

    await _run(db_session, sender)

    assert sender.sent == []


@pytest.mark.parametrize(
    ("cadence", "period"), [("daily", timedelta(days=1)), ("weekly", timedelta(days=7))]
)
async def test_digests_batch_matches_once_per_period(
    client: AsyncClient, db_session: AsyncSession, cadence: str, period: timedelta
):
    await _onboard(client, db_session, cadence=cadence)
    await _add(db_session, "A", **STRONG)
    await _add(db_session, "B", **STRONG)
    sender = FakeSender()

    await _run(db_session, sender)
    await _add(db_session, "C", **STRONG)
    await _run(db_session, sender, NOW + period / 2)
    await _run(db_session, sender, NOW + period)

    assert [e.subject for e in sender.sent] == [
        "2 new opportunities picked for you",
        "New match: C",
    ]


async def test_a_refused_email_is_retried_next_run(client: AsyncClient, db_session: AsyncSession):
    await _onboard(client, db_session, ADA)
    await _onboard(client, db_session, BOLA)
    await _add(db_session, "Strong", **STRONG)

    result = await _run(db_session, FakeSender(refuse=(ADA,)))

    assert (result.emailed, result.refused, result.errored) == (1, 1, 0)
    assert await _logged(db_session, ADA) == []
    assert await _logged(db_session, BOLA) == ["Strong"]

    retry = FakeSender()
    await _run(db_session, retry, NOW + timedelta(minutes=15))

    assert [e.to for e in retry.sent] == [ADA]


async def test_a_session_bound_to_an_engine_is_refused(client: AsyncClient) -> None:
    # The run lock belongs to a connection, not a session, so a session bound to a
    # pooled engine (as the app's normal SessionLocal is) would let the lock protect
    # nothing. run_notifications must refuse rather than run unprotected.
    url, connect_args, engine_kwargs = build_engine_args(_test_database_url())
    engine = create_async_engine(url, poolclass=NullPool, connect_args=connect_args, **engine_kwargs)
    session = AsyncSession(bind=engine, expire_on_commit=False)
    sender = FakeSender()
    try:
        with pytest.raises(RuntimeError, match="single connection"):
            await run_notifications(session, sender, NOW, TODAY, FRONTEND)
    finally:
        await session.close()
        await engine.dispose()

    assert sender.sent == []


async def test_a_database_error_for_one_user_does_not_stop_the_run(
    client: AsyncClient, db_session: AsyncSession
):
    await _onboard(client, db_session, ADA)
    await _onboard(client, db_session, BOLA)
    opportunity = await _add(db_session, "Strong", **STRONG)
    ada_id = await db_session.scalar(select(User.id).where(User.email == ADA))
    # _recipients() orders by (created_at, id); onboarding both in the same instant
    # leaves their order to a coin-flip on id, so pin Ada's created_at earlier to make
    # sure she is processed - and fails - before Bola.
    await db_session.execute(
        update(User).where(User.id == ada_id).values(created_at=NOW - timedelta(days=1))
    )
    sender = FakeSender()

    # Stage a conflicting match_notifications row for Ada without flushing it, so the
    # run's own exclusion query still offers her the opportunity as unseen (mirroring a
    # concurrent run that recorded the same match in the gap between that query and
    # this one's flush). The run's own flush then inserts both rows at once and the
    # real unique index on (user_id, opportunity_id) rejects the duplicate.
    db_session.autoflush = False
    db_session.add(
        MatchNotification(user_id=ada_id, opportunity_id=opportunity.id, score=100, sent_at=NOW)
    )

    result = await _run(db_session, sender)

    assert (result.emailed, result.refused, result.errored) == (1, 0, 1)
    assert await _logged(db_session, ADA) == []
    assert await _logged(db_session, BOLA) == ["Strong"]
    assert [e.to for e in sender.sent] == [BOLA]


async def test_a_commit_failure_after_sending_counts_as_already_sent(
    client: AsyncClient, db_session: AsyncSession
):
    # A commit failing only after the real send has happened (e.g. a dropped connection)
    # is impractical to provoke honestly here, so this patches AsyncSession.commit to
    # fail exactly once, right when _notify calls it post-send. Everything else in the
    # run - the query, the insert, the flush, the send itself - happens for real.
    await _onboard(client, db_session)
    await _add(db_session, "Strong", **STRONG)
    sender = FakeSender()

    real_commit = db_session.commit
    calls = 0

    async def flaky_commit() -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise SQLAlchemyError("connection reset")
        await real_commit()

    db_session.commit = flaky_commit

    result = await _run(db_session, sender)

    assert (result.emailed, result.refused, result.errored) == (0, 0, 1)
    # The email went out even though the commit that would have recorded it failed, so
    # it's unrecorded and the run may email this user again next time.
    assert [e.to for e in sender.sent] == [ADA]
    assert await _logged(db_session, ADA) == []


async def test_a_run_does_nothing_while_another_is_going(
    client: AsyncClient, db_session: AsyncSession
):
    await _onboard(client, db_session)
    await _add(db_session, "Strong", **STRONG)
    url, connect_args, engine_kwargs = build_engine_args(_test_database_url())
    engine = create_async_engine(url, poolclass=NullPool, connect_args=connect_args, **engine_kwargs)
    key = func.hashtextextended(RUN_LOCK_KEY, 0)
    sender = FakeSender()
    try:
        async with engine.connect() as other:
            await other.scalar(select(func.pg_advisory_lock(key)))
            result = await _run(db_session, sender)
            await other.scalar(select(func.pg_advisory_unlock(key)))
    finally:
        await engine.dispose()

    assert result.locked
    assert sender.sent == []
