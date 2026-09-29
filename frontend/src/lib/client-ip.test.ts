import { describe, expect, it } from "vitest";

import { pickClientIp, trustedHopsFromEnv } from "@/lib/client-ip";

describe("pickClientIp", () => {
  it("takes the only entry when one proxy wrote the header", () => {
    expect(pickClientIp("203.0.113.7", 1)).toBe("203.0.113.7");
  });

  it("ignores whatever the client put on the left", () => {
    // A client can send its own X-Forwarded-For; our proxy appends the real address.
    expect(pickClientIp("1.1.1.1, 203.0.113.7", 1)).toBe("203.0.113.7");
  });

  it("counts back past each trusted proxy", () => {
    expect(pickClientIp("1.1.1.1, 203.0.113.7, 10.0.0.9", 2)).toBe("203.0.113.7");
  });

  it("gives up when the header is shorter than the proxy chain", () => {
    expect(pickClientIp("203.0.113.7", 2)).toBeNull();
  });

  it("gives up when there is no header", () => {
    expect(pickClientIp(null, 1)).toBeNull();
    expect(pickClientIp("", 1)).toBeNull();
    expect(pickClientIp(" , ", 1)).toBeNull();
  });
});

describe("trustedHopsFromEnv", () => {
  it("defaults to one proxy", () => {
    expect(trustedHopsFromEnv(undefined)).toBe(1);
  });

  it("reads a positive whole number", () => {
    expect(trustedHopsFromEnv("2")).toBe(2);
  });

  it("falls back to one for anything else", () => {
    expect(trustedHopsFromEnv("0")).toBe(1);
    expect(trustedHopsFromEnv("-1")).toBe(1);
    expect(trustedHopsFromEnv("1.5")).toBe(1);
    expect(trustedHopsFromEnv("lots")).toBe(1);
  });
});
