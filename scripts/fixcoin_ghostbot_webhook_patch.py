#!/usr/bin/env python3
"""Attach a non-blocking NerdQAxe/AxeOS-style webhook to network block candidates."""
from pathlib import Path
import ast
import re

SERVER = Path('/app/stratum/server_full.py')
MARKER = 'FIXEDCOIN_GHOSTBOT_WEBHOOK_V1'

HELPER = r'''
# FIXEDCOIN_GHOSTBOT_WEBHOOK_V1
import threading as _fixedcoin_ghostbot_threading

_FIXEDCOIN_GHOSTBOT_SENT = set()
_FIXEDCOIN_GHOSTBOT_LOCK = _fixedcoin_ghostbot_threading.Lock()


def _fixedcoin_ghostbot_send(payload):
    import json as _json
    import os as _os
    import urllib.request as _urlrequest

    url = (_os.getenv("GHOSTBOT_WEBHOOK_URL") or "").strip()
    if not url:
        return
    try:
        req = _urlrequest.Request(
            url,
            data=_json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "NerdQAxe++/AxeOS",
            },
            method="POST",
        )
        with _urlrequest.urlopen(
            req,
            timeout=float(_os.getenv("GHOSTBOT_WEBHOOK_TIMEOUT", "5")),
        ):
            pass
    except Exception as _exc:
        try:
            log.warning("GhostBot webhook failed: %s", _exc)
        except Exception:
            pass


def _fixedcoin_ghostbot_block_event(message):
    import os as _os
    import re as _re
    import time as _time

    if not (_os.getenv("GHOSTBOT_WEBHOOK_URL") or "").strip():
        return
    if "BLOCK CANDIDATE" not in str(message).upper():
        return

    text = str(message)
    hm = _re.search(r"\bheight=(\d+)", text, _re.I)
    xm = _re.search(r"\bhash=([0-9a-fA-F]{16,64})", text, _re.I)
    wm = _re.search(r"\bworker=([^\s]+)", text, _re.I)
    height = hm.group(1) if hm else "unknown"
    block_hash = xm.group(1) if xm else "unknown"
    worker = wm.group(1) if wm else "solo"
    key = f"{height}:{block_hash}"

    with _FIXEDCOIN_GHOSTBOT_LOCK:
        if key in _FIXEDCOIN_GHOSTBOT_SENT:
            return
        _FIXEDCOIN_GHOSTBOT_SENT.add(key)
        if len(_FIXEDCOIN_GHOSTBOT_SENT) > 512:
            _FIXEDCOIN_GHOSTBOT_SENT.pop()

    dashboard = (_os.getenv("GHOSTBOT_DASHBOARD_URL") or "").strip()
    try:
        embed_color = int(_os.getenv("GHOSTBOT_EMBED_COLOR", "5635925"))
    except ValueError:
        embed_color = 5635925

    # Deliberately use an AxeOS/NerdQAxe identity rather than a visible
    # GhostBot identity. This lets the alert share the same Discord webhook
    # destination as the miner's normal alerts without looking like a second bot.
    username = _os.getenv("GHOSTBOT_WEBHOOK_USERNAME", "NerdQAxe++")
    avatar = (_os.getenv("GHOSTBOT_WEBHOOK_AVATAR_URL") or "").strip()

    payload = {
        "username": username,
        "allowed_mentions": {"parse": []},
        "content": "🚀 **BLOCK FOUND!**",
        "embeds": [{
            "title": "⛏️ NerdQAxe++ — Block Found",
            "description": "Network-difficulty block candidate found by solo mining.",
            "color": embed_color,
            "fields": [
                {"name": "Block Height", "value": f"`#{height}`", "inline": True},
                {"name": "Miner", "value": f"`{worker}`", "inline": True},
                {"name": "Block Hash", "value": f"`{block_hash}`", "inline": False},
            ],
            "footer": {"text": "NerdQAxe++ • AxeOS"},
            "timestamp": _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime()),
            **({"url": dashboard} if dashboard else {}),
        }],
        **({"avatar_url": avatar} if avatar else {}),
    }

    _fixedcoin_ghostbot_threading.Thread(
        target=_fixedcoin_ghostbot_send,
        args=(payload,),
        name="fixedcoin-ghostbot-webhook",
        daemon=True,
    ).start()
'''


def function_span(source, name):
    tree = ast.parse(source)
    node = next(
        (
            n for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name == name
        ),
        None,
    )
    if node is None:
        raise RuntimeError(f'top-level function {name!r} not found')
    lines = source.splitlines(keepends=True)
    start = sum(map(len, lines[: node.lineno - 1]))
    end = sum(map(len, lines[: node.end_lineno]))
    return start, end


text = SERVER.read_text()
if MARKER in text:
    print('GhostBot webhook already patched')
    raise SystemExit(0)

start, end = function_span(text, 'emit')
original = text[start:end]
renamed = re.sub(r'^def\s+emit\s*\(', 'def _fixedcoin_emit_original(', original, count=1, flags=re.M)
if renamed == original:
    raise RuntimeError('could not rename original emit function')

wrapper = r'''

def emit(*args, **kwargs):
    result = _fixedcoin_emit_original(*args, **kwargs)
    try:
        message = kwargs.get("message") or kwargs.get("msg")
        if message is None and len(args) >= 2:
            message = args[1]
        if message is not None:
            _fixedcoin_ghostbot_block_event(message)
    except Exception as _exc:
        try:
            log.warning("GhostBot event hook failed: %s", _exc)
        except Exception:
            pass
    return result
'''

text = text[:start] + HELPER + '\n' + renamed + wrapper + text[end:]
ast.parse(text)
SERVER.write_text(text)
print('NerdQAxe/AxeOS-style webhook installed: non-blocking block-candidate notification with deduplication')
