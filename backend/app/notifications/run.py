"""Finding each user's new strong matches and emailing the users who are due."""

import logging
import uuid
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.engine import Connection as SyncConnection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions import current_actions
from app.email import EmailError, EmailSender
from app.matching.feed import Match, build_feed
from app.models import MatchNotification, Opportunity, User
from app.models.base import ACTIVE_STATUS, EMAIL_CHANNEL, OFF
from app.notifications.content import compose_match_email
from app.notifications.schedule import is_due
from app.user_facts import load_user_facts

logger = logging.getLogger(__name__)

# A match scoring at least this is worth an email: e.g. field of study plus category, or
# every listed skill plus category. Tune it with real usage, like the matching weights.
STRONG_MATCH_SCORE = 60

# One run at a time, so two overlapping runs can't email the same matches.
RUN_LOCK_KEY = "match_notifications:run"


@dataclass(frozen=True)
class Recipient:
    id: uuid.UUID
    email: str
    cadence: str
    created_at: datetime


@dataclass
class RunResult:
    emailed: int = 0  # users emailed
    refused: int = 0  # users whose email was refused before sending; retried next run
    errored: int = 0  # users hit a database error; if it happened after sending, they
    # may be emailed again next run instead of being retried cleanly
    locked: bool = False  # another run was going, so this one did nothing

    @property
    def failed(self) -> int:
        """Total users not cleanly handled, for a quick pass/fail check."""
        return self.refused + self.errored


async def new_strong_matches(db: AsyncSession, user: Recipient, today: date) -> list[Match]:
    """Strong matches the user hasn't been emailed about or acted on, best first.

    Only opportunities added since they signed up: older ones were already in their feed.
    """
    facts = await load_user_facts(db, user.id)
    if facts is None:
        return []
    already_sent = select(MatchNotification.opportunity_id).where(
        MatchNotification.user_id == user.id
    )
    opportunities = list(
        await db.scalars(
            select(Opportunity).where(
                Opportunity.status == ACTIVE_STATUS,
                or_(Opportunity.deadline >= today, Opportunity.deadline.is_(None)),
                Opportunity.created_at >= user.created_at,
                Opportunity.id.not_in(already_sent),
            )
        )
    )
    # Saved, dismissed or applied: they've already seen it.
    acted_on = await current_actions(db, user.id, [o.id for o in opportunities])
    unseen = [o for o in opportunities if o.id not in acted_on]
    return [m for m in build_feed(facts, unseen, today) if m.score >= STRONG_MATCH_SCORE]


async def _recipients(db: AsyncSession) -> list[Recipient]:
    rows = await db.execute(
        select(User.id, User.email, User.notification_cadence, User.created_at)
        .where(
            User.notification_cadence != OFF,
            User.notification_channel == EMAIL_CHANNEL,
            # Nobody is emailed until they've proved the address is theirs. Signing up with
            # someone else's address otherwise turns Opzy into a way to mail them.
            User.email_verified_at.is_not(None),
        )
        .order_by(User.created_at, User.id)
    )
    return [Recipient(*row) for row in rows]


@dataclass
class _Attempt:
    """Tracks, for one user's notify attempt, whether the email already went out."""

    sent: bool = False


async def _notify(
    db: AsyncSession,
    sender: EmailSender,
    user: Recipient,
    now: datetime,
    today: date,
    frontend_url: str,
    attempt: _Attempt,
) -> bool:
    """Email the user their new strong matches if they're due. True if an email went out."""
    last_sent = await db.scalar(
        select(func.max(MatchNotification.sent_at)).where(MatchNotification.user_id == user.id)
    )
    if not is_due(user.cadence, last_sent, now):
        return False
    matches = await new_strong_matches(db, user, today)
    if not matches:
        return False

    # Recorded and flushed before sending, so a duplicate fails here and not after the email
    # has gone. Committed only after sending, so a refused email leaves them unrecorded.
    db.add_all(
        MatchNotification(
            user_id=user.id, opportunity_id=m.opportunity.id, score=m.score, sent_at=now
        )
        for m in matches
    )
    await db.flush()
    await sender.send(compose_match_email(user.email, matches, user.cadence, frontend_url))
    attempt.sent = True
    await db.commit()
    return True


async def run_notifications(
    db: AsyncSession, sender: EmailSender, now: datetime, today: date, frontend_url: str
) -> RunResult:
    """Email every due user their new strong matches. Safe to run as often as you like.

    `db` must be bound to one connection: the run lock is held by the connection, across
    the run's many transactions.
    """
    if not isinstance(db.get_bind(), SyncConnection):
        raise RuntimeError(
            "run_notifications requires a session bound to a single connection (not an "
            "engine): the advisory lock is held by the connection, and the run commits "
            "once per emailed user, so a pooled/engine-bound session would let the lock "
            "protect nothing and could leak it permanently."
        )

    result = RunResult()
    key = func.hashtextextended(RUN_LOCK_KEY, 0)
    if not await db.scalar(select(func.pg_try_advisory_lock(key))):
        result.locked = True
        return result
    try:
        for user in await _recipients(db):
            attempt = _Attempt()
            try:
                if await _notify(db, sender, user, now, today, frontend_url, attempt):
                    result.emailed += 1
            except EmailError:
                await db.rollback()
                result.refused += 1
                logger.exception("Couldn't email user %s; retrying next run", user.id)
            except SQLAlchemyError:
                await db.rollback()
                result.errored += 1
                if attempt.sent:
                    logger.exception(
                        "Emailed user %s but a database error followed; they may be "
                        "emailed again next run",
                        user.id,
                    )
                else:
                    logger.exception(
                        "Database error notifying user %s; retrying next run", user.id
                    )
    except BaseException:
        # Leaves the connection usable for the unlock below.
        await db.rollback()
        raise
    finally:
        # A failure releasing the lock or committing here must never replace an
        # exception already propagating from the loop above - just log it.
        try:
            unlocked = await db.scalar(select(func.pg_advisory_unlock(key)))
        except Exception:
            logger.exception(
                "Couldn't release run lock %r; it may still be held", RUN_LOCK_KEY
            )
        else:
            if not unlocked:
                logger.error(
                    "pg_advisory_unlock did not release lock %r; it may still be held",
                    RUN_LOCK_KEY,
                )
        try:
            await db.commit()
        except Exception:
            logger.exception("Couldn't commit after the notification run")
    return result
