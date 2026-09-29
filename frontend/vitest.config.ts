import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      // `server-only` throws outside a React Server Component render. The modules under
      // test import it as a guard, not for behaviour, so it is stubbed out here.
      "server-only": fileURLToPath(new URL("./src/test/server-only.ts", import.meta.url)),
    },
  },
  test: {
    environment: "node",
    // Only unit tests. Playwright owns `e2e/`, and its files would otherwise be collected.
    include: ["src/**/*.test.ts"],
  },
});
