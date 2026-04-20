<template>
  <div class="toolbar">
    <div class="toolbar__breadcrumb" aria-label="Breadcrumb">
      <span
        v-for="(item, index) in breadcrumbs"
        :key="`${item}-${index}`"
        :class="['toolbar__crumb', { 'toolbar__crumb--active': index === breadcrumbs.length - 1 }]"
      >
        {{ item }}
      </span>
    </div>

    <div class="toolbar__actions">
      <form v-if="showSearch" class="toolbar__search" @submit.prevent="$emit('submit')">
        <img class="toolbar__icon toolbar__icon--search" :src="searchIconUrl" alt="" />
        <input
          aria-label="搜尋"
          :placeholder="placeholder"
          :value="modelValue"
          @input="onInput"
          @focus="$emit('focus')"
          @blur="$emit('blur')"
          @keyup.enter="$emit('submit')"
        />
        <button
          v-if="modelValue"
          aria-label="清除搜尋"
          class="toolbar__clear"
          type="button"
          @click="$emit('clear')"
        ></button>

        <div v-if="historyVisible && history.length" class="toolbar__history">
          <button
            v-for="entry in history"
            :key="entry"
            class="toolbar__history-item"
            type="button"
            @mousedown.prevent="$emit('historySelect', entry)"
          >
            {{ entry }}
          </button>
        </div>
      </form>

      <div class="toolbar__notifications">
        <button class="toolbar__notice-button" type="button" @click="toggleNotifications">
          <img class="toolbar__icon toolbar__icon--action" :src="noticeIconUrl" alt="通知" />
          <span v-if="notificationsStore.unreadCount" class="toolbar__notice-badge">
            {{ notificationsStore.unreadCount }}
          </span>
        </button>

        <div v-if="notificationsOpen" class="toolbar__notice-panel">
          <div class="toolbar__notice-header">
            <strong>通知</strong>
            <button
              v-if="notificationsStore.unreadCount"
              class="toolbar__notice-link"
              type="button"
              @click="markAllRead"
            >
              全部標示為已讀
            </button>
          </div>

          <div v-if="notificationsStore.loading" class="toolbar__notice-empty">載入中...</div>
          <div v-else-if="notificationsStore.items.length" class="toolbar__notice-list">
            <RouterLink
              v-for="notification in notificationsStore.items"
              :key="notification.id"
              class="toolbar__notice-item"
              :class="{ 'toolbar__notice-item--unread': !notification.is_read }"
              :to="{ name: 'records', params: { projectId: notification.project_id } }"
              @click="handleNotificationClick(notification.id, notification.is_read)"
            >
              <strong>{{ notification.notification_title }}</strong>
              <span>{{ notification.notification_body }}</span>
              <small>{{ formatDate(notification.created_at) }}</small>
            </RouterLink>
          </div>
          <div v-else class="toolbar__notice-empty">目前沒有通知。</div>
        </div>
      </div>

      <LegacyWorkspaceUserMenu />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import noticeIconUrl from "@/assets/legacy/Notice/Notice_Default.svg";
import searchIconUrl from "@/assets/legacy/search.svg";
import { useNotificationsStore } from "@/features/notifications/stores/notifications.store";
import { formatDate } from "@/shared/utils/formatDate";
import LegacyWorkspaceUserMenu from "./LegacyWorkspaceUserMenu.vue";

withDefaults(
  defineProps<{
    modelValue: string;
    breadcrumbs: string[];
    placeholder?: string;
    history?: string[];
    historyVisible?: boolean;
    showSearch?: boolean;
  }>(),
  {
    placeholder: "搜尋",
    history: () => [],
    historyVisible: false,
    showSearch: true,
  },
);

const emit = defineEmits<{
  "update:modelValue": [value: string];
  blur: [];
  clear: [];
  focus: [];
  historySelect: [value: string];
  submit: [];
}>();

const notificationsStore = useNotificationsStore();
const notificationsOpen = ref(false);

function onInput(event: Event) {
  emit("update:modelValue", (event.target as HTMLInputElement).value);
}

async function toggleNotifications() {
  notificationsOpen.value = !notificationsOpen.value;
  if (notificationsOpen.value) {
    await notificationsStore.load(true);
  }
}

async function handleNotificationClick(notificationId: number, isRead: boolean) {
  notificationsOpen.value = false;
  if (!isRead) {
    await notificationsStore.markRead(notificationId);
  }
}

async function markAllRead() {
  await notificationsStore.markAllRead();
}

onMounted(() => {
  void notificationsStore.load();
});
</script>

<style scoped>
.toolbar {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0 1rem;
  background: #fff;
}

.toolbar__breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #909399;
  font-size: 0.9rem;
}

.toolbar__crumb::after {
  content: "/";
  margin-left: 0.5rem;
  color: #c7c2c2;
}

.toolbar__crumb:last-child::after {
  display: none;
}

.toolbar__crumb--active {
  color: #303133;
}

.toolbar__actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.toolbar__search {
  position: relative;
  width: min(320px, 48vw);
}

.toolbar__search input {
  width: 100%;
  border: 1px solid transparent;
  border-radius: 999px;
  background: #f2eeee;
  padding: 0.45rem 2.5rem 0.45rem 2.6rem;
  font-size: 0.95rem;
  outline: none;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease;
}

.toolbar__search input:hover {
  background: #e1dcdc;
}

.toolbar__search input:focus {
  background: #fff;
  border-color: #c7c2c2;
}

.toolbar__icon {
  user-select: none;
  -webkit-user-drag: none;
}

.toolbar__icon--search {
  position: absolute;
  top: 50%;
  left: 0.9rem;
  transform: translateY(-50%);
}

.toolbar__icon--action {
  width: 20px;
  height: 20px;
}

.toolbar__clear {
  position: absolute;
  top: 50%;
  right: 0.85rem;
  width: 0.95rem;
  height: 0.95rem;
  border: 0;
  background: transparent;
  cursor: pointer;
  transform: translateY(-50%);
}

.toolbar__clear::before,
.toolbar__clear::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 14px;
  background: #3b3838;
}

.toolbar__clear::before {
  transform: translate(-50%, -50%) rotate(45deg);
}

.toolbar__clear::after {
  transform: translate(-50%, -50%) rotate(-45deg);
}

.toolbar__history {
  position: absolute;
  top: calc(100% + 0.35rem);
  left: 0;
  width: 100%;
  border-radius: 14px;
  background: #fff;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.3),
    0 2px 15px rgba(0, 0, 0, 0.15);
  padding: 0.35rem 0;
  z-index: 20;
}

.toolbar__history-item {
  display: block;
  width: 100%;
  border: 0;
  background: transparent;
  padding: 0.75rem 1rem;
  text-align: left;
  cursor: pointer;
}

.toolbar__history-item:hover {
  background: #f2eeee;
}

.toolbar__notifications {
  position: relative;
}

.toolbar__notice-button {
  position: relative;
  border: 0;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.toolbar__notice-badge {
  position: absolute;
  top: -0.35rem;
  right: -0.45rem;
  min-width: 1rem;
  height: 1rem;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: #c91f2f;
  color: #fff;
  font-size: 0.7rem;
  padding: 0 0.2rem;
}

.toolbar__notice-panel {
  position: absolute;
  top: calc(100% + 0.6rem);
  right: 0;
  width: min(26rem, calc(100vw - 2rem));
  border: 1px solid #ebe4e4;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.14);
  padding: 0.85rem;
  z-index: 30;
}

.toolbar__notice-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.6rem;
}

.toolbar__notice-link {
  border: 0;
  background: transparent;
  color: #9f2931;
  cursor: pointer;
}

.toolbar__notice-list {
  display: grid;
  gap: 0.5rem;
}

.toolbar__notice-item {
  display: grid;
  gap: 0.25rem;
  border-radius: 14px;
  padding: 0.8rem;
  text-decoration: none;
  background: #fbf7f7;
}

.toolbar__notice-item--unread {
  background: #fae4e7;
}

.toolbar__notice-item strong {
  color: #120406;
}

.toolbar__notice-item span,
.toolbar__notice-item small {
  color: #6d6666;
}

.toolbar__notice-empty {
  color: #7a7474;
  padding: 0.85rem 0.2rem 0.35rem;
}

@media (max-width: 920px) {
  .toolbar {
    height: auto;
    padding: 0.75rem 1rem;
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar__actions {
    width: 100%;
    justify-content: space-between;
  }

  .toolbar__search {
    width: 100%;
  }
}
</style>
