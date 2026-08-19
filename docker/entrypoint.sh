#!/bin/bash
set -euo pipefail
DATADIR="${FIX_DATADIR:-/data/fixedcoin}"
RPCUSER="${FIX_RPCUSER:-fixrpc}"
RPCPASS="${FIX_RPCPASS:-}"
RPCPORT="${FIX_RPCPORT:-24761}"
P2PPORT="${FIX_P2PPORT:-24768}"
DASH_PORT="${FIX_DASH_PORT:-5050}"
mkdir -p "$DATADIR" "$DATADIR/wallets" /app/data /app/logs

# Secrets are generated inside the private Docker volume and never committed
# to Git, never printed, and never required in .env.
if [[ -z "$RPCPASS" ]]; then
  if [[ -s "$DATADIR/.rpcpassword" ]]; then
    RPCPASS="$(cat "$DATADIR/.rpcpassword")"
  else
    RPCPASS="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
    umask 077
    printf '%s\n' "$RPCPASS" > "$DATADIR/.rpcpassword"
  fi
fi
export FIX_RPCPASS="$RPCPASS"

cat > "$DATADIR/fixedcoin.conf" <<EOF
server=1
daemon=0
listen=1
port=${P2PPORT}
rpcport=${RPCPORT}
rpcuser=${RPCUSER}
rpcpassword=${RPCPASS}
rpcallowip=127.0.0.1
txindex=1
walletdir=${DATADIR}/wallets
printtoconsole=1
addnode=node1.fixedcoin.org
addnode=node2.fixedcoin.org
EOF
chmod 600 "$DATADIR/fixedcoin.conf" "$DATADIR/.rpcpassword"

fixedcoind -datadir="$DATADIR" -conf="$DATADIR/fixedcoin.conf" >>/app/data/node.log 2>&1 &
NODE_PID=$!
trap 'kill "$NODE_PID" 2>/dev/null || true; kill "${STRATUM_PID:-0}" 2>/dev/null || true; kill "${DASH_PID:-0}" 2>/dev/null || true' EXIT

for i in $(seq 1 180); do
  if fixedcoin-cli -datadir="$DATADIR" -rpcuser="$RPCUSER" -rpcpassword="$RPCPASS" getblockchaininfo >/dev/null 2>&1; then break; fi
  kill -0 "$NODE_PID" 2>/dev/null || { cat /app/data/node.log; exit 1; }
  sleep 1
done
fixedcoin-cli -datadir="$DATADIR" -rpcuser="$RPCUSER" -rpcpassword="$RPCPASS" getblockchaininfo >/dev/null

# Creates the mining wallet and payout address automatically when none is configured.
python3 /app/scripts/setup_address.py

python3 /app/monitor/app.py >>/app/data/dashboard.log 2>&1 &
DASH_PID=$!
python3 /app/stratum/server.py >>/app/data/stratum.log 2>&1 &
STRATUM_PID=$!

echo "FixedCoin Solo online: dashboard :${DASH_PORT}, stratum :3333, RPC :${RPCPORT}"
wait "$NODE_PID"
