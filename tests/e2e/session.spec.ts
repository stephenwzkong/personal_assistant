import { test, expect } from "@playwright/test";

test.describe("Session management", () => {
  test("session persists on refresh", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    const session1 = await page.evaluate(() =>
      sessionStorage.getItem("pa_session")
    );
    expect(session1).toBeTruthy();

    await page.reload();
    await page.waitForTimeout(1000);

    const session2 = await page.evaluate(() =>
      sessionStorage.getItem("pa_session")
    );
    expect(session2).toBe(session1);
  });

  test("session persists across pages", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    const session1 = await page.evaluate(() =>
      sessionStorage.getItem("pa_session")
    );

    await page.goto("/calendar");
    await page.waitForTimeout(500);

    const session2 = await page.evaluate(() =>
      sessionStorage.getItem("pa_session")
    );
    expect(session2).toBe(session1);
  });
});
