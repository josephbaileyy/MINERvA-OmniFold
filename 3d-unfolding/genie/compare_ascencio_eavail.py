#!/usr/bin/env python
"""Compare this analysis's E_avail spectrum to MINERvA's published low-q3 result.

Background (audit 2026-06-03, LITERATURE_NOTES.md). Ascencio et al. (arXiv:2110.13372,
PRD 106 032001) measured d2 sigma/(dq3 dE_avail) for CC-inclusive nu_mu on hydrocarbon at
<E_nu> ~ 6 GeV with q3 < 1.2 GeV -- the closest published MINERvA low-recoil inclusive
result, and it shares the available-energy observable with this 3D measurement. It was
only listed in the related-work table (sec_3d.tex:77); this overlays it.

IMPORTANT phase-space caveat. Ascencio integrates the low-recoil region (q3 < 1.2 GeV);
this analysis's E_avail projection integrates the full muon acceptance (pt < 4.5,
1.5 < pz < 60 GeV), i.e. all q3. The two normalizations therefore differ and a
bin-identical chi2 is NOT meaningful. The comparison is the SHAPE of dsigma/dE_avail
(area-normalized over the shared E_avail range) and, above all, the qualitative question:
does the low-E_avail excess seen here track the well-established MINERvA low-recoil deficit
that Ascencio measured (the missing-2p2h region)?

Our side is built from the frozen 3D result + combined covariance (reusing the tested
projection machinery in overlay_generators_band.py). The Ascencio side is read from a
plain text file you provide from the data release / arXiv ancillary of 2110.13372:

    # eavail_low  eavail_high  dsigma_dEavail   total_err     (any consistent units)
    0.00  0.04  <val>  <err>
    ...

Run from 3d-unfolding/genie/ after `source setup_salloc_env.sh`:
  python compare_ascencio_eavail.py                      # our spectrum only (self-test)
  python compare_ascencio_eavail.py --ascencio ascencio_eavail.txt
"""
import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from overlay_generators_band import load_th3, load_cov, build_projectors, project_cov


def our_eavail():
    """Return (edges, dsigma/dEavail, sigma) for our E_avail projection."""
    cv3d, edges = load_th3("../xsec_3d_MEFHC_5iter_lgbm.root", "hXSec3D")
    J, _ = build_projectors(cv3d, edges)
    cv_rep = cv3d.ravel(order="C")[(cv3d > 0).ravel(order="C")]
    central = J["eavail"] @ cv_rep
    C = load_cov("../uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:"
                 "hCov_combined3d_total")
    band = project_cov(C, J)["eavail"][1]   # {axis: (cov, sigma)}
    return edges[2], central, band


def area_norm(edges, y):
    w = np.diff(edges)
    integral = float(np.sum(y * w))
    return y / integral if integral > 0 else y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ascencio", default="",
                    help="text file: eavail_low eavail_high dsigma err (from 2110.13372)")
    ap.add_argument("--out", default="ascencio_vs_unfolded_eavail.png")
    args = ap.parse_args()

    ea_edges, ours, ours_err = our_eavail()
    centers = 0.5 * (ea_edges[:-1] + ea_edges[1:])
    print(f"[ours] E_avail projection: {len(ours)} bins, "
          f"integral={np.sum(ours*np.diff(ea_edges)):.4e}")

    fig, ax = plt.subplots(figsize=(7, 5))
    ours_n = area_norm(ea_edges, ours)
    ours_err_n = area_norm(ea_edges, ours_err)
    ax.errorbar(centers, ours_n, yerr=ours_err_n, fmt="o-", color="k",
                label="This work (full muon acceptance)", capsize=2)

    if args.ascencio and os.path.exists(args.ascencio):
        d = np.loadtxt(args.ascencio)
        a_lo, a_hi, a_y, a_e = d[:, 0], d[:, 1], d[:, 2], d[:, 3]
        a_c = 0.5 * (a_lo + a_hi)
        a_edges = np.append(a_lo, a_hi[-1])
        a_n = area_norm(a_edges, a_y)
        a_en = area_norm(a_edges, a_e)
        ax.errorbar(a_c, a_n, yerr=a_en, fmt="s--", color="C3",
                    label="Ascencio 2110.13372 (q3<1.2 GeV)", capsize=2)
        # shape comparison over the shared E_avail range
        lo, hi = max(ea_edges[0], a_edges[0]), min(ea_edges[-1], a_edges[-1])
        print(f"[shape] shared E_avail range [{lo:.2f}, {hi:.2f}] GeV; "
              f"area-normalized overlay written. Phase spaces differ (see header) -- "
              f"compare the SHAPE / low-E_avail behaviour, not absolute normalization.")
    else:
        print("[note] no --ascencio data file: plotting our spectrum only. To overlay the")
        print("       published low-q3 result, obtain the 2110.13372 data release / arXiv")
        print("       ancillary, format as 'eavail_low eavail_high dsigma err', and pass")
        print("       it with --ascencio. (MINERvA member access; not public in-session.)")

    ax.set_xlabel(r"$E_{\rm avail}$ (GeV)")
    ax.set_ylabel(r"area-normalized $d\sigma/dE_{\rm avail}$")
    ax.set_title("E_avail shape: this work vs MINERvA low-q3 (2110.13372)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.out, dpi=120)
    print(f"[OK] wrote {args.out}")


if __name__ == "__main__":
    main()
