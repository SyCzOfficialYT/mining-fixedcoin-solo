#!/usr/bin/env python3
import os, subprocess, sys, requests, yaml
from requests.auth import HTTPBasicAuth
from pathlib import Path
CFG=Path('/app/config/config.yaml')
RPC_USER=os.getenv('FIX_RPCUSER','fixrpc'); RPC_PASS=os.getenv('FIX_RPCPASS','change-me'); RPC_PORT=int(os.getenv('FIX_RPCPORT','24761'))

def rpc(method,params=None):
    r=requests.post(f'http://127.0.0.1:{RPC_PORT}',json={'jsonrpc':'1.0','id':'setup','method':method,'params':params or []},auth=HTTPBasicAuth(RPC_USER,RPC_PASS),timeout=30); d=r.json(); return d.get('result'),d.get('error')

def main():
    cfg=yaml.safe_load(CFG.read_text()) if CFG.exists() else {}
    cfg.setdefault('rpc',{}).update({'host':'127.0.0.1','port':RPC_PORT,'user':RPC_USER,'password':RPC_PASS})
    cfg.setdefault('pool',{})
    explicit=os.getenv('FIX_PAYOUT_ADDRESS','').strip()
    if explicit: cfg['pool']['payout_address']=explicit
    addr=cfg['pool'].get('payout_address','')
    if addr and 'CHANGE_ME' not in addr and 'GETNEWADDRESS' not in addr:
        CFG.write_text(yaml.safe_dump(cfg,sort_keys=False)); print('Payout address:',addr); return 0
    wallets,_=rpc('listwallets')
    if 'mining' not in (wallets or []): rpc('createwallet',['mining'])
    addr,_=rpc('getnewaddress',[])
    if not addr:
        print('WARNING: could not create payout address'); return 0
    cfg['pool']['payout_address']=addr; CFG.write_text(yaml.safe_dump(cfg,sort_keys=False)); print('Generated payout address:',addr); return 0
if __name__=='__main__':sys.exit(main())
