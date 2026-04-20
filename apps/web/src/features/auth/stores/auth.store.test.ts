import { createPinia, setActivePinia } from "pinia";
import { describe, expect, it, vi } from "vitest";

import { ACCESS_TOKEN_KEY } from "@/shared/api/client";
import { useAuthStore } from "./auth.store";

vi.mock("../api/auth.api", () => ({
  fetchCurrentUser: vi.fn(async () => ({
    id: 1,
    user_email: "jane@example.com",
    user_name: "Jane",
  })),
  login: vi.fn(async () => ({
    access_token: "token-123",
    token_type: "bearer",
    user: {
      id: 1,
      user_email: "jane@example.com",
      user_name: "Jane",
    },
  })),
  register: vi.fn(),
  submitSurvey: vi.fn(),
}));

describe("auth store", () => {
  it("persists access token after login", async () => {
    setActivePinia(createPinia());
    const store = useAuthStore();

    const user = await store.login({
      user_email: "jane@example.com",
      user_password: "secret",
    });

    expect(user.user_email).toBe("jane@example.com");
    expect(store.isAuthenticated).toBe(true);
    expect(window.localStorage.getItem(ACCESS_TOKEN_KEY)).toBe("token-123");
  });

  it("hydrates user state from oauth access token", async () => {
    setActivePinia(createPinia());
    const store = useAuthStore();

    const user = await store.completeOAuthLogin("oauth-token");

    expect(user.user_name).toBe("Jane");
    expect(store.isAuthenticated).toBe(true);
    expect(window.localStorage.getItem(ACCESS_TOKEN_KEY)).toBe("oauth-token");
  });
});
