# Decisions

## D-001 — Network difficulty stays independent

**Decision:** Miner-facing difficulty and network difficulty are separate values.

**Reason:** Low-hash devices need frequent shares without being granted an easier block target.

## D-002 — Webhooks are asynchronous

**Decision:** GhostBot delivery runs in a daemon thread.

**Reason:** A remote Discord endpoint must never delay `mining.submit` acknowledgement or share validation.

## D-003 — Obsidian is the project memory

**Decision:** Architecture, rationale, incidents, operational procedures and roadmap live in the Obsidian vault under `obsidian/`.

**Reason:** Code alone does not preserve design intent and debugging history.

## D-004 — Build-time patches remain deterministic

**Decision:** Generated upstream Stratum code is modified by repository-owned patch scripts during Docker build.

**Reason:** `server_full.py` is generated and should not become an untracked source of truth.

#decisions #architecture #adr
