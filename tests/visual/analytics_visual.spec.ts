import { test, expect } from "@playwright/test";

test("analytics visual states are visible", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByLabel("data freshness").first()).toContainText("Freshness");
});
