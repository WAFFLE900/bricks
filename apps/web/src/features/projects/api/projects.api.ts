import apiClient from "@/shared/api/client";
import type { Project, ProjectMemberPermission } from "@/shared/types/domain";

export async function listProjects(status: "active" | "ended" | "trash" | "all" = "active") {
  const { data } = await apiClient.get<Project[]>("/projects", { params: { status } });
  return data;
}

export async function createProject(payload: { project_name: string; project_type?: string }) {
  const { data } = await apiClient.post<Project>("/projects", payload);
  return data;
}

export async function getProject(projectId: number) {
  const { data } = await apiClient.get<Project>(`/projects/${projectId}`);
  return data;
}

export async function inviteProjectMember(
  projectId: number,
  payload: { user_email: string; permission: ProjectMemberPermission },
) {
  const { data } = await apiClient.post<Project>(`/projects/${projectId}/members`, payload);
  return data;
}

export async function updateProjectMemberPermission(
  projectId: number,
  memberUserId: number,
  payload: { permission: ProjectMemberPermission },
) {
  const { data } = await apiClient.patch<Project>(`/projects/${projectId}/members/${memberUserId}`, payload);
  return data;
}

export async function searchProjects(query: string, status: "active" | "ended" | "trash" | "all" = "all") {
  const { data } = await apiClient.get<{ items: Array<Project & { score: number }> }>("/search/projects", {
    params: { q: query, status },
  });
  return data.items;
}
