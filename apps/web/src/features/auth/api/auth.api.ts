import apiClient from "@/shared/api/client";
import type { AuthTokenResponse, OAuthProvider, OAuthUrlResponse, User } from "@/shared/types/domain";

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

export async function login(payload: LoginPayload) {
  const { data } = await apiClient.post<AuthTokenResponse>("/auth/login", payload);
  return data;
}

export async function register(payload: RegisterPayload) {
  const { data } = await apiClient.post<AuthTokenResponse>("/auth/register", payload);
  return data;
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}

export async function submitSurvey(payload: SurveyPayload) {
  const { data } = await apiClient.post<User>("/auth/survey", payload);
  return data;
}

export async function fetchOAuthUrl(provider: OAuthProvider, redirect?: string) {
  const { data } = await apiClient.get<OAuthUrlResponse>(`/auth/${provider}/url`, {
    params: redirect ? { redirect } : undefined,
  });
  return data;
}
