#!/usr/bin/env python3
"""RS1 §5's band reading under known truth: how often an arm reads DEFINITE in the right band (audit E1/E3 on #867).

Pure simulation, no inputs and no data: a design check, like FD-STAB's gatesim.

The model, per trial:
- 153 functionals with A0 spreads s_j drawn log-uniform over a decade;
- an arm with spread M_true * s_j;
- per seed, each functional's relative deviation is s_j * z, with z = sqrt(c) g_seed + sqrt(1 - c) e_seed,j;
  c correlates the functionals through the shared seed (unmeasured; the audit used 0 and 0.8);
- the arm's and A0's z at the same seed are correlated by `pair_corr` (paired arms share the protocol's draws on at
  least one axis or one consumer; 0 is the conservative case for the interval's width).

The statistic is §5's exactly:
- per functional, the SD (ddof 1) of F / mean(F) - 1 over seeds;
- ratio to A0's; the median over functionals; 2,000 bootstrap resamples of the seeds, jointly for a paired arm;
- the 5th-95th percentile interval; bands R <= 0.10 < P < 0.70 <= C, DEFINITE when the interval lies in one band.
The deviations are added to 1 and divided by their mean, as the products would be.

    python3 rs1_power_sim.py > rs1_power_sim.out.txt
"""
from __future__ import annotations

import itertools

import numpy as np

N_FUNC = 153
N_BOOT = 2000
N_TRIALS = 150
SEED = 20261106
R_MAX, C_MIN = 0.10, 0.70


def band(m: float) -> str:
    return "R" if m <= R_MAX else ("C" if m >= C_MIN else "P")


def reading(lo: float, hi: float) -> str:
    b1, b2 = band(lo), band(hi)
    return b1 if b1 == b2 else "INCONCLUSIVE"


def rel_sd(F: np.ndarray, axis: int) -> np.ndarray:
    """SD (ddof 1) of F / mean - 1 along the seed axis."""
    return np.std(F / F.mean(axis=axis, keepdims=True), axis=axis, ddof=1)


def trial(rng, n: int, m_true: float, c: float, pair_corr: float, paired: bool) -> tuple[str, float, float, float]:
    s = 1e-3 * 10 ** rng.uniform(-0.5, 0.5, N_FUNC)
    g = rng.normal(size=(2, n, 1))
    e = rng.normal(size=(2, n, N_FUNC))
    z = np.sqrt(c) * g + np.sqrt(1 - c) * e
    z_arm = pair_corr * z[0] + np.sqrt(1 - pair_corr ** 2) * z[1]
    F0 = 1.0 + s * z[0]
    Fa = 1.0 + m_true * s * z_arm
    ok = rel_sd(F0, 0) > 0
    m_point = float(np.median(rel_sd(Fa, 0)[ok] / rel_sd(F0, 0)[ok]))
    i0 = rng.integers(0, n, size=(N_BOOT, n))
    ia = i0 if paired else rng.integers(0, n, size=(N_BOOT, n))
    s0 = rel_sd(F0[i0], 1)
    sa = rel_sd(Fa[ia], 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        rho = np.where(s0 > 0, sa / s0, np.nan)
    med = np.nanmedian(rho, axis=1)
    lo, hi = np.percentile(med, [5, 95])
    return reading(lo, hi), m_point, float(lo), float(hi)


def main() -> None:
    rng = np.random.default_rng(SEED)
    print(f"# RS1 band reading under known truth; {N_TRIALS} trials, {N_BOOT} resamples, {N_FUNC} functionals, seed {SEED}")
    print("# n\tpaired\tpair_corr\tc\tM_true\tP(R)\tP(P)\tP(C)\tP(INCONCL)\tmedian interval")
    grid = itertools.product((10, 20), (True, False), (0.0, 0.5), (0.0, 0.8), (0.0, 0.05, 0.4, 1.0, 1.5))
    for n, paired, pc, c, m in grid:
        if not paired and pc:
            continue
        res = [trial(rng, n, m, c, pc, paired) for _ in range(N_TRIALS)]
        k = [r[0] for r in res]
        p = {b: k.count(b) / N_TRIALS for b in ("R", "P", "C", "INCONCLUSIVE")}
        lo = float(np.median([r[2] for r in res]))
        hi = float(np.median([r[3] for r in res]))
        print(f"{n}\t{paired}\t{pc}\t{c}\t{m}\t{p['R']:.2f}\t{p['P']:.2f}\t{p['C']:.2f}\t{p['INCONCLUSIVE']:.2f}"
              f"\t[{lo:.2f}, {hi:.2f}]", flush=True)


if __name__ == "__main__":
    main()
