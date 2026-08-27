#!/usr/bin/env python3
"""Apply canonical wallet-balance semantics without breaking the final dashboard.

This patch is deliberately idempotent.  The dashboard pipeline contains many
ordered repair passes and some of those passes can rewrite/compact app.py before
this script runs.  If wallet_state() is already semantically correct, success is
the correct result regardless of formatting.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
APP = Path('/app/monitor/app.py')
html = HTML.read_text(encoding='utf-8')
app_text = APP.read_text(encoding='utf-8')

# The final reference template may have helper classes on the root element.
if not re.search(r'class="[^"]*\breference-dashboard\b[^"]*"', html):
    raise RuntimeError('dashboard balance/activity patch: expected repository-owned reference template')

# ---------------------------------------------------------------------------
# Canonical state: do not care how the surrounding Python was formatted.
# ---------------------------------------------------------------------------
# wallet_state() must expose:
#   confirmed = trusted wallet balance
#   pending   = untrusted pending wallet balance
#   immature  = immature coinbase balance
#   total     = confirmed + pending + immature
# Accept either a separate total assignment or an equivalent return expression.
canonical_total = bool(re.search(
    r'(?s)def\s+wallet_state\s*\([^)]*\):.*?\btotal\s*=\s*confirmed\s*\+\s*unconfirmed\s*\+\s*immature\b',
    app_text,
))
canonical_return = bool(re.search(
    r'(?s)def\s+wallet_state\s*\([^)]*\):.*?\breturn\s*\{[^\n]*'
    r'"confirmed"\s*:\s*confirmed[^\n]*'
    r'"pending"\s*:\s*unconfirmed[^\n]*'
    r'"immature"\s*:\s*immature[^\n]*'
    r'"unconfirmed"\s*:\s*unconfirmed[^\n]*'
    r'"total"\s*:\s*total\b',
    app_text,
))

if canonical_total and canonical_return:
    print('dashboard balance/activity: wallet balance semantics already normalized')
    print('dashboard balance/activity: final reference DOM retained; wallet semantics normalized')
    raise SystemExit(0)

# ---------------------------------------------------------------------------
# Legacy compact representation.
# ---------------------------------------------------------------------------
old_return = (
    'return {"confirmed":confirmed,"pending":rpc_pending,"immature":immature,'
    '"unconfirmed":rpc_pending+immature,"total":confirmed,"blocks":blocks,'
    '"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}'
)
new_block = '''total=confirmed+unconfirmed+immature
    return {"confirmed":confirmed,"pending":unconfirmed,"immature":immature,"unconfirmed":unconfirmed,"total":total,"blocks":blocks,"wallet":walletinfo or {},"error":balances_error or walletinfo_error or tx_error}'''

if old_return in app_text:
    app_text = app_text.replace(old_return, new_block, 1)
    APP.write_text(app_text, encoding='utf-8')
    print('dashboard balance/activity: normalized wallet balance semantics')
    print('dashboard balance/activity: final reference DOM retained; wallet semantics normalized')
    raise SystemExit(0)

# Formatting-tolerant fallback for the same legacy representation.  Do not
# require the whole function to be one exact line; patch only the return value.
pattern = (
    r'(?m)^(\s*)return\s*\{\s*"confirmed"\s*:\s*confirmed\s*,\s*'
    r'"pending"\s*:\s*rpc_pending\s*,\s*"immature"\s*:\s*immature\s*,\s*'
    r'"unconfirmed"\s*:\s*rpc_pending\s*\+\s*immature\s*,\s*'
    r'"total"\s*:\s*confirmed\s*,\s*"blocks"\s*:\s*blocks\s*,\s*'
    r'"wallet"\s*:\s*walletinfo\s+or\s+\{\}\s*,\s*'
    r'"error"\s*:\s*balances_error\s+or\s+walletinfo_error\s+or\s+tx_error\s*\}\s*$'
)
app_text, n = re.subn(pattern, lambda m: m.group(1) + new_block.lstrip(), app_text, count=1)
if n != 1:
    # A prior patch may already have normalized the semantics in an equivalent
    # shape.  Treat that as success rather than making the entire Docker build
    # hostage to whitespace/statement layout.
    semantic_old = bool(re.search(
        r'"confirmed"\s*:\s*confirmed.*?"pending"\s*:\s*unconfirmed.*?'
        r'"immature"\s*:\s*immature.*?"unconfirmed"\s*:\s*unconfirmed.*?'
        r'"total"\s*:\s*(?:total|confirmed\s*\+\s*unconfirmed\s*\+\s*immature)',
        app_text,
        re.S,
    ))
    if semantic_old:
        print('dashboard balance/activity: equivalent canonical wallet semantics already present')
        print('dashboard balance/activity: final reference DOM retained; wallet semantics normalized')
        raise SystemExit(0)
    raise RuntimeError('missing wallet balance semantics anchor')

APP.write_text(app_text, encoding='utf-8')
print('dashboard balance/activity: normalized wallet balance semantics')
print('dashboard balance/activity: final reference DOM retained; wallet semantics normalized')
