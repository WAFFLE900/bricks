function toWebSocketBase(httpBase: string): string {
  if (!httpBase) {
    return "";
  }
  const origin = typeof window !== "undefined" ? window.location.origin : "http://localhost";
  try {
    const url = new URL(httpBase, origin);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    return url.toString().replace(/\/$/, "");
  } catch {
    return httpBase.replace(/^http/i, "ws").replace(/\/$/, "");
  }
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

export const env = {
  apiBaseUrl,
  // Realtime collaboration shares the API origin (single uvicorn process); the WS
  // route lives under the same /api/v1 prefix as REST.
  wsBaseUrl: toWebSocketBase(apiBaseUrl),
} as const;
