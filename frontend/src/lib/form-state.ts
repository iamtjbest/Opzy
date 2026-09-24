/**
 * The shape every form in the app gets back from its Server Action.
 *
 * This lives outside the action modules on purpose: a `"use server"` file may only export
 * async functions, so a plain object exported from one arrives as `undefined` on the
 * client and the first render crashes reading `state.fields`.
 */
export type FormState = {
  /** A message for the whole form, or null. */
  error: string | null;
  /** Field name → message, from the backend's 422. */
  fields: Record<string, string>;
};

export const EMPTY_FORM_STATE: FormState = { error: null, fields: {} };

/** The profile form also reports a successful save, since it doesn't always redirect. */
export type ProfileState = FormState & { saved: boolean };

export const EMPTY_PROFILE_STATE: ProfileState = { ...EMPTY_FORM_STATE, saved: false };

/**
 * The forgot-password form reports only that it has finished. It must never report
 * whether the address had an account — the endpoint answers identically either way, and
 * rendering a different state here would undo that.
 */
export type ResetRequestState = FormState & { sent: boolean };

export const EMPTY_RESET_REQUEST_STATE: ResetRequestState = {
  ...EMPTY_FORM_STATE,
  sent: false,
};

/**
 * Signup reports only that it has finished, for the same reason: since Sprint 9 the
 * endpoint answers identically whether the address was new or already registered, and
 * rendering anything different here would give away what the API refuses to.
 */
export type SignupState = FormState & { sent: boolean };

export const EMPTY_SIGNUP_STATE: SignupState = { ...EMPTY_FORM_STATE, sent: false };

/**
 * The /verify-email page's three states. "verifying" is the initial one because the page
 * spends the token as soon as it loads.
 */
export type VerifyState =
  | { status: "verifying" }
  | { status: "verified" }
  | { status: "failed"; error: string };
