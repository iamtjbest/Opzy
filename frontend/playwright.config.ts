import { defineConfig, devices } from "@playwright/test";
import { randomBytes } from "node:crypto";
import path from "node:path";

// __dirname, not import.meta.url: Playwright loads this config as CommonJS.
const BACKEND_DIR = path.resolve(__dirname, "../backend");

// Shared by the two servers below, so the run goes through the same "frontend vouches for
// the browser's address" path as production. Fresh per run; it guards nothing real.
const INTERNAL_API_SECRET = randomBytes(32).toString("hex");

export default defineConfig({
  testDir: "./e2e",
  // One worker: the spec signs up a user and acts on shared seeded opportunities, so two
  // of them racing would dismiss each other's cards.
  workers: 1,
  // Generous because `next dev` compiles each page on its first hit: warm, no spec takes
  // over ~35s, but on a cold start several took close to 60s and timed out.
  timeout: 120_000,
  globalSetup: "./e2e/setup.ts",
  globalTeardown: "./e2e/teardown.ts",
  use: {
    baseURL: "http://localhost:3000",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      // The Docker DB must already be up: `docker compose up -d` in backend/.
      command: `${BACKEND_DIR}/.venv/bin/uvicorn app.main:app --port 8000`,
      cwd: BACKEND_DIR,
      env: {
        // Overrides backend/.env. With resend there, every signup in this suite would send
        // a real email to an address that doesn't exist, and bounces hurt the sender.
        EMAIL_BACKEND: "console",
        INTERNAL_API_SECRET,
      },
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: true,
      timeout: 60_000,
    },
    {
      command: "npm run dev",
      env: { INTERNAL_API_SECRET },
      url: "http://localhost:3000/login",
      reuseExistingServer: true,
      timeout: 120_000,
    },
  ],
});
