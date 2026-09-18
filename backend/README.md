# Backend

FastAPI + SQLAlchemy (async) over the Postgres database already live in Supabase.

Schema is **not** managed from here — it was created from [`../docs/schema.sql`](../docs/schema.sql)
and is documented in [`../docs/DATABASE_SCHEMA.md`](../docs/DATABASE_SCHEMA.md). The models in
`app/models/` mirror it; they do not define it.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # app + test deps

cp .env.example .env
# then set JWT_SECRET in .env — the app won't start without it
```

### Database

Development runs against a local Postgres in Docker, so you don't need Supabase access:

```bash
docker compose up -d
alembic upgrade head
python -m scripts.seed_opportunities
```

That starts Postgres on **port 55432** (not 5432, which a system Postgres may already hold)
and applies [`../docs/schema.sql`](../docs/schema.sql) and
[`../docs/seed.sql`](../docs/seed.sql) automatically on first run — the same SQL that was
applied to the live Supabase project. The dev-only opportunities are loaded by the seed
script after migrations, since they use columns only the migrations create (see
[Seeding opportunities](#seeding-opportunities)). The matching `DATABASE_URL` is already in
`.env.example`.

To point at Supabase instead, swap `DATABASE_URL` for the connection string from the
dashboard → Project Settings → Database → Connection string. Nothing else changes.

To reset the local database to a clean seeded state:

```bash
docker compose down -v && docker compose up -d && alembic upgrade head && python -m scripts.seed_opportunities
```

## Run

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health — returns `200` with `"database": "connected"`
  when Supabase is reachable, `503` when it isn't.

## Auth

Email + password, with stateless JWT access tokens (HS256, 60 minutes by default).

| Endpoint | |
|---|---|
| `POST /auth/signup` | JSON `{email, password}` → `201` with `access_token` and `user`. `409` if the email is taken. |
| `POST /auth/login` | Form-encoded `username` (the email) + `password` → `access_token`. `401` on any failure. |
| `GET /auth/me` | The current user. Needs `Authorization: Bearer <token>`. |

In `/docs`, click **Authorize** and enter your email as the username to call protected routes.

To protect a new route, take the current user as a parameter:

```python
from app.api.deps import CurrentUser

@router.get("/something")
async def something(user: CurrentUser): ...
```

Passwords are hashed with Argon2 and must be 8–128 characters. Emails are trimmed and
lowercased before they're stored or looked up. Not built yet: rate limiting and password
reset (Sprint 7), refresh tokens, logout, email verification.

Two known trade-offs, both deliberate:

- **Argon2 costs ~64 MB of memory per hash** (`m=65536,t=3,p=4`, pwdlib's recommended
  settings). That's what makes stolen hashes expensive to crack, but it also means
  concurrent signups are memory-hungry. Rate limiting (Sprint 7) is the fix; don't lower
  the cost parameters instead.
- **Signup reveals whether an email is registered**, via the 409. Login deliberately does
  not — unknown email and wrong password return an identical 401 in the same amount of
  time. Hiding it at signup as well would mean replying "check your email" to every
  attempt, which needs the email sending built in Sprint 6.

`ENVIRONMENT` must be `development`, `staging` or `production`; an unrecognised value stops
the app at startup rather than silently skipping the `JWT_SECRET` strength check that
`staging` and `production` enforce.

## Profile

One profile per user, holding the onboarding fields. Both routes need
`Authorization: Bearer <token>`.

| Endpoint | |
|---|---|
| `GET /profile` | The current user's profile. `404` if they haven't onboarded yet. |
| `PUT /profile` | Replaces the whole profile — every key required; send `null` / `[]` to clear. Returns the saved profile. |

```json
{
  "education_level": "University student",
  "field_of_study": "Computer Engineering",
  "location": "Zaria, Kaduna",
  "skills": ["Python", "Figma"],
  "interests": ["job", "internship"]
}
```

- Text fields are trimmed, blank becomes `null`, max 100 characters.
- Skills are trimmed, lowercased and deduped (max 30, each 1–50 characters), and returned
  alphabetically.
- Interests must be the stored values (`job`, `internship`, `scholarship`, `fellowship`,
  `grant`, `hackathon`, `competition`), not display labels like "Jobs". They're deduped and
  returned in that order.
- The database enforces one row per skill/interest per profile as well
  (`UNIQUE (profile_id, skill)`, `UNIQUE (profile_id, opportunity_type)`).

## Opportunities

Read-only for now. Both routes need `Authorization: Bearer <token>`.

| Endpoint | |
|---|---|
| `GET /opportunities` | A page of opportunities, soonest deadline first, rolling/unconfirmed deadlines last. |
| `GET /opportunities/{id}` | One opportunity. `404` if it doesn't exist or has been `removed`; expired ones are still returned. |

`GET /opportunities` query parameters, all optional and combinable:

| Param | |
|---|---|
| `category` | Repeat to match any of several: `?category=job&category=internship`. Stored values only (`job`, `internship`, `scholarship`, `fellowship`, `grant`, `hackathon`, `competition`); anything else is `422`. |
| `geography` | Case-insensitive substring of the free-text geography — `lagos` matches "Lagos (in-person, …)". |
| `status` | `active` (default) or `expired`. `removed` is never served. |
| `deadline_after` | `YYYY-MM-DD`; keeps deadlines **on or after** that date. Pass today's date to hide ones that have passed. |
| `include_rolling` | Default `true`: keep opportunities with no deadline. `false` drops them. |
| `limit` / `offset` | Page size 1–100 (default 20) and offset (default 0). |

```json
{
  "items": [
    {
      "id": "…", "title": "Chevening Scholarship", "organization": "UK FCDO",
      "category": "scholarship", "geography": "Nigeria (study in UK)",
      "description": "…", "deadline": "2026-10-06", "eligibility_notes": "…",
      "application_url": "…", "source_url": "…", "quality_rating": 5,
      "verified": true, "status": "active", "created_at": "…", "updated_at": "…"
    }
  ],
  "total": 19, "limit": 20, "offset": 0
}
```

`total` counts every row matching the filters, not just this page.

`status` is set by hand. An opportunity whose deadline has passed stays `active` until
someone changes it, so use `deadline_after` to hide those.

## Seeding opportunities

Opportunities are entered by hand in
[`../docs/OPZY_SOURCE_TRACKING.xlsx`](../docs/OPZY_SOURCE_TRACKING.xlsx), whose columns map
1:1 to the table (its Legend tab explains each one). **Right now most rows are fictional dev
data**, shaded and marked `DUMMY` in the Notes column. Only the four verified rows from
`seed.sql` are real.

```bash
python -m scripts.seed_opportunities          # insert new rows into DATABASE_URL
python -m scripts.seed_opportunities --sql    # regenerate ../docs/seed_opportunities_dev.sql
```

- Both are safe to re-run: rows whose title and organization already exist are updated to
  match the sheet; unchanged rows are left alone.
- Inserting refuses a non-local `DATABASE_URL` unless you pass `--allow-nonlocal`, so the
  dummy rows can't land in Supabase by accident.
- After editing the sheet, regenerate the SQL file. A test fails if the two drift apart.
- `docs/seed_opportunities_dev.sql` is for local Docker and CI only. **Don't run it on
  production.**
- The SQL file needs the migrated schema, so run it after `alembic upgrade head`.

## Tests

```bash
pytest
```

Tests run against the local Docker database (`DATABASE_URL` in `.env`, or `TEST_DATABASE_URL`
if set). Each test runs in a transaction that's rolled back, so the seeded data is never
changed.

The suite refuses to start if that database isn't on a local host, so a `.env` pointing at
Supabase can't send the tests at production data. Override with `ALLOW_NONLOCAL_TEST_DB=1`
only if you're certain.

The same steps run in CI on every PR that touches `backend/`
([`.github/workflows/backend-tests.yml`](../.github/workflows/backend-tests.yml)), including
`alembic check` to catch models drifting from `docs/schema.sql`.

## Verify the DB connection

```bash
python -m scripts.check_db
```

Prints a row count for all seven live tables and loads one full `Opportunity` row, which
confirms every mapped column matches the live schema.

## Layout

```
app/
  main.py              FastAPI app, CORS, router registration
  core/config.py       env-backed settings (pydantic-settings)
  core/db.py           async engine, session factory, get_db dependency
  models/              SQLAlchemy models mirroring the live schema
  core/security.py     password hashing, JWT create/decode
  api/deps.py          shared dependencies (DbSession, CurrentUser)
  api/routes/          one module per resource
  schemas/             request/response models
alembic/               migrations (see below)
tests/                 pytest suite
scripts/check_db.py    schema/connection verification
scripts/seed_opportunities.py  load opportunities from the tracking sheet
```

## Things worth knowing

**Enum-like columns are `text` + CHECK constraints**, not native Postgres enum types. The
models use plain `str`, and the allowed values are single-sourced as tuples in
`app/models/base.py` (`OPPORTUNITY_TYPES`, `USER_ACTIONS`, etc.). Use those rather than
retyping string literals.

**Two connection strings.** Supabase gives a direct connection (port 5432) and a pooled
pgbouncer one (port 6543). Use direct for local dev. `app/core/db.py` detects port 6543 and
disables both prepared-statement caches, because pgbouncer's transaction pooling makes
asyncpg's cached statements collide across sessions.

**`sslmode` is translated automatically.** asyncpg has no `sslmode` parameter (that's the
libpq spelling), so `db.py` strips it from the URL and sets asyncpg's `ssl` instead, so the
`?sslmode=require` Supabase appends works untouched.

**Percent-encode special characters in the password.** Supabase's copied string contains a
literal `[YOUR-PASSWORD]` placeholder, and brackets — like `@`, `/`, `#` and `?` — can't
appear raw in a URL. Replace the placeholder and encode anything exotic (`[` is `%5B`, `]`
is `%5D`, `@` is `%40`). An unencoded password fails to parse before any connection is
attempted; `db.py` reports that as a readable error rather than a stack trace.

**Alembic is baselined.** The first revision in `alembic/versions/` is empty and represents
the already-live schema, so `alembic upgrade head` is safe to run against any database that
already has it — including Supabase when you get access there. Later revisions hold changes
made after that point.

**Keep the models and `docs/schema.sql` in sync.** `alembic revision --autogenerate` is the
check: if it generates anything other than an empty migration, the models and the database
have drifted. This already caught one real bug — the models originally omitted the ten
indexes from `schema.sql`, and autogenerate proposed dropping them all, including the two
unique indexes that enforce one-profile-per-user and one-match-per-user/opportunity.

**Row Level Security is on, with no policies.** A migration enables it on every table. That
blocks Supabase's auto-generated REST API (the `anon` and `authenticated` roles) from reading
anything. The backend isn't affected, because RLS doesn't apply to the role that owns the
tables. Per-user policies aren't written: the API issues its own JWTs, so Supabase's
`auth.uid()` is never set, and access control lives in the API. **On Supabase, connect the
backend as the role that owns the tables** (normally `postgres`), or every query returns
nothing.

## Roadmap

See [`../docs/ROADMAP.md`](../docs/ROADMAP.md) and [`../docs/sprints/`](../docs/sprints/)
for what's built and what's next.
