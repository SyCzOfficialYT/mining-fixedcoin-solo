#!/usr/bin/env python3
"""Give every VarDiff transition a genuinely new Stratum job id.

A mining.set_difficulty message applies to the next mining.notify job. Several
ASIC firmwares will continue submitting against a previous job id if the pool
re-notifies the same id. This patch creates a connection-local child job for
every VarDiff transition while retaining a bounded set of old jobs for the
grace window.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()


def class_function_span(source, class_name, function_name):
    tree = ast.parse(source)
    cls = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name), None)
    if cls is None:
        raise RuntimeError(f"{class_name} class not found")
    fn = next((n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == function_name), None)
    if fn is None:
        raise RuntimeError(f"{class_name}.{function_name} not found")
    lines = source.splitlines(keepends=True)
    start = sum(map(len, lines[:fn.lineno - 1]))
    end = sum(map(len, lines[:fn.end_lineno]))
    return start, end


# The pinned FreeCash base uses either a direct store.current_id lookup or a
# two-step jid lookup. Match the actual generated implementation instead of
# assuming one exact upstream line.
old_direct = 'job = store.get(store.current_id)'
new_direct = 'job = store.get(getattr(self, "_job_override_id", None) or store.current_id)'
old_two_step = '''            with store.lock:
                jid = store.current_id
            job = store.get(jid) if jid else None'''
new_two_step = '''            with store.lock:
                jid = getattr(self, "_job_override_id", None) or store.current_id
            job = store.get(jid) if jid else None'''

if old_direct in text:
    if text.count(old_direct) != 1:
        raise RuntimeError(f"push_job direct job-selection marker mismatch: {text.count(old_direct)}")
    text = text.replace(old_direct, new_direct, 1)
elif old_two_step in text:
    if text.count(old_two_step) != 1:
        raise RuntimeError(f"push_job two-step job-selection marker mismatch: {text.count(old_two_step)}")
    text = text.replace(old_two_step, new_two_step, 1)
else:
    if 'getattr(self, "_job_override_id", None) or store.current_id' not in text:
        raise RuntimeError("push_job job-selection marker not found")

# Add connection-local rollover state without touching global round state.
init_start, init_end = class_function_span(text, "Client", "__init__")
init_fn = text[init_start:init_end]
init_marker = '        self.shares_since_retarget = 0'
if init_marker not in init_fn and 'self._job_override_id = None' not in init_fn:
    raise RuntimeError("Client __init__ rollover marker missing")
if 'self._job_override_id = None' not in init_fn:
    init_fn = init_fn.replace(
        init_marker,
        init_marker + '\n        self._job_override_id = None\n        self._diff_job_seq = 0\n        self._diff_job_ids = []',
        1,
    )
text = text[:init_start] + init_fn + text[init_end:]

# Replace the earlier same-job notify inserted by the difficulty patch. The
# ordering remains: set_difficulty first, then mining.notify for the new job.
set_start, set_end = class_function_span(text, "Client", "set_diff")
set_fn = text[set_start:set_end]
old_rollover = '        self.push_job(clean=True, force_refresh=False)'
if old_rollover not in set_fn:
    # Idempotent: if a previous application already installed the rollover,
    # verify its key markers and leave the function unchanged.
    if 'self.push_job(clean=False, force_refresh=False)' not in set_fn:
        raise RuntimeError("existing VarDiff job rollover marker missing")
else:
    new_rollover = '''        # Create a connection-local child job. Never change store.current_id:
        # other miners may be connected to the same round concurrently.
        self._job_override_id = None
        try:
            with store.lock:
                base = store.jobs.get(store.current_id)
                if base is not None:
                    self._diff_job_seq += 1
                    child_id = f"{base['id']}-d{self._diff_job_seq}-{self.en1.hex()}"
                    child = dict(base)
                    child["id"] = child_id
                    store.jobs[child_id] = child
                    self._diff_job_ids.append(child_id)
                    # Keep enough rollover jobs to cover in-flight ASIC work;
                    # effective_min_diff() decides whether the old target is
                    # still accepted during the configured grace interval.
                    while len(self._diff_job_ids) > 8:
                        stale_id = self._diff_job_ids.pop(0)
                        if stale_id != child_id:
                            store.jobs.pop(stale_id, None)
                    self._job_override_id = child_id
            self.push_job(clean=False, force_refresh=False)
        finally:
            self._job_override_id = None'''
    set_fn = set_fn.replace(old_rollover, new_rollover, 1)
    text = text[:set_start] + set_fn + text[set_end:]

for marker in (
    'getattr(self, "_job_override_id", None) or store.current_id',
    'self._job_override_id = None',
    'self._diff_job_seq = 0',
    'child_id = f"{base[\'id\']}-d{self._diff_job_seq}-{self.en1.hex()}"',
    'self.push_job(clean=False, force_refresh=False)',
):
    if marker not in text:
        raise RuntimeError(f"difficulty job epoch marker missing: {marker}")
if 'with store.lock:\n                base = store.get(store.current_id)' in text:
    raise RuntimeError("difficulty rollover would deadlock JobStore.lock via store.get()")
if 'self.push_job(clean=True, force_refresh=False)' in set_fn:
    raise RuntimeError("same-job clean VarDiff rollover remains")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: per-connection difficulty job epochs, non-clean rollover, bounded old-job retention, and lock-safe job selection")
