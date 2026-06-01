import { test, expect } from "@playwright/test";

test("reports and audit pages are present", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Reports" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Audit Logs" })).toBeVisible();
});
