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
docker compose down -v && docker compose up -d && alembic upgrade head
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
confirms every mapped column matches the live schema. Expect `opportunities` to be empty
until Sprint 3 seeds it.

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
