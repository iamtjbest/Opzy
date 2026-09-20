export const SESSION_COOKIE = "opzy_session";

// The backend's access token lasts 60 minutes (backend/app/core/security.py), so the
// cookie is given exactly that. httpOnly is the point of the whole design: an XSS bug in
// the app can't read the token, because JavaScript never can.
export function sessionCookieOptions() {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 3600,
  };
}

/**
 * The `?next=` value, if it is safe to redirect to, otherwise null.
 *
 * Only a single-slash-prefixed same-site path passes. "//evil.com" is protocol-relative
 * and would leave the site; "https://evil.com" plainly would; a leading backslash is read
 * as a slash by some browsers. Anything rejected leaves the caller to use its own default.
 */
export function safeNext(value: string | null | undefined): string | null {
  if (!value) return null;
  if (!value.startsWith("/")) return null;
  if (value.startsWith("//") || value.startsWith("/\\")) return null;
  return value;
}
