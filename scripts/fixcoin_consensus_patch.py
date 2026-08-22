#!/usr/bin/env python3
"""Apply FixedCoin-only consensus corrections to the generated Stratum adapter."""
from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

new_version = "fixedcoin-consensus-repair-2026-08-21-v34"
marker = re.search(r"^# ADAPT_VERSION=([^\n]+)$", text, re.MULTILINE)
if not marker:
    raise SystemExit("generated adapter version marker missing; refusing to patch")
version = marker.group(1)
if not version.startswith(("fixedcoin-fch-dashboard-repair-", "fixedcoin-consensus-repair-")):
    raise SystemExit(f"unexpected generated adapter version {version!r}; refusing to patch")
text = text[:marker.start()] + f"# ADAPT_VERSION={new_version}" + text[marker.end():]


def sanitize_source(source):
    """Replace raw control bytes that Python's parser rejects with escapes."""
    return source.replace("\x00", "\\x00")


def replace_function(source, name, replacement):
    source = sanitize_source(source)
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


FIXCOIN_POW_LIMIT = int("00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16)

fixedcoin_difficulty = '''def fixedcoin_target_to_difficulty(target):
    """Convert a FixedCoin network target to FixedCoin network difficulty."""
    target = int(target)
    if target <= 0:
        return 0.0
    return FIXCOIN_POW_LIMIT / target
'''

pow_limit_re = re.compile(r"^FIXCOIN_POW_LIMIT\s*=\s*", re.MULTILINE)
difficulty_re = re.compile(r"^def fixedcoin_target_to_difficulty\s*\(", re.MULTILINE)
marker = re.search(r"^# ADAPT_VERSION=[^\n]+$", text, re.MULTILINE)
if not marker:
    raise SystemExit("adapter version marker disappeared before helper injection")
injection = f"\n\nFIXCOIN_POW_LIMIT = {FIXCOIN_POW_LIMIT}\n\n{fixedcoin_difficulty.rstrip()}\n"
if not pow_limit_re.search(text) and not difficulty_re.search(text):
    text = text[:marker.end()] + injection + text[marker.end():]
elif not pow_limit_re.search(text):
    text = text[:marker.end()] + f"\n\nFIXCOIN_POW_LIMIT = {FIXCOIN_POW_LIMIT}\n" + text[marker.end():]
elif not difficulty_re.search(text):
    text = text[:marker.end()] + "\n\n" + fixedcoin_difficulty.rstrip() + "\n" + text[marker.end():]

bip34 = '''def bip34_height(height):
    height = int(height)
    if height < 0:
        raise ValueError("negative coinbase height")
    if height == 0:
        return b"\x00"
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

# FixedCoin network difficulty uses FixedCoin's own powLimit during the
# consensus patch. The network-difficulty patch restores the explorer/Core
# Bitcoin-compatible difficulty-1 scale afterwards.
text = text.replace(
    'net_diff = target_to_difficulty(bits_to_target(nbits))',
    'net_diff = fixedcoin_target_to_difficulty(bits_to_target(nbits))',
    1,
)

coinbase = '''def build_coinbase_parts(height, miner_value_sats, miner_spk, dev_spk=None, dev_value_sats=0, en1_size=4, en2_size=4, witness_commitment_hex=None, *args, **kwargs):
    """Build a FixedCoin coinbase with the miner output and optional witness commitment."""
    tag = b"/FIX-Solo/"
    height_script = bip34_height(height)
    scriptsig_len = len(height_script) + en1_size + en2_size + len(tag)
    part1 = struct.pack("<I", 2) + b"\x01" + b"\x00" * 32 + struct.pack("<I", 0xFFFFFFFF)
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
text = replace_function(text, "build_coinbase_parts", coinbase)

old = '"other_tx": other_tx, "created": time.time(),'
if old in text:
    text = text.replace(old, old + '\n                "witness_commitment": tmpl.get("default_witness_commitment"),', 1)
text = text.replace('"dev_value": dev_sats,', '"dev_value": 0,', 1)

witness = r'''def coinbase_add_witness(tx_nowitness, enabled):
    if not enabled or len(tx_nowitness) < 8 or tx_nowitness[4:6] == b"\x00\x01":
        return tx_nowitness
    return tx_nowitness[:4] + b"\x00\x01" + tx_nowitness[4:-4] + b"\x01\x20" + (b"\x00" * 32) + tx_nowitness[-4:]
'''
if "def coinbase_add_witness" in text:
    text = replace_function(text, "coinbase_add_witness", witness)
elif "\ndef assemble_coinbase(" in text:
    text = text.replace("\ndef assemble_coinbase(", "\n" + witness + "\ndef assemble_coinbase(", 1)
else:
    raise RuntimeError("assemble_coinbase anchor missing")

text = text.replace(
    "block = header + encode_varint(tx_count) + coinbase_tx",
    "block = header + encode_varint(tx_count) + coinbase_add_witness(coinbase_tx, bool(job.get(\"witness_commitment\")))",
    1,
)

oldaddr = '''    info2 = rpc("getaddressinfo", [addr])
    if info2 and info2.get("scriptPubKey"):
        return binascii.unhexlify(info2["scriptPubKey"])
'''
text = text.replace(oldaddr, "", 1)

submission_re = re.compile(
    r'(?ms)^            res = rpc\("submitblock", \[binascii\.hexlify\(block\)\.decode\(\)\]\)\n'
    r'            if res in \(None, ""\):\n'
    r'.*?^                emit\("ERROR", f"submitblock rejected: \{res\}"\)'
)
submission_new = '''            res = rpc("submitblock", [binascii.hexlify(block).decode()])

            candidate_seen = False
            candidate_canonical = False
            try:
                active_hash = str(rpc("getblockhash", [job["height"]]) or "").lower()
                candidate_seen = active_hash == hhex.lower()
                if not candidate_seen:
                    candidate = rpc("getblock", [hhex, 1])
                    candidate_seen = bool(candidate and str(candidate.get("hash") or "").lower() == hhex.lower())
                candidate_canonical = active_hash == hhex.lower()
            except Exception:
                candidate_seen = False

            accepted = res in (None, "") or candidate_seen
            if accepted:
                state = "canonical" if candidate_canonical else "known"
                emit("OK", f"*** BLOCK ACCEPTED *** height={job['height']} state={state} submit={res!r}")
                with _stats_lock:
                    _stats["blocks_found"] = _stats.get("blocks_found", 0) + 1
                    _stats["block_rewards_total"] = _stats.get("block_rewards_total", 0) + job["value"] / 1e8
                    blog = _stats.setdefault("blocks_log", [])
                    blog.append({
                        "ts": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "height": job["height"], "hash": hhex,
                        "reward": job["value"] / 1e8, "address": PAYOUT_ADDRESS,
                        "mature_at_height": job["height"] + int(os.getenv("COINBASE_MATURITY", "100")),
                        "submit_result": res,
                        "canonical": candidate_canonical,
                    })
                    _stats["blocks_log"] = blog[-200:]
                _save_stats()
            else:
                emit("ERROR", f"submitblock rejected: {res}; candidate_not_found={not candidate_seen}")'''
text, n = submission_re.subn(submission_new, text, count=1)
if n != 1:
    raise RuntimeError("submitblock accounting block marker missing")

text = text.replace(
    'self.send({"id": mid, "result": False, "error": [21, "stale job", None]})',
    'emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id}")\n            self.send({"id": mid, "result": False, "error": [21, "stale job", None]})',
    1,
)
text = text.replace(
    'self.send({"id": mid, "result": False, "error": [20, "bad hex", None]})',
    'emit("WARN", f"REJECT reason=bad-hex worker={self.worker} job={job_id} en2={en2_hex} ntime={ntime_hex} nonce={nonce_hex}")\n            self.send({"id": mid, "result": False, "error": [20, "bad hex", None]})',
    1,
)

# Strict Stratum policy: a submitted share must satisfy the advertised pool
# difficulty. A network-valid block candidate is checked independently by the
# block-target path; it is never allowed to bypass normal share enforcement.
low_old = 'self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})'
if text.count(low_old) != 1:
    raise RuntimeError(f"low-difficulty rejection marker mismatch: found {text.count(low_old)}")
if "ACCEPT low-difficulty" in text:
    raise RuntimeError("low-difficulty acceptance bypass remains in generated adapter")

# Build-time regression checks.
text = sanitize_source(text)
ast.parse(text)
ns = {"__name__": "_fixedcoin_patch_test", "__file__": str(PATH)}
exec(compile(text, "<fixedcoin-patched-adapter>", "exec"), ns)
assert ns["bip34_height"](32767) == b"\x02\xff\x7f"
assert ns["bip34_height"](32768) == b"\x03\x00\x80\x00"
assert ns["bip34_height"](44343) == b"\x03\x37\xad\x00"
assert ns["FIXCOIN_POW_LIMIT"] == FIXCOIN_POW_LIMIT
assert ns["fixedcoin_target_to_difficulty"](ns["FIXCOIN_POW_LIMIT"]) == 1.0
assert 'submitblock rejected: {res}; candidate_not_found=' in text
assert 'candidate_seen = active_hash == hhex.lower()' in text
assert 'ACCEPT low-difficulty' not in text
assert 'result": False, "error": [23, "low difficulty", None]' in text
assert "dev_sats = 0" in text
assert "miner_value = new_value" in text
assert 'miner_value = new_value - dev_sats' not in text
assert "DEV_ADDRESS = None" in text
PATH.write_text(text)
print(f"patched {PATH} -> {new_version}; strict Stratum difficulty enforcement restored")
