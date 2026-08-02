"""Collaboration WebSocket route.

Mounted under the existing ``/api/v1`` prefix on the single uvicorn process. Browsers
cannot set an ``Authorization`` header on a WebSocket handshake, so the JWT is passed
as a second ``Sec-WebSocket-Protocol`` token; we echo the app subprotocol back on
accept. Auth/authorization happens before ``accept()`` (A3), and the connection is
rejected outright for non-members / unknown text boxes.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.collab import protocol
from app.collab.auth import CollabAuthError, authenticate_ws
from app.collab.rooms import Peer, registry

logger = logging.getLogger(__name__)

router = APIRouter()


def _extract_token(websocket: WebSocket) -> str | None:
    for candidate in websocket.scope.get("subprotocols", []):
        if candidate and candidate != protocol.SUBPROTOCOL:
            return candidate
    return None


@router.websocket("/ws/text-boxes/{text_box_id}")
async def collaborate_text_box(websocket: WebSocket, text_box_id: int) -> None:
    token = _extract_token(websocket)
    if not token:
        await websocket.close(code=protocol.CLOSE_UNAUTHENTICATED)
        return

    try:
        identity = await authenticate_ws(token, text_box_id)
    except CollabAuthError as exc:
        await websocket.close(code=exc.close_code)
        return

    await websocket.accept(subprotocol=protocol.SUBPROTOCOL)

    peer = Peer(websocket=websocket, identity=identity)
    room = registry.get_room(text_box_id)
    await room.register(peer)

    try:
        # Server SyncStep1 + metadata; the client replies with its own step1/step2 so
        # both docs converge via state-vector diffs (no full-text overwrite).
        await peer.send(room.sync_message(peer))
        await room.broadcast_presence()

        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except (ValueError, TypeError):
                continue
            if not isinstance(data, dict):
                continue
            message_type = data.get("type")
            if message_type == protocol.TYPE_SYNC_STEP1:
                await room.handle_sync_step1(peer, data)
            elif message_type in protocol.MUTATION_TYPES:
                await room.handle_update(peer, data)
    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001 - always run room cleanup below
        logger.exception("collab: unexpected error on text box %s", text_box_id)
    finally:
        await room.remove(peer)
