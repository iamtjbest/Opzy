import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { safeNext } from "@/lib/session";
import { clearSession } from "@/lib/session-cookies";

/**
 * The one place a stale session is thrown away.
 *
 * A Server Component can't delete a cookie mid-render, and a plain redirect to /login
 * would leave the dead cookie sitting there — which proxy.ts would read as "logged in"
 * and bounce straight back to /feed, which would 401 again, forever. A route handler can
 * delete it, so the loop can't start.
 */
export async function GET(request: NextRequest) {
  await clearSession();

  const next = safeNext(request.nextUrl.searchParams.get("next"));
  const target = new URL("/login", request.url);
  if (next) target.searchParams.set("next", next);

  return NextResponse.redirect(target);
}
