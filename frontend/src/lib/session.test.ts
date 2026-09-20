import { describe, expect, it } from "vitest";
import { SESSION_COOKIE, safeNext, sessionCookieOptions } from "@/lib/session";

describe("safeNext", () => {
  it("accepts a same-site path, query string and all", () => {
    expect(safeNext("/feed?category=job")).toBe("/feed?category=job");
    expect(safeNext("/opportunities/abc")).toBe("/opportunities/abc");
  });

  it("rejects a protocol-relative URL", () => {
    expect(safeNext("//evil.com")).toBeNull();
  });

  it("rejects an absolute URL", () => {
    expect(safeNext("https://evil.com")).toBeNull();
    expect(safeNext("http://evil.com")).toBeNull();
  });

  it("rejects a javascript: URL", () => {
    expect(safeNext("javascript:alert(1)")).toBeNull();
  });

  it("rejects a backslash-prefixed path, which some browsers read as a slash", () => {
    expect(safeNext("/\\evil.com")).toBeNull();
    expect(safeNext("\\\\evil.com")).toBeNull();
  });

  it("rejects anything not starting with a slash, and nothing at all", () => {
    expect(safeNext("feed")).toBeNull();
    expect(safeNext("")).toBeNull();
    expect(safeNext(null)).toBeNull();
    expect(safeNext(undefined)).toBeNull();
  });
});

describe("sessionCookieOptions", () => {
  it("is httpOnly, lax, site-wide, and expires with the backend's token", () => {
    const options = sessionCookieOptions();
    expect(options.httpOnly).toBe(true);
    expect(options.sameSite).toBe("lax");
    expect(options.path).toBe("/");
    expect(options.maxAge).toBe(3600);
  });

  it("is not secure outside production, so http://localhost works", () => {
    expect(sessionCookieOptions().secure).toBe(false);
  });

  it("names the cookie opzy_session", () => {
    expect(SESSION_COOKIE).toBe("opzy_session");
  });
});
