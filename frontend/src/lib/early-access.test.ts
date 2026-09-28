import { describe, expect, it } from "vitest";

import {
  WindowLimiter,
  alreadyListed,
  csvLine,
  normalizeEarlyAccessEmail,
} from "@/lib/early-access";

describe("normalizeEarlyAccessEmail", () => {
  it("accepts an ordinary address, trimmed and lowercased", () => {
    expect(normalizeEarlyAccessEmail("  Ada.Lovelace+opzy@Example.COM ")).toBe(
      "ada.lovelace+opzy@example.com",
    );
  });

  it.each([
    // Anything that isn't a string, so a JSON object can't reach the file.
    [undefined],
    [null],
    [42],
    [{ toString: "x" }],
    [["a@b.co"]],
  ])("rejects %j", (value) => {
    expect(normalizeEarlyAccessEmail(value)).toBeNull();
  });

  it.each([
    "",
    "not-an-email",
    "a@b",
    // Spreadsheet formulas: a cell starting with = + - @ is executed when opened.
    "=HYPERLINK(\"http://evil\")@x.co",
    "+1@x.co",
    "-1@x.co",
    "@x.co",
    // Quotes and commas would break out of the CSV cell.
    'a"b@x.co',
    "a,b@x.co",
    "a b@x.co",
    "a\n@x.co",
  ])("rejects %j", (value) => {
    expect(normalizeEarlyAccessEmail(value)).toBeNull();
  });

  it("rejects an address longer than 254 characters", () => {
    expect(normalizeEarlyAccessEmail(`${"a".repeat(250)}@x.co`)).toBeNull();
  });
});

describe("csv", () => {
  it("writes one quoted row", () => {
    expect(csvLine("ada@example.com", new Date("2026-09-28T10:00:00Z"))).toBe(
      '"ada@example.com","2026-09-28T10:00:00.000Z"\n',
    );
  });

  it("spots an address already on the list, and only that one", () => {
    const csv = '"ada@example.com","2026-09-28T10:00:00.000Z"\n';

    expect(alreadyListed(csv, "ada@example.com")).toBe(true);
    expect(alreadyListed(csv, "da@example.com")).toBe(false);
  });
});

describe("WindowLimiter", () => {
  it("allows up to the limit in a window, then refuses", () => {
    const limiter = new WindowLimiter(2, 1000);

    expect(limiter.allow("ip", 0)).toBe(true);
    expect(limiter.allow("ip", 1)).toBe(true);
    expect(limiter.allow("ip", 2)).toBe(false);
    expect(limiter.allow("other", 3)).toBe(true);
  });

  it("starts afresh once the window has passed", () => {
    const limiter = new WindowLimiter(1, 1000);

    expect(limiter.allow("ip", 0)).toBe(true);
    expect(limiter.allow("ip", 500)).toBe(false);
    expect(limiter.allow("ip", 1000)).toBe(true);
  });

  it("can't be grown without bound by many addresses", () => {
    const limiter = new WindowLimiter(5, 1000, 2);

    expect(limiter.allow("a", 0)).toBe(true);
    expect(limiter.allow("b", 0)).toBe(true);
    expect(limiter.allow("c", 0)).toBe(false);
    // Expired windows are cleared to make room.
    expect(limiter.allow("c", 1000)).toBe(true);
  });
});
