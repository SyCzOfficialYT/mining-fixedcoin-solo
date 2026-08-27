# ✦ FixedCoin Solo — Command Center

> **LiveShare • Arcane Forge • Solo Mining**

## System

| Component | Role | Source |
|---|---|---|
| FixedCoin node | Consensus / chain / RPC | `fixedcoind` |
| Stratum | Miner protocol + share validation | `stratum/` |
| LiveShare | Realtime operator UI | `frontend/` |
| Monitor | API + SSE telemetry | `monitor/` |
| Swarm Connector | Miner discovery/control | `swarm-connector/` |
| GhostBot | Block notifications | `scripts/fixcoin_ghostbot_webhook_patch.py` |

## Critical invariants

- Network difficulty is authoritative and separate from pool/share difficulty.
- Low-hash miners can use low share difficulty without weakening block validation.
- A block candidate is only created when the submitted hash reaches the network target.
- Webhook delivery must never block the Stratum response path.
- Dashboard animation is event-driven from the same block event that enters the telemetry stream.

## Current focus

- [ ] Validate GhostBot webhook with a real block candidate
- [ ] Confirm accepted-block path vs candidate path
- [ ] Keep Obsidian notes updated after architecture changes

## Navigation

- [[10 - Architecture]]
- [[20 - Stratum]]
- [[30 - Dashboard]]
- [[40 - Block Pipeline]]
- [[50 - GhostBot]]
- [[60 - Operations]]
- [[70 - Incidents]]
- [[80 - Decisions]]
- [[90 - Roadmap]]

#fixedcoin #solo #homelab #mining
