#!/usr/bin/env python3
"""Give every VarDiff transition a genuinely new Stratum job id.

A mining.set_difficulty message applies to the next job. Re-notifying the
same job id is not enough for several ASIC firmwares: they can keep submitting
shares against the previous target. This patch creates a per-connection child
job from the current round, keeps the old job alive (clean=false), and sends
the new difficulty together with the new job id. The existing grace logic can
therefore accept in-flight shares from the previous target without poisoning
the next target.
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
    start = sum(map(len, lines[: fn.lineno - 1]))
    end = sum(map(len, lines[: fn.end_lineno]))
    return start, end


# push_job normally selects the global current job. During a difficulty
# rollover we temporarily point this connection at a child job instead.
old_job_select = 'job = store.get(store.current_id)'
new_job_select = 'job = store.get(getattr(self, "_job_override_id", None) or store.current_id)'
if text.count(old_job_select) != 1:
    raise RuntimeError(f"push_job job-selection marker mismatch: {text.count(old_job_select)}")
text = text.replace(old_job_select, new_job_select, 1)

# Add connection-local rollover state without touching the global round state.
init_start, init_end = class_function_span(text, "Client", "__init__")
init_fn = text[init_start:init_end]
init_marker = '        self.shares_since_retarget = 0'
if init_marker not in init_fn:
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
    raise RuntimeError("existing VarDiff job rollover marker missing")
new_rollover = '''        # Create a connection-local child job. Do not change store.current_id:
        # other miners may be connected to the same round concurrently.
        self._job_override_id = None
        try:
            with store.lock:
                base = store.get(store.current_id)
                if base is not None:
                    self._diff_job_seq += 1
                    child_id = f"{base['id']}-d{self._diff_job_seq}-{self.en1.hex()}"
                    child = dict(base)
                    child["id"] = child_id
                    store.jobs[child_id] = child
                    self._diff_job_ids.append(child_id)
                    # Keep a small tail of rollover jobs for in-flight shares.
                    # effective_min_diff() controls whether an old target is
                    # still acceptable; pruning is only a memory bound.
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

if 'child_id = f"{base[\'id\']}-d{self._diff_job_seq}-{self.en1.hex()}"' not in text:
    raise RuntimeError("per-connection difficulty job id generation missing")
if 'self.push_job(clean=False, force_refresh=False)' not in text:
    raise RuntimeError("non-clean difficulty rollover notify missing")
if 'self._job_override_id' not in text:
    raise RuntimeError("job override state missing")
if 'self.push_job(clean=True, force_refresh=False)' in text:
    raise RuntimeError("same-job clean rollover remains")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: per-connection difficulty job epochs, non-clean rollover, and bounded old-job retention")
