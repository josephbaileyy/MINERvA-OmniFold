#!/usr/bin/env python3
"""Grade the C_ML tolerance run's reproductions against the unseen stored split replicas, by the predeclared table.

    cml_compare.py --out-dir OUT --stored-dir STORED --seeds seeds.tsv --readout readout.json

AGREEMENT (DECLARATION.md §3.2), fixed before any graded replica is opened:
    two files agree iff they have equal `shape`, `split_seed` and `train_frac`, the SAME zero pattern in `xsec_flat`,
    and max over the bins nonzero in either of |x - y| / max(|x|, |y|)  <=  TAU = 1e-8.
VALIDITY: the fresh same-code floor (task 0, split seed 1, A run twice) must be <= TAU / 100 with an equal zero
pattern, else every reading is VOID.
SEPARATION (per seed, read from A against B): SEPARATED at >= 100 * TAU; COINCIDENT when A and B agree by the
criterion above; anything between is VOID. 07c18aee changes only LightGBM's random_state in seedscan_split.py, so
COINCIDENT is a live outcome here, and it is read, not voided: see seed_verdict.
Exit 0 once the readout is written; 1 on a bad input (a stored file not matching its pinned digest).
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

SCHEMA = "oi160-cml-tolerance-readout/1"
TAU = 1e-8
FLOOR_LIMIT = TAU / 100
SEPARATION_MIN = 100 * TAU
TRAIN_FRAC = 0.8


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=False)
    return {"x": np.asarray(d["xsec_flat"], float), "shape": np.asarray(d["shape"]).tolist(),
            "split_seed": int(np.asarray(d["split_seed"])), "train_frac": float(np.asarray(d["train_frac"])),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


def max_rel(a, b):
    nz = (a != 0) | (b != 0)
    if not nz.any():
        return 0.0
    return float(np.max(np.abs(a[nz] - b[nz]) / np.maximum(np.abs(a[nz]), np.abs(b[nz]))))


def measure(x, y):
    """The quantities the criterion reads, plus description."""
    if x is None or y is None:
        return {"comparable": False, "agree": False, "note": "one side has no output"}
    if x["shape"] != y["shape"] or x["x"].shape != y["x"].shape:
        return {"comparable": False, "agree": False, "note": "different shapes"}
    a, b = x["x"], y["x"]
    zero_equal = bool(np.array_equal(a == 0, b == 0))
    mr = max_rel(a, b)
    nz = (a != 0) | (b != 0)
    med = float(np.median(np.abs(a[nz] - b[nz]) / np.maximum(np.abs(a[nz]), np.abs(b[nz])))) if nz.any() else 0.0
    ids_equal = x["split_seed"] == y["split_seed"] and x["train_frac"] == y["train_frac"]
    return {"comparable": True, "ids_equal": ids_equal, "zero_pattern_equal": zero_equal,
            "max_rel_union_nonzero": mr, "median_rel_union_nonzero_descriptive": med,
            "agree": bool(ids_equal and zero_equal and mr <= TAU)}


def separation(a_vs_b):
    """SEPARATED, COINCIDENT or GREY for one seed's two codes."""
    if not a_vs_b.get("comparable"):
        return "GREY"
    if a_vs_b["agree"]:
        return "COINCIDENT"
    if a_vs_b["max_rel_union_nonzero"] >= SEPARATION_MIN:
        return "SEPARATED"
    return "GREY"


def seed_verdict(a_vs_s, b_vs_s, a_vs_b):
    """CORRECTED / OLD / NEITHER / INERT / VOID for one graded seed (DECLARATION.md §3.3)."""
    if not (a_vs_s["comparable"] and b_vs_s["comparable"]):
        return "VOID", "a reproduction is missing or not comparable"
    sep = separation(a_vs_b)
    a, b = a_vs_s["agree"], b_vs_s["agree"]
    if sep == "GREY":
        return "VOID", "the two codes differ by more than TAU but less than 100 TAU"
    if sep == "COINCIDENT":
        if a and b:
            return "INERT", "both codes reproduce it, and they agree with each other: the contract does not change it"
        if not a and not b:
            return "NEITHER", "the two codes agree with each other, and neither reproduces it within tolerance"
        return "VOID", "the codes agree with each other but only one reproduces it: a boundary case"
    if a and not b:
        return "CORRECTED", "the corrected code (07c18aee) reproduces it within tolerance; the old code does not"
    if b and not a:
        return "OLD", "the old code (07c18aee^) reproduces it within tolerance; the corrected code does not"
    if a and b:
        return "VOID", "both separated codes agree with it, which the criterion cannot produce"
    return "NEITHER", "neither committed code reproduces it within tolerance"


def producer_verdict(verdicts):
    """One producer's reading from its seeds' verdicts."""
    real = [v for v in verdicts if v != "VOID"]
    if not real:
        return "VOID"
    if len(set(real)) == 1:
        return real[0] + (" (with a VOID seed)" if len(real) < len(verdicts) else "")
    return "MIXED"


def overall_verdict(floor_ok, producers):
    real = {v.split(" ")[0] for v in producers.values() if v != "VOID"}
    if not floor_ok or not real:
        return "VOID"
    if len(real) == 1 and real != {"MIXED"}:
        return real.pop()               # every non-VOID producer reads the same
    return "MIXED"                      # producers disagree, or one producer's seeds do


def main(argv=None):
    ap = argparse.ArgumentParser()
    for name in ("out-dir", "stored-dir", "seeds", "readout"):
        ap.add_argument(f"--{name}", required=True)
    a = ap.parse_args(argv)
    out, stored = Path(a.out_dir), Path(a.stored_dir)
    rows = list(csv.DictReader(open(a.seeds), delimiter="\t"))

    c1, c2 = load(out / "control_A1.npz"), load(out / "control_A2.npz")
    floor = measure(c1, c2)
    floor_ok = bool(floor.get("comparable") and floor["ids_equal"] and floor["zero_pattern_equal"]
                    and floor["max_rel_union_nonzero"] <= FLOOR_LIMIT)

    seeds, by_producer = [], {}
    for r in rows:
        s = int(r["seed"])
        st = load(stored / f"res_split_{s}.npz")
        if st is None or st["sha256"] != r["sha256"]:
            print(f"[cml_compare] stored res_split_{s}.npz is missing or not the pinned file"); return 1
        ra, rb = load(out / f"s{s}_A.npz"), load(out / f"s{s}_B.npz")
        a_s, b_s, a_b = measure(ra, st), measure(rb, st), measure(ra, rb)
        v, why = seed_verdict(a_s, b_s, a_b) if floor_ok else ("VOID", "the fresh floor exceeds TAU/100")
        seeds.append({"seed": s, "producer": r["producer"], "verdict": v, "why": why,
                      "separation": separation(a_b),
                      "stored_train_frac_is_declared": st["train_frac"] == TRAIN_FRAC,
                      "A_vs_stored": a_s, "B_vs_stored": b_s, "A_vs_B": a_b,
                      "files": {"A": ra and ra["sha256"], "B": rb and rb["sha256"], "stored": st["sha256"]}})
        by_producer.setdefault(r["producer"], []).append(v)
    producers = {p: producer_verdict(v) for p, v in by_producer.items()}
    readout = {
        "schema": SCHEMA,
        "criterion": {"tau_max_rel_union_nonzero": TAU, "zero_pattern": "must be identical",
                      "floor_limit": FLOOR_LIMIT, "separation_min": SEPARATION_MIN},
        "fresh_floor_control_split1_A_twice": floor, "fresh_floor_ok": floor_ok,
        "seeds": seeds, "producers": producers, "overall": overall_verdict(floor_ok, producers),
        "not_citable_for": ["seeds not graded here, beyond what their producer's verdict covers", "C_stat",
                            "whether either contract is correct", "any change to C_ML, C_stat or the trunk"],
    }
    Path(a.readout).write_text(json.dumps(readout, indent=2) + "\n")
    print(f"[cml_compare] floor_ok={floor_ok} producers={producers} overall={readout['overall']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
