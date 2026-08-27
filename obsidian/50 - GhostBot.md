# GhostBot

## Purpose

Send one rich notification to the configured Discord-compatible incoming webhook whenever the Stratum detects a network-difficulty block candidate.

Discord incoming webhooks accept JSON payloads containing content and embeds, so the integration does not require a persistent bot connection. urlDiscord Webhook APIhttps://docs.discord.com/developers/resources/webhook

## Configuration

```env
GHOSTBOT_WEBHOOK_URL=
GHOSTBOT_WEBHOOK_USERNAME=GhostBot
GHOSTBOT_WEBHOOK_TIMEOUT=5
GHOSTBOT_EMBED_COLOR=5635925
GHOSTBOT_DASHBOARD_URL=
```

The real webhook URL belongs in the local `.env`, never in Git.

## Message

The default message contains:

- FixedCoin block-found title
- block height
- block hash
- worker/miner when present
- dashboard link when configured

## Reliability

- asynchronous delivery
- five-second default HTTP timeout
- notification failure never fails the Stratum share path
- duplicate `(height, hash)` events are suppressed

#ghostbot #discord #webhook #notifications
