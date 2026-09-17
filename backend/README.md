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
```

### Database

Development runs against a local Postgres in Docker, so you don't need Supabase access:

```bash
docker compose up -d
```

That starts Postgres on **port 55432** (not 5432, which a system Postgres may already hold)
and applies [`../docs/schema.sql`](../docs/schema.sql) and
[`../docs/seed.sql`](../docs/seed.sql) automatically on first run — the same SQL that was
applied to the live Supabase project. The matching `DATABASE_URL` is already in
`.env.example`.

To point at Supabase instead, swap `DATABASE_URL` for the connection string from the
dashboard → Project Settings → Database → Connection string. Nothing else changes.

To reset the local database to a clean seeded state:

```bash
docker compose down -v && docker compose up -d
```

## Run

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health — returns `200` with `"database": "connected"`
  when Supabase is reachable, `503` when it isn't.

## Verify the DB connection

```bash
python -m scripts.check_db
```

Prints a row count for all seven live tables and loads one full `Opportunity` row, which
confirms every mapped column matches the live schema. Expect `opportunities` to be empty
until Sprint 3 seeds it.

## Layout

```
app/
  main.py              FastAPI app, CORS, router registration
  core/config.py       env-backed settings (pydantic-settings)
  core/db.py           async engine, session factory, get_db dependency
  models/              SQLAlchemy models mirroring the live schema
  api/routes/          one module per resource
alembic/               migrations (baseline not yet stamped — see below)
scripts/check_db.py    schema/connection verification
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
libpq spelling), so `db.py` strips it from the URL and sets asyncpg's `ssl` instead. You can
paste the Supabase connection string as-is.

**Alembic is baselined.** `alembic/versions/` holds one empty baseline revision
representing the already-live schema. Because it's empty, `alembic upgrade head` is safe to
run against any database that already has the schema — including Supabase when you get
access there. Migrations are only needed for changes *after* that point.

**Keep the models and `docs/schema.sql` in sync.** `alembic revision --autogenerate` is the
check: if it generates anything other than an empty migration, the models and the database
have drifted. This already caught one real bug — the models originally omitted the ten
indexes from `schema.sql`, and autogenerate proposed dropping them all, including the two
unique indexes that enforce one-profile-per-user and one-match-per-user/opportunity.

**Row Level Security is off.** Deliberately — see the note at the bottom of
[`../docs/schema.sql`](../docs/schema.sql). It needs policies written once real auth exists
(Sprint 1), and must be enabled before anything is exposed publicly.

## Roadmap

See [`../docs/ROADMAP.md`](../docs/ROADMAP.md) and [`../docs/sprints/`](../docs/sprints/)
for what's built and what's next.
