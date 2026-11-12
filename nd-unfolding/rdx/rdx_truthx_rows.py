#!/usr/bin/env python3
"""RDX C-TRUTHX (RDX-DECLARATION.md rev 3 §3, D1): on one patched omnifile, every mc_signal_reco row (appended
truth-only miss rows included) has exactly one mc_truth_denom row with the same (truthx_run, truthx_subrun,
truthx_evt), and its five truthx values equal that row's bitwise; truthx_enu > 0 and every truthx value is finite.

    rdx_truthx_rows.py PATCHED.root [--out x.json]

Prints the counts of signal rows, miss rows (sim == -9999 and sim_pass == 0), denom rows, matched rows and rows
without a partner. Both trees are read at their highest cycle (uproot). Exit 0 PASS, 1 FAIL, 2 could not check.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import rdx_common as C  # noqa: E402


def check(sig: dict, den: dict) -> dict:
    """sig, den: column dicts of mc_signal_reco (C1's branches, sim, sim_pass) and mc_truth_denom (C1's branches)."""
    bad = []
    sk, order = C.index_of(C.pack(*(den[k] for k in C.IDS)), "mc_truth_denom")
    qs = C.pack(*(sig[k] for k in C.IDS))
    C.index_of(qs, "mc_signal_reco")
    j = C.lookup(sk, order, qs)
    partnerless = int((j < 0).sum())
    if partnerless:
        bad.append(f"{partnerless} mc_signal_reco rows have no mc_truth_denom row with the same identity")
    ok = j >= 0
    for k in C.TRUTHX:
        a = np.asarray(sig[k], np.float64)
        if not np.all(np.isfinite(a)) or not np.all(np.isfinite(np.asarray(den[k], np.float64))):
            bad.append(f"{k}: non-finite values")
        diff = int((a[ok] != np.asarray(den[k], np.float64)[j[ok]]).sum())
        if diff:
            bad.append(f"{k}: {diff} matched rows differ from their mc_truth_denom row")
    for name, cols in (("mc_signal_reco", sig), ("mc_truth_denom", den)):
        if np.any(~(np.asarray(cols["truthx_enu"], np.float64) > 0)):
            bad.append(f"{name}: truthx_enu is not positive on every row")
    miss = (np.asarray(sig["sim"], np.float64) == -9999.0) & (np.asarray(sig["sim_pass"]) == 0)
    counts = {"signal_rows": int(qs.size), "miss_rows": int(miss.sum()), "reco_rows": int(qs.size - miss.sum()),
              "denom_rows": int(sk.size), "matched_rows": int(ok.sum()), "partnerless_rows": partnerless,
              "matched_miss_rows": int((ok & miss).sum())}
    return {"mode": "rdx-truthx-rows", "counts": counts, "failures": bad, "verdict": "PASS" if not bad else "FAIL"}


def uproot_reader(path: str, tree: str, cols: list[str]) -> dict:
    import uproot
    t = uproot.open(path)[tree]
    return {k: np.asarray(v) for k, v in t.arrays(cols, library="np").items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("patched")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    try:
        sig = uproot_reader(a.patched, "mc_signal_reco", [*C.C1_BRANCHES, "sim", "sim_pass"])
        den = uproot_reader(a.patched, "mc_truth_denom", list(C.C1_BRANCHES))
        res = dict(check(sig, den), file=a.patched)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"verdict": "COULD_NOT_CHECK", "error": repr(exc)}))
        return 2
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        a.out.write_text(text + "\n")
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
