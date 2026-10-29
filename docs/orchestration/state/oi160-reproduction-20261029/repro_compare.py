#!/usr/bin/env python3
"""Compare the reproduced replicas with the two stored ones and read the predeclared outcome.

    repro_compare.py --a1 A1.npz --a2 A2.npz --b1 B1.npz --s-top S_top.npz --s-pre S_pre.npz --out readout.json

The agreement criterion is BITWISE equality of `xsec_flat` (float64, 65,856 values), its `shape`, and
`seed`. No tolerance enters a reading: a tolerance would let two different contracts "agree" at some
threshold chosen after the fact. Distances are reported only to describe a difference. The
declaration's §3 explains why exact equality is the right criterion here.

A missing output file (the old code's SKIPPED path writes nothing) is read as "no output", which
matches nothing. Exit 0 once the readout is written, 1 on a bad input.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

SCHEMA = "oi160-repro-readout/1"


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=False)
    return {"xsec_flat": np.asarray(d["xsec_flat"]), "shape": np.asarray(d["shape"]).tolist(),
            "seed": int(np.asarray(d["seed"])), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


def same(x, y):
    """The agreement criterion: bitwise-equal xsec_flat, equal shape and seed."""
    if x is None or y is None:
        return False
    return (x["shape"] == y["shape"] and x["seed"] == y["seed"]
            and x["xsec_flat"].dtype == y["xsec_flat"].dtype
            and x["xsec_flat"].tobytes() == y["xsec_flat"].tobytes())


def describe(x, y):
    """Descriptive only; never part of a reading."""
    if x is None or y is None:
        return {"equal": False, "note": "one side has no output"}
    a, b = x["xsec_flat"], y["xsec_flat"]
    if a.shape != b.shape:
        return {"equal": False, "note": "different lengths"}
    nz = (a != 0) | (b != 0)
    rel = np.abs(a[nz] - b[nz]) / np.maximum(np.abs(a[nz]), np.abs(b[nz])) if nz.any() else np.zeros(1)
    return {"equal": same(x, y), "n_differing": int((a != b).sum()), "n_union_nonzero": int(nz.sum()),
            "max_abs_diff": float(np.abs(a - b).max()), "median_rel_diff_union_nonzero": float(np.median(rel)),
            "max_rel_diff_union_nonzero": float(rel.max())}


def read(k1, k2, a_top, b_top):
    """The predeclared outcome table (declaration §3.3). Returns (outcome, sentence)."""
    if a_top and not b_top:
        return "R2", "the corrected code (07c18aee) reproduces the top-level replica bit for bit"
    if b_top and not a_top:
        return "R1", "the old code (07c18aee^) reproduces the top-level replica bit for bit"
    if a_top and b_top:
        return "VOID", "both codes reproduce the same file: the two contracts did not differ in this run"
    if not k1:
        return "VOID", "the corrected code does not reproduce itself, so no difference can be read"
    if k2:
        return "THIRD", ("the old code reproduces the June replica, but neither committed code reproduces "
                         "the top-level one: a third producer, or a July-only environment")
    return "INCONCLUSIVE", "today's environment reproduces neither stored replica"


def main(argv=None):
    ap = argparse.ArgumentParser()
    for name in ("a1", "a2", "b1", "s-top", "s-pre", "out"):
        ap.add_argument(f"--{name}", required=True)
    ap.add_argument("--s-top-sha256", required=True)
    ap.add_argument("--s-pre-sha256", required=True)
    a = ap.parse_args(argv)
    s_top, s_pre = load(a.s_top), load(a.s_pre)
    if s_top is None or s_pre is None:
        print("[repro_compare] a stored replica is missing"); return 1
    if s_top["sha256"] != a.s_top_sha256 or s_pre["sha256"] != a.s_pre_sha256:
        print("[repro_compare] a stored replica's sha256 is not the pinned one"); return 1
    a1, a2, b1 = load(a.a1), load(a.a2), load(a.b1)
    k1, k2 = same(a1, a2), same(b1, s_pre)
    a_top, b_top = same(a1, s_top), same(b1, s_top)
    outcome, sentence = read(k1, k2, a_top, b_top)
    readout = {
        "schema": SCHEMA,
        "criterion": "bitwise-equal xsec_flat (float64), equal shape and seed; no tolerance",
        "files": {k: (v["sha256"] if v else None) for k, v in
                  {"A1": a1, "A2": a2, "B1": b1, "S_top": s_top, "S_pre": s_pre}.items()},
        "K1_A1_equals_A2": k1,
        "K2_B1_equals_S_pre": k2,
        "A1_equals_S_top": a_top,
        "B1_equals_S_top": b_top,
        "A1_equals_S_pre": same(a1, s_pre),
        "outcome": outcome,
        "reading": sentence,
        "describe": {f"{x}_vs_{y}": describe(p, q) for (x, p), (y, q) in
                     [(("A1", a1), ("A2", a2)), (("B1", b1), ("S_pre", s_pre)), (("A1", a1), ("S_top", s_top)),
                      (("B1", b1), ("S_top", s_top)), (("A1", a1), ("S_pre", s_pre)), (("S_top", s_top), ("S_pre", s_pre))]},
        "not_citable_for": ["any other replica than seed 1", "C_ML or seedscan_split", "whether either contract is "
                            "correct", "any change to C_stat, C_ML or the adopted trunk"],
    }
    Path(a.out).write_text(json.dumps(readout, indent=2) + "\n")
    print(f"[repro_compare] outcome {outcome}: {sentence}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
