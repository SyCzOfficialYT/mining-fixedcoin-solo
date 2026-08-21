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

# fixcoin_consensus_patch.py intentionally converts the original low-
# difficulty rejection into an accounting accept. Do not depend on exact
# whitespace or on the presence of the original `need = ...` marker: the
# generated adapter has changed shape several times during the repair work.
accept_marker = 'ACCEPT low-difficulty share'
accept_pos = text.find(accept_marker)
if accept_pos < 0:
    raise RuntimeError("low-difficulty acceptance marker not found")

# Find the beginning of the generated low-difficulty section. Prefer the
# effective difficulty assignment when present; otherwise walk backwards to
# the nearest conditional/hash guard surrounding the acceptance marker.
section_start = text.rfind('            need = self.effective_min_diff()\n', 0, accept_pos)
if section_start < 0:
    section_start = text.rfind('            if h_int > difficulty_to_target(need):', 0, accept_pos)
if section_start < 0:
    # Last-resort structural fallback: locate the line containing the
    # acceptance emit and back up to the nearest four-space/12-space block
    # boundary. This handles generated variants where the `need` assignment
    # is folded into another helper.
    line_start = text.rfind('\n', 0, accept_pos) + 1
    block_marker = '            '
    section_start = text.rfind('\n' + block_marker, 0, line_start)
    section_start = section_start + 1 if section_start >= 0 else line_start

# The normal share accounting resumes at vardiff timing. Everything after
# that point belongs to the valid-share path and must remain untouched.
end_marker = '            self.vardiff_buf.append(time.time())\n'
section_end = text.find(end_marker, accept_pos)
if section_end < 0:
    raise RuntimeError("low-difficulty block end marker not found")

candidate = text[section_start:section_end]
if 'ACCEPT low-difficulty share' not in candidate:
    raise RuntimeError("low-difficulty block content mismatch")
if 'self.send({"id": mid, "result": True, "error": None})' not in candidate:
    raise RuntimeError("low-difficulty accept response missing")

text = text[:section_start] + replacement + text[section_end:]

if text.count('share_target = difficulty_to_target(need)') != 1:
    raise RuntimeError("share target guard mismatch")
if text.count('error": [23, "low difficulty", None]') != 1:
    raise RuntimeError("low-difficulty rejection mismatch")
if 'ACCEPT low-difficulty share' in text:
    raise RuntimeError("old low-difficulty acceptance path remains")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: fixed Stratum difficulty enforcement")
