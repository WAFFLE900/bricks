import { onBeforeUnmount, onMounted, ref } from "vue";
import * as Y from "yjs";

import { CollabConnection, type CollabMember, type CollabStatus } from "../api/collab.client";

interface UseTextBoxCollaborationOptions {
  textBoxId: number;
  initialContent: string;
  /** Whether the local user has project edit permission (A1 client-side gate). */
  canEdit: boolean;
}

// Root key of the shared Text; must match CONTENT_KEY in app/collab/rooms.py.
const CONTENT_KEY = "content";

/**
 * Computes the minimal (prefix, deleteLength, insertText) diff between two strings so a
 * whole-textarea value change is applied to the CRDT as targeted insert/delete ops.
 * Character-level ops are what let concurrent edits merge instead of clobber (F1) and
 * keep other peers' carets stable.
 */
function diffStrings(current: string, next: string): { index: number; deleteLength: number; insert: string } {
  const maxPrefix = Math.min(current.length, next.length);
  let prefix = 0;
  while (prefix < maxPrefix && current[prefix] === next[prefix]) {
    prefix += 1;
  }
  let suffix = 0;
  while (
    suffix < maxPrefix - prefix &&
    current[current.length - 1 - suffix] === next[next.length - 1 - suffix]
  ) {
    suffix += 1;
  }
  return {
    index: prefix,
    deleteLength: current.length - prefix - suffix,
    insert: next.slice(prefix, next.length - suffix),
  };
}

/**
 * Binds one text-box collaboration room to a Yjs document. The shared {@link Y.Text}
 * is the source of truth: local edits are applied as character-level ops, remote
 * updates are merged by the CRDT, and {@link content} always mirrors the converged
 * text. The connection only transports state vectors / updates — reconnection re-runs
 * the Yjs sync handshake so offline edits merge rather than overwrite (F3).
 */
export function useTextBoxCollaboration(options: UseTextBoxCollaborationOptions) {
  const { textBoxId, initialContent, canEdit } = options;

  const status = ref<CollabStatus>("idle");
  const members = ref<CollabMember[]>([]);
  const content = ref(initialContent);
  const remoteCanEdit = ref(false);

  // The client doc starts empty and receives content from the server on sync; it never
  // seeds from initialContent, so the server's seed of a legacy row is not duplicated.
  const doc = new Y.Doc();
  const yText = doc.getText(CONTENT_KEY);
  // Marks transactions whose updates came off the wire, so we don't echo them back.
  const remoteOrigin = Symbol("collab-remote");

  const connection = new CollabConnection(textBoxId, {
    onSync: ({ sv, canEdit: serverCanEdit, members: roster }) => {
      remoteCanEdit.value = serverCanEdit;
      members.value = roster;
      // Reply to the server's SyncStep1 with what it is missing, then request what we
      // are missing. Both directions are state-vector diffs — no full-text overwrite.
      connection.sendSyncStep2(Y.encodeStateAsUpdate(doc, sv));
      connection.sendSyncStep1(Y.encodeStateVector(doc));
    },
    onSyncStep2: (update) => {
      Y.applyUpdate(doc, update, remoteOrigin);
    },
    onUpdate: (update) => {
      Y.applyUpdate(doc, update, remoteOrigin);
    },
    onPresence: (roster) => {
      members.value = roster;
    },
    onStatus: (next) => {
      status.value = next;
    },
  });

  const onDocUpdate = (update: Uint8Array, origin: unknown): void => {
    // Keep the reactive mirror aligned with the converged CRDT text.
    content.value = yText.toString();
    if (origin === remoteOrigin) {
      return; // never re-broadcast an update we just received
    }
    if (!canEdit) {
      return; // A1 client-side gate
    }
    connection.sendUpdate(update);
  };

  doc.on("update", onDocUpdate);

  /** Apply a full textarea value as a minimal CRDT diff (character-level merge). */
  function pushLocalEdit(nextContent: string): void {
    if (!canEdit) {
      content.value = nextContent;
      return;
    }
    const currentText = yText.toString();
    if (currentText === nextContent) {
      return;
    }
    const { index, deleteLength, insert } = diffStrings(currentText, nextContent);
    doc.transact(() => {
      if (deleteLength > 0) {
        yText.delete(index, deleteLength);
      }
      if (insert) {
        yText.insert(index, insert);
      }
    });
  }

  onMounted(() => {
    connection.connect();
  });

  onBeforeUnmount(() => {
    doc.off("update", onDocUpdate);
    connection.disconnect();
    doc.destroy();
  });

  return { status, members, content, remoteCanEdit, pushLocalEdit };
}
