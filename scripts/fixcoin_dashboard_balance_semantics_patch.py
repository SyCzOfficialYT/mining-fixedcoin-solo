#!/usr/bin/env python3
"""Keep confirmed, unconfirmed and immature wallet balances distinct."""
from pathlib import Path

APP = Path('/app/monitor/app.py')
text = APP.read_text()
old = '''    # "total" intentionally means confirmed wallet balance only.\n    return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":rpc_pending+immature,"total":confirmed,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}\n'''
new = '''    # Keep the four wallet components semantically distinct.\n    # - confirmed: trusted/spendable wallet balance\n    # - unconfirmed: untrusted pending transactions only\n    # - immature: coinbase rewards waiting for maturity\n    # - total: all three components displayed by the dashboard\n    total=confirmed+rpc_pending+immature\n    return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":rpc_pending,"total":total,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}\n'''
if new in text:
    print('dashboard wallet balance semantics already patched')
elif old in text:
    APP.write_text(text.replace(old,new,1))
    print('patched wallet balance semantics: unconfirmed excludes immature; total sums all components')
else:
    raise RuntimeError('missing wallet balance semantics anchor')
