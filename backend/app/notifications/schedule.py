"""Whether a user is due an email, given their cadence and when they were last emailed."""

from datetime import datetime, timedelta

from app.models.base import DAILY, INSTANT, OFF, WEEKLY

# The shortest gap between two emails to one user. Instant has none: the next run sends.
CADENCE_PERIODS = {
    INSTANT: timedelta(0),
    DAILY: timedelta(days=1),
    WEEKLY: timedelta(days=7),
}
# Each run starts a little later than the previous send did. Without slack, a digest would
# slip by one run interval every period.
PERIOD_SLACK = timedelta(hours=1)


def is_due(cadence: str, last_sent: datetime | None, now: datetime) -> bool:
    if cadence == OFF:
        return False
    if last_sent is None:
        return True
    return now - last_sent >= CADENCE_PERIODS[cadence] - PERIOD_SLACK
