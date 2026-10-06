# BCH Mining Theory

A modern, self-hosted Bitcoin Cash mining probability dashboard inspired by the information density of Blitzpool's Mining Theory page.

## Features

- Live BCH difficulty, block height and network hashrate from a BCHN JSON-RPC node
- NerdQAxe++ hashrate input (defaults to 4.80 TH/s)
- Poisson probability for 1 hour / 24 hours / 7 days / 30 days
- Expected block time, blocks/day and BCH/day
- Network-share visualization
- BCH chain-state display
- Server-side RPC credentials; nothing sensitive is exposed to the browser
- Auto-refresh every 30 seconds
- Next.js 16 + React 19 + TypeScript + Tailwind CSS 4 + Motion

## Important calculation note

The dashboard uses the standard difficulty-to-work conversion of `difficulty × 2^32` hashes and the Poisson model for `P(X ≥ 1) = 1 − e^-λ`.

The expected BCH/day number uses the subsidy configured in `NEXT_PUBLIC_BCH_BLOCK_REWARD` and intentionally excludes transaction fees.

## Run locally

```bash
npm install
cp .env.example .env.local
npm run dev
```

The dashboard expects a BCHN node reachable through the RPC endpoint in `.env.local`.

### Environment

```env
BCH_RPC_URL=http://127.0.0.1:8332
BCH_RPC_USER=change-me
BCH_RPC_PASSWORD=change-me
NEXT_PUBLIC_MINER_HASHRATE=4800000000000
NEXT_PUBLIC_BCH_BLOCK_REWARD=3.125
```

The `BCH_RPC_*` values stay server-side. Do not rename them to `NEXT_PUBLIC_*`.

## Routes

- `/` — dashboard
- `/mining-theory` — dashboard alias
- `/api/bch/network` — live BCH node data

## Architecture

```text
Browser
  │
  ├── /api/bch/network
  │          │
  │          ▼
  │       BCHN RPC
  │
  └── Mining Theory Engine
             ├── expected block time
             ├── Poisson probability
             ├── expected blocks/day
             └── expected BCH/day
```

## Sources / inspiration

The BCH pool/dashboard ecosystem that motivated this project includes BCHPool and CKPool-derived BCH implementations. This repository is an independent frontend + calculation layer; it is not affiliated with Blitzpool or BCHPool.
