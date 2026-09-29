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
| notification_cadence | enum(instant, daily, weekly, off) | matches Settings screen, default 'daily'; 'off' sends no emails |
| notification_channel | enum(email, whatsapp) | default 'email' |

## profiles

One-to-one with `users`. Matches the Onboarding screen fields exactly.

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK -> users.id | |
| nationality | text, nullable | ISO 3166 alpha-2, e.g. "NG"; matched against opportunities.eligible_countries |
| education_level | text, nullable | secondary / undergraduate / graduate / postgraduate (CHECK) |
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
| eligible_countries | text[], default '{}' | ISO alpha-2 codes; empty = any country. Hard constraint. |
| education_levels | text[], default '{}' | secondary / undergraduate / graduate / postgraduate; empty = any level. Hard constraint. |
| fields_of_study | text[], default '{}' | e.g. "Computer Science"; empty = any field. Ranking only. |
| skills | text[], default '{}' | e.g. "Python"; empty = none listed. Ranking only. |
| application_url | text | |
| source_url | text | where it was found |
| quality_rating | integer (1-5) | matches sheet's star rating |
| verified | boolean | matches sheet's Verified? column, default false |
| status | enum(active, expired, removed) | default 'active' |
| created_at | timestamp | |
| updated_at | timestamp | |

**Structured eligibility (Sprint 4):** country and education level are real columns because
the matching engine filters on them deterministically; `eligibility_notes` stays as free
text for everything else (age, experience, documents) and is never parsed for matching.
Age and experience can become columns the same way once matching needs them.

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

## match_notifications

One row per opportunity emailed to a user as a new strong match (Sprint 6). The unique
index on (user_id, opportunity_id) means a match is never emailed twice. The user's latest
`sent_at` is when they were last emailed, which is what daily and weekly digests are
timed from.

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK -> users.id | cascade delete |
| opportunity_id | uuid, FK -> opportunities.id | cascade delete |
| score | integer | the match score when it was emailed |
| sent_at | timestamp | when the email went out |

## user_opportunity_actions

Matches the Save/Dismiss/Mark-applied actions on the Feed, Detail, and Saved & Applications
screens. One row per action, not one column per state, so the history isn't lost if someone
saves, then later dismisses. A user's **current state** for an opportunity is its most
recent row (`created_at`, then `id`). Removing a saved item writes an `unsaved` row, which
leaves no current state.

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK -> users.id | |
| opportunity_id | uuid, FK -> opportunities.id | |
| action | enum(saved, unsaved, dismissed, applied) | `unsaved` added in Sprint 5 |
| dismiss_reason | text, nullable | matches the "Not for you? Tell us why" link on the detail screen. The API only accepts `not_relevant`, `pay_too_low`, `not_eligible`, `not_interested_org`, `other` |
| created_at | timestamp | |

**Indexes:** `user_id`, `opportunity_id`, `user_id, opportunity_id, created_at` (latest action lookup)

---

## What this does and doesn't cover

**Covers:** everything needed for the screens already built, sign up/login, onboarding,
a personalized feed with score and reasons, opportunity detail, save/dismiss/apply
tracking, and notification settings.

**Doesn't cover yet, on purpose:** admin/review workflow tables (not needed while you're
entering opportunities by hand from the tracking sheet), anything for automated
ingestion/scraping (not being built yet, per the earlier decision to keep sourcing manual),
and structured eligibility rules beyond free text (see note above).
