<template>
  <LegacyWorkspaceShell>
    <template #sidebar>
      <aside class="profile-sidebar">
        <div class="profile-sidebar__card">
          <div class="profile-sidebar__avatar">{{ initials }}</div>
          <strong>{{ authStore.user?.user_name || "未命名使用者" }}</strong>
          <p>{{ authStore.user?.user_email }}</p>
        </div>

        <button class="profile-sidebar__back" type="button" @click="router.push({ name: 'projects' })">
          返回專案總覽
        </button>

        <div class="profile-sidebar__meta">
          <span>帳戶管理</span>
          <small>管理姓名、偏好設定、社群綁定與登入密碼。</small>
        </div>
      </aside>
    </template>

    <template #header>
      <LegacyWorkspaceToolbar :breadcrumbs="['BRICKS', '個人頁面']" :model-value="''" :show-search="false" />
    </template>

    <section class="profile-page">
      <div v-if="oauthSuccessMessage" class="profile-page__banner profile-page__banner--success">
        {{ oauthSuccessMessage }}
      </div>
      <div v-if="oauthErrorMessage" class="profile-page__banner profile-page__banner--error">
        {{ oauthErrorMessage }}
      </div>

      <section class="profile-hero">
        <div>
          <p class="profile-hero__eyebrow">Account Center</p>
          <h1>{{ authStore.user?.user_name || "我的帳戶" }}</h1>
          <p class="profile-hero__copy">管理顯示姓名、社群登入綁定、使用偏好與密碼安全設定。</p>
        </div>

        <button class="profile-hero__logout" type="button" @click="handleLogout">登出</button>
      </section>

      <div class="profile-grid">
        <article class="profile-card">
          <div class="profile-card__header">
            <div>
              <p class="profile-card__eyebrow">Profile</p>
              <h2>基本資料</h2>
            </div>
            <span class="profile-card__stamp">建立於 {{ createdAtLabel }}</span>
          </div>

          <form class="profile-form" @submit.prevent="saveProfile">
            <label class="profile-form__field">
              <span>姓名</span>
              <input v-model="profileForm.user_name" maxlength="100" placeholder="請輸入顯示名稱" type="text" />
            </label>

            <label class="profile-form__field">
              <span>電子信箱</span>
              <input :value="authStore.user?.user_email || ''" disabled type="email" />
            </label>

            <section class="profile-form__group">
              <h3>你的角色</h3>
              <div class="profile-chips">
                <button
                  v-for="option in identityOptions"
                  :key="option"
                  :class="['profile-chip', { 'profile-chip--active': profileForm.user_identity === option }]"
                  type="button"
                  @click="profileForm.user_identity = profileForm.user_identity === option ? '' : option"
                >
                  {{ option }}
                </button>
              </div>
            </section>

            <section class="profile-form__group">
              <h3>你最常用 BRICKS 做什麼</h3>
              <div class="profile-chips">
                <button
                  v-for="option in purposeOptions"
                  :key="option"
                  :class="['profile-chip', { 'profile-chip--active': profileForm.user_purpose.includes(option) }]"
                  type="button"
                  @click="toggleSelection(profileForm.user_purpose, option)"
                >
                  {{ option }}
                </button>
              </div>
            </section>

            <section class="profile-form__group">
              <h3>常搭配的工具</h3>
              <div class="profile-chips">
                <button
                  v-for="option in toolOptions"
                  :key="option"
                  :class="['profile-chip', { 'profile-chip--active': profileForm.user_otherTool.includes(option) }]"
                  type="button"
                  @click="toggleSelection(profileForm.user_otherTool, option)"
                >
                  {{ option }}
                </button>
              </div>
            </section>

            <p v-if="profileError" class="profile-form__message profile-form__message--error">
              {{ profileError }}
            </p>
            <p v-if="profileSuccess" class="profile-form__message profile-form__message--success">
              {{ profileSuccess }}
            </p>

            <button class="profile-form__submit" :disabled="isSavingProfile" type="submit">
              {{ isSavingProfile ? "儲存中..." : "儲存個人資料" }}
            </button>
          </form>
        </article>

        <article class="profile-card">
          <div class="profile-card__header">
            <div>
              <p class="profile-card__eyebrow">Security</p>
              <h2>登入與安全</h2>
            </div>
            <span class="profile-card__stamp">更新於 {{ updatedAtLabel }}</span>
          </div>

          <div class="security-list">
            <article class="security-item">
              <div>
                <strong>密碼登入</strong>
                <p>{{ authStore.user?.has_password ? "已設定本地密碼" : "尚未設定密碼，可直接在下方建立。" }}</p>
              </div>
              <span :class="['security-item__badge', { 'security-item__badge--active': authStore.user?.has_password }]">
                {{ authStore.user?.has_password ? "已啟用" : "未設定" }}
              </span>
            </article>

            <article class="security-item">
              <div>
                <strong>Google</strong>
                <p>{{ authStore.user?.has_google_account ? socialBoundText : "綁定後可直接用 Google 登入。" }}</p>
              </div>
              <button
                v-if="!authStore.user?.has_google_account"
                class="security-item__action"
                :disabled="linkingProvider === 'google'"
                type="button"
                @click="startSocialLink('google')"
              >
                {{ linkingProvider === "google" ? "前往綁定..." : "綁定 Google" }}
              </button>
              <span v-else class="security-item__badge security-item__badge--active">已綁定</span>
            </article>

            <article class="security-item">
              <div>
                <strong>Facebook</strong>
                <p>{{ authStore.user?.has_facebook_account ? socialBoundText : "綁定後可直接用 Facebook 登入。" }}</p>
              </div>
              <button
                v-if="!authStore.user?.has_facebook_account"
                class="security-item__action"
                :disabled="linkingProvider === 'facebook'"
                type="button"
                @click="startSocialLink('facebook')"
              >
                {{ linkingProvider === "facebook" ? "前往綁定..." : "綁定 Facebook" }}
              </button>
              <span v-else class="security-item__badge security-item__badge--active">已綁定</span>
            </article>
          </div>

          <form class="profile-form profile-form--password" @submit.prevent="savePassword">
            <h3>修改密碼</h3>

            <label v-if="authStore.user?.has_password" class="profile-form__field">
              <span>目前密碼</span>
              <input
                v-model="passwordForm.current_password"
                autocomplete="current-password"
                placeholder="請輸入目前密碼"
                type="password"
              />
            </label>

            <label class="profile-form__field">
              <span>{{ authStore.user?.has_password ? "新密碼" : "設定密碼" }}</span>
              <input
                v-model="passwordForm.new_password"
                autocomplete="new-password"
                placeholder="至少 8 個字元"
                type="password"
              />
            </label>

            <label class="profile-form__field">
              <span>再次輸入新密碼</span>
              <input
                v-model="passwordForm.confirm_password"
                autocomplete="new-password"
                placeholder="再次輸入新密碼"
                type="password"
              />
            </label>

            <p v-if="passwordError" class="profile-form__message profile-form__message--error">
              {{ passwordError }}
            </p>
            <p v-if="passwordSuccess" class="profile-form__message profile-form__message--success">
              {{ passwordSuccess }}
            </p>

            <button class="profile-form__submit" :disabled="isSavingPassword" type="submit">
              {{ isSavingPassword ? "更新中..." : authStore.user?.has_password ? "更新密碼" : "建立密碼" }}
            </button>
          </form>
        </article>
      </div>
    </section>
  </LegacyWorkspaceShell>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { identityOptions, purposeOptions, toolOptions } from "@/features/auth/constants/survey-options";
import { useAuthStore } from "@/features/auth/stores/auth.store";
import LegacyWorkspaceShell from "@/shared/ui/legacy/LegacyWorkspaceShell.vue";
import LegacyWorkspaceToolbar from "@/shared/ui/legacy/LegacyWorkspaceToolbar.vue";
import type { OAuthProvider, User } from "@/shared/types/domain";
import { formatDate } from "@/shared/utils/formatDate";
import { getApiErrorMessage } from "@/shared/utils/getApiErrorMessage";
import { changePassword, fetchSocialLinkUrl, updateProfile } from "../api/profile.api";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const isSavingPassword = ref(false);
const isSavingProfile = ref(false);
const linkingProvider = ref<OAuthProvider | "">("");
const profileError = ref("");
const profileSuccess = ref("");
const passwordError = ref("");
const passwordSuccess = ref("");

const profileForm = reactive({
  user_name: "",
  user_identity: "",
  user_purpose: [] as string[],
  user_otherTool: [] as string[],
});

const passwordForm = reactive({
  current_password: "",
  new_password: "",
  confirm_password: "",
});

const providerLabels: Record<OAuthProvider, string> = {
  google: "Google",
  facebook: "Facebook",
};

const oauthSuccessMessage = computed(() => {
  const linked = route.query.linked;
  if (typeof linked !== "string" || !(linked in providerLabels)) {
    return "";
  }

  return `已成功綁定 ${providerLabels[linked as OAuthProvider]} 帳戶。`;
});

const oauthErrorMessage = computed(() => {
  const value = route.query.oauth_error;
  return typeof value === "string" ? value : "";
});

const initials = computed(() => (authStore.user?.user_name || "U").trim().charAt(0).toUpperCase() || "U");
const createdAtLabel = computed(() => formatDate(authStore.user?.created_at));
const updatedAtLabel = computed(() => formatDate(authStore.user?.updated_at));
const socialBoundText = computed(() => authStore.user?.user_email || "已綁定");

function splitList(value?: string | null) {
  if (!value) {
    return [];
  }

  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function syncForm(user: User | null) {
  profileForm.user_name = user?.user_name || "";
  profileForm.user_identity = user?.user_identity || "";
  profileForm.user_purpose = [...(user?.user_purpose_list?.length ? user.user_purpose_list : splitList(user?.user_purpose))];
  profileForm.user_otherTool = [
    ...(user?.user_other_tool_list?.length ? user.user_other_tool_list : splitList(user?.user_otherTool)),
  ];
}

function toggleSelection(target: string[], option: string) {
  const index = target.indexOf(option);
  if (index >= 0) {
    target.splice(index, 1);
    return;
  }

  target.push(option);
}

async function saveProfile() {
  profileError.value = "";
  profileSuccess.value = "";

  if (!profileForm.user_name.trim()) {
    profileError.value = "姓名不能空白。";
    return;
  }

  isSavingProfile.value = true;
  try {
    const user = await updateProfile({
      user_name: profileForm.user_name.trim(),
      user_identity: profileForm.user_identity || null,
      user_purpose: [...profileForm.user_purpose],
      user_otherTool: [...profileForm.user_otherTool],
    });
    authStore.setUser(user);
    profileSuccess.value = "個人資料已更新。";
  } catch (error) {
    profileError.value = getApiErrorMessage(error, "儲存個人資料失敗，請稍後再試。");
  } finally {
    isSavingProfile.value = false;
  }
}

async function savePassword() {
  passwordError.value = "";
  passwordSuccess.value = "";

  if (passwordForm.new_password.length < 8) {
    passwordError.value = "新密碼至少需要 8 個字元。";
    return;
  }

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = "兩次輸入的新密碼不一致。";
    return;
  }

  isSavingPassword.value = true;
  const hadPassword = Boolean(authStore.user?.has_password);
  try {
    const user = await changePassword({
      current_password: passwordForm.current_password || null,
      new_password: passwordForm.new_password,
    });
    authStore.setUser(user);
    passwordForm.current_password = "";
    passwordForm.new_password = "";
    passwordForm.confirm_password = "";
    passwordSuccess.value = hadPassword ? "密碼已更新。" : "密碼已建立，之後也能用密碼登入。";
  } catch (error) {
    passwordError.value = getApiErrorMessage(error, "修改密碼失敗，請稍後再試。");
  } finally {
    isSavingPassword.value = false;
  }
}

async function startSocialLink(provider: OAuthProvider) {
  passwordError.value = "";
  linkingProvider.value = provider;

  try {
    const { auth_url } = await fetchSocialLinkUrl(provider, "/profile");
    window.location.href = auth_url;
  } catch (error) {
    passwordError.value = getApiErrorMessage(error, `目前無法啟動 ${providerLabels[provider]} 綁定流程。`);
  } finally {
    linkingProvider.value = "";
  }
}

async function handleLogout() {
  authStore.logout();
  await router.push({ name: "login" });
}

watch(
  () => authStore.user,
  (user) => {
    syncForm(user);
  },
  { immediate: true },
);
</script>

<style scoped>
.profile-sidebar {
  min-height: 100%;
  display: grid;
  align-content: start;
  gap: 1rem;
  padding: 1.25rem;
}

.profile-sidebar__card,
.profile-sidebar__meta {
  border: 1px solid #e1dcdc;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.88);
  padding: 1.2rem;
}

.profile-sidebar__avatar {
  width: 3.5rem;
  height: 3.5rem;
  display: grid;
  place-items: center;
  border-radius: 18px;
  background: #b82c30;
  color: #fff;
  font-size: 1.3rem;
  font-weight: 700;
}

.profile-sidebar__card strong,
.profile-sidebar__card p {
  display: block;
}

.profile-sidebar__card strong {
  margin-top: 0.85rem;
  font-size: 1.05rem;
}

.profile-sidebar__card p,
.profile-sidebar__meta small {
  margin: 0.35rem 0 0;
  color: #7a7474;
  line-height: 1.7;
}

.profile-sidebar__back {
  border: 0;
  border-radius: 14px;
  background: #fff;
  padding: 0.95rem 1rem;
  text-align: left;
  cursor: pointer;
}

.profile-sidebar__back:hover {
  background: #f6f0f0;
}

.profile-sidebar__meta {
  display: grid;
  gap: 0.45rem;
}

.profile-sidebar__meta span {
  font-weight: 700;
}

.profile-page {
  display: grid;
  gap: 1.5rem;
  min-height: 100%;
}

.profile-page__banner {
  border-radius: 16px;
  padding: 0.95rem 1.1rem;
  font-size: 0.95rem;
}

.profile-page__banner--success {
  border: 1px solid #8fbf8e;
  background: #eef8ee;
  color: #356337;
}

.profile-page__banner--error {
  border: 1px solid #c65659;
  background: #f8e4e5;
  color: #b82c30;
}

.profile-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border: 1px solid #e1dcdc;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.88);
  padding: 1.6rem 1.8rem;
}

.profile-hero__eyebrow,
.profile-card__eyebrow {
  margin: 0 0 0.35rem;
  color: #b6aeae;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

.profile-hero h1,
.profile-card h2 {
  margin: 0;
}

.profile-hero__copy {
  margin: 0.65rem 0 0;
  color: #5c5454;
}

.profile-hero__logout,
.profile-form__submit,
.security-item__action {
  border: 0;
  border-radius: 14px;
  background: #b82c30;
  color: #fff;
  cursor: pointer;
}

.profile-hero__logout {
  padding: 0.95rem 1.35rem;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.5rem;
}

.profile-card {
  border: 1px solid #e1dcdc;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 1.5rem;
}

.profile-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.profile-card__stamp {
  color: #7a7474;
  font-size: 0.88rem;
}

.profile-form {
  margin-top: 1.4rem;
  display: grid;
  gap: 1rem;
}

.profile-form--password {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #ebe3e3;
}

.profile-form--password h3,
.profile-form__group h3 {
  margin: 0 0 0.85rem;
  font-size: 1rem;
}

.profile-form__field {
  display: grid;
  gap: 0.45rem;
}

.profile-form__field span {
  font-size: 0.92rem;
  color: #5c5454;
}

.profile-form__field input {
  width: 100%;
  border: 1px solid #d8d0d0;
  border-radius: 14px;
  background: #fff;
  padding: 0.9rem 1rem;
}

.profile-form__field input:disabled {
  background: #f6f0f0;
  color: #7a7474;
}

.profile-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.profile-chip {
  border: 1px solid #d8d0d0;
  border-radius: 999px;
  background: #fff;
  padding: 0.8rem 1rem;
  cursor: pointer;
}

.profile-chip--active {
  border-color: #b82c30;
  background: #f8e4e5;
  color: #b82c30;
}

.profile-form__message {
  margin: 0;
  border-radius: 14px;
  padding: 0.8rem 0.95rem;
  font-size: 0.92rem;
}

.profile-form__message--error {
  background: #f8e4e5;
  color: #b82c30;
}

.profile-form__message--success {
  background: #eef8ee;
  color: #356337;
}

.profile-form__submit,
.security-item__action {
  padding: 0.95rem 1rem;
}

.profile-form__submit:disabled,
.security-item__action:disabled {
  cursor: wait;
  opacity: 0.72;
}

.security-list {
  margin-top: 1.4rem;
  display: grid;
  gap: 0.85rem;
}

.security-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border: 1px solid #ebe3e3;
  border-radius: 16px;
  background: #fff;
  padding: 1rem;
}

.security-item strong,
.security-item p {
  display: block;
}

.security-item p {
  margin: 0.35rem 0 0;
  color: #7a7474;
}

.security-item__badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 4.5rem;
  border-radius: 999px;
  background: #ebe3e3;
  padding: 0.45rem 0.8rem;
  color: #5c5454;
}

.security-item__badge--active {
  background: #eef8ee;
  color: #356337;
}

@media (max-width: 1180px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .profile-hero,
  .profile-card__header,
  .security-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-hero__logout,
  .profile-form__submit,
  .security-item__action {
    width: 100%;
  }

  .profile-chip {
    width: 100%;
    text-align: left;
  }
}
</style>
