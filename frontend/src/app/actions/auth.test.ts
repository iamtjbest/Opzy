import { afterEach, describe, expect, it, vi } from "vitest";

const apiPublic = vi.fn();
const apiFetch = vi.fn();
const setSession = vi.fn();
const clearSession = vi.fn();
const redirect = vi.fn((url: string) => {
  throw new Error(`NEXT_REDIRECT:${url}`);
});

class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly detail: string,
    readonly fields: Record<string, string> = {},
  ) {
    super(detail);
  }
}

vi.mock("@/lib/api/server", () => ({ ApiError, apiPublic, apiFetch }));
vi.mock("@/lib/session-cookies", () => ({ setSession, clearSession }));
vi.mock("next/navigation", () => ({ redirect }));

const { signup, verifyEmail, resendVerification, deleteAccount } = await import(
  "@/app/actions/auth"
);

const EMPTY = { error: null, fields: {} };
const EMPTY_SIGNUP = { ...EMPTY, sent: false };

function form(entries: Record<string, string>): FormData {
  const data = new FormData();
  for (const [key, value] of Object.entries(entries)) data.append(key, value);
  return data;
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("signup", () => {
  it("reports that the email was sent, and logs nobody in", async () => {
    apiPublic.mockResolvedValue({ detail: "Check your email" });

    const state = await signup(EMPTY_SIGNUP, form({ email: "a@b.co", password: "12345678" }));

    expect(state).toEqual({ error: null, fields: {}, sent: true });
    // Signup no longer returns a token, so there is nothing to store and no session yet.
    expect(setSession).not.toHaveBeenCalled();
    expect(redirect).not.toHaveBeenCalled();
  });

  it("posts the credentials to the signup endpoint", async () => {
    apiPublic.mockResolvedValue({ detail: "Check your email" });

    await signup(EMPTY_SIGNUP, form({ email: "a@b.co", password: "12345678" }));

    const [path, init] = apiPublic.mock.calls[0];
    expect(path).toBe("/auth/signup");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ email: "a@b.co", password: "12345678" });
  });

  it("renders the same state whether or not the address was already registered", async () => {
    // The backend answers 202 with the same body either way; this asserts the action
    // doesn't reintroduce the difference the API deliberately removed.
    apiPublic.mockResolvedValue({ detail: "Check your email" });
    const fresh = await signup(EMPTY_SIGNUP, form({ email: "new@b.co", password: "12345678" }));
    const taken = await signup(EMPTY_SIGNUP, form({ email: "old@b.co", password: "12345678" }));

    expect(fresh).toEqual(taken);
  });

  it("explains a rate limit rather than showing the raw detail", async () => {
    apiPublic.mockRejectedValue(new ApiError(429, "Too many requests"));

    const state = await signup(EMPTY_SIGNUP, form({ email: "a@b.co", password: "12345678" }));

    expect(state.sent).toBe(false);
    expect(state.error).toMatch(/wait a few minutes/i);
  });

  it("passes field errors from a 422 through to the form", async () => {
    apiPublic.mockRejectedValue(
      new ApiError(422, "Invalid", { password: "At least 8 characters." }),
    );

    const state = await signup(EMPTY_SIGNUP, form({ email: "a@b.co", password: "short" }));

    expect(state.fields.password).toBe("At least 8 characters.");
    expect(state.sent).toBe(false);
  });
});

describe("verifyEmail", () => {
  it("stores the returned session and reports success", async () => {
    apiPublic.mockResolvedValue({ access_token: "tok-9", token_type: "bearer" });

    const state = await verifyEmail("a-token");

    expect(state).toEqual({ status: "verified" });
    expect(setSession).toHaveBeenCalledWith("tok-9");
    const [path, init] = apiPublic.mock.calls[0];
    expect(path).toBe("/auth/verify-email/confirm");
    expect(JSON.parse(init.body)).toEqual({ token: "a-token" });
  });

  it("reports the backend's message when the link is spent or expired", async () => {
    apiPublic.mockRejectedValue(
      new ApiError(400, "That confirmation link is invalid or has expired."),
    );

    const state = await verifyEmail("stale");

    expect(state).toEqual({
      status: "failed",
      error: "That confirmation link is invalid or has expired.",
    });
    expect(setSession).not.toHaveBeenCalled();
  });

  it("explains a rate limit", async () => {
    apiPublic.mockRejectedValue(new ApiError(429, "Too many requests"));

    const state = await verifyEmail("whatever");

    expect(state.status).toBe("failed");
    expect(state.status === "failed" && state.error).toMatch(/wait a few minutes/i);
  });
});

describe("resendVerification", () => {
  it("reports only that it finished", async () => {
    apiPublic.mockResolvedValue({ detail: "If that email needs confirming…" });

    const state = await resendVerification({ ...EMPTY, sent: false }, form({ email: "a@b.co" }));

    expect(state).toEqual({ error: null, fields: {}, sent: true });
    const [path, init] = apiPublic.mock.calls[0];
    expect(path).toBe("/auth/verify-email/resend");
    expect(JSON.parse(init.body)).toEqual({ email: "a@b.co" });
  });

  it("explains a rate limit", async () => {
    apiPublic.mockRejectedValue(new ApiError(429, "Too many requests"));

    const state = await resendVerification({ ...EMPTY, sent: false }, form({ email: "a@b.co" }));

    expect(state.sent).toBe(false);
    expect(state.error).toMatch(/wait a few minutes/i);
  });
});

describe("deleteAccount", () => {
  it("sends the password, clears the session and goes home", async () => {
    apiFetch.mockResolvedValue(undefined);

    await expect(deleteAccount(EMPTY, form({ password: "hunter22" }))).rejects.toThrow(
      "NEXT_REDIRECT:/",
    );

    const [path, init] = apiFetch.mock.calls[0];
    expect(path).toBe("/account");
    expect(init.method).toBe("DELETE");
    expect(JSON.parse(init.body)).toEqual({ password: "hunter22" });
    expect(clearSession).toHaveBeenCalled();
  });

  it("keeps the session when the password is wrong", async () => {
    // 403, not 401 — a 401 never reaches here, because apiFetch turns it into a redirect
    // through /session/end. That is why the backend uses 403 for a wrong password.
    apiFetch.mockRejectedValue(new ApiError(403, "That password is incorrect."));

    const state = await deleteAccount(EMPTY, form({ password: "wrong" }));

    expect(state.error).toMatch(/password is incorrect/i);
    expect(clearSession).not.toHaveBeenCalled();
    expect(redirect).not.toHaveBeenCalled();
  });
});
