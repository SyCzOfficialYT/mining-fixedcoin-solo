#!/usr/bin/env python3
"""Patch Stratum reject telemetry to distinguish current/effective difficulty."""
from pathlib import Path

PATH = Path('/app/stratum/server_full.py')
text = PATH.read_text()

old = 'emit("WARN", f"REJECT reason=low-difficulty worker={self.worker} job={job_id} height={height} share_diff={share_diff:.6f} required_diff={required_diff:.6f} fixed_diff={self.diff:.6f} ntime={ntime:08x} nonce={nonce:08x} hash={hash_hex}")'
new = 'emit("WARN", f"REJECT reason=low-difficulty worker={self.worker} job={job_id} height={height} share_diff={share_diff:.6f} required_diff={required_diff:.6f} current_diff={self.diff:.6f} previous_diff={self.diff_prev:.6f} grace_active={int(time.time() - self.diff_changed_at < DIFF_GRACE_SEC)} ntime={ntime:08x} nonce={nonce:08x} hash={hash_hex}")'

if old not in text:
    raise SystemExit('target reject telemetry line not found; refusing to patch')

PATH.write_text(text.replace(old, new, 1))
print('patched reject telemetry: current_diff/previous_diff/grace_active')
