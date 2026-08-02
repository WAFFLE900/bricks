# Architect Journal

## Iteration 1
- design: 未收斂：high 缺口 2-0-0（REST↔CRDT 雙 writer）仍在，A2/F1/F3 未著落，且 A4/F5 帳面 placed 實受反噬 (converged=false)
- implemented: Landed the realtime-collaboration backbone for record text boxes across apps/api and apps/web: durable CRDT-state schema, an authenticated per-textBox WebSocket room with relay + debounced Postgres materialization + re-hooked mentions, and a frontend collab client seam with live editing/presence and read-only gating. The CRDT merge engine (pycrdt server / yjs client) is deliberately isolated behind a protocol seam for a later dependency-adding increment, because both lockfiles are consumed frozen and no new deps could be added safely this pass. No new dependencies added; existing test/build locks stay valid. Did not run build/test (left to the next step); verified via py_compile and an app-import sanity check only.
- build ok=true; test ok=true (0 failed); acceptance met=false (score 0.4)
- carry-forward failures: 6

## Iteration 2
- design: 設計未收斂：A2（記錄範圍）與 F3（離線重連合併）仍 at-risk 未著落；F1/F4 名義 placed 但 CRDT 合併引擎尚未進相依樹（現為 LWW 全文覆寫）。無 high 缺口，僅 1 條 med（mention 歸屬 2-0-1），惟「全部 placed」門檻未達。 (converged=false)
- implemented: Wired a real CRDT engine (pycrdt server-side, yjs client-side) implementing the Yjs two-step sync protocol, replacing the last-writer-wins full-text overwrite. Concurrent edits now merge via apply_update + raw-update relay (F1/F4); offline clients reconcile on reconnect via state-vector diffs instead of clobbering (F3); the editor textarea is uncontrolled with caret-preserving reconciliation and character-level diff ops (Criterion 5). Added docker-compose healthchecks for api and web, and a new WebSocket test suite covering convergence, offline-reconnect merge, and viewer read-only (A1). Viewer read-only (A1) and ORM materialization with mention re-hook (A4/F5) preserved; record-scoping (A2) remains deferred per the ledger.
- build ok=true; test ok=true (0 failed); acceptance met=true (score 0.85)
- carry-forward failures: 2
