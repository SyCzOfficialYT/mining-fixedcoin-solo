#!/bin/bash
set -euo pipefail
DATADIR="${FIX_DATADIR:-/data/fixedcoin}"
RPCUSER="${FIX_RPCUSER:-fixrpc}"
RPCPASS="${FIX_RPCPASS:-change-me}"
RPCPORT="${FIX_RPCPORT:-24761}"
P2PPORT="${FIX_P2PPORT:-24768}"
DASH_PORT="${FIX_DASH_PORT:-5050}"
mkdir -p "$DATADIR" /app/data /app/logs
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
printtoconsole=1
addnode=node1.fixedcoin.org
addnode=node2.fixedcoin.org
EOF

fixedcoind -datadir="$DATADIR" -conf="$DATADIR/fixedcoin.conf" >>/app/data/node.log 2>&1 &
NODE_PID=$!
trap 'kill "$NODE_PID" 2>/dev/null || true; kill "${STRATUM_PID:-0}" 2>/dev/null || true' EXIT

for i in $(seq 1 180); do
  if fixedcoin-cli -datadir="$DATADIR" -rpcuser="$RPCUSER" -rpcpassword="$RPCPASS" getblockchaininfo >/dev/null 2>&1; then break; fi
  kill -0 "$NODE_PID" 2>/dev/null || { cat /app/data/node.log; exit 1; }
  sleep 1
done
fixedcoin-cli -datadir="$DATADIR" -rpcuser="$RPCUSER" -rpcpassword="$RPCPASS" getblockchaininfo >/dev/null

# Initialize/validate payout wallet when possible. An explicit FIX_PAYOUT_ADDRESS always wins.
python3 /app/scripts/setup_address.py || true

python3 /app/monitor/app.py >>/app/data/dashboard.log 2>&1 &
DASH_PID=$!
python3 /app/stratum/server.py >>/app/data/stratum.log 2>&1 &
STRATUM_PID=$!

echo "FixedCoin Solo online: dashboard :${DASH_PORT}, stratum :3333, RPC :${RPCPORT}"
wait "$NODE_PID"
