"""End-to-end tests for the realtime collaboration WebSocket.

These prove the CRDT properties the feature promises, over the real wire protocol:
concurrent edits converge with no lost characters (F1/F4), an offline client's edits
merge on reconnect instead of clobbering peers (F3), and viewers are read-only (A1).
Two ``pycrdt`` docs stand in for two browsers running Yjs.
"""

from __future__ import annotations

import base64
from typing import Callable

from pycrdt import Doc, Text

SUBPROTOCOL = "bricks.collab.v1"
CONTENT_KEY = "content"


def _b64e(blob: bytes) -> str:
    return base64.b64encode(blob).decode("ascii")


def _b64d(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))


class Peer:
    """A simulated browser peer: a Yjs doc plus the client half of the sync protocol."""

    def __init__(self) -> None:
        self.doc = Doc()
        self.doc[CONTENT_KEY] = Text()

    @property
    def text(self) -> Text:
        return self.doc[CONTENT_KEY]

    def value(self) -> str:
        return str(self.doc[CONTENT_KEY])

    def handshake(self, ws) -> dict:
        sync = _recv_until(ws, "sync")
        server_sv = _b64d(sync["sv"])
        # Reply with what the server is missing, then request what we are missing.
        ws.send_json({"type": "sync-step2", "update": _b64e(self.doc.get_update(server_sv))})
        ws.send_json({"type": "sync-step1", "sv": _b64e(self.doc.get_state())})
        step2 = _recv_until(ws, "sync-step2")
        if step2.get("update"):
            self.doc.apply_update(_b64d(step2["update"]))
        return sync

    def edit(self, ws, mutate: Callable[[Text], None]) -> None:
        before = self.doc.get_state()
        mutate(self.text)
        ws.send_json({"type": "update", "update": _b64e(self.doc.get_update(before))})

    def edit_offline(self, mutate: Callable[[Text], None]) -> None:
        """Mutate the local doc without sending — simulates editing while disconnected."""
        mutate(self.text)

    def barrier(self, ws) -> None:
        """Round-trip on this socket so prior messages are guaranteed processed."""
        ws.send_json({"type": "sync-step1", "sv": _b64e(self.doc.get_state())})
        step2 = _recv_until(ws, "sync-step2")
        if step2.get("update"):
            self.doc.apply_update(_b64d(step2["update"]))

    def drain_until(self, ws, predicate: Callable[[str], bool]) -> None:
        while not predicate(self.value()):
            message = ws.receive_json()
            if message.get("type") in {"update", "sync-step2"} and message.get("update"):
                self.doc.apply_update(_b64d(message["update"]))


def _recv_until(ws, wanted: str) -> dict:
    while True:
        message = ws.receive_json()
        if message.get("type") == wanted:
            return message


def _register(client, email: str, name: str, password: str = "super-secret") -> str:
    response = client.post(
        "/api/v1/auth/register",
        json={"user_email": email, "user_password": password, "user_name": name},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _setup_shared_text_box(client, *, second_permission: str) -> tuple[str, str, int, int]:
    """Owner + one invited member (edit/view) on a project with one empty text box."""
    owner_token = _register(client, "owner@example.com", "Owner")
    member_token = _register(client, "member@example.com", "Member")

    project = client.post(
        "/api/v1/projects",
        headers=_auth(owner_token),
        json={"project_name": "Collab Hub", "project_type": "Shared"},
    ).json()
    project_id = project["id"]

    invite = client.post(
        f"/api/v1/projects/{project_id}/members",
        headers=_auth(owner_token),
        json={"user_email": "member@example.com", "permission": second_permission},
    )
    assert invite.status_code == 201

    record = client.post(
        f"/api/v1/projects/{project_id}/records",
        headers=_auth(owner_token),
        json={"record_name": "Sync"},
    ).json()

    text_box = client.post(
        f"/api/v1/records/{record['id']}/text-boxes",
        headers=_auth(owner_token),
        json={"textBox_content": ""},
    ).json()
    return owner_token, member_token, text_box["id"], record["id"]


def _ws_url(text_box_id: int) -> str:
    return f"/api/v1/ws/text-boxes/{text_box_id}"


def test_concurrent_edits_converge(client):
    owner_token, editor_token, text_box_id, _ = _setup_shared_text_box(client, second_permission="edit")

    with client.websocket_connect(_ws_url(text_box_id), subprotocols=[SUBPROTOCOL, owner_token]) as ws_a, \
        client.websocket_connect(_ws_url(text_box_id), subprotocols=[SUBPROTOCOL, editor_token]) as ws_b:
        peer_a = Peer()
        peer_b = Peer()
        assert peer_a.handshake(ws_a)["canEdit"] is True
        assert peer_b.handshake(ws_b)["canEdit"] is True

        # Two editors type at the same position simultaneously.
        peer_a.edit(ws_a, lambda t: t.insert(0, "Hello"))
        peer_b.edit(ws_b, lambda t: t.insert(0, "World"))

        peer_a.drain_until(ws_a, lambda v: "World" in v)
        peer_b.drain_until(ws_b, lambda v: "Hello" in v)

        # No lost updates, no manual conflict resolution: both sides converge identically.
        assert peer_a.value() == peer_b.value()
        assert "Hello" in peer_a.value()
        assert "World" in peer_a.value()
        assert len(peer_a.value()) == len("Hello") + len("World")


def test_offline_reconnect_merges_without_clobber(client):
    owner_token, editor_token, text_box_id, _ = _setup_shared_text_box(client, second_permission="edit")

    peer_a = Peer()
    peer_b = Peer()

    # B stays connected the whole time; A connects, disconnects, then reconnects.
    with client.websocket_connect(_ws_url(text_box_id), subprotocols=[SUBPROTOCOL, editor_token]) as ws_b:
        peer_b.handshake(ws_b)

        # A connects briefly and seeds "AAA", which B receives.
        with client.websocket_connect(_ws_url(text_box_id), subprotocols=[SUBPROTOCOL, owner_token]) as ws_a:
            peer_a.handshake(ws_a)
            peer_a.edit(ws_a, lambda t: t.insert(0, "AAA"))
            peer_b.drain_until(ws_b, lambda v: "AAA" in v)
        # A is now offline (inner socket closed); B is still connected.

        # B keeps working while A is away.
        peer_b.edit(ws_b, lambda t: t.insert(len(t), "BBB"))
        peer_b.barrier(ws_b)  # ensure the server applied "BBB"

        # A, still offline, makes a local edit the server has never seen.
        peer_a.edit_offline(lambda t: t.insert(0, "Z"))

        # A reconnects: the sync handshake merges its offline "Z" with the server's
        # "AAABBB" instead of overwriting either side.
        with client.websocket_connect(_ws_url(text_box_id), subprotocols=[SUBPROTOCOL, owner_token]) as ws_a2:
            peer_a.handshake(ws_a2)
            peer_a.drain_until(ws_a2, lambda v: "BBB" in v)
            peer_b.drain_until(ws_b, lambda v: "Z" in v)

    # Everyone converged and nothing was lost.
    assert peer_a.value() == peer_b.value()
    for fragment in ("Z", "AAA", "BBB"):
        assert fragment in peer_a.value()


def test_viewer_updates_are_dropped(client):
    from app.collab.rooms import registry

    owner_token, viewer_token, text_box_id, _ = _setup_shared_text_box(client, second_permission="view")

    with client.websocket_connect(_ws_url(text_box_id), subprotocols=[SUBPROTOCOL, owner_token]) as ws_owner:
        owner = Peer()
        owner.handshake(ws_owner)
        owner.edit(ws_owner, lambda t: t.insert(0, "OWNER"))
        owner.barrier(ws_owner)  # ensure the server applied the owner's edit

        with client.websocket_connect(
            _ws_url(text_box_id), subprotocols=[SUBPROTOCOL, viewer_token]
        ) as ws_viewer:
            viewer = Peer()
            assert viewer.handshake(ws_viewer)["canEdit"] is False

            # Viewer attempts a mutation; the server must drop it (A1).
            rogue = Doc()
            rogue[CONTENT_KEY] = Text()
            rogue[CONTENT_KEY].insert(0, "HACK")
            ws_viewer.send_json({"type": "update", "update": _b64e(rogue.get_update())})
            viewer.barrier(ws_viewer)  # forces the server to process the dropped update first

            room = registry.get_room(text_box_id)
            assert "HACK" not in str(room.doc[CONTENT_KEY])
            assert "OWNER" in str(room.doc[CONTENT_KEY])
