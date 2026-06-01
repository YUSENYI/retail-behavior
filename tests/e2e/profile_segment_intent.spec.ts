import { test, expect } from "@playwright/test";

test("profile, segment, and purchase intent pages are present", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "User Profile" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "User Segments" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Purchase Intent" })).toBeVisible();
});
