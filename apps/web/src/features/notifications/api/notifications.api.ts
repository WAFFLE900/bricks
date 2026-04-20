import apiClient from "@/shared/api/client";
import type { ProjectNotification } from "@/shared/types/domain";

export async function listNotifications() {
  const { data } = await apiClient.get<ProjectNotification[]>("/notifications");
  return data;
}

export async function markNotificationRead(notificationId: number) {
  const { data } = await apiClient.post<ProjectNotification>(`/notifications/${notificationId}/read`);
  return data;
}

export async function markAllNotificationsRead() {
  await apiClient.post("/notifications/read-all");
}
