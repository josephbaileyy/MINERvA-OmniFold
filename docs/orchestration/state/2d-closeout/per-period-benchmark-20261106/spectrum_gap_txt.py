#!/usr/bin/env python3
"""Eigenvalue gaps of the published TotalCovariance at the decade cutoffs of diagnose_tension.py:190.

Covariance only: no cross section is read and nothing is compared. It reads the rounded TEXT release in
2d-unfolding/minerva_paper_anc/, so it only checks whether a cutoff sits near an eigenvalue. The bound run reads the
precision ROOT (DECLARATION.md, C-K). Usage: python3 spectrum_gap_txt.py <repo root>
"""
import sys
import numpy as np

root = sys.argv[1]
anc = f"{root}/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV_"


def load(kind):
    m = np.zeros((224, 224))
    with open(anc + kind + ".txt") as fh:
        next(fh)
        for line in fh:
            if line.strip():
                i, j, v = line.split(",")
                m[int(i), int(j)] = float(v)
    return m


tot, stat = load("total"), load("stat")
mask = np.diag(stat) > 0
lam = np.linalg.eigvalsh(tot[np.ix_(mask, mask)])
r = np.sort(lam / lam.max())[::-1]
print(f"reported cells: {int(mask.sum())}")
print("cutoff   k_kept   lam_k/lam_max   lam_k+1/lam_max   (lam_k/cutoff - 1)")
for c in (1e-2, 1e-4, 1e-6, 1e-8):
    k = int((r > c).sum())
    print(f"{c:7.0e}  {k:6d}   {r[k-1]:.6e}      {r[k]:.6e}        {r[k-1]/c - 1:+.4f}")
