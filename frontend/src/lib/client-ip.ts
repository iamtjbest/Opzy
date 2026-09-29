/**
 * The browser's address, from the X-Forwarded-For this server received, or null.
 *
 * Next.js fills X-Forwarded-For with the socket address only when the header is missing,
 * and keeps whatever a client sent otherwise, so the leftmost entries are the client's to
 * invent. Count from the right instead: the last `trustedHops` entries were appended by
 * proxies we run (Vercel's edge, an nginx in front, or Next itself locally), and the
 * leftmost of those is the address they saw. A header shorter than that didn't come
 * through the expected chain, so give up rather than trust client-supplied text.
 *
 * Mirrors `client_ip` in backend/app/core/rate_limit.py.
 */
export function pickClientIp(
  forwardedFor: string | null | undefined,
  trustedHops: number,
): string | null {
  if (!forwardedFor || !Number.isInteger(trustedHops) || trustedHops < 1) return null;
  const hops = forwardedFor
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
  if (hops.length < trustedHops) return null;
  return hops[hops.length - trustedHops];
}

/** TRUSTED_PROXY_HOPS from the environment: how many proxies stand in front of Next. */
export function trustedHopsFromEnv(value: string | undefined): number {
  const parsed = Number(value ?? "1");
  return Number.isInteger(parsed) && parsed >= 1 ? parsed : 1;
}
