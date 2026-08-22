#!/usr/bin/env python3
"""Validate strict FixedCoin Stratum share-difficulty enforcement and job stability."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

# Normal Stratum shares below the advertised fixed pool difficulty must remain
# rejected. A genuine network-valid block candidate is checked separately by
# the block-target path and must never be accepted through this share path.
required_rejection = 'self.send({"id": mid, "result": False, "error": [23, "low difficulty", None]})'
if text.count(required_rejection) != 1:
    raise RuntimeError(
        f"generated Stratum low-difficulty rejection mismatch: expected 1, found {text.count(required_rejection)}"
    )

if "ACCEPT low-difficulty" in text:
    raise RuntimeError("generated Stratum low-difficulty acceptance bypass remains")

# Do not search the entire generated adapter for a generic success response:
# mining.extranonce.subscribe and the normal accepted-share path legitimately
# return result=True. Validate only the actual low-difficulty branch.
low_diff_marker = "if h_int > difficulty_to_target(need):"
accepted_share_marker = "if share_work >= self.diff:"
if low_diff_marker not in text or accepted_share_marker not in text:
    raise RuntimeError("generated Stratum low-difficulty branch markers are missing")
low_diff_branch = text.split(low_diff_marker, 1)[1].split(accepted_share_marker, 1)[0]
if 'result": True, "error": None' in low_diff_branch:
    raise RuntimeError("generated Stratum low-difficulty branch contains a success response")

# FixedCoin must not create a second Stratum job merely because getblocktemplate
# changes transaction selection or coinbase fees while the chain height is still
# the same. That produces a clean mining.notify without a real new round and can
# make ASICs submit against a freshly replaced job with hashes below the local
# share target. Keep the current job stable for the complete block height.
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

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: strict low-difficulty rejection and one stable Stratum job per block height")
