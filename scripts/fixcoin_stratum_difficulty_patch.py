#!/usr/bin/env python3
"""Validate and finalize FixedCoin Stratum share-difficulty enforcement."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

required_rejection = 'self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})'
if text.count(required_rejection) != 1:
    raise RuntimeError(
        f"generated Stratum low-difficulty rejection mismatch: expected 1, found {text.count(required_rejection)}"
    )

if "ACCEPT low-difficulty" in text:
    raise RuntimeError("generated Stratum low-difficulty acceptance bypass remains")

low_diff_marker = "if h_int > difficulty_to_target(need):"
accepted_share_marker = "if share_work >= self.diff:"
if low_diff_marker not in text or accepted_share_marker not in text:
    raise RuntimeError("generated Stratum low-difficulty branch markers are missing")
low_diff_branch = text.split(low_diff_marker, 1)[1].split(accepted_share_marker, 1)[0]
if 'result": True, "error": None' in low_diff_branch:
    raise RuntimeError("generated Stratum low-difficulty branch contains a success response")

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
                # A transaction/fee refresh at the same height is not a new
                # Stratum round. Keep the existing job id, coinbase and merkle
                # data stable until the next block height arrives.
                job["ntime"] = min(int(tmpl["curtime"]), int(job.get("ntime") or tmpl["curtime"]))
                job["net_diff"] = net_diff
                return job, False
'''
if same_height_old not in text:
    raise RuntimeError("generated same-height JobStore refresh block not found")
text = text.replace(same_height_old, same_height_new, 1)

if "same_value = int(job.get(\"value\") or 0) == new_value" in text:
    raise RuntimeError("same-height fee/template replacement logic remains")
if "same_txs = (len(other_tx)" in text:
    raise RuntimeError("same-height transaction comparison remains")
if same_height_new not in text:
    raise RuntimeError("same-height stable-job patch was not applied")

telemetry_old = 'emit("WARN", f"REJECT reason=low-difficulty worker={self.worker} job={job_id} height={job[\'height\']} share_diff={share_work:.6f} required_diff={need:.6f} fixed_diff={self.diff:.6f} ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:24]}")'
telemetry_new = 'emit("WARN", f"REJECT reason=low-difficulty worker={self.worker} job={job_id} height={job[\'height\']} share_diff={share_work:.6f} required_diff={need:.6f} current_diff={self.diff:.6f} previous_diff={self.diff_prev:.6f} vardiff={int(self.vardiff_enabled)} grace_active={int(time.time() - self.diff_changed_at < DIFF_GRACE_SEC)} ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:24]}")'
if telemetry_old not in text:
    raise RuntimeError("generated Stratum reject telemetry line not found")
text = text.replace(telemetry_old, telemetry_new, 1)

# Password `x` is an explicit per-miner VarDiff opt-in. The global
# pool.vardiff setting remains the default for all other miners.
class_marker = "class Client"
class_start = text.find(class_marker)
if class_start < 0:
    raise RuntimeError("Client class not found")

# Find the next top-level declaration, not the first method inside Client.
# This keeps the complete Client class available for the per-connection patch.
tail = text[class_start:]
match = re.search(r"\n(?:(?:class|def)\s+|if\s+__name__\s*==)", tail[1:])
class_end = class_start + 1 + match.start() if match else len(text)
client = text[class_start:class_end]

# Every Client gets an explicit per-connection VarDiff switch. The generated
# adapter may already have a global VARDIFF flag, but password `x` must not
# affect other miners.
if "self.vardiff_enabled" not in client:
    init_marker = "        self.diff_from_password = False"
    if init_marker not in client:
        raise RuntimeError("Client __init__ difficulty marker not found")
    client = client.replace(
        init_marker,
        init_marker + "\n        self.vardiff_enabled = VARDIFF\n        self.diff_prev = self.diff\n        self.diff_changed_at = time.time()",
        1,
    )

password_markers = [
    '        password = params[1] if len(params) > 1 else ""',
    "        password = params[1] if len(params) > 1 else ''",
]
password_marker = next((m for m in password_markers if m in client), None)
if password_marker is None:
    raise RuntimeError("authorize password marker not found")

if 'password.lower().strip() == "x"' not in client:
    vardiff_block = '''        # `x` is the explicit VarDiff password for this miner.
        # Global pool.vardiff remains the default for miners without it.
        self.vardiff_enabled = VARDIFF or (isinstance(password, str) and password.lower().strip() == "x")
        if self.vardiff_enabled:
            self.diff_from_password = False
            self.diff_prev = self.diff
            self.diff = max(START_DIFF, MIN_DIFF)
            self.diff_changed_at = time.time()
        else:
            self.diff = FIXED_DIFF
            self.diff_prev = self.diff
            self.diff_changed_at = time.time()
'''
    client = client.replace(password_marker, password_marker + "\n" + vardiff_block.rstrip(), 1)

# Manual password d= remains an explicit fixed-difficulty override.
d_marker = '                    self.diff_from_password = True'
if d_marker in client and 'self.vardiff_enabled = False\n                    self.diff_from_password = True' not in client:
    client = client.replace(d_marker, '                    self.vardiff_enabled = False\n                    self.diff_from_password = True', 1)

# Use the connection-local switch for every VarDiff decision inside Client.
client = client.replace("if VARDIFF:", "if self.vardiff_enabled:")
client = client.replace("if not VARDIFF:", "if not self.vardiff_enabled:")

# Before authorization, stay at the safe fixed difficulty. Authorization then
# selects either fixed mode or VarDiff based on the supplied password.
client = client.replace(
    "self.diff = FIXED_DIFF if not self.vardiff_enabled else max(START_DIFF, MIN_DIFF)",
    "self.diff = FIXED_DIFF",
)
client = client.replace(
    "self.diff = FIXED_DIFF if not VARDIFF else max(START_DIFF, MIN_DIFF)",
    "self.diff = FIXED_DIFF",
)

text = text[:class_start] + client + text[class_end:]

# Hard guarantees for the opt-in behavior.
if 'password.lower().strip() == "x"' not in text:
    raise RuntimeError("password x VarDiff opt-in was not installed")
if "self.vardiff_enabled = VARDIFF" not in text:
    raise RuntimeError("per-client VarDiff flag was not installed")
if "self.diff = FIXED_DIFF" not in text:
    raise RuntimeError("fixed difficulty fallback was removed")
if "self.diff = max(START_DIFF, MIN_DIFF)" not in text:
    raise RuntimeError("VarDiff start difficulty was not installed")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: strict share difficulty, stable jobs, and password-x VarDiff opt-in")
