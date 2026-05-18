import { test, expect } from "@playwright/test";

test.describe("Tasks page", () => {
  test("tasks page renders board", async ({ page }) => {
    await page.goto("/tasks");
    await expect(page.getByText("Tasks")).toBeVisible();
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
    await expect(page.getByPlaceholderText(/Schedule a meeting/)).toBeVisible();
  });
});
