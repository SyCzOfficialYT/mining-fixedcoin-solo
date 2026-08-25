#!/usr/bin/env python3
"""Apply wallet-balance semantics while leaving the repository-owned final HUD intact.

This patch is intentionally idempotent.  The dashboard pipeline contains several
successive repair patches, so this script must tolerate both the older compact
wallet_state() return and the already-normalized implementation produced by the
current dashboard backend.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
APP = Path('/app/monitor/app.py')
html = HTML.read_text()
app_text = APP.read_text()

# The final reference template may have helper classes on the root dashboard
# element (e.g. `class="dashboard reference-dashboard"`). Treat the marker as
# a class token instead of requiring an exact class attribute.
if not re.search(r'class="[^\"]*\breference-dashboard\b[^\"]*"', html):
    raise RuntimeError('dashboard balance/activity patch: expected repository-owned reference template')

# Current wallet_state() already exposes the canonical four buckets directly:
#   confirmed   = trusted wallet balance
#   pending     = untrusted pending wallet balance
#   immature    = immature coinbase balance
#   total       = confirmed + pending + immature
# Do not rewrite an implementation which already has those semantics.
canonical_total = re.search(
    r'(?m)^\s*total\s*=\s*confirmed\s*\+\s*unconfirmed\s*\+\s*immature\s*$',
    app_text,
)
canonical_return = re.search(
    r'(?m)^\s*return\s*\{\s*"confirmed"\s*:\s*confirmed\s*,\s*'
    r'"pending"\s*:\s*unconfirmed\s*,\s*"immature"\s*:\s*immature\s*,\s*'
    r'"unconfirmed"\s*:\s*unconfirmed\s*,\s*"total"\s*:\s*total\s*,',
    app_text,
)

if canonical_total and canonical_return:
    print('dashboard balance/activity: wallet balance semantics already normalized')
    print('dashboard balance/activity: final reference DOM retained; wallet semantics normalized')
    raise SystemExit(0)

# Older compact representation used rpc_pending + immature for the public
# unconfirmed field. Replace only that exact wallet_state return expression.
old_return = (
    'return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,'
    '"unconfirmed":rpc_pending+immature,"total":confirmed,"blocks":blocks,'
    '"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}'
)
new_block = '''total=confirmed+unconfirmed+immature
    return {"confirmed":confirmed,"pending":unconfirmed,"immature":immature,"unconfirmed":unconfirmed,"total":total,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}'''

if old_return in app_text:
    app_text = app_text.replace(old_return, new_block, 1)
    APP.write_text(app_text)
    print('dashboard balance/activity: normalized wallet balance semantics')
    print('dashboard balance/activity: final reference DOM retained; wallet semantics normalized')
    raise SystemExit(0)

# Formatting-tolerant fallback for the same old return expression.
pattern = (
    r'(?m)^\s*return\s*\{\s*"confirmed"\s*:\s*confirmed\s*,\s*'
    r'"pending"\s*:\s*rpc_pending\s*,\s*"immature"\s*:\s*immature\s*,\s*'
    r'"unconfirmed"\s*:\s*rpc_pending\s*\+\s*immature\s*,\s*'
    r'"total"\s*:\s*confirmed\s*,\s*"blocks"\s*:\s*blocks\s*,\s*'
    r'"wallet"\s*:\s*walletinfo\s+or\s+\{\}\s*,\s*'
    r'"error"\s*:\s*balances_error\s+or\s+walletinfo_error\s+or\s+tx_error\s*\}\s*$'
)
app_text, n = re.subn(pattern, new_block, app_text, count=1)
if n != 1:
    raise RuntimeError('missing wallet balance semantics anchor')

APP.write_text(app_text)
print('dashboard balance/activity: normalized wallet balance semantics')
print('dashboard balance/activity: final reference DOM retained; wallet semantics normalized')
