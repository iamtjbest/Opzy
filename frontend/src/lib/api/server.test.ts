import { afterEach, describe, expect, it, vi } from "vitest";

const getToken = vi.fn();
const redirect = vi.fn((url: string) => {
  throw new Error(`NEXT_REDIRECT:${url}`);
});
const headerStore = { get: vi.fn(() => "/saved") };

vi.mock("@/lib/session-cookies", () => ({ getToken }));
vi.mock("next/navigation", () => ({ redirect }));
vi.mock("next/headers", () => ({ headers: async () => headerStore }));

const { ApiError, apiFetch, apiPublic } = await import("@/lib/api/server");

function jsonResponse(status: number, body: unknown) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.restoreAllMocks();
  getToken.mockReset();
  redirect.mockClear();
});

describe("apiFetch", () => {
  it("sends the token as a bearer header and never caches", async () => {
    getToken.mockResolvedValue("tok-123");
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(jsonResponse(200, { items: [], total: 0, limit: 20, offset: 0 }));

    await apiFetch("/saved");

    const [url, init] = fetchMock.mock.calls[0];
    expect(String(url)).toBe("http://127.0.0.1:8000/saved");
    expect(new Headers(init!.headers).get("Authorization")).toBe("Bearer tok-123");
    expect(init!.cache).toBe("no-store");
  });

  it("returns the parsed body", async () => {
    getToken.mockResolvedValue("tok-123");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(jsonResponse(200, { total: 7 }));

    await expect(apiFetch<{ total: number }>("/saved")).resolves.toEqual({ total: 7 });
  });

  it("throws ApiError carrying the backend's detail", async () => {
    getToken.mockResolvedValue("tok-123");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(jsonResponse(500, { detail: "boom" }));

    await expect(apiFetch("/saved")).rejects.toMatchObject({ status: 500, detail: "boom" });
  });

  it("turns a 422 into per-field messages", async () => {
    getToken.mockResolvedValue("tok-123");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse(422, {
        detail: [
          { loc: ["body", "nationality"], msg: "must be an ISO 3166 two-letter country code" },
          { loc: ["body", "skills", 0], msg: "String should have at most 50 characters" },
        ],
      }),
    );

    const error = await apiFetch("/profile").catch((e) => e as InstanceType<typeof ApiError>);
    expect(error.status).toBe(422);
    expect(error.fields).toEqual({
      nationality: "must be an ISO 3166 two-letter country code",
      skills: "String should have at most 50 characters",
    });
  });

  it("sends a 401 to /session/end with the page it happened on", async () => {
    getToken.mockResolvedValue("stale");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(jsonResponse(401, { detail: "nope" }));

    await expect(apiFetch("/saved")).rejects.toThrow(
      "NEXT_REDIRECT:/session/end?next=%2Fsaved",
    );
    expect(redirect).toHaveBeenCalledWith("/session/end?next=%2Fsaved");
  });

  it("goes to /session/end even with no cookie at all", async () => {
    getToken.mockResolvedValue(undefined);

    await expect(apiFetch("/saved")).rejects.toThrow("NEXT_REDIRECT:");
    expect(redirect).toHaveBeenCalled();
  });

  it("reads a 204 as null rather than choking on an empty body", async () => {
    getToken.mockResolvedValue("tok-123");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(null, { status: 204 }));

    await expect(apiFetch("/anything")).resolves.toBeNull();
  });
});

describe("apiPublic", () => {
  it("sends no Authorization header", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(jsonResponse(200, { access_token: "t", token_type: "bearer" }));

    await apiPublic("/auth/login", { method: "POST" });

    const [, init] = fetchMock.mock.calls[0];
    expect(new Headers(init!.headers).has("Authorization")).toBe(false);
    expect(getToken).not.toHaveBeenCalled();
  });

  it("throws ApiError on a 409 instead of redirecting", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse(409, { detail: "An account with this email already exists" }),
    );

    await expect(apiPublic("/auth/signup", { method: "POST" })).rejects.toMatchObject({
      status: 409,
    });
    expect(redirect).not.toHaveBeenCalled();
  });
});
