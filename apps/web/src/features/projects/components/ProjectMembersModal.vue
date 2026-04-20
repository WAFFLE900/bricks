<template>
  <section class="modal" role="dialog" aria-modal="true" aria-labelledby="project-members-title">
    <button class="modal__close" type="button" @click="$emit('close')"></button>

    <div class="modal__header">
      <div>
        <p class="modal__eyebrow">專案權限</p>
        <h2 id="project-members-title">{{ project.project_name }}</h2>
      </div>
      <span class="modal__badge">{{ project.member_count }} 位成員</span>
    </div>

    <form class="modal__invite" @submit.prevent="submitInvite">
      <label class="modal__field">
        <span>成員 Email</span>
        <input v-model="inviteEmail" placeholder="teammate@example.com" type="email" />
      </label>

      <label class="modal__field">
        <span>權限</span>
        <select v-model="invitePermission">
          <option value="view">可觀看</option>
          <option value="edit">可編輯</option>
        </select>
      </label>

      <button class="modal__submit" :disabled="loading || !inviteEmail.trim()" type="submit">邀請成員</button>
    </form>

    <p v-if="activeErrorMessage" class="modal__error">{{ activeErrorMessage }}</p>

    <div class="modal__members">
      <article v-for="member in project.members" :key="member.user_id" class="modal__member">
        <div class="modal__member-copy">
          <strong>{{ member.user_name }}</strong>
          <span>{{ member.user_email }}</span>
        </div>

        <div class="modal__member-actions">
          <span v-if="member.role === 'owner'" class="modal__owner-tag">建立者</span>
          <label v-else class="modal__permission">
            <span class="sr-only">權限</span>
            <select
              :value="member.permission"
              :disabled="loading"
              @change="updatePermission(member.user_id, $event)"
            >
              <option value="view">可觀看</option>
              <option value="edit">可編輯</option>
            </select>
          </label>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

import type { Project, ProjectMemberPermission } from "@/shared/types/domain";

const props = defineProps<{
  errorMessage?: string;
  project: Project;
  loading?: boolean;
}>();

const emit = defineEmits<{
  close: [];
  invite: [payload: { user_email: string; permission: ProjectMemberPermission }];
  updatePermission: [payload: { memberUserId: number; permission: ProjectMemberPermission }];
}>();

const localErrorMessage = ref("");
const inviteEmail = ref("");
const invitePermission = ref<ProjectMemberPermission>("view");
const activeErrorMessage = computed(() => localErrorMessage.value || props.errorMessage || "");

function submitInvite() {
  const user_email = inviteEmail.value.trim();
  if (!user_email) {
    localErrorMessage.value = "請輸入成員 Email。";
    return;
  }

  localErrorMessage.value = "";
  emit("invite", {
    user_email,
    permission: invitePermission.value,
  });
  inviteEmail.value = "";
  invitePermission.value = "view";
}

function updatePermission(memberUserId: number, event: Event) {
  const permission = (event.target as HTMLSelectElement).value as ProjectMemberPermission;
  emit("updatePermission", { memberUserId, permission });
}
</script>

<style scoped>
.modal {
  position: relative;
  width: min(40rem, calc(100vw - 2rem));
  max-height: min(88vh, 52rem);
  overflow: auto;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.28);
  padding: 1.75rem;
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

.modal__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.modal__eyebrow {
  margin: 0 0 0.35rem;
  color: #9f9292;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.modal__header h2 {
  margin: 0;
}

.modal__badge {
  border-radius: 999px;
  background: #f8e7e8;
  color: #9f2931;
  padding: 0.45rem 0.85rem;
  font-size: 0.9rem;
}

.modal__invite {
  margin-top: 1.5rem;
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 0.9fr) auto;
  gap: 0.85rem;
  align-items: end;
}

.modal__field {
  display: grid;
  gap: 0.45rem;
}

.modal__field span {
  color: #6d6666;
  font-size: 0.9rem;
}

.modal__field input,
.modal__field select,
.modal__permission select {
  width: 100%;
  border: 1px solid #d9cfcf;
  border-radius: 12px;
  padding: 0.8rem 1rem;
  background: #fff;
}

.modal__submit {
  border: 0;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  background: #b82c30;
  color: #fff;
  cursor: pointer;
}

.modal__submit:disabled {
  cursor: wait;
  opacity: 0.75;
}

.modal__error {
  margin: 0.85rem 0 0;
  color: #b42318;
}

.modal__members {
  margin-top: 1.4rem;
  display: grid;
  gap: 0.75rem;
}

.modal__member {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border: 1px solid #ebe4e4;
  border-radius: 14px;
  background: #fbf9f9;
  padding: 1rem;
}

.modal__member-copy {
  display: grid;
  gap: 0.15rem;
}

.modal__member-copy span {
  color: #7a7474;
}

.modal__member-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.modal__owner-tag {
  border-radius: 999px;
  background: #1f6feb14;
  color: #1f4f99;
  padding: 0.4rem 0.85rem;
  font-size: 0.9rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 720px) {
  .modal__invite {
    grid-template-columns: 1fr;
  }

  .modal__member {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
