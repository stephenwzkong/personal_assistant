import { test, expect } from "@playwright/test";

test.describe("Calendar page", () => {
  test("calendar page renders", async ({ page }) => {
    await page.goto("/calendar");
    await expect(page.getByRole("main").getByText("Calendar")).toBeVisible();
    await expect(page.getByRole("button", { name: "Today" })).toBeVisible();
  });

  test("has view toggle buttons", async ({ page }) => {
    await page.goto("/calendar");
    await expect(page.getByRole("button", { name: "Day", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Week" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Month" })).toBeVisible();
  });

  test("navigate between views", async ({ page }) => {
    await page.goto("/calendar");
    await page.getByRole("button", { name: "Month" }).first().click();
    await page.waitForTimeout(500);
    await page.getByRole("button", { name: "Week" }).first().click();
    await page.waitForTimeout(500);
    await expect(page.getByRole("button", { name: "Today" })).toBeVisible();
  });
});
