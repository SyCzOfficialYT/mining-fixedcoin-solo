# GhostBot

## Purpose

Send one rich block-found notification through the configured Discord-compatible incoming webhook whenever Stratum detects a network-difficulty block candidate.

The notification path is deliberately **non-blocking** and is treated as a side effect of the block event. It must never become a dependency of share acceptance, block processing, or the dashboard.

## Architecture

```text
FixedCoin Stratum
      │
      │ BLOCK CANDIDATE
      ├───────────────► Dashboard event / animation
      │
      └───────────────► GhostBot notifier (async)
                              │
                              ▼
                    Discord-compatible webhook
```

The notifier does not require a persistent Discord bot connection. It sends an HTTP JSON webhook payload and identifies the notification as `NerdQAxe++` by default so the alert can visually match the miner's normal alert identity.

## Configuration

```env
GHOSTBOT_WEBHOOK_URL=
GHOSTBOT_WEBHOOK_USERNAME=NerdQAxe++
GHOSTBOT_WEBHOOK_AVATAR_URL=
GHOSTBOT_WEBHOOK_TIMEOUT=5
GHOSTBOT_EMBED_COLOR=5635925
GHOSTBOT_DASHBOARD_URL=
```

The real webhook URL belongs in the local `.env`, never in Git.

## Message

The default message contains:

- `BLOCK FOUND!` notification
- FixedCoin / NerdQAxe++ block-found title
- block height
- block hash
- worker/miner when present
- dashboard link when configured
- AxeOS-style footer identity

## Reliability invariants

1. **Dashboard animation is independent of Discord.** The block-found dashboard event/animation is emitted directly from the block-candidate path and must not wait for, inspect, or depend on webhook delivery.
2. **Webhook delivery is asynchronous.** HTTP delivery runs in a daemon thread so network latency cannot stall Stratum processing.
3. **Webhook failure is non-fatal.** DNS, timeout, HTTP errors, or Discord downtime may be logged, but must never fail the share/block path or suppress the dashboard animation.
4. **Duplicate events are suppressed.** Notifications are deduplicated by `(height, hash)`.
5. **No Discord credentials are stored in the repository.** The webhook URL remains local configuration only.

#ghostbot #discord #webhook #notifications #reliability
