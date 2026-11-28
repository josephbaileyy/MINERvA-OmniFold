#!/usr/bin/env python3
"""geanttw C2's pre-check (p2p3/AMENDMENT-P2P3.md A1, A3; cov2d's (C3)): P0's pinned 1L dump against UOMNI's 1L slice.

    python3 -I c2_check.py pre --uomni UOMNI --dump P0_PINNED_1L.root [--json OUT]

pre:  rows [OFFSET_1L[t], OFFSET_1L[t] + N_1L[t]) of each tree (C4's 1L block; the dump must have exactly N_1L[t]), for all 37 slim branches, bitwise, on entry order. Both
      sides are pinned semantics, so the six GEANT truth targets are compared too. The full C2 runs inside the slim
      job's single pass over UOMNI (p3_slim.py build, cov2d's (C) amendment 3); this module gives it SLIM,
      NON_TARGET and same_bits.

The branch lists are cov2d's (C) grant: UOMNI is read for these branches only (c4/c4_header.py's SLIM). UOMNI is
read through an O_NOATIME file object, so a Python without O_NOATIME refuses. Values are compared as raw bytes
(bitwise, NaN-safe). Entry counts must agree. Exit 0 PASS, 1 FAIL (the mismatches are listed), 2 unusable input.
"""
import argparse
import json
import os
import sys

import numpy as np
import uproot

TREES = ("data", "mc_background", "mc_truth_denom", "mc_signal_reco")
G = [f"GEANT_{b}_{i}" for b in ("Neutron", "Pion", "Proton") for i in (0, 1)]
SLIM = {
    "data": ["measured", "measured_pz", "measured_pass"],
    "mc_background": ["sim_background", "sim_background_pz", "sim_background_pass"] + [f"w_bkg_{g}" for g in G],
    "mc_truth_denom": ["MC", "MC_pz"] + [f"w_truth_{g}" for g in G],
    "mc_signal_reco": ["MC", "MC_pz", "sim", "sim_pz", "sim_pass"] + [x for g in G for x in (f"w_truth_{g}", f"w_reco_{g}")],
}
TARGETS = {t: [f"w_truth_{g}" for g in G] for t in ("mc_truth_denom", "mc_signal_reco")}
NON_TARGET = {t: [b for b in SLIM[t] if b not in TARGETS.get(t, [])] for t in TREES}
OFFSET_1L = {"data": 2778489, "mc_background": 407731, "mc_truth_denom": 20716792, "mc_signal_reco": 20716792}  # c4.out
N_1L = {"data": 49872, "mc_background": 7820, "mc_truth_denom": 383848, "mc_signal_reco": 383848}   # c4.out, 1L's blocks
NOATIME_OPTIONAL = False
if os.environ.get("C2_TEST"):   # the tests' only door: no O_NOATIME needed, and a small 1L offset
    NOATIME_OPTIONAL = True
    OFFSET_1L = json.loads(os.environ["C2_TEST_OFFSET"])
    N_1L = json.loads(os.environ["C2_TEST_N"])


class Unusable(Exception):
    pass


def open_uomni(path):
    flag = getattr(os, "O_NOATIME", None)
    if flag is None and not NOATIME_OPTIONAL:
        raise Unusable("this Python has no O_NOATIME")
    return uproot.open(os.fdopen(os.open(path, os.O_RDONLY | (flag or 0)), "rb"))


def same_bits(a, b):
    if a.dtype != b.dtype or a.shape != b.shape:
        return False
    return np.array_equal(np.ascontiguousarray(a).view(np.uint8), np.ascontiguousarray(b).view(np.uint8))


def compare(uomni, ours, branches, start):
    """{tree: {branch: verdict}} for UOMNI rows [start[t], start[t] + N_1L[t]) against our arrays. Every tree of the
    dump must have exactly C4's 1L count before any UOMNI row is read, so the read is the granted 1L slice and
    nothing past it, and a truncated dump cannot pass on a matching prefix."""
    for t in branches:
        got = {len(v) for v in ours[t].values()}
        if got != {N_1L[t]}:
            raise Unusable(f"{t}: the dump has {sorted(got)} rows, not C4's 1L count {N_1L[t]}")
    res, bad = {}, []
    for t, names in branches.items():
        stop = start[t] + N_1L[t]
        if stop > uomni[t].num_entries:
            raise Unusable(f"{t}: rows [{start[t]}, {stop}) exceed UOMNI's {uomni[t].num_entries}")
        res[t] = {}
        for b in names:
            u = uomni[t][b].array(library="np", entry_start=start[t], entry_stop=stop)
            ok = same_bits(u, ours[t][b])
            res[t][b] = "EQUAL" if ok else "DIFFER"
            if not ok:
                bad.append(f"{t}:{b}")
    return res, bad


def read_dump(path, branches):
    f = uproot.open(path)
    out = {}
    for t, names in branches.items():
        if t not in f:
            raise Unusable(f"{path} has no tree {t}")
        missing = [b for b in names if b not in f[t]]
        if missing:
            raise Unusable(f"{path}:{t} lacks {missing}")
        out[t] = {b: f[t][b].array(library="np") for b in names}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=("pre",))
    ap.add_argument("--uomni", required=True)
    ap.add_argument("--dump")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    try:
        branches, start = SLIM, OFFSET_1L
        ours = read_dump(a.dump, branches) if a.dump else None
        if ours is None:
            raise Unusable("pre takes --dump")
        uomni = open_uomni(a.uomni)
        res, bad = compare(uomni, ours, branches, start)
    except Unusable as e:
        print(f"C2-{a.mode.upper()} UNUSABLE: {e}")
        return 2
    n = sum(len(v) for v in branches.values())
    verdict = "PASS" if not bad else "FAIL"
    print(f"C2-{a.mode.upper()} {verdict}: {n - len(bad)}/{n} branches bitwise equal")
    for b in bad:
        print(f"    DIFFER {b}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"mode": a.mode, "verdict": verdict, "branches": res, "differ": bad}, fh, indent=1, sort_keys=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
