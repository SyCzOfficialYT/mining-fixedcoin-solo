#!/usr/bin/env python3
"""Load the final explicit 3-row/5-row metric geometry after the main reference layer.

The rebuild pass owns the stylesheet version, so this patch must not depend on a
specific cache-busting query string.  Keep the patch chain idempotent and attach the
rows stylesheet immediately after the rebuild stylesheet.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
s = HTML.read_text()

# Remove any previous rows stylesheet first so repeated build runs cannot duplicate it.
s = re.sub(
    r'<link\s+rel="stylesheet"\s+href="/static/dashboard_v4_reference_rows\.css\?v=[^"]+">',
    '',
    s,
)

rows_link = '<link rel="stylesheet" href="/static/dashboard_v4_reference_rows.css?v=20260825-1">'

# The rebuild patch currently emits v2, while older builds emitted v1.  Match the
# stylesheet semantically instead of coupling this patch to one cache-buster value.
rebuild_pattern = r'(<link\s+rel="stylesheet"\s+href="/static/dashboard_v4_reference_rebuild\.css\?v=[^"]+">)'
s, n = re.subn(rebuild_pattern, r'\1' + rows_link, s, count=1)
if n != 1:
    raise RuntimeError('reference rows patch: rebuild stylesheet link missing')

HTML.write_text(s)
print('dashboard reference rows patch applied: 3 primary + 5 balance/rate cards with explicit gaps')
