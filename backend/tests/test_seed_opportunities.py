from datetime import date, datetime
from pathlib import Path

import pytest
from openpyxl import Workbook
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity, OpportunityMatch, UserOpportunityAction
from scripts.seed_opportunities import (
    DEFAULT_SHEET,
    DEFAULT_SQL,
    HEADERS,
    REGIONS,
    parse_sheet,
    seed,
    to_sql,
)


def _sheet(tmp_path: Path, *rows: list) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Opportunities"
    ws.append(HEADERS)
    for row in rows:
        ws.append(row)
    path = tmp_path / "sheet.xlsx"
    wb.save(path)
    return path


def _row(**overrides) -> list:
    values = {
        "Title": "Graduate Data Analyst",
        "Organization": "Sahel Insights",
        "Category": "job",
        "Geography": "Abuja",
        "Description": "Entry-level analyst role.",
        "Deadline": datetime(2026, 11, 1),
        "Eligibility Notes": "BSc required",
        "Application URL": "https://example.com/apply",
        "Source URL": "https://example.com/source",
        "Quality Rating": 3,
        "Verified?": "No",
        "Status": "active",
        "Eligible Countries": "NG",
        "Education Levels": "Graduate, postgraduate",
        "Fields of Study": "Mathematics, Statistics",
        "Skills": "SQL, Excel",
        "Notes": "anything",
        **overrides,
    }
    return [values[h] for h in HEADERS]


# --- parsing ---------------------------------------------------------------------------


def test_parses_a_row_into_table_columns(tmp_path: Path):
    [row] = parse_sheet(_sheet(tmp_path, _row()))

    assert row == {
        "title": "Graduate Data Analyst",
        "organization": "Sahel Insights",
        "category": "job",
        "geography": "Abuja",
        "description": "Entry-level analyst role.",
        "deadline": date(2026, 11, 1),
        "eligibility_notes": "BSc required",
        "application_url": "https://example.com/apply",
        "source_url": "https://example.com/source",
        "quality_rating": 3,
        "verified": False,
        "status": "active",
        "eligible_countries": ["NG"],
        "education_levels": ["graduate", "postgraduate"],
        "fields_of_study": ["Mathematics", "Statistics"],
        "skills": ["SQL", "Excel"],
    }


def test_not_confirmed_and_blank_deadlines_become_null(tmp_path: Path):
    rows = parse_sheet(
        _sheet(tmp_path, _row(Deadline="NOT CONFIRMED"), _row(Deadline=" not confirmed "),
               _row(Deadline=None))
    )

    assert [r["deadline"] for r in rows] == [None, None, None]


def test_verified_yes_no_and_blank(tmp_path: Path):
    rows = parse_sheet(
        _sheet(tmp_path, _row(**{"Verified?": "Yes"}), _row(**{"Verified?": "no"}),
               _row(**{"Verified?": None}))
    )

    assert [r["verified"] for r in rows] == [True, False, False]


def test_text_is_trimmed_and_blank_becomes_null(tmp_path: Path):
    [row] = parse_sheet(
        _sheet(tmp_path, _row(Title="  Padded  ", Organization="   ", Category=" Grant "))
    )

    assert row["title"] == "Padded"
    assert row["organization"] is None
    assert row["category"] == "grant"


def test_blank_status_defaults_to_active(tmp_path: Path):
    [row] = parse_sheet(_sheet(tmp_path, _row(Status=None)))

    assert row["status"] == "active"


def test_empty_rows_are_skipped(tmp_path: Path):
    rows = parse_sheet(_sheet(tmp_path, _row(), [None] * len(HEADERS), _row(Title="Second")))

    assert [r["title"] for r in rows] == ["Graduate Data Analyst", "Second"]


def test_list_cells_are_split_trimmed_and_deduped(tmp_path: Path):
    [row, blank] = parse_sheet(
        _sheet(
            tmp_path,
            _row(Skills=" SQL , sql,Excel,, ", **{"Education Levels": "postgraduate, Graduate"}),
            _row(Skills=None, **{"Eligible Countries": None, "Education Levels": "  ",
                                 "Fields of Study": None}),
        )
    )

    assert row["skills"] == ["SQL", "Excel"]
    # Canonical EDUCATION_LEVELS order, whatever order the cell used.
    assert row["education_levels"] == ["graduate", "postgraduate"]
    assert (blank["skills"], blank["eligible_countries"], blank["education_levels"],
            blank["fields_of_study"]) == ([], [], [], [])


def test_country_codes_are_uppercased_and_regions_expand(tmp_path: Path):
    [row] = parse_sheet(_sheet(tmp_path, _row(**{"Eligible Countries": "ecowas, ng"})))

    assert row["eligible_countries"] == sorted(REGIONS["ECOWAS"])
    assert row["eligible_countries"].count("NG") == 1


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"Title": None}, "Title is required"),
        ({"Category": "Jobs"}, "Category"),
        ({"Status": "archived"}, "Status"),
        ({"Quality Rating": 6}, "Quality Rating"),
        ({"Quality Rating": "five"}, "Quality Rating"),
        ({"Verified?": "maybe"}, "Verified?"),
        ({"Deadline": "next month"}, "Deadline"),
        ({"Eligible Countries": "Nigeria"}, "Eligible Countries"),
        ({"Eligible Countries": "XX"}, "Eligible Countries"),
        ({"Education Levels": "University student"}, "Education Levels"),
    ],
)
def test_bad_values_name_the_row_and_column(tmp_path: Path, overrides: dict, message: str):
    with pytest.raises(ValueError, match=rf"Row 3: .*{message}"):
        parse_sheet(_sheet(tmp_path, _row(), _row(**overrides)))


def test_missing_column_is_rejected(tmp_path: Path):
    wb = Workbook()
    wb.active.title = "Opportunities"
    wb.active.append([h for h in HEADERS if h != "Category"])
    path = tmp_path / "sheet.xlsx"
    wb.save(path)

    with pytest.raises(ValueError, match="Category"):
        parse_sheet(path)


def test_the_committed_sheet_parses():
    rows = parse_sheet(DEFAULT_SHEET)

    assert 10 <= len(rows) <= 30
    assert "Chevening Scholarship" in {r["title"] for r in rows}


def test_committed_sql_matches_the_sheet():
    # docs/seed_opportunities_dev.sql is generated from the sheet; regenerate it with
    # `python -m scripts.seed_opportunities --sql` after editing the sheet.
    assert DEFAULT_SQL.read_text() == to_sql(parse_sheet(DEFAULT_SHEET))


# --- SQL output ------------------------------------------------------------------------


def test_sql_escapes_quotes_and_writes_nulls(tmp_path: Path):
    rows = parse_sheet(
        _sheet(tmp_path, _row(Title="Women's Fund", Deadline="NOT CONFIRMED", **{"Verified?": "Yes"}))
    )

    sql = to_sql(rows)

    assert "'Women''s Fund'" in sql
    assert "null" in sql
    assert "true" in sql


def test_sql_writes_lists_as_text_arrays(tmp_path: Path):
    rows = parse_sheet(_sheet(tmp_path, _row(Skills=None)))

    sql = to_sql(rows)

    assert "array['NG']::text[]" in sql
    assert "'{}'::text[]" in sql


async def test_generated_sql_updates_existing_rows(tmp_path: Path, db_session: AsyncSession):
    await db_session.execute(delete(OpportunityMatch))
    await db_session.execute(delete(UserOpportunityAction))
    await db_session.execute(delete(Opportunity))
    db_session.add(
        Opportunity(title="Graduate Data Analyst", organization="Sahel Insights",
                    category="job", geography="old value")
    )
    await db_session.flush()
    sql = to_sql(parse_sheet(_sheet(tmp_path, _row())))

    conn = await db_session.connection()
    for statement in filter(str.strip, sql.split(";\n")):
        await conn.exec_driver_sql(statement)

    db_session.expire_all()
    [stored] = await db_session.scalars(
        select(Opportunity).where(Opportunity.title == "Graduate Data Analyst")
    )
    assert stored.geography == "Abuja"
    assert stored.eligible_countries == ["NG"]


async def test_generated_sql_runs_and_is_idempotent(tmp_path: Path, db_session: AsyncSession):
    rows = parse_sheet(_sheet(tmp_path, _row(Title="Women's Fund", Deadline=None), _row()))
    sql = to_sql(rows)
    before = await db_session.scalar(select(func.count()).select_from(Opportunity))

    # Raw driver SQL, as psql would run it: text() would read any ":word" in the data as a
    # bind parameter.
    conn = await db_session.connection()
    for _ in range(2):
        for statement in filter(str.strip, sql.split(";\n")):
            await conn.exec_driver_sql(statement)

    after = await db_session.scalar(select(func.count()).select_from(Opportunity))
    assert after - before == 2


# --- inserting -------------------------------------------------------------------------


async def test_seed_inserts_new_rows_and_updates_changed_ones(
    tmp_path: Path, db_session: AsyncSession
):
    await db_session.execute(delete(OpportunityMatch))
    await db_session.execute(delete(UserOpportunityAction))
    await db_session.execute(delete(Opportunity))
    rows = parse_sheet(
        _sheet(tmp_path, _row(Title="One"), _row(Title="Two", Organization=None))
    )

    first = await seed(db_session, rows)
    unchanged = await seed(db_session, rows)
    changed = await seed(db_session, [{**rows[0], "skills": ["Go"]}, rows[1]])

    assert (first, unchanged, changed) == ((2, 0), (0, 0), (0, 1))
    stored = await db_session.scalars(select(Opportunity).order_by(Opportunity.title))
    [one, two] = stored
    assert (one.title, one.deadline, one.verified, one.skills) == (
        "One", date(2026, 11, 1), False, ["Go"]
    )
    assert (two.title, two.organization) == ("Two", None)
