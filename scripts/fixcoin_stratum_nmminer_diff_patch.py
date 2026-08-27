#!/usr/bin/env python3
"""Finalize Stratum low-hash difficulty authority.

NMMiner, NerdMiner and NerdQAxe++ are low-hashrate miners. Their difficulty
must not be overwritten by the normal ASIC/VarDiff path. Explicit ``d=``
password difficulty remains authoritative for every other miner.
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

authorize_fn = next(
    (n for n in ast.walk(client_tree)
     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "handle_authorize"),
    None,
)
if authorize_fn is None:
    raise RuntimeError("handle_authorize not found")

clines = client_text.splitlines(keepends=True)
fn_start = sum(map(len, clines[:authorize_fn.lineno - 1]))
fn_end = sum(map(len, clines[:authorize_fn.end_lineno]))

replacement = '''    def handle_authorize(self, mid, params):
        self.worker = params[0] if params else "?"
        password = params[1] if len(params) > 1 else ""
        password_text = password.lower().strip() if isinstance(password, str) else ""

        miner_family = str(getattr(self, "miner_family", "") or "").strip().lower()
        low_hash_miner = miner_family in {"nmminer", "nerdminer", "nerdqaxe"}

        # Low-hash miner families use the configured low-hash target and are
        # never handed to the normal ASIC VarDiff controller.
        fixed = parse_fixed_diff(password, self.worker)

        if low_hash_miner:
            raw_low_diff = (
                os.getenv("FIX_NMMINER_DIFF")
                or os.getenv("FIX_LOW_HASH_DIFF")
                or str(cfg["pool"].get("nmminer_difficulty", 0.001))
            )
            try:
                low_diff = float(raw_low_diff)
            except (TypeError, ValueError):
                raise RuntimeError(
                    "FIX_NMMINER_DIFF / FIX_LOW_HASH_DIFF / pool.nmminer_difficulty must be numeric"
                )
            if not low_diff > 0:
                raise RuntimeError(
                    "FIX_NMMINER_DIFF / FIX_LOW_HASH_DIFF / pool.nmminer_difficulty must be > 0"
                )
            self.vardiff_enabled = False
            self.diff_from_password = True
            self.diff = low_diff
            mode = "low-hash-fixed"
        elif fixed is not None:
            self.vardiff_enabled = False
            self.diff_from_password = True
            self.diff = fixed
            mode = "fixed"
            emit("INFO", f"FIXED DIFF from password: {fixed} (VarDiff OFF)")
        else:
            # `x` explicitly opts this connection into VarDiff even when the
            # global pool default is fixed. Otherwise honor pool.vardiff.
            self.vardiff_enabled = bool(VARDIFF) or password_text == "x"
            if self.vardiff_enabled:
                self.diff_from_password = False
                self.diff = max(START_DIFF, MIN_DIFF)
                mode = "vardiff=True"
            else:
                self.diff_from_password = True
                self.diff = FIXED_DIFF
                mode = "fixed"

        self.diff_prev = self.diff
        self.diff_changed_at = time.time()
        self.shares_since_retarget = 0
        self.vardiff_buf = []

        self.send({"id": mid, "result": True, "error": None})
        self.send({"id": None, "method": "mining.set_difficulty", "params": [self.diff]})
        if low_hash_miner:
            emit(
                "INFO",
                f"LOW-HASH DIFF worker={self.worker} diff={self.diff:g} "
                f"miner={getattr(self, 'miner_family', 'unknown')} mode=low-hash fixed",
            )
        emit(
            "INFO",
            f"authorize {self.worker} diff={self.diff:g} mode={mode} "
            f"miner={getattr(self, 'miner_family', 'unknown')}/{getattr(self, 'miner_variant', '') or 'unknown'} "
            f"version={getattr(self, 'miner_version', '') or 'unknown'}",
        )
        self.push_job(clean=True, force_refresh=True)
'''

client_text = client_text[:fn_start] + replacement + client_text[fn_end:]
text = text[:start] + client_text + text[end:]

for marker in (
    'low_hash_miner = miner_family in {"nmminer", "nerdminer", "nerdqaxe"}',
    'os.getenv("FIX_LOW_HASH_DIFF")',
    'nmminer_difficulty',
    'mining.set_difficulty',
    'self.push_job(clean=True, force_refresh=True)',
):
    if marker not in text:
        raise RuntimeError(f"low-hash authorization marker missing: {marker}")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: NMMiner/NerdMiner/NerdQAxe low-hash difficulty authority installed")
