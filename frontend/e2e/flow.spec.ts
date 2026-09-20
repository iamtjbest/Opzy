import { expect, test } from "@playwright/test";

const PASSWORD = "e2e-password-123";

function newEmail() {
  // The teardown deletes everything matching e2e-%@example.com.
  return `e2e-${Date.now()}@example.com`;
}

/** Wait for a Server Action's redirect rather than for the network to go quiet. */
const NAV_TIMEOUT = 20_000;

test("a new user can go from signup to applied and back out again", async ({ page }) => {
  const email = newEmail();

  // --- Sign up -------------------------------------------------------------------
  await page.goto("/signup");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(PASSWORD);
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL("**/onboarding", { timeout: NAV_TIMEOUT });

  // --- Onboard -------------------------------------------------------------------
  await page.getByLabel("Nationality").selectOption("NG");
  await page.getByLabel("Education level").selectOption("undergraduate");
  await page.getByLabel("Field of study").fill("Computer Engineering");
  await page.getByLabel("Location").fill("Zaria, Kaduna");
  await page.getByLabel("Add a skill").fill("python");
  await page.getByLabel("Add a skill").press("Enter");
  // Every interest, so the feed has something in it whatever the seed data looks like.
  for (const label of [
    "Jobs",
    "Internships",
    "Scholarships",
    "Fellowships",
    "Grants",
    "Hackathons",
    "Competitions",
  ]) {
    await page.getByRole("button", { name: label, exact: true }).click();
  }
  await page.getByRole("button", { name: "Find my opportunities" }).click();
  await page.waitForURL("**/feed", { timeout: NAV_TIMEOUT });

  // --- The feed ------------------------------------------------------------------
  const cards = page.locator("[data-testid='feed-card']");
  await expect(cards.first()).toBeVisible();
  const cardCount = await cards.count();
  expect(cardCount).toBeGreaterThan(0);

  // Every card carries its explanation — the thing the product is for.
  await expect(cards.first().locator("[data-testid='explanation']")).not.toBeEmpty();

  // Save the first one.
  const savedTitle = await cards.first().locator("h2").innerText();
  await cards.first().getByRole("button", { name: "Save" }).click();
  await expect(
    cards.filter({ hasText: savedTitle }).getByRole("button", { name: "Saved" }),
  ).toBeVisible();

  // Dismiss another, with a reason, and check it stays gone across a reload.
  if (cardCount > 1) {
    const dismissed = cards.filter({ hasNotText: savedTitle }).first();
    const dismissedTitle = await dismissed.locator("h2").innerText();
    await dismissed.getByRole("button", { name: "Dismiss" }).click();
    await page.getByRole("button", { name: "Not relevant to my skills" }).click();
    await expect(cards.filter({ hasText: dismissedTitle })).toHaveCount(0);

    await page.reload();
    await expect(
      page.locator("[data-testid='feed-card']").filter({ hasText: dismissedTitle }),
    ).toHaveCount(0);
  }

  // --- Saved ---------------------------------------------------------------------
  await page.goto("/saved");
  const savedRow = page.locator("[data-testid='saved-row']").filter({ hasText: savedTitle });
  await expect(savedRow).toHaveCount(1);

  // --- Detail, then applied ------------------------------------------------------
  await savedRow.getByRole("link", { name: savedTitle }).click();
  await page.waitForURL(/\/opportunities\//, { timeout: NAV_TIMEOUT });
  await page.getByRole("button", { name: "Mark as applied" }).click();
  await expect(page.getByRole("button", { name: "Applied ✓" })).toBeVisible();

  await page.goto("/applications");
  await expect(page.getByRole("link", { name: savedTitle })).toBeVisible();

  // Applying replaces saving, so it has left the Saved list.
  await page.goto("/saved");
  await expect(
    page.locator("[data-testid='saved-row']").filter({ hasText: savedTitle }),
  ).toHaveCount(0);

  // --- Settings: the notification cadence, including off --------------------------
  await page.goto("/settings");
  await page.getByRole("radio", { name: /Off/ }).click();
  await page.reload();
  await expect(page.getByRole("radio", { name: /Off/ })).toHaveAttribute(
    "aria-checked",
    "true",
  );

  // --- Log out -------------------------------------------------------------------
  await page.getByRole("button", { name: "Log out" }).first().click();
  await page.waitForURL(/\/login/, { timeout: NAV_TIMEOUT });

  await page.goto("/feed");
  await expect(page).toHaveURL(/\/login/);
});

test("a dead token lands on login instead of looping", async ({ page, context }) => {
  // Not a real token, so the backend answers 401 on the first call the feed makes.
  await context.addCookies([
    {
      name: "opzy_session",
      value: "not.a.real.token",
      domain: "localhost",
      path: "/",
      httpOnly: true,
    },
  ]);

  await page.goto("/feed");

  await expect(page).toHaveURL(/\/login/);
  // The cookie has to be gone, or proxy.ts would bounce /login straight back to /feed.
  const cookies = await context.cookies();
  expect(cookies.find((c) => c.name === "opzy_session")?.value ?? "").toBe("");
});

test("a forgotten password can be reset from the browser", async ({ page, context }) => {
  const email = newEmail();

  // An account to reset.
  await page.goto("/signup");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(PASSWORD);
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL("**/onboarding", { timeout: NAV_TIMEOUT });
  await context.clearCookies();

  // The reset panel must look the same whether or not the address has an account —
  // that is what stops this endpoint being an account-existence oracle.
  await page.goto("/forgot-password");
  await page.getByLabel("Email").fill(email);
  await page.getByRole("button", { name: "Send reset link" }).click();
  const known = page.getByText("a reset link is on its way");
  await expect(known).toBeVisible();
  const knownPanel = await page.locator("body").innerText();

  await page.goto("/forgot-password");
  await page.getByLabel("Email").fill(`e2e-nobody-${Date.now()}@example.com`);
  await page.getByRole("button", { name: "Send reset link" }).click();
  await expect(page.getByText("a reset link is on its way")).toBeVisible();
  expect(await page.locator("body").innerText()).toBe(knownPanel);

  // A link with no token explains itself rather than crashing. The happy path needs the
  // token out of the email, which only exists in the backend's log, so it is covered by
  // the manual check in the plan rather than here.
  await page.goto("/reset-password");
  await expect(page.getByText("missing its reset code")).toBeVisible();

  // A token that was never issued is refused with the generic message.
  await page.goto("/reset-password?token=not-a-real-token");
  await page.getByLabel("New password", { exact: true }).fill("another-password-123");
  await page.getByLabel("Confirm new password").fill("another-password-123");
  await page.getByRole("button", { name: "Set new password" }).click();
  await expect(page.getByText(/invalid or has expired/i)).toBeVisible();
});
