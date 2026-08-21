#!/usr/bin/env python3
"""Make the dashboard's Network Difficulty match FixedCoin Core getdifficulty."""
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "monitor" / "app.py"
text = PATH.read_text()

old = 'info,info_error=rpc("getblockchaininfo"); net,_=rpc("getnetworkinfo"); mininginfo,_=rpc("getmininginfo"); info=info or {}; net=net or {}; mininginfo=mininginfo or {}'
new = 'info,info_error=rpc("getblockchaininfo"); net,_=rpc("getnetworkinfo"); mininginfo,_=rpc("getmininginfo"); core_diff,_=rpc("getdifficulty"); info=info or {}; net=net or {}; mininginfo=mininginfo or {}'
if text.count(old) != 1:
    raise RuntimeError(f"dashboard RPC marker mismatch: expected 1, found {text.count(old)}")
text = text.replace(old, new, 1)

old = 'network_diff=as_number(stats.get("network_diff")) or as_number(log_job.get("network_diff")) or as_number(mininginfo.get("difficulty"))'
new = 'network_diff=as_number(core_diff) or as_number(mininginfo.get("difficulty")) or as_number(stats.get("network_diff")) or as_number(log_job.get("network_diff"))'
if text.count(old) != 1:
    raise RuntimeError(f"dashboard difficulty marker mismatch: expected 1, found {text.count(old)}")
text = text.replace(old, new, 1)

# The round/job difficulty remains the Stratum GBT difficulty. Only the
# dashboard's node/network difficulty is switched to Core's current tip value.
if 'core_diff,_=rpc("getdifficulty")' not in text:
    raise RuntimeError("getdifficulty RPC missing")
if 'network_diff=as_number(core_diff)' not in text:
    raise RuntimeError("Core difficulty is not authoritative")

PATH.write_text(text)
print("patched dashboard network difficulty: FixedCoin Core getdifficulty is authoritative")
