"use server";

import { redirect } from "next/navigation";

import { ApiError, apiFetch, apiPublic } from "@/lib/api/server";
import type { Profile, SignupResponse, TokenResponse } from "@/lib/api/types";
import type { FormState } from "@/lib/form-state";
import { safeNext } from "@/lib/session";
import { clearSession, setSession } from "@/lib/session-cookies";

function failure(error: unknown, fallback: string): FormState {
  // An ApiError is the backend saying no, which the form renders. Anything else — a
  // redirect thrown by next/navigation, a network failure — belongs to the framework or
  // to error.tsx, and must keep travelling.
  if (!(error instanceof ApiError)) throw error;
  return { error: error.status === 401 ? fallback : error.detail, fields: error.fields };
}

/** Where a just-logged-in user belongs: onboarding if they have no profile yet. */
async function landingPath(next: string): Promise<string> {
  try {
    await apiFetch<Profile>("/profile");
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return "/onboarding";
    throw error;
  }
  return safeNext(next) ?? "/feed";
}

export async function login(_previous: FormState, data: FormData): Promise<FormState> {
  // The backend's login is the OAuth2 password flow: form-encoded, and the email goes in
  // the field called `username`.
  const body = new URLSearchParams({
    username: String(data.get("email") ?? ""),
    password: String(data.get("password") ?? ""),
  });

  let destination: string;
  try {
    const token = await apiPublic<TokenResponse>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    await setSession(token.access_token);
    destination = await landingPath(String(data.get("next") ?? ""));
  } catch (error) {
    return failure(error, "Incorrect email or password.");
  }

  // Outside the try: redirect() works by throwing, and catching it here would swallow it.
  redirect(destination);
}

export async function signup(_previous: FormState, data: FormData): Promise<FormState> {
  try {
    const result = await apiPublic<SignupResponse>("/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: String(data.get("email") ?? ""),
        password: String(data.get("password") ?? ""),
      }),
    });
    await setSession(result.access_token);
  } catch (error) {
    return failure(error, "Couldn't create that account.");
  }

  // A new account has no profile, so it always starts at onboarding.
  redirect("/onboarding");
}

export async function logout(): Promise<void> {
  await clearSession();
  redirect("/login");
}
