#!/usr/bin/env python3
"""Apply FixedCoin-only consensus corrections to the generated Stratum adapter."""
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "stratum" / "server.py"
text = PATH.read_text()

old_version = 'ADAPT_VERSION = "fixedcoin-fch-dashboard-repair-2026-08-20-v12"'
new_version = 'ADAPT_VERSION = "fixedcoin-consensus-repair-2026-08-20-v14"'
if old_version not in text:
    if new_version in text:
        raise SystemExit(0)
    raise SystemExit("unexpected server.py adapter version; refusing to patch")
text = text.replace(old_version, new_version, 1)

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
if old_coinbase not in text:
    raise SystemExit("coinbase adapter block missing")
text = text.replace(old_coinbase, new_coinbase, 1)

PATH.write_text(text)
print(f"patched {PATH} -> {new_version}")
