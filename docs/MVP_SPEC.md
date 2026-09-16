# MVP Specification — Opportunity Engine

**Status:** Draft v1, following the locked GO decision in `PRODUCT_THESIS.md`.
**Last updated:** Sept 14, 2026.

---

## Product Definition

**One-line description:** A personalized opportunity discovery platform that continuously
finds the jobs, internships, scholarships, fellowships, grants, hackathons, and other
opportunities a specific person is eligible for and actually cares about — and tells them
in plain language why.

**Problem statement:** Nigerian students, graduates, and early-career professionals can't
efficiently find opportunities that are relevant to them and that they qualify for, because
opportunities are scattered across many disconnected channels and eligibility, timing, and
legitimacy are all unclear.

**Target audience (initial):** Nigerian university students, recent graduates, and
early-career professionals — heavy tech/software skew in the validated sample, but the
taxonomy should not assume tech-only.

**Core promise:** Never miss an opportunity that fits you.

**Positioning:** A personal opportunity radar — not a job board, not a scholarship directory,
not a general-purpose AI chatbot. The wedge is discovery + eligibility + explanation, not
listing volume.

**Initial opportunity categories:** Jobs (full-time, part-time, remote), internships,
scholarships, fellowships, grants, hackathons, competitions. Training, research, and
accelerator programs follow once the core loop is proven.

**Initial geography:** Nigeria. Expansion path: West Africa → Africa → other emerging
markets, in that order, once the core matching loop works well in one market.

**Primary success metric:** Meaningful opportunities acted upon per active user — do people
return because they don't want to miss something, and do they actually save/click/apply,
not just view.

---

## MVP Scope

- Authentication (email-based to start)
- Onboarding / profile: education level, field, skills, experience level, location,
  interested opportunity types, preferences — kept as short as possible to avoid drop-off
- Opportunity database, sourced manually/semi-automatically at first
- Deterministic eligibility screening (hard constraints only — see Eligibility Model)
- Personalized feed: match score **+ plain-language explanation** for every recommendation
- Save / dismiss / mark-as-applied actions, with basic application tracking
- Notifications: email first, WhatsApp as a close second priority
- **Notification cadence as a user setting** (instant / daily / weekly) — interview
  follow-ups showed this preference is genuinely mixed across people, not a single default
- Basic admin: review queue for newly ingested opportunities before they go live

## Non-MVP (explicitly deferred)

- Native mobile apps
- Recruiter marketplace / employer dashboard
- Resume builder
- Complex ML-based ranking (start with transparent, deterministic + simple scoring)
- WhatsApp automation beyond basic notifications
- Auto-apply / stored-profile submission — two interview respondents independently raised
  this (one as a pain point, one as an explicit feature request); real signal, but it's a
  post-MVP roadmap item, not a v1 feature
- 20+ opportunity categories — start narrow, expand once the core loop works

---

## Core User Journey

```
LANDING PAGE
     ↓
SIGN UP
     ↓
CREATE PROFILE (short — education, field, skills, experience, location, interests)
     ↓
SELECT OPPORTUNITY TYPES
     ↓
SYSTEM FINDS OPPORTUNITIES
     ↓
PERSONALIZED FEED (match score + explanation)
     ↓
VIEW OPPORTUNITY DETAILS
     ↓
SAVE / APPLY / DISMISS
     ↓
RECEIVE FUTURE MATCHES (per chosen cadence)
     ↓
FEEDBACK (was this relevant? were you eligible? did you apply?)
```

Key loop: **Discover → Understand → Match → Rank → Explain → Act → Track → Learn**

## MVP Screens

**Public:** Landing page, About, FAQ, Login, Signup
**User:** Onboarding, Profile, Opportunity feed, Opportunity details, Saved opportunities,
Applications, Notifications settings (including cadence)
**Admin:** Dashboard, Opportunities, Sources, Review queue, Users

Keep the first implementation of each minimal — this is a scope list, not a design spec.

---

## Data Model (conceptual)

**Users:** User, Profile, Skills, Education, Experience, Preferences

**Opportunities:** Opportunity, OpportunitySource, Organization, OpportunityCategory,
EligibilityRequirement, Location, Deadline, ApplicationLink

**User activity:** SavedOpportunity, Application, DismissedOpportunity, Notification,
UserFeedback, OpportunityOutcome

**Intelligence:** OpportunityMatch, MatchReason, RecommendationScore

The final schema should stay derived from this MVP scope rather than implementing every
entity immediately (e.g., OpportunityEmbedding / semantic search can wait).

### Opportunity data contract (core fields)

`id, title, organization, category, description, country, eligible_countries, location,
remote, opportunity_type, education_level, field, skills, experience_level,
age_requirement, deadline, application_url, source_url, source, published_date, status,
eligibility, required_documents, tags, created_at, updated_at`

Open questions to resolve during build: which fields are mandatory vs optional, which need
AI extraction vs deterministic entry, how missing values are represented, how expired
opportunities are handled, how duplicates are detected.

---

## Eligibility Model

Distinguish clearly between:

- **Hard constraints** (deterministic, block a match if failed): country eligibility, age
  requirement, education requirement, deadline, citizenship, required experience
- **Soft signals** (influence ranking, don't block): skills, interests, career direction,
  preferred industry, preferred location

AI can assist with *interpreting* eligibility language, but should not be the sole authority
on hard eligibility — get those checks deterministic wherever possible. This matters more
than it might otherwise, since eligibility uncertainty is the single most-named pain point
in the validation data.

## Matching & Ranking Model

```
Eligibility (hard constraints)
     ↓
Relevance (field, skills, experience match)
     ↓
Preference (opportunity type, location)
     ↓
Ranking
     ↓
Explanation
```

Don't lock numerical weights until real usage data exists. Every recommendation should be
explainable in plain language, e.g.: *"Recommended because you're a Nigerian Computer
Engineering student with Python experience, and this opportunity accepts Nigerian
undergraduate applicants."*

**Trust note from interviews:** an instant, highly-confident match can itself read as
suspicious if it isn't paired with a visible explanation ("this looks too obvious, the
authenticity starts to get sketchy" — one respondent). Explanation isn't just a nice UX
touch here, it's load-bearing for trust.

---

## Notifications

**Types:** strong new match, new opportunity, deadline approaching, saved-opportunity
reminder, application follow-up.

**Channels:** email first (matches the largest stated preference), WhatsApp next.

**Cadence:** make this a user setting from day one — instant / daily / weekly. The original
survey majority favored instant (20/25), but 4 interview follow-ups split three ways
(2 toward weekly, 1 toward instant, 1 to daily), for reasons ranging from feeling overwhelmed
to needing time to prepare a tailored application. Don't hard-code one default as the only
option.

---

## Concierge MVP (do this before/alongside the software build)

Per the original readiness plan — and now more valuable given TjBest's own read that further
survey/interview replies are unlikely:

- **Target:** 8–10 early users, prioritizing the respondents who gave contact info, rated
  the concept highly, and said yes to testing.
- **For each:** collect a short profile (skills, education, location, interests, opportunity
  types wanted).
- **Manually send 5–10 personalized opportunities per person** over WhatsApp/email — real
  opportunities, hand-picked to fit what they told you.
- **Track:** opened, saved, clicked, applied, dismissed, marked "not eligible," marked
  "irrelevant."
- **Questions this answers:** Are the recommendations actually relevant? Do people discover
  something they'd otherwise miss? Do they act on it? Do they come back and ask for more?

A strong concierge result here is worth more than any additional survey responses at this
point — it's the first real behavioral evidence, and it can start immediately without
waiting on any technical build.

---

## Early Phase — what "testable" actually means

Since real testers are ready now, the target isn't the full MVP scope above — it's the
smallest real, working slice of the product loop: **sign up → tell us about yourself → see
opportunities picked for you, with a reason → do something about it.** Everything else in
the MVP scope can come after this loop is proven with real users.

**What must exist (v0 / Alpha):**
- Signup (email is enough — skip social login for now)
- Short profile form: education level, field, skills (free text/tags), location,
  opportunity types interested in — this replaces the manual "collect a profile" step from
  the concierge plan with a real, reusable form
- A seeded opportunity database — manually entered at first (10–30 real opportunities is
  plenty to start), not an automated ingestion pipeline
- Matching logic v0: deterministic only — filter by hard eligibility (country, education
  level, deadline not passed), then a simple relevance score (field match, skill overlap).
  No ML needed yet.
- The feed screen: each match shows a score/reason in plain language — this is the single
  most important screen, since explanation is what interview data showed is load-bearing
  for trust, not optional polish
- Opportunity detail view (full description, deadline, application link)
- Save / Dismiss / Mark-as-applied actions
- One notification channel (email), simple cadence choice (even just instant vs. weekly to
  start — daily can come later)

**What can wait past this phase:**
- Admin UI (you can seed/manage opportunities directly in the database or a simple internal
  spreadsheet-to-DB script for now — doesn't need a built interface yet)
- WhatsApp notifications
- Full landing page copy/marketing site (testers can go straight to a signup link)
- Analytics dashboards, feedback forms beyond a simple reaction
- Any of the "Not in MVP" list from above

**Screens to prioritize in Figma, in this order:**
1. Signup / login
2. Profile creation (the questions above, kept short — interview data flagged onboarding
   length as a real drop-off risk)
3. **Opportunity feed** — the core screen, worth spending the most design time here
4. Opportunity detail
5. Saved / applications list
6. A lightweight settings screen (just notification cadence for now)

Admin and landing page can come later — they don't block a real tester from experiencing
the core loop.

---

## Source Strategy (starting point)

Track in a simple sheet: source, URL, category, geography, opportunity types, update
frequency, whether deadline/eligibility info is available, application URL, collection
method/difficulty, and a source quality rating (official org ★★★★★ down to unverified ★☆☆☆☆).
Start with a short list of official/established sources you can check manually — don't build
scraping infrastructure before the concierge test validates that curated recommendations
actually land.

---

## Not Decided Yet (deliberately left open)

- Product name and brand (still "Opportunity Engine" as a working name)
- Exact monetization pricing
- Hosting/infrastructure choice
- Whether/when to add Telegram or push notifications

These don't block starting the concierge test or early technical setup, and shouldn't be
allowed to stall it.
