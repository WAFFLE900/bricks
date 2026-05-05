<template>
  <div class="register-page">
    <LegacyPublicHeader />

    <main class="register-page__body">
      <section class="register-card">
        <h1>註冊</h1>
        <p class="register-card__lead">建立你的 BRICKS 帳號，開始管理你的專案與會議記錄。</p>

        <p v-if="errorMessage" class="register-card__error" role="alert">
          {{ errorMessage }}
        </p>

        <form class="register-form" @submit.prevent="handleSubmit">
          <input
            v-model="form.user_name"
            aria-label="Name"
            autocomplete="name"
            placeholder="憪?"
            required
            type="text"
          />
          <input
            v-model="form.user_email"
            aria-label="Email"
            autocomplete="email"
            placeholder="?餃?靽∠拳"
            required
            type="email"
          />

          <div class="register-form__password">
            <input
              v-model="form.user_password"
              aria-label="Password"
              autocomplete="new-password"
              placeholder="撖Ⅳ"
              required
              :type="showPassword ? 'text' : 'password'"
            />
            <button class="register-form__toggle" type="button" @click="showPassword = !showPassword">
              <img :src="showPassword ? eyeOnIconUrl : eyeOffIconUrl" alt="Toggle password visibility" />
            </button>
          </div>

          <button aria-label="Register" class="register-form__submit" :disabled="authStore.loading" type="submit">
            撱箇?撣唾?
          </button>
        </form>

        <p class="register-card__switch">
          撌脩??董??嚗?          <RouterLink to="/login">??餃</RouterLink>
        </p>
      </section>
    </main>

    <LegacyPublicFooter />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import eyeOffIconUrl from "@/assets/legacy/eye/eye_origin.svg";
import eyeOnIconUrl from "@/assets/legacy/eye/eye_on.svg";
import LegacyPublicFooter from "@/shared/ui/legacy/LegacyPublicFooter.vue";
import LegacyPublicHeader from "@/shared/ui/legacy/LegacyPublicHeader.vue";
import { getApiErrorMessage } from "@/shared/utils/getApiErrorMessage";
import { useAuthStore } from "../stores/auth.store";

const authStore = useAuthStore();
const router = useRouter();
const errorMessage = ref("");
const showPassword = ref(false);

const form = reactive({
  user_name: "",
  user_email: "",
  user_password: "",
});

async function handleSubmit() {
  errorMessage.value = "";

  try {
    await authStore.register(form);
    await router.push({ name: "survey" });
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, "Registration failed. Please try again.");
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: url("@/assets/legacy/bricks_bg.svg") center top / cover no-repeat;
}

.register-page__body {
  flex: 1;
  display: grid;
  place-items: center;
  padding: 8.5rem 1.5rem 2rem;
}

.register-card {
  width: min(24rem, 100%);
}

.register-card h1 {
  margin: 0;
  text-align: center;
  font-size: 1.8rem;
}

.register-card__lead {
  margin: 0.75rem 0 0;
  text-align: center;
  color: #6d6666;
  line-height: 1.7;
}

.register-card__error {
  margin: 1rem 0 0;
  border: 1px solid #c65659;
  border-radius: 14px;
  background: #f1d5d6;
  padding: 0.8rem 1rem;
  color: #c65659;
}

.register-form {
  display: grid;
  gap: 1rem;
  margin-top: 1.5rem;
}

.register-form input {
  width: 100%;
  border: 1.5px solid #c7c2c2;
  border-radius: 12px;
  padding: 0.95rem 1rem 0.95rem 1.15rem;
  background: #fff;
}

.register-form__password {
  position: relative;
}

.register-form__toggle {
  position: absolute;
  top: 50%;
  right: 0.9rem;
  transform: translateY(-50%);
  border: 0;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.register-form__toggle img {
  width: 1.15rem;
  height: 1.15rem;
}

.register-form__submit {
  border: 0;
  border-radius: 14px;
  padding: 0.95rem 1rem;
  background: #b82c30;
  color: #fff;
  cursor: pointer;
}

.register-form__submit:hover {
  background: #d48083;
}

.register-form__submit:disabled {
  cursor: wait;
  opacity: 0.7;
}

.register-card__switch {
  margin: 1rem 0 0;
  text-align: center;
  color: #b6aeae;
}

.register-card__switch a {
  color: #c65659;
  text-decoration: none;
}

@media (max-width: 720px) {
  .register-page__body {
    padding-top: 10rem;
  }
}
</style>



