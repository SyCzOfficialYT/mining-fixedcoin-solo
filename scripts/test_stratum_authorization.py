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
run_case("NMMiner", "NMMiner", "x", float(s.cfg["pool"].get("nmminer_difficulty", 0.001)), False, True)
run_case("NerdMiner", "NerdMiner", "x", float(s.cfg["pool"].get("nmminer_difficulty", 0.001)), False, True)
run_case("NerdQAxe++", "NerdQAxe", "x", float(s.cfg["pool"].get("nmminer_difficulty", 0.001)), False, True)

print("Stratum authorization regression tests: PASS")
