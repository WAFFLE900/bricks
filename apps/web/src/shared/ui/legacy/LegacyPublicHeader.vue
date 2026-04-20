<template>
  <header :class="['public-header', { 'public-header--transparent': transparent }]">
    <RouterLink class="public-header__brand" to="/">
      <img :src="logoUrl" alt="Bricks" />
    </RouterLink>

    <nav class="public-header__nav" aria-label="Primary">
      <RouterLink class="public-header__button" to="/">探索</RouterLink>
      <RouterLink class="public-header__button public-header__button--accent" to="/login">
        登入
      </RouterLink>
      <RouterLink class="public-header__button" to="/register">註冊</RouterLink>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";

import logoUrl from "@/assets/legacy/brickslogo.svg";

defineProps<{
  transparent?: boolean;
}>();
</script>

<style scoped>
.public-header {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 50;
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-height: 64px;
  padding: 0.8rem 5.21%;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(12px);
}

.public-header--transparent {
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}

.public-header__brand img {
  width: auto;
  height: 2rem;
  display: block;
}

.public-header__nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.public-header__button {
  min-width: 4.75rem;
  border: 1px solid #120405;
  border-radius: 10px;
  padding: 0.55rem 1rem;
  text-align: center;
  text-decoration: none;
  letter-spacing: 0.08em;
  font-size: 0.95rem;
  background: rgba(255, 255, 255, 0.85);
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.public-header--transparent .public-header__button {
  background: rgba(255, 255, 255, 0.3);
}

.public-header__button:hover {
  background: #f2eeee;
}

.public-header__button--accent {
  background: #b82c30;
  border-color: #b82c30;
  color: #fff;
}

.public-header__button--accent:hover {
  background: #d48083;
}

@media (max-width: 720px) {
  .public-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .public-header__nav {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }
}
</style>
