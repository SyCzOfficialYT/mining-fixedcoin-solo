#!/usr/bin/env python3
"""Enforce the configured FixedCoin Stratum share difficulty."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

# fixcoin_consensus_patch.py runs immediately before this script and changes
# the low-difficulty branch into an accounting accept. Match the exact
# post-consensus block instead of relying on fragile multiline regex spacing.
old = '''            need = self.effective_min_diff()
            if h_int > difficulty_to_target(need):
                emit("INFO", f"ACCEPT low-difficulty share worker={self.worker} job={job_id} height={job['height']} share_diff={share_work:.6f} advertised_diff={need:.6f} fixed_diff={self.diff:.6f} ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:24]}")
            _bump_worker(self.worker, ok=True)
            _record_share(self.worker, share_work, self.diff, job.get("network_diff", 0.0), hhex, job["height"], accepted=True)
            _add_round_share(self.diff, share_work, job.get("network_diff", 0.0), job["height"])
            self.send({"id": mid, "result": True, "error": None})'''

# The consensus patch preserves the original `if h_int > ...` line, while
# replacing the body. Its generated indentation is therefore intentionally
# different from the original pre-consensus rejection block.
if old not in text:
    marker = '            need = self.effective_min_diff()\n'
    start = text.find(marker)
    if start < 0:
        raise RuntimeError("low-difficulty marker not found")
    end_marker = '            self.vardiff_buf.append(time.time())\n'
    end = text.find(end_marker, start)
    if end < 0:
        raise RuntimeError("low-difficulty block end marker not found")
    candidate = text[start:end]
    if 'ACCEPT low-difficulty share' not in candidate or 'self.send({"id": mid, "result": True, "error": None})' not in candidate:
        raise RuntimeError("low-difficulty post-consensus block content mismatch")
    # Keep everything after the low-difficulty block intact. The consensus
    # patch's block ends immediately before the normal vardiff accounting.
    replacement = '''            need = self.effective_min_diff()
            share_target = difficulty_to_target(need)
            if h_int > share_target:
                emit(
                    "WARN",
                    f"REJECT reason=low-difficulty worker={self.worker} job={job_id} "
                    f"height={job['height']} share_diff={share_work:.6f} "
                    f"required_diff={need:.6f} fixed_diff={self.diff:.6f} "
                    f"ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:64]}"
                )
                self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})
                self.shares_bad += 1
                _bump_worker(self.worker, False)
                _save_stats()
                return
'''
    text = text[:start] + replacement + text[end:]
else:
    replacement = '''            need = self.effective_min_diff()
            share_target = difficulty_to_target(need)
            if h_int > share_target:
                emit(
                    "WARN",
                    f"REJECT reason=low-difficulty worker={self.worker} job={job_id} "
                    f"height={job['height']} share_diff={share_work:.6f} "
                    f"required_diff={need:.6f} fixed_diff={self.diff:.6f} "
                    f"ntime={ntime_hex} nonce={nonce_hex} hash={hhex[:64]}"
                )
                self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})
                self.shares_bad += 1
                _bump_worker(self.worker, False)
                _save_stats()
                return
'''
    text = text.replace(old, replacement, 1)

if text.count('share_target = difficulty_to_target(need)') != 1:
    raise RuntimeError("share target guard mismatch")
if text.count('error": [23, "low difficulty", None]') != 1:
    raise RuntimeError("low-difficulty rejection mismatch")
if 'ACCEPT low-difficulty share' in text:
    raise RuntimeError("old low-difficulty acceptance path remains")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: fixed Stratum difficulty enforcement")
