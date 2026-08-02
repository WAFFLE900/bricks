"""Realtime collaboration for record text boxes.

Scope is a single ``textBox`` content block per room (A2/A5): the room key is the
existing integer ``TextBox.id`` primary key, and content edits never create, delete
or re-key rows. Block-set lifecycle (create/reorder/delete text boxes), projects,
records, tags, memberships and notifications remain REST.

The room authority is the in-process :mod:`app.collab.rooms` registry on the single
uvicorn process (free-tier constraint: no Redis/broker). It is backed by a durable
Postgres snapshot (``TextBox.textBox_crdt_state``) so a reconnecting/cold client
rehydrates after the process restarts or spins down. The CRDT merge engine itself is
kept behind a provider seam (see :mod:`app.collab.protocol`): update payloads are
relayed opaquely between peers today, and a server-side pycrdt/yrs document can be
dropped in later without changing the transport, auth or persistence layers.
"""
