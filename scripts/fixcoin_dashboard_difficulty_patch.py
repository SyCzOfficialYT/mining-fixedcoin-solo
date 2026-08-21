#!/usr/bin/env python3
"""Make the dashboard's Network Difficulty match FixedCoin Core getdifficulty."""
from pathlib import Path
import re

PATH = Path(__file__).resolve().parent.parent / "monitor" / "app.py"
text = PATH.read_text()

# The dashboard source is intentionally kept compact. Match the RPC assignment
# semantically instead of depending on one exact whitespace/formatting layout.
rpc_pattern = re.compile(
    r'(?P<prefix>info,info_error=rpc\("getblockchaininfo"\);\s*'
    r'net,_=rpc\("getnetworkinfo"\);\s*'
    r'mininginfo,_=rpc\("getmininginfo"\);\s*)'
    r'(?P<tail>info=info or \{\};\s*net=net or \{\};\s*mininginfo=mininginfo or \{\})'
)

if 'core_diff,_=rpc("getdifficulty")' not in text:
    match = rpc_pattern.search(text)
    if not match:
        raise RuntimeError("dashboard RPC marker mismatch: could not locate status RPC block")
    replacement = f'{match.group("prefix")}core_diff,_=rpc("getdifficulty"); {match.group("tail")}'
    text = text[:match.start()] + replacement + text[match.end():]

# Core getdifficulty is authoritative for the node/network difficulty shown by
# the dashboard. Stratum round difficulty remains separate.
network_pattern = re.compile(
    r'network_diff=as_number\(stats\.get\("network_diff"\)\)\s*or\s*'
    r'as_number\(log_job\.get\("network_diff"\)\)\s*or\s*'
    r'as_number\(mininginfo\.get\("difficulty"\)\)'
)

replacement = 'network_diff=as_number(core_diff) or as_number(mininginfo.get("difficulty")) or as_number(stats.get("network_diff")) or as_number(log_job.get("network_diff"))'
if network_pattern.search(text):
    text = network_pattern.sub(replacement, text, count=1)
elif 'network_diff=as_number(core_diff)' not in text:
    raise RuntimeError("dashboard difficulty marker mismatch: could not locate network_diff assignment")

if 'core_diff,_=rpc("getdifficulty")' not in text:
    raise RuntimeError("getdifficulty RPC missing")
if 'network_diff=as_number(core_diff)' not in text:
    raise RuntimeError("Core difficulty is not authoritative")

PATH.write_text(text)
print("patched dashboard network difficulty: FixedCoin Core getdifficulty is authoritative")
