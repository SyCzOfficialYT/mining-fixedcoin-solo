#!/usr/bin/env python3
"""Generate and run the known-good FixedCoin Stratum implementation."""
import ast, os, runpy, sys, urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent; FULL=HERE/'server_full.py'
URL='https://raw.githubusercontent.com/SyCzOfficialYT/freecash-coin/a88d89675b3a41cc6774e1b975e57e050d4892cc/stratum/server.py'
ADAPT_VERSION='fixedcoin-solo-2026-08'

def replace_function(source,name,replacement):
    tree=ast.parse(source); target=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
    if target is None: raise RuntimeError(f'function {name!r} not found in upstream stratum')
    lines=source.splitlines(keepends=True); start=sum(map(len,lines[:target.lineno-1])); end=sum(map(len,lines[:target.end_lineno])); return source[:start]+replacement.rstrip()+'\n'+source[end:]

def adapt(t):
    t=t.replace('job_interval", 20)','job_interval", 30)').replace('blog[-20:]','blog[-1000:]').replace('+ 14400','+ 100').replace(' FCH',' FIX').replace('FreeCash','FixedCoin').replace('/FCH-Solo/','/FIX-Solo/')
    # FixedCoin Core requires BIP145/SegWit GBT negotiation.
    t=t.replace('rpc("getblocktemplate", [{"rules": []}])','rpc("getblocktemplate", [{"rules": ["segwit"]}])')
    if 'getblocktemplate", [{"rules": ["segwit"]}]' not in t: raise RuntimeError('GBT segwit patch failed')
    marker='MAX_DIFF = int(cfg["pool"].get("vardiff_max", 50_000_000))'
    if marker in t:t=t.replace(marker,marker+'\nFIXED_DIFF = int(cfg["pool"].get("fixed_difficulty", 13354))',1)
    # Keep the upstream implementation as the source of truth for transaction construction;
    # only coinbase maturity and branding are changed here.
    t=t.replace('mature_at_height": job["height"] + 14400','mature_at_height": job["height"] + 100')
    return t

def generate():
    print('Fetching known-good Stratum base…',flush=True)
    raw=urllib.request.urlopen(URL,timeout=60).read().decode()
    adapted=adapt(raw); ast.parse(adapted)
    assert 'rules": ["segwit"]' in adapted
    assert 'rules": []' not in adapted
    FULL.write_text(f'# ADAPT_VERSION={ADAPT_VERSION}\n'+adapted)
    print('Generated',FULL,FULL.stat().st_size,'bytes',flush=True)

if os.environ.get('STRATUM_BUILD_ONLY')=='1': generate(); raise SystemExit(0)
if not FULL.exists() or ADAPT_VERSION not in FULL.read_text(errors='ignore'): generate()
sys.argv[0]=str(FULL); runpy.run_path(str(FULL),run_name='__main__')
