<template>
  <section :class="['group', { 'group--muted': variant === 'muted' }]">
    <div class="group__heading">
      <p>{{ title }}</p>
      <div class="group__line"></div>
    </div>

    <div v-if="projects.length" class="group__boxes">
      <article v-for="project in projects" :key="project.id" class="group__box">
        <RouterLink
          :title="formatDate(project.project_edit_date)"
          class="group__link"
          :to="{ name: 'records', params: { projectId: project.id } }"
        >
          <span class="group__dot"></span>
          <div class="group__copy">
            <strong class="group__label">{{ project.project_name }}</strong>
            <span class="group__meta">
              {{ permissionLabels[project.current_user_permission] }} · {{ project.member_count }} 位成員
            </span>
            <span class="group__meta">建立者：{{ project.owner_name }}</span>
          </div>
        </RouterLink>

        <button
          v-if="project.can_manage_members"
          class="group__manage"
          type="button"
          @click="$emit('manageMembers', project.id)"
        >
          管理成員
        </button>
      </article>
    </div>

    <p v-else class="group__empty">這個分類目前還沒有專案。</p>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";

import type { Project } from "@/shared/types/domain";
import { formatDate } from "@/shared/utils/formatDate";

withDefaults(
  defineProps<{
    title: string;
    projects: Project[];
    variant?: "plain" | "muted";
  }>(),
  {
    variant: "plain",
  },
);

defineEmits<{
  manageMembers: [projectId: number];
}>();

const permissionLabels = {
  owner: "建立者",
  edit: "可編輯",
  view: "可觀看",
} as const;
</script>

<style scoped>
.group {
  border: 1px solid #e1dcdc;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
  padding: 1.4rem 1.5rem 1.7rem;
}

.group--muted {
  background: #f2eeee;
}

.group__heading {
  display: grid;
  gap: 0.5rem;
}

.group__heading p {
  margin: 0;
  font-size: 1rem;
}

.group__line {
  width: min(19rem, 100%);
  border-bottom: 1px solid #c7c2c2;
}

.group__boxes {
  margin-top: 1.5rem;
  display: grid;
  gap: 0.85rem;
}

.group__box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border: 1.5px solid #e1dcdc;
  border-radius: 13px;
  background: #fff;
  padding: 0.95rem 1rem;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    transform 0.2s ease;
}

.group__box:hover {
  background: #f8f3f3;
  border-color: #c7c2c2;
  transform: translateY(-1px);
}

.group__link {
  min-width: 0;
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  text-decoration: none;
}

.group__dot {
  width: 0.9rem;
  height: 0.9rem;
  border-radius: 999px;
  background: #b82c30;
  flex: 0 0 auto;
}

.group__copy {
  min-width: 0;
  display: grid;
  gap: 0.2rem;
}

.group__label {
  display: block;
  color: #120406;
  letter-spacing: 0.05em;
}

.group__meta {
  color: #6d6666;
  font-size: 0.9rem;
}

.group__manage {
  flex: 0 0 auto;
  border: 1px solid #d9b8ba;
  border-radius: 999px;
  background: #fff6f6;
  color: #9f2931;
  padding: 0.65rem 1rem;
  cursor: pointer;
}

.group__manage:hover {
  background: #fae4e7;
}

.group__empty {
  margin: 1.5rem 0 0;
  color: #7a7474;
}

@media (max-width: 900px) {
  .group__box {
    flex-direction: column;
    align-items: stretch;
  }

  .group__manage {
    width: 100%;
  }
}
</style>
