"use server";

import { redirect } from "next/navigation";

import { ApiError, apiFetch, apiPublic } from "@/lib/api/server";
import type { AcceptedResponse, Profile, TokenResponse } from "@/lib/api/types";
import type {
  FormState,
  ResetRequestState,
  SignupState,
  VerifyState,
} from "@/lib/form-state";
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

/**
 * Create an account. Nobody is logged in by this — the backend answers 202 with no token
 * and mails a confirmation link, and it answers exactly the same way for an address that
 * already has an account. So this renders one "check your email" state for both cases; a
 * separate "that email is taken" message here would leak precisely what the 202 hides.
 */
export async function signup(
  _previous: SignupState,
  data: FormData,
): Promise<SignupState> {
  try {
    await apiPublic<AcceptedResponse>("/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: String(data.get("email") ?? ""),
        password: String(data.get("password") ?? ""),
      }),
    });
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    if (error.status === 429) {
      return {
        error: "Too many attempts just now. Wait a few minutes and try again.",
        fields: {},
        sent: false,
      };
    }
    return { error: error.detail, fields: error.fields, sent: false };
  }

  return { error: null, fields: {}, sent: true };
}

/**
 * Spend a verification token. On success the backend returns an access token, so the user
 * lands logged in rather than being sent back to a login form.
 *
 * Returns rather than redirects: the caller is an effect on page load, not a form, and it
 * needs to render "expired, here's a resend button" when this fails.
 */
export async function verifyEmail(token: string): Promise<VerifyState> {
  try {
    const result = await apiPublic<TokenResponse>("/auth/verify-email/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });
    await setSession(result.access_token);
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    return {
      status: "failed",
      error:
        error.status === 429
          ? "Too many attempts just now. Wait a few minutes and try again."
          : error.detail,
    };
  }

  return { status: "verified" };
}

/**
 * Ask for a fresh confirmation link. Like the reset request, the backend answers 202 with
 * an identical body whichever the address is, so this reports only that it finished.
 */
export async function resendVerification(
  _previous: ResetRequestState,
  data: FormData,
): Promise<ResetRequestState> {
  try {
    await apiPublic("/auth/verify-email/resend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: String(data.get("email") ?? "") }),
    });
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    if (error.status === 429) {
      return {
        error: "Too many requests just now. Wait a few minutes and try again.",
        fields: {},
        sent: false,
      };
    }
    return { error: error.detail, fields: error.fields, sent: false };
  }

  return { error: null, fields: {}, sent: true };
}

/**
 * Delete the logged-in user's account, for good. The backend wants the current password —
 * a session cookie alone must not be enough to destroy an account — and cascades away the
 * profile, actions and everything else.
 */
export async function deleteAccount(
  _previous: FormState,
  data: FormData,
): Promise<FormState> {
  try {
    await apiFetch("/account", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: String(data.get("password") ?? "") }),
    });
  } catch (error) {
    // The backend answers 403 for a wrong password, deliberately: a 401 would be caught by
    // apiFetch as an expired session and redirect through /session/end, logging the user
    // out over a typo. So this renders the backend's own message.
    if (!(error instanceof ApiError)) throw error;
    return { error: error.detail, fields: error.fields };
  }

  // The account is gone, so the cookie points at nothing. Clear it before leaving, or the
  // next request travels with a token whose user no longer exists.
  await clearSession();
  redirect("/");
}

export async function logout(): Promise<void> {
  await clearSession();
  redirect("/login");
}

/**
 * Ask for a reset link. The backend answers 202 with an identical body whether or not the
 * address has an account — that is the whole point of the endpoint — so this renders the
 * same confirmation either way. A 429 is the rate limiter and is worth showing.
 */
export async function requestPasswordReset(
  _previous: ResetRequestState,
  data: FormData,
): Promise<ResetRequestState> {
  try {
    await apiPublic("/auth/password-reset/request", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: String(data.get("email") ?? "") }),
    });
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    if (error.status === 429) {
      return {
        error: "Too many requests just now. Wait a few minutes and try again.",
        fields: {},
        sent: false,
      };
    }
    return { error: error.detail, fields: error.fields, sent: false };
  }

  return { error: null, fields: {}, sent: true };
}

/** Spend a reset token. 400 covers unknown, spent and expired alike, by design. */
export async function confirmPasswordReset(
  _previous: FormState,
  data: FormData,
): Promise<FormState> {
  const password = String(data.get("password") ?? "");
  if (password !== String(data.get("confirm") ?? "")) {
    return { error: null, fields: { confirm: "Those two passwords don't match." } };
  }

  try {
    await apiPublic("/auth/password-reset/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token: String(data.get("token") ?? ""),
        new_password: password,
      }),
    });
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    return { error: error.detail, fields: error.fields };
  }

  // 204, no token back: the user logs in with the new password like anyone else.
  redirect("/login?reset=1");
}
