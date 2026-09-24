# Backend

FastAPI + SQLAlchemy (async) over the Postgres database already live in Supabase.

Schema management is split in two: [`../docs/schema.sql`](../docs/schema.sql) is the baseline
that was applied to the live project, and everything since is an Alembic revision under
[`alembic/versions/`](alembic/versions/), applied with `alembic upgrade head`. Both are
documented in [`../docs/DATABASE_SCHEMA.md`](../docs/DATABASE_SCHEMA.md). The models in
`app/models/` mirror the result; they do not define it.

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

**Applying schema changes to Supabase.** Run `alembic upgrade head` against Supabase, then
deploy the matching backend right away — old code and the new schema (and vice versa) break
each other. For example, the education-level CHECK rejects old free-text values, and new
code expects the new columns. Never run [`../docs/seed_opportunities_dev.sql`](../docs/seed_opportunities_dev.sql)
or `scripts.seed_opportunities --sql`'s output against Supabase: the sheet holds fictional
rows. The real opportunities' structured eligibility values don't have a production load
path yet; that's a known open item.

To reset the local database to a clean seeded state:

```bash
docker compose down -v && docker compose up -d && alembic upgrade head && python -m scripts.seed_opportunities
```

If you're an existing developer pulling new migrations rather than starting fresh, run
`alembic upgrade head` and then `python -m scripts.seed_opportunities` so your existing dev
rows pick up any new sheet columns.

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
| `POST /auth/signup` | JSON `{email, password}` → `202`, **no token**, always the same body whether the address is new or already registered. Emails a confirmation link, or a "you already have an account" notice. |
| `POST /auth/login` | Form-encoded `username` (the email) + `password` → `access_token`. `401` on any failure. Works for unverified accounts. |
| `GET /auth/me` | The current user, including `email_verified_at`. Needs `Authorization: Bearer <token>`. |
| `POST /auth/verify-email/confirm` | JSON `{token}` → `200` with `access_token`, so the user lands logged in. `400` for a token that's unknown, already spent, or expired — one message for all three. |
| `POST /auth/verify-email/resend` | JSON `{email}` → `202`, always the same body. A fresh link if the address needs confirming, a "you're already confirmed" note if it doesn't, nothing at all if it has no account. |
| `POST /auth/password-reset/request` | JSON `{email}` → `202`, always the same body whether or not the account exists. Emails a single-use link valid for 1 hour. |
| `POST /auth/password-reset/confirm` | JSON `{token, new_password}` → `204`. `400` for a token that's unknown, already spent, or expired — one message for all three. |
| `DELETE /account` | JSON `{password}` → `204`. Needs a bearer token **and** the current password; a wrong one is `403`, not `401`. Hard delete: everything cascades from the user row. |

In `/docs`, click **Authorize** and enter your email as the username to call protected routes.

To protect a new route, take the current user as a parameter:

```python
from app.api.deps import CurrentUser

@router.get("/something")
async def something(user: CurrentUser): ...
```

Passwords are hashed with Argon2 and must be 8–128 characters. Emails are trimmed and
lowercased before they're stored or looked up. Not built yet: refresh tokens,
logout-everywhere, and changing your email address once verified.

### Email verification

Signing up doesn't log you in. `signup` answers `202` with a fixed body — **the same body
and status whether the address is new, already registered, or nonsense** — and mails either
a `FRONTEND_URL/verify-email?token=…` link or, if the address already has an account, a
notice with no token in it. There is no `409` any more; that status was an
account-existence oracle for anyone who cared to ask.

The password is hashed *before* the new-versus-existing branch so both paths pay the same
~64 MB Argon2 cost, and both mails are queued as background tasks, for exactly the reason
the password-reset section gives below.

`verify-email/confirm` spends the token, stamps `users.email_verified_at` and returns an
access token — clicking a link only you could have received is at least as good as a
password, so there's no point bouncing the user to a login form.

**An unverified account is a normal account, except it gets no email.** It can log in,
onboard, use the feed and change its settings; `send_notifications` simply skips any user
whose `email_verified_at` is null. Blocking login instead would turn a spam-foldered email
into a permanent lockout, which is a worse failure than a delayed digest.

**Keep `EMAIL_BACKEND=console` for local work and for the e2e suite.** Signup now sends mail
on *every* attempt, where before Sprint 9 it sent none, so with `EMAIL_BACKEND=resend` a
Playwright run makes a real Resend API call per signup. Every one is refused — the suite's
addresses are `@example.com`, which Resend rejects with `422 validation_error` — and the
refusal is logged and swallowed rather than surfaced, exactly as designed, so the tests still
pass. It is just wasted quota and a noisy log.

`email_verification_tokens` is its own table rather than a `purpose` column on
`password_reset_tokens`. Sharing one table means a reset token could be spent as proof of
address anywhere a query forgot to filter — two tables make that impossible to write.

### Deleting an account

`DELETE /account` is a hard delete, and wants the current password in the body as well as a
valid bearer token: a borrowed or stolen session alone should not be able to destroy an
account irreversibly. A wrong password is a **`403`**, not a `401` — everything in this app
reads a 401 as "your session expired", and the frontend turns one into a forced logout, so
answering 401 here would log a user out for a typo. The `ON DELETE CASCADE`s in `../docs/schema.sql` take the profile, its
skills and interests, every action, the notification log and both token tables with the user
row, so afterwards the address is free to sign up again as a brand-new account.

### Password reset

`request` mints 32 random bytes, stores only their SHA-256, and emails the token as a
`FRONTEND_URL/reset-password?token=…` link. `confirm` looks the hash up, sets the new
Argon2 hash, marks the token spent, and retires every other outstanding token for that
user. Nothing is revealed either way: an unknown address gets the same `202` and the same
body as a real one, and a failed send is logged rather than surfaced.

The send is queued as a background task rather than awaited. Only a real account has mail
to send, so waiting for Resend would make a registered address answer measurably slower
than an unregistered one — the enumeration the identical response exists to prevent. What
remains in the request is one local insert; the endpoint is much closer to constant-time,
not exactly constant-time.

Reset tokens are SHA-256, not Argon2, on purpose — there is nothing to brute-force in a
256-bit random token, and an Argon2 verify per attempt would be a 64 MB-per-request DoS.

In development `EMAIL_BACKEND=console` just logs the email, so the reset link appears in
the server log.

### Rate limiting

Fixed windows counted in `rate_limit_hits`, in Postgres rather than in memory so the limit
still holds if the API ever runs as more than one worker.

| Endpoint | Per IP | Per email |
|---|---|---|
| `POST /auth/login` | 30 / 15 min | 10 / 15 min |
| `POST /auth/signup` | 5 / hour | 3 / hour |
| `POST /auth/verify-email/resend` | 10 / hour | 3 / hour |
| `POST /auth/verify-email/confirm` | 10 / hour | — |
| `POST /auth/password-reset/request` | 10 / hour | 3 / hour |
| `POST /auth/password-reset/confirm` | 10 / hour | — |
| `DELETE /account` | 10 / hour | — |

Signup gained a per-email budget in Sprint 9: it now mails the address whether or not that
address has an account, so without one it would be a way to bomb somebody's inbox.

Over the limit is a `429` with `Retry-After`. The counter increments *before* the password
is hashed, and a successful login refunds its own hit — so good logins never eat the
budget, without the race that a check-then-increment would have.

The per-IP key comes from the socket address. Set `TRUST_PROXY_HEADER=true` (with
`TRUSTED_PROXY_HOPS`) only when a proxy really is in front; otherwise `X-Forwarded-For` is
attacker-controlled and a fresh value per request would make the limit a no-op.

### Changing a password invalidates old tokens

`users.password_changed_at` is set on reset, and `get_current_user` rejects any access
token whose `iat` predates it. It costs nothing — the dependency already loads the user row.

Two known trade-offs, both deliberate:

- **Argon2 costs ~64 MB of memory per hash** (`m=65536,t=3,p=4`, pwdlib's recommended
  settings). That's what makes stolen hashes expensive to crack, but it also means
  concurrent signups are memory-hungry. Rate limiting is the mitigation; don't lower the
  cost parameters instead.
- **Signup still reveals whether an email is registered**, via the 409. Login and password
  reset deliberately do not. Hiding it at signup means replying "check your email" to every
  attempt, so signup can no longer log you straight in — that's an email-verification
  feature, deferred to its own sprint. Per-IP throttling makes bulk enumeration slow in the
  meantime.

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

Read-only; users act on opportunities through [User actions](#user-actions). Both routes
need `Authorization: Bearer <token>`.

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

### Feed

`GET /feed` — the logged-in user's matches, best first. Requires a Bearer token; `404`
`"Profile not found"` until they've saved a profile.

Query: `category` (repeatable), `limit` (1–100, default 20), `offset`.

```json
{"items": [{"opportunity": {…}, "score": 73,
            "explanation": "Recommended because you study Computer Engineering, you know Python, and you're looking for internships. It's open to undergraduates.",
            "user_action": null}],
 "total": 10, "limit": 20, "offset": 0}
```

Opportunities the user has dismissed or applied to are left out before ranking, so `total`
and the pages only count what's shown. Saved ones stay in, with `"user_action": "saved"`.

How matching works (`app/matching/`):

- **Hard eligibility** drops an opportunity when its `eligible_countries` or
  `education_levels` exclude the user's `nationality` or `education_level`, when its
  deadline has passed (Lagos date), or when it isn't `active`. Empty lists and unknown
  profile values never block.
- **Score** (0–100) = field of study 40 + skill overlap 40 × share of the opportunity's
  skills + wanted category 20. Weights live in `Weights` in `app/matching/engine.py`;
  they're deliberately untuned until there's usage data.
- **Ranking**: score, then soonest deadline (rolling last), then title.
- **Explanation**: every match gets one, and it only claims eligibility that was checked.
- Computed per request; nothing is written to `opportunity_matches` yet.

## User actions

Save, dismiss or mark as applied. All three routes need `Authorization: Bearer <token>`, but
not a profile.

| Endpoint | |
|---|---|
| `POST /opportunities/{id}/actions` | Record an action; returns the user's state for that opportunity after it. `404` if the opportunity doesn't exist or is `removed`; expired ones are fine. |
| `GET /saved` | Opportunities the user has saved, most recently saved first. |
| `GET /applications` | Opportunities the user has marked applied, most recent first. |

```json
POST /opportunities/{id}/actions
{"action": "dismissed", "dismiss_reason": "not_eligible"}

200
{"opportunity_id": "…", "action": "dismissed", "dismiss_reason": "not_eligible",
 "actioned_at": "2026-09-19T10:00:00Z"}
```

- `action` is `saved`, `unsaved` (the Saved screen's Remove), `dismissed` or `applied`.
- `dismiss_reason` is optional and only allowed with `dismissed` (otherwise `422`). The
  allowed codes are `not_relevant`, `pay_too_low`, `not_eligible`, `not_interested_org`
  and `other`, one for each option in the frontend's dismiss dialog.
- `unsaved` clears whatever state the opportunity had. The response then has `action`,
  `dismiss_reason` and `actioned_at` all `null`.
- Actions replace each other: the latest one is the state. So saving a dismissed opportunity
  undoes the dismiss, and applying to a saved one moves it from Saved to Applications.
- Repeating the current state writes nothing and returns it unchanged. That includes a
  dismiss with no reason, which keeps the reason already given; a different reason is
  recorded.

The lists take `limit` (1–100, default 20) and `offset`, and return
`{"items": [{"opportunity": {…}, "actioned_at": "…"}], "total", "limit", "offset"}`.
Expired opportunities stay in them; `removed` ones don't.

How it's stored: `user_opportunity_actions` is an append-only log, one row per action, so
history is kept. The latest row per user and opportunity is the current state. That rule
lives in one place, `latest_actions` in `app/actions.py`. Each request takes a
per-user-and-opportunity advisory lock before reading the state, so simultaneous identical
requests (a double-click) log one row, not two.

## Notifications

Users are emailed about **new strong matches**: opportunities scoring at least
`STRONG_MATCH_SCORE` (60, in `app/notifications/run.py`) that were added after they signed
up, that they haven't saved, dismissed or applied to, and that haven't been emailed to them
before. `match_notifications` records every one sent.

How often depends on their cadence:

| Cadence | Emails |
|---|---|
| `instant` | on the next run after a match appears |
| `daily` | at most one digest a day |
| `weekly` | at most one digest a week |
| `off` | none |

Nothing is sent when there's nothing new. Each email lists up to 10 matches, best first,
and links to the rest on the feed.

`GET /settings/notifications` returns `{"cadence": "daily", "channel": "email"}`.
`PUT /settings/notifications` with `{"cadence": "weekly"}` changes it. The channel is
always `email` for now.

Sending is a script, run on a schedule:

```bash
python -m scripts.send_notifications
# cron, every 15 minutes:
# */15 * * * * cd /path/to/backend && .venv/bin/python -m scripts.send_notifications
```

It's safe to re-run and to overlap: only one run works at a time. A refused email (the
provider rejected it) is retried cleanly on the next run. A database error is handled
differently depending on when it struck: if it happened before sending, the user is
retried next run like a refusal; if it happened after the email had already gone out (for
example, the commit that records it failed), the user may simply be emailed again next
run rather than cleanly retried. Either kind of failure makes the script exit 1.
`EMAIL_BACKEND=console` (the default) only logs emails. Set `EMAIL_BACKEND=resend`,
`RESEND_API_KEY` and `EMAIL_FROM` to send for real, and `FRONTEND_URL` for the links.
Deployed environments refuse to start with the console backend.

### Testing it for real, without mailing strangers

Before running with `EMAIL_BACKEND=resend`, **check who would receive mail**:

```bash
docker compose exec -T db psql -U opzy -d opzy \
  -c "select email, notification_cadence from users;"
```

Testing leaves behind `@example.com` users. That's a reserved domain that can never receive
mail, so every one is a guaranteed bounce, and bounces damage the sending reputation of the
domain you send from. Set everything to `off`, then enable only an address you control:

```bash
docker compose exec -T db psql -U opzy -d opzy \
  -c "delete from users where email like '%@example.com';" \
  -c "update users set notification_cadence = 'off';" \
  -c "update users set notification_cadence = 'instant' where email = 'you@example.org';"
```

Never point a test run at the production database: the script emails whoever it finds there.

Four things then decide whether anything actually sends, and all four are easy to mistake
for a broken setup:

- **The address must be confirmed.** Since Sprint 9 a user with `email_verified_at` null is
  skipped entirely, so an account created by hand or by the test suite sends nothing until
  it verifies. To enable one for testing:
  `update users set email_verified_at = now() where email = 'you@example.org';`
- **The profile must be filled in.** Only matches scoring 60 or more
  (`STRONG_MATCH_SCORE`) are emailed. A profile with no nationality or education level
  scores everything below that, so a run reports `Emailed 0 user(s)` and exits 0.
- **The opportunity must be newer than the account** — `Opportunity.created_at >=
  user.created_at`. This is deliberate, so a new signup isn't mailed the whole back
  catalogue, but it means seeded opportunities never notify an account created after them.
  To test, insert one dated `now()`.
- **Resend's test sender only mails you.** With `EMAIL_FROM=Opzy <onboarding@resend.dev>`
  and no verified domain, any recipient other than the Resend account's own address is
  refused with `403 validation_error`. The script logs it, marks the user for retry, and
  exits 1 — working as designed, not a bug.

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
  matching/            feed eligibility, scoring and explanations (no DB access)
  actions.py           a user's current state per opportunity, from the actions log
  api/routes/          one module per resource
  schemas/             request/response models
  email.py             sending email: console backend for dev, Resend for real
  user_facts.py        what matching knows about a user, from their profile
  notifications/       who's due an email, what it says, and the run that sends them
alembic/               migrations (see below)
tests/                 pytest suite
scripts/check_db.py    schema/connection verification
scripts/seed_opportunities.py  load opportunities from the tracking sheet
scripts/send_notifications.py  the scheduled job that emails new strong matches
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
