import { expect, test } from "@playwright/test";

test("login to project dashboard and open records workspace", async ({ page }) => {
  await page.route("**/api/v1/auth/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "token-123",
        token_type: "bearer",
        user: {
          id: 1,
          user_email: "jane@example.com",
          user_name: "Jane",
          user_identity: "founder",
        },
      }),
    });
  });

  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        user_email: "jane@example.com",
        user_name: "Jane",
        user_identity: "founder",
      }),
    });
  });

  await page.route("**/api/v1/projects?status=active", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: 7,
          project_name: "Rewrite Bricks",
          project_type: "Roadmap",
          project_image: null,
          project_trashcan: false,
          project_ended: false,
          project_edit: true,
          project_visible: true,
          project_comment: true,
          project_creation_date: new Date().toISOString(),
          project_edit_date: new Date().toISOString(),
        },
      ]),
    });
  });

  await page.route("**/api/v1/projects/7/records?include_trashed=false", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: 11,
          record_name: "Sprint Sync",
          record_date: null,
          record_department: "Product",
          record_attendances: 4,
          record_place: "Room A",
          record_host_name: "Jane",
          record_trashcan: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          tags: [],
          text_boxes: [],
        },
      ]),
    });
  });

  await page.route("**/api/v1/projects/7/records/11", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 11,
        record_name: "Sprint Sync",
        record_date: null,
        record_department: "Product",
        record_attendances: 4,
        record_place: "Room A",
        record_host_name: "Jane",
        record_trashcan: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        tags: [],
        text_boxes: [],
      }),
    });
  });

  await page.goto("/login");
  await page.getByLabel("Email").fill("jane@example.com");
  await page.getByLabel("Password").fill("super-secret");
  await page.getByRole("button", { name: "Login" }).click();

  await expect(page.getByRole("heading", { name: "Workspace dashboard" })).toBeVisible();
  await page.getByRole("link", { name: /Rewrite Bricks/i }).click();
  await expect(page.getByRole("heading", { name: /record workspace/i })).toBeVisible();
});
