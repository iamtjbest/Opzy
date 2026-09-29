/**
 * The rules for the landing page's early-access list, kept apart from the route handler
 * so they can be tested without a filesystem.
 */

export const MAX_BODY_BYTES = 1024;
// RFC 5321's limit on a whole address.
export const MAX_EMAIL_LENGTH = 254;
// The list is a file on the server's disk. Past this, stop writing rather than let a
// flood of addresses fill the disk.
export const MAX_FILE_BYTES = 1024 * 1024;

export const PER_IP_LIMIT = 5;
export const PER_IP_WINDOW_MS = 60 * 60 * 1000;

// Deliberately narrow. The file is a CSV that gets opened in a spreadsheet, so an address
// must not be able to carry quotes or commas (breaking out of its cell) or begin with
// = + - @ (which a spreadsheet runs as a formula). Starting with a letter or digit, and
// allowing no quotes anywhere, rules out both.
const EMAIL_PATTERN = /^[a-z0-9][a-z0-9._%+-]*@[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)*\.[a-z]{2,}$/;

/** The address to store, lowercased and trimmed, or null if it isn't acceptable. */
export function normalizeEarlyAccessEmail(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const email = value.trim().toLowerCase();
  if (email.length === 0 || email.length > MAX_EMAIL_LENGTH) return null;
  return EMAIL_PATTERN.test(email) ? email : null;
}

/** One CSV row. Only ever given an address normalizeEarlyAccessEmail accepted. */
export function csvLine(email: string, at: Date): string {
  return `"${email}","${at.toISOString()}"\n`;
}

/** Whether the file already lists this address. */
export function alreadyListed(csv: string, email: string): boolean {
  return csv.split("\n").some((line) => line.startsWith(`"${email}",`));
}

/**
 * A per-IP fixed window, in memory. Good enough for a sign-up form: it resets on restart
 * and isn't shared between instances, but it stops one client hammering the endpoint.
 */
export class WindowLimiter {
  private readonly hits = new Map<string, { start: number; count: number }>();

  constructor(
    private readonly limit: number,
    private readonly windowMs: number,
    // Bounded, so the map itself can't be grown without limit by a spread of addresses.
    private readonly maxKeys = 10_000,
  ) {}

  /** Count one attempt; false if the key is over its limit. */
  allow(key: string, now: number): boolean {
    const entry = this.hits.get(key);
    if (!entry || now - entry.start >= this.windowMs) {
      if (!entry && this.hits.size >= this.maxKeys) this.prune(now);
      if (!entry && this.hits.size >= this.maxKeys) return false;
      this.hits.set(key, { start: now, count: 1 });
      return true;
    }
    entry.count += 1;
    return entry.count <= this.limit;
  }

  private prune(now: number): void {
    for (const [key, entry] of this.hits) {
      if (now - entry.start >= this.windowMs) this.hits.delete(key);
    }
  }
}
