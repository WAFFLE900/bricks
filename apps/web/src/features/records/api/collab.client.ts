import { ACCESS_TOKEN_KEY } from "@/shared/api/client";
import { env } from "@/shared/config/env";

// Must match app.collab.protocol.SUBPROTOCOL on the API.
export const COLLAB_SUBPROTOCOL = "bricks.collab.v1";

export type CollabStatus = "idle" | "connecting" | "open" | "closed";

export interface CollabMember {
  userId: number;
  userName: string;
  canEdit: boolean;
}

export interface CollabSyncPayload {
  /** Server state vector (Yjs SyncStep1). */
  sv: Uint8Array;
  canEdit: boolean;
  members: CollabMember[];
}

export interface CollabHandlers {
  /** Server SyncStep1 + room metadata, sent right after the socket opens (and on every reconnect). */
  onSync?: (payload: CollabSyncPayload) => void;
  /** A diff the server computed against our state vector — apply it to the local doc. */
  onSyncStep2?: (update: Uint8Array) => void;
  /** A relayed peer update — apply it to the local doc. */
  onUpdate?: (update: Uint8Array) => void;
  onPresence?: (members: CollabMember[]) => void;
  onStatus?: (status: CollabStatus) => void;
}

const MAX_RECONNECT_DELAY = 15000;

function toBase64(bytes: Uint8Array): string {
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}

function fromBase64(value: unknown): Uint8Array | null {
  if (typeof value !== "string" || value.length === 0) {
    return null;
  }
  try {
    const binary = atob(value);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  } catch {
    return null;
  }
}

/**
 * Thin WebSocket transport for one text-box collaboration room. It frames base64
 * Yjs blobs (state vectors / updates) over JSON and reconnects with backoff. It holds
 * no document state of its own: on (re)connect the server sends {@link CollabHandlers.onSync}
 * and the owning composable drives the Yjs sync handshake, so offline edits merge via
 * state-vector diffs instead of being replayed as a clobbering full-text buffer (F3).
 */
export class CollabConnection {
  private socket: WebSocket | null = null;
  private status: CollabStatus = "idle";
  private closedByClient = false;
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private readonly textBoxId: number,
    private readonly handlers: CollabHandlers = {},
  ) {}

  connect(): void {
    if (!env.wsBaseUrl) {
      return;
    }
    const token = window.localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
      return;
    }

    this.closedByClient = false;
    this.setStatus("connecting");

    const url = `${env.wsBaseUrl}/ws/text-boxes/${this.textBoxId}`;
    const socket = new WebSocket(url, [COLLAB_SUBPROTOCOL, token]);
    this.socket = socket;

    socket.onopen = () => {
      this.reconnectAttempts = 0;
      this.setStatus("open");
    };
    socket.onmessage = (event) => this.handleMessage(event);
    socket.onclose = () => this.handleClose();
    socket.onerror = () => {
      // onclose fires after onerror; reconnect is scheduled there.
    };
  }

  /** Ask the server for everything we are missing relative to our state vector. */
  sendSyncStep1(stateVector: Uint8Array): void {
    this.send({ type: "sync-step1", sv: toBase64(stateVector) });
  }

  /** Send our contribution (the update the server is missing) during the handshake. */
  sendSyncStep2(update: Uint8Array): void {
    this.send({ type: "sync-step2", update: toBase64(update) });
  }

  /** Broadcast an incremental local Yjs update. */
  sendUpdate(update: Uint8Array): void {
    this.send({ type: "update", update: toBase64(update) });
  }

  disconnect(): void {
    this.closedByClient = true;
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socket) {
      this.socket.onclose = null;
      this.socket.close();
      this.socket = null;
    }
    this.setStatus("closed");
  }

  private send(message: Record<string, unknown>): void {
    // Dropped while the socket is down: the local Yjs doc retains the change and the
    // reconnect sync handshake re-merges it, so there is nothing to buffer here.
    if (this.socket && this.status === "open") {
      this.socket.send(JSON.stringify(message));
    }
  }

  private handleMessage(event: MessageEvent): void {
    if (typeof event.data !== "string") {
      return;
    }
    let message: Record<string, unknown>;
    try {
      message = JSON.parse(event.data) as Record<string, unknown>;
    } catch {
      return;
    }

    switch (message.type) {
      case "sync": {
        const sv = fromBase64(message.sv) ?? new Uint8Array();
        this.handlers.onSync?.({
          sv,
          canEdit: Boolean(message.canEdit),
          members: (message.members as CollabMember[]) ?? [],
        });
        this.handlers.onPresence?.((message.members as CollabMember[]) ?? []);
        break;
      }
      case "sync-step2": {
        const update = fromBase64(message.update);
        if (update) {
          this.handlers.onSyncStep2?.(update);
        }
        break;
      }
      case "update": {
        const update = fromBase64(message.update);
        if (update) {
          this.handlers.onUpdate?.(update);
        }
        break;
      }
      case "presence":
        this.handlers.onPresence?.((message.members as CollabMember[]) ?? []);
        break;
    }
  }

  private handleClose(): void {
    this.socket = null;
    if (this.closedByClient) {
      this.setStatus("closed");
      return;
    }
    this.setStatus("closed");
    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    const delay = Math.min(MAX_RECONNECT_DELAY, 500 * 2 ** this.reconnectAttempts);
    this.reconnectAttempts += 1;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delay);
  }

  private setStatus(status: CollabStatus): void {
    if (this.status === status) {
      return;
    }
    this.status = status;
    this.handlers.onStatus?.(status);
  }
}
