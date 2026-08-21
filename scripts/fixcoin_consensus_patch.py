#!/usr/bin/env python3
"""Apply FixedCoin-only consensus corrections to the generated Stratum adapter."""
from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

new_version = "fixedcoin-consensus-repair-2026-08-21-v27"
marker = re.search(r"^# ADAPT_VERSION=([^\n]+)$", text, re.MULTILINE)
if not marker:
    raise SystemExit("generated adapter version marker missing; refusing to patch")
version = marker.group(1)
if not version.startswith(("fixedcoin-fch-dashboard-repair-", "fixedcoin-consensus-repair-")):
    raise SystemExit(f"unexpected generated adapter version {version!r}; refusing to patch")
text = text[:marker.start()] + f"# ADAPT_VERSION={new_version}" + text[marker.end():]


def replace_function(source, name, replacement):
    tree = ast.parse(source)
    target = next(
        (n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name),
        None,
    )
    if target is None:
        raise RuntimeError(f"function {name!r} not found in generated Stratum adapter")
    lines = source.splitlines(keepends=True)
    start = sum(map(len, lines[: target.lineno - 1]))
    end = sum(map(len, lines[: target.end_lineno]))
    return source[:start] + replacement.rstrip() + "\n" + source[end:]


# FixedCoin BIP34 height encoding.
bip34 = '''def bip34_height(height):
    height = int(height)
    if height < 0:
        raise ValueError("negative coinbase height")
    if height == 0:
        return b"\\x00"
    raw = bytearray()
    n = height
    while n:
        raw.append(n & 0xFF)
        n >>= 8
    if raw[-1] & 0x80:
        raw.append(0)
    return bytes([len(raw)]) + bytes(raw)
'''
text = replace_function(text, "bip34_height", bip34)

# FixedCoin has no FreeCash governance/dev payout.
text = text.replace('DEV_ADDRESS = "FTqiqAyXHnK7uDTXzMap3acvqADK4ZGzts"', "DEV_ADDRESS = None", 1)
dev_block = '''        if self.dev_spk is None:
            self.dev_spk = address_to_scriptpubkey(DEV_ADDRESS)
            emit("INFO", f"dev/governance scriptPubKey ready for {DEV_ADDRESS}")
'''
text = text.replace(dev_block, "        self.dev_spk = None\n", 1)
text = text.replace("dev_sats = get_dev_reward_sats(height)", "dev_sats = 0", 1)

# GBT coinbasevalue is the complete miner payout.
accounting_old = '''        new_value = int(tmpl["coinbasevalue"])
        dev_sats = min(get_dev_reward_sats(height), new_value)
        miner_value = new_value - dev_sats
        if miner_value < 0 or miner_value + dev_sats != new_value:'''
accounting_new = '''        new_value = int(tmpl["coinbasevalue"])
        dev_sats = 0
        miner_value = new_value
        if miner_value + dev_sats != new_value:'''
text = text.replace(accounting_old, accounting_new, 1)
text = text.replace(
    '''        dev_sats = min(get_dev_reward_sats(height), new_value)
        miner_value = new_value - dev_sats''',
    '''        dev_sats = 0
        miner_value = new_value''',
    1,
)

coinbase = '''def build_coinbase_parts(height, miner_value_sats, miner_spk, dev_spk=None, dev_value_sats=0, en1_size=4, en2_size=4, witness_commitment_hex=None, *args, **kwargs):'''
text = replace_function(text, "build_coinbase_parts", coinbase + "\n    return build_coinbase_parts_original(height, miner_value_sats, miner_spk, dev_spk, dev_value_sats, en1_size, en2_size, witness_commitment_hex, *args, **kwargs)") if False else text

# Keep the existing v26 consensus transformations unchanged; v27 only
# advances the generated-adapter marker so startup validation has one source
# of truth with stratum/server.py.

def generate_server():
    raise RuntimeError("fixcoin_consensus_patch.py is a runtime patcher; server.py must generate server_full.py first")
