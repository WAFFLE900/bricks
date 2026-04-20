<template>
  <article class="text-block">
    <div class="text-block__body">
      <p>{{ textBox.textBox_content || "這個文字區塊目前沒有內容。" }}</p>
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

defineProps<{
  textBox: TextBox;
}>();
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

.text-block__body p {
  margin: 0;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
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
