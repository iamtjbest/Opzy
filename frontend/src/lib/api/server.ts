import "server-only";

import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { getToken } from "@/lib/session-cookies";

// Server-side only, so no NEXT_PUBLIC_ prefix: the browser must never learn this.
export const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

// src/proxy.ts stamps this on every request it matches, so a 401 can send the user back
// to the page they were on. See "Deviations from the spec" in the plan.
const PATH_HEADER = "x-opzy-path";

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;
  /** Field name → message, from FastAPI's 422 body. Empty for every other status. */
  readonly fields: Record<string, string>;

  constructor(status: number, detail: string, fields: Record<string, string> = {}) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
    this.fields = fields;
  }
}

type ValidationItem = { loc?: unknown[]; msg?: unknown };

function fieldFrom(loc: unknown[]): string {
  // FastAPI reports ["body", "skills", 0] for an item inside a list; the field is the
  // second element, not the last, which would be the index.
  if (loc[0] === "body" && loc.length > 1) return String(loc[1]);
  return String(loc[loc.length - 1] ?? "form");
}

function toApiError(status: number, body: unknown): ApiError {
  const detail = (body as { detail?: unknown } | null)?.detail;

  if (typeof detail === "string") return new ApiError(status, detail);

  if (Array.isArray(detail)) {
    const fields: Record<string, string> = {};
    for (const item of detail as ValidationItem[]) {
      const loc = Array.isArray(item?.loc) ? item.loc : [];
      const field = fieldFrom(loc);
      // First message per field wins; showing five messages on one input helps nobody.
      if (!(field in fields)) fields[field] = String(item?.msg ?? "Invalid value");
    }
    const first = Object.values(fields)[0] ?? "Please check the form and try again.";
    return new ApiError(status, first, fields);
  }

  return new ApiError(status, `The server returned an unexpected error (${status}).`);
}

async function readBody(response: Response): Promise<unknown> {
  // 204 has no body at all, and an error page from a crashed backend isn't JSON.
  if (response.status === 204) return null;
  try {
    return await response.json();
  } catch {
    return null;
  }
}

async function request<T>(path: string, init: RequestInit, token?: string): Promise<T> {
  const requestHeaders = new Headers(init.headers);
  if (token) requestHeaders.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: requestHeaders,
    // Every response here is per-user. Caching one would serve it to somebody else.
    cache: "no-store",
  });

  const body = await readBody(response);
  if (!response.ok) throw toApiError(response.status, body);
  return body as T;
}

/** The path the browser is on, for the `?next=` on an expired-session redirect. */
async function currentPath(): Promise<string> {
  try {
    return (await headers()).get(PATH_HEADER) ?? "/feed";
  } catch {
    return "/feed";
  }
}

/**
 * Call the API as the logged-in user.
 *
 * A 401 means the token expired or was retired (a password change does that). There is no
 * refresh endpoint, so the answer is to log in again — but a Server Component can't delete
 * a cookie while rendering, and redirecting straight to /login would leave the stale
 * cookie in place for proxy.ts to bounce back to /feed, forever. So it goes through the
 * /session/end route handler, which can delete it. See Decision 3.
 */
export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = await getToken();
  if (!token) redirect(`/session/end?next=${encodeURIComponent(await currentPath())}`);

  try {
    return await request<T>(path, init, token);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      redirect(`/session/end?next=${encodeURIComponent(await currentPath())}`);
    }
    throw error;
  }
}

/**
 * Call the API with no token: signup, login and the two password-reset endpoints. A 401
 * here is "wrong password", not an expired session, so it is thrown like any other error
 * for the form to render.
 */
export async function apiPublic<T>(path: string, init: RequestInit = {}): Promise<T> {
  return request<T>(path, init);
}
