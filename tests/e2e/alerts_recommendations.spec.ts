import { test, expect } from "@playwright/test";

test("alerts and recommendation analysis pages are present", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Alerts" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Recommendation Analysis" })).toBeVisible();
});
