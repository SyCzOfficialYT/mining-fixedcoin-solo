#!/usr/bin/env python3
"""Enforce the configured FixedCoin Stratum share difficulty."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

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

# fixcoin_consensus_patch.py intentionally changes the original low-
# difficulty rejection into an accounting accept. Replace that whole
# generated low-difficulty section again, but locate its boundaries by the
# stable control-flow anchors instead of depending on exact generated text.
start_marker = '            need = self.effective_min_diff()\n'
end_marker = '            if share_work >= self.diff:\n'

start = text.find(start_marker)
if start < 0:
    raise RuntimeError("low-difficulty start marker not found")

end = text.find(end_marker, start)
if end < 0:
    raise RuntimeError("low-difficulty block end marker not found")

candidate = text[start:end]
if 'h_int > difficulty_to_target(need)' not in candidate:
    raise RuntimeError("low-difficulty guard not found")
if 'ACCEPT low-difficulty share' not in candidate:
    raise RuntimeError("low-difficulty acceptance marker not found")
if 'self.send({"id": mid, "result": True, "error": None})' not in candidate:
    raise RuntimeError("low-difficulty accept response missing")
if 'self.shares_bad += 1' not in candidate:
    raise RuntimeError("low-difficulty accounting tail not found")

text = text[:start] + replacement + text[end:]

if text.count('share_target = difficulty_to_target(need)') != 1:
    raise RuntimeError("share target guard mismatch")
if text.count('error": [23, "low difficulty", None]') != 1:
    raise RuntimeError("low-difficulty rejection mismatch")
if 'ACCEPT low-difficulty share' in text:
    raise RuntimeError("old low-difficulty acceptance path remains")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: fixed Stratum difficulty enforcement")
