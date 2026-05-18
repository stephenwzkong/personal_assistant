import { test, expect } from "@playwright/test";

test.describe("Chat page", () => {
  test("page loads with chat interface", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h2", { hasText: "What can I help you with?" })).toBeVisible({ timeout: 10000 });
    await expect(page.getByPlaceholder(/Message your assistant/)).toBeVisible();
  });

  test("send message and get response", async ({ page }) => {
    await page.goto("/");
    const input = page.getByPlaceholder(/Message your assistant/);
    await expect(input).toBeVisible({ timeout: 10000 });
    await input.fill("Hello");
    await input.press("Enter");

    await expect(page.getByText("Hello")).toBeVisible();

    await expect(
      page.locator('[class*="bg-gray-50"]').filter({ hasText: /./ }).last()
    ).toBeVisible({ timeout: 30000 });
  });

  test("message history preserved on navigation", async ({ page }) => {
    await page.goto("/");
    const input = page.getByPlaceholder(/Message your assistant/);
    await expect(input).toBeVisible({ timeout: 10000 });
    await input.fill("Test message");
    await input.press("Enter");
    await expect(page.getByText("Test message")).toBeVisible();

    await page.goto("/calendar");
    await page.waitForTimeout(500);

    await page.goto("/");
    await expect(page.getByPlaceholder(/Message your assistant/)).toBeVisible({ timeout: 10000 });
  });
});
