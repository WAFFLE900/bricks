import apiClient from "@/shared/api/client";
import type { OAuthProvider, OAuthUrlResponse, User } from "@/shared/types/domain";

interface ProfilePayload {
  user_name: string;
  user_identity?: string | null;
  user_purpose: string[];
  user_otherTool: string[];
}

interface PasswordPayload {
  current_password?: string | null;
  new_password: string;
}

export async function updateProfile(payload: ProfilePayload) {
  const { data } = await apiClient.patch<User>("/users/me", payload);
  return data;
}

export async function changePassword(payload: PasswordPayload) {
  const { data } = await apiClient.post<User>("/users/me/password", payload);
  return data;
}

export async function fetchSocialLinkUrl(provider: OAuthProvider, redirect = "/profile") {
  const { data } = await apiClient.get<OAuthUrlResponse>(`/users/me/social-accounts/${provider}/link-url`, {
    params: { redirect },
  });
  return data;
}
