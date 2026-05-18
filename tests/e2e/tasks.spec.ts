import { test, expect } from "@playwright/test";

test.describe("Tasks page", () => {
  test("tasks page renders board", async ({ page }) => {
    await page.goto("/tasks");
    await expect(page.getByRole("heading", { name: "Tasks" })).toBeVisible();
    await expect(page.getByText("To Do")).toBeVisible();
    await expect(page.getByText("In Progress")).toBeVisible();
    await expect(page.getByText("Done")).toBeVisible();
  });

  test("has new task button", async ({ page }) => {
    await page.goto("/tasks");
    await expect(page.getByText("+ New Task")).toBeVisible();
  });

  test("new task button navigates to chat", async ({ page }) => {
    await page.goto("/tasks");
    await page.getByText("+ New Task").click();
    await expect(page.getByPlaceholder(/Message your assistant/)).toBeVisible({ timeout: 10000 });
  });
});
