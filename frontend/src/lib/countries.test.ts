import { describe, expect, it } from "vitest";
import { COUNTRY_CODES } from "@/lib/countries";
import { countryName } from "@/lib/format";

describe("COUNTRY_CODES", () => {
  it("puts Nigeria first", () => {
    expect(COUNTRY_CODES[0]).toBe("NG");
  });

  it("covers the whole ISO 3166 alpha-2 list", () => {
    // pycountry ships 249 alpha-2 codes; the backend accepts exactly those.
    expect(COUNTRY_CODES.length).toBe(249);
  });

  it("holds only uppercase two-letter codes, with no duplicates", () => {
    for (const code of COUNTRY_CODES) expect(code).toMatch(/^[A-Z]{2}$/);
    expect(new Set(COUNTRY_CODES).size).toBe(COUNTRY_CODES.length);
  });

  it("sorts everything after Nigeria by display name", () => {
    const rest = COUNTRY_CODES.slice(1).map(countryName);
    expect(rest).toEqual([...rest].sort((a, b) => a.localeCompare(b, "en")));
  });
});
