#!/usr/bin/env python3
"""Restore the four wallet balance metrics and live Recent Activity UI."""
from pathlib import Path

HTML = Path('/app/monitor/templates/dashboard_v4.html')
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

once(
    '<link rel="stylesheet" href="/static/dashboard_v4_forge_motion.css?v=20260823-1">',
    '<link rel="stylesheet" href="/static/dashboard_v4_forge_motion.css?v=20260823-1"><link rel="stylesheet" href="/static/dashboard_v4_balance_activity.css?v=20260823-2">',
    'patched dashboard balance/activity stylesheet'
)

old_balance = '<div class="stat panel"><span>INVALID SHARES</span><strong class="red" id="invalidShares">0</strong><small id="invalidPct">0.0%</small></div>'
new_balance = old_balance + (
    '<div class="stat panel balance-stat balance-confirmed"><span>CONFIRMED BALANCE</span>'
    '<strong id="balanceConfirmed">—</strong><small>confirmed / trusted</small></div>'
    '<div class="stat panel balance-stat balance-unconfirmed"><span>UNCONFIRMED BALANCE</span>'
    '<strong id="balanceUnconfirmed">—</strong><small>untrusted pending</small></div>'
    '<div class="stat panel balance-stat balance-immature"><span>IMMATURE BALANCE</span>'
    '<strong id="balanceImmature">—</strong><small>coinbase maturity</small></div>'
    '<div class="stat panel balance-stat balance-total"><span>TOTAL BALANCE</span>'
    '<strong id="balanceTotal">—</strong><small>confirmed + unconfirmed + immature</small></div>'
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
