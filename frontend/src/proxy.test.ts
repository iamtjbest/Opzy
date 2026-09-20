import { describe, expect, it } from "vitest";
import { route } from "@/proxy";

describe("route, logged out", () => {
  it("sends every protected page to login, remembering where they were going", () => {
    for (const path of [
      "/feed",
      "/saved",
      "/applications",
      "/settings",
      "/onboarding",
      "/opportunities/7c9e6679-7425-40de-944b-e07fc1f90ae7",
    ]) {
      expect(route(path, false)).toBe(`/login?next=${encodeURIComponent(path)}`);
    }
  });

  it("leaves the public pages alone", () => {
    expect(route("/login", false)).toBeNull();
    expect(route("/signup", false)).toBeNull();
    expect(route("/forgot-password", false)).toBeNull();
    expect(route("/reset-password", false)).toBeNull();
    expect(route("/", false)).toBeNull();
  });
});

describe("route, logged in", () => {
  it("keeps a logged-in user off login and signup", () => {
    expect(route("/login", true)).toBe("/feed");
    expect(route("/signup", true)).toBe("/feed");
  });

  it("lets every protected page through", () => {
    for (const path of ["/feed", "/saved", "/applications", "/settings", "/onboarding"]) {
      expect(route(path, true)).toBeNull();
    }
  });

  it("leaves the reset pages reachable, so a stale link isn't bounced to the feed", () => {
    expect(route("/forgot-password", true)).toBeNull();
    expect(route("/reset-password", true)).toBeNull();
  });
});

describe("route, path matching", () => {
  it("does not treat a lookalike prefix as protected", () => {
    expect(route("/feedback", false)).toBeNull();
    expect(route("/settings-help", false)).toBeNull();
  });

  it("protects children of a protected path", () => {
    expect(route("/settings/anything", false)).toBe(
      `/login?next=${encodeURIComponent("/settings/anything")}`,
    );
  });

  it("never touches the session-end handler, which must run without a session", () => {
    expect(route("/session/end", false)).toBeNull();
    expect(route("/session/end", true)).toBeNull();
  });
});
