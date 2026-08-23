#!/usr/bin/env python3
"""Wire AxeOS /api/system/info hashrate into the dashboard status payload."""
from pathlib import Path

APP = Path("/app/monitor/app.py")
JS = Path("/app/monitor/static/dashboard_v4.js")
text = APP.read_text()

if "AXEOS_URL" not in text:
    needle = 'WORKER_ACTIVE_SECONDS = int(os.getenv("WORKER_ACTIVE_SECONDS", "180"))'
    if needle not in text:
        raise SystemExit("WORKER_ACTIVE_SECONDS anchor missing")
    text = text.replace(
        needle,
        needle + '\nAXEOS_URL = os.getenv("AXEOS_URL", "http://192.168.50.133").rstrip("/")',
        1,
    )

AXE_FN = '''
def fetch_axeos_hashrate_hs():
    """AxeOS /api/system/info → hashRate is GH/s; return H/s or None."""
    try:
        r = requests.get(f"{AXEOS_URL}/api/system/info", timeout=2.0)
        r.raise_for_status()
        data = r.json() if r.content else {}
        ghs = data.get("hashRate_1m")
        if ghs is None:
            ghs = data.get("hashRate")
        if ghs is None:
            ghs = data.get("hashRate_10m")
        ghs = float(ghs or 0)
        if ghs <= 0:
            return None
        return ghs * 1e9  # GH/s → H/s
    except Exception:
        return None

'''

if "def fetch_axeos_hashrate_hs" not in text:
    anchor = (
        "def hashrate(shares,window):\n"
        "    now=time.time(); recent=[x for x in shares if x.get(\"epoch\") and 0<=now-x[\"epoch\"]<=window and float(x.get(\"work\") or 0)>0]\n"
        "    return sum(float(x.get(\"work\") or 0)*(2**32) for x in recent)/float(window) if recent else 0.0\n"
    )
    if anchor not in text:
        raise SystemExit("hashrate() anchor missing")
    text = text.replace(anchor, anchor + AXE_FN, 1)

old_h = "h5=hashrate(shares,300); h1=hashrate(shares,3600); network_hashrate=as_number(mininginfo.get(\"networkhashps\"))"
new_h = (
    "h5_shares=hashrate(shares,300); h1=hashrate(shares,3600); "
    "axe_hs=fetch_axeos_hashrate_hs(); "
    "h5=(axe_hs if (axe_hs is not None and axe_hs>0) else h5_shares); "
    "hashrate_source=(\"axeos\" if (axe_hs is not None and axe_hs>0) else \"shares\"); "
    "network_hashrate=as_number(mininginfo.get(\"networkhashps\"))"
)
if "axe_hs=fetch_axeos_hashrate_hs" not in text:
    if old_h not in text:
        raise SystemExit("h5=hashrate anchor missing")
    text = text.replace(old_h, new_h, 1)

if '"hashrate_source"' not in text:
    text = text.replace(
        '"hashrate_5m":h5,"hashrate_1h":h1,',
        '"hashrate_5m":h5,"hashrate_1h":h1,"hashrate_source":hashrate_source,',
        1,
    )

APP.write_text(text)
compile(text, str(APP), "exec")
print("axeos hashrate patch applied →", APP)

# Dashboard label: AXEOS LIVE vs 5M WINDOW
if JS.exists():
    js = JS.read_text()
    needle = "$('forgeHashrate').textContent=hashRate(m.hashrate_5m);"
    repl = (
        "$('forgeHashrate').textContent=hashRate(m.hashrate_5m);"
        "{const lab=document.querySelector('.hashrate-card small');"
        "if(lab)lab.textContent=m.hashrate_source==='axeos'?'AXEOS LIVE':'5M WINDOW';}"
    )
    if "AXEOS LIVE" not in js:
        if needle not in js:
            raise SystemExit("forgeHashrate JS anchor missing")
        js = js.replace(needle, repl, 1)
        JS.write_text(js)
        print("dashboard JS hashrate label patched")
    else:
        print("dashboard JS already has AXEOS LIVE label")
