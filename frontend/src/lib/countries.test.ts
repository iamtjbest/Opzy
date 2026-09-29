import { describe, expect, it } from "vitest";
import { COUNTRY_CODES, countryName } from "@/lib/countries";

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

describe("countryName", () => {
  it("names a code, and falls back to the code when it can't", () => {
    expect(countryName("NG")).toBe("Nigeria");
    expect(countryName("ZZZZ")).toBe("ZZZZ");
  });

  it("prefers the short common name, as the backend does", () => {
    expect(countryName("TZ")).toBe("Tanzania");
  });

  it("names every code it offers, so no option ever renders as a bare code", () => {
    for (const code of COUNTRY_CODES) expect(countryName(code)).not.toBe(code);
  });

  it("does not depend on Intl, whose data differs between Node and the browser", () => {
    // Regression guard: Node's ICU calls FK "Falkland Islands (Islas Malvinas)" and
    // Chromium calls it "Falkland Islands". Rendering that difference inside a client
    // component is a hydration mismatch, so the name must come from the generated table.
    const intl = new Intl.DisplayNames(["en"], { type: "region" }).of("FK");
    expect(countryName("FK")).toBe("Falkland Islands (Malvinas)");
    expect(countryName("FK")).not.toBe(intl);
  });
});
