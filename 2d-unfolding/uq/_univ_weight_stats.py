#!/usr/bin/env python3
"""Per-band universe weight variation summary.

For each band X (Flux, MaCCQE, Rvp1pi, Rvn1pi, MinosEfficiency,
Muon_Energy_MINOS) and each universe index U, compute the per-event
ratio r = w_truth_X_U / w_truth, and report:

  - median |r-1|  (typical weight perturbation)
  - rms (r-1)     (envelope-defining RMS weight perturbation)
  - max |r-1|     (extreme bin contribution)
  - per-event-weighted sum-ratio (Sum w_X_U / Sum w_CV) -> integrated yield shift

Reads the mc_truth_denom tree of runEventLoopOmniFold_MEFHC_universes.root.
Samples up to N_SAMPLE entries to keep this fast (the file is 64 GB)."""

import re
import numpy as np
import ROOT
from collections import defaultdict

ROOT.gROOT.SetBatch(True)
N_SAMPLE = 500_000  # uniform stride sample

f = ROOT.TFile.Open("../runEventLoopOmniFold_MEFHC_universes.root")
t = f.Get("mc_truth_denom")
N = t.GetEntries()
print(f"[univ-weights] tree has {N} entries; sampling {N_SAMPLE}")

names = [b.GetName() for b in t.GetListOfBranches()]
univ = [n for n in names if re.match(r"w_truth_.+_\d+$", n)]
bands = defaultdict(list)
for n in univ:
    m = re.match(r"w_truth_(.+)_(\d+)$", n)
    bands[m.group(1)].append((int(m.group(2)), n))
for b in bands:
    bands[b].sort()

print(f"[univ-weights] bands: { {b: len(v) for b,v in bands.items()} }")

# Build sampled CV weight array via TTree::Draw with GetVal + Estimate
stride = max(1, N // N_SAMPLE)
selection = f"(Entry$ % {stride}) == 0"

def sample(branch):
    t.SetEstimate(N_SAMPLE + 1000)
    n = t.Draw(branch, selection, "goff")
    arr = np.frombuffer(t.GetV1(), dtype=np.float64, count=int(n)).astype(np.float64).copy()
    return arr

print("[univ-weights] sampling CV weight w_truth ...")
cv = sample("w_truth")
finite = np.isfinite(cv)
print(f"  CV n_sample={cv.size}  mean={cv[finite].mean():.4e}  "
      f"nonzero={(cv!=0).sum()}  finite={finite.sum()}  "
      f"min={cv[finite].min():.3e}  max={cv[finite].max():.3e}")

# Restrict to events with |cv| above a sane floor and finite
cv_floor = 1e-6 * np.median(np.abs(cv[cv != 0]))
nz = (np.abs(cv) > cv_floor) & np.isfinite(cv)
print(f"  Using {nz.sum()}/{cv.size} events (|cv| > {cv_floor:.3e})")

print()
print(f"Per-event weight perturbation r = w_universe / w_CV, reported as |r-1| in %.")
print(f"Using percentile-based statistics (robust to outlier events).")
print()
print(f"{'band':<22} {'#u':>3} {'med':>8} {'p84':>8} {'p99':>8} {'p99.9':>9} {'yield_shift_rms':>16}")
print("-" * 80)
for band, lst in sorted(bands.items()):
    p50_rs, p84_rs, p99_rs, p999_rs, ws_rs = [], [], [], [], []
    pairs_detail = []
    for idx, br in lst:
        wu = sample(br).astype(np.float64)
        if wu.size != cv.size:
            print(f"  WARN size mismatch {br}")
            continue
        good = nz & np.isfinite(wu)
        r = wu[good] / cv[good]
        good_r = np.isfinite(r)
        absd = np.abs(r[good_r] - 1.0)
        p50_rs.append(np.percentile(absd, 50) * 100)
        p84_rs.append(np.percentile(absd, 84) * 100)
        p99_rs.append(np.percentile(absd, 99) * 100)
        p999_rs.append(np.percentile(absd, 99.9) * 100)
        ws_rs.append((wu[good][good_r].sum() / cv[good][good_r].sum() - 1.0) * 100)
        pairs_detail.append((br, p50_rs[-1], p84_rs[-1], p99_rs[-1], p999_rs[-1], ws_rs[-1]))
    # Across-universe within the band: median of per-universe stats
    p50 = np.median(p50_rs)
    p84 = np.median(p84_rs)
    p99 = np.median(p99_rs)
    p999 = np.median(p999_rs)
    ws_rms = np.sqrt(np.mean(np.array(ws_rs) ** 2))
    print(f"{band:<22} {len(lst):>3} "
          f"{p50:>7.3f}% {p84:>7.3f}% {p99:>7.3f}% {p999:>8.3f}% {ws_rms:>15.3f}%")
    if len(lst) == 2:
        for br, m, s, n, t9, w in pairs_detail:
            print(f"  {br:<30}  p50={m:6.3f}%  p84={s:6.3f}%  p99={n:7.3f}%  p99.9={t9:7.3f}%  yield_shift={w:+7.3f}%")
print()
print("Notes:")
print("  med|r-1| = per-event typical weight perturbation (median, |.|).")
print("  rms(r-1) = per-event RMS weight perturbation.")
print("  max|r-1| = tail bound (one outlier event can be large).")
print("  <r>w     = integrated-yield shift (sum w_u / sum w_CV - 1), RMS over universes.")
