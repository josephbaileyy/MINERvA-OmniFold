"""Probe: s5n_pseudo.bootstrap_replica seeds its Poisson streams from b alone, so PA's and PB's replica b weight their
row i identically. Correlation of the paired fractional fluctuations of a 16-cell sum and of one cell."""
import numpy as np
NA, NB = 533_000, 295_000            # rows in proportion to the exposure shares
rng = np.random.default_rng(0)
cellA = rng.integers(0, 40, NA); cellB = rng.integers(0, 40, NB)   # 40 bins, 16 of them "reported"
rep = lambda c: c < 16
def frac(cells, k, sel):
    return k[sel(cells)].sum() / sel(cells).sum() - 1
for mode in ("shared seed b (5B)", "distinct seeds (2D: 1000+b, 2000+b)"):
    dA, dB, cA, cB = [], [], [], []
    for b in range(1, 401):
        kA = np.random.default_rng(b).poisson(np.ones(NA))
        kB = np.random.default_rng(b if mode.startswith("shared") else 2000 + b).poisson(np.ones(NB))
        dA.append(frac(cellA, kA, rep)); dB.append(frac(cellB, kB, rep))
        cA.append(frac(cellA, kA, lambda c: c == 3)); cB.append(frac(cellB, kB, lambda c: c == 3))
    r16 = np.corrcoef(dA, dB)[0, 1]; r1 = np.corrcoef(cA, cB)[0, 1]
    sd_ratio = np.std(np.subtract(dA, dB)) / np.sqrt(np.var(dA) + np.var(dB))
    print(f"{mode}: corr(16-cell sum) {r16:+.3f}, corr(one cell) {r1:+.3f}, "
          f"sd(dA-dB)/sqrt(varA+varB) {sd_ratio:.3f}")
print("prediction for the 16-cell sum: (16/40) * sqrt(NB/NA) =", round(16 / 40 * np.sqrt(NB / NA), 3))
