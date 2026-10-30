"""Probe: how large is the relative change of 5B's noise sigma (floor, g_sig) when U @ x is summed in another order
(another BLAS / numpy build)? A1 requires the rebuilt floor and g_sig to equal the committed ones to rtol 1e-12.
Synthetic fine-grid x (no real product read); U is S1's functional matrix from the committed definition."""
import math, sys
from pathlib import Path
import numpy as np
W = Path(sys.argv[1]); sys.path.insert(0, str(W / "nd-unfolding"))
import s1_assemble as sa
fm = sa.fine_map(W / "nd-unfolding/pv-ladder/readouts/h2_definition.json")
U = sa.functional_matrix(fm)
print("nonzeros per row:", (U != 0).sum(axis=1).min(), "-", (U != 0).sum(axis=1).max())
e = {"PA": 0.5334, "PB": 0.2945, "PC": 0.1721}
k = sum(v * v for v in e.values()); k = k / (1 - k)
worst_floor, worst_gsig = [], []
for s in range(20):
    rng = np.random.default_rng(s)
    xs = {X: rng.lognormal(0, 1, U.shape[1]) * 1e-39 for X in e}
    xb = {X: [xs[X] * (1 + rng.normal(0, 0.03, U.shape[1])) for _ in range(10)] for X in e}  # ~0.1-0.3% per cell
    def build(dot):
        x = {X: dot(xs[X]) for X in e}
        D = {X: [dot(v) / x[X] - 1 for v in xb[X]] for X in e}
        gn = [{X: D[X][i] - sum(e[Y] * D[Y][i] for Y in e) for X in e} for i in range(10)]
        Cn = np.mean([k * sum(e[X] * np.outer(h[X], h[X]) for X in e) for h in gn], axis=0)
        gs = {X: np.sqrt(np.mean([h[X] ** 2 for h in gn], axis=0)) for X in e}
        return np.sqrt(np.diag(Cn)), gs, D
    f1, g1, D1 = build(lambda v: U @ v)
    f2, g2, _ = build(lambda v: np.array([math.fsum(U[c] * v) for c in range(16)]))          # exact rounding
    f3, g3, _ = build(lambda v: np.array([np.sum((U[c] * v)[::-1]) for c in range(16)]))     # another order
    worst_floor.append(max(np.max(np.abs(f1 / f2 - 1)), np.max(np.abs(f1 / f3 - 1))))
    worst_gsig.append(max(max(np.max(np.abs(g1[X] / g2[X] - 1)), np.max(np.abs(g1[X] / g3[X] - 1))) for X in e))
print("typical |D|:", np.median(np.abs(np.concatenate([np.concatenate(D1[X]) for X in e]))))
print("max rel diff floor sigma over 20 seeds:", max(worst_floor), " median:", np.median(worst_floor))
print("max rel diff g_sig over 20 seeds:", max(worst_gsig), " median:", np.median(worst_gsig))
print("A1 tolerance 1e-12 exceeded in", sum(v > 1e-12 for v in worst_floor + worst_gsig), "of", 2 * len(worst_floor))
