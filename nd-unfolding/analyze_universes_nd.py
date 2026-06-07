#!/usr/bin/env python3
"""Universe-covariance rollup for the ND (4D q3) OmniFold UQ campaign.

ND analogue of ../3d-unfolding/uq_3d/analyze_universes_3d.py. Reads the flat
hXSecND_flat (C-order ravel over the nd shape) from a CV unfold and the per-(band,idx)
universe unfolds produced by `unfold_nd_omnifold_unbinned.py --universe BAND:IDX`, and
builds the block-summed systematic covariance (per-band C_band = (1/N)sum (X-<X>)(X-<X>)^T,
MAT-conformant), an optional flat normalization band, and an optional block-sum with extra
(stat/ML) covariances. Reported bins = CV>0.

  python analyze_universes_nd.py --cv products/4d/xsec_4d_MEFHC_5iter_lgbm.root \
      --glob 'uq_4d/universe_sweep/4d_xsec_*_uni_full_*.root' \
      --add-norm 0.014 --outdir uq_4d/universe_stage2_4d/
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


def load_flat(path):
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
    ap.add_argument("--outdir", default="uq_4d/universe_stage2_4d")
    ap.add_argument("--out-root", default="uq_universe_4d_covariance.root")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    cv = load_flat(args.cv)
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
        by_band[m.group("band")].append((int(m.group("idx")), load_flat(p) - cv))
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
    print(f"\n[TOTAL syst 4D] sqrt-trace={np.sqrt(max(np.trace(total),0)):.3e} "
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
        print(f"[COMBINED 4D] sqrt-trace={np.sqrt(max(np.trace(combined),0)):.3e} "
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

    wcov("hCov_universe4d_total", total)
    for b, c in band_cov.items():
        wcov(f"hCov_universe4d_{b}", c)
    if combined is not None:
        wcov("hCov_combined4d_total", combined)
    rf.Close()
    print(f"[wrote] {out}")

    with open(os.path.join(args.outdir, "uq_universe_4d_summary.txt"), "w") as fh:
        fh.write(f"CV: {args.cv}\nglob: {args.glob}\nreported bins: {n_rep}/{cv.size}\n")
        fh.write(f"total syst sqrt-trace={np.sqrt(max(np.trace(total),0)):.4e} "
                 f"median rel={100*np.median(trel):.3f}%\n")
        grp = defaultdict(float)
        for b, c in band_cov.items():
            grp[category_for_band(b)] += np.sqrt(max(np.trace(c), 0))
        for cat in CATEGORY_ORDER:
            if grp[cat] > 0:
                fh.write(f"  {cat:22s} sum sqrt-trace={grp[cat]:.3e}\n")
    print(f"[wrote] {os.path.join(args.outdir, 'uq_universe_4d_summary.txt')}")


if __name__ == "__main__":
    main()
