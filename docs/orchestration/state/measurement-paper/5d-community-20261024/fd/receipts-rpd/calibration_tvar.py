#!/usr/bin/env python3
"""calibration_spread.py's null with the term it omits: the independent Gaussian with T's MC variance on each cell that
fd_rpd.make_noise adds to every resampled replica deviation (FD-RPD-DECLARATION-PART2.md section 4; the director's ask
(1) of 2026-11-03). T's MC sd has no committed value, so it is bracketed as kappa times the replica sd, in two shapes:
"1/sqrt(e)" (kappa * 0.002/sqrt(e_X), MC exposure proportional to the data's) and "flat" (kappa * the median replica sd
on every playlist). kappa = 0 draws no Gaussian and must reproduce calibration_spread.log's alphas exactly. Everything
else is calibration_spread.py's: the metric, e, the replica noise, the seeds, 8 realizations of 300 null datasets.
calibration_pooled.py reads the log block by block.

    python3 -I -B calibration_tvar.py <repo>
"""
import math
import re
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(REPO / "nd-unfolding"), str(REPO / "nd-unfolding/tests")]
import fd_rpd as rp  # noqa: E402
import test_fd_ct_readers as TR  # noqa: E402

t = TR.Tree(Path(tempfile.mkdtemp()) / "s1", seed=3)
M = (t.Ct + t.Cr) / np.outer(t.f, t.f)
e = np.array([.0847, .0176, .0405, .1359, .0972, .1575, .1311, .0127, .1507, .1001, .0280, .0439])
e /= e.sum()
r2 = rp.R2(e, np.linalg.inv(M))
sd = 0.002 / np.sqrt(e)
SHAPES = {"1/sqrt(e)": sd, "flat": np.full(12, np.median(sd))}
spread = (REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd"
          / "calibration_spread.log").read_text()
print(f"threshold {rp.r2_gate_threshold():.4f} (at {rp.R2_GATE_N} datasets)")
for shape, kappa in [("1/sqrt(e)", 0.0), *((s, k) for s in SHAPES for k in (0.5, 1.0, 2.0))]:
    tsd = kappa * SHAPES[shape][:, None] * np.ones((12, 16))
    print(f"== T's MC sd = {kappa} x {shape} replica sd")
    for nrep in (3, 10, 30):
        al = []
        for real in range(8):
            rng = np.random.default_rng(100 + real)
            reps = {i: rng.standard_normal((nrep, 16)) * sd[i] for i in range(12)}
            dev = {i: (v - v.mean(0)) * math.sqrt(nrep / (nrep - 1)) for i, v in reps.items()}

            def noise(rng):
                k = rng.integers(0, nrep, 12)
                x = np.vstack([dev[i][k[i]] for i in range(12)])
                return x + rng.standard_normal(tsd.shape) * tsd if kappa else x
            al.append(float(np.mean([r2.test(r2.g_of(0.0, noise(rng)))[1] < 0.05 for _ in range(300)])))
        line = f"replicas {nrep:2d}: alpha by realization {[round(a, 3) for a in al]}; min {min(al):.3f} max {max(al):.3f}"
        print(line, flush=True)
        if not kappa:
            assert re.search(rf"^{re.escape(line)}$", spread, re.M), "kappa 0 does not reproduce calibration_spread.log"
