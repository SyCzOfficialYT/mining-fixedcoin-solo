# Architecture

```text
NerdQAxe / NerdMiner / NMMiner
            │ Stratum
            ▼
     ┌───────────────┐
     │ FixedCoin     │
     │ Stratum       │
     └──────┬────────┘
            │ RPC / GBT
            ▼
     ┌───────────────┐
     │ fixedcoind    │
     │ consensus     │
     └──────┬────────┘
            │
            ├── log/SSE ──► LiveShare / Arcane Forge
            │
            └── block event ──► GhostBot webhook
```

## Design principles

1. **Consensus stays authoritative.** UI, notifications and analytics never decide whether a block is valid.
2. **Stratum stays fast.** Non-critical integrations are asynchronous.
3. **Events are the integration contract.** A block candidate becomes a first-class event consumed by dashboard and notification layers.
4. **Obsidian documents intent.** Code tells us *what*; this vault records *why*.

## Important paths

- `stratum/server.py` — source adapter/generator
- `monitor/app.py` — dashboard API/SSE
- `frontend/` — LiveShare UI
- `scripts/` — deterministic build-time patches
- `docker-compose.yml` — runtime wiring
