<template>
  <div class="callback-page">
    <LegacyPublicHeader />

    <main class="callback-page__body">
      <section class="callback-card">
        <h1>{{ errorMessage ? "登入遇到問題" : "正在完成登入" }}</h1>
        <p>{{ errorMessage || statusMessage }}</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import LegacyPublicHeader from "@/shared/ui/legacy/LegacyPublicHeader.vue";
import { getApiErrorMessage } from "@/shared/utils/getApiErrorMessage";
import { useAuthStore } from "../stores/auth.store";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const errorMessage = ref("");
const statusMessage = ref("請稍候，我們正在同步你的帳戶資訊。");

function normalizeRedirect(path: string | null | undefined, fallback: string) {
  if (!path || !path.startsWith("/") || path.startsWith("//")) {
    return fallback;
  }

  return path;
}

function queryParam(name: string) {
  const value = route.query[name];
  return typeof value === "string" ? value : "";
}

async function redirectWithError(message: string) {
  const mode = queryParam("mode") === "link" ? "link" : "login";
  const redirect = normalizeRedirect(queryParam("redirect"), mode === "link" ? "/profile" : "/projects");
  const targetPath = mode === "link" ? redirect : "/login";
  const query: Record<string, string> = { oauth_error: message };

  if (mode === "login" && redirect !== "/projects") {
    query.redirect = redirect;
  }

  await router.replace({ path: targetPath, query });
}

onMounted(async () => {
  const mode = queryParam("mode") === "link" ? "link" : "login";
  const redirect = normalizeRedirect(queryParam("redirect"), mode === "link" ? "/profile" : "/projects");
  const provider = queryParam("provider");
  const remoteError = queryParam("error");
  const hashParams = new URLSearchParams(window.location.hash.slice(1));
  const accessToken = hashParams.get("access_token");

  if (remoteError) {
    errorMessage.value = remoteError;
    await redirectWithError(remoteError);
    return;
  }

  if (!accessToken) {
    const message = "登入資訊已失效，請重新再試一次。";
    errorMessage.value = message;
    await redirectWithError(message);
    return;
  }

  try {
    const user = await authStore.completeOAuthLogin(accessToken);
    if (mode === "link") {
      await router.replace({
        path: redirect,
        query: provider ? { linked: provider } : undefined,
      });
      return;
    }

    if (!user.user_identity && !user.user_purpose) {
      await router.replace({ name: "survey" });
      return;
    }

    await router.replace({ path: redirect });
  } catch (error) {
    const message = getApiErrorMessage(error, "登入失敗，請稍後再試一次。");
    errorMessage.value = message;
    await redirectWithError(message);
  }
});
</script>

<style scoped>
.callback-page {
  min-height: 100vh;
  background: url("@/assets/legacy/bricks_bg.svg") center top / cover no-repeat;
}

.callback-page__body {
  min-height: calc(100vh - 48px);
  display: grid;
  place-items: center;
  padding: 8rem 1.5rem 2rem;
}

.callback-card {
  width: min(28rem, 100%);
  border: 1px solid #e1dcdc;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.9);
  padding: 2rem 1.5rem;
  text-align: center;
  box-shadow: 0 18px 36px rgba(18, 4, 6, 0.08);
}

.callback-card h1 {
  margin: 0;
  font-size: 1.75rem;
}

.callback-card p {
  margin: 0.9rem 0 0;
  color: #5c5454;
  line-height: 1.7;
}
</style>
