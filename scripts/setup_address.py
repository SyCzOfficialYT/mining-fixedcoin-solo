#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from urllib.parse import quote

import requests
import yaml
from requests.auth import HTTPBasicAuth

CFG = Path('/app/config/config.yaml')
DATADIR = Path(os.getenv('FIX_DATADIR', '/data/fixedcoin'))
WALLETS_DIR = DATADIR / 'wallets'
PAYOUT_FILE = DATADIR / 'payout_address'
RPC_USER = os.getenv('FIX_RPCUSER', 'fixrpc')
RPC_PASS = os.getenv('FIX_RPCPASS', '').strip()
RPC_PORT = int(os.getenv('FIX_RPCPORT', '24761'))
WALLET_NAME = 'mining'


def rpc(method, params=None, wallet=None):
    endpoint = f'http://127.0.0.1:{RPC_PORT}'
    if wallet:
        endpoint += f'/wallet/{quote(wallet, safe="")}'
    response = requests.post(
        endpoint,
        json={'jsonrpc': '1.0', 'id': 'setup', 'method': method, 'params': params or []},
        auth=HTTPBasicAuth(RPC_USER, RPC_PASS),
        timeout=30,
    )
    try:
        data = response.json()
    except ValueError:
        response.raise_for_status()
        raise RuntimeError(f'{method}: RPC returned non-JSON HTTP {response.status_code}')
    return data.get('result'), data.get('error')


def wallet_exists_on_disk():
    wallet_dir = WALLETS_DIR / WALLET_NAME
    return wallet_dir.is_dir() or (WALLETS_DIR / f'{WALLET_NAME}.dat').exists()


def persist_payout(address):
    PAYOUT_FILE.write_text(address.strip() + '\n')
    os.chmod(PAYOUT_FILE, 0o600)


def set_config(cfg, address):
    cfg.setdefault('pool', {})['payout_address'] = address
    CFG.write_text(yaml.safe_dump(cfg, sort_keys=False))


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
        persist_payout(explicit)
        set_config(cfg, explicit)
        print('Payout address configured from environment.')
        return 0

    # The Docker image contains /app/config, but that directory is not a
    # persistent volume. Keep the generated payout address in the daemon
    # datadir so recreating the container never creates a second address.
    if PAYOUT_FILE.is_file():
        saved = PAYOUT_FILE.read_text(errors='ignore').strip()
        if saved and 'CHANGE_ME' not in saved and 'GETNEWADDRESS' not in saved:
            set_config(cfg, saved)
            print(f'Existing payout address restored: {saved}')
            return 0

    current = str(cfg['pool'].get('payout_address', '') or '').strip()
    if current and 'CHANGE_ME' not in current and 'GETNEWADDRESS' not in current:
        persist_payout(current)
        set_config(cfg, current)
        print(f'Existing payout address retained: {current}')
        return 0

    wallets, error = rpc('listwallets')
    if error:
        print(f'ERROR: listwallets failed: {error}', file=sys.stderr)
        return 1

    loaded = WALLET_NAME in (wallets or [])
    if not loaded:
        if wallet_exists_on_disk():
            _, error = rpc('loadwallet', [WALLET_NAME])
            if error and 'already loaded' not in str(error).lower():
                print(f'ERROR: loadwallet failed: {error}', file=sys.stderr)
                return 1
            print('Existing mining wallet loaded.')
        else:
            _, error = rpc('createwallet', [WALLET_NAME])
            if error:
                if 'already exists' in str(error).lower() or wallet_exists_on_disk():
                    _, load_error = rpc('loadwallet', [WALLET_NAME])
                    if load_error and 'already loaded' not in str(load_error).lower():
                        print(f'ERROR: createwallet failed: {error}; loadwallet failed: {load_error}', file=sys.stderr)
                        return 1
                else:
                    print(f'ERROR: createwallet failed: {error}', file=sys.stderr)
                    return 1
            else:
                print('Mining wallet created.')

    address, error = rpc('getnewaddress', ['solo-mining', 'bech32'], wallet=WALLET_NAME)
    if error or not address:
        address, error = rpc('getnewaddress', [], wallet=WALLET_NAME)
    if error or not address:
        print(f'ERROR: could not create payout address: {error}', file=sys.stderr)
        return 1

    persist_payout(address)
    set_config(cfg, address)
    print(f'Generated a new mining payout address: {address}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
