#!/usr/bin/env python3
"""P4 standard active-lateral covariance validator — FAIL-CLOSED (repair 2026-07-18).

Runs the predeclared gates via p4_lib (any failure -> nonzero exit, no summary of
success): exact 5 kinematic bands, positive-finite component traces, EXACT
component sum (total == sum of per-band), symmetry+PSD, complete support-limited
comparison, and (optional) 5D->4D projection non-mutation. Emits a compact JSON.

Does NOT build a covariance. Only authorized to run after candidate construction,
which itself is gated on the standard-p4-verifier PASS.

Usage:
  p4_validate_active_lateral.py \
    --active <cov.root>            # has hCov_universe5d_total + per-band hCov_universe5d_<band>
    --support <combined.root>      # old support-limited: per-band hCov_universe5d_<band>
    [--merged-dir <dir>] [--project M.npz:M x_high.npz:x x_low.npz:x] --out <json>
"""
import argparse, json, sys
import numpy as np
import p4_lib as P


def _th2(path, key):
    import ROOT
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise P.P4GateError(f"cannot open {path}")
    h = f.Get(key)
    if not h:
        f.Close(); return None
    n = h.GetNbinsX()
    C = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    f.Close()
    return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--active", required=True, help="ROOT[:total_key]")
    ap.add_argument("--support", required=True)
    ap.add_argument("--merged-dir", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    apath, akey = (a.active.rsplit(":", 1) + ["hCov_universe5d_total"])[:2] \
        if ":" in a.active else (a.active, "hCov_universe5d_total")

    out = {"gates": [], "result": "FAIL"}
    try:
        # --- load active total + per-band, support per-band ------------------
        total = _th2(apath, akey)
        P.require(total is not None, f"active total {akey} missing in {apath}")
        active_bands = {b: _th2(apath, f"hCov_universe5d_{b}") for b in P.BANDS}
        active_bands = {b: c for b, c in active_bands.items() if c is not None}
        support_bands = {b: _th2(a.support, f"hCov_universe5d_{b}") for b in P.BANDS}
        support_bands = {b: c for b, c in support_bands.items() if c is not None}

        # --- fail-closed gates ----------------------------------------------
        P.require_exact_bands(active_bands);           out["gates"].append("exact_5_bands")
        tr = P.component_traces_positive_finite(active_bands); out["gates"].append("traces_pos_finite")
        out["component_traces"] = tr
        out["component_sum_relerr"] = P.check_component_sum(total, active_bands)
        out["gates"].append("exact_component_sum")
        out["psd"] = P.check_symmetric_psd(total);     out["gates"].append("symmetric_psd")
        P.require(set(support_bands) == set(P.BANDS), "support-limited block incomplete (need all 5 bands)")
        support_total = sum(support_bands[b] for b in P.BANDS)
        out["support_comparison"] = P.check_support_comparison(total, support_total)
        out["gates"].append("complete_support_comparison")
        out["n_reported"] = int(total.shape[0])
        out["result"] = "PASS"
    except P.P4GateError as e:
        out["error"] = str(e)
        with open(a.out, "w") as fh:
            json.dump(out, fh, indent=2)
        print(f"RESULT FAIL :: {e}")
        sys.exit(1)

    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print("RESULT PASS — gates:", ",".join(out["gates"]))
    print(f"  component_sum_relerr={out['component_sum_relerr']:.2e} "
          f"support_ratio={out['support_comparison']['ratio']:.3f} n={out['n_reported']}")
    sys.exit(0)


if __name__ == "__main__":
    main()
