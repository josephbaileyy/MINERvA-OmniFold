#!/usr/bin/env python3
"""geanttw C2 and its pre-check (p2p3/AMENDMENT-P2P3.md A1, A3): our dumps against UOMNI, bitwise, on entry order.

    python3 -I c2_check.py pre  --uomni UOMNI --dump P0_PINNED_1L.root [--json OUT]
    python3 -I c2_check.py full --uomni UOMNI --dumps D_1A ... D_1P (hadd order) [--json OUT]

pre:  P0's pinned 1L dump against UOMNI's 1L slice: rows [OFFSET_1L[t], OFFSET_1L[t] + n) of each tree, for all 37
      slim branches. Both sides are pinned semantics, so the six GEANT truth targets are compared too.
full: the 12 patched dumps, concatenated in hadd order, against UOMNI's whole trees, for the 25 non-target slim
      branches: the 37 minus the six w_truth_GEANT_* in mc_signal_reco and in mc_truth_denom.

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
NOATIME_OPTIONAL = False
if os.environ.get("C2_TEST"):   # the tests' only door: no O_NOATIME needed, and a small 1L offset
    NOATIME_OPTIONAL = True
    OFFSET_1L = json.loads(os.environ["C2_TEST_OFFSET"])


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
    """{tree: {branch: verdict}} for UOMNI rows [start[t], start[t] + len(ours[t])) against our arrays."""
    res, bad = {}, []
    for t, names in branches.items():
        n = len(next(iter(ours[t].values())))
        stop = start[t] + n
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


def concat(parts, branches):
    return {t: {b: np.concatenate([p[t][b] for p in parts]) for b in names} for t, names in branches.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=("pre", "full"))
    ap.add_argument("--uomni", required=True)
    ap.add_argument("--dump")
    ap.add_argument("--dumps", nargs="+")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    try:
        if a.mode == "pre":
            if not a.dump or a.dumps:
                raise Unusable("pre takes --dump only")
            branches, start = SLIM, OFFSET_1L
            ours = read_dump(a.dump, branches)
        else:
            if a.dump or not a.dumps or len(a.dumps) != 12:
                raise Unusable("full takes --dumps with the 12 playlists' dumps, in hadd order")
            branches, start = NON_TARGET, {t: 0 for t in TREES}
            ours = concat([read_dump(d, branches) for d in a.dumps], branches)
        uomni = open_uomni(a.uomni)
        if a.mode == "full":
            short = {t: (len(next(iter(ours[t].values()))), uomni[t].num_entries) for t in TREES
                     if len(next(iter(ours[t].values()))) != uomni[t].num_entries}
            if short:
                raise Unusable(f"entry counts differ from UOMNI's: {short}")
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
