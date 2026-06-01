import { test, expect } from "@playwright/test";

test("behavior journey page exposes filters and journey surface", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Behavior Events" })).toBeVisible();
  await expect(page.getByLabel("current filters").first()).toContainText("timeRange");
});
