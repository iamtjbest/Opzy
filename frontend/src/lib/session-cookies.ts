import "server-only";

import { cookies } from "next/headers";

import { SESSION_COOKIE, sessionCookieOptions } from "@/lib/session";

/** The backend JWT, or undefined when there is no session. Safe to call while rendering. */
export async function getToken(): Promise<string | undefined> {
  return (await cookies()).get(SESSION_COOKIE)?.value;
}

/**
 * Store the token. Only callable from a Server Action or a Route Handler — HTTP can't set
 * a cookie once rendering has started streaming.
 */
export async function setSession(token: string): Promise<void> {
  (await cookies()).set(SESSION_COOKIE, token, sessionCookieOptions());
}

/** Drop the session. Same Server-Action-or-Route-Handler restriction as setSession. */
export async function clearSession(): Promise<void> {
  (await cookies()).delete(SESSION_COOKIE);
}
