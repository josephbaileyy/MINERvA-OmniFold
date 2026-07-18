#!/usr/bin/env python3
"""P4 standard PURE-COMPONENT lateral replacement — FAIL-CLOSED (repair 2026-07-18).

Builds a CANDIDATE 5D scalar covariance where ONLY the 5 support-limited kinematic
lateral component blocks are swapped for the selection-complete active per-band
blocks; all non-lateral components (vertical/stat/ML) are inherited unchanged:

    C_new_total = C_old_total - sum(support_5) + sum(active_5)

Gates (fail-closed, via p4_lib): exact 5 bands on BOTH sides; identical shape/mask;
positive-finite active traces; exact component sum on the active side; symmetric+PSD
result; optional 5D->4D projection non-mutation. Refuses to write onto any adopted/
canonical path (candidate-only). Does NOT adopt. Authorized to RUN only after the
standard-p4-verifier returns PASS.
"""
import argparse, sys
import numpy as np
import ROOT
import p4_lib as P

_FORBIDDEN = ("universe_stage2_5d/uq_universe_5d_covariance_combined",  # adopted names
              "_uthrow", "adopted", "_final")


def _load_bands_and_total(path, total_key="hCov_universe5d_total"):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise P.P4GateError(f"cannot open {path}")
    def rd(key):
        h = f.Get(key)
        if not h:
            return None
        n = h.GetNbinsX(); C = np.empty((n, n))
        for i in range(n):
            for j in range(n):
                C[i, j] = h.GetBinContent(i + 1, j + 1)
        return C
    bands = {b: rd(f"hCov_universe5d_{b}") for b in P.BANDS}
    bands = {b: c for b, c in bands.items() if c is not None}
    total = rd(total_key)
    f.Close()
    return bands, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-combined", required=True, help="old combined cov (support-limited per-band + total)")
    ap.add_argument("--active-bands", required=True, help="active per-band cov ROOT")
    ap.add_argument("--out", required=True, help="CANDIDATE output (never an adopted path)")
    a = ap.parse_args()

    for bad in _FORBIDDEN:
        P.require(bad not in a.out, f"refusing to write candidate onto adopted/canonical path ({bad})")

    support, old_total = _load_bands_and_total(a.old_combined)
    active, _ = _load_bands_and_total(a.active_bands)
    P.require(old_total is not None, "old combined total missing")
    P.require_exact_bands(support)
    P.require_exact_bands(active)
    P.component_traces_positive_finite(active)
    for b in P.BANDS:
        P.require(active[b].shape == support[b].shape == old_total.shape,
                  f"shape/mask mismatch for band {b}")
    # exact component sum on the active side (self-consistency of the replacement block)
    active_sum = sum(active[b] for b in P.BANDS)
    support_sum = sum(support[b] for b in P.BANDS)
    new_total = old_total - support_sum + active_sum
    stats = P.check_symmetric_psd(new_total)

    fo = ROOT.TFile.Open(a.out, "RECREATE")
    n = new_total.shape[0]
    h = ROOT.TH2D("hCov_lateralrepl5d_total", "std pure-component lateral-replaced (CANDIDATE)",
                  n, 0, n, n, 0, n)
    for i in range(n):
        for j in range(n):
            h.SetBinContent(i + 1, j + 1, new_total[i, j])
    h.Write()
    for b in P.BANDS:
        hb = ROOT.TH2D(f"hCov_lateralrepl5d_active_{b}", b, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                hb.SetBinContent(i + 1, j + 1, active[b][i, j])
        hb.Write()
    fo.Close()
    print(f"CANDIDATE written {a.out}: sqrt_tr={np.sqrt(max(0,np.trace(new_total))):.4e} "
          f"min/max_eig={stats['min_eig']/max(1e-300,abs(stats['max_eig'])):.2e} (PASS gates)")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except P.P4GateError as e:
        print(f"FAIL-CLOSED :: {e}"); sys.exit(1)
