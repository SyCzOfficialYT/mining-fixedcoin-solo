# FixedCoin Solo Mining Node

Reproducible Docker deployment for a **FixedCoin solo-mining node + Stratum server + live dashboard**.

This repository is the clean deployment/rebuild target for the known-good FixedCoin Solo implementation. The build pins the known-good upstream implementation instead of relying on a floating branch.

## Components

- FixedCoin Core 29.1.3
- FixedCoin Solo Stratum on `3333`
- Dashboard on `5050`
- FixedCoin P2P/RPC: `24768` / `24761`
- Fixed share difficulty with the validated FixedCoin Stratum flow
- SegWit/BIP145 `getblocktemplate` negotiation
- Immediate block-found visibility before wallet indexing catches up
- Coinbase maturity tracking at 100 blocks
- Persistent `/data` volume

## Start

```bash
git clone https://github.com/SyCzOfficialYT/mining-fixedcoin-solo.git
cd mining-fixedcoin-solo
cp .env.example .env
# Set FIX_PAYOUT_ADDRESS in .env
docker compose build --no-cache
docker compose up -d
```

Dashboard:

```text
http://HOST:5050
```

Stratum:

```text
HOST:3333
```

## ASIC configuration

Use the Stratum endpoint exposed by the host and a worker name such as:

```text
stratum+tcp://HOST:3333
worker: nerdqaxe++
password: x
```

The pool uses the validated fixed-difficulty path. A share is not treated as a block merely because it was accepted; a block is only recorded after the submitted header satisfies the network target and the resulting chain state is verified.

## Important

The payout address is intentionally supplied through `.env` and is not committed as a secret/config default.
