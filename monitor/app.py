#!/usr/bin/env python3
from flask import Flask, jsonify, render_template
from requests.auth import HTTPBasicAuth
from pathlib import Path
from datetime import datetime
import os, re, time, requests

app=Flask(__name__,template_folder='templates',static_folder='static')
DATA=Path('/app/data'); CFG=Path('/app/config/config.yaml')
RPC_URL=f"http://127.0.0.1:{os.getenv('FIX_RPCPORT','24761')}"; RPC_AUTH=HTTPBasicAuth(os.getenv('FIX_RPCUSER','fixrpc'),os.getenv('FIX_RPCPASS',''))
MATURITY=int(os.getenv('COINBASE_MATURITY','100')); LOG=DATA/'stratum.log'; DIFF_HISTORY=[]

def config():
    try:
        import yaml; c=yaml.safe_load(CFG.read_text()) or {}; return c.get('pool',{})
    except Exception:return {}

def rpc(method,params=None,timeout=3):
    try:
        d=requests.post(RPC_URL,json={'jsonrpc':'1.0','id':'dashboard','method':method,'params':params or []},auth=RPC_AUTH,timeout=timeout).json(); return d.get('result'),d.get('error')
    except Exception as e:return None,str(e)

def lines(path,n=1500):
    try:return path.read_text(errors='replace').splitlines()[-n:]
    except Exception:return []

def parse_ts(s):
    try:return datetime.strptime(s[:19],'%Y-%m-%d %H:%M:%S').timestamp()
    except Exception:return 0.0

def parse_logs():
    accepted=[]; rejected=0; blocks=[]; worker='unknown'; job={}
    for line in lines(LOG):
        m=re.search(r'authorize\s+(\S+).*?(?:diff|share_diff)\s*[=:]\s*([0-9.]+)',line,re.I)
        if m:worker=m.group(1)
        m=re.search(r'Job\s+id=([^\s]+).*?(?:height=)?(\d+).*?(?:net_diff|network_diff)[≈:=~]?\s*([0-9.eE+-]+)',line,re.I)
        if m:job={'job_id':m.group(1),'height':int(m.group(2)),'network_diff':float(m.group(3))}
        m=re.search(r'ACCEPT\s+#(\d+)\s+work=([0-9.]+).*?(?:pool|pool_diff)=([0-9.]+).*?hash=([0-9a-fA-F]+)',line,re.I)
        if m:
            n,work,pd,h=m.groups();accepted.append({'ts':line[:19],'epoch':parse_ts(line),'num':int(n),'work':float(work),'pool_diff':float(pd),'hash':h[:16],'worker':worker})
        if re.search(r'\bREJECT\b',line,re.I):rejected+=1
        m=re.search(r'BLOCK ACCEPTED.*?height=(\d+).*?hash=([0-9a-fA-F]{16,64})(?:.*?reward=([0-9.]+))?',line,re.I)
        if m:
            h,b,r=m.groups();blocks.append({'height':int(h),'hash':b[:16],'reward':float(r or 0),'mature_at':int(h)+MATURITY})
    return accepted[-100:],rejected,blocks[-100:],job

def hashrate(shares,window):
    now=time.time(); recent=[x for x in shares if x.get('epoch',0) and now-x['epoch']<=window]
    if not recent:return 0.0
    # Each accepted share represents difficulty work. Convert summed share-difficulty
    # to hashes over the actual rolling window, matching the pool's standard estimator.
    return sum(x['work'] for x in recent)*(2**32)/window

def status():
    info,_=rpc('getblockchaininfo'); net,_=rpc('getnetworkinfo'); mininginfo,_=rpc('getmininginfo'); bal,_=rpc('getbalances')
    shares,rejected,blocks,job=parse_logs(); pool=config(); height=int((info or {}).get('blocks') or 0); network_diff=float((info or {}).get('difficulty') or job.get('network_diff') or 0); mine=(bal or {}).get('mine') or {}
    trusted=float(mine.get('trusted') or 0); pending=float(mine.get('untrusted_pending') or 0); immature=float(mine.get('immature') or 0); best=max((x['work'] for x in shares),default=0); last=shares[-1]['work'] if shares else 0; effort=min(100,100*best/network_diff) if network_diff else 0
    h5=hashrate(shares,300); h1=hashrate(shares,3600); net_hash=float((mininginfo or {}).get('networkhashps') or 0); competition=(h5/net_hash*100) if net_hash else 0
    if network_diff: DIFF_HISTORY.append({'ts':int(time.time()),'height':height,'difficulty':network_diff})
    cutoff=time.time()-86400; DIFF_HISTORY[:]=[x for x in DIFF_HISTORY if x['ts']>=cutoff][-120:]
    workers={}
    for x in shares:
        w=workers.setdefault(x['worker'],{'accepted':0,'rejected':0,'difficulty':x['pool_diff']});w['accepted']+=1
    if workers and rejected:next(iter(workers.values()))['rejected']=rejected
    return {'node':{'online':bool(info),'synced':bool(info) and not info.get('initialblockdownload',False),'height':height,'headers':int((info or {}).get('headers') or height),'difficulty':network_diff,'connections':int((net or {}).get('connections') or 0),'network_hashrate':net_hash},'competition':{'your_hashrate':h5,'network_hashrate':net_hash,'your_network_pct':competition,'network_share_ppm':competition*10000},'mining':{'accepted':len(shares),'rejected':rejected,'reject_pct':round(100*rejected/max(1,len(shares)+rejected),2),'hashrate':h5,'hashrate_1h':h1,'fixed_difficulty':float(pool.get('fixed_difficulty',13354)),'best_share':best,'last_work':last,'effort':round(effort,6),'workers':workers},'wallet':{'confirmed':trusted,'pending':pending,'immature':immature,'total_rewards':sum(x['reward'] for x in blocks)},'blocks':blocks,'shares':shares,'job':job,'history_diff':DIFF_HISTORY,'payout':pool.get('payout_address',''),'maturity':MATURITY,'ts':int(time.time())}

@app.get('/')
def index():return render_template('dashboard.html',payout=config().get('payout_address',''),maturity=MATURITY)
@app.get('/api/status')
def api_status():return jsonify(status())
@app.get('/api/logs')
def api_logs():
    out=[]
    for line in lines(LOG,180):
        if any(k in line for k in ('ACCEPT','REJECT','BLOCK','ERROR','NEW ROUND','authorize','Job id=')):
            level='success' if 'ACCEPT' in line or 'BLOCK' in line else 'danger' if 'ERROR' in line else 'warning' if 'REJECT' in line else 'info';out.append({'ts':line[:19],'level':level,'message':line[20:].strip() if len(line)>20 else line})
    return jsonify({'events':out[-120:]})
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.getenv('FIX_DASH_PORT','5050')),threaded=True)
