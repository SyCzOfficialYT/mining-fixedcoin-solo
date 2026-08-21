#!/usr/bin/env python3
"""Generate the FixedCoin Stratum server from the pinned FreeCash base."""
import ast
import os
import re
import runpy
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = HERE / "server_full.py"
URL = "https://raw.githubusercontent.com/SyCzOfficialYT/freecash-coin/a88d89675b3a41cc6774e1b975e57e050d4892cc/stratum/server.py"
ADAPT_VERSION = "fixedcoin-consensus-repair-2026-08-21-v31"


def sanitize_source(source):
    """Turn accidental literal control bytes into Python escape sequences."""
    return "".join(
        f"\\x{ord(ch):02x}" if ord(ch) < 0x20 and ch not in "\n\r\t" else ch
        for ch in source
    )


def replace_function(source, name, replacement):
    replacement = sanitize_source(replacement)
    tree = ast.parse(source)
    target = next((n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)
    if target is None:
        raise RuntimeError(f"function {name!r} not found in FreeCash base")
    lines = source.splitlines(keepends=True)
    start = sum(map(len, lines[: target.lineno - 1]))
    end = sum(map(len, lines[: target.end_lineno]))
    return source[:start] + replacement.rstrip() + "\n" + source[end:]
