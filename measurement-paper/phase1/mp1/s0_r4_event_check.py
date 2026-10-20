#!/usr/bin/env python3
"""MP1-A S0, ruling R4 (report only): is the CV-selected subset of the full-universe production 1A omnifile the same
set of events, with the same values, as a lateral-only 1A pass?

The omnifiles carry no event key, so events are compared by their full CV record: every scalar CV branch of the tree
(the production file's per-universe columns, names ending in _<digit(s)>, are ignored). For mc_signal_reco and
mc_background the rows with the CV pass flag set are compared as multisets of records (sorted lexicographically),
and also in file order. Rows without the pass flag (truth misses, other universes' entrants) are counted only.
Prints JSON; exit 0 = the CV-selected subsets are identical in every tree compared, 1 = they differ.

    python -I s0_r4_event_check.py <production.root> <lateral.root> [--out x.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys

import numpy as np
import uproot

PASS = {"mc_signal_reco": "sim_pass", "mc_background": "sim_background_pass"}


def cv_branches(tree) -> list[str]:
    return [k for k in tree.keys() if not re.search(r"_\d+$", k)]


def compare(prod, lat, name: str) -> dict:
    tp, tl = prod[name], lat[name]
    bp, bl = cv_branches(tp), cv_branches(tl)
    common = sorted(set(bp) & set(bl))
    ap = tp.arrays(common, library="np")
    al = tl.arrays(common, library="np")
    flag = PASS[name]
    sp, sl = ap[flag].astype(int) == 1, al[flag].astype(int) == 1
    out = {"cv_branches_prod_only": sorted(set(bp) - set(bl)), "cv_branches_lat_only": sorted(set(bl) - set(bp)),
           "entries_prod": int(tp.num_entries), "entries_lat": int(tl.num_entries),
           "cv_pass_rows_prod": int(sp.sum()), "cv_pass_rows_lat": int(sl.sum()),
           "non_pass_rows_prod": int((~sp).sum()), "non_pass_rows_lat": int((~sl).sum())}
    if sp.sum() != sl.sum():
        out["identical"] = False
        return out
    cols = [c for c in common if c != flag]
    Xp = np.stack([ap[c][sp].astype(float) for c in cols], axis=1)
    Xl = np.stack([al[c][sl].astype(float) for c in cols], axis=1)
    out["same_in_file_order"] = bool(np.array_equal(Xp, Xl, equal_nan=True))
    op, ol = np.lexsort(Xp.T[::-1]), np.lexsort(Xl.T[::-1])
    same = np.array_equal(Xp[op], Xl[ol], equal_nan=True)
    out["same_as_multiset"] = bool(same)
    if not same:
        diff = ~np.all((Xp[op] == Xl[ol]) | (np.isnan(Xp[op]) & np.isnan(Xl[ol])), axis=1)
        out["rows_differing_after_sort"] = int(diff.sum())
    out["columns_compared"] = cols
    out["identical"] = bool(same)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("production")
    ap.add_argument("lateral")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    prod, lat = uproot.open(a.production), uproot.open(a.lateral)
    res = {"production": a.production, "lateral": a.lateral,
           "trees": {t: compare(prod, lat, t) for t in PASS},
           "truth_denom_entries": {"prod": int(prod["mc_truth_denom"].num_entries),
                                   "lat": int(lat["mc_truth_denom"].num_entries)}}
    res["cv_selected_identical"] = all(v["identical"] for v in res["trees"].values())
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text + "\n")
    return 0 if res["cv_selected_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
