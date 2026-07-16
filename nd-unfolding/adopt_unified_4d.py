#!/usr/bin/env python3
"""Adopt the rigorous 4D unified-throw systematic into the published combined 4D covariance.

The unified throw (uq_4d/unified_throw_cov_4d.root, 160 joint re-unfolds of the 12 knob bands
+ flux) measures the per-bin systematic variance INCLUDING the nonlinear cross-band term the
block-sum drops. But with 160 throws << 4830 bins, C_unified is rank-160 -- a noisy estimate
of the full 4830x4830 matrix. Swapping the whole matrix in directly breaks positive-definiteness
(verified: 2285 negative eigenvalues, most-negative = -1.25% of max). So we adopt the throw's
fractional MAGNITUDE inflation (per-bin variance, which converges fast and carries the nonlinear
cross-term) and transfer it onto the SWEEP's own vertical block -- exactly the engine-independent
fractional-transfer logic used for the PET lateral band (task 15). Using the sweep's block as the
carrier (not the bank block) is what keeps the result PSD: the throw's own bank block-sum and the
sweep block-sum are two DIFFERENT estimators, so subtracting the bank block from the sweep-based
combined leaves uncancelled negative directions; subtracting the SWEEP vertical block does not.

    g_i = sqrt( max(sigma_uni_i^2, sigma_blockbank_i^2) ) / sigma_blockbank_i   >= 1   (from the throw)
    C_vert_adopt = G C_vert_sweep G              (G = diag(g);  PSD, sweep correlation preserved)
    C_combined_new = (C_combined_old - C_vert_sweep) + C_vert_adopt
                   = (C_other_bands + C_stat + C_ML) + G C_vert_sweep G        <- PSD by construction

C_vert_sweep = sum of the 13 vertical per-band covs (12 knobs + Flux) the throw covers, taken
from the combined file's per-band hCov_universe4d_<band> (so C_comb - C_vert_sweep is a sum of
PSD pieces from the same sweep). The conservative max() never UNDER-covers relative to the block
baseline in the ~50% of (noisy) bins where the throw dips below block; it inflates where the
nonlinear cross-term is real (the high-pT / low-E_avail corner, top 1% of bins = 78% of excess).

  python adopt_unified_4d.py        # writes uq_4d/.../uq_universe_4d_covariance_combined_uthrow.root
"""
import argparse
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _th2(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    b = np.frombuffer(h.GetArray(), dtype=np.float64, count=(nx + 2) * (ny + 2)).reshape(ny + 2, nx + 2)
    return b[1:ny + 1, 1:nx + 1].T.copy()


def main():
    import ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--uthrow", default="uq_4d/unified_throw_cov_4d.root")
    ap.add_argument("--combined", default="uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined.root")
    ap.add_argument("--prod", default="products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--out", default="uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow.root")
    ap.add_argument("--cv-centered", action="store_true",
                    help="F7 CV-centered variant: add per-bin joint mean_shift^2 to the unified "
                         "variance (default is mean-centered, diag(C_unified) only). Parity with "
                         "adopt_unified_5d.py --cv-centered.")
    args = ap.parse_args()

    # the 13 vertical bands the unified throw covers (12 knobs + Flux)
    VERT_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2", "LowQ2",
                  "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi", "Flux"]

    fu = ROOT.TFile.Open(args.uthrow)
    C_uni = _th2(fu.Get("C_unified"))
    C_block = _th2(fu.Get("C_blocksum"))      # bank vertical block-sum (the throw's own comparator)
    mean_shift2 = None
    if args.cv_centered:
        hms = fu.Get("hJointMeanShift")
        if not hms:
            raise SystemExit("[FAIL] --cv-centered needs hJointMeanShift in the unified-throw ROOT")
        ms = np.array([hms.GetBinContent(i + 1) for i in range(hms.GetNbinsX())])
        mean_shift2 = ms ** 2
    fu.Close()
    fc = ROOT.TFile.Open(args.combined)
    C_comb = _th2(fc.Get("hCov_combined4d_total"))
    # the sweep's own vertical block = sum of the 13 per-band covs (same estimator as C_comb)
    C_vert_sweep = None
    for b in VERT_BANDS:
        h = fc.Get(f"hCov_universe4d_{b}")
        if not h:
            raise SystemExit(f"[FAIL] missing per-band cov hCov_universe4d_{b}")
        cb = _th2(h)
        C_vert_sweep = cb if C_vert_sweep is None else C_vert_sweep + cb
    fc.Close()
    fp = ROOT.TFile.Open(args.prod)
    h = fp.Get("hXSecND_flat")
    xfull = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    fp.Close()
    x = xfull[xfull > 0]
    n = C_comb.shape[0]
    assert C_uni.shape == C_block.shape == C_comb.shape == C_vert_sweep.shape == (n, n), "dim mismatch"

    vu = np.clip(np.diag(C_uni), 0, None)
    if mean_shift2 is not None:
        assert mean_shift2.size == vu.size, f"mean_shift dim {mean_shift2.size} != unified dim {vu.size}"
        vu = vu + mean_shift2                  # F7 CV-centered: variance + shift^2
    vb = np.clip(np.diag(C_block), 0, None)    # bank vertical block (the throw's comparator)
    # conservative per-bin inflation FACTOR measured by the throw (never below block baseline)
    s_adopt = np.sqrt(np.maximum(vu, vb))
    sb = np.sqrt(vb)
    g = np.ones(n)
    m = sb > 0
    g[m] = s_adopt[m] / sb[m]                  # >= 1
    G = g[:, None] * g[None, :]
    # transfer the fractional inflation onto the SWEEP's vertical block (PSD-preserving carrier)
    C_vert_adopt = G * C_vert_sweep            # G C_vert_sweep G
    C_new = (C_comb - C_vert_sweep) + C_vert_adopt

    # symmetrize against float drift
    C_new = 0.5 * (C_new + C_new.T)

    # --- verification ---
    ev = np.linalg.eigvalsh(C_new)
    do = np.sqrt(np.clip(np.diag(C_comb), 0, None)) / x
    dn = np.sqrt(np.clip(np.diag(C_new), 0, None)) / x
    print(f"[adopt] bins                = {n}  (reported)")
    print(f"[adopt] inflation g: bins>1 = {(g > 1.0001).sum()} ({100*(g>1.0001).mean():.1f}%)  "
          f"median={np.median(g):.3f}  max={g.max():.2f}")
    print(f"[adopt] sqrt-trace  old combined = {np.sqrt(np.trace(C_comb)):.4e}")
    print(f"[adopt] sqrt-trace  new combined = {np.sqrt(np.trace(C_new)):.4e}  "
          f"(x{np.sqrt(np.trace(C_new)/np.trace(C_comb)):.3f})")
    print(f"[adopt] median frac/bin  old={100*np.median(do):.2f}%   new={100*np.median(dn):.2f}%")
    print(f"[adopt] PSD check: min eigenvalue = {ev[0]:.3e}  "
          f"(neg: {(ev<0).sum()}; most-neg/max = {ev[0]/ev[-1]:.2e})")
    if ev[0] < -1e-12 * ev[-1]:
        raise SystemExit("[FAIL] adopted covariance is not PSD")
    print("[adopt] PSD OK (PSD by construction: lateral+stat+ML + G C_block G)")

    # --- write ---
    fo = ROOT.TFile.Open(args.out, "RECREATE")
    nb = n
    hnew = ROOT.TH2D("hCov_combined4d_total_uthrow", "combined 4D cov (unified-throw adopted)",
                     nb, 0, nb, nb, 0, nb)
    for i in range(nb):
        for j in range(nb):
            hnew.SetBinContent(i + 1, j + 1, C_new[i, j])
    hnew.Write()
    hg = ROOT.TH1D("hInflation_g", "per-bin unified/block sigma inflation", nb, 0, nb)
    for i in range(nb):
        hg.SetBinContent(i + 1, g[i])
    hg.Write()
    ROOT.TParameter("double")("sqrt_tr_old", float(np.sqrt(np.trace(C_comb)))).Write()
    ROOT.TParameter("double")("sqrt_tr_new", float(np.sqrt(np.trace(C_new)))).Write()
    fo.Close()
    print(f"[adopt] wrote {args.out}")


if __name__ == "__main__":
    main()
