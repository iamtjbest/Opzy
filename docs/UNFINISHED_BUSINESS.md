# Unfinished Business

Everything still open on Opzy, as of 2026-09-29. The code for the MVP loop (sign up →
profile → matched feed with a reason → save / dismiss / apply → email notifications) is
built and tested. What's left is mostly getting it live, and getting real data into it.

Update this file as items close: delete the item, or move it to "Done" at the bottom.

---

## 1. Blocking launch

These have to be done before a real user can use Opzy.

### 1.1 Push and merge the branch
- The 7 commits from the 2026-09-28 audit are on `sprint-1-auth` locally and **not pushed**.
- PR #2 (`sprint-1-auth` → `main`) carries Sprints 5–9, but its title still says
  "Sprint 5". Retitle it before merging.
- PR #2 is merged by the owner, by hand.

### 1.2 Deploy
- **Nothing is deployed.** There is no host chosen, no Dockerfile, and no hosting config.
- `FRONTEND_URL` is still `http://localhost:3000`, so every link in every email (verify,
  reset, matches) points at a laptop.
- Environment the deploy needs:
  - **Backend:** `DATABASE_URL`, `JWT_SECRET` (32+ chars), `ENVIRONMENT=production`,
    `EMAIL_BACKEND=resend`, `RESEND_API_KEY`, `EMAIL_FROM`, `FRONTEND_URL`,
    `CORS_ORIGINS`, `INTERNAL_API_SECRET`.
  - **Frontend:** `API_URL`, `INTERNAL_API_SECRET` (same value as the backend's), and
    `TRUSTED_PROXY_HOPS` if more than one proxy sits in front of Next.js.
- The API **refuses to start** in staging or production without a strong `JWT_SECRET`,
  the Resend settings, and `INTERNAL_API_SECRET`. That's deliberate. Without
  `INTERNAL_API_SECRET`, every user shares one rate-limit bucket.
- `TRUST_PROXY_HEADER` / `TRUSTED_PROXY_HOPS` on the backend: set them only if a proxy
  really sits in front of the API itself.

### 1.3 Supabase
- The Supabase credentials we were given don't work, so all development ran against a
  local Docker Postgres that replays `docs/schema.sql`.
- Once access works:
  - Point `DATABASE_URL` at Supabase. Use the pooled connection (port 6543) for deploys.
  - Run `alembic upgrade head`. **Every migration since the baseline is unapplied
    there:** row-level security, the profile uniqueness constraints, nationality and
    education levels, structured eligibility, the unsaved action, off-cadence and match
    notifications, auth hardening, and email verification.
  - **Row-level security is still off in Supabase** until that runs.
  - Before the uniqueness migration, check for duplicate skills and interests, or the
    upgrade fails and rolls back:
    `SELECT profile_id, skill, count(*) FROM profile_skills GROUP BY 1,2 HAVING count(*) > 1;`
    and the same for `profile_interests` on `opportunity_type`.
  - The email-verification migration marks every existing user as verified. That's right
    for dev data; think again if real users exist by then.
  - Re-run Sprint 0's check against the live tables (`python -m scripts.check_db`).

### 1.4 Email
- **Verify a sender domain in Resend.** `EMAIL_FROM` is Resend's test sender, which
  delivers only to the Resend account's own address. Every other recipient gets
  `403 validation_error`, so Opzy can't yet email a single real user. That covers
  verification links, password resets and match emails.
- **Schedule the notification job:** `python -m scripts.send_notifications` every ~15
  minutes (the cron line is in `backend/README.md`). It needs the production database,
  so it depends on 1.2 and 1.3.

### 1.5 Real opportunities
- **20 of the 24 opportunities are fictional** (`DUMMY` in
  `docs/OPZY_SOURCE_TRACKING.xlsx`, or `[TEST]`).
- Replace them with 10–30 real, hand-entered ones. This roadmap item is still open.
- Decide how the real ones reach production. Either run
  `python -m scripts.seed_opportunities --allow-nonlocal`, or generate the SQL without
  the dummy rows.

---

## 2. Decisions still to make

### 2.1 Expired opportunities
- Opportunity `status` is set by hand, so past-deadline rows stay `active`.
- `/feed` and the notification job filter those out themselves.
- `GET /opportunities` doesn't, unless the caller passes `deadline_after=<today>`.
- Undecided: an automatic expiry job, or just filtering past deadlines everywhere by
  default.

### 2.2 Where early-access signups live
- The landing page's early-access form writes to `frontend/data/early_access.csv` on the
  server's disk. That file is gitignored.
- Most hosts, Vercel included, throw that disk away on every deploy, and it isn't shared
  between instances. **Signups would be lost.**
- Options: a table in the backend database, a form or email-list provider, or a
  persistent volume.
- Its rate limit is in memory too, so it resets on restart and isn't shared between
  instances.

### 2.3 Open questions from the MVP spec
- Which opportunity fields are mandatory and which are optional.
- Which fields need AI extraction, and which are entered by hand. Today, all are by hand.
- How missing values are represented. Partly settled already: a null deadline means
  rolling or unconfirmed, and an empty eligibility list means unrestricted.
- How duplicate opportunities are detected. Today it's only exact title + organisation,
  in the seed script.

### 2.4 Matching thresholds
- Relevance weights (field 40, skills 40, interest 20) and the "strong match" threshold
  for emails (60) are first guesses. The MVP spec says not to lock them until real usage
  data exists, so revisit them once people are using it.

---

## 3. Known gaps and tech debt (not blocking)

- **No full Content-Security-Policy.** The frontend sends `frame-ancestors 'none'`,
  `X-Frame-Options`, `nosniff` and a referrer policy, but no script policy. Next.js's
  inline scripts need nonces for one, which is its own piece of work.
- **The notification job re-scores every due user on every run**, even when nothing is
  new. Fine now; it becomes the job's main cost at a few thousand users. Cheap exact fix:
  take `max(opportunities.created_at)` once per run, and skip anyone emailed at or after
  it.
- **Matches aren't stored.** `opportunity_matches` is unused, and the feed is ranked in
  memory on every request. Fine at tens or hundreds of opportunities; store the scores
  once that stops being true.
- **The notification job's local-testing traps**, documented in `backend/README.md`:
  - It only considers opportunities created after the user signed up.
  - It only sends matches scoring 60 or more.
  - It will try to email every `@example.com` user left over from testing.
  - Check `select email, notification_cadence from users` before running it with
    `EMAIL_BACKEND=resend`, and never test it against production.
- **`backend/.env` has `EMAIL_BACKEND=resend`.** Anything run locally with it sends real
  email. The Playwright config overrides it; anything else run by hand has to as well.
- **Playwright isn't in CI.** It needs Postgres, uvicorn and seeded opportunities, so it
  runs locally only (`npm run test:e2e` in `frontend/`).
- **`next dev` creates a stray `frontend/frontend/.next/`.** The cause is unknown; it
  isn't Turbopack root detection. ESLint ignores it, and it's safe to delete.
- **A test email address is still in git history** from the early-access CSV that used
  to be committed. It's no longer tracked. Removing it from history would mean rewriting
  published commits, which hasn't been done.
- **`CLAUDE.md` is in older commits** from before it was made local. History wasn't
  rewritten.

---

## 4. Out of scope until the MVP loop is proven

Not unfinished, but deliberately deferred per `MVP_SPEC.md`. Don't pull these forward
without a scope decision:

- admin UI or review queue for opportunities (manage them directly in the database for
  now)
- WhatsApp notifications
- ML-based ranking
- auto-apply
- native mobile apps, recruiter marketplace, employer dashboard, resume builder
- more than the 7 current opportunity categories
- automated opportunity ingestion or scraping

---

## 5. Local housekeeping

- Delete the leftover test opportunity in the dev database. It was added by hand on
  2026-09-22 while proving the notification path:
  `delete from opportunities where title like '[TEST]%';`
- Delete the local tag `pre-main-merge-backup` once you're happy with the merge of
  `main`: `git tag -d pre-main-merge-backup`. It was never pushed.

---

## Done

_Move items here as they close, with the date._
