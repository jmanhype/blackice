import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright configuration for Agent Flywheel web e2e testing.
 * @see https://playwright.dev/docs/test-configuration
 */
const isCI = !!process.env.CI;

const DEFAULT_PORT = 3000;
const parsedPort = Number.parseInt(process.env.PW_PORT || process.env.PORT || "", 10);
const port = Number.isFinite(parsedPort) && parsedPort > 0 ? parsedPort : DEFAULT_PORT;

const baseURL = process.env.PLAYWRIGHT_BASE_URL || `http://localhost:${port}`;

// Skip local webServer when testing against external URL (e.g., production)
const isExternalUrl = !!process.env.PLAYWRIGHT_BASE_URL;

const webServerCommand = (() => {
  // Default to production server for stability (matches CI behavior).
  // Override locally with PW_USE_DEV_SERVER=1 if needed.
  if (!isCI && process.env.PW_USE_DEV_SERVER === "1") {
    return `bun run dev -- --port ${port}`;
  }
  return `bun run build && bun run start -- -p ${port}`;
})();

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "github" : "html",
  // Increase timeout for CI environments
  timeout: process.env.CI ? 60000 : 30000,
  // Give actions more time in CI
  expect: {
    timeout: process.env.CI ? 10000 : 5000,
  },

  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    // Increase action timeout for CI
    actionTimeout: process.env.CI ? 15000 : 10000,
    navigationTimeout: process.env.CI ? 30000 : 15000,
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"] },
    },
    {
      name: "Mobile Safari",
      use: { ...devices["iPhone 12"] },
    },
  ],

  // Skip webServer when testing against external URL (production smoke tests)
  webServer: isExternalUrl
    ? undefined
    : {
        command: webServerCommand,
        url: baseURL,
        reuseExistingServer: !isCI,
        timeout: 180000, // 3 minutes for build + start
      },
});
