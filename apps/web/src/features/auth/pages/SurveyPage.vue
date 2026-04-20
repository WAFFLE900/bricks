<template>
  <div class="survey-page">
    <LegacyPublicHeader />

    <main class="survey-page__body">
      <section class="survey-card">
        <h1>註冊問卷</h1>

        <article class="survey-question">
          <h2>你最希望 BRICKS 幫你完成什麼？</h2>
          <div class="survey-grid">
            <button
              v-for="option in purposeOptions"
              :key="option"
              :class="['survey-chip', { 'survey-chip--active': purposeSelections.includes(option) }]"
              type="button"
              @click="togglePurpose(option)"
            >
              {{ option }}
            </button>
          </div>
        </article>

        <article class="survey-question">
          <h2>你目前主要的角色是？</h2>
          <div class="survey-grid">
            <button
              v-for="option in identityOptions"
              :key="option"
              :class="['survey-chip', { 'survey-chip--active': identitySelection === option }]"
              type="button"
              @click="identitySelection = option"
            >
              {{ option }}
            </button>
          </div>
        </article>

        <article class="survey-question">
          <h2>你現在也會搭配哪些工具？</h2>
          <div class="survey-grid">
            <button
              v-for="option in toolOptions"
              :key="option"
              :class="['survey-chip', { 'survey-chip--active': toolSelections.includes(option) }]"
              type="button"
              @click="toggleTool(option)"
            >
              {{ option }}
            </button>
          </div>
        </article>

        <div class="survey-actions">
          <button class="survey-actions__ghost" :disabled="authStore.loading" type="button" @click="skip">
            稍後再填
          </button>
          <button class="survey-actions__primary" :disabled="authStore.loading" type="button" @click="complete">
            完成
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import LegacyPublicHeader from "@/shared/ui/legacy/LegacyPublicHeader.vue";
import { identityOptions, purposeOptions, toolOptions } from "../constants/survey-options";
import { useAuthStore } from "../stores/auth.store";

const authStore = useAuthStore();
const router = useRouter();

const purposeSelections = ref<string[]>([]);
const identitySelection = ref("");
const toolSelections = ref<string[]>([]);

function toggleItem(target: "purpose" | "tool", option: string) {
  const source = target === "purpose" ? purposeSelections : toolSelections;

  if (source.value.includes(option)) {
    source.value = source.value.filter((item) => item !== option);
    return;
  }

  source.value = [...source.value, option];
}

function togglePurpose(option: string) {
  toggleItem("purpose", option);
}

function toggleTool(option: string) {
  toggleItem("tool", option);
}

async function submit(payload: { user_purpose: string[]; user_identity?: string | null; user_otherTool: string[] }) {
  await authStore.completeSurvey(payload);
  await router.push({ name: "projects" });
}

async function complete() {
  await submit({
    user_purpose: purposeSelections.value,
    user_identity: identitySelection.value || null,
    user_otherTool: toolSelections.value,
  });
}

async function skip() {
  await submit({
    user_purpose: [],
    user_identity: null,
    user_otherTool: [],
  });
}
</script>

<style scoped>
.survey-page {
  min-height: 100vh;
  background: url("@/assets/legacy/bricks_bg.svg") center top / cover no-repeat;
}

.survey-page__body {
  padding: 8rem 5.21% 3rem;
}

.survey-card {
  width: min(64rem, 100%);
  margin: 0 auto;
}

.survey-card h1 {
  margin: 0;
  text-align: center;
  font-size: clamp(2rem, 4vw, 3.4rem);
}

.survey-question {
  margin-top: 2.2rem;
}

.survey-question h2 {
  margin: 0 0 1rem;
  font-size: 1.2rem;
}

.survey-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
}

.survey-chip {
  min-width: 9rem;
  border: 1px solid #b6aeae;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  background: #fff;
  color: #3b3838;
  cursor: pointer;
}

.survey-chip:hover {
  background: #f2eeee;
}

.survey-chip--active {
  background: #f1d5d6;
}

.survey-actions {
  margin-top: 2.5rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.survey-actions button {
  flex: 1;
  border-radius: 14px;
  padding: 0.95rem 1rem;
  font-size: 1rem;
  cursor: pointer;
}

.survey-actions button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.survey-actions__ghost {
  border: 1px solid #b6aeae;
  background: #fff;
  color: #b6aeae;
}

.survey-actions__ghost:hover {
  background: #f2eeee;
}

.survey-actions__primary {
  border: 1px solid #b82c30;
  background: #b82c30;
  color: #fff;
}

.survey-actions__primary:hover {
  background: #d48083;
}

@media (max-width: 720px) {
  .survey-page__body {
    padding-top: 10rem;
  }

  .survey-actions {
    flex-direction: column;
  }

  .survey-chip {
    width: 100%;
  }
}
</style>
