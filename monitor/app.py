#!/usr/bin/env python3
from flask import Flask, jsonify, render_template
from requests.auth import HTTPBasicAuth
from pathlib import Path
import os, json, re, time, requests

ROOT=Path(__file__).resolve().parent.parent
app=Flask(__name__, template_folder='templates', static_folder='static')
DATA=Path('/app/data')
RPC_URL=f"http://127.0.0.1:{os.getenv('FIX_RPCPORT','24761')}"
RPC_AUTH=HTTPBasicAuth(os.getenv('FIX_RPCUSER','fixrpc'), os.getenv('FIX_RPCPASS',''))
PAYOUT=os.getenv('FIX_PAYOUT_ADDRESS','fix1CHANGE_ME')
MATURITY=int(os.getenv('COINBASE_MATURITY','100'))
LOG=DATA/'stratum.log'
EVENTS=DATA/'events.jsonl'


def rpc(method, params=None, timeout=3):
    try:
        r=requests.post(RPC_URL,json={'jsonrpc':'1.0','id':'dashboard','method':method,'params':params or []},auth=RPC_AUTH,timeout=timeout)
        d=r.json()
        return d.get('result'), d.get('error')
    except Exception as e:
        return None,str(e)


def lines(path, n=1500):
    try:return path.read_text(errors='replace').splitlines()[-n:]
    except Exception:return []


def parse_logs():
    accepted=[]; rejected=0; blocks=[]; worker='unknown'; diff=13354
    for line in lines(LOG):
        m=re.search(r'authorize\s+(\S+).*?(?:diff|share_diff)\s*[=:]\s*([0-9.]+)',line,re.I)
        if m: worker=m.group(1); diff=float(m.group(2))
        m=re.search(r'ACCEPT\s+#(\d+)\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)',line,re.I)
        if m:
            n,work,pd,h=m.groups(); accepted.append({'ts':line[:19],'num':int(n),'work':float(work),'pool_diff':float(pd),'hash':h[:16],'worker':worker})
        if re.search(r'\bREJECT\b',line,re.I): rejected+=1
        m=re.search(r'BLOCK ACCEPTED.*?height=(\d+).*?hash=([0-9a-fA-F]{16,64})(?:.*?reward=([0-9.]+))?',line,re.I)
        if m:
            h,b,r=m.groups(); blocks.append({'height':int(h),'hash':b[:16],'reward':float(r or 0),'mature_at':int(h)+MATURITY})
    return accepted[-100:],rejected,blocks[-100:]


def status():
    info,_=rpc('getblockchaininfo')
    net,_=rpc('getnetworkinfo')
    bal,_=rpc('getbalances')
    shares,rejected,blocks=parse_logs()
    height=int((info or {}).get('blocks') or 0)
    network_diff=float((info or {}).get('difficulty') or 0)
    trusted=float(((bal or {}).get('mine') or {}).get('trusted') or 0)
    pending=float(((bal or {}).get('mine') or {}).get('untrusted_pending') or 0)
    immature=float(((bal or {}).get('mine') or {}).get('immature') or 0)
    best=max((x['work'] for x in shares),default=0)
    last=shares[-1]['work'] if shares else 0
    effort=min(100,100*best/network_diff) if network_diff else 0
    span=max(1, time.time()-time.mktime(time.strptime(shares[0]['ts'],'%Y-%m-%d %H:%M:%S'))) if shares else 1
    hashrate=sum(x['pool_diff'] for x in shares)*(2**32)/span if shares else 0
    workers={}
    for x in shares:
        w=workers.setdefault(x['worker'],{'accepted':0,'rejected':0,'difficulty':x['pool_diff']})
        w['accepted']+=1
    if workers and rejected: next(iter(workers.values()))['rejected']=rejected
    return {'node':{'online':bool(info),'synced':bool(info) and not info.get('initialblockdownload',False),'height':height,'headers':int((info or {}).get('headers') or height),'difficulty':network_diff,'connections':int((net or {}).get('connections') or 0)},'mining':{'accepted':len(shares),'rejected':rejected,'reject_pct':round(100*rejected/max(1,len(shares)+rejected),2),'hashrate':hashrate,'fixed_difficulty':13354,'best_share':best,'last_work':last,'effort':round(effort,4),'workers':workers},'wallet':{'confirmed':trusted,'pending':pending,'immature':immature,'total_rewards':sum(x['reward'] for x in blocks)},'blocks':blocks,'payout':PAYOUT,'maturity':MATURITY,'ts':int(time.time())}

@app.get('/')
def index():return render_template('dashboard.html', payout=PAYOUT, maturity=MATURITY)

@app.get('/api/status')
def api_status():return jsonify(status())

@app.get('/api/logs')
def api_logs():
    out=[]
    for line in lines(LOG,180):
        if any(k in line for k in ('ACCEPT','REJECT','BLOCK','ERROR','NEW ROUND','authorize')):
            level='success' if 'ACCEPT' in line or 'BLOCK' in line else 'danger' if 'ERROR' in line else 'warning' if 'REJECT' in line else 'info'
            out.append({'ts':line[:19],'level':level,'message':line[20:].strip() if len(line)>20 else line})
    return jsonify({'events':out[-120:]})

if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.getenv('FIX_DASH_PORT','5050')))
