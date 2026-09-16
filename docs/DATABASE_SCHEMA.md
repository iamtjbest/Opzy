# Database Schema (v1) — Opzy

**Status:** Draft, stack-agnostic. Written to match the screens already built in Figma and
the fields in `OPZY_SOURCE_TRACKING.xlsx`, so seeding and the onboarding form line up
exactly with no translation step needed. Works on Postgres regardless of host
(Railway, Render, Supabase all fine).

---

## users

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| email | text, unique | |
| password_hash | text | |
| created_at | timestamp | |
| notification_cadence | enum(instant, daily, weekly) | matches Settings screen, default 'daily' |
| notification_channel | enum(email, whatsapp) | default 'email' |

## profiles

One-to-one with `users`. Matches the Onboarding screen fields exactly.

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK -> users.id | |
| education_level | text | e.g. "University student" |
| field_of_study | text | e.g. "Computer Engineering" |
| location | text | e.g. "Zaria, Kaduna" |
| updated_at | timestamp | |

## profile_skills

Many-to-many, since skills are a tag list in onboarding, not a single field.

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| profile_id | uuid, FK -> profiles.id | |
| skill | text | e.g. "Python" |

## profile_interests

Matches the "What are you looking for?" multi-select on onboarding.

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| profile_id | uuid, FK -> profiles.id | |
| opportunity_type | enum(job, internship, scholarship, fellowship, grant, hackathon, competition) | |

## opportunities

Matches the columns in `OPZY_SOURCE_TRACKING.xlsx` directly, so the sheet maps to this
table with almost no transformation.

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| title | text | |
| organization | text | |
| category | enum(job, internship, scholarship, fellowship, grant, hackathon, competition) | |
| geography | text | e.g. "Nigeria", "Lagos", "ECOWAS region" |
| description | text | |
| deadline | date, nullable | null means rolling/unconfirmed, matches sheet's "NOT CONFIRMED" rows |
| eligibility_notes | text | free text for now, matches sheet |
| application_url | text | |
| source_url | text | where it was found |
| quality_rating | integer (1-5) | matches sheet's star rating |
| verified | boolean | matches sheet's Verified? column, default false |
| status | enum(active, expired, removed) | default 'active' |
| created_at | timestamp | |
| updated_at | timestamp | |

**Deliberately not yet split out:** structured eligibility rules (country, age, education
level as separate filterable fields). Free-text `eligibility_notes` is enough for the first
10-30 manually-entered opportunities. Splitting it into real filterable columns is worth
doing once there's enough volume that free-text matching stops being good enough, not before.

## opportunity_matches

The output of the matching logic, one row per user/opportunity pair that was scored.

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK -> users.id | |
| opportunity_id | uuid, FK -> opportunities.id | |
| match_score | integer (0-100) | matches the "92% match" badge shown in the feed |
| match_reasons | text[] | short phrases, matches the reason chips shown in the feed and detail screen |
| created_at | timestamp | |

## user_opportunity_actions

Matches the Save/Dismiss/Mark-applied actions on the Feed, Detail, and Saved & Applications
screens. One row per action, not one column per state, so the history isn't lost if someone
saves, then later dismisses.

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK -> users.id | |
| opportunity_id | uuid, FK -> opportunities.id | |
| action | enum(saved, dismissed, applied) | |
| dismiss_reason | text, nullable | matches the "Not for you? Tell us why" link on the detail screen |
| created_at | timestamp | |

---

## What this does and doesn't cover

**Covers:** everything needed for the screens already built, sign up/login, onboarding,
a personalized feed with score and reasons, opportunity detail, save/dismiss/apply
tracking, and notification settings.

**Doesn't cover yet, on purpose:** admin/review workflow tables (not needed while you're
entering opportunities by hand from the tracking sheet), anything for automated
ingestion/scraping (not being built yet, per the earlier decision to keep sourcing manual),
and structured eligibility rules beyond free text (see note above).
