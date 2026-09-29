import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { SESSION_COOKIE } from "@/lib/session";

// Pages that need a logged-in user. Children are protected too.
const PROTECTED = [
  "/feed",
  "/opportunities",
  "/saved",
  "/applications",
  "/settings",
  "/onboarding",
] as const;

// Pages there is no point showing someone who is already logged in.
const LOGGED_OUT_ONLY = ["/login", "/signup"] as const;

// apiFetch reads this to build the ?next= on an expired-session redirect.
const PATH_HEADER = "x-opzy-path";

function isProtected(pathname: string): boolean {
  // Exact match or a child — so /feedback is not /feed.
  return PROTECTED.some((base) => pathname === base || pathname.startsWith(`${base}/`));
}

/**
 * Where this request should be sent instead, or null to let it through.
 *
 * An optimistic check only, exactly as the Next.js authentication guide advises: it looks
 * at whether a cookie exists, never at whether the token in it is any good. The real
 * check is the backend's 401, which apiFetch turns into /session/end.
 *
 * Exported separately from the proxy so it can be tested without building a NextRequest.
 */
export function route(pathname: string, hasSession: boolean): string | null {
  if (!hasSession && isProtected(pathname)) {
    return `/login?next=${encodeURIComponent(pathname)}`;
  }
  if (hasSession && (LOGGED_OUT_ONLY as readonly string[]).includes(pathname)) {
    return "/feed";
  }
  return null;
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = request.cookies.has(SESSION_COOKIE);

  const destination = route(pathname, hasSession);
  if (destination) {
    return NextResponse.redirect(new URL(destination, request.url));
  }

  // Pass the pathname along so server code fetching for this page knows where it is.
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set(PATH_HEADER, pathname);
  return NextResponse.next({ request: { headers: requestHeaders } });
}

export const config = {
  // `:path*` matches zero or more segments, so "/feed" and "/feed/anything" both match.
  // /session/end is deliberately absent: it has to run for a user whose cookie is stale.
  matcher: [
    "/feed/:path*",
    "/opportunities/:path*",
    "/saved/:path*",
    "/applications/:path*",
    "/settings/:path*",
    "/onboarding/:path*",
    "/login",
    "/signup",
  ],
};
