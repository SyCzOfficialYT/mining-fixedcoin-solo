#!/usr/bin/env python3
"""Restore wallet balance UI and make Recent Activity truly realtime from /api/logs."""
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
    '<link rel="stylesheet" href="/static/dashboard_v4_forge_motion.css?v=20260823-1"><link rel="stylesheet" href="/static/dashboard_v4_balance_activity.css?v=20260823-1">',
    'patched dashboard balance/activity stylesheet'
)

once(
    '<div class="stat panel"><span>INVALID SHARES</span><strong class="red" id="invalidShares">0</strong><small id="invalidPct">0.0%</small></div>',
    '<div class="stat panel"><span>INVALID SHARES</span><strong class="red" id="invalidShares">0</strong><small id="invalidPct">0.0%</small></div><div class="stat panel balance-stat"><span>BALANCE</span><strong id="balanceValue">—</strong><small id="balanceMeta">confirmed wallet balance</small></div>',
    'restored dashboard wallet balance card'
)

once(
    '<script defer src="/static/dashboard_v4_forge.js?v=20260823-2"></script>',
    '<script defer src="/static/dashboard_v4_forge.js?v=20260823-2"></script><script defer src="/static/dashboard_v4_balance_activity.js?v=20260823-1"></script>',
    'patched dashboard realtime balance/activity client'
)

if changed:
    HTML.write_text(text)
print('dashboard balance/activity repair complete')
