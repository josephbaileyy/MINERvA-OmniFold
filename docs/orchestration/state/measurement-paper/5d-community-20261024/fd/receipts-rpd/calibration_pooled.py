#!/usr/bin/env python3
"""The numbers FD-RPD-DECLARATION-PART2.md section 4 quotes from calibration_spread.log (the director's ruling of
2026-11-03): per replica count, the pooled alpha over the 8 realizations of 300 null datasets and its binomial error;
the dispersion chi-square of the 8 counts about the pooled rate (7 dof), and its p; and, at the 30-replica pooled rate,
the binomial probability that one 300-dataset alpha, and one 2000-dataset alpha (the readout's), exceeds the gate.
Arithmetic on the log only; each count is recovered from its alpha (count/300, printed to 3 places).

    python3 -I -B calibration_pooled.py <calibration_spread.log>
"""
import math
import re
import sys

N_SET, N_GATE = 300, 2000


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p), summed in log space."""
    lp, lq = math.log(p), math.log1p(-p)
    return sum(math.exp(math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1) + j * lp + (n - j) * lq)
               for j in range(k, n + 1))


def chi2_sf(x: float, dof: int) -> float:
    """Upper tail of chi-square with an odd number of dof, by the closed form."""
    assert dof % 2 == 1
    s = math.erfc(math.sqrt(x / 2))
    term = math.sqrt(2 * x / math.pi) * math.exp(-x / 2)
    for k in range(1, (dof - 1) // 2 + 1):
        s += term
        term *= x / (2 * k + 1)
    return s


text = open(sys.argv[1]).read()
gate = 0.05 + 3.0 * math.sqrt(0.05 * 0.95 / N_GATE)      # part 1 section 5; the log prints it to 4 places
assert re.search(rf"threshold {gate:.4f} \(at {N_GATE} datasets\)", text), "the log's threshold is not the gate"
p30 = None
for nrep, vals in re.findall(r"replicas\s+(\d+): alpha by realization \[([^\]]+)\]", text):
    alphas = [float(v) for v in vals.split(",")]
    counts = [round(a * N_SET) for a in alphas]      # the log prints count/300 to 3 places, so the count is unique
    assert all(abs(c / N_SET - a) < 6e-4 for c, a in zip(counts, alphas)), "a logged alpha is not a count over 300"
    n = N_SET * len(counts)
    p = sum(counts) / n
    chi2 = sum((c - N_SET * p) ** 2 / (N_SET * p * (1 - p)) for c in counts)
    se = math.sqrt(p * (1 - p) / n)
    print(f"replicas {int(nrep):2d}: counts {counts}; pooled {sum(counts)}/{n} = {p:.4f} +- {se:.4f};"
          f" dispersion chi2 {chi2:.2f} on {len(counts) - 1} dof, p {chi2_sf(chi2, len(counts) - 1):.2f}")
    if int(nrep) == 30:
        p30 = p
print(f"gate {gate:.5f}; at the 30-replica pooled rate {p30:.4f}:"
      f" P(one {N_SET}-set alpha > gate) = {binom_sf(math.floor(gate * N_SET) + 1, N_SET, p30):.3f},"
      f" P(one {N_GATE}-set alpha > gate) = {binom_sf(math.floor(gate * N_GATE) + 1, N_GATE, p30):.3f}")
