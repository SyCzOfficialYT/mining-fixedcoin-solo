#!/usr/bin/env python3
"""Restore FixedCoin's canonical network-difficulty scale after consensus patching.

FixedCoin consensus uses its own powLimit for proof-of-work validation, but the
RPC/Explorer difficulty number is Bitcoin-compatible difficulty-1:
0x00000000ffff0000... / target.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

wrong = "net_diff = fixedcoin_target_to_difficulty(bits_to_target(nbits))"
correct = "net_diff = target_to_difficulty(bits_to_target(nbits))"

count = text.count(wrong)
if count != 1:
    raise RuntimeError(f"network difficulty marker mismatch: expected 1, found {count}")

text = text.replace(wrong, correct, 1)

# Regression: FixedCoin Core's GetDifficulty() uses the Bitcoin difficulty-1
# target, exactly like the explorer. Block 38897 (bits 19600c8f) is a known
# FixedCoin reference and must evaluate to 44,715,709.8033.
DIFF1_TARGET = 0x00000000FFFF0000000000000000000000000000000000000000000000000000

def bits_to_target(nbits):
    bits = int(nbits, 16) if isinstance(nbits, str) else int(nbits)
    exponent = bits >> 24
    mantissa = bits & 0x007FFFFF
    if exponent <= 3:
        return mantissa >> (8 * (3 - exponent))
    return mantissa << (8 * (exponent - 3))

def canonical_difficulty(nbits):
    return DIFF1_TARGET / bits_to_target(nbits)

reference = canonical_difficulty("19600c8f")
if abs(reference - 44715709.803317755) > 0.01:
    raise RuntimeError(f"difficulty regression failed: {reference}")

if wrong in text:
    raise RuntimeError("wrong powLimit-based network difficulty formula remains")
if text.count(correct) != 1:
    raise RuntimeError("canonical network difficulty formula missing or duplicated")

PATH.write_text(text)
print(f"patched network difficulty: canonical FixedCoin/Core scale (diff={reference:.4f})")
