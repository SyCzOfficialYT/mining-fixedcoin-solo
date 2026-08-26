#!/usr/bin/env python3
"""Give NMMiner/NerdMiner low-hashrate clients a usable Stratum share difficulty.

The pool's canonical ASIC difficulty is intentionally high for SHA-256 ASICs.
NMMiner/NerdMiner devices are tiny miners, so the same fixed difficulty can
make a share statistically impossible to see in a normal session. The miner
identity is detected during mining.subscribe by the preceding miner-detection
patch; this patch applies a dedicated difficulty during authorize.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

tree = ast.parse(text)
client = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Client"), None)
if client is None:
    raise RuntimeError("Client class not found")

lines = text.splitlines(keepends=True)
start = sum(map(len, lines[:client.lineno - 1]))
end = sum(map(len, lines[:client.end_lineno]))
client_text = text[start:end]
client_tree = ast.parse(client_text)

authorize_fn = None
for node in ast.walk(client_tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "handle_authorize":
        authorize_fn = node
        break
if authorize_fn is None:
    raise RuntimeError("handle_authorize not found")

clines = client_text.splitlines(keepends=True)
fn_start = sum(map(len, clines[:authorize_fn.lineno - 1]))
fn_end = sum(map(len, clines[:authorize_fn.end_lineno]))
fn_text = client_text[fn_start:fn_end]

marker = '        self.worker = params[0] if params else "?"\n'
if marker not in fn_text:
    raise RuntimeError("authorize worker marker not found")

injection = '''
        # NMMiner/NerdMiner has a tiny hashrate compared with the ASIC target.
        # At the canonical FIX difficulty (~13.3K), a ~400 KH/s device would
        # statistically need years per share. Give these detected clients a
        # dedicated low difficulty while keeping ASICs on the canonical target.
        miner_family = str(getattr(self, "miner_family", "") or "").strip().lower()
        if miner_family in {"nmminer", "nerdminer"}:
            nm_diff = float(os.getenv("FIX_NMMINER_DIFF", "1"))
            if not nm_diff > 0:
                raise RuntimeError("FIX_NMMINER_DIFF must be > 0")
            self.diff = nm_diff
            self.diff_prev = nm_diff
            self.diff_from_password = True
            self.diff_changed_at = time.time()
            emit("INFO", f"NMMINER DIFF worker={self.worker} diff={nm_diff:g} mode=low-hash fixed")
'''
fn_text = fn_text.replace(marker, marker + injection, 1)
client_text = client_text[:fn_start] + fn_text + client_text[fn_end:]
text = text[:start] + client_text + text[end:]

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: NMMiner/NerdMiner low-hash difficulty enabled")
