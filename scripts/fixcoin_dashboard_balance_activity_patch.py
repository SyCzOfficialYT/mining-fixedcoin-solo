#!/usr/bin/env python3
"""Apply wallet-balance semantics while leaving the repository-owned final HUD intact."""
from pathlib import Path
import re

HTML=Path('/app/monitor/templates/dashboard_v4.html')
APP=Path('/app/monitor/app.py')
html=HTML.read_text(); app_text=APP.read_text()

# The final reference template may have helper classes on the root dashboard
# element (e.g. `class="dashboard reference-dashboard"`). Treat the marker as
# a class token instead of requiring an exact class attribute.
if not re.search(r'class="[^\"]*\breference-dashboard\b[^\"]*"', html):
    raise RuntimeError('dashboard balance/activity patch: expected repository-owned reference template')

# wallet_state() has intentionally been kept compact by earlier dashboard
# patches, so do not depend on one exact multiline source representation.
# Replace only the authoritative return expression and make the semantics
# explicit and idempotent:
#   confirmed  = trusted wallet balance
#   total      = confirmed
#   unconfirmed= immature Coinbase balance
#   immature   = same immature Coinbase balance
old_return='return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":rpc_pending+immature,"total":confirmed,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}'
new_block='''total=confirmed
    unconfirmed=immature
    return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":unconfirmed,"total":total,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}'''

if 'unconfirmed=immature' not in app_text:
    if old_return in app_text:
        app_text=app_text.replace(old_return,new_block,1)
    else:
        # Fallback for formatting changes: target the wallet_state return by
        # its stable field sequence, without touching unrelated API returns.
        pattern=r'(?m)^\s*return \{"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":rpc_pending\+immature,"total":confirmed,"blocks":blocks,"wallet":walletinfo or \{\},"error":balances_error or walletinfo_error or tx_error\}\s*$'
        app_text,n=re.subn(pattern,new_block,app_text,count=1)
        if n != 1:
            raise RuntimeError('missing wallet balance semantics anchor')
    APP.write_text(app_text)
    print('dashboard balance/activity: normalized wallet balance semantics')
else:
    print('dashboard balance/activity: wallet balance semantics already normalized')

print('dashboard balance/activity: final reference DOM retained; wallet semantics normalized')
