<template>
  <div class="shell">
    <header class="shell__header">
      <div>
        <p class="shell__eyebrow">Bricks Rewrite</p>
        <h1>Modern Frontend Shell</h1>
      </div>
      <nav class="shell__nav">
        <RouterLink to="/projects">Projects</RouterLink>
        <RouterLink v-if="!authStore.isAuthenticated" to="/login">Login</RouterLink>
        <RouterLink v-if="!authStore.isAuthenticated" to="/register">Register</RouterLink>
        <button v-if="authStore.isAuthenticated" type="button" @click="logout">Logout</button>
      </nav>
    </header>
    <main class="shell__content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, useRouter } from "vue-router";

import { useAuthStore } from "@/features/auth/stores/auth.store";

const authStore = useAuthStore();
const router = useRouter();

function logout() {
  authStore.logout();
  router.push({ name: "login" });
}
</script>

<style scoped>
.shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(255, 232, 214, 0.8), transparent 32%),
    radial-gradient(circle at top right, rgba(202, 234, 255, 0.75), transparent 28%),
    linear-gradient(180deg, #fcfaf6 0%, #f2eee5 100%);
  color: #1f2937;
}

.shell__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(31, 41, 55, 0.08);
  backdrop-filter: blur(10px);
}

.shell__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #b45309;
}

.shell__header h1 {
  margin: 0.25rem 0 0;
  font-size: 1.4rem;
}

.shell__nav {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.shell__nav a,
.shell__nav button {
  border: 0;
  background: rgba(255, 255, 255, 0.75);
  color: inherit;
  padding: 0.75rem 1rem;
  border-radius: 999px;
  text-decoration: none;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.shell__content {
  padding: 2rem;
}

@media (max-width: 720px) {
  .shell__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .shell__content {
    padding: 1rem;
  }
}
</style>

