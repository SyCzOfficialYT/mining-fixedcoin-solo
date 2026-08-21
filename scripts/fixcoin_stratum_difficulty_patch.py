#!/usr/bin/env python3
"""Enforce the configured FixedCoin Stratum share difficulty.

The consensus patch intentionally keeps cryptographically valid low-difficulty
shares for solo accounting. The fixed-difficulty Stratum policy is applied
after that patch and converts those accounting accepts into real Stratum
rejections when the submitted PoW is below the advertised target.

Network/block validation remains handled by FixedCoin Core.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

# fixcoin_consensus_patch.py deliberately rewrites the low-difficulty branch to
# accept the share for solo accounting. This patch runs immediately afterwards,
# so match that post-consensus form rather than the pre-consensus rejection.
pattern = re.compile(
    r'''(?ms)^            need = self\.effective_min_diff\(\)\n'
    r'''\s*emit\("INFO", f"ACCEPT low-difficulty share worker=\{self\.worker\} job=\{job_id\} height=\{job\['height'\]\} share_diff=\{share_work:\.6f\} advertised_diff=\{need:\.6f\} fixed_diff=\{self\.diff:\.6f\} ntime=\{ntime_hex\} nonce=\{nonce_hex\} hash=\{hhex\[:24\]\}"\)\n'
    r'''\s*_bump_worker\(self\.worker, ok=True\)\n'
    r'''\s*_record_share\(self\.worker, share_work, self\.diff, job\.get\("network_diff", 0\.0\), hhex, job\["height"\], accepted=True\)\n'
    r'''\s*_add_round_share\(self\.diff, share_work, job\.get\("network_diff", 0\.0\), job\["height"\]\)\n'
    r'''\s*self\.send\(\{"id": mid, "result": True, "error": None\}\)'''
)

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
                return'''

count = len(pattern.findall(text))
if count != 1:
    raise RuntimeError(f"low-difficulty post-consensus block mismatch: expected 1, found {count}")

text, count = pattern.subn(replacement, text, count=1)

# Regression guards: the generated adapter must reject below-target shares and
# must no longer contain the old accounting/acceptance path.
if text.count('share_target = difficulty_to_target(need)') != 1:
    raise RuntimeError("share target guard mismatch")
if text.count('error": [23, "low difficulty", None]') != 1:
    raise RuntimeError("low-difficulty rejection mismatch")
if 'ACCEPT low-difficulty share' in text:
    raise RuntimeError("old low-difficulty acceptance path remains")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: fixed Stratum difficulty enforcement")
