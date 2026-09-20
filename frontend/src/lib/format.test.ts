import { describe, expect, it } from "vitest";
import {
  CADENCES,
  CATEGORY_LABELS,
  DISMISS_REASONS,
  OPPORTUNITY_TYPES,
  countryName,
  deadlineLabel,
  lagosToday,
} from "@/lib/format";

describe("deadlineLabel", () => {
  const today = "2026-09-20";

  it("calls a missing deadline rolling", () => {
    expect(deadlineLabel(null, today)).toBe("Rolling");
  });

  it("calls a past deadline closed", () => {
    expect(deadlineLabel("2026-09-19", today)).toBe("Closed");
  });

  it("names today and tomorrow", () => {
    expect(deadlineLabel("2026-09-20", today)).toBe("Closes today");
    expect(deadlineLabel("2026-09-21", today)).toBe("Closes tomorrow");
  });

  it("counts the days otherwise", () => {
    expect(deadlineLabel("2026-09-30", today)).toBe("Closes in 10 days");
  });

  it("counts across a month and a year boundary", () => {
    expect(deadlineLabel("2026-10-01", "2026-09-29")).toBe("Closes in 2 days");
    expect(deadlineLabel("2027-01-01", "2026-12-31")).toBe("Closes tomorrow");
  });
});

describe("lagosToday", () => {
  it("uses the Lagos calendar date, not the machine's", () => {
    // 2026-09-20T23:30Z is already the 21st in Lagos (UTC+1).
    expect(lagosToday(new Date("2026-09-20T23:30:00Z"))).toBe("2026-09-21");
    // ...and 2026-09-20T00:30Z is still the 20th.
    expect(lagosToday(new Date("2026-09-20T00:30:00Z"))).toBe("2026-09-20");
  });
});

describe("DISMISS_REASONS", () => {
  it("keeps the five labels the modal already shows", () => {
    expect(DISMISS_REASONS.map((r) => r.label)).toEqual([
      "Not relevant to my skills",
      "Pay is too low",
      "Not eligible (location, degree)",
      "Not interested in this company",
      "Other",
    ]);
  });

  it("maps them to the codes the backend accepts", () => {
    // backend/app/models/base.py :: DISMISS_REASONS, in that order.
    expect(DISMISS_REASONS.map((r) => r.code)).toEqual([
      "not_relevant",
      "pay_too_low",
      "not_eligible",
      "not_interested_org",
      "other",
    ]);
  });
});

describe("CADENCES", () => {
  it("offers all four of the backend's cadences, off included", () => {
    expect(CADENCES.map((c) => c.value)).toEqual(["instant", "daily", "weekly", "off"]);
  });
});

describe("CATEGORY_LABELS", () => {
  it("labels every opportunity type, with none left over", () => {
    expect(Object.keys(CATEGORY_LABELS).sort()).toEqual([...OPPORTUNITY_TYPES].sort());
  });
});

describe("countryName", () => {
  it("names a code, and falls back to the code when it can't", () => {
    expect(countryName("NG")).toBe("Nigeria");
    expect(countryName("ZZZZ")).toBe("ZZZZ");
  });
});
