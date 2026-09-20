# Opzy frontend

Next.js 16 (App Router) talking to the FastAPI backend in `../backend`.

**Read `AGENTS.md` before writing Next-specific code.** This version has breaking changes
from older Next.js, and the guides in `node_modules/next/dist/docs/` are the reference.
`middleware.ts` is gone — route protection lives in `src/proxy.ts`.

## How it fits together

Next.js is a backend-for-frontend. The browser never sees the backend's JWT:

- Logging in stores the token in an **httpOnly cookie** (`opzy_session`) that only server
  code can read. There is no `NEXT_PUBLIC_` API URL and nothing in `localStorage`.
- Pages are async Server Components that fetch through one module, `src/lib/api/server.ts`.
- Mutations are Server Actions in `src/app/actions/`.
- A `401` from the backend goes to `/session/end`, which clears the cookie and redirects to
  login. It has to be a route handler: a Server Component can't delete a cookie mid-render,
  and leaving a dead cookie in place makes `proxy.ts` bounce `/login` back to `/feed` forever.

## Running it

The backend and the Docker database must both be up:

```bash
cd ../backend
docker compose up -d                       # Postgres
.venv/bin/uvicorn app.main:app --port 8000 # API
```

Then:

```bash
npm install
npm run dev     # http://localhost:3000
```

`API_URL` points at the backend and defaults to `http://127.0.0.1:8000`. It is read on the
server only — do not give it a `NEXT_PUBLIC_` prefix.

## Tests

```bash
npm test         # Vitest: pure logic and the server helpers, with fetch mocked
npm run test:e2e # Playwright: one full journey in a real browser
npm run lint
npx tsc --noEmit
npm run build    # needs no backend — every page reads cookies, so all are dynamic
```

CI (`.github/workflows/frontend.yml`) runs everything except Playwright, which needs
Postgres, uvicorn and seeded opportunities.

**Playwright starts its own Next and uvicorn**, but the Docker database must already be
running, with the dev opportunities loaded (`python -m scripts.seed_opportunities` in
`backend/`). It signs up `e2e-<timestamp>@example.com`, and its teardown deletes every
`e2e-%@example.com` user afterwards.

Its global setup clears `rate_limit_hits` first. Signup is capped at 5 per hour per IP,
so without that the sixth run in an hour fails on "Too many attempts" — which looks like a
broken app but is the backend working as designed. The same applies to manual testing: if
signup starts refusing you locally, that is why.

## Things worth knowing

- **Allowed values live in one place.** Opportunity types, education levels, dismiss
  reasons and notification cadences are in `src/lib/format.ts`; country codes and names are
  in `src/lib/countries.ts`. They mirror `backend/app/models/base.py`. Don't re-declare them.
- **Country names are generated, not looked up with `Intl.DisplayNames`.** Intl's data
  differs between Node and the browser (Node says "Falkland Islands (Islas Malvinas)",
  Chromium says "Falkland Islands"), which is a hydration mismatch in a client component.
  The regeneration command is in the header of `src/lib/countries.ts`.
- **Form-state constants are in `src/lib/form-state.ts`, not in the action files.** A
  `"use server"` module may only export async functions; a plain object exported from one
  arrives as `undefined` on the client.
- **`error.tsx` uses `retry()`, not `reset()`.** `reset()` re-renders without re-fetching,
  so an error thrown during a server render comes straight back.
- **Settings has a "Delete Account" button that does nothing.** There is no endpoint behind
  it yet; Sprint 9 builds `DELETE /account` and wires it up.
