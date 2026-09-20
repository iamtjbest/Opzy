# Sprint 7 — Auth Hardening: design

**Date:** 2026-09-20
**Sprint doc:** `../../sprints/sprint-07-auth-hardening.md`

Closes the two auth gaps Sprint 1 left open: no throttling, and no password recovery.

## Decisions taken

| Question | Decision | Why |
| --- | --- | --- |
| Rate-limit store | Postgres counter table | Deploy shape (single process vs. replicas) isn't settled; in-memory counters would silently give an attacker N× the limit once a second worker exists. No Redis in the stack. |
| How throttling attaches | FastAPI dependency per route | Matches `CurrentUser`/`DbSession`. The dependency sees the parsed body, so keying on email is trivial; middleware would have to re-parse it. |
| Signup enumeration | Keep the 409 | Hiding it properly means signup can no longer log you in immediately — it needs a full email-verification flow, which is not in this sprint. Per-IP throttling makes bulk enumeration slow. Revisit as its own sprint. |
| Token invalidation | `users.password_changed_at` | `get_current_user` already loads the user row, so the check is free. Doubles as auditable data. |
| Client IP source | `TRUST_PROXY_HEADER`, default off | Blindly trusting `X-Forwarded-For` makes the per-IP limit a no-op; never reading it makes every request look like one IP behind a proxy. |
| Limits | Moderate | Room for a shared office NAT and an honest user fumbling a password. |

## 1. Rate limiting

**Table** `rate_limit_hits(key text, window_start timestamptz, count int)`, PK `(key, window_start)`, RLS policy to match `2d6c5e3b3a6b_enable_row_level_security_on_all_tables`.

**Algorithm:** fixed windows. One
`INSERT … ON CONFLICT (key, window_start) DO UPDATE SET count = count + 1 RETURNING count`
per attempt; a 429 with `Retry-After` when the returned count exceeds the limit. Fixed
windows permit a 2× burst across a boundary — acceptable here, and far simpler than a
sliding log.

**Keys:** `{bucket}:ip:{addr}` and `{bucket}:email:{normalized}`.

**Limits:**

| Endpoint | Per IP | Per email |
| --- | --- | --- |
| `POST /auth/login` | 30 / 15 min | 10 / 15 min (IP+email) |
| `POST /auth/signup` | 5 / hr | — |
| `POST /auth/password-reset/request` | 10 / hr | 3 / hr |
| `POST /auth/password-reset/confirm` | 10 / hr | — |

**Counting rule:** login counts *failed* attempts only — a successful login must not consume
a legitimate user's budget. Signup and reset-request count every attempt, since there is no
"success" to distinguish without leaking account existence.

**Modules:** `app/core/rate_limit.py` holds the limit table, the counter write, and client-IP
resolution (`TRUST_PROXY_HEADER` bool + `TRUSTED_PROXY_HOPS` int in `Settings`, default off →
`request.client.host`; when on, the rightmost-but-N entry of `X-Forwarded-For`).
`app/api/deps.py` gains the dependency factory.

**Pruning:** an opportunistic `DELETE` of windows older than the longest limit, run on a small
fraction of requests. No cron job.

Rate limiting is also the mitigation for Argon2's ~64 MB-per-hash memory cost, so it is
load-bearing beyond brute-force defence. Do not lower the hash cost instead.

## 2. Password reset

**Table** `password_reset_tokens(id, user_id FK→users ON DELETE CASCADE, token_hash unique,
expires_at, used_at nullable, created_at)`, with RLS. Model in `app/models/password_reset.py`,
exported from `app/models/__init__.py`.

**Token:** `secrets.token_urlsafe(32)`. Stored as `sha256(token)` hex; lookup is a direct
indexed match on the hash. SHA-256 is correct here and Argon2 is not: the token carries 256
bits of entropy so there is nothing to brute-force, and an Argon2 verify per attempt would be
a 64 MB memory-exhaustion vector of exactly the kind this sprint closes. Lifetime 1 hour.

**`POST /auth/password-reset/request`** → always `202` with an identical body whether or not
the email exists. On a hit: invalidate the user's outstanding tokens, insert a new one, send
mail through the existing `EmailSender` with a `{frontend_url}/reset-password?token=…` link.
An `EmailError` is logged, never surfaced — the response must not vary.

**`POST /auth/password-reset/confirm`** → `{token, new_password}`. Unknown, used, or expired
tokens all get one generic `400`. On success, in a single transaction: set the new Argon2
hash, set `password_changed_at`, mark the token used, invalidate the user's other outstanding
tokens. Returns `204`; no access token is issued, so the user logs in fresh. Password
validation reuses `MAX_PASSWORD_LENGTH` and the `SignupRequest` rules.

## 3. Token invalidation

`users.password_changed_at timestamptz NULL`, in the same migration as the two new tables.
`create_access_token` already emits `iat`; `get_current_user` rejects a token whose `iat`
predates `password_changed_at`, using the row it already loads — no extra query.

JWT `iat` has one-second granularity, so a token minted in the same second as the change
survives. Irrelevant for the stolen-token case this defends against.

## 4. Testing

`tests/test_rate_limit.py` — window arithmetic, the IP resolver (including a spoofed
`X-Forwarded-For` with trust off), 429 shape and `Retry-After`.

`tests/test_auth.py` additions — identical responses for known and unknown emails; a token
works exactly once; an expired token is rejected; a reset invalidates a pre-existing access
token; sibling tokens die on confirm; a successful login does not consume the failure budget.

Email assertions go through the console/fake sender the Sprint 6 tests already use.

## Out of scope

- Hiding account existence at signup, and any email-verification flow.
- Sliding-window or token-bucket limiting.
- Rate limiting on endpoints other than the four above.
