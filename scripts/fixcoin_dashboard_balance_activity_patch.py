#!/usr/bin/env python3
"""Restore the four wallet balance metrics and live Recent Activity UI."""
from pathlib import Path

HTML = Path('/app/monitor/templates/dashboard_v4.html')
APP = Path('/app/monitor/app.py')
text = HTML.read_text()
changed = False


def once(old, new, label):
    global text, changed
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f'missing dashboard balance/activity anchor: {label}')
    text = text.replace(old, new, 1)
    changed = True
    print(label)

# Keep API semantics aligned with the dashboard's intended four values.
# Total follows confirmed/trusted balance.
# The dashboard's UNCONFIRMED card follows the immature Coinbase balance.
# IMMATURE remains exposed separately as the same underlying immature value.
app_text = APP.read_text()
old_semantics = '''    # "total" intentionally means confirmed wallet balance only.\n    return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":rpc_pending+immature,"total":confirmed,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}\n'''
new_semantics = '''    # Dashboard balance semantics:\n    # - confirmed: trusted wallet balance\n    # - total: follows confirmed/trusted balance\n    # - unconfirmed: follows immature Coinbase balance for the dashboard card\n    # - immature: the same underlying immature Coinbase balance, exposed separately\n    total=confirmed\n    unconfirmed=immature\n    return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,"unconfirmed":unconfirmed,"total":total,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}\n'''
if new_semantics not in app_text:
    if old_semantics not in app_text:
        raise RuntimeError('missing wallet balance semantics anchor')
    APP.write_text(app_text.replace(old_semantics, new_semantics, 1))
    print('patched wallet balance semantics: total follows confirmed; unconfirmed follows immature')
else:
    print('wallet balance semantics already patched')

# The forge motion stylesheet has already advanced through several dashboard
# iterations. Do not hard-code an obsolete version here: find the current
# forge-motion link and append the balance/activity stylesheet after it.
forge_motion_marker = '<link rel="stylesheet" href="/static/dashboard_v4_forge_motion.css?v='
forge_motion_start = text.find(forge_motion_marker)
if '/static/dashboard_v4_balance_activity.css?' not in text:
    if forge_motion_start < 0:
        raise RuntimeError('missing dashboard balance/activity stylesheet anchor: forge motion stylesheet')
    forge_motion_end = text.find('">', forge_motion_start)
    if forge_motion_end < 0:
        raise RuntimeError('missing dashboard balance/activity stylesheet anchor: malformed forge motion link')
    forge_motion_end += 2
    text = text[:forge_motion_end] + '<link rel="stylesheet" href="/static/dashboard_v4_balance_activity.css?v=20260823-2">' + text[forge_motion_end:]
    changed = True
    print('patched dashboard balance/activity stylesheet')

old_balance = '<div class="stat panel"><span>INVALID SHARES</span><strong class="red" id="invalidShares">0</strong><small id="invalidPct">0.0%</small></div>'
new_balance = old_balance + (
    '<div class="stat panel balance-stat balance-confirmed"><span>CONFIRMED BALANCE</span>'
    '<strong id="balanceConfirmed">—</strong><small>confirmed / trusted</small></div>'
    '<div class="stat panel balance-stat balance-unconfirmed"><span>UNCONFIRMED BALANCE</span>'
    '<strong id="balanceUnconfirmed">—</strong><small>follows immature balance</small></div>'
    '<div class="stat panel balance-stat balance-immature"><span>IMMATURE BALANCE</span>'
    '<strong id="balanceImmature">—</strong><small>coinbase maturity</small></div>'
    '<div class="stat panel balance-stat balance-total"><span>TOTAL BALANCE</span>'
    '<strong id="balanceTotal">—</strong><small>follows confirmed balance</small></div>'
)
once(old_balance, new_balance, 'restored confirmed/unconfirmed/immature/total balance cards')

once(
    '<script defer src="/static/dashboard_v4_forge.js?v=20260823-2"></script>',
    '<script defer src="/static/dashboard_v4_forge.js?v=20260823-2"></script><script defer src="/static/dashboard_v4_balance_activity.js?v=20260823-2"></script>',
    'patched dashboard realtime balance/activity client'
)

if changed:
    HTML.write_text(text)
print('dashboard balance/activity repair complete')
