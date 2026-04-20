import { defineStore } from "pinia";

import type { ProjectNotification } from "@/shared/types/domain";
import * as notificationsApi from "../api/notifications.api";

export const useNotificationsStore = defineStore("notifications", {
  state: () => ({
    items: [] as ProjectNotification[],
    loaded: false,
    loading: false,
  }),
  getters: {
    unreadCount: (state) => state.items.filter((item) => !item.is_read).length,
  },
  actions: {
    async load(force = false) {
      if (this.loading || (this.loaded && !force)) {
        return this.items;
      }

      this.loading = true;
      try {
        this.items = await notificationsApi.listNotifications();
        this.loaded = true;
        return this.items;
      } finally {
        this.loading = false;
      }
    },
    async markRead(notificationId: number) {
      const notification = await notificationsApi.markNotificationRead(notificationId);
      const index = this.items.findIndex((item) => item.id === notificationId);
      if (index >= 0) {
        this.items.splice(index, 1, notification);
      }
      return notification;
    },
    async markAllRead() {
      await notificationsApi.markAllNotificationsRead();
      this.items = this.items.map((item) => ({ ...item, is_read: true }));
    },
  },
});
