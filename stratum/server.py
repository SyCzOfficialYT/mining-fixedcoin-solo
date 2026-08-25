#!/usr/bin/env python3
"""Generate the FixedCoin Stratum server from the pinned FreeCash base."""
import ast
import os
import re
import runpy
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = HERE / "server_full.py"
URL = "https://raw.githubusercontent.com/SyCzOfficialYT/freecash-coin/a88d89675b3a41cc6774e1b975e57e050d4892cc/stratum/server.py"
ADAPT_VERSION = "fixedcoin-consensus-repair-2026-08-25-v35"


def sanitize_source(source):
    """Turn accidental literal control bytes into Python escape sequences."""
    return "".join(
        f"\\x{ord(ch):02x}" if ord(ch) < 0x20 and ch not in "\n\r\t" else ch
        for ch in source
    )


def replace_function(source, name, replacement):
    replacement = sanitize_source(replacement)
    tree = ast.parse(source)
    target = next((n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)
    if target is None:
        raise RuntimeError(f"function {name!r} not found in FreeCash base")
    lines = source.splitlines(keepends=True)
    start = sum(map(len, lines[: target.lineno - 1]))
    end = sum(map(len, lines[: target.end_lineno]))
    return source[:start] + replacement.rstrip() + "\n" + source[end:]


def adapt(t):
    t = t.replace('job_interval", 20)', 'job_interval", 30)')
    t = t.replace('blog[-20:]', 'blog[-1000:]')
    t = t.replace('+ 14400', '+ 100')
    t = t.replace(' FCH', ' FIX')
    t = t.replace('FreeCash', 'FixedCoin')
    t = t.replace('/FCH-Solo/', '/FIX-Solo/')

    gbt_pattern = re.compile(r'rpc\("getblocktemplate",\s*\[\{\s*"rules"\s*:\s*\[\]\s*\}\]\)\s*or\s*rpc\("getblocktemplate",\s*\[\]\)')
    t, n = gbt_pattern.subn('rpc("getblocktemplate", [{"rules": ["segwit"]}])', t, count=1)
    if n == 0:
        t = t.replace('rpc("getblocktemplate", [{"rules": []}])', 'rpc("getblocktemplate", [{"rules": ["segwit"]}])', 1)
        t = t.replace('rpc("getblocktemplate", [])', 'rpc("getblocktemplate", [{"rules": ["segwit"]}])', 1)
    if 'rpc("getblocktemplate", [{"rules": ["segwit"]}])' not in t:
        raise RuntimeError('segwit GBT patch failed')
    if 'rpc("getblocktemplate", [{"rules": []}])' in t:
        raise RuntimeError('old invalid GBT request remains')

    rpc_replacement = '''def rpc(method, params=None):
    import requests as _requests
    from requests.auth import HTTPBasicAuth as _HTTPBasicAuth

    endpoint = f"http://{RPC_HOST}:{RPC_PORT}"
    payload = {"jsonrpc": "1.0", "id": "stratum", "method": method, "params": params or []}
    user = os.getenv("FIX_RPCUSER", RPC_USER) or RPC_USER
    password = os.getenv("FIX_RPCPASS", RPC_PASS) or RPC_PASS

    # Keep the last valid GBT in memory. FixedCoin can temporarily return
    # -10 while it is advancing/syncing. Existing Stratum jobs remain valid
    # during that short window, so do not destroy a working job just because
    # a refresh attempt failed.
    global _FIX_GBT_CACHE
    if "_FIX_GBT_CACHE" not in globals():
        _FIX_GBT_CACHE = None

    attempts = []
    if password:
        attempts.append(("basic-env", _HTTPBasicAuth(user, password)))
    cookie_path = Path(os.getenv("FIX_DATADIR", "/data/fixedcoin")) / ".cookie"
    if cookie_path.is_file():
        try:
            raw = cookie_path.read_text().strip()
            if ":" in raw:
                cuser, cpass = raw.split(":", 1)
                attempts.append(("cookie", _HTTPBasicAuth(cuser, cpass)))
        except Exception:
            pass
    if not attempts:
        attempts.append(("basic-config", _HTTPBasicAuth(user, password)))

    last_error = None
    for auth_name, auth in attempts:
        try:
            r = _requests.post(endpoint, json=payload, auth=auth, timeout=60)
            try:
                data = r.json()
            except ValueError:
                last_error = f"HTTP {r.status_code}: {r.text[:500]}"
                continue
            if data.get("error"):
                last_error = data.get("error")
                if r.status_code in (401, 403):
                    continue
                if method == "getblocktemplate" and isinstance(last_error, dict) and int(last_error.get("code", 0)) == -10:
                    if _FIX_GBT_CACHE is not None:
                        log.warning("getblocktemplate temporarily unavailable (-10); keeping last valid template/job")
                        return _FIX_GBT_CACHE
                    log.error("RPC %s via %s: %s", method, auth_name, last_error)
                    return None
                log.error("RPC %s via %s: %s", method, auth_name, last_error)
                return None
            if r.status_code >= 400:
                last_error = {"code": r.status_code, "message": r.text[:500]}
                continue
            result = data.get("result")
            if method == "getblocktemplate" and result:
                _FIX_GBT_CACHE = result
            return result
        except Exception as exc:
            last_error = str(exc)

    if method == "getblocktemplate" and _FIX_GBT_CACHE is not None:
        log.warning("getblocktemplate refresh failed; keeping last valid template/job: %s", last_error)
        return _FIX_GBT_CACHE
    log.error("RPC %s failed after %d auth attempt(s): %s", method, len(attempts), last_error)
    return None
'''
    t = replace_function(t, 'rpc', rpc_replacement)

    bip34 = '''def bip34_height(height):
    """Return the minimally encoded positive CScriptNum for BIP34."""
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
    t = replace_function(t, 'bip34_height', bip34)

    marker = 'MAX_DIFF = int(cfg["pool"].get("vardiff_max", 50_000_000))'
    if marker not in t:
        raise RuntimeError('vardiff marker missing')
    t = t.replace(
        marker,
        marker + '\n'
        'FIXED_DIFF = int(cfg["pool"].get("fixed_difficulty", 13354))\n'
        'MIN_DIFF = int(cfg["pool"].get("min_difficulty", cfg["pool"].get("vardiff_min", FIXED_DIFF)))\n'
        'VARDIFF = bool(cfg["pool"].get("vardiff", False))',
        1,
    )

    fixed_parser = '''def parse_fixed_diff(*candidates):
    for raw in candidates:
        if not raw or not isinstance(raw, str):
            continue
        m = re.search(r"(?:^|[;,\\s])(?:d|diff)\\s*[=:]\\s*(\\d+(?:\\.\\d+)?)", raw, re.I)
        if not m:
            m = re.match(r"^(?:d|diff)\\s*[=:]\\s*(\\d+(?:\\.\\d+)?)$", raw.strip(), re.I)
        if m:
            try:
                d = float(m.group(1))
                if 16 <= d <= MAX_DIFF:
                    return int(round(d))
            except Exception:
                pass
    return None
'''
    t = replace_function(t, 'parse_fixed_diff', fixed_parser)

    coinbase = '''def build_coinbase_parts(height, miner_value_sats, miner_spk, dev_spk=None, dev_value_sats=0, en1_size=4, en2_size=4, witness_commitment_hex=None, *args, **kwargs):
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
    t = replace_function(t, 'build_coinbase_parts', coinbase)

    old = '"other_tx": other_tx, "created": time.time(),'
    if old in t:
        t = t.replace(old, old + '\n                "witness_commitment": tmpl.get("default_witness_commitment"),', 1)

    accounting_old = '''        dev_sats = get_dev_reward_sats(height)
        new_value = int(tmpl["coinbasevalue"])'''
    accounting_new = '''        new_value = int(tmpl["coinbasevalue"])
        dev_sats = min(get_dev_reward_sats(height), new_value)
        miner_value = new_value - dev_sats
        if miner_value < 0 or miner_value + dev_sats != new_value:
            raise RuntimeError(
                f"invalid coinbase accounting: miner={miner_value} dev={dev_sats} "
                f"total={miner_value + dev_sats} gbt={new_value}"
            )'''
    if accounting_old not in t:
        raise RuntimeError('coinbase accounting marker missing')
    t = t.replace(accounting_old, accounting_new, 1)
    t = t.replace('"id": job_id, "height": height, "value": new_value,', '"id": job_id, "height": height, "value": miner_value,', 1)

    t = t.replace('len(self.en1), self.en2_size, job.get("witness_commitment"),', 'job.get("dev_value", 0), len(self.en1), self.en2_size, job.get("witness_commitment"),')
    t = t.replace('len(self.en1), self.en2_size,\n        )', 'job.get("dev_value", 0), len(self.en1), self.en2_size, job.get("witness_commitment"),\n        )')
    if '"dev_value": dev_sats,' not in t:
        raise RuntimeError('dev_value job field missing')

    witness = '''def coinbase_add_witness(tx_nowitness, enabled):
    if not enabled or len(tx_nowitness) < 8 or tx_nowitness[4:6] == b"\x00\x01":
        return tx_nowitness
    return tx_nowitness[:4] + b"\x00\x01" + tx_nowitness[4:-4] + b"\x01\x20" + (b"\x00" * 32) + tx_nowitness[-4:]
'''
    if 'def coinbase_add_witness' in t:
        t = replace_function(t, 'coinbase_add_witness', witness)
    else:
        t = t.replace('\ndef assemble_coinbase(', '\n' + witness + '\ndef assemble_coinbase(', 1)

    t = t.replace('block = header + encode_varint(tx_count) + coinbase_tx', 'block = header + encode_varint(tx_count) + coinbase_add_witness(coinbase_tx, bool(job.get("witness_commitment")))', 1)
    oldaddr = '''    info2 = rpc("getaddressinfo", [addr])
    if info2 and info2.get("scriptPubKey"):
        return binascii.unhexlify(info2["scriptPubKey"])
'''
    t = t.replace(oldaddr, '')

    t = t.replace(
        'self.send({"id": mid, "result": False, "error": [21, "stale job", None]})',
        'emit("WARN", f"REJECT reason=stale-job worker={self.worker} job={job_id} height={job.get(\'height\')} ntime={ntime_hex} nonce={nonce_hex}")\n            self.send({"id": mid, "result": False, "error": [21, "stale job", None]})',
        1,
    )
    t = t.replace(
        'self.send({"id": mid, "result": False, "error": [20, "bad hex", None]})',
        'emit("WARN", f"REJECT reason=bad-hex worker={self.worker} job={job_id} en2={en2_hex} ntime={ntime_hex} nonce={nonce_hex}")\n            self.send({"id": mid, "result": False, "error": [20, "bad hex", None]})',
        1,
    )
    t = t.replace(
        'self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})',
        'emit("WARN", f"REJECT reason=low-difficulty worker={self.worker} job={job_id} height={job[\'height\']} share_diff={share_work:.6f} required_diff={need:.6f} fixed_diff={self.diff:.6f} ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:24]}")\n            self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})',
        1,
    )

    # FixedCoin solo uses a single fixed Stratum target when vardiff is off.
    # Do this after the upstream base has been adapted so the generated
    # server_full.py cannot silently fall back to the base's VARDIFF defaults.
    t = t.replace(
        'self.diff = max(START_DIFF, MIN_DIFF)',
        'self.diff = FIXED_DIFF if not VARDIFF else max(START_DIFF, MIN_DIFF)',
        1,
    )
    t = t.replace(
        'self.diff_from_password = False',
        'self.diff_from_password = not VARDIFF',
        1,
    )

    return t


def generate_server():
    print("Fetching pinned FreeCash stratum base…", flush=True)
    raw = urllib.request.urlopen(URL, timeout=60).read().decode()
    adapted = adapt(raw)
    adapted = sanitize_source(adapted)
    ast.parse(adapted)
    assert 'rpc("getblocktemplate", [{"rules": ["segwit"]}])' in adapted
    assert 'rpc("getblocktemplate", [{"rules": []}])' not in adapted
    assert 'def rpc(method, params=None):' in adapted
    assert 'def bip34_height(height):' in adapted
    assert 'REJECT reason=low-difficulty' in adapted
    assert 'REJECT reason=stale-job' in adapted
    assert 'keeping last valid template/job' in adapted
    assert 'FIXED_DIFF if not VARDIFF else max(START_DIFF, MIN_DIFF)' in adapted
    assert 'self.diff_from_password = not VARDIFF' in adapted
    ns = {"__name__": "_fixedcoin_adapter_test", "__file__": str(FULL)}
    exec(compile(adapted, "<fixedcoin-adapter-test>", "exec"), ns)
    assert ns["bip34_height"](44343) == b"\x03\x37\xad\x00", "BIP34 44343 encoding regression"
    FULL.write_text(f"# ADAPT_VERSION={ADAPT_VERSION}\n" + adapted)
    print("Wrote", FULL, FULL.stat().st_size, flush=True)


if os.environ.get('STRATUM_BUILD_ONLY') == '1':
    generate_server()
    raise SystemExit(0)

if not FULL.exists() or ADAPT_VERSION not in FULL.read_text(errors='ignore'):
    generate_server()

sys.argv[0] = str(FULL)
runpy.run_path(str(FULL), run_name='__main__')
