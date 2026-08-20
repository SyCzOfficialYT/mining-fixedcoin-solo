#!/usr/bin/env python3
"""Apply FixedCoin-only consensus corrections to the generated Stratum adapter."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parent.parent
FULL = ROOT / "stratum" / "server_full.py"

# IMPORTANT: server.py is the generator. The actual pinned/adapted FreeCash
# implementation lives in server_full.py and THAT is what must be patched.
PATH = FULL
text = PATH.read_text()

new_version = 'fixedcoin-consensus-repair-2026-08-20-v17'
old_versions = (
    'fixedcoin-consensus-repair-2026-08-20-v16',
    'fixedcoin-consensus-repair-2026-08-20-v14',
    'fixedcoin-fch-dashboard-repair-2026-08-20-v12',
)


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

# The generated file carries its own generator marker on line 1. Replace it
# after generation so the entrypoint can tell exactly which patched adapter is
# installed. Do not touch the generator's ADAPT_VERSION in server.py here.
for version in old_versions:
    text = text.replace(f"# ADAPT_VERSION={version}", f"# ADAPT_VERSION={new_version}", 1)

if f"# ADAPT_VERSION={new_version}" not in text:
    raise SystemExit("unexpected generated adapter version; refusing to patch")

if 'def build_coinbase_parts(' not in text:
    raise RuntimeError('build_coinbase_parts function missing from generated Stratum adapter')

# FixedCoin does not use the FreeCash governance/dev payout.
text = text.replace('DEV_ADDRESS = "FTqiqAyXHnK7uDTXzMap3acvqADK4ZGzts"', 'DEV_ADDRESS = None', 1)

dev_block = """        if self.dev_spk is None:
            self.dev_spk = address_to_scriptpubkey(DEV_ADDRESS)
            emit("INFO", f"dev/governance scriptPubKey ready for {DEV_ADDRESS}")
"""
text = text.replace(dev_block, '        self.dev_spk = None\n', 1)
text = text.replace('dev_sats = get_dev_reward_sats(height)', 'dev_sats = 0', 1)

coinbase = '''def build_coinbase_parts(height, miner_value_sats, miner_spk, dev_spk=None, dev_value_sats=0, en1_size=4, en2_size=4, witness_commitment_hex=None, *args, **kwargs):
    """Build a FixedCoin coinbase with miner output and optional witness commitment only."""
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
text = replace_function(text, 'build_coinbase_parts', coinbase)

# Preserve the template witness commitment on the generated job.
old = '"other_tx": other_tx, "created": time.time(),'
if old in text:
    text = text.replace(old, old + '\n                "witness_commitment": tmpl.get("default_witness_commitment"),', 1)

# FixedCoin has no governance/dev output.
text = text.replace('"dev_value": dev_sats,', '"dev_value": 0,', 1)

# Do not manufacture a second witness marker if the assembled coinbase already
# contains one. Keep this helper compatible with the adapter's existing call.
witness = '''def coinbase_add_witness(tx_nowitness, enabled):
    if not enabled or len(tx_nowitness) < 8 or tx_nowitness[4:6] == b"\\x00\\x01":
        return tx_nowitness
    return tx_nowitness[:4] + b"\\x00\\x01" + tx_nowitness[4:-4] + b"\\x01\\x20" + (b"\\x00" * 32) + tx_nowitness[-4:]
'''
if 'def coinbase_add_witness' in text:
    text = replace_function(text, 'coinbase_add_witness', witness)
else:
    if '\ndef assemble_coinbase(' not in text:
        raise RuntimeError('assemble_coinbase anchor missing')
    text = text.replace('\ndef assemble_coinbase(', '\n' + witness + '\ndef assemble_coinbase(', 1)

# Candidate blocks must use the same witness-enabled coinbase the miner hashed.
text = text.replace(
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
text = text.replace(oldaddr, '', 1)

# Validate the generated adapter before persisting it. This prevents a broken
# patch from turning into a restart loop inside Docker.
ast.parse(text)
PATH.write_text(text)
print(f"patched {PATH} -> {new_version}")
