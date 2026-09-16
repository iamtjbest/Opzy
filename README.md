# Opzy

Never miss an opportunity that fits you.

A personalized opportunity discovery platform for Nigerian students, graduates, and
early-career professionals, jobs, internships, scholarships, fellowships, grants,
hackathons, and competitions, matched to what you're actually eligible for and explained
in plain language.

## Status

Pre-build. Product validated (survey + interviews), all screens designed in Figma,
database schema live in Supabase with the first seed data in. Backend and frontend
build starting now.

## Stack

- **Frontend:** Next.js / React / TypeScript
- **Backend:** FastAPI / Python
- **Database:** Postgres via Supabase (schema and seed data already live)

## Structure

```
/frontend   Next.js app
/backend    FastAPI app
/docs       Product thesis, MVP spec, database schema, design system
```

## Getting started

1. Clone the repo
2. Copy `.env.example` to `.env` in both `/frontend` and `/backend`, fill in the Supabase
   credentials (ask in the group chat if you don't have them)
3. See `/docs` for full context before writing code, especially `MVP_SPEC.md` for what's
   in scope for v1 and `DATABASE_SCHEMA.md` for the table structure already live

## Docs

- `docs/PRODUCT_THESIS.md`, the problem, evidence, and why this is being built
- `docs/MVP_SPEC.md`, exact scope: what's in v1, what's deliberately deferred
- `docs/DATABASE_SCHEMA.md`, table structure (matches `schema.sql`, already run in Supabase)
- `docs/DESIGN_SYSTEM.md`, colors, type, and brand mark
- `docs/schema.sql` / `docs/seed.sql`, the actual SQL already live in the Supabase project

Figma file (all screens, designed and ready): [add the link here]
