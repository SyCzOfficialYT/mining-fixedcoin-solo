#!/usr/bin/env python3
"""Regression tests for generated FixedCoin Stratum authorization."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import stratum.server_full as s

sent = []


def fake_send(self, obj):
    sent.append(obj)


def fake_push_job(self, clean=True, force_refresh=False):
    return None


s.Client.send = fake_send
s.Client.push_job = fake_push_job


def run_case(name, family, password, expected_diff, expected_vardiff, expected_fixed):
    sent.clear()
    c = s.Client.__new__(s.Client)
    c.worker = "?"
    c.miner_family = family
    c.miner_variant = "v2" if family else ""
    c.miner_version = "test"
    c.vardiff_enabled = bool(s.VARDIFF)
    c.low_hash_vardiff = False
    c.diff_from_password = not bool(s.VARDIFF)
    c.diff = s.FIXED_DIFF
    c.diff_prev = c.diff
    c.diff_changed_at = 0.0
    c.shares_since_retarget = 0
    c.vardiff_buf = []
    c.handle_authorize(1, ["fix-test.worker", password])

    assert abs(float(c.diff) - float(expected_diff)) < 1e-12, (name, c.diff, expected_diff)
    assert bool(c.vardiff_enabled) is expected_vardiff, (name, c.vardiff_enabled)
    assert bool(c.diff_from_password) is expected_fixed, (name, c.diff_from_password)
    assert any(
        x.get("method") == "mining.set_difficulty"
        and abs(float(x["params"][0]) - float(expected_diff)) < 1e-12
        for x in sent
    ), (name, sent)


run_case("ASIC fixed", "", "", s.FIXED_DIFF, False, True)
run_case("password-x VarDiff", "", "x", max(s.START_DIFF, s.MIN_DIFF), True, False)
run_case("explicit fixed", "", "d=20000", 20000, False, True)

low_hash_diff = float(s.cfg["pool"].get("nmminer_difficulty", 0.001))
run_case("NMMiner low-hash VarDiff", "NMMiner", "x", low_hash_diff, True, False)
assert s.Client.__new__(s.Client) is not None
run_case("NerdMiner low-hash VarDiff", "NerdMiner", "x", low_hash_diff, True, False)
run_case("NerdQAxe++ low-hash VarDiff", "NerdQAxe", "x", low_hash_diff, True, False)

# The low-hash controller must remain float-capable below integer ASIC
# difficulty. Verify it can move 0.001 -> 0.0013 and emit Stratum difficulty.
sent.clear()
c = s.Client.__new__(s.Client)
c.worker = "fix-test.nerd"
c.low_hash_vardiff = True
c.vardiff_enabled = True
c.diff_from_password = False
c.diff = low_hash_diff
c.diff_prev = c.diff
c.diff_changed_at = 0.0
c.shares_since_retarget = 0
c.vardiff_buf = []
c._set_low_hash_diff(low_hash_diff * 1.3, "regression")
assert c.diff > low_hash_diff, c.diff
assert any(
    x.get("method") == "mining.set_difficulty"
    and abs(float(x["params"][0]) - float(c.diff)) < 1e-12
    for x in sent
), sent

# Block validation must remain a network-target check, not a share-target check.
source = Path(s.__file__).read_text()
assert 'if h_int <= job["target"]:' in source

print("Stratum authorization regression tests: PASS")
