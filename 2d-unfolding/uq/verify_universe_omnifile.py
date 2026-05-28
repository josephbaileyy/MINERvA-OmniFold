#!/usr/bin/env python3
"""Verify a universe-enabled omnifile.

Checks:
  1. mc_signal_reco and mc_truth_denom carry the expected (band, idx)
     branch pairs (w_truth_<sanitized>_<idx>, w_reco_<sanitized>_<idx>).
  2. Per-band index counts match what the C++ allowlist requested.
  3. Spot-check a handful of MC events to confirm the universe weights
     are non-trivial (Flux universes shift on every event; vertical
     GENIE knobs match CV on non-applicable channels).
  4. CV weight columns (w_truth, w_reco) are unchanged compared to the
     pre-universe omnifile (if available alongside) for a small sample.

Usage:
  python uq/verify_universe_omnifile.py \
      --omnifile runEventLoopOmniFold_1A_universes.root \
      [--cv-omnifile runEventLoopOmniFold_1A.root]
"""
from __future__ import annotations

import argparse
import re
from collections import defaultdict

import numpy as np
import ROOT


EXPECTED_BANDS = {
    "Flux": 100,
    "MaCCQE": 2,
    "Rvp1pi": 2,
    "Rvn1pi": 2,
    "MinosEfficiency": 2,
    "Muon_Energy_MINOS": 2,
}


def _sanitize(band: str) -> str:
    return "".join(c if (c.isalnum() or c == "_") else "_" for c in band)


def _parse_uni_branches(brs, prefix):
    pat = re.compile(rf"^w_{prefix}_(.+)_(\d+)$")
    table = defaultdict(list)
    for b in brs:
        if b in ("w_truth", "w_reco"):
            continue
        m = pat.match(b)
        if not m:
            continue
        table[m.group(1)].append((int(m.group(2)), b))
    return {k: sorted(v) for k, v in table.items()}


def check_tree(t, name, prefix, expected):
    brs = [b.GetName() for b in t.GetListOfBranches()]
    table = _parse_uni_branches(brs, prefix)
    print(f"\n[{name}] prefix={prefix}: found {sum(len(v) for v in table.values())} universe branches")
    ok = True
    for band, want_n in expected.items():
        san = _sanitize(band)
        got = table.get(san, [])
        marker = "OK " if len(got) == want_n else "BAD"
        print(f"  [{marker}] {band:30s} expected {want_n:3d}, got {len(got):3d}")
        if len(got) != want_n:
            ok = False
    extras = [b for b in table if b not in {_sanitize(x) for x in expected}]
    if extras:
        print(f"  [WARN] unexpected bands in tree: {extras}")
    return ok


def spotcheck_weights(t, sample_n=10):
    brs = [b.GetName() for b in t.GetListOfBranches()]
    cv_b = "w_truth" if "w_truth" in brs else "w_reco"
    flux0 = f"w_{cv_b.split('_')[1]}_Flux_0"
    macc0 = f"w_{cv_b.split('_')[1]}_MaCCQE_0"
    if flux0 not in brs or macc0 not in brs:
        print(f"  [skip] required universe columns absent ({flux0}, {macc0})")
        return
    n = min(t.GetEntries(), sample_n)
    cv = np.zeros(n); fl = np.zeros(n); mc = np.zeros(n)
    for i in range(n):
        t.GetEntry(i)
        cv[i] = getattr(t, cv_b)
        fl[i] = getattr(t, flux0)
        mc[i] = getattr(t, macc0)
    print(f"  Spot check on first {n} events of '{cv_b}':")
    print(f"    {cv_b:12s}  mean={cv.mean():.4g}  range=({cv.min():.4g}, {cv.max():.4g})")
    print(f"    {flux0:25s} mean={fl.mean():.4g}  shift vs CV: mean={(fl/cv-1).mean()*100:+.2f}%  max|d|={np.max(np.abs(fl/cv-1))*100:.2f}%")
    print(f"    {macc0:25s} mean={mc.mean():.4g}  shift vs CV: mean={(mc/cv-1).mean()*100:+.2f}%  max|d|={np.max(np.abs(mc/cv-1))*100:.2f}%")


def cv_regression(omni, cv_omni, tree_name, weight_col, sample_n=200):
    if cv_omni is None:
        print(f"\n[CV regression {tree_name}] no --cv-omnifile given, skipping.")
        return
    f1 = ROOT.TFile.Open(omni)
    f2 = ROOT.TFile.Open(cv_omni)
    t1 = f1.Get(tree_name); t2 = f2.Get(tree_name)
    if not t1 or not t2:
        print(f"\n[CV regression {tree_name}] tree missing in one file, skipping.")
        return
    n = min(t1.GetEntries(), t2.GetEntries(), sample_n)
    a = np.zeros(n); b = np.zeros(n)
    for i in range(n):
        t1.GetEntry(i); t2.GetEntry(i)
        a[i] = getattr(t1, weight_col)
        b[i] = getattr(t2, weight_col)
    delta = np.abs(a - b)
    print(f"\n[CV regression {tree_name}.{weight_col}] sample={n}")
    print(f"  universe-omnifile mean={a.mean():.6g}  pre-universe mean={b.mean():.6g}")
    print(f"  max|delta|={delta.max():.3e}  median|delta|={np.median(delta):.3e}")
    print(f"  STATUS: {'OK' if delta.max() < 1e-9 else 'DIFFERS'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--cv-omnifile", default=None,
                    help="Optional CV omnifile (no universes) for w_truth/w_reco regression.")
    args = ap.parse_args()

    f = ROOT.TFile.Open(args.omnifile)
    print(f"Inspecting {args.omnifile}")
    print(f"  file size: {f.GetSize()} bytes")

    all_ok = True
    for tname, prefix in [("mc_signal_reco", "truth"), ("mc_signal_reco", "reco"),
                          ("mc_truth_denom", "truth")]:
        t = f.Get(tname)
        if not t:
            print(f"\n[{tname}] MISSING")
            all_ok = False
            continue
        ok = check_tree(t, tname, prefix, EXPECTED_BANDS)
        all_ok = all_ok and ok
        if prefix == "truth":
            spotcheck_weights(t)

    cv_regression(args.omnifile, args.cv_omnifile, "mc_signal_reco", "w_reco")
    cv_regression(args.omnifile, args.cv_omnifile, "mc_signal_reco", "w_truth")

    print("\nOVERALL:", "OK" if all_ok else "FAIL")


if __name__ == "__main__":
    main()
