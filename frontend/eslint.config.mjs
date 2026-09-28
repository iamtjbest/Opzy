import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // `next dev` (16.3) also writes a stray frontend/frontend/.next/dev/static; without
    // this, `npm run lint` after any Playwright run reports thousands of problems in it.
    "**/.next/**",
  ]),
]);

export default eslintConfig;
