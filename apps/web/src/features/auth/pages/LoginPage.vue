<template>
  <div class="auth-page">
    <LegacyPublicHeader />

    <main class="auth-page__body">
      <section class="auth-card">
        <h1>登入</h1>

        <div :class="['auth-card__alert', { 'auth-card__alert--hidden': !errorMessage }]" role="alert">
          <img :src="warningIconUrl" alt="" />
          <p>{{ errorMessage || " " }}</p>
        </div>

        <form class="auth-form" @submit.prevent="handleSubmit">
          <input
            v-model="form.user_email"
            aria-label="Email"
            autocomplete="email"
            class="auth-form__input"
            placeholder="電子信箱"
            required
            type="email"
          />

          <div class="auth-form__password">
            <input
              v-model="form.user_password"
              aria-label="Password"
              autocomplete="current-password"
              class="auth-form__input"
              placeholder="密碼"
              required
              :type="showPassword ? 'text' : 'password'"
            />
            <button class="auth-form__eye" type="button" @click="showPassword = !showPassword">
              <img :src="showPassword ? eyeOnIconUrl : eyeOffIconUrl" alt="Toggle password visibility" />
            </button>
          </div>

          <div class="auth-form__meta">
            <button class="auth-form__remember" type="button" @click="rememberMe = !rememberMe">
              <img :src="rememberMe ? checkboxOnIconUrl : checkboxOffIconUrl" alt="" />
              <span>保持登入</span>
            </button>
            <span class="auth-form__link">登入後可於個人頁面修改密碼</span>
          </div>

          <button aria-label="Login" class="auth-form__submit" :disabled="authStore.loading" type="submit">
            登入
          </button>
        </form>

        <div class="auth-card__divider">
          <span>其他方式</span>
        </div>

        <div class="auth-card__socials">
          <button class="auth-card__social auth-card__social--wide" type="button" @click="startOAuthLogin('google')">
            <img :src="googleIconUrl" alt="" />
            <span>Google 登入</span>
          </button>
          <button class="auth-card__social auth-card__social--wide" type="button" @click="startOAuthLogin('facebook')">
            <img :src="facebookIconUrl" alt="" />
            <span>Facebook 登入</span>
          </button>
        </div>

        <p class="auth-card__switch">
          還沒有帳號？
          <RouterLink to="/register">立即註冊</RouterLink>
        </p>
      </section>
    </main>

    <LegacyPublicFooter />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import checkboxOffIconUrl from "@/assets/legacy/checkbox/CheckBox_off.svg";
import checkboxOnIconUrl from "@/assets/legacy/checkbox/CheckBox_on.svg";
import eyeOffIconUrl from "@/assets/legacy/eye/eye_origin.svg";
import eyeOnIconUrl from "@/assets/legacy/eye/eye_on.svg";
import facebookIconUrl from "@/assets/legacy/FB_login.svg";
import googleIconUrl from "@/assets/legacy/Google_login.svg";
import warningIconUrl from "@/assets/legacy/exclamation.svg";
import LegacyPublicFooter from "@/shared/ui/legacy/LegacyPublicFooter.vue";
import LegacyPublicHeader from "@/shared/ui/legacy/LegacyPublicHeader.vue";
import type { OAuthProvider } from "@/shared/types/domain";
import { getApiErrorMessage } from "@/shared/utils/getApiErrorMessage";
import { fetchOAuthUrl } from "../api/auth.api";
import { useAuthStore } from "../stores/auth.store";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const errorMessage = ref("");
const rememberMe = ref(false);
const showPassword = ref(false);

const form = reactive({
  user_email: "",
  user_password: "",
});

const providerLabels: Record<OAuthProvider, string> = {
  google: "Google",
  facebook: "Facebook",
};

watch(
  () => route.query.oauth_error,
  (value) => {
    errorMessage.value = typeof value === "string" ? value : "";
  },
  { immediate: true },
);

async function handleSubmit() {
  errorMessage.value = "";

  try {
    const user = await authStore.login(form);
    if (!user.user_identity && !user.user_purpose) {
      await router.push({ name: "survey" });
      return;
    }

    await router.push(String(route.query.redirect || "/projects"));
  } catch {
    errorMessage.value = "帳號或密碼有誤，請重新確認後再試一次。";
  }
}

async function startOAuthLogin(provider: OAuthProvider) {
  const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/projects";

  try {
    const { auth_url } = await fetchOAuthUrl(provider, redirect);
    window.location.href = auth_url;
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, `這個環境目前沒有啟用 ${providerLabels[provider]} 登入。`);
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: url("@/assets/legacy/bricks_bg.svg") center top / cover no-repeat;
}

.auth-page__body {
  flex: 1;
  display: grid;
  place-items: center;
  padding: 8.5rem 1.5rem 2rem;
}

.auth-card {
  width: min(22rem, 100%);
}

.auth-card h1 {
  margin: 0 0 1rem;
  text-align: center;
  font-size: 1.8rem;
}

.auth-card__alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 3rem;
  border: 1px solid #c65659;
  border-radius: 14px;
  background: #f1d5d6;
  padding: 0.5rem 0.9rem;
  color: #c65659;
  font-size: 0.9rem;
}

.auth-card__alert img {
  width: 1.05rem;
  height: 1.05rem;
}

.auth-card__alert p {
  margin: 0;
}

.auth-card__alert--hidden {
  opacity: 0;
}

.auth-form {
  margin-top: 1rem;
}

.auth-form__input {
  width: 100%;
  border: 1.5px solid #c7c2c2;
  border-radius: 12px;
  padding: 0.95rem 1rem 0.95rem 1.15rem;
  background: #fff;
  font-size: 0.95rem;
}

.auth-form__input + .auth-form__input,
.auth-form__password {
  margin-top: 1rem;
}

.auth-form__password {
  position: relative;
}

.auth-form__eye {
  position: absolute;
  top: 50%;
  right: 0.9rem;
  transform: translateY(-50%);
  border: 0;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.auth-form__eye img {
  width: 1.15rem;
  height: 1.15rem;
}

.auth-form__meta {
  margin-top: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.9rem;
}

.auth-form__remember {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border: 0;
  background: transparent;
  padding: 0;
  cursor: pointer;
  color: #3b3838;
}

.auth-form__remember img {
  width: 1rem;
  height: 1rem;
}

.auth-form__link {
  color: #c65659;
}

.auth-form__submit {
  width: 100%;
  margin-top: 1rem;
  border: 0;
  border-radius: 14px;
  padding: 0.95rem 1rem;
  background: #b82c30;
  color: #fff;
  cursor: pointer;
}

.auth-form__submit:hover {
  background: #d48083;
}

.auth-form__submit:disabled {
  cursor: wait;
  opacity: 0.7;
}

.auth-card__divider {
  margin: 1.5rem 0 1rem;
  position: relative;
  text-align: center;
  color: #b6aeae;
}

.auth-card__divider::before,
.auth-card__divider::after {
  content: "";
  position: absolute;
  top: 50%;
  width: calc(50% - 2.5rem);
  border-bottom: 1px solid #b6aeae;
}

.auth-card__divider::before {
  left: 0;
}

.auth-card__divider::after {
  right: 0;
}

.auth-card__socials {
  display: grid;
  gap: 0.75rem;
}

.auth-card__social {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  width: 100%;
  border: 1px solid #b6aeae;
  border-radius: 14px;
  padding: 0.85rem 1rem;
  background: #fff;
  color: #7a7474;
  cursor: pointer;
}

.auth-card__social img {
  width: 1rem;
  height: 1rem;
}

.auth-card__switch {
  margin: 1rem 0 0;
  text-align: center;
  color: #b6aeae;
}

.auth-card__switch a {
  color: #c65659;
  text-decoration: none;
}

@media (max-width: 720px) {
  .auth-page__body {
    padding-top: 10rem;
  }
}
</style>
