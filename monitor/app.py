#!/usr/bin/env python3
from flask import Flask, jsonify, render_template
from requests.auth import HTTPBasicAuth
from pathlib import Path
from datetime import datetime
import os, re, time, requests

app = Flask(__name__, template_folder="templates", static_folder="static")
DATA = Path("/app/data")
CFG = Path("/app/config/config.yaml")
RPC_PORT = int(os.getenv("FIX_RPCPORT", "24761"))
RPC_URL = f"http://127.0.0.1:{RPC_PORT}"
RPC_AUTH = HTTPBasicAuth(os.getenv("FIX_RPCUSER", "fixrpc"), os.getenv("FIX_RPCPASS", ""))
MATURITY = int(os.getenv("COINBASE_MATURITY", "100"))
LOG = DATA / "stratum.log"
DIFF_HISTORY = []


def config():
    try:
        import yaml
        c = yaml.safe_load(CFG.read_text()) or {}
        return c.get("pool", {})
    except Exception:
        return {}


def rpc(method, params=None, timeout=3):
    try:
        response = requests.post(RPC_URL, json={"jsonrpc": "1.0", "id": "dashboard", "method": method, "params": params or []}, auth=RPC_AUTH, timeout=timeout)
        data = response.json()
        return data.get("result"), data.get("error")
    except Exception as exc:
        return None, str(exc)


def lines(path, n=1500):
    try:
        return path.read_text(errors="replace").splitlines()[-n:]
    except Exception:
        return []


def parse_ts(s):
    try:
        return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S").timestamp()
    except Exception:
        return 0.0


def parse_logs():
    accepted, rejected, blocks = [], 0, []
    worker = "unknown"
    job = {}
    for line in lines(LOG):
        m = re.search(r"authorize\s+(\S+).*?(?:diff|share_diff)\s*[=:]\s*([0-9.]+)", line, re.I)
        if m:
            worker = m.group(1)
        # Current server emits: Job <id> height=<n> ... netdiff=<d>
        # Keep compatibility with the older Job id=<id> format as well.
        m = re.search(r"Job\s+(?:id=)?([^\s]+).*?(?:height=)?(\d+).*?(?:net_diff|network_diff|netdiff)[≈:=~]?\s*([0-9.eE+-]+)", line, re.I)
        if m:
            job = {"job_id": m.group(1), "height": int(m.group(2)), "network_diff": float(m.group(3))}
        m = re.search(r"ACCEPT\s+#(\d+)\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)", line, re.I)
        if m:
            n, work, pool_diff, h = m.groups()
            accepted.append({"ts": line[:19], "epoch": parse_ts(line), "num": int(n), "work": float(work), "pool_diff": float(pool_diff), "hash": h[:16], "worker": worker})
        if re.search(r"\bREJECT\b", line, re.I):
            rejected += 1
        m = re.search(r"BLOCK ACCEPTED.*?height=(\d+).*?hash=([0-9a-fA-F]{16,64})(?:.*?reward=([0-9.]+))?", line, re.I)
        if m:
            h, block_hash, reward = m.groups()
            blocks.append({"height": int(h), "hash": block_hash[:16], "reward": float(reward or 0), "mature_at": int(h) + MATURITY})
    return accepted[-100:], rejected, blocks[-100:], job


def hashrate(shares, window):
    now = time.time()
    recent = [x for x in shares if x.get("epoch", 0) and now - x["epoch"] <= window]
    return sum(x["work"] for x in recent) * (2**32) / window if recent else 0.0


def as_int(value):
    if value is None or value == "":
        return 0
    try:
        if isinstance(value, str):
            text = value.strip().lower().removeprefix("0x")
            if re.fullmatch(r"[0-9a-f]+", text) and any(c in "abcdef" for c in text):
                return int(text, 16)
            return int(text)
        return int(value)
    except Exception:
        return 0


def target_hex(value):
    if value in (None, ""):
        return None
    try:
        if isinstance(value, int):
            return f"{value:064x}"
        text = str(value).strip().lower().removeprefix("0x")
        if re.fullmatch(r"[0-9a-f]{1,64}", text):
            return text.zfill(64)
        return f"{int(float(text)):064x}"
    except Exception:
        return None


def status():
    info, _ = rpc("getblockchaininfo")
    net, _ = rpc("getnetworkinfo")
    mininginfo, _ = rpc("getmininginfo")
    balances, _ = rpc("getbalances")
    shares, rejected, blocks, parsed_job = parse_logs()
    pool = config()
    info, mininginfo, net, balances = info or {}, mininginfo or {}, net or {}, balances or {}

    height = int(info.get("blocks") or mininginfo.get("blocks") or 0)
    headers = int(info.get("headers") or height)
    network_diff = float(mininginfo.get("difficulty") or parsed_job.get("network_diff") or 0)
    network_hashrate = float(mininginfo.get("networkhashps") or 0)
    network_target = target_hex(mininginfo.get("target"))
    nbits = str(mininginfo.get("bits") or "")
    next_info = mininginfo.get("next") or {}
    next_height = int(next_info.get("height") or (height + 1 if height else 0))
    next_diff = float(next_info.get("difficulty") or 0)
    next_target = target_hex(next_info.get("target"))
    next_bits = str(next_info.get("bits") or "")

    fixed_difficulty = float(pool.get("fixed_difficulty", 13354))
    network_target_int = as_int(network_target)
    share_target = target_hex(int(network_target_int * network_diff / fixed_difficulty)) if network_target_int and network_diff > 0 and fixed_difficulty > 0 else None

    mine = balances.get("mine") or {}
    trusted, pending, immature = float(mine.get("trusted") or 0), float(mine.get("untrusted_pending") or 0), float(mine.get("immature") or 0)
    best = max((x["work"] for x in shares), default=0)
    effort = min(100.0, 100.0 * best / network_diff) if network_diff else 0.0
    h5, h1 = hashrate(shares, 300), hashrate(shares, 3600)
    competition = h5 / network_hashrate * 100.0 if network_hashrate else 0.0

    if network_diff:
        DIFF_HISTORY.append({"ts": int(time.time()), "height": height, "difficulty": network_diff})
    cutoff = time.time() - 86400
    DIFF_HISTORY[:] = [x for x in DIFF_HISTORY if x["ts"] >= cutoff][-120:]

    workers = {}
    for share in shares:
        w = workers.setdefault(share["worker"], {"accepted": 0, "rejected": 0, "difficulty": share["pool_diff"]})
        w["accepted"] += 1
    if workers and rejected:
        next(iter(workers.values()))["rejected"] = rejected

    return {
        "node": {"online": bool(info), "synced": bool(info) and not info.get("initialblockdownload", False), "initial_block_download": bool(info.get("initialblockdownload", False)), "height": height, "headers": headers, "difficulty": network_diff, "target": network_target, "bits": nbits, "connections": int(net.get("connections") or 0), "network_hashrate": network_hashrate, "chain": info.get("chain") or mininginfo.get("chain") or "unknown", "verification_progress": float(info.get("verificationprogress") or 0)},
        "next": {"height": next_height, "difficulty": next_diff, "target": next_target, "bits": next_bits},
        "competition": {"your_hashrate": h5, "network_hashrate": network_hashrate, "your_network_pct": competition, "network_share_ppm": competition * 10000},
        "mining": {"accepted": len(shares), "rejected": rejected, "reject_pct": round(100 * rejected / max(1, len(shares) + rejected), 2), "hashrate": h5, "hashrate_1h": h1, "fixed_difficulty": fixed_difficulty, "share_target": share_target, "best_share": best, "effort": round(effort, 8), "workers": workers},
        "wallet": {"confirmed": trusted, "pending": pending, "immature": immature, "total_rewards": sum(x["reward"] for x in blocks)},
        "blocks": blocks, "shares": shares, "job": parsed_job, "history_diff": DIFF_HISTORY, "payout": pool.get("payout_address", ""), "maturity": MATURITY, "ts": int(time.time()),
    }


@app.get("/")
def index():
    return render_template("dashboard.html", payout=config().get("payout_address", ""), maturity=MATURITY)


@app.get("/api/status")
def api_status():
    return jsonify(status())


@app.get("/api/stats")
def api_stats():
    return jsonify(status())


@app.get("/api/logs")
def api_logs():
    out = []
    for line in lines(LOG, 180):
        if any(k in line for k in ("ACCEPT", "REJECT", "BLOCK", "ERROR", "NEW ROUND", "authorize", "Job ")):
            level = "success" if "ACCEPT" in line or "BLOCK" in line else "danger" if "ERROR" in line else "warning" if "REJECT" in line else "info"
            out.append({"ts": line[:19], "level": level, "message": line[20:].strip() if len(line) > 20 else line})
    return jsonify({"events": out[-120:]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("FIX_DASH_PORT", "5050")), threaded=True)
