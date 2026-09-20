import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

// __dirname, not import.meta.url: Playwright loads this config as CommonJS.
const BACKEND_DIR = path.resolve(__dirname, "../backend");

export default defineConfig({
  testDir: "./e2e",
  // One worker: the spec signs up a user and acts on shared seeded opportunities, so two
  // of them racing would dismiss each other's cards.
  workers: 1,
  timeout: 60_000,
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
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: true,
      timeout: 60_000,
    },
    {
      command: "npm run dev",
      url: "http://localhost:3000/login",
      reuseExistingServer: true,
      timeout: 120_000,
    },
  ],
});
