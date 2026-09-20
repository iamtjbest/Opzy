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
