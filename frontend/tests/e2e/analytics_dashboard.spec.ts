import { test, expect } from "@playwright/test";

test("analytics dashboard pages expose MVP headings", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Behavior Summary" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Conversion Funnel" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Product Heat" })).toBeVisible();
});
