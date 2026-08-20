#!/usr/bin/env python3
"""Apply FixedCoin-only consensus corrections to the generated Stratum adapter."""
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "stratum" / "server.py"
text = PATH.read_text()

old_versions = (
    'ADAPT_VERSION = "fixedcoin-fch-dashboard-repair-2026-08-20-v12"',
    'ADAPT_VERSION = "fixedcoin-consensus-repair-2026-08-20-v14"',
)
new_version = 'ADAPT_VERSION = "fixedcoin-consensus-repair-2026-08-20-v15"'
if new_version not in text:
    found = next((v for v in old_versions if v in text), None)
    if found is None:
        raise SystemExit("unexpected server.py adapter version; refusing to patch")
    text = text.replace(found, new_version, 1)

anchor = "    t = t.replace('/FCH-Solo/', '/FIX-Solo/')\n"
patch = '''    t = t.replace('/FCH-Solo/', '/FIX-Solo/')

    # FixedCoin does NOT use the FreeCash governance/dev payout.
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
text = text.replace(anchor, patch, 1)

# Replace the upstream function structurally instead of matching its exact
# source text. The pinned FreeCash base has changed formatting/implementation
# over time; exact whole-block matching caused the container to fail with
# "coinbase adapter block missing" even though the function existed.
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
if 'def build_coinbase_parts(' not in t:
    raise RuntimeError('build_coinbase_parts function missing from pinned FreeCash base')
t = replace_function(t, 'build_coinbase_parts', coinbase)

# Carry the template's witness commitment into the job.
old = '"other_tx": other_tx, "created": time.time(),'
if old in t:
    t = t.replace(old, old + '\n                "witness_commitment": tmpl.get("default_witness_commitment"),', 1)

# The FixedCoin coinbase builder keeps the historical call signature but ignores
# governance/dev parameters. Preserve the upstream call sites unchanged.

# Store a zero governance reward on every job when the upstream field exists.
old_job = '"dev_value": dev_sats,'
if old_job in t:
    t = t.replace(old_job, '"dev_value": 0,', 1)

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

# Candidate blocks must contain the same witness-enabled coinbase that the miner
# hashed, followed by all GBT transactions.
t = t.replace(
    'block = header + encode_varint(tx_count) + coinbase_tx',
    'block = header + encode_varint(tx_count) + coinbase_add_witness(coinbase_tx, bool(job.get("witness_commitment")))',
    1,
)

# Do not depend on getaddressinfo for the fixed bech32 address when the node
# rejects that RPC shape. validateaddress already returns scriptPubKey.
oldaddr = '''    info2 = rpc("getaddressinfo", [addr])
    if info2 and info2.get("scriptPubKey"):
        return binascii.unhexlify(info2["scriptPubKey"])
'''
t = t.replace(oldaddr, '', 1)

# Emit useful job/notify diagnostics.
t = t.replace(
    '        try:\n            c.push_job(clean=clean, force_refresh=False)\n        except Exception as e:\n            emit("WARN", f"push {c.worker}: {e}")',
    '        try:\n            c.push_job(clean=clean, force_refresh=False)\n            emit("INFO", f"notify worker={c.worker} job={store.current_id} height={store.last_height} clean={clean}")\n        except Exception as e:\n            emit("WARN", f"push {c.worker}: {e}")',
    1,
)

needle = '        height = tmpl["height"]\n        prevhash = tmpl["previousblockhash"]'
replacement = '        height = tmpl["height"]\n        prevhash = tmpl["previousblockhash"]\n        emit("INFO", f"GBT height={height} prev={prevhash[:16]} bits={tmpl.get(\'bits\')} txs={len(tmpl.get(\'transactions\', []))}")'
if needle in t:
    t = t.replace(needle, replacement, 1)

# Ensure new-height jobs are explicitly visible in logs.
t = t.replace(
    'if job is not None and clean:\n                broadcast_job(clean=True)',
    'if job is not None and clean:\n                emit("INFO", f"broadcast new job={job[\\"id\\"]} height={job[\\"height\\"]}")\n                broadcast_job(clean=True)',
    1,
)

PATH.write_text(text)
print(f"patched {PATH} -> {new_version}")
