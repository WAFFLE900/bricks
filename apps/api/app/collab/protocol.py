"""Wire protocol for the collaboration WebSocket.

This is the seam between the transport/room layer and the CRDT engine. Frames are
JSON text messages carrying base64-encoded Yjs binary blobs (state vectors and
updates) produced/consumed by a real CRDT document (``pycrdt.Doc`` server-side,
``yjs`` client-side). It implements the standard Yjs two-step sync handshake so that
convergence (F1/F4) and offline-reconnect merge (F3) are driven by state-vector diffs
rather than full-text overwrites.

Message shapes
--------------
server -> client ``sync``        : {type, sv, canEdit, members}   # metadata + server SyncStep1
client -> server ``sync-step1``  : {type, sv}                     # "send me what I'm missing"
server -> client ``sync-step2``  : {type, update}                 # diff computed against a peer sv
client -> server ``sync-step2``  : {type, update}                 # the client's contribution (editors only)
client -> server ``update``      : {type, update}                 # incremental Yjs update (editors only)
server -> client ``update``      : {type, update, from}           # relayed peer update
server -> client ``presence``    : {type, members}
"""

from __future__ import annotations

import base64
import binascii
from typing import Any

# Subprotocol echoed back on accept so browsers keep the connection open. The JWT is
# offered as a second subprotocol token by the client (browsers cannot set headers on
# a WebSocket handshake); see app.collab.routes.
SUBPROTOCOL = "bricks.collab.v1"

# Application-defined close codes (RFC 6455 4000-4999 private range).
CLOSE_UNAUTHENTICATED = 4401
CLOSE_NOT_FOUND = 4404
CLOSE_INTERNAL_ERROR = 4500

TYPE_SYNC = "sync"
TYPE_SYNC_STEP1 = "sync-step1"
TYPE_SYNC_STEP2 = "sync-step2"
TYPE_UPDATE = "update"
TYPE_PRESENCE = "presence"
TYPE_ERROR = "error"

# Inbound frames that carry a Yjs update to be applied to the room document. Both are
# treated identically server-side (apply + relay); a viewer's are dropped for A1.
MUTATION_TYPES = frozenset({TYPE_SYNC_STEP2, TYPE_UPDATE})


def encode_bytes(blob: bytes | None) -> str | None:
    if blob is None:
        return None
    return base64.b64encode(blob).decode("ascii")


def decode_bytes(value: Any) -> bytes | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (ValueError, binascii.Error):
        return None
