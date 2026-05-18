import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "../../../tests/e2e",
  testMatch: "**/*.spec.ts",
  timeout: 30000,
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: "cd ../../.. && cd src/assistant && uvicorn api.main:app --port 8082",
      port: 8082,
      reuseExistingServer: true,
    },
    {
      command: "pnpm dev",
      port: 5173,
      reuseExistingServer: true,
    },
  ],
});
