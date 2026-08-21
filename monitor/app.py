#!/usr/bin/env python3
from flask import Flask, jsonify, render_template
from requests.auth import HTTPBasicAuth
from pathlib import Path
from datetime import datetime
import json, os, re, subprocess, time, requests

app = Flask(__name__, template_folder="templates", static_folder="static")
DATA = Path("/app/data")
CFG = Path("/app/config/config.yaml")
DATADIR = Path(os.getenv("FIX_DATADIR", "/data/fixedcoin"))
RPC_PORT = int(os.getenv("FIX_RPCPORT", "24761"))
RPC_URL = f"http://127.0.0.1:{RPC_PORT}"
RPC_AUTH = HTTPBasicAuth(os.getenv("FIX_RPCUSER", "fixrpc"), os.getenv("FIX_RPCPASS", ""))
WALLET = os.getenv("FIX_WALLET_NAME", "mining")
CLI = os.getenv("FIXCOIN_CLI", "fixedcoin-cli")
MATURITY = int(os.getenv("COINBASE_MATURITY", "100"))
ROUND_SECONDS = int(os.getenv("ROUND_TARGET_SECONDS", "600"))
WORKER_ACTIVE_SECONDS = int(os.getenv("WORKER_ACTIVE_SECONDS", "180"))
LOG = DATA / "stratum.log"
STATS = DATA / "stats.json"
BLOCKS = DATA / "blocks.json"
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
        r = requests.post(RPC_URL, json={"jsonrpc":"1.0","id":"dashboard","method":method,"params":params or []}, auth=RPC_AUTH, timeout=timeout)
        data = r.json()
        return data.get("result"), data.get("error")
    except Exception as exc:
        return None, str(exc)


def wallet_rpc(method, params=None, timeout=5):
    """Use the CLI wallet selector; avoids FixedCoin wallet-endpoint quirks."""
    cmd = [CLI, f"-datadir={DATADIR}", f"-rpcwallet={WALLET}", method]
    for value in (params or []):
        if isinstance(value, (dict, list, bool)):
            cmd.append(json.dumps(value, separators=(",", ":")))
        else:
            cmd.append(str(value))
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if p.returncode != 0:
            return None, p.stderr.strip() or p.stdout.strip() or f"exit {p.returncode}"
        return json.loads(p.stdout), None
    except Exception as exc:
        return None, str(exc)


def read_stats():
    try: return json.loads(STATS.read_text()) if STATS.exists() else {}
    except Exception: return {}


def read_ledger():
    try:
        rows=json.loads(BLOCKS.read_text()) if BLOCKS.exists() else []
        return rows if isinstance(rows,list) else []
    except Exception:
        return []


def lines(path, n=2200):
    try: return path.read_text(errors="replace").splitlines()[-n:]
    except Exception: return []


def parse_ts(s):
    try: return datetime.strptime(str(s)[:19], "%Y-%m-%d %H:%M:%S").timestamp()
    except Exception: return 0.0


def parse_logs():
    accepted, rejected, blocks, workers, job = [], 0, [], {}, {}
    now=time.time(); current_worker=None
    for line in lines(LOG):
        ts=parse_ts(line[:19])
        m=re.search(r"authorize\s+(\S+).*?(?:diff|share_diff)\s*[=:]\s*([0-9.]+)",line,re.I)
        if m:
            name,diff=m.groups(); current_worker=name
            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})
            w["difficulty"]=float(diff); w["last_seen"]=ts
        m=re.search(r"NEW ROUND\s+height=(\d+)\s+netdiff=([0-9.eE+-]+)",line,re.I)
        if m: job["height"]=int(m.group(1)); job["network_diff"]=float(m.group(2))
        m=re.search(r"Job\s+([^\s]+).*?height=(\d+).*?(?:miner=([0-9.eE+-]+))?.*?(?:dev=([0-9.eE+-]+))?",line,re.I)
        if m:
            job.update({"job_id":m.group(1),"height":int(m.group(2))})
            if m.group(3): job["miner_value"]=float(m.group(3))
            if m.group(4): job["dev_value"]=float(m.group(4))
        m=re.search(r"ACCEPT\s+#(\d+)\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)",line,re.I)
        if m:
            num,work,diff,h=m.groups(); worker=current_worker or "unknown"
            accepted.append({"ts":line[:19],"epoch":ts,"num":int(num),"work":float(work),"pool_diff":float(diff),"hash":h[:16],"worker":worker})
            w=workers.setdefault(worker,{"accepted":0,"rejected":0,"difficulty":float(diff)})
            w["accepted"]+=1; w["last_seen"]=ts; w["difficulty"]=float(diff)
        if re.search(r"\bREJECT\b|\blow difficulty\b|stale job|bad params|invalid",line,re.I): rejected+=1
    for w in workers.values():
        w["active"]=bool(w.get("last_seen") and now-w["last_seen"]<=WORKER_ACTIVE_SECONDS)
    return accepted[-200:],rejected,blocks[-100:],workers,job


def hashrate(shares,window):
    now=time.time(); recent=[x for x in shares if x.get("epoch") and 0<=now-x["epoch"]<=window and float(x.get("work") or 0)>0]
    return sum(float(x.get("work") or 0)*(2**32) for x in recent)/float(window) if recent else 0.0


def normalize_recent(raw):
    out=[]
    if not isinstance(raw,list): return out
    for x in raw[-200:]:
        if not isinstance(x,dict): continue
        ts=x.get("ts") or x.get("time") or x.get("timestamp"); epoch=parse_ts(ts) if isinstance(ts,str) else float(ts or 0)
        out.append({"ts":datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S") if epoch else str(ts or "—"),"epoch":epoch,"num":x.get("num") or x.get("id") or 0,"work":float(x.get("work") or x.get("share_work") or x.get("difficulty") or 0),"pool_diff":float(x.get("pool_diff") or x.get("credited") or x.get("share_diff") or 0),"hash":str(x.get("hash") or x.get("share_hash") or "")[:16],"worker":str(x.get("worker") or "unknown")})
    return out


def as_number(v,default=0.0):
    try:return float(v)
    except Exception:return default


def wallet_state(current_height):
    balances, balances_error=wallet_rpc("getbalances",timeout=4)
    walletinfo,walletinfo_error=wallet_rpc("getwalletinfo",timeout=4)
    txs,tx_error=wallet_rpc("listtransactions",["*",200,0,True],timeout=5)
    mine=(balances or {}).get("mine") or {}
    confirmed=as_number(mine.get("trusted"))
    rpc_pending=as_number(mine.get("untrusted_pending"))
    rpc_immature=as_number(mine.get("immature"))
    ledger=read_ledger(); blocks=[]; seen=set()
    for b in ledger:
        if not isinstance(b,dict): continue
        txid=str(b.get("txid") or ""); bh=int(b.get("height") or 0); key=(txid,bh)
        if (not txid and not bh) or key in seen: continue
        seen.add(key)
        confirmations=max(0,current_height-bh+1) if bh and current_height else 0
        maturity_height=int(b.get("maturity_height") or (bh+MATURITY if bh else 0))
        remaining=max(0,maturity_height-current_height) if maturity_height else MATURITY
        orphaned=bool(b.get("orphaned") or str(b.get("status") or "").upper()=="ORPHANED")
        state="ORPHANED" if orphaned else ("MATURED" if confirmations>=MATURITY else "IMMATURE")
        blocks.append({"txid":txid,"height":bh,"confirmations":confirmations,"validity_rounds":confirmations,"validity_target":MATURITY,"reward":abs(as_number(b.get("reward"))),"category":"generate","state":state,"maturity_height":maturity_height,"maturity_remaining":remaining,"time":parse_ts(b.get("found_at") or b.get("last_seen")) if isinstance(b.get("found_at") or b.get("last_seen"),str) else int(b.get("time") or 0),"blockhash":str(b.get("blockhash") or ""),"status":state})
    immature=rpc_immature
    ledger_immature=sum(x["reward"] for x in blocks if x["state"]=="IMMATURE")
    if ledger_immature>0: immature=max(immature,ledger_immature)
    blocks.sort(key=lambda x:(x.get("height") or 0,x.get("time") or 0),reverse=True)
    return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":rpc_pending+immature,"total":confirmed+rpc_pending+immature,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}


def status():
    stats=read_stats(); log_shares,log_rejected,log_blocks,log_workers,log_job=parse_logs(); shares=normalize_recent(stats.get("recent_shares")) or log_shares
    rejected=int(stats.get("shares_bad") or log_rejected or 0); accepted=int(stats.get("shares_ok") or len(shares)); info,info_error=rpc("getblockchaininfo"); net,_=rpc("getnetworkinfo"); mininginfo,_=rpc("getmininginfo"); info=info or {}; net=net or {}; mininginfo=mininginfo or {}
    pool=config(); fixed_diff=as_number(pool.get("fixed_difficulty",13354),13354); network_diff=as_number(stats.get("network_diff")) or as_number(log_job.get("network_diff")) or as_number(mininginfo.get("difficulty")); height=int(stats.get("round_height") or info.get("blocks") or mininginfo.get("blocks") or log_job.get("height") or 0); headers=int(info.get("headers") or height); initial_sync=bool(info.get("initialblockdownload",False)); wallet=wallet_state(height)
    if network_diff: DIFF_HISTORY.append({"ts":int(time.time()),"height":height,"difficulty":network_diff})
    DIFF_HISTORY[:]=[x for x in DIFF_HISTORY if x["ts"]>=time.time()-86400][-180:]
    job={"job_id":log_job.get("job_id"),"height":stats.get("round_height") or log_job.get("height") or height,"network_diff":network_diff}; job.update(log_job)
    round_best=as_number(stats.get("round_best"),max((as_number(x.get("work")) for x in shares),default=0)); round_work=as_number(stats.get("round_work")); round_shares=int(stats.get("round_shares") or 0); best_pct=(round_best/network_diff*100) if network_diff else 0; remaining=max(0,network_diff-round_best) if network_diff else 0; round_effort=as_number(stats.get("round_effort_pct"),best_pct); h5=hashrate(shares,300); h1=hashrate(shares,3600); network_hashrate=as_number(mininginfo.get("networkhashps"))
    persisted=stats.get("workers") if isinstance(stats.get("workers"),dict) else {}; workers={}
    for name in set(log_workers)|set(persisted):
        lv=log_workers.get(name,{}); pv=persisted.get(name,{}) if isinstance(persisted.get(name,{}),dict) else {}
        active=bool(lv.get("active"))
        if not active:
            continue
        workers[name]={"accepted":int(pv.get("ok") or pv.get("accepted") or pv.get("shares") or lv.get("accepted") or 0),"rejected":int(pv.get("bad") or pv.get("rejected") or lv.get("rejected") or 0),"difficulty":as_number(pv.get("difficulty") or lv.get("difficulty") or fixed_diff,fixed_diff),"active":True}
    active_workers=list(workers.keys())
    blocks=wallet["blocks"] or (stats.get("blocks_log") if isinstance(stats.get("blocks_log"),list) else []) or log_blocks
    return {"status":"online" if info or stats else "degraded","last_update":int(time.time()),"node":{"online":bool(info) or bool(stats),"synced":bool(info) and not initial_sync,"initial_block_download":initial_sync,"height":height,"headers":headers,"difficulty":network_diff,"target":mininginfo.get("target"),"bits":mininginfo.get("bits"),"connections":int(net.get("connections") or 0),"network_hashrate":network_hashrate,"chain":info.get("chain") or mininginfo.get("chain") or "unknown","verification_progress":as_number(info.get("verificationprogress"),0),"rpc_error":info_error},"mining":{"accepted":accepted,"rejected":rejected,"reject_pct":round(100*rejected/max(1,accepted+rejected),3),"hashrate_5m":h5,"hashrate_1h":h1,"fixed_difficulty":fixed_diff,"best_share":round_best,"best_share_pct":best_pct,"difficulty_remaining":remaining,"round_work":round_work,"round_shares":round_shares,"round_effort":round_effort,"workers":workers,"worker_count":len(active_workers),"active_workers":active_workers},"round":{"height":int(stats.get("round_height") or height),"shares":round_shares,"work":round_work,"best_share":round_best,"effort_pct":round_effort,"best_share_pct":best_pct,"difficulty":network_diff,"remaining":remaining,"started_at":stats.get("round_started_at"),"target_seconds":ROUND_SECONDS},"competition":{"your_hashrate":h5,"network_hashrate":network_hashrate},"wallet":{"confirmed":wallet["confirmed"],"pending":wallet["pending"],"immature":wallet["immature"],"unconfirmed":wallet["unconfirmed"],"total":wallet["total"],"total_rewards":as_number(stats.get("block_rewards_total"))},"job":job,"shares":shares[-100:],"blocks":blocks,"history_diff":DIFF_HISTORY,"payout":pool.get("payout_address",""),"maturity":MATURITY,"ts":int(time.time())}

@app.get("/")
def index(): return render_template("dashboard_v3.html",payout=config().get("payout_address",""),maturity=MATURITY)
@app.get("/api/status")
def api_status(): return jsonify(status())
@app.get("/api/overview")
def api_overview(): return jsonify(status())
@app.get("/api/stats")
def api_stats(): return jsonify(status())
@app.get("/api/logs")
def api_logs():
    events=[]
    for line in lines(LOG,220):
        if any(k in line for k in ("ACCEPT","REJECT","BLOCK","ERROR","NEW ROUND","authorize","Job ","GBT","notify")):
            level="success" if "ACCEPT" in line or "BLOCK" in line else "danger" if "ERROR" in line or "REJECT" in line else "warning" if "WARN" in line else "info"; events.append({"ts":line[:19],"level":level,"message":line[20:].strip() if len(line)>20 else line})
    return jsonify({"events":events[-160:]})

if __name__ == "__main__": app.run(host="0.0.0.0",port=int(os.getenv("FIX_DASH_PORT","5050")),threaded=True)