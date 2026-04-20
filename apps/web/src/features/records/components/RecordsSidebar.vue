<template>
  <div class="sidebar">
    <RouterLink class="sidebar__brand" to="/projects">
      <img :src="logoUrl" alt="Bricks" />
    </RouterLink>

    <button class="sidebar__add" :disabled="!canCreate" type="button" @click="$emit('create')">
      <span class="sidebar__plus"></span>
      新增會議記錄
    </button>

    <button class="sidebar__back" type="button" @click="$emit('back')">返回專案列表</button>

    <div class="sidebar__section">
      <p class="sidebar__label">{{ projectTitle || `專案 ${projectId}` }}</p>
      <p v-if="!canCreate" class="sidebar__hint">目前僅有觀看權限</p>

      <div class="sidebar__records">
        <button
          v-for="record in records"
          :key="record.id"
          :class="['sidebar__record', { 'sidebar__record--active': selectedRecordId === record.id }]"
          type="button"
          @click="$emit('select', record.id)"
        >
          <strong>{{ record.record_name }}</strong>
          <span>{{ record.record_department || "未設定部門" }}</span>
        </button>

        <p v-if="loading" class="sidebar__empty">載入會議記錄中...</p>
        <p v-else-if="!records.length" class="sidebar__empty">目前還沒有會議記錄。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";

import logoUrl from "@/assets/legacy/brickslogo.svg";
import type { RecordItem } from "@/shared/types/domain";

withDefaults(
  defineProps<{
    canCreate?: boolean;
    loading?: boolean;
    projectId: number;
    projectTitle?: string;
    records: RecordItem[];
    selectedRecordId?: number | null;
  }>(),
  {
    canCreate: true,
    loading: false,
    projectTitle: "",
    selectedRecordId: null,
  },
);

defineEmits<{
  back: [];
  create: [];
  select: [recordId: number];
}>();
</script>

<style scoped>
.sidebar {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0.85rem 0 1.25rem;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.12);
}

.sidebar__brand {
  display: inline-flex;
  align-items: center;
  padding: 0 1rem;
  min-height: 48px;
}

.sidebar__brand img {
  width: auto;
  height: 2rem;
}

.sidebar__add {
  position: relative;
  margin: 0.75rem 1rem 0;
  border: 0;
  border-radius: 999px;
  padding: 0.95rem 1rem 0.95rem 3.35rem;
  background: #c91f2f;
  color: #fff;
  text-align: left;
  cursor: pointer;
}

.sidebar__add:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.sidebar__plus {
  position: absolute;
  top: 50%;
  left: 1.2rem;
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

.sidebar__back {
  margin: 0.85rem 1rem 0;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 0.75rem 1rem;
  background: #fff;
  text-align: left;
  cursor: pointer;
}

.sidebar__section {
  margin-top: 1rem;
  padding: 0 1rem;
}

.sidebar__label {
  margin: 0 0 0.35rem;
  color: #303133;
  font-weight: 600;
}

.sidebar__hint {
  margin: 0 0 0.85rem;
  color: #a15b61;
  font-size: 0.9rem;
}

.sidebar__records {
  display: grid;
  gap: 0.75rem;
}

.sidebar__record {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  background: #fff;
  padding: 0.85rem 0.95rem;
  text-align: left;
  cursor: pointer;
}

.sidebar__record strong,
.sidebar__record span {
  display: block;
}

.sidebar__record span {
  margin-top: 0.25rem;
  color: #7a7474;
}

.sidebar__record:hover,
.sidebar__record--active {
  background: #fae4e7;
  border-color: #f4cbcf;
}

.sidebar__empty {
  margin: 0;
  color: #7a7474;
}
</style>
