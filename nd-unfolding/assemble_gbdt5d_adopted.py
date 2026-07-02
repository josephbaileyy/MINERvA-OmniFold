#!/usr/bin/env python3
"""D5 -- assemble the ADOPTED GBDT 5D covariance from the unified-throw systematic.

Adopted GBDT total covariance =
    C_unified                         (unified-throw systematic: all VERTICAL reweight
                                        universes -- Flux, GENIE knobs, 2p2h -- re-unfolded
                                        together, so cross-band correlations are captured)
  + hCov_stat5d_reported              (bootstrap statistical)
  + hCov_mlsplit5d_reported           (ML train/test-split)
  + sum of the 9 DETECTOR-LATERAL bands (shifted-kinematics response, which a frozen-sample
    reweight throw cannot produce, so they are added from the per-band universe file):
      BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA, Muon_Energy_MINOS,
      MinosEfficiency, GEANT_Neutron, GEANT_Pion, GEANT_Proton

This is the unified-throw analogue of the published block-sum GBDT budget: the vertical
bands move from a per-band block sum into the single re-unfolded C_unified (which also
carries their cross-correlations + the retraining nonlinearity), while the lateral +
stat + ML pieces are unchanged. All inputs are TH2D on the SAME 10694-bin CV>0 reported
ordering (hXSecND_flat mask of the 14x16x7x7x6 grid). ROOT TH2D::Add does the sum at
C++ speed. Writes a NEW file (uq_5d/gbdt_5d_covariance_adopted.root); touches nothing.

Run from nd-unfolding/ after `source ../setup_salloc_env.sh`:
  python assemble_gbdt5d_adopted.py
"""
import argparse
import os

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"

LAT_BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution",
             "Muon_Energy_MINERvA", "Muon_Energy_MINOS", "MinosEfficiency",
             "GEANT_Neutron", "GEANT_Pion", "GEANT_Proton"]


def diag(h):
    n = h.GetNbinsX()
    return np.array([h.GetBinContent(i, i) for i in range(1, n + 1)])


def main():
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError

    ap = argparse.ArgumentParser()
    ap.add_argument("--unified", default=f"{_REPO}/nd-unfolding/uq_5d/unified_throw_cov_5d.root")
    ap.add_argument("--unified-hist", default="C_unified")
    ap.add_argument("--stat", default=f"{_REPO}/nd-unfolding/uq_cov_stat_5d.root")
    ap.add_argument("--stat-hist", default="hCov_stat5d_reported")
    ap.add_argument("--ml", default=f"{_REPO}/nd-unfolding/uq_cov_mlsplit_5d.root")
    ap.add_argument("--ml-hist", default="hCov_mlsplit5d_reported")
    ap.add_argument("--univ", default=f"{_REPO}/nd-unfolding/uq_5d/universe_stage2_5d/"
                                      "uq_universe_5d_covariance_combined.root")
    ap.add_argument("--cv", default=f"{_REPO}/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--cv-hist", default="hXSecND_flat")
    ap.add_argument("--out", default=f"{_REPO}/nd-unfolding/uq_5d/gbdt_5d_covariance_adopted.root")
    args = ap.parse_args()

    comp_tr = {}  # component sqrt(trace) for the budget printout

    # ---- C_unified is the accumulator ----
    fu = ROOT.TFile.Open(args.unified)
    hU = fu.Get(args.unified_hist)
    assert hU, f"missing {args.unified_hist} in {args.unified}"
    hTot = hU.Clone("hCov_gbdt5d_adopted")
    hTot.SetDirectory(0)
    n = hTot.GetNbinsX()
    comp_tr["unified"] = float(np.sqrt(diag(hU).sum()))
    fu.Close()
    print(f"[D5] C_unified: n={n}  sqrt(tr)={comp_tr['unified']:.4e}")

    # ---- + stat, + ML ----
    for tag, path, hist in (("stat", args.stat, args.stat_hist),
                            ("ml", args.ml, args.ml_hist)):
        f = ROOT.TFile.Open(path)
        h = f.Get(hist)
        assert h, f"missing {hist} in {path}"
        assert h.GetNbinsX() == n, f"{hist} dim {h.GetNbinsX()} != {n}"
        comp_tr[tag] = float(np.sqrt(diag(h).sum()))
        hTot.Add(h)
        f.Close()
        print(f"[D5] + {tag:5s} ({hist}): sqrt(tr)={comp_tr[tag]:.4e}")

    # ---- + 9 detector-lateral bands ----
    fl = ROOT.TFile.Open(args.univ)
    lat_tr2 = 0.0
    for b in LAT_BANDS:
        h = fl.Get(f"hCov_universe5d_{b}")
        assert h, f"missing hCov_universe5d_{b} in {args.univ}"
        assert h.GetNbinsX() == n, f"{b} dim {h.GetNbinsX()} != {n}"
        lat_tr2 += diag(h).sum()
        hTot.Add(h)
        print(f"[D5] + lateral {b:22s} sqrt(tr)={np.sqrt(diag(h).sum()):.4e}")
    fl.Close()
    comp_tr["lateral_sum9"] = float(np.sqrt(lat_tr2))

    # ---- totals + per-bin fractional summary ----
    d_tot = diag(hTot)
    comp_tr["ADOPTED_total"] = float(np.sqrt(d_tot.sum()))

    fc = ROOT.TFile.Open(args.cv)
    hcv = fc.Get(args.cv_hist)
    cv_full = np.array([hcv.GetBinContent(i + 1) for i in range(hcv.GetNbinsX())])
    fc.Close()
    rep = cv_full[cv_full > 0]
    assert rep.size == n, f"CV reported {rep.size} != cov dim {n}"
    frac = np.sqrt(np.clip(d_tot, 0, None)) / rep
    med = float(np.median(frac[np.isfinite(frac) & (frac > 0)]))

    print("\n=== D5 adopted GBDT 5D covariance -- component sqrt(trace) budget ===")
    for k in ("unified", "lateral_sum9", "stat", "ml", "ADOPTED_total"):
        print(f"  {k:16s} {comp_tr[k]:.4e}")
    print(f"  median per-bin fractional uncertainty = {100*med:.2f}%   (n_bins={n})")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fo = ROOT.TFile.Open(args.out, "RECREATE")
    hTot.Write()
    for k, v in comp_tr.items():
        ROOT.TParameter("double")(f"sqrt_tr_{k}", v).Write()
    ROOT.TParameter("double")("median_frac", med).Write()
    fo.Close()
    print(f"\n[D5] wrote {args.out} :: hCov_gbdt5d_adopted")


if __name__ == "__main__":
    main()
