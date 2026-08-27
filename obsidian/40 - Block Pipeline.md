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
    ├── dashboard SSE event
    ├── Arcane Forge animation
    └── GhostBot webhook
```

## Important distinction

`share difficulty >= pool difficulty` does not mean a block.

A block candidate requires the submitted hash to satisfy the network target.

## Notification rule

GhostBot is triggered from the block-candidate event. Delivery is asynchronous and deduplicated by height + hash so reconnects or repeated log processing do not spam Discord.

#block #consensus #stratum #events
