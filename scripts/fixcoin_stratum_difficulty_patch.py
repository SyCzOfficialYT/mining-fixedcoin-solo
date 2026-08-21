#!/usr/bin/env python3
"""Enforce the configured FixedCoin Stratum share difficulty."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

# fixcoin_consensus_patch.py intentionally changes the original low-
# difficulty rejection into an accounting accept. Replace that generated
# section again. The generated adapter has an outer low-difficulty branch and
# an ``else:`` containing the normal share-credit path. Keep that branch
# structure intact; only replace the low-difficulty body.

def last_line_start_before(source, pattern, before):
    matches = list(re.finditer(pattern, source[:before], re.MULTILINE))
    return matches[-1].start() if matches else -1


def line_indent(source, pos):
    line_start = source.rfind("\n", 0, pos) + 1
    return re.match(r"[ \t]*", source[line_start:pos]).group(0)


guard = "if h_int > difficulty_to_target(need):"
guard_pos = text.find(guard)
if guard_pos < 0:
    raise RuntimeError("low-difficulty guard not found")

start = last_line_start_before(
    text,
    r'^[ \t]*need\s*=\s*self\.effective_min_diff\(\)\s*$',
    guard_pos,
)
if start < 0:
    raise RuntimeError("low-difficulty start marker not found")

# The normal share-credit path begins at this stable semantic anchor. We
# replace everything from ``need =`` up to that path, including the existing
# outer ``else:``. The replacement restores the same else branch explicitly.
end_match = re.search(
    r'^[ \t]*if\s+share_work\s*>=\s*self\.diff\s*:\s*$',
    text[guard_pos:],
    re.MULTILINE,
)
if not end_match:
    raise RuntimeError("low-difficulty block end marker not found")
end = guard_pos + end_match.start()

candidate = text[start:end]
if guard not in candidate:
    raise RuntimeError("low-difficulty guard not inside candidate block")
if "ACCEPT low-difficulty share" not in candidate:
    raise RuntimeError("low-difficulty acceptance marker not found")
if 'self.send({"id": mid, "result": True, "error": None})' not in candidate:
    raise RuntimeError("low-difficulty accept response missing")
if "self.shares_bad += 1" not in candidate:
    raise RuntimeError("low-difficulty accounting tail not found")

indent = line_indent(text, start)
replacement_body = '''need = self.effective_min_diff()
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
else:
'''
replacement = "".join(
    indent + line if line.strip() else line
    for line in replacement_body.splitlines(True)
)

text = text[:start] + replacement + text[end:]

if text.count("share_target = difficulty_to_target(need)") != 1:
    raise RuntimeError("share target guard mismatch")
if text.count('error": [23, "low difficulty", None]') != 1:
    raise RuntimeError("low-difficulty rejection mismatch")
if "ACCEPT low-difficulty share" in text:
    raise RuntimeError("old low-difficulty acceptance path remains")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"patched {PATH}: fixed Stratum difficulty enforcement")
