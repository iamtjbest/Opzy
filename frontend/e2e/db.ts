import { execFileSync } from "node:child_process";
import path from "node:path";

// __dirname, not import.meta.url: Playwright loads these files as CommonJS.
const COMPOSE_FILE = path.resolve(__dirname, "../../backend/docker-compose.yml");

/**
 * Run one statement against the local dev database, through Docker Compose.
 *
 * Returns null instead of throwing: housekeeping around the suite must never turn a
 * passing run red, and a developer without Docker up gets a warning, not a failure.
 */
export function psql(statement: string): string | null {
  try {
    return execFileSync(
      "docker",
      [
        "compose",
        "-f",
        COMPOSE_FILE,
        "exec",
        "-T",
        "db",
        "psql",
        "-U",
        "opzy",
        "-d",
        "opzy",
        "-t",
        "-A",
        "-c",
        statement,
      ],
      { encoding: "utf8" },
    ).trim();
  } catch {
    return null;
  }
}

/** Every user this suite has ever created. Everything else cascades from the user row. */
export const E2E_USER_PATTERN = "e2e-%@example.com";

/**
 * Forget every rate-limit counter.
 *
 * Clearing once before the run stopped being enough in Sprint 9: signup is capped at 5 per
 * hour per IP, and the suite now creates six or more accounts in a single run (the journey,
 * the taken-address check, and two in the deletion test). So this is called before each
 * signup rather than only at startup — otherwise a later test fails on "Too many attempts",
 * which looks like a broken app but is the backend working exactly as designed.
 */
export function clearRateLimits(): boolean {
  return psql("delete from rate_limit_hits") !== null;
}

/**
 * Mark an account's address confirmed, standing in for clicking the emailed link.
 *
 * The browser can't do this the real way: only the sha256 of a verification token is
 * stored, so the token exists nowhere but the email itself. The /verify-email page's own
 * behaviour is covered separately with a token that was never issued.
 */
export function verifyUser(email: string): void {
  const result = psql(
    `update users set email_verified_at = now() where email = '${email}'`,
  );
  if (result === null) {
    throw new Error(`e2e: couldn't mark ${email} verified — is the dev database up?`);
  }
}
