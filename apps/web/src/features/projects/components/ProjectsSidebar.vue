<template>
  <div class="sidebar">
    <RouterLink class="sidebar__brand" to="/">
      <img :src="logoUrl" alt="Bricks" />
    </RouterLink>

    <button class="sidebar__add" type="button" @click="$emit('create')">
      <span class="sidebar__plus"></span>
      新增專案
    </button>

    <nav class="sidebar__nav" aria-label="專案狀態">
      <button
        v-for="item in items"
        :key="item.value"
        :class="['sidebar__link', { 'sidebar__link--active': status === item.value }]"
        type="button"
        @click="$emit('selectStatus', item.value)"
      >
        <img :src="item.icon" alt="" />
        <span>{{ item.label }}</span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";

import logoUrl from "@/assets/legacy/brickslogo.svg";
import activeIconUrl from "@/assets/legacy/icon/icon_file.svg";
import endedIconUrl from "@/assets/legacy/icon/icon_over.svg";
import trashIconUrl from "@/assets/legacy/icon/icon_trashcan.svg";

defineProps<{
  status: "active" | "ended" | "trash" | "all";
}>();

defineEmits<{
  create: [];
  selectStatus: [value: "active" | "ended" | "trash"];
}>();

const items = [
  { label: "進行中", value: "active" as const, icon: activeIconUrl },
  { label: "已結束", value: "ended" as const, icon: endedIconUrl },
  { label: "垃圾桶", value: "trash" as const, icon: trashIconUrl },
];
</script>

<style scoped>
.sidebar {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0.85rem 0 1.5rem;
  background: #f2eeee;
  border-radius: 0 14px 14px 0;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.18);
}

.sidebar__brand {
  display: inline-flex;
  align-items: center;
  padding: 0 1.5rem;
  min-height: 48px;
}

.sidebar__brand img {
  width: auto;
  height: 2rem;
}

.sidebar__add {
  position: relative;
  margin: 2rem 2.75rem 0;
  border: 0;
  border-radius: 999px;
  padding: 1.2rem 1.5rem 1.2rem 3.9rem;
  background: #b82c30;
  color: #fff;
  font-size: 1.05rem;
  letter-spacing: 0.08em;
  text-align: left;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.28);
  cursor: pointer;
}

.sidebar__add:hover {
  background: #d48083;
}

.sidebar__plus {
  position: absolute;
  top: 50%;
  left: 1.5rem;
  width: 1rem;
  height: 1rem;
  transform: translateY(-50%);
}

.sidebar__plus::before,
.sidebar__plus::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #fff;
  transform: translate(-50%, -50%);
}

.sidebar__plus::after {
  transform: translate(-50%, -50%) rotate(90deg);
}

.sidebar__nav {
  margin-top: 1.5rem;
}

.sidebar__link {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 0;
  background: transparent;
  padding: 1.3rem 1.75rem;
  font-size: 1.05rem;
  text-align: left;
  cursor: pointer;
}

.sidebar__link img {
  width: 1.25rem;
  height: 1.25rem;
}

.sidebar__link:hover,
.sidebar__link--active {
  background: #e1dcdc;
}

@media (max-width: 1100px) {
  .sidebar {
    border-radius: 0;
  }
}
</style>
