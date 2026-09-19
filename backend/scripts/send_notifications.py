"""Email users their new strong matches, at the cadence each chose.

Run from the backend/ directory, on a schedule. Every 15 minutes is enough for "instant":

    python -m scripts.send_notifications

Safe to re-run and to overlap: each match is emailed once, and a run that finds another
one going does nothing. With EMAIL_BACKEND=console (the default) emails are only logged.
"""

import asyncio
import logging
import sys
from datetime import UTC, datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.feed import get_today
from app.core.config import get_settings
from app.email import EMAIL_TIMEOUT_SECONDS, get_email_sender
from app.notifications.run import RunResult, run_notifications


async def _run() -> RunResult:
    from app.core.db import engine

    settings = get_settings()
    try:
        async with (
            httpx.AsyncClient(timeout=EMAIL_TIMEOUT_SECONDS) as http,
            engine.connect() as conn,
            # One connection for the whole run: it holds the run lock.
            AsyncSession(bind=conn, expire_on_commit=False) as db,
        ):
            return await run_notifications(
                db,
                get_email_sender(settings, http),
                datetime.now(UTC),
                get_today(),
                settings.frontend_url,
            )
    finally:
        await engine.dispose()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    result = asyncio.run(_run())
    if result.locked:
        print("Another run is in progress; nothing done.")
        return
    print(f"Emailed {result.emailed} user(s); {result.failed} refused, retried next run.")
    if result.failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
