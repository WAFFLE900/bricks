<template>
  <article class="text-block">
    <header class="text-block__status">
      <span class="text-block__dot" :class="`text-block__dot--${status}`"></span>
      <span class="text-block__status-label">{{ statusLabel }}</span>
      <div v-if="members.length" class="text-block__presence">
        <span v-for="member in members" :key="member.userId" class="text-block__avatar" :title="presenceTitle(member)">
          {{ initials(member.userName) }}
        </span>
      </div>
    </header>

    <div class="text-block__body">
      <textarea
        v-if="canEdit"
        ref="editorRef"
        class="text-block__editor"
        placeholder="開始輸入，編輯會即時同步給其他協作成員。"
        @input="onInput"
      ></textarea>
      <p v-else>{{ content || "這個文字區塊目前沒有內容。" }}</p>
    </div>

    <div class="text-block__footer">
      <div class="text-block__tags">
        <span v-for="tag in textBox.tags" :key="tag" class="text-block__tag">
          {{ tag }}
        </span>
        <span v-if="!textBox.tags.length" class="text-block__tag text-block__tag--empty">尚未加入標籤</span>
      </div>
      <span class="text-block__date">{{ formatDate(textBox.updated_at) }}</span>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { TextBox } from "@/shared/types/domain";
import { formatDate } from "@/shared/utils/formatDate";
import type { CollabMember } from "../api/collab.client";
import { useTextBoxCollaboration } from "../composables/useTextBoxCollaboration";
import { computed, onMounted, ref, watch } from "vue";

const props = withDefaults(
  defineProps<{
    textBox: TextBox;
    canEdit?: boolean;
  }>(),
  { canEdit: false },
);

const { status, members, content, pushLocalEdit } = useTextBoxCollaboration({
  textBoxId: props.textBox.id,
  initialContent: props.textBox.textBox_content ?? "",
  canEdit: props.canEdit,
});

const editorRef = ref<HTMLTextAreaElement | null>(null);

/**
 * Maps a caret offset from the old value to the new one so a remote merge that lands
 * before the caret shifts it instead of resetting it to the end while typing.
 */
function mapCaret(oldValue: string, newValue: string, caret: number): number {
  const maxPrefix = Math.min(oldValue.length, newValue.length);
  let prefix = 0;
  while (prefix < maxPrefix && oldValue[prefix] === newValue[prefix]) {
    prefix += 1;
  }
  if (caret <= prefix) {
    return caret;
  }
  let suffix = 0;
  while (
    suffix < maxPrefix - prefix &&
    oldValue[oldValue.length - 1 - suffix] === newValue[newValue.length - 1 - suffix]
  ) {
    suffix += 1;
  }
  if (caret >= oldValue.length - suffix) {
    return caret + (newValue.length - oldValue.length);
  }
  return Math.min(caret, newValue.length - suffix);
}

// The textarea is uncontrolled (no :value binding) so Vue never resets the caret on
// re-render. Remote merges are reconciled here, preserving the local selection.
watch(content, (next) => {
  const el = editorRef.value;
  if (!el || el.value === next) {
    return;
  }
  const { selectionStart, selectionEnd } = el;
  const previous = el.value;
  el.value = next;
  el.selectionStart = mapCaret(previous, next, selectionStart ?? next.length);
  el.selectionEnd = mapCaret(previous, next, selectionEnd ?? next.length);
});

onMounted(() => {
  if (editorRef.value) {
    editorRef.value.value = content.value;
  }
});

const statusLabel = computed(() => {
  switch (status.value) {
    case "open":
      return "即時協作中";
    case "connecting":
      return "連線中…";
    case "closed":
      return "已離線";
    default:
      return "尚未連線";
  }
});

function onInput(event: Event): void {
  pushLocalEdit((event.target as HTMLTextAreaElement).value);
}

function initials(name: string): string {
  return name.trim().slice(0, 1).toUpperCase() || "?";
}

function presenceTitle(member: CollabMember): string {
  return member.canEdit ? `${member.userName}（可編輯）` : `${member.userName}（觀看）`;
}
</script>

<style scoped>
.text-block {
  border: 1px solid #ddd;
  border-radius: 14px;
  background: #fff;
  padding: 1rem;
  display: grid;
  gap: 1rem;
}

.text-block__status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #7a7474;
  font-size: 0.8rem;
}

.text-block__dot {
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 50%;
  background: #c7c2c2;
}

.text-block__dot--open {
  background: #2fa36b;
}

.text-block__dot--connecting {
  background: #e0a92e;
}

.text-block__dot--closed {
  background: #b82c30;
}

.text-block__presence {
  display: flex;
  gap: 0.3rem;
  margin-left: auto;
}

.text-block__avatar {
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 50%;
  background: #ebeef5;
  color: #5c5454;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}

.text-block__body p {
  margin: 0;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

.text-block__editor {
  width: 100%;
  min-height: 6rem;
  border: 1px solid #e1dcdc;
  border-radius: 10px;
  padding: 0.75rem;
  line-height: 1.8;
  resize: vertical;
  font: inherit;
}

.text-block__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.text-block__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.text-block__tag {
  border: 1px solid #f4cbcf;
  border-radius: 999px;
  padding: 0.25rem 0.75rem;
  color: #c91f2f;
  font-size: 0.85rem;
}

.text-block__tag--empty {
  border-color: #e1dcdc;
  color: #7a7474;
}

.text-block__date {
  color: #7a7474;
  font-size: 0.85rem;
}
</style>
