<template>
  <LegacyWorkspaceShell>
    <template #sidebar>
      <RecordsSidebar
        :can-create="canEditContent"
        :loading="recordsStore.loading"
        :project-id="projectId"
        :project-title="recordsStore.project?.project_name"
        :records="filteredRecords"
        :selected-record-id="recordsStore.selectedRecord?.id"
        @back="router.push({ name: 'projects' })"
        @create="openCreateModal"
        @select="openRecord"
      />
    </template>

    <template #header>
      <LegacyWorkspaceToolbar
        v-model="searchQuery"
        :breadcrumbs="breadcrumbs"
        :history="searchHistory"
        :history-visible="showSearchHistory"
        placeholder="搜尋會議記錄"
        @blur="hideHistory"
        @clear="clearSearch"
        @focus="showSearchHistory = true"
        @history-select="selectHistory"
        @submit="submitSearch"
      />
    </template>

    <section class="records-page">
      <div v-if="isCreateOpen" class="records-page__overlay" @click="isCreateOpen = false"></div>
      <div v-if="isCreateOpen" class="records-page__modal">
        <RecordCreateModal :loading="recordsStore.loading" @close="isCreateOpen = false" @submit="createRecord" />
      </div>

      <template v-if="recordsStore.selectedRecord">
        <section class="records-page__hero">
          <div>
            <p class="records-page__eyebrow">會議記錄</p>
            <h1>{{ recordsStore.selectedRecord.record_name }}</h1>
            <p class="records-page__copy">
              {{ recordsStore.project?.project_name || `專案 ${projectId}` }} · {{ permissionLabel }}
            </p>
          </div>
          <button class="records-page__cta" :disabled="!canEditContent" type="button" @click="openCreateModal">
            新增會議記錄
          </button>
        </section>

        <div class="records-page__layout">
          <article class="records-page__summary">
            <table>
              <tbody>
                <tr>
                  <th>會議名稱</th>
                  <td>{{ recordsStore.selectedRecord.record_name }}</td>
                </tr>
                <tr>
                  <th>日期</th>
                  <td>{{ recordsStore.selectedRecord.record_date || "未設定" }}</td>
                </tr>
                <tr>
                  <th>出席人數</th>
                  <td>{{ recordsStore.selectedRecord.record_attendances ?? "-" }}</td>
                </tr>
                <tr>
                  <th>地點</th>
                  <td>{{ recordsStore.selectedRecord.record_place || "-" }}</td>
                </tr>
                <tr>
                  <th>主持人</th>
                  <td>{{ recordsStore.selectedRecord.record_host_name || "-" }}</td>
                </tr>
                <tr>
                  <th>最後更新</th>
                  <td>{{ formatDate(recordsStore.selectedRecord.updated_at) }}</td>
                </tr>
              </tbody>
            </table>
          </article>

          <section class="records-page__content">
            <form class="records-page__composer" @submit.prevent="createTextBox">
              <textarea
                ref="composerTextarea"
                v-model="newTextBox"
                :disabled="!canEditContent"
                :placeholder="
                  canEditContent
                    ? '輸入文字內容，並可在儲存前使用 @成員名稱 標記專案成員。'
                    : '你目前只有觀看權限，無法新增文字區塊。'
                "
              ></textarea>

              <div v-if="canEditContent && mentionableMembers.length" class="records-page__mentions">
                <p class="records-page__mention-copy">
                  可在內容中輸入 <code>@成員名稱</code>，或直接點選下方成員加入 mention。只有按下儲存後才會送出通知。
                </p>
                <div class="records-page__mention-list">
                  <button
                    v-for="member in mentionableMembers"
                    :key="member.user_id"
                    class="records-page__mention-chip"
                    type="button"
                    @click="insertMention(member.user_name)"
                  >
                    @{{ member.user_name }}
                  </button>
                </div>
              </div>

              <button :disabled="!canEditContent" type="submit">儲存文字區塊</button>
            </form>

            <p v-if="!canEditContent" class="records-page__hint">
              這個專案目前只分享給你觀看，你可以閱讀內容，但只有可編輯成員才能新增或修改文字區塊。
            </p>

            <div class="records-page__blocks">
              <RecordTextBlockCard
                v-for="textBox in recordsStore.selectedRecord.text_boxes"
                :key="textBox.id"
                :can-edit="canEditContent"
                :text-box="textBox"
              />
              <div v-if="!recordsStore.selectedRecord.text_boxes.length" class="records-page__empty">
                目前還沒有任何文字區塊。
              </div>
            </div>
          </section>
        </div>
      </template>

      <div v-else class="records-page__empty">請先從左側選擇一筆會議記錄。</div>
    </section>
  </LegacyWorkspaceShell>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/features/auth/stores/auth.store";
import LegacyWorkspaceShell from "@/shared/ui/legacy/LegacyWorkspaceShell.vue";
import LegacyWorkspaceToolbar from "@/shared/ui/legacy/LegacyWorkspaceToolbar.vue";
import { formatDate } from "@/shared/utils/formatDate";
import RecordCreateModal from "../components/RecordCreateModal.vue";
import RecordsSidebar from "../components/RecordsSidebar.vue";
import RecordTextBlockCard from "../components/RecordTextBlockCard.vue";
import { useRecordsStore } from "../stores/records.store";

const HISTORY_KEY = "bricks-record-search-history";

const props = defineProps<{
  projectId: string;
}>();

const router = useRouter();
const authStore = useAuthStore();
const recordsStore = useRecordsStore();
const composerTextarea = ref<HTMLTextAreaElement | null>(null);
const hideHistoryTimer = ref<number>();
const isCreateOpen = ref(false);
const newTextBox = ref("");
const searchQuery = ref("");
const searchHistory = ref<string[]>(loadHistory());
const showSearchHistory = ref(false);

const projectId = computed(() => Number(props.projectId));
const canEditContent = computed(() => recordsStore.project?.can_edit_content ?? false);
const mentionableMembers = computed(() =>
  (recordsStore.project?.members || []).filter((member) => member.user_id !== authStore.user?.id),
);
const permissionLabel = computed(() => {
  const permission = recordsStore.project?.current_user_permission;
  if (permission === "owner") {
    return "建立者";
  }
  if (permission === "edit") {
    return "可編輯";
  }
  return "可觀看";
});
const breadcrumbs = computed(() => [
  "專案",
  recordsStore.project?.project_name || `專案 ${projectId.value}`,
  "會議記錄",
]);

const filteredRecords = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase();
  if (!keyword) {
    return recordsStore.items;
  }

  return recordsStore.items.filter((record) =>
    [record.record_name, record.record_department, record.record_place, record.tags.join(" ")]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(keyword)),
  );
});

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

async function loadRecords() {
  await recordsStore.load(projectId.value);
  if (recordsStore.items[0]) {
    await openRecord(recordsStore.items[0].id);
  }
}

function openCreateModal() {
  if (!canEditContent.value) {
    return;
  }
  isCreateOpen.value = true;
}

async function openRecord(recordId: number) {
  await recordsStore.open(projectId.value, recordId);
}

function insertMention(memberName: string) {
  if (!canEditContent.value) {
    return;
  }

  const textarea = composerTextarea.value;
  const mention = `@${memberName} `;

  if (!textarea) {
    newTextBox.value = `${newTextBox.value}${newTextBox.value ? " " : ""}${mention}`;
    return;
  }

  const start = textarea.selectionStart ?? newTextBox.value.length;
  const end = textarea.selectionEnd ?? start;
  const before = newTextBox.value.slice(0, start);
  const after = newTextBox.value.slice(end);
  const prefix = before && !/\s$/.test(before) ? " " : "";
  const nextValue = `${before}${prefix}${mention}${after}`;
  const cursorPosition = before.length + prefix.length + mention.length;

  newTextBox.value = nextValue;
  void nextTick(() => {
    textarea.focus();
    textarea.setSelectionRange(cursorPosition, cursorPosition);
  });
}

async function submitSearch() {
  const value = searchQuery.value.trim();
  if (!value) {
    clearSearch();
    return;
  }

  saveHistory(value);
  showSearchHistory.value = false;

  const firstMatch = filteredRecords.value[0];
  if (firstMatch) {
    await openRecord(firstMatch.id);
  }
}

function clearSearch() {
  searchQuery.value = "";
  showSearchHistory.value = false;
}

function selectHistory(value: string) {
  window.clearTimeout(hideHistoryTimer.value);
  searchQuery.value = value;
  void submitSearch();
}

async function createRecord(payload: {
  record_name: string;
  record_department?: string;
  record_place?: string;
  record_host_name?: string;
  record_attendances?: number;
}) {
  if (!payload.record_name.trim() || !canEditContent.value) {
    return;
  }

  await recordsStore.create(projectId.value, payload);
  isCreateOpen.value = false;
}

async function createTextBox() {
  const content = newTextBox.value.trim();
  if (!content || !recordsStore.selectedRecord || !canEditContent.value) {
    return;
  }

  await recordsStore.addTextBox(recordsStore.selectedRecord.id, content);
  newTextBox.value = "";
}

watch(
  projectId,
  () => {
    void loadRecords();
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  window.clearTimeout(hideHistoryTimer.value);
});
</script>

<style scoped>
.records-page {
  position: relative;
  min-height: 100%;
  display: grid;
  gap: 1.5rem;
}

.records-page__overlay {
  position: fixed;
  inset: 0;
  background: rgba(59, 56, 56, 0.55);
  z-index: 15;
}

.records-page__modal {
  position: fixed;
  inset: 50% auto auto 50%;
  z-index: 16;
  transform: translate(-50%, -50%);
}

.records-page__hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border: 1px solid #e1dcdc;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.84);
  padding: 1.5rem 1.75rem;
}

.records-page__eyebrow {
  margin: 0 0 0.35rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #b6aeae;
}

.records-page__hero h1 {
  margin: 0;
  font-size: clamp(2rem, 3.2vw, 3rem);
}

.records-page__copy {
  margin: 0.5rem 0 0;
  color: #5c5454;
}

.records-page__cta {
  border: 0;
  border-radius: 999px;
  padding: 0.95rem 1.5rem;
  background: #b82c30;
  color: #fff;
  cursor: pointer;
}

.records-page__cta:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.records-page__layout {
  display: grid;
  grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.2fr);
  gap: 1.5rem;
}

.records-page__summary,
.records-page__content {
  border: 1px solid #e1dcdc;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.88);
  padding: 1.5rem;
}

.records-page__summary table {
  width: 100%;
  border-collapse: collapse;
}

.records-page__summary th,
.records-page__summary td {
  border: 1px solid #ccc;
  padding: 0.95rem 1rem;
  text-align: left;
}

.records-page__summary th {
  width: 7rem;
  background: #ebeef5;
}

.records-page__composer {
  display: grid;
  gap: 0.85rem;
}

.records-page__composer textarea {
  min-height: 10rem;
  border: 1px solid #ccc;
  border-radius: 14px;
  padding: 1rem;
  resize: vertical;
}

.records-page__mentions {
  display: grid;
  gap: 0.65rem;
  border-radius: 14px;
  background: #faf3f3;
  padding: 0.9rem 1rem;
}

.records-page__mention-copy {
  margin: 0;
  color: #7a4d4f;
  line-height: 1.6;
}

.records-page__mention-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.records-page__mention-chip {
  border: 1px solid #f4cbcf;
  border-radius: 999px;
  background: #fff;
  color: #b82c30;
  padding: 0.45rem 0.8rem;
  cursor: pointer;
}

.records-page__composer button {
  justify-self: end;
  border: 0;
  border-radius: 14px;
  padding: 0.85rem 1.2rem;
  background: #b82c30;
  color: #fff;
  cursor: pointer;
}

.records-page__composer button:disabled,
.records-page__composer textarea:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.records-page__hint {
  margin: 1rem 0 0;
  color: #a15b61;
}

.records-page__blocks {
  margin-top: 1rem;
  display: grid;
  gap: 1rem;
}

.records-page__empty {
  border: 1px dashed #c7c2c2;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.55);
  padding: 1.25rem;
  text-align: center;
  color: #7a7474;
}

@media (max-width: 960px) {
  .records-page__hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .records-page__layout {
    grid-template-columns: 1fr;
  }

  .records-page__cta {
    width: 100%;
  }
}
</style>
