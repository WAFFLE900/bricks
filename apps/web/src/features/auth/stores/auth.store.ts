import { defineStore } from "pinia";

import { ACCESS_TOKEN_KEY } from "@/shared/api/client";
import type { User } from "@/shared/types/domain";
import * as authApi from "../api/auth.api";

interface LoginPayload {
  user_email: string;
  user_password: string;
}

interface RegisterPayload extends LoginPayload {
  user_name: string;
}

interface SurveyPayload {
  user_purpose: string[];
  user_identity?: string | null;
  user_otherTool: string[];
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: window.localStorage.getItem(ACCESS_TOKEN_KEY) || "",
    user: null as User | null,
    ready: false,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.user),
  },
  actions: {
    setUser(user: User | null) {
      this.user = user;
    },
    setToken(token: string) {
      this.token = token;
      if (token) {
        window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
      } else {
        window.localStorage.removeItem(ACCESS_TOKEN_KEY);
      }
    },
    async bootstrap() {
      if (this.ready) {
        return;
      }

      if (!this.token) {
        this.ready = true;
        return;
      }

      this.loading = true;
      try {
        this.setUser(await authApi.fetchCurrentUser());
      } catch {
        this.logout();
      } finally {
        this.loading = false;
        this.ready = true;
      }
    },
    async login(payload: LoginPayload) {
      this.loading = true;
      try {
        const response = await authApi.login(payload);
        this.setToken(response.access_token);
        this.setUser(response.user);
        this.ready = true;
        return response.user;
      } finally {
        this.loading = false;
      }
    },
    async register(payload: RegisterPayload) {
      this.loading = true;
      try {
        const response = await authApi.register(payload);
        this.setToken(response.access_token);
        this.setUser(response.user);
        this.ready = true;
        return response.user;
      } finally {
        this.loading = false;
      }
    },
    async completeSurvey(payload: SurveyPayload) {
      this.loading = true;
      try {
        this.setUser(await authApi.submitSurvey(payload));
        return this.user;
      } finally {
        this.loading = false;
      }
    },
    async completeOAuthLogin(accessToken: string) {
      this.loading = true;
      this.setToken(accessToken);

      try {
        const user = await authApi.fetchCurrentUser();
        this.setUser(user);
        this.ready = true;
        return user;
      } catch (error) {
        this.logout();
        throw error;
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.setToken("");
      this.setUser(null);
      this.ready = true;
    },
  },
});
