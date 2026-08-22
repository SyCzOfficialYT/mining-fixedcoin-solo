#!/bin/bash
set -euo pipefail
DATADIR="${FIX_DATADIR:-/data/fixedcoin}"
RPCUSER="${FIX_RPCUSER:-fixrpc}"
RPCPASS="${FIX_RPCPASS:-}"
RPCPORT="${FIX_RPCPORT:-24761}"
P2PPORT="${P2PPORT:-24768}"
DASH_PORT="${FIX_DASH_PORT:-5050}"
mkdir -p "$DATADIR" "$DATADIR/wallets" /app/data /app/logs

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
walletdir=${DATADIR}/wallets
printtoconsole=1
addnode=node1.fixedcoin.org
addnode=node2.fixedcoin.org
EOF
chmod 600 "$DATADIR/fixedcoin.conf" "$DATADIR/.rpcpassword"

fixedcoind -datadir="$DATADIR" -conf="$DATADIR/fixedcoin.conf" >>/app/data/node.log 2>&1 &
NODE_PID=$!
STRATUM_PID=0
DASH_PID=0
LEDGER_PID=0
LOG_PID=0
trap 'kill "$NODE_PID" 2>/dev/null || true; kill "$STRATUM_PID" 2>/dev/null || true; kill "$DASH_PID" 2>/dev/null || true; kill "$LEDGER_PID" 2>/dev/null || true; kill "$LOG_PID" 2>/dev/null || true' EXIT

for i in $(seq 1 180); do
  if fixedcoin-cli -datadir="$DATADIR" -rpcuser="$RPCUSER" -rpcpassword="$RPCPASS" getblockchaininfo >/dev/null 2>&1; then break; fi
  kill -0 "$NODE_PID" 2>/dev/null || { cat /app/data/node.log; exit 1; }
  sleep 1
done
fixedcoin-cli -datadir="$DATADIR" -rpcuser="$RPCUSER" -rpcpassword="$RPCPASS" getblockchaininfo >/dev/null

python3 /app/scripts/setup_address.py
ln -sfn "$DATADIR/solo-blocks.json" /app/data/blocks.json

python3 /app/monitor/app.py >>/app/data/dashboard.log 2>&1 &
DASH_PID=$!

# Always generate the adapter first, then apply all FixedCoin-only patches.
# The consensus patch owns the final adapter version marker.
STRATUM_BUILD_ONLY=1 python3 /app/stratum/server.py
python3 /app/scripts/fixcoin_consensus_patch.py
python3 /app/scripts/fixcoin_network_difficulty_patch.py
python3 /app/scripts/fixcoin_stratum_difficulty_patch.py
python3 /app/scripts/fixcoin_dashboard_difficulty_patch.py

# Keep the startup guard synchronized with the version produced by the
# consensus patch itself. Do not compare against the unpatched generator
# version: the consensus patch intentionally bumps that marker.
EXPECTED_ADAPT_VERSION="$(sed -n 's/^new_version = [\"'"'"']\([^\"'"'"']*\)[\"'"'"']$/\1/p' /app/scripts/fixcoin_consensus_patch.py | head -n 1)"
if [[ -z "$EXPECTED_ADAPT_VERSION" ]]; then
  echo "FATAL: could not determine expected patched Stratum adapter version" >&2
  exit 1
fi
ACTUAL_ADAPT_VERSION="$(sed -n '1s/^# ADAPT_VERSION=//p' /app/stratum/server_full.py)"
if [[ "$ACTUAL_ADAPT_VERSION" != "$EXPECTED_ADAPT_VERSION" ]]; then
  echo "FATAL: generated Stratum adapter version mismatch: expected=$EXPECTED_ADAPT_VERSION actual=$ACTUAL_ADAPT_VERSION" >&2
  exit 1
fi

# Hard runtime invariants: the container must never start Stratum unless the
# FixedCoin powLimit helper and canonical network-difficulty scale are actually
# present in the adapter that will be executed. This catches stale/partial
# images instead of silently running the unpatched v31/v32 adapter.
python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, "/app")
import stratum.server_full as s

source = Path("/app/stratum/server_full.py").read_text()
expected_pow_limit = int("00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16)
canonical_diff1 = 0x00000000FFFF0000000000000000000000000000000000000000000000000000

assert getattr(s, "FIXCOIN_POW_LIMIT", None) == expected_pow_limit, "FATAL: FixedCoin powLimit missing or wrong"
assert callable(getattr(s, "fixedcoin_target_to_difficulty", None)), "FATAL: FixedCoin difficulty helper missing"
assert s.fixedcoin_target_to_difficulty(s.FIXCOIN_POW_LIMIT) == 1.0, "FATAL: FixedCoin powLimit difficulty regression"
assert s.difficulty_to_target(1) == canonical_diff1, "FATAL: Stratum diff-1 target is not canonical Bitcoin/Core scale"
assert "net_diff = target_to_difficulty(bits_to_target(nbits))" in source, "FATAL: canonical network difficulty formula missing"
assert "net_diff = fixedcoin_target_to_difficulty(bits_to_target(nbits))" not in source, "FATAL: powLimit-based network difficulty is still active"
print("Verified FixedCoin Stratum runtime invariants: powLimit + canonical network difficulty")
PY

python3 -m py_compile /app/stratum/server_full.py

python3 /app/stratum/server.py >>/app/data/stratum.log 2>&1 &
STRATUM_PID=$!

# The persistent ledger must start only after the node RPC and Stratum process
# are both initialized. It uses authenticated RPC directly and scans the chain
# as the authoritative source, so container recreation cannot erase found blocks.
python3 /app/scripts/block_ledger.py >>/app/data/block-ledger.log 2>&1 &
LEDGER_PID=$!
sleep 1
if ! kill -0 "$LEDGER_PID" 2>/dev/null; then
  echo "FATAL: persistent block ledger exited during startup" >&2
  cat /app/data/block-ledger.log >&2 || true
  exit 1
fi

echo "FixedCoin Solo online: dashboard :${DASH_PORT}, stratum :3333, RPC :${RPCPORT}"

tail -n 0 -F /app/data/stratum.log &
LOG_PID=$!

wait "$NODE_PID"
