#!/usr/bin/env python3
"""Keep dashboard network difficulty authoritative and expose live Stratum difficulty/mode."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "monitor" / "app.py"
HTML = ROOT / "monitor" / "templates" / "dashboard_v3.html"
JS = ROOT / "monitor" / "static" / "dashboard.js"

text = APP.read_text()

# The dashboard source is intentionally kept compact. Match the RPC assignment
# semantically instead of depending on one exact whitespace/formatting layout.
rpc_pattern = re.compile(
    r'(?P<prefix>info,info_error=rpc\("getblockchaininfo"\);\s*'
    r'net,_=rpc\("getnetworkinfo"\);\s*'
    r'mininginfo,_=rpc\("getmininginfo"\);\s*)'
    r'(?P<tail>info=info or \{\};\s*net=net or \{\};\s*mininginfo=mininginfo or \{\})'
)

if 'core_diff,_=rpc("getdifficulty")' not in text:
    match = rpc_pattern.search(text)
    if not match:
        raise RuntimeError("dashboard RPC marker mismatch: could not locate status RPC block")
    replacement = f'{match.group("prefix")}core_diff,_=rpc("getdifficulty"); {match.group("tail")}'
    text = text[:match.start()] + replacement + text[match.end():]

# IMPORTANT: consume the complete as_number(...) expression, including both
# closing parentheses. The previous patch consumed only get(...), leaving an
# extra ')' in generated app.py and breaking Docker's py_compile step.
network_pattern = re.compile(
    r'network_diff=as_number\(stats\.get\("network_diff"\)\)\s*or\s*'
    r'as_number\(log_job\.get\("network_diff"\)\)\s*or\s*'
    r'as_number\(mininginfo\.get\("difficulty"\)\)'
)
replacement = 'network_diff=as_number(core_diff) or as_number(mininginfo.get("difficulty")) or as_number(stats.get("network_diff")) or as_number(log_job.get("network_diff"))'
if network_pattern.search(text):
    text = network_pattern.sub(replacement, text, count=1)
elif 'network_diff=as_number(core_diff)' not in text:
    raise RuntimeError("dashboard difficulty marker mismatch: could not locate network_diff assignment")

# Track the actual live Stratum state from authorize/VARDIFF log events. This
# deliberately does not derive the UI from the configured fixed_difficulty: in
# VarDiff mode the current pool difficulty changes at runtime.
worker_anchor = 'm=re.search(r"authorize\\s+(\\S+).*?(?:diff|share_diff)\\s*[=:]\\s*([0-9.]+)",line,re.I)'
if 'mode="fixed" if "mode=fixed"' not in text:
    old = worker_anchor
    new = old + '\n        m2=re.search(r"authorize\\s+(\\S+).*?diff=([0-9.]+).*?mode=(fixed|vardiff(?:=True)?)",line,re.I)\n        if m2:\n            name,diff,mode=m2.groups(); w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(diff),"mode":"fixed"}); w["difficulty"]=float(diff); w["mode"]="fixed" if mode.lower()=="fixed" else "vardiff"; w["last_seen"]=ts; current_worker=name'
    if old not in text:
        raise RuntimeError("dashboard worker authorize marker mismatch")
    text = text.replace(old, new, 1)

vardiff_marker = 'm=re.search(r"NEW ROUND\\s+height=(\\d+)\\s+netdiff=([0-9.eE+-]+)",line,re.I)'
if 'm=re.search(r"VARDIFF\\s+(\\S+)\\s+([0-9.]+)→' not in text:
    insert = 'm=re.search(r"VARDIFF\\s+(\\S+)\\s+([0-9.]+)→([0-9.]+)",line,re.I)\n        if m:\n            name,prev_diff,new_diff=m.groups(); w=workers.setdefault(name,{"accepted":0,"rejected":0,"difficulty":float(new_diff),"mode":"vardiff"}); w["difficulty"]=float(new_diff); w["mode"]="vardiff"; w["last_seen"]=ts; current_worker=name\n        ' + vardiff_marker
    if vardiff_marker not in text:
        raise RuntimeError("dashboard round marker mismatch")
    text = text.replace(vardiff_marker, insert, 1)

# Ensure workers returned by status carry mode and current live difficulty.
old_worker = 'workers[name]={"accepted":int(pv.get("ok") or pv.get("accepted") or pv.get("shares") or lv.get("accepted") or 0),"rejected":int(pv.get("bad") or pv.get("rejected") or lv.get("rejected") or 0),"difficulty":as_number(pv.get("difficulty") or lv.get("difficulty") or fixed_diff,fixed_diff),"active":True}'
new_worker = 'workers[name]={"accepted":int(pv.get("ok") or pv.get("accepted") or pv.get("shares") or lv.get("accepted") or 0),"rejected":int(pv.get("bad") or pv.get("rejected") or lv.get("rejected") or 0),"difficulty":as_number(lv.get("difficulty") or pv.get("difficulty") or fixed_diff,fixed_diff),"mode":str(lv.get("mode") or pv.get("mode") or ("fixed" if as_number(pv.get("difficulty") or lv.get("difficulty") or fixed_diff,fixed_diff)==fixed_diff else "vardiff")),"active":True}'
if old_worker in text:
    text = text.replace(old_worker, new_worker, 1)
elif '"mode":str(lv.get("mode")' not in text:
    raise RuntimeError("dashboard worker output marker mismatch")

# Add a compact mining-level representation used by the dashboard card.
old_mining = '"fixed_difficulty":fixed_diff,"best_share":round_best'
new_mining = '"fixed_difficulty":fixed_diff,"stratum_difficulty":next((as_number(w.get("difficulty")) for w in workers.values() if w.get("active")),fixed_diff),"stratum_mode":next((str(w.get("mode") or "fixed") for w in workers.values() if w.get("active")),"fixed"),"best_share":round_best'
if old_mining in text and '"stratum_difficulty":next(' not in text:
    text = text.replace(old_mining, new_mining, 1)
elif '"stratum_difficulty":next(' not in text:
    raise RuntimeError("dashboard mining output marker mismatch")

APP.write_text(text)

# Dashboard card: always show the live Stratum difficulty and its actual mode.
html = HTML.read_text()
old_card = '<div class="card metric"><span class="metric-dot cyan-dot"></span><div class="eyebrow">Share Difficulty</div><div class="metric-value cyan" id="shareDiff">—</div><div class="metric-sub">fixed Stratum target</div><span class="fixed-pill">Fixed</span></div>'
new_card = '<div class="card metric"><span class="metric-dot cyan-dot"></span><div class="eyebrow">Share Difficulty</div><div class="metric-value cyan" id="shareDiff">—</div><div class="metric-sub" id="shareDiffSub">Fixed Stratum target</div><span class="fixed-pill" id="shareDiffMode">Fixed</span></div>'
if old_card in html:
    html = html.replace(old_card, new_card, 1)
elif 'id="shareDiffMode"' not in html:
    raise RuntimeError("dashboard Share Difficulty card marker mismatch")
HTML.write_text(html)

js = JS.read_text()
old_js = "set('shareDiff',compact(m.fixed_difficulty));"
new_js = "const stratumDiff=n(m.stratum_difficulty||m.fixed_difficulty);const stratumMode=String(m.stratum_mode||'fixed').toLowerCase()==='vardiff'?'VarDiff':'Fixed';set('shareDiff',compact(stratumDiff));set('shareDiffSub',`${stratumMode} Stratum target`);set('shareDiffMode',stratumMode);"
if old_js in js:
    js = js.replace(old_js, new_js, 1)
elif 'const stratumDiff=n(m.stratum_difficulty||m.fixed_difficulty);' not in js:
    raise RuntimeError("dashboard Share Difficulty JS marker mismatch")
JS.write_text(js)

# Self-checks so Docker fails at build time instead of shipping a stale UI.
if 'core_diff,_=rpc("getdifficulty")' not in text:
    raise RuntimeError("getdifficulty RPC missing")
if 'network_diff=as_number(core_diff)' not in text:
    raise RuntimeError("Core difficulty is not authoritative")
if '"stratum_difficulty":next(' not in text or '"stratum_mode":next(' not in text:
    raise RuntimeError("live Stratum state is not exposed")
if 'id="shareDiffMode"' not in html or 'id="shareDiffSub"' not in html:
    raise RuntimeError("Share Difficulty mode UI missing")
if 'const stratumDiff=n(m.stratum_difficulty||m.fixed_difficulty);' not in js:
    raise RuntimeError("Share Difficulty rendering missing")

print("patched dashboard: Core network difficulty authoritative; live Stratum Fixed/VarDiff state exposed")