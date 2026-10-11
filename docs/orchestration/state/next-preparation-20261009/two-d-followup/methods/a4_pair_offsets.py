#!/usr/bin/env python3
"""A4 items 2-3: the producer of the sigma_ML-scaled pair numbers, from the two-d-path operands only.

    python3 a4_pair_offsets.py --out results/a4_pair_offsets.json

Reads (immutable, committed): ``T/operands/remote_reduce_pairs.json`` (per sweep and band, the
signed pair displacement ``A_signed`` and half-width ``h_abs`` per reported cell),
``T/operands/remote_reduce.json`` (``sigma_abs.ml``, the absolute seed spread per cell) and
``T/operands/remote_reduce_pn.json`` (the July CV cross section ``pn_cv_xsec`` and the maximal
background change per band). Computes, per sweep (``adopted_fluxfix`` = May, ``purity_newomni`` =
July):

* for the NC-only and small bands: max |A|/x, median |A|/sigma_ML, median h/sigma_ML;
* the correlation of EtaNCEL's A with the common mode (cell-wise mean A) of the vertical bands,
  with and without EtaNCEL and MaNCEL themselves (both are the May offset; including them makes the
  offset correlate partly with itself);
* pairwise correlations of the small bands' A.

No data-event values are read or written: A, h and sigma_ML are unfolded cross-section differences.
"""
import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
T = HERE.parents[1] / "two-d-path" / "operands"
LATERAL = {"BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA", "Muon_Energy_MINOS"}
SMALL = ["EtaNCEL", "MaNCEL", "NormNCRES", "NormDISCC", "FrPiProd_N", "FrElas_pi", "FrAbs_N", "MaRES"]
SWEEPS = ["adopted_fluxfix", "purity_newomni"]


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    q = json.loads((T / "remote_reduce_pairs.json").read_text())["sweeps"]
    d = json.loads((T / "remote_reduce.json").read_text())
    p = json.loads((T / "remote_reduce_pn.json").read_text())
    s_ml = np.array(d["sigma_abs"]["ml"])
    x = np.array(p["pn_cv_xsec"])
    bkg = p["max_rel_bkg_change_vs_cv_by_band"]
    out = {"inputs": {f: __import__("hashlib").sha256((T / f).read_bytes()).hexdigest()
                      for f in ("remote_reduce_pairs.json", "remote_reduce.json", "remote_reduce_pn.json")},
           "n_cells": int(len(x)), "sweeps": {}}
    for sw in SWEEPS:
        pairs = q[sw]["pairs"]
        A = {b: np.array(pairs[b]["A_signed"]) for b in pairs}
        vertical = sorted(b for b in pairs if b not in LATERAL)
        rec = {"n_vertical_bands": len(vertical), "bands": {}}
        for b in SMALL:
            h = np.array(pairs[b]["h_abs"])
            rec["bands"][b] = {"max_rel_bkg_change": bkg.get(b), "max_absA_over_x": float(np.max(np.abs(A[b]) / x)),
                               "median_absA_over_sigma_ml": float(np.median(np.abs(A[b]) / s_ml)),
                               "median_h_over_sigma_ml": float(np.median(h / s_ml))}
        cm_all = np.mean([A[b] for b in vertical], axis=0)
        others = [b for b in vertical if b not in ("EtaNCEL", "MaNCEL")]
        cm_others = np.mean([A[b] for b in others], axis=0)
        rec["corr_EtaNCEL_with_vertical_common_mode"] = {"all_vertical": corr(A["EtaNCEL"], cm_all),
                                                         "excluding_EtaNCEL_MaNCEL": corr(A["EtaNCEL"], cm_others),
                                                         "n_excluding": len(others)}
        rec["pair_corr"] = {f"{u}~{v}": corr(A[u], A[v]) for u, v in
                            (("EtaNCEL", "MaNCEL"), ("EtaNCEL", "NormNCRES"), ("MaNCEL", "NormNCRES"),
                             ("EtaNCEL", "NormDISCC"))}
        rec["max_abs_EtaNCEL_minus_MaNCEL_over_sigma_ml"] = float(np.max(np.abs(A["EtaNCEL"] - A["MaNCEL"]) / s_ml))
        out["sweeps"][sw] = rec
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for sw, rec in out["sweeps"].items():
        c = rec["corr_EtaNCEL_with_vertical_common_mode"]
        print(sw, "vertical bands", rec["n_vertical_bands"], "corr(EtaNCEL, common mode) all %.3f excl %s" % (
            c["all_vertical"] or float("nan"), "%.3f" % c["excluding_EtaNCEL_MaNCEL"] if c["excluding_EtaNCEL_MaNCEL"] is not None else None))
        for b in ("EtaNCEL", "NormNCRES"):
            r = rec["bands"][b]
            print("  %s med|A|/sML %.3f max|A|/x %.3g" % (b, r["median_absA_over_sigma_ml"], r["max_absA_over_x"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
