<template>
  <section class="modal" role="dialog" aria-modal="true" aria-labelledby="create-record-title">
    <button class="modal__close" type="button" @click="$emit('close')"></button>
    <h2 id="create-record-title">新增會議記錄</h2>

    <form class="modal__form" @submit.prevent="submit">
      <input v-model="record.record_name" placeholder="請輸入會議名稱" required type="text" />
      <input v-model="record.record_department" placeholder="部門" type="text" />
      <input v-model="record.record_place" placeholder="地點" type="text" />
      <input v-model="record.record_host_name" placeholder="主持人" type="text" />
      <input v-model.number="record.record_attendances" min="0" placeholder="出席人數" type="number" />

      <button class="modal__submit" :disabled="loading" type="submit">建立會議記錄</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { reactive } from "vue";

withDefaults(
  defineProps<{
    loading?: boolean;
  }>(),
  {
    loading: false,
  },
);

const emit = defineEmits<{
  close: [];
  submit: [
    payload: {
      record_name: string;
      record_department?: string;
      record_place?: string;
      record_host_name?: string;
      record_attendances?: number;
    },
  ];
}>();

const record = reactive({
  record_attendances: 0,
  record_department: "",
  record_host_name: "",
  record_name: "",
  record_place: "",
});

function submit() {
  emit("submit", {
    record_name: record.record_name.trim(),
    record_department: record.record_department.trim() || undefined,
    record_place: record.record_place.trim() || undefined,
    record_host_name: record.record_host_name.trim() || undefined,
    record_attendances: record.record_attendances || undefined,
  });
}
</script>

<style scoped>
.modal {
  position: relative;
  width: min(22rem, calc(100vw - 2rem));
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

.modal__form {
  margin-top: 1.5rem;
  display: grid;
  gap: 0.85rem;
}

.modal__form input {
  width: 100%;
  border: 1px solid #c7c2c2;
  border-radius: 12px;
  padding: 0.8rem 1rem;
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
