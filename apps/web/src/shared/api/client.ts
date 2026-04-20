import axios from "axios";

import { env } from "@/shared/config/env";

export const ACCESS_TOKEN_KEY = "bricks.access_token";

const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  const token = window.localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;

