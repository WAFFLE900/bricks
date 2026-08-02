"""In-process collaboration rooms (single-process free-tier authority).

One room per ``TextBox.id``. A room owns a server-authoritative ``pycrdt.Doc`` whose
``content`` :class:`~pycrdt.Text` is the merged document. Inbound Yjs updates from
editors are applied to that doc (CRDT merge, F1/F4) and relayed to peers immediately
(F2); the state-vector sync handshake lets a reconnecting/offline client converge
without clobbering peers (F3). Viewers authenticate but their inbound mutations are
dropped (A1). A debounced flush materialises the converged text + a full CRDT
snapshot back to Postgres (A4/F5), and the snapshot rehydrates the doc on cold start.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

from pycrdt import Doc, Text
from starlette.websockets import WebSocket

from app.collab import protocol
from app.collab.auth import CollabIdentity
from app.collab.persistence import load_snapshot, persist_snapshot
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Root key of the shared Text inside each room's Y.Doc. Must match the client
# (useTextBoxCollaboration.ts) so both docs address the same shared type.
CONTENT_KEY = "content"


@dataclass(eq=False)
class Peer:
    """A single WebSocket connection. Identity-hashed so it can live in a set."""

    websocket: WebSocket
    identity: CollabIdentity

    async def send(self, message: dict[str, Any]) -> None:
        await self.websocket.send_text(json.dumps(message))


class Room:
    def __init__(self, text_box_id: int, registry: "RoomRegistry") -> None:
        self.text_box_id = text_box_id
        self._registry = registry
        self.peers: set[Peer] = set()
        self.doc = Doc()
        self.doc[CONTENT_KEY] = Text()
        self._loaded = False
        self._dirty = False
        self._last_editor_id: int | None = None
        self._debounce = get_settings().collab_snapshot_debounce_seconds
        self._flush_task: asyncio.Task[None] | None = None
        self._flush_lock = asyncio.Lock()

    @property
    def _content(self) -> Text:
        return self.doc[CONTENT_KEY]

    async def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        snapshot = await load_snapshot(self.text_box_id)
        if snapshot is not None:
            if snapshot.state:
                # Authoritative CRDT snapshot: rehydrate the doc exactly.
                try:
                    self.doc.apply_update(snapshot.state)
                except Exception:  # noqa: BLE001 - a corrupt snapshot must not brick the room
                    logger.exception("collab: failed to rehydrate CRDT state for %s", self.text_box_id)
            elif snapshot.text:
                # Legacy row created via REST before it was ever collaborated on: seed
                # the shared Text once so peers see existing content. Only the server
                # seeds (clients start empty) so there is no double-insert on join.
                self._content.insert(0, snapshot.text)
        self._loaded = True

    async def register(self, peer: Peer) -> None:
        await self._ensure_loaded()
        self.peers.add(peer)

    def sync_message(self, peer: Peer) -> dict[str, Any]:
        """Server SyncStep1 + room metadata sent right after the socket opens."""
        return {
            "type": protocol.TYPE_SYNC,
            "sv": protocol.encode_bytes(self.doc.get_state()),
            "canEdit": peer.identity.can_edit,
            "members": self._members(),
        }

    async def handle_sync_step1(self, peer: Peer, data: dict[str, Any]) -> None:
        """Reply with the update the requesting peer is missing (read-only; viewers too)."""
        state_vector = protocol.decode_bytes(data.get("sv"))
        if state_vector is None:
            return
        try:
            update = self.doc.get_update(state_vector)
        except Exception:  # noqa: BLE001 - a bad state vector must not kill the socket
            logger.debug("collab: bad state vector on text box %s", self.text_box_id, exc_info=True)
            return
        await peer.send({"type": protocol.TYPE_SYNC_STEP2, "update": protocol.encode_bytes(update)})

    async def handle_update(self, peer: Peer, data: dict[str, Any]) -> None:
        """Apply an editor's Yjs update to the room doc and relay it to peers."""
        if not peer.identity.can_edit:
            # A1: viewers are strictly read-only; drop inbound update / sync-step2.
            return

        update = protocol.decode_bytes(data.get("update"))
        if update is None:
            return
        try:
            self.doc.apply_update(update)
        except Exception:  # noqa: BLE001 - a malformed update must not kill the socket
            logger.debug("collab: bad update on text box %s", self.text_box_id, exc_info=True)
            return

        self._last_editor_id = peer.identity.user_id
        self._dirty = True

        # Relay the raw update to the other peers. Yjs updates are commutative,
        # idempotent and associative, so re-broadcasting the exact bytes converges
        # regardless of interleave/reorder/duplication (F4).
        await self._broadcast(
            {
                "type": protocol.TYPE_UPDATE,
                "update": data.get("update"),
                "from": peer.identity.user_id,
            },
            exclude=peer,
        )
        self._schedule_flush()

    async def broadcast_presence(self) -> None:
        await self._broadcast({"type": protocol.TYPE_PRESENCE, "members": self._members()})

    async def remove(self, peer: Peer) -> None:
        self.peers.discard(peer)
        if self.peers:
            await self.broadcast_presence()
            return
        # Last peer left: flush any pending edit before the room is discarded so the
        # converged state survives even if nobody reconnects.
        await self._cancel_flush()
        await self._flush()
        self._registry.discard(self.text_box_id)

    def _members(self) -> list[dict[str, Any]]:
        deduped: dict[int, dict[str, Any]] = {}
        for peer in self.peers:
            deduped[peer.identity.user_id] = {
                "userId": peer.identity.user_id,
                "userName": peer.identity.user_name,
                "canEdit": peer.identity.can_edit,
            }
        return list(deduped.values())

    async def _broadcast(self, message: dict[str, Any], exclude: Peer | None = None) -> None:
        payload = json.dumps(message)
        for peer in list(self.peers):
            if peer is exclude:
                continue
            try:
                await peer.websocket.send_text(payload)
            except Exception:  # noqa: BLE001 - a dead peer must not break the room
                logger.debug("collab: failed to send to peer, dropping", exc_info=True)
                self.peers.discard(peer)

    def _schedule_flush(self) -> None:
        if self._flush_task is not None and not self._flush_task.done():
            self._flush_task.cancel()
        self._flush_task = asyncio.create_task(self._debounced_flush())

    async def _debounced_flush(self) -> None:
        try:
            await asyncio.sleep(self._debounce)
        except asyncio.CancelledError:
            return
        await self._flush()

    async def _cancel_flush(self) -> None:
        task = self._flush_task
        if task is not None and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def _flush(self) -> None:
        async with self._flush_lock:
            if not self._dirty or self._last_editor_id is None:
                return
            # Materialise the converged CRDT state: plain text for REST/search/tags
            # (A4) plus a full update blob so a cold start rehydrates identically (F3).
            text = str(self._content)
            state = self.doc.get_update()
            actor = self._last_editor_id
            self._dirty = False
            try:
                await persist_snapshot(self.text_box_id, state, text, actor)
            except Exception:  # noqa: BLE001 - persistence failure should not kill the socket
                logger.exception("collab: failed to persist text box %s", self.text_box_id)
                self._dirty = True  # retry on the next edit / final flush


class RoomRegistry:
    def __init__(self) -> None:
        self._rooms: dict[int, Room] = {}

    def get_room(self, text_box_id: int) -> Room:
        room = self._rooms.get(text_box_id)
        if room is None:
            room = Room(text_box_id, self)
            self._rooms[text_box_id] = room
        return room

    def discard(self, text_box_id: int) -> None:
        self._rooms.pop(text_box_id, None)


registry = RoomRegistry()
