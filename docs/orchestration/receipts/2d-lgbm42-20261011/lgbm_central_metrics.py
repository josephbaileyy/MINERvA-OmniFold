#!/usr/bin/env python3
"""Read-only: paper-comparison metrics for candidate 2D centrals (E_C, LightGBM seed-42 CV, seed 1..10).

Inputs (argv):
  1 fig_arrays.npz (sha256 72394a2b..., manifest committed at publication/release/figs/_data/)
  2 remote_reduce.json (committed, docs/orchestration/state/next-preparation-20261009/two-d-path/operands/)
Definitions copied from 2d-unfolding/compare_to_paper_fullcov.py (pinv over positive-diagonal bins,
pull = diff/sqrt(diag TotalCov), np.std) and agreement_windows_receipt.py (|ours/paper-1| windows,
integral = sum x*area).
"""
import json
import sys

import numpy as np

z = np.load(sys.argv[1], allow_pickle=False)
rr = json.load(open(sys.argv[2]))
paper, C, Cs, area = z["paper_v"], z["cov_total"], z["cov_stat"], z["area_paper"]
area_o = z["area_ours"]  # receipt convention: ours integrated with its own bin areas
mask = np.diag(Cs) > 0
assert mask.sum() == 205
gids = np.array([pt * 16 + pz for pt, pz in rr["cells"]])
assert np.array_equal(np.sort(gids), np.flatnonzero(mask)), "cell order/mask mismatch"


def to224(v):
    out = np.zeros(224)
    out[gids] = np.asarray(v, float)
    return out


cands = {k: to224(v) for k, v in rr["central"].items()}
# control: E_C from remote_reduce must equal the figure-array ours_v (142a45b0) on the mask
ctl = np.max(np.abs(cands["E_C"][mask] - z["ours_v"][mask]) / z["ours_v"][mask])
print(f"control E_C(remote_reduce) vs ours_v(fig_arrays) max rel diff on 205: {ctl:.3e}")

Cm = C[np.ix_(mask, mask)]
Cinv = np.linalg.pinv(Cm)
sig = np.sqrt(np.diag(C))
paper_int = float(np.sum(paper * area))
Ec = cands["E_C"]
print(f"paper integral {paper_int:.5e}")
print(f"{'cand':20s} {'integral':>11s} {'ratio':>7s} {'med r':>7s} {'5%':>9s} {'10%':>9s} {'20%':>9s}"
      f" {'pullMu':>7s} {'pullRMS':>7s} {'chi2/ndf':>8s} {'med|d vs E_C|%':>14s} {'max|d|%':>8s}")
seeds = {}
for k in ["E_C", "CV42_universe_file"] + [f"seed{i}" for i in range(1, 11)]:
    v = cands[k]
    integ = float(np.sum(v * area_o))
    r = v[mask] / paper[mask]
    w = {t: int(np.sum(np.abs(r - 1) <= t)) for t in (0.05, 0.10, 0.20)}
    d = (v - paper)[mask]
    pull = d / sig[mask]
    chi2 = float(d @ Cinv @ d) / 205
    dE = np.abs(v[mask] / Ec[mask] - 1) * 100
    seeds[k] = chi2
    print(f"{k:20s} {integ:11.5e} {integ/paper_int:7.4f} {np.median(r):7.4f} "
          f"{w[0.05]:3d}={100*w[0.05]/205:4.1f} {w[0.10]:3d}={100*w[0.10]/205:4.1f} {w[0.20]:3d}={100*w[0.20]/205:4.1f} "
          f"{pull.mean():7.3f} {pull.std():7.3f} {chi2:8.4f} {np.median(dE):14.3f} {dE.max():8.2f}")
s = np.array([seeds[f"seed{i}"] for i in range(1, 11)])
print(f"seeds1-10 chi2/ndf mean {s.mean():.4f} sd {s.std(ddof=1):.4f} range {s.min():.4f}-{s.max():.4f}")
v42, v1 = cands["CV42_universe_file"][mask], cands["seed1"][mask]
d = np.abs(v42 / v1 - 1) * 100
print(f"CV42 vs seed1 per-bin |rel diff| %: median {np.median(d):.3f} max {d.max():.3f}")
sb = np.asarray(rr["sigma_abs"]["boot_vl170"], float)
print(f"CV42-seed1 in sigma_VL170: median {np.median(np.abs(v42-v1)/sb):.3f} max {np.max(np.abs(v42-v1)/sb):.3f}")
e = Ec[mask]
print(f"E_C-seed1 in sigma_VL170: median {np.median(np.abs(e-v1)/sb):.3f}; E_C-CV42: median {np.median(np.abs(e-v42)/sb):.3f}")
