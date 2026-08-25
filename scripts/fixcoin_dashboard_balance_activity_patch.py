#!/usr/bin/env python3
"""Apply wallet-balance semantics while leaving the repository-owned final HUD intact."""
from pathlib import Path

HTML=Path('/app/monitor/templates/dashboard_v4.html')
APP=Path('/app/monitor/app.py')
html=HTML.read_text(); app_text=APP.read_text()
if 'class="reference-dashboard"' not in html:
    raise RuntimeError('dashboard balance/activity patch: expected repository-owned reference template')
old='''    # "total" intentionally means confirmed wallet balance only.\n    return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":rpc_pending+immature,"total":confirmed,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}\n'''
new='''    # Dashboard balance semantics:\n    # - confirmed/trusted is the confirmed balance\n    # - total follows confirmed/trusted balance\n    # - unconfirmed follows immature Coinbase balance\n    # - immature is exposed separately using the same underlying value\n    total=confirmed\n    unconfirmed=immature\n    return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":unconfirmed,"total":total,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}\n'''
if new not in app_text:
    if old not in app_text: raise RuntimeError('missing wallet balance semantics anchor')
    app_text=app_text.replace(old,new,1)
    APP.write_text(app_text)
print('dashboard balance/activity: final reference DOM retained; wallet semantics normalized')
