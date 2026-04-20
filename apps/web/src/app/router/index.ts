import { createRouter, createWebHistory } from "vue-router";

import { pinia } from "../store";
import { useAuthStore } from "@/features/auth/stores/auth.store";

const routes = [
  {
    path: "/",
    name: "home",
    component: () => import("@/features/home/pages/HomeLandingPage.vue"),
    meta: { public: true },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/features/auth/pages/LoginPage.vue"),
    meta: { public: true },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/features/auth/pages/RegisterPage.vue"),
    meta: { public: true },
  },
  {
    path: "/auth/callback",
    name: "oauth-callback",
    component: () => import("@/features/auth/pages/OAuthCallbackPage.vue"),
    meta: { public: true },
  },
  {
    path: "/survey",
    name: "survey",
    component: () => import("@/features/auth/pages/SurveyPage.vue"),
  },
  {
    path: "/profile",
    name: "profile",
    component: () => import("@/features/profile/pages/ProfilePage.vue"),
  },
  {
    path: "/projects",
    name: "projects",
    component: () => import("@/features/projects/pages/ProjectDashboardPage.vue"),
  },
  {
    path: "/projects/:projectId/records",
    name: "records",
    component: () => import("@/features/records/pages/RecordWorkspacePage.vue"),
    props: true,
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore(pinia);

  if (!authStore.ready) {
    await authStore.bootstrap();
  }

  if (to.meta.public) {
    if (authStore.isAuthenticated && (to.name === "login" || to.name === "register")) {
      return { name: "projects" };
    }
    return true;
  }

  if (!authStore.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }

  return true;
});
