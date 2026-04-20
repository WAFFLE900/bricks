<template>
  <div ref="root" class="user-menu">
    <button class="user-menu__trigger" type="button" @click="isOpen = !isOpen">
      <span v-if="avatarUrl" class="user-menu__avatar user-menu__avatar--image">
        <img :src="avatarUrl" alt="" />
      </span>
      <span v-else class="user-menu__avatar">{{ initials }}</span>
      <span class="user-menu__meta">
        <strong>{{ displayName }}</strong>
        <small>{{ methodsSummary }}</small>
      </span>
    </button>

    <div v-if="isOpen" class="user-menu__dropdown">
      <div class="user-menu__panel">
        <strong>{{ displayName }}</strong>
        <p>{{ email }}</p>
      </div>

      <button class="user-menu__item" type="button" @click="goToProfile">個人頁面</button>
      <button class="user-menu__item user-menu__item--danger" type="button" @click="logout">登出</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/features/auth/stores/auth.store";

const authStore = useAuthStore();
const router = useRouter();
const isOpen = ref(false);
const root = ref<HTMLElement | null>(null);

const displayName = computed(() => authStore.user?.user_name || "未命名使用者");
const email = computed(() => authStore.user?.user_email || "");
const avatarUrl = computed(() => authStore.user?.user_avatar || "");
const initials = computed(() => displayName.value.trim().charAt(0).toUpperCase() || "U");
const methodsSummary = computed(() => {
  const total = [
    authStore.user?.has_password,
    authStore.user?.has_google_account,
    authStore.user?.has_facebook_account,
  ].filter(Boolean).length;

  return total ? `已啟用 ${total} 種登入方式` : "尚未設定登入方式";
});

function handleOutsideClick(event: MouseEvent) {
  if (!root.value?.contains(event.target as Node)) {
    isOpen.value = false;
  }
}

async function goToProfile() {
  isOpen.value = false;
  await router.push({ name: "profile" });
}

async function logout() {
  isOpen.value = false;
  authStore.logout();
  await router.push({ name: "login" });
}

onMounted(() => {
  document.addEventListener("mousedown", handleOutsideClick);
});

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", handleOutsideClick);
});
</script>

<style scoped>
.user-menu {
  position: relative;
}

.user-menu__trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  border: 0;
  border-radius: 999px;
  background: transparent;
  padding: 0.2rem 0.25rem;
  cursor: pointer;
}

.user-menu__trigger:hover {
  background: #f6f0f0;
}

.user-menu__avatar {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: #b82c30;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 700;
  overflow: hidden;
}

.user-menu__avatar--image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-menu__meta {
  display: grid;
  text-align: left;
  color: #303133;
}

.user-menu__meta strong {
  font-size: 0.92rem;
  line-height: 1.2;
}

.user-menu__meta small {
  color: #7a7474;
  font-size: 0.74rem;
}

.user-menu__dropdown {
  position: absolute;
  top: calc(100% + 0.65rem);
  right: 0;
  min-width: 14rem;
  border: 1px solid #e1dcdc;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 18px 36px rgba(18, 4, 6, 0.12);
  padding: 0.5rem;
  z-index: 30;
}

.user-menu__panel {
  border-radius: 12px;
  background: #f6f0f0;
  padding: 0.9rem;
}

.user-menu__panel strong,
.user-menu__panel p {
  display: block;
}

.user-menu__panel p {
  margin: 0.35rem 0 0;
  color: #7a7474;
  word-break: break-word;
}

.user-menu__item {
  width: 100%;
  border: 0;
  border-radius: 12px;
  background: transparent;
  padding: 0.8rem 0.9rem;
  text-align: left;
  cursor: pointer;
}

.user-menu__item:hover {
  background: #f6f0f0;
}

.user-menu__item--danger {
  color: #b82c30;
}

@media (max-width: 840px) {
  .user-menu__meta {
    display: none;
  }
}
</style>
