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
