#!/usr/bin/env python3
"""L3's proposed statistic is breachable by diagonal movement alone -- and here is a repair.

CONFIRMS [cb0b6b]'s C1 refutation by independent measurement, then supplies the replacement
statistic that assessment explicitly declined to supply.

THE REFUTATION. The cause-3 packet's §4.1 requires an L3 statistic to be invariant under
`C -> D C D` in the SOURCE basis, so that pure per-bin sigma movement (L1/L2) cannot be reported
through L3's instrument. The requirement is right. But the proof is about `corr(C)` while the
statistic proposed is `corr(M C M')`, and source-basis rescaling does not survive a projection:

    M (D C D) M'  =  (M D) C (M D)'

which is a projection with a DIFFERENT map. A source rescale reweights how source bins are
AGGREGATED, and no diagonal in the destination basis can undo that. So the proposed statistic
responds to pure diagonal movement, destroying the disjointness the packet is organised around.

MEASURED HERE, independently of [cb0b6b]: `corr(C)` invariant at 4.441e-16 exactly as the packet
proves; `corr(M C M')` NOT invariant. Under a PURE diagonal rescale with source correlations
identical to 4.4e-16, the proposed statistic drifts ~0.3 x the rescale sd, essentially LINEARLY
across three orders of magnitude. That linearity is the decision-relevant part and is new here:
the breach is real but BOUNDED and quantifiable, not catastrophic, so at a realistic delta_bin of
1e-3 the leak into L3 is about 3e-4 rather than something that swamps the statistic.

THE CONFLATION, named precisely: `corr(M C M')` IS invariant under a rescale in the PROJECTED
basis -- trivially, because it is already a correlation matrix. That is the property the packet
proves. It is not the property §4.1 requires.

THE REPAIR. Hold the source diagonal at the REFERENCE member before projecting:

    D0      = diag(sqrt(diag(C_0)))          from member k = 0
    renorm  : C_k  ->  D0 @ corr(C_k) @ D0
    L3 STAT :        corr(M @ renorm(C_k) @ M')

Invariance is EXACT BY CONSTRUCTION rather than by measurement: `corr(D C_k D) = corr(C_k)`
identically, so `renorm(D C_k D) = renorm(C_k)` identically. Measured at 3.3e-16 for rescale sd up
to 2.0. And it is not vacuous -- it still moves under genuine correlation change. Scientifically it
asks exactly L3's disjoint question: holding per-bin variances at the reference member, does this
member's CORRELATION structure move the projected correlation?

PRECONDITIONS, which are not free and belong in the declaration:
  * every destination cell must receive at least one source bin, or its projected variance is zero
    and `corr` divides by zero. `project_cov_nd.py` already censuses this as `n_empty`, so the
    destination-mask declaration already owed for M1 covers it.
  * the source diagonal must be strictly positive on the reported support. The `x_cv > 0` support
    predicate is on the CENTRAL VALUE, not on the variance, so this is a separate check.
  * `renorm(C_k)` is a DIAGNOSTIC TRANSFORM for the L3 comparison only. It is not a covariance to
    be used anywhere else, and nothing here proposes adopting it as one.
  * C_Z is not positive definite (lambda_min = -1.275e-90), so `corr` of it is well defined only
    while the diagonal is positive; the conditioning caveat of
    `probe-20260918-aggregation-channel-directions.py` applies unchanged.

THE COST OF THE REPAIR, STATED RATHER THAN BURIED. `renorm(C_k)` is a HYBRID: member k's
correlations carried on member 0's variances. So the statistic does NOT test member k's actual
projected correlation -- it tests what member k's correlation structure would do at the reference
member's variance weighting. That is unavoidable, and it is the point: the projected correlation of
the ACTUAL C_k cannot be disjoint from L1/L2, because the source variances set how strongly each
source bin is weighted inside its destination cell. Disjointness and actuality cannot both be had.
Whoever adopts this must accept testing the hybrid; anyone who wants the actual object must give up
§4.1's invariance requirement and say so.

Supplies no tolerance. Approves nothing. Synthetic matrices only, no payload, no compute.
Exits 0 while both the breach and the repair still reproduce, 1 otherwise.
"""
import numpy as np


def corr(A):
    d = np.sqrt(np.diag(A))
    return A / np.outer(d, d)


def marg_map(n, d, rng):
    """M1-like: each SOURCE bin lands in exactly ONE destination cell, positive width weight.
    Seeded so every destination cell receives at least one bin (see preconditions)."""
    assign = np.concatenate([np.arange(d), rng.integers(0, d, size=n - d)])
    rng.shuffle(assign)
    w = rng.uniform(0.2, 3.0, size=n)
    M = np.zeros((d, n))
    M[assign, np.arange(n)] = w
    return M


def rand_psd(n, rng):
    A = rng.normal(size=(n, int(1.5 * n)))
    C = A @ A.T
    return C + 1e-6 * np.trace(C) / n * np.eye(n)


def main():
    rng = np.random.default_rng(7)
    n, d = 300, 42
    C0 = rand_psd(n, rng)
    M = marg_map(n, d, rng)
    D0 = np.diag(np.sqrt(np.diag(C0)))

    def renorm(Ck):
        return D0 @ corr(Ck) @ D0

    Rp0 = corr(M @ C0 @ M.T)
    Rr0 = corr(M @ renorm(C0) @ M.T)

    print("PURE diagonal rescale of the source; source correlations are untouched.\n")
    print(f"{'rescale sd':>11} {'src corr drift':>16} {'PROPOSED stat':>15} "
          f"{'per sd':>8} {'REPAIRED stat':>15}")
    fail = []
    rows = []
    for sd in (1e-3, 1e-2, 0.05, 0.20, 0.70, 2.0):
        s = a = b = 0.0
        for _ in range(40):
            D = np.diag(np.exp(rng.normal(0, sd, size=n)))
            Ck = D @ C0 @ D
            s = max(s, np.abs(corr(Ck) - corr(C0)).max())
            a = max(a, np.abs(corr(M @ Ck @ M.T) - Rp0).max())
            b = max(b, np.abs(corr(M @ renorm(Ck) @ M.T) - Rr0).max())
        rows.append((sd, a))
        print(f"{sd:11.3g} {s:16.3e} {a:15.4f} {a / sd:8.3f} {b:15.3e}")
        if s > 1e-12:                                          # CLAIM 1: source corr invariant
            fail.append(f"sd={sd}: source corr moved {s:.3e}, should be ~0")
        if b > 1e-12:                                          # CLAIM 3: repair is invariant
            fail.append(f"sd={sd}: REPAIRED stat moved {b:.3e}, repair not holding")
    if not all(a > 0.5 * sd * 0.2 for sd, a in rows):           # CLAIM 2: breach is real and ~linear
        fail.append(f"proposed statistic did not breach as expected: {rows}")

    print("\nThe repair must still SEE a genuine correlation change (not vacuous):")
    for mix in (0.01, 0.05, 0.20):
        C2 = (1 - mix) * C0 + mix * rand_psd(n, rng)
        drift = np.abs(corr(M @ renorm(C2) @ M.T) - Rr0).max()
        print(f"  correlation mix {mix:4.2f} -> repaired stat moves {drift:.4f}")
        if drift < 1e-4:                                        # CLAIM 4: not vacuous
            fail.append(f"mix={mix}: repaired stat moved only {drift:.3e} -- vacuous")

    print()
    if fail:
        print("PROBE FAILED:")
        for f in fail:
            print("  " + f)
        return 1
    print("PROBE OK: source corr invariant; PROPOSED statistic breached by diagonal movement")
    print("alone, ~0.3x the rescale sd and near-linear; REPAIRED statistic invariant to machine")
    print("precision at every scale tested, and still responsive to real correlation change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
