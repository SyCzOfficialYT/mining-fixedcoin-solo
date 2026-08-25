#!/usr/bin/env python3
"""Expose authoritative Core difficulty and live Stratum state to the dashboard.

This patch is intentionally backend-only. The dashboard was migrated to v4, so
legacy v3 HTML/CSS/JS markers must not be required during the image build.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "monitor" / "app.py"

text = APP.read_text()

# ---------------------------------------------------------------------------
# 1. Ask FixedCoin Core for the authoritative network difficulty.
# ---------------------------------------------------------------------------
old = 'info,info_error=rpc("getblockchaininfo"); net,_=rpc("getnetworkinfo"); mininginfo,_=rpc("getmininginfo"); info=info or {}; net=net or {}; mininginfo=mininginfo or {}'
new = 'info,info_error=rpc("getblockchaininfo"); net,_=rpc("getnetworkinfo"); mininginfo,_=rpc("getmininginfo"); core_diff,_=rpc("getdifficulty"); info=info or {}; net=net or {}; mininginfo=mininginfo or {}'
if 'core_diff,_=rpc("getdifficulty")' not in text:
    if old not in text:
        raise RuntimeError("dashboard RPC marker mismatch: could not locate status RPC block")
    text = text.replace(old, new, 1)

old = 'network_diff=as_number(stats.get("network_diff")) or as_number(log_job.get("network_diff")) or as_number(mininginfo.get("difficulty"))'
new = 'network_diff=as_number(core_diff) or as_number(mininginfo.get("difficulty")) or as_number(stats.get("network_diff")) or as_number(log_job.get("network_diff"))'
if old in text:
    text = text.replace(old, new, 1)
elif 'network_diff=as_number(core_diff)' not in text:
    raise RuntimeError("dashboard difficulty marker mismatch: could not locate network_diff assignment")

# The pool/Stratum difficulty is a separate value from network difficulty.
# Keep it explicitly defined so /api/status can never reference an undefined
# pool_difficulty variable after the dashboard patches are applied.
old = 'pool=config(); fixed_diff=as_number(pool.get("fixed_difficulty",13354),13354); network_diff='
new = 'pool=config(); fixed_diff=as_number(pool.get("fixed_difficulty",13354),13354); pool_difficulty=fixed_diff; network_diff='
if old in text:
    text = text.replace(old, new, 1)
elif 'pool_difficulty=fixed_diff; network_diff=' not in text:
    raise RuntimeError("dashboard pool difficulty marker mismatch: could not locate pool configuration block")

# ---------------------------------------------------------------------------
# 2. Parse explicit Fixed/VarDiff telemetry from Stratum logs.
# ---------------------------------------------------------------------------
old = 'm=re.search(r"authorize\\s+(\\S+).*?(?:diff|share_diff)\\s*[=:]\\s*([0-9.]+)",line,re.I)\n        if m:\n            name,diff=m.groups(); current_worker=name\n            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff)})\n            w["difficulty"]=float(diff); w["last_seen"]=ts'
new = 'm=re.search(r"authorize\\s+(\\S+).*?(?:diff|share_diff)\\s*[=:]\\s*([0-9.]+)",line,re.I)\n        if m:\n            name,diff=m.groups(); current_worker=name\n            w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff),"mode":"fixed"})\n            w["difficulty"]=float(diff); w["last_seen"]=ts\n            m2=re.search(r"authorize\\s+\\S+.*?diff=([0-9.]+).*?mode=(fixed|vardiff(?:=True)?)",line,re.I)\n            if m2:\n                w["difficulty"]=float(m2.group(1)); w["mode"]="fixed" if m2.group(2).lower()=="fixed" else "vardiff"'
if 'mode=(fixed|vardiff' not in text:
    if old not in text:
        raise RuntimeError("dashboard worker authorize marker mismatch")
    text = text.replace(old, new, 1)

old = 'm=re.search(r"NEW ROUND\\s+height=(\\d+)\\s+netdiff=([0-9.eE+-]+)",line,re.I)'
new = 'm=re.search(r"VARDIFF\\s+(\\S+)\\s+([0-9.]+)→([0-9.]+)",line,re.I)\n        if m:\n            name,prev_diff,new_diff=m.groups(); w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(new_diff),"mode":"vardiff"}); w["difficulty"]=float(new_diff); w["mode"]="vardiff"; w["last_seen"]=ts; current_worker=name\n        ' + old
if 'VARDIFF\\s+(\\S+)\\s+([0-9.]+)→([0-9.]+)' not in text:
    if old not in text:
        raise RuntimeError("dashboard round marker mismatch")
    text = text.replace(old, new, 1)

# Accepted shares inherit the current worker difficulty/mode.
old = 'w=workers.setdefault(worker,{"accepted":0,"rejected":0,"difficulty":float(diff)})\n            w["accepted"]+=1; w["last_seen"]=ts; w["difficulty"]=float(diff)'
new = 'w=workers.setdefault(worker,{"accepted":0,"rejected":0,"difficulty":float(diff),"mode":"fixed"})\n            w["accepted"]+=1; w["last_seen"]=ts; w["difficulty"]=float(w.get("difficulty") or diff)'
if old in text:
    text = text.replace(old, new, 1)

# ---------------------------------------------------------------------------
# 3. Return live Stratum difficulty/mode in /api/status.
# ---------------------------------------------------------------------------
old = 'workers[name]={"accepted":int(pv.get("ok") or pv.get("accepted") or pv.get("shares") or lv.get("accepted") or 0),"rejected":int(pv.get("bad") or pv.get("rejected") or lv.get("rejected") or 0),"difficulty":as_number(pv.get("difficulty") or lv.get("difficulty") or fixed_diff,fixed_diff),"active":True}'
new = 'workers[name]={"accepted":int(pv.get("ok") or pv.get("accepted") or pv.get("shares") or lv.get("accepted") or 0),"rejected":int(pv.get("bad") or pv.get("rejected") or lv.get("rejected") or 0),"difficulty":as_number(lv.get("difficulty") or pv.get("difficulty") or fixed_diff,fixed_diff),"mode":str(lv.get("mode") or pv.get("mode") or ("fixed" if as_number(lv.get("difficulty") or pv.get("difficulty") or fixed_diff,fixed_diff)==fixed_diff else "vardiff")),"active":True}'
if old in text:
    text = text.replace(old, new, 1)
elif '"mode":str(lv.get("mode")' not in text:
    raise RuntimeError("dashboard worker output marker mismatch")

old = '"fixed_difficulty":fixed_diff,"best_share":round_best'
new = '"fixed_difficulty":fixed_diff,"pool_difficulty":pool_difficulty,"vardiff_mode":next((str(w.get("mode") or "fixed") for w in workers.values() if w.get("active")),"fixed")=="vardiff","stratum_difficulty":next((as_number(w.get("difficulty")) for w in workers.values() if w.get("active")),fixed_diff),"stratum_mode":next((str(w.get("mode") or "fixed") for w in workers.values() if w.get("active")),"fixed"),"best_share":round_best'
if old in text:
    text = text.replace(old, new, 1)
elif '"pool_difficulty":pool_difficulty' not in text:
    raise RuntimeError("dashboard mining output marker mismatch")

# ---------------------------------------------------------------------------
# 4. Real node uptime, measured from the fixedcoind process.
# ---------------------------------------------------------------------------
uptime_helper = '''\n\ndef node_uptime_seconds():\n    try:\n        hz = os.sysconf(os.sysconf_names["SC_CLK_TCK"])\n        now_ticks = time.clock_gettime(time.CLOCK_MONOTONIC) * hz\n        for pid in Path("/proc").iterdir():\n            if not pid.name.isdigit():\n                continue\n            try:\n                if (pid / "comm").read_text(errors="ignore").strip() != "fixedcoind":\n                    continue\n                fields = (pid / "stat").read_text().split()\n                return max(0.0, (now_ticks - float(fields[21])) / hz)\n            except (OSError, ValueError, IndexError):\n                continue\n    except (OSError, ValueError, KeyError):\n        pass\n    return 0.0\n'''
if 'def node_uptime_seconds()' not in text:
    marker = '\n\ndef status():'
    if marker not in text:
        raise RuntimeError("dashboard status marker mismatch")
    text = text.replace(marker, uptime_helper + marker, 1)

old = '"history_diff":DIFF_HISTORY,"payout":pool.get("payout_address","")'
new = '"history_diff":DIFF_HISTORY,"uptime_seconds":node_uptime_seconds(),"payout":pool.get("payout_address","")'
if old in text:
    text = text.replace(old, new, 1)
elif '"uptime_seconds":node_uptime_seconds()' not in text:
    raise RuntimeError("dashboard uptime output marker mismatch")

APP.write_text(text)

# v4 is the active dashboard. Do not require obsolete v3 card markers here.
print("patched dashboard backend: Core difficulty authoritative; pool difficulty defined; live Stratum difficulty/mode and node uptime exposed")
