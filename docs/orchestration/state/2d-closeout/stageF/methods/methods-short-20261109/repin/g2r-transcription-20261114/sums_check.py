#!/usr/bin/env python3
"""Measure whether #981's exact block identities can hold under C_new, from the committed transcriptions only.
Run from the top of a checkout: python3 sums_check.py. #981 (91f9cb615) requires, bitwise, Q == s5_total + C_PL and
s5_total == universe + stat + c08 (build_package.py:575-579). C_new replaces only the universe block's G2R part:
C_new = Q - C_univ_old + C_univ_new (bitwise, transcribe.out). The package's universe block is not C_univ_old (it
also holds the other bands and the normalization), so its new universe and s5_total blocks must be derived. This
prints, for each of the two natural derivation orders, the number of the 42025 entries at which each identity fails
bitwise, and the largest relative residual (over the largest |entry| of C_new)."""
import csv, subprocess
import numpy as np

C2A = ("docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/receipts/c2a-20261109/"
       "transcription")
G2R = "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/repin/g2r-transcription-20261114/transcription"


def mat(text):
    r = list(csv.reader(text.splitlines()))
    return np.array([[float(v) for v in q[1:]] for q in r[1:]], dtype=np.float64)


c2a = {k: mat(subprocess.run(["git", "show", f"origin/pkg/methods-result-20261109:{C2A}/cov2d_{k}.csv"],
                             capture_output=True, text=True, check=True).stdout)
       for k in ("Q", "s5_total", "universe", "stat", "c08", "C_PL")}
g = {k: mat(open(f"{G2R}/g2r_{k}.csv").read()) for k in ("C_new", "C_univ_old", "C_univ_new")}
uo, un, cn = g["C_univ_old"], g["C_univ_new"], g["C_new"]
scale = np.max(np.abs(cn))
print("c2a, as committed: Q == s5_total + C_PL bitwise:", (c2a["s5_total"] + c2a["C_PL"]).tobytes() == c2a["Q"].tobytes(),
      "; s5_total == universe + stat + c08 bitwise:",
      (c2a["universe"] + c2a["stat"] + c2a["c08"]).tobytes() == c2a["s5_total"].tobytes())
for name, U, S in (("universe - C_univ_old + C_univ_new, s5_total - C_univ_old + C_univ_new",
                    c2a["universe"] - uo + un, c2a["s5_total"] - uo + un),
                   ("universe + (C_univ_new - C_univ_old), s5_total + (C_univ_new - C_univ_old)",
                    c2a["universe"] + (un - uo), c2a["s5_total"] + (un - uo))):
    print(f"derivation: {name}")
    for lab, lhs, rhs in (("C_new == s5_total' + C_PL", cn, S + c2a["C_PL"]),
                          ("s5_total' == universe' + stat + c08", S, U + c2a["stat"] + c2a["c08"])):
        print(f"  {lab}: {int(np.sum(lhs != rhs))} of 42025 entries differ; largest |residual|/max|C_new| "
              f"{float(np.max(np.abs(lhs - rhs)) / scale):.3e}")
R = c2a["universe"] - uo
w = np.linalg.eigvalsh((R + R.T) / 2)
print(f"package universe block - C_univ_old: eigenvalues above 1e-12 of the largest: {int(np.sum(w > 1e-12 * w[-1]))}; "
      f"smallest/largest {w[0] / w[-1]:.3e}")
