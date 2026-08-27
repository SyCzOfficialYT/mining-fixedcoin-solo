# Block Pipeline

```text
miner submit
    ↓
header / share validation
    ↓
actual share difficulty
    ↓
compare against miner difficulty
    ↓
compare against network target
    ↓
BLOCK CANDIDATE
    ├── log event
    ├── dashboard SSE/event
    │      └── Arcane Forge animation
    │
    └── GhostBot notifier (ASYNC)
           └── Discord-compatible webhook
```

## Important distinction

`share difficulty >= pool difficulty` does not mean a block.

A block candidate requires the submitted hash to satisfy the network target.

## Event contract

`BLOCK CANDIDATE` is the authoritative internal event. Consumers must be independent:

- **Dashboard:** immediately emits its live event and starts the block-found animation.
- **GhostBot:** receives the same event and schedules asynchronous webhook delivery.
- **Ledger / chain handling:** continues independently of notification delivery.

A failed or slow webhook must therefore **never** prevent the dashboard animation. The animation is a local/live UI reaction to the block event, not a confirmation that Discord accepted a message.

## Notification rule

GhostBot is triggered from the block-candidate event. Delivery is asynchronous and deduplicated by height + hash so reconnects or repeated log processing do not spam Discord.

#block #consensus #stratum #events #dashboard #ghostbot
