<template>
  <LegacyWorkspaceShell>
    <template #sidebar>
      <ProjectsSidebar :status="currentStatus" @create="openCreateModal" @select-status="load" />
    </template>

    <template #header>
      <LegacyWorkspaceToolbar
        v-model="searchQuery"
        :breadcrumbs="['BRICKS', statusLabel]"
        :history="searchHistory"
        :history-visible="showSearchHistory"
        placeholder="搜尋專案"
        @blur="hideHistory"
        @clear="clearSearch"
        @focus="showSearchHistory = true"
        @history-select="selectHistory"
        @submit="submitSearch"
      />
    </template>

    <section class="projects-page">
      <div v-if="isCreateOpen || managedProject" class="projects-page__overlay" @click="closeModals"></div>

      <div v-if="isCreateOpen" class="projects-page__modal">
        <ProjectCreateModal
          :loading="projectsStore.loading"
          :types="availableTypes"
          @close="isCreateOpen = false"
          @submit="createProject"
        />
      </div>

      <div v-if="managedProject" class="projects-page__modal projects-page__modal--wide">
        <ProjectMembersModal
          :error-message="memberActionError"
          :loading="memberActionLoading"
          :project="managedProject"
          @close="closeMembersModal"
          @invite="inviteMember"
          @update-permission="changeMemberPermission"
        />
      </div>

      <section class="projects-page__hero">
        <div>
          <p class="projects-page__eyebrow">專案</p>
          <h1>{{ statusLabel }}</h1>
          <p class="projects-page__copy">
            你可以邀請其他成員加入同一個專案，並分別設定成每個人只能觀看或可以編輯。
          </p>
        </div>
        <button class="projects-page__cta" type="button" @click="openCreateModal">新增專案</button>
      </section>

      <section v-if="searchQuery" class="projects-page__search">
        <div class="projects-page__section-title">
          <h2>搜尋結果</h2>
          <p>共 {{ projectsStore.searchResults.length }} 筆</p>
        </div>

        <div v-if="projectsStore.searchResults.length" class="projects-page__search-results">
          <RouterLink
            v-for="project in projectsStore.searchResults"
            :key="`search-${project.id}`"
            class="projects-page__search-item"
            :to="{ name: 'records', params: { projectId: project.id } }"
          >
            <strong>{{ project.project_name }}</strong>
            <span>{{ project.project_type || "未分類" }}</span>
            <small>{{ permissionLabels[project.current_user_permission] }}</small>
          </RouterLink>
        </div>
        <p v-else class="projects-page__empty">找不到符合的專案。</p>
      </section>

      <div v-if="projectsStore.loading" class="projects-page__empty">載入專案中...</div>
      <div v-else class="projects-page__groups">
        <ProjectTypeGroup
          title="未分類"
          :projects="uncategorizedProjects"
          variant="muted"
          @manage-members="openMembersModal"
        />
        <ProjectTypeGroup
          v-for="group in groupedProjects"
          :key="group.title"
          :projects="group.projects"
          :title="group.title"
          @manage-members="openMembersModal"
        />
        <div v-if="!projectsStore.items.length" class="projects-page__empty">
          目前還沒有專案，先建立一個專案再邀請協作者加入吧。
        </div>
      </div>
    </section>
  </LegacyWorkspaceShell>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import LegacyWorkspaceShell from "@/shared/ui/legacy/LegacyWorkspaceShell.vue";
import LegacyWorkspaceToolbar from "@/shared/ui/legacy/LegacyWorkspaceToolbar.vue";
import type { Project, ProjectMemberPermission } from "@/shared/types/domain";
import { getApiErrorMessage } from "@/shared/utils/getApiErrorMessage";
import ProjectCreateModal from "../components/ProjectCreateModal.vue";
import ProjectMembersModal from "../components/ProjectMembersModal.vue";
import ProjectsSidebar from "../components/ProjectsSidebar.vue";
import ProjectTypeGroup from "../components/ProjectTypeGroup.vue";
import { useProjectsStore } from "../stores/projects.store";

type ProjectStatus = "active" | "ended" | "trash" | "all";

const HISTORY_KEY = "bricks-project-search-history";

const projectsStore = useProjectsStore();
const currentStatus = ref<ProjectStatus>(projectsStore.status);
const hideHistoryTimer = ref<number>();
const isCreateOpen = ref(false);
const managedProject = ref<Project | null>(null);
const memberActionLoading = ref(false);
const memberActionError = ref("");
const searchQuery = ref("");
const searchHistory = ref<string[]>(loadHistory());
const showSearchHistory = ref(false);

const statusLabels: Record<ProjectStatus, string> = {
  active: "進行中的專案",
  all: "全部專案",
  ended: "已結束的專案",
  trash: "垃圾桶",
};

const permissionLabels = {
  owner: "建立者",
  edit: "可編輯",
  view: "可觀看",
} as const;

const statusLabel = computed(() => statusLabels[currentStatus.value]);

const uncategorizedProjects = computed(() =>
  projectsStore.items.filter((project) => !project.project_type?.trim()),
);

const groupedProjects = computed(() => {
  const groups = new Map<string, Project[]>();

  for (const project of projectsStore.items) {
    const title = project.project_type?.trim();
    if (!title) {
      continue;
    }

    const bucket = groups.get(title) || [];
    bucket.push(project);
    groups.set(title, bucket);
  }

  return Array.from(groups.entries()).map(([title, projects]) => ({ title, projects }));
});

const availableTypes = computed(() => groupedProjects.value.map((group) => group.title));

function loadHistory() {
  try {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    return raw ? (JSON.parse(raw) as string[]) : [];
  } catch {
    return [];
  }
}

function saveHistory(value: string) {
  searchHistory.value = [value, ...searchHistory.value.filter((entry) => entry !== value)].slice(0, 6);
  window.localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value));
}

function hideHistory() {
  hideHistoryTimer.value = window.setTimeout(() => {
    showSearchHistory.value = false;
  }, 120);
}

function openCreateModal() {
  managedProject.value = null;
  memberActionError.value = "";
  isCreateOpen.value = true;
}

function closeModals() {
  isCreateOpen.value = false;
  managedProject.value = null;
  memberActionError.value = "";
}

function closeMembersModal() {
  managedProject.value = null;
  memberActionError.value = "";
}

async function load(status: ProjectStatus = currentStatus.value) {
  currentStatus.value = status;
  showSearchHistory.value = false;
  await projectsStore.loadProjects(status);
}

async function submitSearch() {
  const value = searchQuery.value.trim();
  if (!value) {
    clearSearch();
    return;
  }

  saveHistory(value);
  showSearchHistory.value = false;
  await projectsStore.searchProjects(value);
}

function clearSearch() {
  searchQuery.value = "";
  showSearchHistory.value = false;
  projectsStore.searchResults = [];
}

function selectHistory(value: string) {
  window.clearTimeout(hideHistoryTimer.value);
  searchQuery.value = value;
  void submitSearch();
}

async function createProject(payload: { project_name: string; project_type?: string }) {
  if (!payload.project_name.trim()) {
    return;
  }

  await projectsStore.createProject(payload);
  isCreateOpen.value = false;
  clearSearch();
  await load("active");
}

async function openMembersModal(projectId: number) {
  memberActionLoading.value = true;
  memberActionError.value = "";
  try {
    managedProject.value = await projectsStore.fetchProject(projectId);
    isCreateOpen.value = false;
  } catch (error) {
    memberActionError.value = getApiErrorMessage(error, "無法載入專案成員。");
  } finally {
    memberActionLoading.value = false;
  }
}

async function inviteMember(payload: { user_email: string; permission: ProjectMemberPermission }) {
  if (!managedProject.value) {
    return;
  }

  memberActionLoading.value = true;
  memberActionError.value = "";
  try {
    managedProject.value = await projectsStore.inviteMember(managedProject.value.id, payload);
  } catch (error) {
    memberActionError.value = getApiErrorMessage(error, "邀請成員失敗。");
  } finally {
    memberActionLoading.value = false;
  }
}

async function changeMemberPermission(payload: { memberUserId: number; permission: ProjectMemberPermission }) {
  if (!managedProject.value) {
    return;
  }

  memberActionLoading.value = true;
  memberActionError.value = "";
  try {
    managedProject.value = await projectsStore.updateMemberPermission(
      managedProject.value.id,
      payload.memberUserId,
      { permission: payload.permission },
    );
  } catch (error) {
    memberActionError.value = getApiErrorMessage(error, "更新成員權限失敗。");
  } finally {
    memberActionLoading.value = false;
  }
}

onMounted(async () => {
  await load(currentStatus.value);
});

onBeforeUnmount(() => {
  window.clearTimeout(hideHistoryTimer.value);
});
</script>

<style scoped>
.projects-page {
  position: relative;
  min-height: 100%;
  display: grid;
  gap: 1.5rem;
}

.projects-page__overlay {
  position: fixed;
  inset: 0;
  background: rgba(59, 56, 56, 0.55);
  z-index: 15;
}

.projects-page__modal {
  position: fixed;
  inset: 50% auto auto 50%;
  z-index: 16;
  transform: translate(-50%, -50%);
}

.projects-page__modal--wide {
  width: min(40rem, calc(100vw - 2rem));
}

.projects-page__hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border: 1px solid #e1dcdc;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.82);
  padding: 1.5rem 1.75rem;
}

.projects-page__eyebrow {
  margin: 0 0 0.35rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #b6aeae;
}

.projects-page__hero h1 {
  margin: 0;
  font-size: clamp(2rem, 3.3vw, 3rem);
}

.projects-page__copy {
  margin: 0.6rem 0 0;
  color: #5c5454;
  max-width: 44rem;
}

.projects-page__cta {
  border: 0;
  border-radius: 999px;
  padding: 0.95rem 1.5rem;
  background: #b82c30;
  color: #fff;
  cursor: pointer;
}

.projects-page__cta:hover {
  background: #d48083;
}

.projects-page__search,
.projects-page__groups {
  display: grid;
  gap: 1rem;
}

.projects-page__section-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
}

.projects-page__section-title h2 {
  margin: 0;
}

.projects-page__section-title p {
  margin: 0;
  color: #7a7474;
}

.projects-page__search-results {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
}

.projects-page__search-item {
  min-width: min(17rem, 100%);
  flex: 1 1 17rem;
  border: 1px solid #e1dcdc;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.88);
  padding: 1rem 1.15rem;
  text-decoration: none;
}

.projects-page__search-item strong,
.projects-page__search-item span,
.projects-page__search-item small {
  display: block;
}

.projects-page__search-item span,
.projects-page__search-item small {
  margin-top: 0.25rem;
  color: #7a7474;
}

.projects-page__empty {
  border: 1px dashed #c7c2c2;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.55);
  padding: 1.25rem;
  text-align: center;
  color: #7a7474;
}

@media (max-width: 900px) {
  .projects-page__hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .projects-page__cta {
    width: 100%;
  }
}
</style>
