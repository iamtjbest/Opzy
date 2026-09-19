from datetime import UTC, datetime, timedelta

import pytest

from app.notifications.schedule import is_due

NOW = datetime(2026, 9, 18, 9, 0, tzinfo=UTC)


@pytest.mark.parametrize("cadence", ["instant", "daily", "weekly"])
def test_never_emailed_is_due(cadence):
    assert is_due(cadence, None, NOW)


@pytest.mark.parametrize("last_sent", [None, NOW - timedelta(days=365)])
def test_off_is_never_due(last_sent):
    assert not is_due("off", last_sent, NOW)


def test_instant_is_always_due():
    assert is_due("instant", NOW - timedelta(minutes=1), NOW)


@pytest.mark.parametrize(
    ("cadence", "since_last", "due"),
    [
        ("daily", timedelta(hours=12), False),
        # The job runs every few minutes, so a digest is allowed an hour early; otherwise
        # it would slip by one run interval every period.
        ("daily", timedelta(hours=23, minutes=30), True),
        ("daily", timedelta(days=1), True),
        ("weekly", timedelta(days=6), False),
        ("weekly", timedelta(days=7) - timedelta(minutes=30), True),
        ("weekly", timedelta(days=8), True),
    ],
)
def test_digests_wait_for_their_period(cadence, since_last, due):
    assert is_due(cadence, NOW - since_last, NOW) is due
