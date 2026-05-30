#!/usr/bin/env python3
"""Apply the missing 1/Phi flux normalization to the Flux universe unfolds.

The 2D cross section is dsigma = U / (c * Phi(pT) * N * POT * dpT * dpz),
with Phi entering only as a per-pT divisor broadcast over pz. Every flux
universe unfold divided by the *CV* flux integral, so each Flux-universe
cross section is wrong by exactly the factor Phi_CV(pT)/Phi_u(pT):

    sigma_u^correct(pT, pz) = sigma_u^current(pT, pz) * Phi_CV(pT)/Phi_u(pT)

This is exact (U and c are untouched by the flux division), so we correct
the 100 existing Flux-universe outputs analytically -- no re-unfolding.

Builds a complete drop-in sweep directory:
  - symlinks to the 87 non-Flux universe outputs + the CV (untouched), and
  - 100 freshly rescaled Flux-universe hXSec2D files,
so `analyze_universes.py --glob '<outdir>/*_uni_full_*.root'` re-rolls the
full systematic covariance with the corrected flux band.

Per-universe flux integrals come from build_flux_universe_band.py; index u
== PPFX universe u == w_{truth,reco}_Flux_u in the omnifile (alignment
verified, Pearson 0.96).
"""
import argparse
import glob
import os
import re
import sys
import numpy as np
import ROOT

BASE = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
FLUX_BAND = f"{BASE}/baseline_flux/flux_integral_universes_MEFHC.root"
SWEEP_GLOB = f"{BASE}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root"
FLUX_RE = re.compile(r"_uni_full_Flux_(\d+)\.root$")


def load_flux(path):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        sys.exit(f"[FAIL] cannot open flux band file {path} "
                 f"(run uq/build_flux_universe_band.py first)")
    hcv = f.Get("hFluxCV")
    huniv = f.Get("hFluxUniv")
    n_pt = hcv.GetNbinsX()
    nu = huniv.GetNbinsY()
    phi_cv = np.array([hcv.GetBinContent(i) for i in range(1, n_pt + 1)])
    phi_u = np.array([[huniv.GetBinContent(i, u) for i in range(1, n_pt + 1)]
                      for u in range(1, nu + 1)])  # (nu, n_pt)
    f.Close()
    return phi_cv, phi_u


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--flux-band", default=FLUX_BAND)
    ap.add_argument("--outdir", default=f"{BASE}/uq/universe_sweep_fluxfix")
    args = ap.parse_args()

    phi_cv, phi_u = load_flux(args.flux_band)
    n_pt, nu = phi_cv.size, phi_u.shape[0]
    print(f"[info] flux band: {n_pt} pT bins, {nu} universes")

    os.makedirs(args.outdir, exist_ok=True)
    files = sorted(glob.glob(SWEEP_GLOB))
    n_link = n_rescale = 0
    for src in files:
        base = os.path.basename(src)
        dst = os.path.join(args.outdir, base)
        m = FLUX_RE.search(base)
        if not m:
            # non-Flux universe or CV: symlink untouched
            if os.path.lexists(dst):
                os.remove(dst)
            os.symlink(src, dst)
            n_link += 1
            continue
        u = int(m.group(1))
        if not (0 <= u < nu):
            sys.exit(f"[FAIL] Flux index {u} out of range [0,{nu})")
        scale = phi_cv / phi_u[u]               # (n_pt,) per pT-bin factor
        fi = ROOT.TFile.Open(src)
        h = fi.Get("hXSec2D")
        if not h:
            sys.exit(f"[FAIL] hXSec2D missing in {src}")
        h2 = h.Clone("hXSec2D")
        h2.SetDirectory(0)
        nx, ny = h2.GetNbinsX(), h2.GetNbinsY()
        if nx != n_pt:
            sys.exit(f"[FAIL] {base}: nx={nx} != n_pt={n_pt}")
        for ix in range(1, nx + 1):
            s = float(scale[ix - 1])
            for iy in range(1, ny + 1):
                h2.SetBinContent(ix, iy, h2.GetBinContent(ix, iy) * s)
                h2.SetBinError(ix, iy, h2.GetBinError(ix, iy) * s)
        fi.Close()
        if os.path.lexists(dst):
            os.remove(dst)
        fo = ROOT.TFile.Open(dst, "RECREATE")
        h2.Write("hXSec2D")
        fo.Close()
        n_rescale += 1

    print(f"[info] symlinked {n_link} (non-Flux + CV), rescaled {n_rescale} Flux")
    print(f"[wrote] {args.outdir}")
    if n_rescale != nu:
        print(f"[WARN] rescaled {n_rescale} Flux files but band has {nu} universes")


if __name__ == "__main__":
    main()
