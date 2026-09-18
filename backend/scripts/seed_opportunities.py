"""Load opportunities from the source tracking sheet.

The sheet (docs/OPZY_SOURCE_TRACKING.xlsx) is the source of truth for hand-entered
opportunities; its columns map 1:1 to the `opportunities` table.

Run from the backend/ directory:

    python -m scripts.seed_opportunities          # insert new rows into DATABASE_URL
    python -m scripts.seed_opportunities --sql    # regenerate docs/seed_opportunities_dev.sql

Both are safe to re-run: a row whose title and organization are already in the table is
skipped. Inserting refuses a non-local DATABASE_URL unless --allow-nonlocal is passed,
because the sheet currently holds fictional dev data.
"""

import argparse
import asyncio
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity
from app.models.base import OPPORTUNITY_STATUSES, OPPORTUNITY_TYPES

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SHEET = REPO_ROOT / "docs" / "OPZY_SOURCE_TRACKING.xlsx"
DEFAULT_SQL = REPO_ROOT / "docs" / "seed_opportunities_dev.sql"
SHEET_NAME = "Opportunities"
NOT_CONFIRMED = "not confirmed"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "db"}

# Sheet header -> table column. "Notes" is for people reading the sheet and isn't imported.
COLUMNS = {
    "Title": "title",
    "Organization": "organization",
    "Category": "category",
    "Geography": "geography",
    "Description": "description",
    "Deadline": "deadline",
    "Eligibility Notes": "eligibility_notes",
    "Application URL": "application_url",
    "Source URL": "source_url",
    "Quality Rating": "quality_rating",
    "Verified?": "verified",
    "Status": "status",
}
HEADERS = [*COLUMNS, "Notes"]

# Postgres types for the non-text columns, so NULLs in generated SQL are typed.
SQL_TYPES = {"deadline": "date", "quality_rating": "integer", "verified": "boolean"}


def _text(value: object) -> str | None:
    if value is None:
        return None
    return str(value).strip() or None


def _deadline(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _text(value)
    if text is None or text.lower() == NOT_CONFIRMED:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise ValueError(
            f"Deadline must be a date or NOT CONFIRMED, got {text!r}"
        ) from None


def _rating(value: object) -> int | None:
    if value is None or _text(value) is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float) or value != int(value):
        raise ValueError(f"Quality Rating must be a whole number 1-5, got {value!r}")
    if not 1 <= value <= 5:
        raise ValueError(f"Quality Rating must be 1-5, got {value!r}")
    return int(value)


def _verified(value: object) -> bool:
    text = (_text(value) or "no").lower()
    if text not in ("yes", "no"):
        raise ValueError(f"Verified? must be Yes or No, got {value!r}")
    return text == "yes"


def _choice(value: object, header: str, allowed: tuple[str, ...], default: str | None) -> str:
    text = (_text(value) or default or "").lower()
    if text not in allowed:
        raise ValueError(f"{header} must be one of {', '.join(allowed)}, got {value!r}")
    return text


def _parse_row(cells: dict[str, object]) -> dict:
    title = _text(cells["Title"])
    if title is None:
        raise ValueError("Title is required")
    return {
        "title": title,
        "organization": _text(cells["Organization"]),
        "category": _choice(cells["Category"], "Category", OPPORTUNITY_TYPES, None),
        "geography": _text(cells["Geography"]),
        "description": _text(cells["Description"]),
        "deadline": _deadline(cells["Deadline"]),
        "eligibility_notes": _text(cells["Eligibility Notes"]),
        "application_url": _text(cells["Application URL"]),
        "source_url": _text(cells["Source URL"]),
        "quality_rating": _rating(cells["Quality Rating"]),
        "verified": _verified(cells["Verified?"]),
        "status": _choice(cells["Status"], "Status", OPPORTUNITY_STATUSES, "active"),
    }


def parse_sheet(path: Path) -> list[dict]:
    """The sheet's rows as `opportunities` column dicts. Raises ValueError naming the row."""
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb[SHEET_NAME] if SHEET_NAME in wb.sheetnames else wb.active
        rows = ws.iter_rows(values_only=True)
        header = [_text(h) for h in next(rows, ())]
        missing = [h for h in COLUMNS if h not in header]
        if missing:
            raise ValueError(f"Sheet is missing column(s): {', '.join(missing)}")
        index = {h: header.index(h) for h in COLUMNS}

        parsed = []
        for number, values in enumerate(rows, start=2):
            if all(_text(v) is None for v in values):
                continue
            cells = {h: values[i] if i < len(values) else None for h, i in index.items()}
            try:
                parsed.append(_parse_row(cells))
            except ValueError as exc:
                raise ValueError(f"Row {number}: {exc}") from None
        return parsed
    finally:
        wb.close()


async def seed(db: AsyncSession, rows: list[dict]) -> int:
    """Insert rows not already present (by title + organization). Returns how many."""
    existing = set(
        (await db.execute(select(Opportunity.title, Opportunity.organization))).tuples()
    )
    added = 0
    for row in rows:
        key = (row["title"], row["organization"])
        if key in existing:
            continue
        db.add(Opportunity(**row))
        existing.add(key)
        added += 1
    await db.flush()
    return added


def _literal(column: str, value: object) -> str:
    if value is None:
        sql_type = SQL_TYPES.get(column)
        return f"null::{sql_type}" if sql_type else "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, date):
        return f"date '{value.isoformat()}'"
    return "'" + str(value).replace("'", "''") + "'"


def to_sql(rows: list[dict]) -> str:
    """Idempotent INSERTs for psql / the Supabase SQL editor / docker-entrypoint-initdb.d."""
    columns = list(COLUMNS.values())
    parts = [
        f"-- GENERATED from docs/{DEFAULT_SHEET.name} by backend/scripts/seed_opportunities.py.\n"
        "-- Don't edit by hand: edit the sheet, then run `python -m scripts.seed_opportunities --sql`.\n"
        "--\n"
        "-- DEV/TEST DATA: includes fictional opportunities (see the sheet's Notes column).\n"
        "-- Never run this against production.\n"
        "--\n"
        "-- Safe to re-run: rows already present (same title and organization) are skipped.\n"
    ]
    for row in rows:
        values = ",\n       ".join(_literal(c, row[c]) for c in columns)
        parts.append(
            f"\ninsert into opportunities ({', '.join(columns)})\n"
            f"select {values}\n"
            f"where not exists (\n"
            f"  select 1 from opportunities\n"
            f"  where title = {_literal('title', row['title'])}\n"
            f"    and organization is not distinct from "
            f"{_literal('organization', row['organization'])}\n"
            f");\n"
        )
    return "".join(parts)


async def _insert(rows: list[dict]) -> int:
    from app.core.db import SessionLocal, engine

    try:
        async with SessionLocal() as session:
            added = await seed(session, rows)
            await session.commit()
            return added
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--sheet", type=Path, default=DEFAULT_SHEET)
    parser.add_argument(
        "--sql",
        nargs="?",
        type=Path,
        const=DEFAULT_SQL,
        help=f"write SQL instead of inserting (default path: {DEFAULT_SQL.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--allow-nonlocal", action="store_true", help="insert into a non-local database"
    )
    args = parser.parse_args()

    try:
        rows = parse_sheet(args.sheet)
    except ValueError as exc:
        sys.exit(f"{args.sheet}: {exc}")

    if args.sql:
        args.sql.write_text(to_sql(rows))
        print(f"Wrote {len(rows)} opportunities to {args.sql}")
        return

    from app.core.config import get_settings

    host = urlsplit(get_settings().database_url).hostname
    if host not in LOCAL_HOSTS and not args.allow_nonlocal:
        sys.exit(
            f"Refusing to seed non-local database host {host!r}: the sheet holds fictional "
            "dev data. Pass --allow-nonlocal if you really mean it."
        )
    added = asyncio.run(_insert(rows))
    print(f"Inserted {added} of {len(rows)} opportunities ({len(rows) - added} already present)")


if __name__ == "__main__":
    main()
