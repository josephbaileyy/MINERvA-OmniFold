#!/usr/bin/env python3
"""Adopt the rigorous 5D unified-throw systematic into the published combined 5D covariance.

5D (pt,pz,Eavail,q3,W) analogue of adopt_unified_4d.py. The unified throw
(uq_5d/unified_throw_cov_5d.root, joint re-unfolds of the 12 knob bands + 100 flux
universes) measures the per-bin systematic variance INCLUDING the nonlinear
cross-band term the block-sum drops. But with n_throws << bins, C_unified is a
low-rank (noisy) estimate of the full N x N matrix; swapping the whole matrix in
directly breaks positive-definiteness. So -- exactly as in 4D (adopt_unified_4d.py) --
we adopt the throw's fractional per-bin variance INFLATION and transfer it onto the
SWEEP's own vertical block, PSD by construction:

    g_i = sqrt( max(sigma_uni_i^2, sigma_block_i^2) ) / sigma_block_i   >= 1
    C_combined_new = (C_combined_old - C_vert_sweep) + G C_vert_sweep G
                   = C_combined_old + (g_i g_j - 1) * C_vert_sweep       <- PSD by construction

C_vert_sweep = sum of the 13 vertical per-band covs (12 knobs + Flux) the throw covers,
from the combined file's per-band hCov_universe5d_<band> (same sweep estimator as C_comb).
The 9 detector-lateral bands and the stat/ML blocks already inside hCov_combined5d_total
are left untouched -- the throw does not cover them. The conservative max() never
UNDER-covers vs the block baseline; it inflates where the nonlinear cross-term is real.

Memory-frugal: 10694^2 f64 ~= 0.9 GB/matrix; only C_comb + C_vert are resident, and
C_new is built into C_comb row-by-row (1-D temporaries), so peak ~2 matrices + eigvalsh.

  python adopt_unified_5d.py    # -> uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root
"""
import argparse
import gc
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# the 13 vertical bands the 5D unified throw covers (12 KNOB_BANDS + Flux); identical
# to the 4D set -- verified present in both bank_uthrow_5d and the per-band sweep covs.
VERT_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2", "LowQ2",
              "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi", "Flux"]


def _th2(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    b = np.frombuffer(h.GetArray(), dtype=np.float64, count=(nx + 2) * (ny + 2)).reshape(ny + 2, nx + 2)
    return b[1:ny + 1, 1:nx + 1].T.copy()


def _diag(h):
    """Read only the diagonal of a square TH2D (no full-matrix materialization)."""
    n = h.GetNbinsX()
    return np.array([h.GetBinContent(i + 1, i + 1) for i in range(n)])


def _write_th2(name, title, M):
    """Fast dense TH2D write via the writable ROOT buffer (avoids 1e8 SetBinContent calls)."""
    import ROOT
    n = M.shape[0]
    h = ROOT.TH2D(name, title, n, 0, n, n, 0, n)
    arr = np.frombuffer(h.GetArray(), dtype=np.float64, count=(n + 2) * (n + 2)).reshape(n + 2, n + 2)
    try:
        arr.setflags(write=True)
    except Exception:
        pass
    arr[1:n + 1, 1:n + 1] = M.T   # _th2 reads inner.T; for symmetric M this round-trips exactly
    return h


def main():
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ap = argparse.ArgumentParser()
    ap.add_argument("--uthrow", default="uq_5d/unified_throw_cov_5d.root")
    ap.add_argument("--combined",
                    default="uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined.root")
    ap.add_argument("--prod", default="products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--out",
                    default="uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root")
    args = ap.parse_args()

    # --- per-bin inflation factor g from the throw (diagonals only; cheap) ---
    fu = ROOT.TFile.Open(args.uthrow)
    vu = np.clip(_diag(fu.Get("C_unified")), 0, None)   # unified per-bin variance
    vb = np.clip(_diag(fu.Get("C_blocksum")), 0, None)  # bank block-sum per-bin variance (comparator)
    fu.Close()
    s_adopt = np.sqrt(np.maximum(vu, vb))               # conservative: never below block baseline
    sb = np.sqrt(vb)
    n = vu.size
    g = np.ones(n)
    m = sb > 0
    g[m] = s_adopt[m] / sb[m]                            # >= 1

    # --- reported CV (frac/bin diagnostics + dim check) ---
    fp = ROOT.TFile.Open(args.prod)
    h = fp.Get("hXSecND_flat")
    xfull = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    fp.Close()
    x = xfull[xfull > 0]
    assert x.size == n, f"reported CV ({x.size}) != throw dim ({n})"

    # --- load C_comb (becomes C_new in place) + the sweep vertical block sum ---
    fc = ROOT.TFile.Open(args.combined)
    C_new = _th2(fc.Get("hCov_combined5d_total"))
    assert C_new.shape == (n, n), f"combined dim {C_new.shape} != throw dim {n}"
    sqrt_tr_comb = float(np.sqrt(np.trace(C_new)))
    diag_comb = np.clip(np.diag(C_new), 0, None).copy()
    C_vert = None
    for b in VERT_BANDS:
        hb = fc.Get(f"hCov_universe5d_{b}")
        if not hb:
            raise SystemExit(f"[FAIL] missing per-band cov hCov_universe5d_{b}")
        cb = _th2(hb)
        if C_vert is None:
            C_vert = cb
        else:
            C_vert += cb
            del cb
            gc.collect()
    fc.Close()

    # --- C_new = C_comb + (g_i g_j - 1) * C_vert   (row-by-row; peak ~2 matrices) ---
    for i in range(n):
        C_new[i, :] += (g[i] * g - 1.0) * C_vert[i, :]
    del C_vert
    gc.collect()

    # --- verification (eigvalsh reads the lower triangle; construction-symmetric) ---
    ev = np.linalg.eigvalsh(C_new)
    diag_new = np.clip(np.diag(C_new), 0, None)
    do = np.sqrt(diag_comb) / x
    dn = np.sqrt(diag_new) / x
    sqrt_tr_new = float(np.sqrt(np.trace(C_new)))
    print(f"[adopt5d] bins                = {n}  (reported)")
    print(f"[adopt5d] inflation g: bins>1 = {(g > 1.0001).sum()} ({100*(g>1.0001).mean():.1f}%)  "
          f"median={np.median(g):.3f}  max={g.max():.2f}")
    print(f"[adopt5d] sqrt-trace  old combined = {sqrt_tr_comb:.4e}")
    print(f"[adopt5d] sqrt-trace  new combined = {sqrt_tr_new:.4e}  "
          f"(x{sqrt_tr_new/sqrt_tr_comb:.3f})")
    print(f"[adopt5d] median frac/bin  old={100*np.median(do):.2f}%   new={100*np.median(dn):.2f}%")
    print(f"[adopt5d] PSD check: min eigenvalue = {ev[0]:.3e}  "
          f"(neg: {(ev<0).sum()}; most-neg/max = {ev[0]/ev[-1]:.2e})")
    if ev[0] < -1e-12 * ev[-1]:
        raise SystemExit("[FAIL] adopted covariance is not PSD")
    print("[adopt5d] PSD OK (PSD by construction: lateral+stat+ML + G C_vert G)")

    # --- write ---
    fo = ROOT.TFile.Open(args.out, "RECREATE")
    hnew = _write_th2("hCov_combined5d_total_uthrow",
                      "combined 5D cov (unified-throw adopted)", C_new)
    hnew.Write()
    hg = ROOT.TH1D("hInflation_g", "per-bin unified/block sigma inflation", n, 0, n)
    for i in range(n):
        hg.SetBinContent(i + 1, g[i])
    hg.Write()
    ROOT.TParameter("double")("sqrt_tr_old", sqrt_tr_comb).Write()
    ROOT.TParameter("double")("sqrt_tr_new", sqrt_tr_new).Write()
    fo.Close()
    print(f"[adopt5d] wrote {args.out}")


if __name__ == "__main__":
    main()
