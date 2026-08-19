# FixedCoin Solo

Production-oriented FixedCoin solo-mining stack for an ASIC such as the NerdQaxe++.

## Stack

- FixedCoin Core 29.1.3
- FixedCoin-derived Stratum server
- fixed share difficulty
- SegWit/BIP145 `getblocktemplate` negotiation
- automatic payout-wallet initialization when no payout address is supplied
- rolling 5m/1h share-based hashrate telemetry
- live network competition
- difficulty history graph
- current job / network target information
- block lifecycle: found → immature → spendable
- responsive dark dashboard inspired by the BCH Jarvis desktop layout
- Docker Compose + GitHub Actions build validation

## Start

```bash
git clone https://github.com/SyCzOfficialYT/mining-fixedcoin-solo.git
cd mining-fixedcoin-solo
cp .env.example .env
nano .env
docker compose build --no-cache
docker compose up -d
```

Dashboard: `http://SERVER-IP:5050`

Stratum: `stratum+tcp://SERVER-IP:3333`

## ASIC

Configure the ASIC against port `3333`. Use your FixedCoin payout address as the Stratum username and any worker suffix, for example:

```text
stratum+tcp://SERVER-IP:3333
user: fix1...worker
password: x
```

## Maturity

`COINBASE_MATURITY=100` is the default. A found block is tracked as immature until its maturity height is reached; the dashboard shows the remaining blocks and then marks it spendable.

## Security

The default Compose file does **not** publish RPC `24761`. Only Stratum `3333`, dashboard `5050`, and P2P `24768` are exposed.

Use a long random `FIX_RPCPASS` in `.env` and do not commit `.env`.

## Telemetry correctness

The dashboard does not fake an ASIC hashrate. Its rolling estimate is calculated from accepted share work over the actual time window. Network competition uses the node's reported `networkhashps` when available. The best-share progress bar compares the best accepted share against the current network difficulty/target.
