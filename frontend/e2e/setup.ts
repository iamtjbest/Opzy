import { clearRateLimits } from "./db";

/**
 * Clear the rate limiter before the run.
 *
 * Sprint 7 caps signups at 5 per hour per IP, and this suite signs up a fresh user every
 * time. Without this, the sixth local run inside an hour fails on "Too many attempts" —
 * which looks like a broken app but is the backend working exactly as designed.
 *
 * Only ever run against the local Docker database. Never point this at anything shared.
 */
export default function setup() {
  if (!clearRateLimits()) {
    console.warn(
      "e2e setup: couldn't clear rate_limit_hits. If signup fails with 'Too many " +
        "attempts', that is why — wait an hour or start the Docker database.",
    );
  }
}
