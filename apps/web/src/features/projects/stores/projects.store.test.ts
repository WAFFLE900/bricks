import { createPinia, setActivePinia } from "pinia";
import { describe, expect, it, vi } from "vitest";

import { useProjectsStore } from "./projects.store";

vi.mock("../api/projects.api", () => ({
  listProjects: vi.fn(async () => [
    {
      id: 1,
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
  createProject: vi.fn(),
  searchProjects: vi.fn(async () => []),
}));

describe("projects store", () => {
  it("loads project list from the shared API layer", async () => {
    setActivePinia(createPinia());
    const store = useProjectsStore();

    const items = await store.loadProjects("active");

    expect(items).toHaveLength(1);
    expect(items[0].project_name).toBe("Rewrite Bricks");
  });
});

