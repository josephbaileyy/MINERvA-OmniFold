#!/usr/bin/env python3
"""FPS extension-region validation: hidden-variable closure + coverage toys,
split into published-phase-space cells vs extension (extrapolated) cells.

Two independent parts (run whichever inputs are given):

1. --closure-root  closure_2d_FPS_hidden_eavail_MEFHC.root
   Hidden-variable closure (driver --closure --closure-reweight-axis eavail with
   --axes "": the bump lives in true E_avail, which the 2D FPS unfold never
   sees). Compares hXSecND (unfolded) vs hClosureRefND (bump-reweighted truth)
   per cell; reports |ratio-1| median/p90/max separately for published-PS and
   extension cells. Context scale: the 3-prior envelope half-spread medians
   (2.9% published / 7.9% extension, FPS_PILOT.md tier-2 band).

2. --toys-glob 'cov_fps/res_toy_*.npz' --npz of_inputs_fps.npz
   Coverage from closure+bootstrap toys (coverage_toy_nd.py). Truth reference =
   unfluctuated closure truth from the npz (completeness=1). Per-bin sigma over
   toys, residual r=(toy-truth)/sigma, coverage=frac(|r|<=1), target 68.27%;
   reported per region (published vs extension).

  python fps_extension_validation.py \
      --closure-root products/5d/closure_2d_FPS_hidden_eavail_MEFHC.root \
      --toys-glob 'cov_fps/res_toy_*.npz' --npz of_inputs_fps.npz
"""
import argparse
import glob
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import unfold_2d_omnifold_unbinned as u2d
from fps_acceptance import PT_EXT, PZ_EXT
from fps_pilot_compare import reported_mask, th2_np
from xsec_nd import extract_cross_section_nd


def region_masks():
    """(published, extension) boolean masks on the extended (pT,pz) grid."""
    pt_ext, pz_ext = np.asarray(PT_EXT, float), np.asarray(PZ_EXT, float)
    pt_pap, pz_pap = np.asarray(u2d.PT_EDGES, float), np.asarray(u2d.PZ_EDGES, float)
    i0 = int(np.searchsorted(pt_ext, pt_pap[0]))
    j0 = int(np.searchsorted(pz_ext, pz_pap[0]))
    npt, npz = len(pt_pap) - 1, len(pz_pap) - 1
    assert np.allclose(pt_ext[i0:i0 + npt + 1], pt_pap), "pT edges not nested"
    assert np.allclose(pz_ext[j0:j0 + npz + 1], pz_pap), "pz edges not nested"
    pub = np.zeros((len(pt_ext) - 1, len(pz_ext) - 1), bool)
    pub[i0:i0 + npt, j0:j0 + npz] = reported_mask(pt_pap, pz_pap)
    return pub, ~pub


def summarize(name, vals):
    v = np.abs(vals)
    print(f"  [{name:22s}] n={v.size:4d}  median={100*np.median(v):6.2f}%  "
          f"p90={100*np.percentile(v, 90):6.2f}%  max={100*v.max():6.2f}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--closure-root", default=None)
    ap.add_argument("--toys-glob", default=None)
    ap.add_argument("--npz", default="of_inputs_fps.npz")
    ap.add_argument("--target", type=float, default=0.65,
                    help="per-bin coverage floor to flag (2D convention)")
    args = ap.parse_args()
    pub, ext = region_masks()
    print(f"[regions] published cells={pub.sum()}  extension cells={ext.sum()}")

    if args.closure_root:
        print(f"\n=== HIDDEN-VARIABLE CLOSURE ({args.closure_root}) ===")
        unf = th2_np(args.closure_root, "hXSecND")
        ref = th2_np(args.closure_root, "hClosureRefND")
        ok = (unf > 0) & (ref > 0)
        r = np.full(unf.shape, np.nan)
        r[ok] = unf[ok] / ref[ok] - 1.0
        for nm, m in [("published-PS cells", pub & ok), ("extension cells", ext & ok)]:
            summarize(nm, r[m])
        print("  context: 3-prior envelope half-spread medians 2.9% (published) / "
              "7.9% (extension)")

    if args.toys_glob:
        print(f"\n=== COVERAGE TOYS ({args.toys_glob}) ===")
        paths = sorted(glob.glob(args.toys_glob))
        if not paths:
            raise SystemExit(f"[FAIL] no toys matched {args.toys_glob}")
        X = np.stack([np.load(p)["xsec_flat"] for p in paths], 0)
        print(f"  toys = {X.shape[0]}")
        d = np.load(args.npz, allow_pickle=True)
        ne = int(d["nedges"]); edges = [d[f"edges_{i}"] for i in range(ne)]
        bins = [np.asarray(e, float) for e in edges]
        pt_mask = d["pass_truth"].astype(bool)
        samp = np.column_stack([d["MCgen"][pt_mask, i] for i in range(d["MCgen"].shape[1])])
        refh, _ = np.histogramdd(samp, bins=bins, weights=d["w_truth"][pt_mask])
        ref_xs, _ = extract_cross_section_nd(refh, np.ones_like(refh), d["flux"],
                                             float(d["data_pot"]), float(d["n_nucleons"]),
                                             edges)
        ref = ref_xs.ravel(order="C")
        assert X.shape[1] == ref.size, f"toy nbins {X.shape[1]} != ref {ref.size}"
        sig = X.std(axis=0, ddof=1)
        good = (ref > 0) & (sig > 0)
        R = (X[:, good] - ref[good]) / sig[good]
        cov_bin = (np.abs(R) <= 1.0).mean(axis=0)
        pub_f = pub.ravel(order="C")[good]
        ext_f = ext.ravel(order="C")[good]
        print(f"  reported bins = {int(good.sum())} of {ref.size}  "
              f"(target coverage 68.27%, mean |r| target 0.798)")
        for nm, m in [("ALL", np.ones(good.sum(), bool)),
                      ("published-PS", pub_f), ("extension", ext_f)]:
            c = cov_bin[m]
            ar = np.abs(R[:, m]).mean()
            sr = R[:, m].mean()
            low = (c < args.target).sum()
            print(f"  [{nm:14s}] bins={c.size:4d}  coverage mean={100*c.mean():.2f}% "
                  f"median={100*np.median(c):.2f}%  <|r|>={ar:.3f}  "
                  f"signed r mean={sr:+.3f}  bins<{int(100*args.target)}%={low}")
        status = "PASS" if abs(cov_bin.mean() - 0.6827) < 0.05 else "CHECK"
        print(f"  STATUS {status} (overall mean coverage within 5% of 68.27%: "
              f"{100*cov_bin.mean():.2f}%)")


if __name__ == "__main__":
    main()
