# Product Thesis — Opportunity Engine

**Status:** 🟢 GO — locked.
**Last updated:** Sept 14, 2026, after 25 survey responses + 6 partial interviews.
**Owner:** TjBest

---

## Problem

Nigerian students, graduates, and early-career professionals cannot efficiently find the
specific opportunities (jobs, internships, scholarships, fellowships, grants, hackathons,
competitions, etc.) that are actually relevant to them and that they qualify for — because
opportunities are scattered across many disconnected channels, and it is often unclear who
is eligible and when something closes.

It is not "I can't find jobs." It is: *"I don't know which opportunities exist, which ones
matter to me, whether I can actually apply, and when I need to act."*

## User

Primary: Nigerian university students, recent graduates, and early-career professionals —
especially in tech/software and engineering — roughly 18–30 years old, who are already
actively searching for opportunities most days or several times a week.

*(Current survey sample skews toward this exact group — 17/25 university students, 17/25
tech/software, 100% Nigeria — which matches the intended beachhead but hasn't yet been
tested outside it.)*

## Current Behaviour

They check anywhere from 2 to 10+ sources per search cycle — LinkedIn, Google, WhatsApp
groups, Telegram, X, university groups, Jobberman/MyJobMag/Indeed, GitHub/dev communities,
and friends/referrals — spending mostly 30 minutes to 3 hours a week on it (a minority spend
5+ hours). Friends/referrals and LinkedIn are the two most common discovery channels (15/22
each), ahead of any single job board.

## Pain

Ranked by how often each was named as the single **biggest** problem (n=25):

| Problem | Respondents |
|---|---|
| Knowing whether I'm eligible | 6 |
| Finding opportunities early enough | 5 |
| Finding relevant opportunities | 5 |
| Verifying legitimacy | 3 |
| Knowing what's worth my time | 2 |
| Other (one place, tracking, completing) | 4 |

Three things stand out beyond the table:
- **Eligibility uncertainty** is the single most-named biggest problem, and 12/25 said they
  don't know if they're actually eligible for things they find. This looks like the sharpest
  wedge, not a secondary feature.
- **Lateness/deadlines dominate the concrete stories.** When asked to describe an opportunity
  they actually missed, most described being late, missing a deadline, or a deadline that
  wasn't clearly stated — even though "finding opportunities early enough" alone wasn't
  always the label people picked when forced into one category. The lived pain is more
  timing-driven than the checkbox breakdown alone suggests.
- **Legitimacy/trust is a real, named concern** (3/25 biggest problem, 8/25 experienced it),
  and follow-up interviews added a sharper nuance: an instant, well-matched alert can itself
  *trigger* suspicion ("looking very obvious... the authenticity starts to get sketchy" — one
  respondent). Speed needs to be paired with visible explanation, or it undermines the trust
  it's meant to build.

**Emerging from interviews, not yet in the survey — application-completion friction.**
Two independent respondents raised a problem outside the four above: the application itself
being long, document-heavy, or exhausting. One described nearly abandoning a 10-essay
scholarship application partway through; another spontaneously proposed a stored-profile
auto-apply feature. Discovery wasn't the failure point in either story — follow-through was.
Treated as a secondary problem, worth a line in the roadmap rather than the MVP itself.

## Existing Alternatives

General job boards (Jobberman, MyJobMag, HotNigerianJobs, Indeed), LinkedIn, Wellfound,
Opportunity Desk, informal community channels (WhatsApp/Telegram/X/university groups), and
increasingly, asking an AI chatbot directly. None combine personalized matching + eligibility
screening + deadline intelligence + explanation in one place — most either leave the
filtering work to the user or cover one narrow category.

## Hypothesis

A system that builds a persistent profile per user, continuously discovers opportunities
from many sources, screens them against eligibility rules, ranks by relevance, and explains
*why* each one matches — delivered close to real time rather than as a digest — will get
people to check it habitually and act on more of the opportunities that actually fit them,
because it directly attacks the three problems named most: not knowing if they qualify,
seeing things too late, and drowning in irrelevant listings.

## Evidence

**For:**
- 25 survey responses total; 21/25 rated the concept 4–5/5 on usefulness; 21/25 said
  "definitely" they'd try a free version; 20/25 want to test an early version.
- 20/25 (survey) wanted opportunities instantly rather than a digest — but 6 async/interview
  follow-ups complicated this (see below), so treat the underlying preference as real but
  not uniform.
- 21/25 agree/definitely agree they'd consider paying if it consistently helps (stated,
  not observed, willingness).
- 6 of 25 respondents gave async follow-up answers (full notes in `INTERVIEW_NOTES.md`).
  One gave a detailed, specific behavioural story (a real application he nearly abandoned
  partway through) — the closest thing to observed behaviour collected so far, even though
  it's recalled rather than watched directly.
- One friend, after seeing the full material, is ready to work on this with TjBest (not
  just interested) — an informal team signal, separate from product validation.

**Against / still open:**
- Still no directly-observed behaviour — no one has used even a manual/concierge version yet;
  what we have is detailed recall, which is stronger than a survey checkbox but not the same.
- Sample is small (25) and drawn from TjBest's own network, skewed toward university
  students in tech — strong fit for the intended beachhead, but not yet evidence the pain
  generalizes further.
- Willingness to pay is hypothetical.
- Cadence preference turned out to be less settled than the survey majority suggested: of
  4 interview respondents who addressed it, 2 flipped toward weekly, 1 flipped toward
  instant, 1 softened to daily. Genuinely mixed, not a converging signal — see MVP note below.
- Remaining respondents from the interview round are unlikely to reply further; the decision
  below treats the current sample as close to final for this validation round.

## MVP

Web app with: authentication; user profile (education, skills, experience, preferences,
eligibility info); opportunity database (manually/semi-automatically sourced at first);
deterministic eligibility checks; personalized feed with a match score **and** a plain-language
explanation; save / dismiss / mark-applied; basic notifications (email first, per stated
channel preference, WhatsApp as a close second). **Notification cadence should be a simple
user setting (instant / daily / weekly) rather than hard-coded to real-time** — interview
follow-ups showed this preference is genuinely mixed, not converging on one default.

Not in MVP: native mobile apps, recruiter marketplace, employer dashboard, resume builder,
complex ML ranking, WhatsApp automation, 20+ categories, auto-apply/stored-profile submission
(flagged by two interview respondents independently — worth keeping on the post-MVP roadmap).

## Success Metric

Primary candidate: **meaningful opportunities acted upon per active user** — i.e., do people
return because they don't want to miss something, and do they actually save/click/apply, not
just view. Early-stage proxy (concierge/interview phase): do respondents open, save, and
apply to hand-picked recommendations, and do they ask for the next batch?

## Monetization

Freemium: free basic feed + limited recommendations; Pro (hypothesis: ₦2,000–₦7,000/month)
for deeper personalization, unlimited tracking, advanced alerts, eligibility analysis. Later,
B2B (sponsored/verified listings, institutional partnerships) — paid placement must never
quietly override relevance ranking, since trust is the core asset.

## Moat

Not the AI itself. Potential durable advantages: structured opportunity database, eligibility
intelligence, persistent user profiles, behavioural and outcome data, verification/trust, and
distribution through communities that come to rely on it.

## Risks

- Aggregation alone is easy to copy → counter with personalization, data quality, outcomes.
- Bad recommendations destroy trust fast — now more clearly true, given legitimacy is a named
  concern for a meaningful share of respondents.
- Users don't return if the feed doesn't stay sharp → counter with strong feedback loop.
- "Why not just ask ChatGPT?" is a real competitive question → answer with persistent profile,
  structured verified data, and continuously running discovery, not "our AI is better."
- Small, network-sourced sample may overstate true demand beyond TjBest's own circles.
- Monetization could damage trust if paid listings corrupt ranking.

## Current Decision

**🟢 GO.** Locked Sept 14, 2026.

The signal has been consistent from 13 → 22 → 25 survey responses and across 6 partial
interviews: eligibility, timing/lateness, and relevance are recurring, named, costly
problems, with legitimacy as a real fourth concern. One interview produced a detailed,
specific behavioural story rather than pure stated interest. Remaining interview replies
are unlikely to arrive in meaningful numbers, so this is treated as close to final for this
validation round rather than something to keep waiting on.

This is not a claim that every open question is answered — sample size and diversity remain
thin, willingness to pay is still hypothetical, and cadence preference turned out to be more
mixed than the survey majority suggested. But per the original decision framework, none of
the PIVOT or STOP conditions are met (no wrong-solution signal, no dominant single category,
no weak interest despite pain), and enough of the GO conditions are: a clear recurring
problem, fragmented current behaviour, strong usefulness ratings, real intent to test, and a
plausible monetization path.

**Next step:** freeze the MVP scope (see `MVP_SPEC.md`) and start the concierge test —
manually send curated opportunities to the highest-signal respondents — in parallel with
name/brand and technical setup. Remaining survey/interview replies still get logged in
`INTERVIEW_NOTES.md` if they arrive, but are no longer a blocker to moving forward.
