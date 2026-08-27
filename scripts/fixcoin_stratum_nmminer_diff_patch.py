#!/usr/bin/env python3
"""Install a dedicated low-hash VarDiff controller for Nerd-class miners.

NMMiner, NerdMiner and NerdQAxe++ are low-hashrate miners. They must not be
fed through the normal integer ASIC VarDiff path, but they also must not stay
at a permanently tiny difficulty. A dedicated float-capable controller keeps
their share rate sane while the real block test remains the network target.

Explicit ``d=`` passwords remain authoritative and disable VarDiff for that
connection.
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


def function_bounds(source, tree_node, name):
    fn = next(
        (n for n in ast.walk(tree_node)
         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name),
        None,
    )
    if fn is None:
        raise RuntimeError(f"{name} not found")
    ls = source.splitlines(keepends=True)
    return sum(map(len, ls[:fn.lineno - 1])), sum(map(len, ls[:fn.end_lineno]))


# Replace authorization with three distinct modes:
#   1. explicit d=... -> fixed, no VarDiff
#   2. low-hash miner -> dedicated float VarDiff
#   3. everything else -> existing pool/ASIC VarDiff behavior
fn_start, fn_end = function_bounds(client_text, client_tree, "handle_authorize")
replacement = '''    def handle_authorize(self, mid, params):
        self.worker = params[0] if params else "?"
        password = params[1] if len(params) > 1 else ""
        password_text = password.lower().strip() if isinstance(password, str) else ""

        miner_family = str(getattr(self, "miner_family", "") or "").strip().lower()
        low_hash_miner = miner_family in {"nmminer", "nerdminer", "nerdqaxe"}
        fixed = parse_fixed_diff(password, self.worker)

        # Explicit d=... always wins. This is useful for diagnostics and for
        # miners that cannot tolerate dynamic difficulty changes.
        if fixed is not None:
            self.vardiff_enabled = False
            self.diff_from_password = True
            self.low_hash_vardiff = False
            self.diff = fixed
            mode = "fixed"
            emit("INFO", f"FIXED DIFF from password: {fixed} (VarDiff OFF)")
        elif low_hash_miner:
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
            self.vardiff_enabled = True
            self.low_hash_vardiff = True
            self.diff_from_password = False
            self.diff = low_diff
            mode = "low-hash-vardiff"
        else:
            # `x` explicitly opts this connection into normal VarDiff even
            # when the global pool default is fixed.
            self.vardiff_enabled = bool(VARDIFF) or password_text == "x"
            self.low_hash_vardiff = False
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
        if low_hash_miner and fixed is None:
            emit(
                "INFO",
                f"LOW-HASH DIFF worker={self.worker} diff={self.diff:g} "
                f"miner={getattr(self, 'miner_family', 'unknown')} mode=low-hash-vardiff",
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

# Reparse after authorization replacement.
client_tree = ast.parse(client_text)

# Replace normal retarget_vardiff with a dispatcher plus a float-capable
# controller for low-hash miners. Normal ASIC behavior is left intact.
fn_start, fn_end = function_bounds(client_text, client_tree, "retarget_vardiff")
retarget = '''    def _set_low_hash_diff(self, new_diff, reason=""):
        if not getattr(self, "low_hash_vardiff", False):
            return
        raw_min = os.getenv("FIX_NMMINER_MIN_DIFF", "0.001")
        raw_max = os.getenv("FIX_NMMINER_MAX_DIFF", "0.100")
        try:
            min_diff = float(raw_min)
            max_diff = float(raw_max)
        except (TypeError, ValueError):
            raise RuntimeError("FIX_NMMINER_MIN_DIFF / FIX_NMMINER_MAX_DIFF must be numeric")
        if min_diff <= 0 or max_diff < min_diff:
            raise RuntimeError("invalid low-hash difficulty bounds")

        new_diff = max(min_diff, min(max_diff, float(new_diff)))
        # Keep enough precision for the sub-1 difficulty range while avoiding
        # meaningless floating-point noise in Stratum telemetry.
        new_diff = round(new_diff, 6)
        if abs(new_diff - float(self.diff)) < max(1e-9, min_diff * 0.005):
            return

        self.diff_prev = self.diff
        self.diff = new_diff
        self.diff_changed_at = time.time()
        self.shares_since_retarget = 0
        self.vardiff_buf = []
        self.send({"id": None, "method": "mining.set_difficulty", "params": [self.diff]})
        emit(
            "INFO",
            f"LOW-HASH VARDIFF {self.worker} {self.diff_prev:g}→{self.diff:g} "
            f"{reason} (grace {DIFF_GRACE_SEC:.0f}s)",
        )
        self.push_job(clean=True, force_refresh=False)

    def _retarget_low_hash_vardiff(self):
        now = time.time()
        if now - self.diff_changed_at < DIFF_GRACE_SEC:
            return

        self.shares_since_retarget += 1
        # Five samples give NerdMiner-class devices a stable enough window
        # without waiting minutes for every retarget.
        if self.shares_since_retarget < 5:
            return

        self.vardiff_buf = [t for t in self.vardiff_buf if now - t < 90]
        if len(self.vardiff_buf) < 5:
            return

        window = now - self.vardiff_buf[0]
        if window < 15:
            return

        rate = (len(self.vardiff_buf) - 1) / window
        if rate <= 0:
            return

        try:
            target_share_sec = float(
                os.getenv("FIX_NMMINER_TARGET_SHARE_SEC", str(TARGET_SHARE_SEC))
            )
        except (TypeError, ValueError):
            target_share_sec = float(TARGET_SHARE_SEC)
        target_share_sec = max(5.0, min(120.0, target_share_sec))
        target_rate = 1.0 / target_share_sec

        # More shares than desired -> increase difficulty.
        # Fewer shares than desired -> decrease difficulty.
        factor = max(0.70, min(1.30, rate / target_rate))
        if 0.90 <= factor <= 1.10:
            return

        self._set_low_hash_diff(
            float(self.diff) * factor,
            f"rate={rate:.3f}/s want={target_rate:.3f}/s",
        )

    def retarget_vardiff(self):
        if getattr(self, "low_hash_vardiff", False):
            self._retarget_low_hash_vardiff()
            return
        if not VARDIFF or self.diff_from_password:
            return
        now = time.time()
        if now - self.diff_changed_at < DIFF_GRACE_SEC:
            return
        self.shares_since_retarget += 1
        if self.shares_since_retarget < 5:
            return
        self.vardiff_buf = [t for t in self.vardiff_buf if now - t < 90]
        self.vardiff_buf.append(now)
        if len(self.vardiff_buf) < 5:
            return
        window = now - self.vardiff_buf[0]
        if window < 15:
            return
        rate = (len(self.vardiff_buf) - 1) / window
        target_rate = 1.0 / TARGET_SHARE_SEC
        if rate <= 0:
            return
        factor = rate / target_rate
        factor = max(0.7, min(1.3, factor))
        if 0.9 <= factor <= 1.1:
            return
        new_d = int(self.diff * factor)
        if new_d >= 1_000_000:
            new_d = int(round(new_d / 50000) * 50000)
        elif new_d >= 10000:
            new_d = int(round(new_d / 1000) * 1000)
        elif new_d >= 1000:
            new_d = int(round(new_d / 100) * 100)
        self.set_diff(new_d, f"rate={rate:.3f}/s want={target_rate:.3f}/s")
'''
client_text = client_text[:fn_start] + retarget + client_text[fn_end:]

text = text[:start] + client_text + text[end:]

for marker in (
    'low_hash_miner = miner_family in {"nmminer", "nerdminer", "nerdqaxe"}',
    'self.low_hash_vardiff = True',
    'def _set_low_hash_diff(self, new_diff, reason=""):',
    'def _retarget_low_hash_vardiff(self):',
    'if getattr(self, "low_hash_vardiff", False):',
    'FIX_NMMINER_TARGET_SHARE_SEC',
    'self.send({"id": None, "method": "mining.set_difficulty", "params": [self.diff]})',
    'if h_int <= job["target"]:',
):
    if marker not in text:
        raise RuntimeError(f"low-hash VarDiff marker missing: {marker}")

if 'self.vardiff_enabled = False\n            self.diff_from_password = True\n            self.low_hash_vardiff = False' not in text:
    raise RuntimeError("explicit fixed difficulty authority missing")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: dedicated float low-hash VarDiff installed; network block target remains independent")
