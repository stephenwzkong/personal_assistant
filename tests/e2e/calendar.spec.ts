import { test, expect } from "@playwright/test";

test.describe("Calendar page", () => {
  test("calendar page renders", async ({ page }) => {
    await page.goto("/calendar");
    await expect(page.getByText("Calendar")).toBeVisible();
    await expect(page.getByText("Today")).toBeVisible();
  });

  test("has view toggle buttons", async ({ page }) => {
    await page.goto("/calendar");
    await expect(page.getByText("Day")).toBeVisible();
    await expect(page.getByText("Week")).toBeVisible();
    await expect(page.getByText("Month")).toBeVisible();
  });

  test("navigate between views", async ({ page }) => {
    await page.goto("/calendar");
    await page.getByText("Month").click();
    await page.waitForTimeout(500);
    await page.getByText("Week").click();
    await page.waitForTimeout(500);
    await expect(page.getByText("Today")).toBeVisible();
  });
});
