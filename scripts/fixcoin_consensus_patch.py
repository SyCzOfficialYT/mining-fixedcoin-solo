#!/usr/bin/env python3
"""Apply the FixedCoin-only consensus corrections to the generated Stratum adapter.

The Stratum adapter is intentionally generated from a pinned upstream FreeCash file.
This patch keeps that architecture but removes the FreeCash-specific governance
output/reward from the generated source. FixedCoin's observed chain templates use
the GBT coinbase value for the miner payout; a SegWit witness commitment, when
present, is the only additional coinbase output.
"""
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "stratum" / "server.py"
text = PATH.read_text()

old_version = 'ADAPT_VERSION = "fixedcoin-fch-dashboard-repair-2026-08-20-v12"'
new_version = 'ADAPT_VERSION = "fixedcoin-consensus-repair-2026-08-20-v13"'
if old_version not in text:
    if new_version in text:
        raise SystemExit(0)
    raise SystemExit("unexpected server.py adapter version; refusing to patch")
text = text.replace(old_version, new_version, 1)

anchor = "    t = t.replace('/FCH-Solo/', '/FIX-Solo/')\n"
patch = r'''    t = t.replace('/FCH-Solo/', '/FIX-Solo/')

    # FixedCoin does NOT use the FreeCash governance/dev payout. Its GBT
    # coinbasevalue is the complete miner reward (subsidy + fees). Do not add
    # the upstream 25-FCH governance output or the old FreeCash address.
    t = t.replace('DEV_ADDRESS = "FTqiqAyXHnK7uDTXzMap3acvqADK4ZGzts"', 'DEV_ADDRESS = None')
    dev_block = '''        if self.dev_spk is None:
            self.dev_spk = address_to_scriptpubkey(DEV_ADDRESS)
            emit("INFO", f"dev/governance scriptPubKey ready for {DEV_ADDRESS}")
'''
    t = t.replace(dev_block, '        self.dev_spk = None\n', 1)
    t = t.replace('dev_sats = get_dev_reward_sats(height)', 'dev_sats = 0', 1)
'''
if anchor not in text:
    raise SystemExit("adapter anchor missing")
text = text.replace(anchor, patch, 1)

old_coinbase = '''def build_coinbase_parts(height, miner_value_sats, miner_spk, dev_spk=None, dev_value_sats=0, en1_size=4, en2_size=4, witness_commitment_hex=None, *args, **kwargs):
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

    outputs = 1 + (1 if dev_spk and int(dev_value_sats or 0) > 0 else 0) + (1 if witness else 0)
    part2 = tag + struct.pack("<I", 0xFFFFFFFF) + encode_varint(outputs)
    part2 += struct.pack("<Q", int(miner_value_sats)) + encode_varint(len(miner_spk)) + miner_spk

    if dev_spk and int(dev_value_sats or 0) > 0:
        part2 += struct.pack("<Q", int(dev_value_sats)) + encode_varint(len(dev_spk)) + dev_spk

    if witness:
        part2 += struct.pack("<Q", 0) + encode_varint(len(witness)) + witness

    part2 += struct.pack("<I", 0)
    return binascii.hexlify(part1).decode(), binascii.hexlify(part2).decode()
'''
new_coinbase = '''def build_coinbase_parts(height, miner_value_sats, miner_spk, dev_spk=None, dev_value_sats=0, en1_size=4, en2_size=4, witness_commitment_hex=None, *args, **kwargs):
    """Build a FixedCoin coinbase: BIP34 height + miner payout + optional witness commitment.

    The upstream FreeCash governance output is deliberately ignored. The miner
    payout is exactly the node-provided coinbasevalue; adding another reward
    would create an invalid FixedCoin coinbase.
    """
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
if old_coinbase not in text:
    raise SystemExit("coinbase adapter block missing")
text = text.replace(old_coinbase, new_coinbase, 1)

# Make the generated source self-check the exact BIP34 prefix before a block is
# ever handed to the node. This turns a silent consensus mismatch into a precise
# Stratum error and records the actual script bytes in the log.
validation = r'''    # Consensus guard: FixedCoin BIP34 requires the first coinbase scriptSig
    # push to encode exactly the submitted job height. Never submit a candidate
    # with a stale/malformed height field.
    expected_height_script = bip34_height(job["height"])
    if not coinbase_tx.startswith(b"\\x02\\x00\\x00\\x00"):
        emit("ERROR", f"COINBASE consensus guard: bad version height={job['height']}")
        self.send({"id": mid, "result": False, "error": [23, "bad coinbase", None]})
        self.shares_bad += 1; _bump_worker(self.worker, False); _save_stats(); return
    try:
        actual_height_script = coinbase_tx[42:42 + len(expected_height_script)]
    except Exception:
        actual_height_script = b""
    if actual_height_script != expected_height_script:
        emit("ERROR", f"COINBASE consensus guard: height={job['height']} expected={expected_height_script.hex()} actual={actual_height_script.hex()}")
        self.send({"id": mid, "result": False, "error": [23, "bad-cb-height", None]})
        self.shares_bad += 1; _bump_worker(self.worker, False); _save_stats(); return
'''
submit_needle = '        coinbase_tx = assemble_coinbase(coinb1, self.en1, en2, coinb2)\n        merkle = full_merkle_root(sha256d(coinbase_tx), job["other_tx"])'
if submit_needle not in text:
    raise SystemExit("submit coinbase insertion point missing")
text = text.replace(submit_needle, '        coinbase_tx = assemble_coinbase(coinb1, self.en1, en2, coinb2)\n' + validation + '        merkle = full_merkle_root(sha256d(coinbase_tx), job["other_tx"])', 1)

PATH.write_text(text)
print(f"patched {PATH} -> {new_version}")
