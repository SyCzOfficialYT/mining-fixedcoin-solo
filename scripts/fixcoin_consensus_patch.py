#!/usr/bin/env python3
"""Apply FixedCoin-only consensus corrections to the generated Stratum adapter."""
from pathlib import Path
import ast

PATH = Path(__file__).resolve().parent.parent / "stratum" / "server.py"
text = PATH.read_text()

old_versions = (
    'ADAPT_VERSION = "fixedcoin-fch-dashboard-repair-2026-08-20-v12"',
    'ADAPT_VERSION = "fixedcoin-consensus-repair-2026-08-20-v14"',
)
new_version = 'ADAPT_VERSION = "fixedcoin-consensus-repair-2026-08-20-v16"'


def replace_function(source, name, replacement):
    tree = ast.parse(source)
    target = next(
        (n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name),
        None,
    )
    if target is None:
        raise RuntimeError(f"function {name!r} not found in pinned FreeCash base")
    lines = source.splitlines(keepends=True)
    start = sum(map(len, lines[: target.lineno - 1]))
    end = sum(map(len, lines[: target.end_lineno]))
    return source[:start] + replacement.rstrip() + "\n" + source[end:]


if new_version not in text:
    found = next((v for v in old_versions if v in text), None)
    if found is None:
        raise SystemExit("unexpected server.py adapter version; refusing to patch")
    text = text.replace(found, new_version, 1)

anchor = "    t = t.replace('/FCH-Solo/', '/FIX-Solo/')\n"
patch = '''    t = t.replace('/FCH-Solo/', '/FIX-Solo/')

    # FixedCoin does not use the FreeCash governance/dev payout.
    t = t.replace('DEV_ADDRESS = "FTqiqAyXHnK7uDTXzMap3acvqADK4ZGzts"', 'DEV_ADDRESS = None')
    dev_block = """        if self.dev_spk is None:
            self.dev_spk = address_to_scriptpubkey(DEV_ADDRESS)
            emit("INFO", f"dev/governance scriptPubKey ready for {DEV_ADDRESS}")
"""
    t = t.replace(dev_block, '        self.dev_spk = None\\n', 1)
    t = t.replace('dev_sats = get_dev_reward_sats(height)', 'dev_sats = 0', 1)
'''

if anchor not in text:
    raise SystemExit("adapter anchor missing")

# IMPORTANT: all subsequent structural edits operate on the adapted source.
# The previous version forgot this assignment and later referenced undefined `t`.
t = text.replace(anchor, patch, 1)

if 'def build_coinbase_parts(' not in t:
    raise RuntimeError('build_coinbase_parts function missing from pinned FreeCash base')

coinbase = '''def build_coinbase_parts(height, miner_value_sats, miner_spk, dev_spk=None, dev_value_sats=0, en1_size=4, en2_size=4, witness_commitment_hex=None, *args, **kwargs):
    """Build a FixedCoin coinbase without the upstream governance output."""
    tag = b"/FIX-Solo/"
    height_script = bip34_height(height)
    scriptsig_len = len(height_script) + en1_size + en2_size + len(tag)
    part1 = struct.pack("<I", 2) + b"\\x01" + b"\\x00" * 32 + struct.pack("<I", 0xFFFFFFFF)
    part1 += encode_varint(scriptsig_len) + height_script

    witness = b""
    if witness_commitment_hex:
        try:
            witness = binascii.unhexlify(witness_commitment_hex)
        except Exception:
            witness = b""

    outputs = 1 + (1 if witness else 0)
    part2 = tag + struct.pack("<I", 0xFFFFFFFF) + encode_varint(outputs)
    part2 += struct.pack("<Q", int(miner_value_sats)) + encode_varint(len(miner_spk)) + miner_spk

    if witness:
        part2 += struct.pack("<Q", 0) + encode_varint(len(witness)) + witness

    part2 += struct.pack("<I", 0)
    return binascii.hexlify(part1).decode(), binascii.hexlify(part2).decode()
'''
t = replace_function(t, 'build_coinbase_parts', coinbase)

# Preserve the template witness commitment on the generated job.
old = '"other_tx": other_tx, "created": time.time(),'
if old in t:
    t = t.replace(old, old + '\n                "witness_commitment": tmpl.get("default_witness_commitment"),', 1)

# FixedCoin has no governance/dev output.
old_job = '"dev_value": dev_sats,'
if old_job in t:
    t = t.replace(old_job, '"dev_value": 0,', 1)

# Do not manufacture a second witness marker if the assembled coinbase already
# contains one. This helper is retained for compatibility with the adapter.
witness = '''def coinbase_add_witness(tx_nowitness, enabled):
    if not enabled or len(tx_nowitness) < 8 or tx_nowitness[4:6] == b"\\x00\\x01":
        return tx_nowitness
    return tx_nowitness[:4] + b"\\x00\\x01" + tx_nowitness[4:-4] + b"\\x01\\x20" + (b"\\x00" * 32) + tx_nowitness[-4:]
'''
if 'def coinbase_add_witness' in t:
    t = replace_function(t, 'coinbase_add_witness', witness)
else:
    if '\ndef assemble_coinbase(' not in t:
        raise RuntimeError('assemble_coinbase anchor missing')
    t = t.replace('\ndef assemble_coinbase(', '\n' + witness + '\ndef assemble_coinbase(', 1)

# Candidate blocks must use the same witness-enabled coinbase the miner hashed.
t = t.replace(
    'block = header + encode_varint(tx_count) + coinbase_tx',
    'block = header + encode_varint(tx_count) + coinbase_add_witness(coinbase_tx, bool(job.get("witness_commitment")))',
    1,
)

# validateaddress is sufficient for the FixedCoin payout script; do not rely on
# getaddressinfo accepting the upstream address shape.
oldaddr = '''    info2 = rpc("getaddressinfo", [addr])
    if info2 and info2.get("scriptPubKey"):
        return binascii.unhexlify(info2["scriptPubKey"])
'''
t = t.replace(oldaddr, '', 1)

# Diagnostics: make successful GBT acquisition and miner notifications explicit.
t = t.replace(
    '        try:\n            c.push_job(clean=clean, force_refresh=False)\n        except Exception as e:\n            emit("WARN", f"push {c.worker}: {e}")',
    '        try:\n            c.push_job(clean=clean, force_refresh=False)\n            emit("INFO", f"notify worker={c.worker} job={store.current_id} height={store.last_height} clean={clean}")\n        except Exception as e:\n            emit("WARN", f"push {c.worker}: {e}")',
    1,
)

needle = '        height = tmpl["height"]\n        prevhash = tmpl["previousblockhash"]'
replacement = '        height = tmpl["height"]\n        prevhash = tmpl["previousblockhash"]\n        emit("INFO", f"GBT height={height} prev={prevhash[:16]} bits={tmpl.get(\'bits\')} txs={len(tmpl.get(\'transactions\', []))}")'
if needle in t:
    t = t.replace(needle, replacement, 1)

t = t.replace(
    'if job is not None and clean:\n                broadcast_job(clean=True)',
    'if job is not None and clean:\n                emit("INFO", f"broadcast new job={job[\\"id\\"]} height={job[\\"height\\"]}")\n                broadcast_job(clean=True)',
    1,
)

# Validate the generated adapter before persisting it. This prevents a broken
# patch from turning into a restart loop inside Docker.
ast.parse(t)
PATH.write_text(t)
print(f"patched {PATH} -> {new_version}")
