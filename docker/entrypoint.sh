#!/bin/bash
set -euo pipefail
DATADIR="${FIX_DATADIR:-/data/fixedcoin}"
RPCUSER="${FIX_RPCUSER:-fixrpc}"
RPCPASS="${FIX_RPCPASS:-}"
RPCPORT="${FIX_RPCPORT:-24761}"
P2PPORT="${FIX_P2PPORT:-24768}"
DASH_PORT="${FIX_DASH_PORT:-5050}"
mkdir -p "$DATADIR" "$DATADIR/wallets" /app/data /app/logs

if [[ -z "$RPCPASS" ]]; then
  if [[ -s "$DATADIR/.rpcpassword" ]]; then RPCPASS="$(cat "$DATADIR/.rpcpassword")"; else
    RPCPASS="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"; umask 077; printf '%s\n' "$RPCPASS" > "$DATADIR/.rpcpassword"
  fi
fi
export FIX_RPCPASS="$RPCPASS"

cat > "$DATADIR/fixedcoin.conf" <<EOF
daemon=0
server=1
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
NODE_PID=$!; STRATUM_PID=0; DASH_PID=0; LEDGER_PID=0; LOG_PID=0
trap 'kill "$NODE_PID" 2>/dev/null || true; kill "$STRATUM_PID" 2>/dev/null || true; kill "$DASH_PID" 2>/dev/null || true; kill "$LEDGER_PID" 2>/dev/null || true; kill "$LOG_PID" 2>/dev/null || true' EXIT

for i in $(seq 1 180); do
  if fixedcoin-cli -datadir="$DATADIR" -rpcuser="$RPCUSER" -rpcpassword="$RPCPASS" getblockchaininfo >/dev/null 2>&1; then break; fi
  kill -0 "$NODE_PID" 2>/dev/null || { cat /app/data/node.log; exit 1; }; sleep 1
done
fixedcoin-cli -datadir="$DATADIR" -rpcuser="$RPCUSER" -rpcpassword="$RPCPASS" getblockchaininfo >/dev/null

python3 /app/scripts/setup_address.py
ln -sfn "$DATADIR/solo-blocks.json" /app/data/blocks.json

# All source mutations/patches are performed at IMAGE BUILD TIME in the
# Dockerfile. Never rewrite the application on every container restart:
# startup-time patching made the container non-deterministic and could fail on
# an already-patched source tree, leaving the node unhealthy even though the
# image itself had passed every build-time invariant.
python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, "/app")
import stratum.server_full as s
source = Path("/app/stratum/server_full.py").read_text()
expected_pow_limit = int("00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16)
canonical_diff1 = 0x00000000FFFF0000000000000000000000000000000000000000000000000000
low_reject = 'self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})'
assert getattr(s, "FIXCOIN_POW_LIMIT", None) == expected_pow_limit, "FATAL: FixedCoin powLimit missing or wrong"
assert callable(getattr(s, "fixedcoin_target_to_difficulty", None)), "FATAL: FixedCoin difficulty helper missing"
assert s.fixedcoin_target_to_difficulty(s.FIXCOIN_POW_LIMIT) == 1.0, "FATAL: FixedCoin powLimit difficulty regression"
assert s.difficulty_to_target(1) == canonical_diff1, "FATAL: Stratum diff-1 target is not canonical Bitcoin/Core scale"
assert "net_diff = target_to_difficulty(bits_to_target(nbits))" in source, "FATAL: canonical network difficulty formula missing"
assert "net_diff = fixedcoin_target_to_difficulty(bits_to_target(nbits))" not in source, "FATAL: powLimit-based network difficulty is still active"
assert source.count(low_reject) == 1, "FATAL: strict low-difficulty rejection is missing or duplicated"
assert "ACCEPT low-difficulty" not in source, "FATAL: low-difficulty acceptance bypass is still present"
# The low-hash patch was deliberately renamed from the historical NMMINER
# marker to the shared LOW-HASH marker because NerdMiner and NerdQAxe++ use
# the same fixed low-hash authority. Keep the runtime invariant aligned with
# the implementation instead of checking a stale legacy log string.
assert "LOW-HASH DIFF" in source, "FATAL: low-hash miner compatibility patch missing"
assert "low_hash_miner = miner_family in {\"nmminer\", \"nerdminer\", \"nerdqaxe\"}" in source, "FATAL: low-hash miner family detection missing"
assert "MINER DETECT family=" in source, "FATAL: miner detection patch missing"
print("Verified FixedCoin runtime invariants: consensus + canonical difficulty + strict shares + miner compatibility")
PY

python3 -m py_compile /app/stratum/server_full.py /app/monitor/app.py
python3 /app/scripts/test_stratum_authorization.py

python3 /app/monitor/app.py >>/app/data/dashboard.log 2>&1 &
DASH_PID=$!
for i in $(seq 1 30); do
  if ! kill -0 "$DASH_PID" 2>/dev/null; then echo "FATAL: dashboard exited during startup" >&2; cat /app/data/dashboard.log >&2 || true; exit 1; fi
  if curl -fsS "http://127.0.0.1:${DASH_PORT}/healthz" >/dev/null 2>&1; then break; fi
  sleep 1
done
if ! curl -fsS "http://127.0.0.1:${DASH_PORT}/healthz" >/dev/null 2>&1; then echo "FATAL: dashboard liveness check failed on :${DASH_PORT}" >&2; cat /app/data/dashboard.log >&2 || true; exit 1; fi

python3 /app/stratum/server_full.py >>/app/data/stratum.log 2>&1 &
STRATUM_PID=$!; sleep 1
if ! kill -0 "$STRATUM_PID" 2>/dev/null; then echo "FATAL: Stratum exited during startup" >&2; tail -100 /app/data/stratum.log >&2 || true; exit 1; fi

python3 /app/scripts/block_ledger.py >>/app/data/block-ledger.log 2>&1 &
LEDGER_PID=$!; sleep 1
if ! kill -0 "$LEDGER_PID" 2>/dev/null; then echo "FATAL: persistent block ledger exited during startup" >&2; cat /app/data/block-ledger.log >&2 || true; exit 1; fi

echo "FixedCoin Solo online: dashboard :${DASH_PORT}, stratum :3333, RPC :${RPCPORT}"
tail -n 0 -F /app/data/stratum.log &
LOG_PID=$!
wait "$NODE_PID"
