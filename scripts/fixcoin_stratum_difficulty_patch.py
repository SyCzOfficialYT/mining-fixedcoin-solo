#!/usr/bin/env python3
"""Finalize FixedCoin Stratum difficulty handling.

VarDiff is connection-local.  Password `x` must receive the configured
VarDiff start/minimum difficulty immediately during authorization; it must
never inherit FIXED_DIFF=13354 first and wait for a later retarget.
"""
import ast
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

required_rejection = 'self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})'
if text.count(required_rejection) != 1:
    raise RuntimeError(f"generated Stratum low-difficulty rejection mismatch: {text.count(required_rejection)}")
if "ACCEPT low-difficulty" in text:
    raise RuntimeError("generated Stratum low-difficulty acceptance bypass remains")
if "if h_int > difficulty_to_target(need):" not in text or "if share_work >= self.diff:" not in text:
    raise RuntimeError("generated Stratum difficulty markers are missing")

# Keep a stable Stratum job while the same block height/template is refreshed.
same_height_old = '''            if (self.current_id and self.last_height == height and self.last_prevhash == prevhash
                    and self.current_id in self.jobs):
                job = self.jobs[self.current_id]
                same_txs = (len(other_tx) == len(job.get("other_tx") or [])
                            and all(a == b for a, b in zip(other_tx, job.get("other_tx") or [])))
                same_value = int(job.get("value") or 0) == new_value
                if same_txs and same_value:
                    job["ntime"] = tmpl["curtime"]
                    job["template"] = tmpl
                    job["net_diff"] = net_diff
                    return job, False
'''
same_height_new = '''            if (self.current_id and self.last_height == height and self.last_prevhash == prevhash
                    and self.current_id in self.jobs):
                job = self.jobs[self.current_id]
                # Same height is the same Stratum round. Refresh ntime only;
                # never replace the job/coinbase merely because fees changed.
                job["ntime"] = min(int(tmpl["curtime"]), int(job.get("ntime") or tmpl["curtime"]))
                job["net_diff"] = net_diff
                return job, False
'''
if same_height_old in text:
    text = text.replace(same_height_old, same_height_new, 1)
if "same_txs = (len(other_tx)" in text or "same_value = int(job.get(\"value\") or 0) == new_value" in text:
    raise RuntimeError("same-height unstable job refresh remains")
if same_height_new not in text:
    raise RuntimeError("stable same-height job patch missing")

# Better reject telemetry for diagnosing per-client difficulty.
old_tel = 'emit("WARN", f"REJECT reason=low-difficulty worker={self.worker} job={job_id} height={job[\'height\']} share_diff={share_work:.6f} required_diff={need:.6f} fixed_diff={self.diff:.6f} ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:24]}")'
new_tel = 'emit("WARN", f"REJECT reason=low-difficulty worker={self.worker} job={job_id} height={job[\'height\']} share_diff={share_work:.6f} required_diff={need:.6f} current_diff={self.diff:.6f} previous_diff={self.diff_prev:.6f} vardiff={int(self.vardiff_enabled)} grace_active={int(time.time() - self.diff_changed_at < DIFF_GRACE_SEC)} ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:24]}")'
if old_tel in text:
    text = text.replace(old_tel, new_tel, 1)

# Work only on the real Client class.
tree = ast.parse(text)
client_node = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Client"), None)
if client_node is None:
    raise RuntimeError("Client class not found")
lines = text.splitlines(keepends=True)
class_start = sum(map(len, lines[:client_node.lineno - 1]))
class_end = sum(map(len, lines[:client_node.end_lineno]))
client = text[class_start:class_end]

# Per-connection VarDiff switch. Global pool.vardiff remains the default.
if "self.vardiff_enabled = VARDIFF" not in client:
    marker = "        self.diff_from_password = False"
    if marker not in client:
        marker = "        self.diff_from_password = not VARDIFF"
    if marker not in client:
        raise RuntimeError("Client difficulty initialization marker not found")
    client = client.replace(marker, marker + "\n        self.vardiff_enabled = VARDIFF", 1)

password_marker = next((m for m in (
    '        password = params[1] if len(params) > 1 else ""',
    "        password = params[1] if len(params) > 1 else ''",
) if m in client), None)
if password_marker is None:
    raise RuntimeError("authorize password marker not found")

if 'password.lower().strip() == "x"' not in client:
    block = '''        # Password `x` opts this connection into VarDiff.
        self.vardiff_enabled = VARDIFF or (
            isinstance(password, str) and password.lower().strip() == "x"
        )
        if self.vardiff_enabled:
            self.diff_from_password = False
            self.diff = max(START_DIFF, MIN_DIFF)
            self.diff_prev = self.diff
            self.diff_changed_at = time.time()
        else:
            self.diff = FIXED_DIFF
            self.diff_prev = self.diff
            self.diff_changed_at = time.time()
'''
    client = client.replace(password_marker, password_marker + "\n" + block.rstrip(), 1)

# Explicit d=<difficulty> always wins and disables VarDiff for that connection.
d_marker = '                    self.diff_from_password = True'
if d_marker in client and '                    self.vardiff_enabled = False\n                    self.diff_from_password = True' not in client:
    client = client.replace(d_marker, '                    self.vardiff_enabled = False\n                    self.diff_from_password = True', 1)

# Convert retarget guards to the connection-local flag.
converted = []
for line in client.splitlines(keepends=True):
    stripped = line.lstrip()
    if stripped.startswith("if ") or stripped.startswith("elif "):
        line = re.sub(r"\bVARDIFF\b", "self.vardiff_enabled", line)
    converted.append(line)
client = "".join(converted)

# CRITICAL: the upstream authorize path can assign self.diff again after the
# password selector. Apply the connection's final difficulty immediately
# before the authorization log/response. This guarantees x starts at 1000
# (or configured start/min) instead of 13354.
auth_log = '        emit("INFO", f"authorize {self.worker} diff={self.diff} mode={mode}")'
if auth_log not in client:
    raise RuntimeError("authorization log marker not found")
finalize = '''        # Final authorization authority: password-x VarDiff must be active
        # on the very first set_difficulty sent to this miner.
        if self.vardiff_enabled and not self.diff_from_password:
            self.diff = max(START_DIFF, MIN_DIFF)
            self.diff_prev = self.diff
            self.diff_changed_at = time.time()
        elif not self.vardiff_enabled and not self.diff_from_password:
            self.diff = FIXED_DIFF
            self.diff_prev = self.diff
            self.diff_changed_at = time.time()
'''
if "# Final authorization authority: password-x VarDiff" not in client:
    client = client.replace(auth_log, finalize + auth_log, 1)

mode_old = 'mode = "fixed" if self.diff_from_password else f"vardiff={VARDIFF}"'
mode_new = 'mode = "fixed" if self.diff_from_password else f"vardiff={self.vardiff_enabled}"'
if mode_old in client:
    client = client.replace(mode_old, mode_new, 1)

text = text[:class_start] + client + text[class_end:]

# Hard guarantees.
for marker in (
    'password.lower().strip() == "x"',
    "self.vardiff_enabled = VARDIFF",
    "self.vardiff_enabled = VARDIFF or",
    "self.diff = max(START_DIFF, MIN_DIFF)",
    "# Final authorization authority: password-x VarDiff",
):
    if marker not in text:
        raise RuntimeError(f"VarDiff marker missing: {marker}")
if re.search(r"^\s*if\s+.*\bVARDIFF\b", client, re.M):
    raise RuntimeError("VarDiff conditional still uses global VARDIFF")
if not re.search(r"^\s*if\s+not\s+self\.vardiff_enabled\s+or\s+self\.diff_from_password\s*:", client, re.M):
    raise RuntimeError("per-client VarDiff retarget guard missing")
if 'mode = "fixed" if self.diff_from_password else f"vardiff={self.vardiff_enabled}"' not in client:
    raise RuntimeError("authorization mode still uses global VARDIFF")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: strict share difficulty, stable jobs, and password-x VarDiff starts at configured minimum")
