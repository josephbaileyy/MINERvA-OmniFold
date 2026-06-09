#!/usr/bin/env python3
"""Per-generator significance of the high-E_avail excess (open question 6), using the
existing 4D combined covariance marginalized to the E_avail axis.

The generator BAND (3d-unfolding/genie/) established the central-value statement: the
unfolded data sits above every generator in the high-E_avail / high-W corner. This turns
that into a NUMBER -- a chi^2 / N-sigma per generator on dsigma/dE_avail -- without waiting
for the 5D (E_avail,W) systematic campaign, by reusing the published 4D combined covariance
(uq_universe_4d_covariance_combined.root: syst+stat+ML on the 4830 reported bins).

Marginalization is the project_marginal linear map M (integrate out pt,pz,q3):
    y_k = sum_{cells in E_avail bin k} x_cell * (dpt dpz dq3)        (dsigma/dEavail)
    C_y = M C_4d M^T            (7x7, rigorous propagation of the full 4D covariance)
Then per generator g:  chi^2 = (y_data - y_g)^T C_y^{-1} (y_data - y_g), and the same on
the high-E_avail sub-block (E_avail >= 0.8 GeV, the DIS tail) for the corner statement.

This is the (E_avail,W)->E_avail-projected significance; the W-resolved corner version
follows from the 5D _universes_full campaign (ev5duni). Run in the analysis env.

  python eavail_generator_significance.py
"""
import argparse
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _th2(h):
    # fast buffer read: TH2D internal array is (ny+2)x(nx+2) row-major incl. under/overflow,
    # flat index = binx + (nx+2)*biny. Extract the physical nx x ny block (C[i,k]=content(i+1,k+1)).
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    buf = np.frombuffer(h.GetArray(), dtype=np.float64, count=(nx + 2) * (ny + 2))
    arr = buf.reshape(ny + 2, nx + 2)            # arr[biny, binx]
    return arr[1:ny + 1, 1:nx + 1].T.copy()      # -> [binx-1, biny-1]


def _th1(h):
    return np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])


def main():
    import ROOT
    from scipy import stats
    import unfold_nd_omnifold_unbinned as und
    import unfold_2d_omnifold_unbinned as u2d
    ap = argparse.ArgumentParser()
    ap.add_argument("--cov", default="uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined.root")
    ap.add_argument("--cov-hist", default="hCov_combined4d_total")
    ap.add_argument("--prod", default="products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--gendir", default="../3d-unfolding/genie")
    ap.add_argument("--gens", default="GENIE-CV:genie_cv_xsec_eavailW.root,"
                    "GENIE+MEC:genie_mec_xsec_eavailW.root,"
                    "NuWro:nuwro_cv_xsec_eavailW.root,"
                    "GiBUU:gibuu_cv_xsec_eavailW.root")
    args = ap.parse_args()

    pt_e = np.asarray(u2d.PT_EDGES, float)
    pz_e = np.asarray(u2d.PZ_EDGES, float)
    ea_e = np.asarray(und.EXTRA_AXES["eavail"]["edges"], float)
    q3_e = np.asarray(und.EXTRA_AXES["q3"]["edges"], float)
    shape = (len(pt_e) - 1, len(pz_e) - 1, len(ea_e) - 1, len(q3_e) - 1)  # (14,16,7,7)
    dpt, dpz, dea, dq3 = (np.diff(pt_e), np.diff(pz_e), np.diff(ea_e), np.diff(q3_e))
    n_ea = len(ea_e) - 1

    # --- 4D CV xsec (full grid) + reported mask + covariance (reported bins) ---
    fp = ROOT.TFile.Open(args.prod)
    xfull = _th1(fp.Get("hXSecND_flat"))
    fp.Close()
    gmask = np.where(xfull > 0)[0]
    x_rep = xfull[gmask]
    fc = ROOT.TFile.Open(args.cov)
    C4 = _th2(fc.Get(args.cov_hist))
    fc.Close()
    assert C4.shape[0] == gmask.size, f"cov dim {C4.shape[0]} != reported {gmask.size}"
    nrep = gmask.size

    # --- marginalization map M (n_ea x nrep): weight = dpt dpz dq3, grouped by eavail bin ---
    ipt, ipz, iea, iq3 = np.unravel_index(gmask, shape)        # C-order
    wcell = dpt[ipt] * dpz[ipz] * dq3[iq3]
    M = np.zeros((n_ea, nrep))
    M[iea, np.arange(nrep)] = wcell
    y_data = M @ x_rep                                         # dsigma/dEavail (7)
    C_y = M @ C4 @ M.T                                         # 7x7
    sig = np.sqrt(np.clip(np.diag(C_y), 0, None))
    print(f"[eavail] reported 4D bins={nrep}  marginalized to {n_ea} E_avail bins")
    print(f"[eavail] data dsigma/dEavail (x1e-39) +- sqrt(diag):")
    for k in range(n_ea):
        print(f"   {ea_e[k]:.1f}-{ea_e[k+1]:<6.1f}  {1e39*y_data[k]:8.3f} +- {1e39*sig[k]:6.3f}"
              f"  ({100*sig[k]/y_data[k]:.1f}%)")

    # conditioning diagnostic: a highly-correlated systematic covariance (flux is a
    # coherent normalization) can be near-singular -> pinv amplifies shape directions
    # and inflates chi^2. Report eigenvalues + condition number so the significance is
    # interpretable, not a numerical artifact.
    evals = np.linalg.eigvalsh(C_y)
    print(f"\n[cond] C_y eigenvalues (x1e-78): {np.array2string(evals*1e78, precision=2)}")
    print(f"[cond] condition number = {evals[-1]/max(evals[0],1e-300):.2e}  "
          f"(corr-dominated cov -> shape directions carry tiny variance)")
    hi = ea_e[:-1] >= 0.8                                      # DIS-tail sub-block
    Cinv = np.linalg.pinv(C_y)
    Cinv_hi = np.linalg.pinv(C_y[np.ix_(hi, hi)])

    def chi2_to_sigma(chi2, ndf):
        p = stats.chi2.sf(chi2, ndf)
        # one-sided Gaussian-equivalent significance
        z = stats.norm.isf(p / 2.0) if p > 0 else float("inf")
        return p, z

    print(f"\n[eavail] per-generator chi^2 (data - gen)^T C^-1 (data - gen):")
    print(f"   {'generator':12s} {'chi2/ndf(all7)':>16s} {'p':>9s} {'Nsigma':>7s} "
          f"| {'chi2/ndf(DIS>=0.8)':>18s} {'p':>9s} {'Nsigma':>7s}")
    for spec in args.gens.split(","):
        tag, fn = spec.split(":")
        path = os.path.join(args.gendir, fn)
        if not os.path.exists(path):
            print(f"   {tag:12s}  (missing {fn} -- not yet generated)")
            continue
        fg = ROOT.TFile.Open(path)
        y_g = _th1(fg.Get("hXSec_eavail"))
        fg.Close()
        if y_g.size != n_ea:
            print(f"   {tag:12s}  (eavail bins {y_g.size} != {n_ea})"); continue
        d = y_data - y_g
        pulls = d / sig                                        # per-bin (data-gen)/sqrt(diag)
        chi2 = float(d @ Cinv @ d); p, z = chi2_to_sigma(chi2, n_ea)
        dh = d[hi]; chi2h = float(dh @ Cinv_hi @ dh); ph, zh = chi2_to_sigma(chi2h, int(hi.sum()))
        print(f"   {tag:12s} {chi2:9.2f}/{n_ea:<6d} {p:9.2e} {z:7.2f} "
              f"| {chi2h:11.2f}/{int(hi.sum()):<6d} {ph:9.2e} {zh:7.2f}")
        print(f"      per-bin pulls (data-gen)/sqrt(diag): {np.array2string(pulls, precision=1)}  "
              f"data/gen ratio: {np.array2string(y_data/np.where(y_g>0,y_g,np.nan), precision=2)}")


if __name__ == "__main__":
    main()
