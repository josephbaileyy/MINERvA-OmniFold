#!/usr/bin/env python3
"""The size of R2's permutation test under a replica-resampled null, by the number of replicas (FD-RPD-DECLARATION-PART2.md
section 4; the director's request of 2026-11-02 to record the alpha measurements at 10 and 30 replicas). Synthetic:
the readers' test metric (test_fd_ct_readers.Tree seed 3), the 12 approximate exposure shares, independent Gaussian
replica noise of relative sd 0.002/sqrt(e) per cell; for each replica count, 8 realizations of the replica set, each
with 300 null datasets drawn by resampling the replica deviations (as fd_rpd.run_readout's noise does). alpha is the
share with p_flux < 0.05. Monte Carlo error per alpha at 300: about 0.013.

    python3 -I -B calibration_spread.py <repo>
"""
import math
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
print(f"threshold {rp.r2_gate_threshold():.4f} (at {rp.R2_GATE_N} datasets)")
for nrep in (3, 10, 30):
    al = []
    for real in range(8):
        rng = np.random.default_rng(100 + real)
        reps = {i: rng.standard_normal((nrep, 16)) * sd[i] for i in range(12)}
        dev = {i: (v - v.mean(0)) * math.sqrt(nrep / (nrep - 1)) for i, v in reps.items()}

        def noise(rng):
            k = rng.integers(0, nrep, 12)
            return np.vstack([dev[i][k[i]] for i in range(12)])
        al.append(float(np.mean([r2.test(r2.g_of(0.0, noise(rng)))[1] < 0.05 for _ in range(300)])))
    print(f"replicas {nrep:2d}: alpha by realization {[round(a, 3) for a in al]}; min {min(al):.3f} max {max(al):.3f}")
