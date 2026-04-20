<template>
  <section class="modal" role="dialog" aria-modal="true" aria-labelledby="create-project-title">
    <button class="modal__close" type="button" @click="$emit('close')"></button>
    <h2 id="create-project-title">新增專案</h2>

    <div class="modal__preview">
      <img :src="plusIconUrl" alt="" />
    </div>

    <form class="modal__form" @submit.prevent="submit">
      <input v-model="projectName" placeholder="請輸入專案名稱" required type="text" />

      <div class="modal__select">
        <button class="modal__select-button" type="button" @click="isTypeListOpen = !isTypeListOpen">
          <span>{{ selectedType || "選擇分類" }}</span>
          <span class="modal__arrow">{{ isTypeListOpen ? "▲" : "▼" }}</span>
        </button>

        <div v-if="isTypeListOpen" class="modal__options">
          <button class="modal__option" type="button" @click="chooseType('')">未分類</button>
          <button
            v-for="type in types"
            :key="type"
            class="modal__option"
            type="button"
            @click="chooseType(type)"
          >
            {{ type }}
          </button>

          <div class="modal__divider"></div>
          <input
            v-model="customType"
            class="modal__custom-input"
            placeholder="輸入新分類"
            type="text"
            @focus="selectedType = ''"
          />
        </div>
      </div>

      <button class="modal__submit" :disabled="loading" type="submit">建立專案</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";

import plusIconUrl from "@/assets/legacy/add_proj_pic_plus.svg";

withDefaults(
  defineProps<{
    loading?: boolean;
    types: string[];
  }>(),
  {
    loading: false,
  },
);

const emit = defineEmits<{
  close: [];
  submit: [payload: { project_name: string; project_type?: string }];
}>();

const customType = ref("");
const isTypeListOpen = ref(false);
const projectName = ref("");
const selectedType = ref("");

function chooseType(value: string) {
  selectedType.value = value;
  customType.value = "";
  isTypeListOpen.value = false;
}

function submit() {
  const project_type = customType.value.trim() || selectedType.value || undefined;
  emit("submit", {
    project_name: projectName.value.trim(),
    project_type,
  });
}
</script>

<style scoped>
.modal {
  position: relative;
  width: min(21.5rem, calc(100vw - 2rem));
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.28);
  padding: 1.5rem 2rem 2rem;
}

.modal h2 {
  margin: 0;
  text-align: center;
  font-size: 1.3rem;
}

.modal__close {
  position: absolute;
  top: 1.1rem;
  right: 1.2rem;
  width: 1rem;
  height: 1rem;
  border: 0;
  background: transparent;
  cursor: pointer;
}

.modal__close::before,
.modal__close::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 16px;
  background: #120406;
}

.modal__close::before {
  transform: translate(-50%, -50%) rotate(45deg);
}

.modal__close::after {
  transform: translate(-50%, -50%) rotate(-45deg);
}

.modal__preview {
  margin-top: 1.8rem;
  border-radius: 14px;
  background: #f2eeee;
  min-height: 8.75rem;
  display: grid;
  place-items: center;
}

.modal__preview img {
  width: 3.2rem;
  height: 3.2rem;
}

.modal__form {
  margin-top: 1.4rem;
  display: grid;
  gap: 0.85rem;
}

.modal__form input,
.modal__select-button {
  width: 100%;
  border: 1px solid #c7c2c2;
  border-radius: 12px;
  padding: 0.8rem 1rem;
  background: #fff;
}

.modal__select {
  position: relative;
}

.modal__select-button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-align: left;
  cursor: pointer;
}

.modal__options {
  position: absolute;
  top: calc(100% + 0.35rem);
  left: 0;
  width: 100%;
  border-radius: 14px;
  background: #fff;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.3),
    0 2px 15px rgba(0, 0, 0, 0.15);
  padding: 0.5rem 0;
  z-index: 4;
}

.modal__option {
  width: 100%;
  border: 0;
  background: transparent;
  padding: 0.75rem 1rem;
  text-align: left;
  cursor: pointer;
}

.modal__option:hover,
.modal__custom-input:hover {
  background: #f2eeee;
}

.modal__divider {
  height: 1px;
  margin: 0.25rem 0;
  background: #e1dcdc;
}

.modal__custom-input {
  border: 0;
  border-radius: 0;
  padding: 0.75rem 1rem;
}

.modal__submit {
  border: 0;
  border-radius: 14px;
  padding: 0.9rem 1rem;
  background: #b82c30;
  color: #fff;
  cursor: pointer;
}

.modal__submit:hover {
  background: #d48083;
}

.modal__submit:disabled {
  cursor: wait;
  opacity: 0.7;
}
</style>
