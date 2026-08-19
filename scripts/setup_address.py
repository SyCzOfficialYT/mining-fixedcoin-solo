#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import requests
import yaml
from requests.auth import HTTPBasicAuth

CFG = Path('/app/config/config.yaml')
DATADIR = Path(os.getenv('FIX_DATADIR', '/data/fixedcoin'))
RPC_USER = os.getenv('FIX_RPCUSER', 'fixrpc')
RPC_PASS = os.getenv('FIX_RPCPASS', '').strip()
RPC_PORT = int(os.getenv('FIX_RPCPORT', '24761'))


def rpc(method, params=None):
    response = requests.post(
        f'http://127.0.0.1:{RPC_PORT}',
        json={'jsonrpc': '1.0', 'id': 'setup', 'method': method, 'params': params or []},
        auth=HTTPBasicAuth(RPC_USER, RPC_PASS),
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data.get('result'), data.get('error')


def main():
    cfg = yaml.safe_load(CFG.read_text()) if CFG.exists() else {}
    cfg.setdefault('rpc', {}).update({
        'host': '127.0.0.1',
        'port': RPC_PORT,
        'user': RPC_USER,
        'password': RPC_PASS,
    })
    cfg.setdefault('pool', {})

    explicit = os.getenv('FIX_PAYOUT_ADDRESS', '').strip()
    if explicit:
        cfg['pool']['payout_address'] = explicit
        CFG.write_text(yaml.safe_dump(cfg, sort_keys=False))
        print('Payout address configured from environment.')
        return 0

    current = str(cfg['pool'].get('payout_address', '') or '').strip()
    if current and 'CHANGE_ME' not in current and 'GETNEWADDRESS' not in current:
        CFG.write_text(yaml.safe_dump(cfg, sort_keys=False))
        print('Existing payout address retained.')
        return 0

    wallets, error = rpc('listwallets')
    if error:
        print(f'ERROR: listwallets failed: {error}', file=sys.stderr)
        return 1

    if 'mining' not in (wallets or []):
        _, error = rpc('createwallet', ['mining'])
        if error and 'already exists' not in str(error).lower():
            print(f'ERROR: createwallet failed: {error}', file=sys.stderr)
            return 1

    address, error = rpc('getnewaddress', ['solo-mining', 'bech32'])
    if error or not address:
        # Some FixedCoin builds may not accept the optional label/type parameters.
        address, error = rpc('getnewaddress', [])

    if error or not address:
        print(f'ERROR: could not create payout address: {error}', file=sys.stderr)
        return 1

    cfg['pool']['payout_address'] = address
    CFG.write_text(yaml.safe_dump(cfg, sort_keys=False))
    print('Generated a new mining payout address.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
