# Backend

FastAPI app goes here. Not scaffolded yet.

Database is already live in Supabase, schema matches `../docs/DATABASE_SCHEMA.md` and
`../docs/schema.sql`. Connect via `DATABASE_URL` in `.env`.

Core endpoints needed for v1 (see `../docs/MVP_SPEC.md`):
- Auth (sign up / log in)
- Profile (create/update, matches the onboarding fields)
- Opportunities (list/filter, matches the feed + detail screens)
- User actions (save / dismiss / mark applied)
- Matching logic (deterministic: eligibility filter + relevance score, no ML yet)
