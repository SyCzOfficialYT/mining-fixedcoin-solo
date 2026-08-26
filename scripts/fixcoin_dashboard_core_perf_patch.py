#!/usr/bin/env python3
"""Finalize dashboard core performance and Python 3.12 UTC handling.

The visual core is now animated by the dedicated Motion mini module and
compositor-friendly CSS. Do not inject a second requestAnimationFrame loop:
that duplicated the animation workload and could fight the Motion transform
on mobile devices.

Idempotent: safe to run repeatedly in the Docker build pipeline.
"""
from pathlib import Path

SERVER = Path('/app/stratum/server_full.py')
HTML = Path('/app/monitor/templates/dashboard_v4.html')

if not HTML.exists() or 'id="forgeCore"' not in HTML.read_text():
    raise RuntimeError('core perf patch: forgeCore anchor missing')

if not SERVER.exists():
    raise RuntimeError('core perf patch: generated server_full.py missing')

server = SERVER.read_text()
deprecated = 'datetime.datetime.utcnow()'
replacement = 'datetime.datetime.now(datetime.UTC)'
count = server.count(deprecated)
if count:
    server = server.replace(deprecated, replacement)
    SERVER.write_text(server)
    print(f'fixed Stratum UTC timestamps: {count} deprecated utcnow call(s) replaced')

if deprecated in server:
    raise RuntimeError('core perf patch: deprecated datetime.utcnow remains in server_full.py')

html = HTML.read_text()
legacy_marker = '/* FIXCOIN CORE PERF JS v1 */'
if legacy_marker in html:
    start = html.find('<script>\n' + legacy_marker)
    if start >= 0:
        end = html.find('</script>', start)
        if end >= 0:
            html = html[:start] + html[end + len('</script>'):]
            HTML.write_text(html)
            print('removed legacy mobile core rAF animation loop')

print('dashboard core mobile performance patch applied: Motion mini + CSS compositor path')
