#!/usr/bin/env python3
"""Universe-covariance rollup for the 5D (pt,pz,eavail,q3,W) OmniFold UQ campaign.

5D-named sibling of analyze_universes_nd.py (identical math; only the output histogram
names carry a 5d tag, e.g. hCov_combined5d_total). Reads the flat hXSecND_flat (C-order
ravel over the 5D shape) from the CV unfold and the per-(band,idx) universe unfolds
(sweep_bank_5d.py --run / sbatch_unfold_5d_detector.sh), builds the block-summed
systematic covariance, an optional flat normalization band, and an optional block-sum
with extra (stat/ML) covariances. Reported bins = CV>0.

  python analyze_universes_5d.py --cv products/5d/xsec_5d_MEFHC_5iter_lgbm.root \
      --glob 'uq_5d/universe_sweep/5d_xsec_*_uni_full_*.root' \
      --add-norm 0.014 \
      --bootstrap-cov uq_cov_stat_5d.root:hCov_stat5d_reported \
                      uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported \
      --outdir uq_5d/universe_stage2_5d/ --out-root uq_universe_5d_covariance_combined.root
"""
import argparse
import glob
import os
import re
from collections import defaultdict

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
UNI_RE = re.compile(r".*_uni(?:_full)?_(?P<band>[A-Za-z0-9_]+?)_(?P<idx>\d+)\.root$")

CATEGORY_ORDER = ["Flux", "Models", "Normalization", "Hadronic response",
                  "Muon reconstruction"]


def category_for_band(band):
    c = band[len("full_"):] if band.startswith("full_") else band
    if c == "Flux":
        return "Flux"
    if c == "__Normalization_flat":
        return "Normalization"
    if c.startswith("Fr") or c.startswith("MFP_") or c.startswith("GEANT_"):
        return "Hadronic response"
    if (c.startswith("Muon_") or c.startswith("BeamAngle") or
            c in {"MuonResolution", "MinosEfficiency"}):
        return "Muon reconstruction"
    return "Models"


def load_flat(path, expect_nbins=None):
    # B4 / BEN-481: THIS WAS THE ONE GENUINELY UNPROTECTED CONSUMER. It checked IsZombie() only, so a
    # TRUNCATED product -- one ROOT had to recover because the producer died mid-write -- was ACCEPTED
    # and folded into the 188-universe analysis. ROOT sets TFile::kRecovered on any file not closed
    # through Close(), which is exactly the interrupted-producer case, and the sweep leg's skip is
    # existence-only so a partial file is also skipped forever on retry rather than repaired.
    #
    # Delegated to fps_unfold_complete.check rather than re-implemented: that module already carried
    # the right COMPLETE definition and a second copy of a completeness rule drifts invisibly, because
    # each copy passes its own tests.
    #
    # TIGHTENED 2026-08-18, and the earlier justification here was FALSE OF THIS FAMILY. It read
    # "does not always write globalCompleteness". Measured: BOTH writers of this family write it
    # UNCONDITIONALLY, in the same straight-line block as hXSecND_flat itself --
    #     sweep_bank_5d.py:289             (169 vertical universes)
    #     unfold_nd_omnifold_unbinned.py:1014  (19 lateral + CV)
    # and the mediator independently read the key out of a real archive product
    # (5d_xsec_MEFHC_5iter_lgbm_uni_full_2p2h_0.root, globalCompleteness = 0.9998608732766575).
    # There is no absent case, so the premise of the relaxation did not exist.
    #
    # WHAT THE RELAXATION ACTUALLY COST is worse than a weak comment: require_completeness=False
    # skipped the NaN gate as well as the threshold, and NaN IS REACHABLE WITH A KNOWN CAUSE --
    # both writers emit float("nan") when denom_nd.sum() <= 0 (sweep_bank_5d.py:265,
    # unfold_nd_omnifold_unbinned.py:999). A universe whose denominator integrates to zero has a
    # meaningless cross-section, and I was folding it into the 188-universe covariance silently.
    # That is the same class of defect as the kRecovered hole this delegation was written to close.
    #
    # SO: presence + finiteness are now REQUIRED. The FPS floor (MIN_COMPLETE = 0.50) is
    # deliberately NOT inherited -- min_complete=0.0 -- because I have not measured the completeness
    # distribution across the 188 universes and a floor tuned on the 285-bin FPS grid is not a
    # measurement about this one. That is a cheap cluster follow-up, and stating it this way makes
    # the missing measurement falsifiable rather than invisible.
    #
    # expect_nbins: the CV defines the grid, so it passes 0 (skip). Universes are checked against the
    # CV's own bin count, which turns a wrong-grid product into this function's clean diagnostic
    # instead of a numpy broadcast error at the subtraction two frames up.
    # NOTE THE SENTINEL ASYMMETRY, which is a documented trap in check() itself: expect_nbins=None
    # means "use the FPS 285 default", expect_nbins=0 means "skip". They are opposite meanings.
    import fps_unfold_complete as _fuc
    _v = _fuc.check(path, expect_nbins=(0 if expect_nbins is None else expect_nbins),
                    min_complete=0.0, require_completeness=True)
    if not _v.get("ok"):
        raise SystemExit(f"[FAIL] {path} is not a COMPLETE product: {_v.get('why')}")
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {path}")
    h = f.Get("hXSecND_flat")
    if not h:
        raise SystemExit(f"[FAIL] hXSecND_flat missing in {path}")
    a = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    f.Close()
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", required=True)
    ap.add_argument("--glob", required=True)
    ap.add_argument("--add-norm", type=float, default=0.0)
    ap.add_argument("--bootstrap-cov", nargs="+", default=None, metavar="ROOT:HIST")
    ap.add_argument("--outdir", default="uq_5d/universe_stage2_5d")
    ap.add_argument("--out-root", default="uq_universe_5d_covariance_combined.root")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    cv = load_flat(args.cv)   # the CV DEFINES the grid, so no bin-count expectation
    print(f"[INFO] CV flat nbins={cv.size}")
    paths = sorted(glob.glob(args.glob))
    if not paths:
        raise SystemExit(f"[FAIL] no universe files matched {args.glob}")

    by_band = defaultdict(list)
    for p in paths:
        m = UNI_RE.match(os.path.basename(p))
        if not m:
            print(f"  [skip] {p}")
            continue
        by_band[m.group("band")].append((int(m.group("idx")),
                                        load_flat(p, expect_nbins=cv.size) - cv))
    print(f"[INFO] {len(paths)} universe files across {len(by_band)} bands")

    rep = cv > 0
    n_rep = int(rep.sum())
    print(f"[INFO] reported bins = {n_rep} of {cv.size}")
    cv_rep = cv[rep]

    band_cov, total = {}, np.zeros((n_rep, n_rep))
    for band, entries in sorted(by_band.items()):
        D = np.stack([d[rep] for _, d in sorted(entries)], axis=0)
        if D.shape[0] < 2:
            print(f"  [skip] {band}: {D.shape[0]} universe(s)")
            continue
        Z = D - D.mean(axis=0, keepdims=True)
        cov = (Z.T @ Z) / D.shape[0]
        band_cov[band] = cov
        total += cov
        diag = np.sqrt(np.maximum(np.diag(cov), 0))
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(cv_rep > 0, diag / cv_rep, 0)
        print(f"  [{band:24s} N={D.shape[0]:3d}] sqrt-tr={np.sqrt(max(np.trace(cov),0)):.3e} "
              f"med rel={100*np.median(rel):.2f}%")

    if args.add_norm > 0:
        v = args.add_norm * cv_rep
        nc = np.outer(v, v)
        band_cov["__Normalization_flat"] = nc
        total += nc
        print(f"  [__Normalization_flat sigma={args.add_norm}] sqrt-tr={np.sqrt(np.trace(nc)):.3e}")

    def cond_rank(m, rc=1e-12):
        ev = np.linalg.eigvalsh(0.5 * (m + m.T))
        pos = ev[ev > ev.max() * rc] if ev.size else ev
        return int(pos.size)

    tdiag = np.sqrt(np.maximum(np.diag(total), 0))
    with np.errstate(divide="ignore", invalid="ignore"):
        trel = np.where(cv_rep > 0, tdiag / cv_rep, 0)
    print(f"\n[TOTAL syst 5D] sqrt-trace={np.sqrt(max(np.trace(total),0)):.3e} "
          f"rank={cond_rank(total)}/{n_rep} median rel={100*np.median(trel):.2f}% "
          f"p84={100*np.percentile(trel,84):.2f}%")

    combined = None
    if args.bootstrap_cov:
        combined = total.copy()
        for spec in args.bootstrap_cov:
            bp, _, bh = spec.partition(":")
            bh = bh or "hCov_stat_reported"
            bf = ROOT.TFile.Open(bp)
            hh = bf.Get(bh)
            nb = hh.GetNbinsX()
            extra = np.array([[hh.GetBinContent(i + 1, j + 1) for j in range(nb)]
                              for i in range(nb)])
            bf.Close()
            if extra.shape != total.shape:
                raise SystemExit(f"[FAIL] {spec} shape {extra.shape} != {total.shape}")
            combined += extra
            print(f"  [+ {bp}:{bh} sqrt-tr={np.sqrt(max(np.trace(extra),0)):.3e}]")
        cdiag = np.sqrt(np.maximum(np.diag(combined), 0))
        with np.errstate(divide="ignore", invalid="ignore"):
            crel = np.where(cv_rep > 0, cdiag / cv_rep, 0)
        print(f"[COMBINED 5D] sqrt-trace={np.sqrt(max(np.trace(combined),0)):.3e} "
              f"rank={cond_rank(combined)}/{n_rep} median rel={100*np.median(crel):.2f}%")

    out = os.path.join(args.outdir, args.out_root)
    rf = ROOT.TFile.Open(out, "RECREATE")

    def wcov(name, mat):
        n = mat.shape[0]
        h = ROOT.TH2D(name, name, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                h.SetBinContent(i + 1, j + 1, float(mat[i, j]))
        h.Write()

    wcov("hCov_universe5d_total", total)
    for b, c in band_cov.items():
        wcov(f"hCov_universe5d_{b}", c)
    if combined is not None:
        wcov("hCov_combined5d_total", combined)
    rf.Close()
    print(f"[wrote] {out}")

    with open(os.path.join(args.outdir, "uq_universe_5d_summary.txt"), "w") as fh:
        fh.write(f"CV: {args.cv}\nglob: {args.glob}\nreported bins: {n_rep}/{cv.size}\n")
        fh.write(f"total syst sqrt-trace={np.sqrt(max(np.trace(total),0)):.4e} "
                 f"median rel={100*np.median(trel):.3f}%\n")
        if combined is not None:
            fh.write(f"combined sqrt-trace={np.sqrt(max(np.trace(combined),0)):.4e} "
                     f"median rel={100*np.median(crel):.3f}%\n")
        grp = defaultdict(float)
        for b, c in band_cov.items():
            grp[category_for_band(b)] += np.sqrt(max(np.trace(c), 0))
        for cat in CATEGORY_ORDER:
            if grp[cat] > 0:
                fh.write(f"  {cat:22s} sum sqrt-trace={grp[cat]:.3e}\n")
    print(f"[wrote] {os.path.join(args.outdir, 'uq_universe_5d_summary.txt')}")


if __name__ == "__main__":
    main()
