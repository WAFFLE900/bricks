import { defineStore } from "pinia";

import type { Project, ProjectMemberPermission } from "@/shared/types/domain";
import * as projectsApi from "../api/projects.api";

export const useProjectsStore = defineStore("projects", {
  state: () => ({
    items: [] as Project[],
    searchResults: [] as Array<Project & { score?: number }>,
    loading: false,
    status: "active" as "active" | "ended" | "trash" | "all",
  }),
  actions: {
    upsertProject(project: Project) {
      const index = this.items.findIndex((item) => item.id === project.id);
      if (index === -1) {
        this.items.unshift(project);
      } else {
        this.items.splice(index, 1, project);
      }
      return project;
    },
    async loadProjects(status: "active" | "ended" | "trash" | "all" = "active") {
      this.loading = true;
      try {
        this.status = status;
        this.items = await projectsApi.listProjects(status);
        return this.items;
      } finally {
        this.loading = false;
      }
    },
    async createProject(payload: { project_name: string; project_type?: string }) {
      const project = await projectsApi.createProject(payload);
      if (this.status === "active") {
        this.upsertProject(project);
      }
      return project;
    },
    async fetchProject(projectId: number) {
      const project = await projectsApi.getProject(projectId);
      this.upsertProject(project);
      return project;
    },
    async inviteMember(projectId: number, payload: { user_email: string; permission: ProjectMemberPermission }) {
      const project = await projectsApi.inviteProjectMember(projectId, payload);
      this.upsertProject(project);
      return project;
    },
    async updateMemberPermission(
      projectId: number,
      memberUserId: number,
      payload: { permission: ProjectMemberPermission },
    ) {
      const project = await projectsApi.updateProjectMemberPermission(projectId, memberUserId, payload);
      this.upsertProject(project);
      return project;
    },
    async searchProjects(query: string) {
      this.searchResults = await projectsApi.searchProjects(query, this.status);
      return this.searchResults;
    },
  },
});
