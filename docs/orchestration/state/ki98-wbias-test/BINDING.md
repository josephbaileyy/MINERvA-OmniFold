# Binding: the KI 98 W-bias confirming test (2026-10-22)

**By** the paper-tighten lane, as director, under [`ASSIGNMENT.md`](ASSIGNMENT.md).

**Bound:** [`DECLARATION.md`](DECLARATION.md) as merged in PR #224 (`4e322dbe`, merged at `be9179bd`), file sha256
`a941ea10518e9411b1b463a96aa98f978687ad0709b4bba72d0193611bdb5262`. It is bound as written: the arms, seeds, metric,
standard errors, decision rule, compute cap and order. Any change after this binding needs a new declaration and a
new binding, and no change may follow a result.

## What the director checked before binding

- **The assignment's conditions are met:**
  - the code commit and the sha256 of every input are named;
  - seeds 204000–204004, by position;
  - the functionals named in the assignment, plus the band aggregates;
  - the metric and its standard errors;
  - a numerical decision rule, k = 2.776 (t, 4 dof), on a declared primary band, EW with W ≥ 3, whose branches were
    exercised on constructed products;
  - a compute cap of 0.5 CPU node-h, enforced by two 15-minute single-node jobs on regular QOS;
  - outputs on `$PSCRATCH` only, and a ledger.
- **The arms answer the question.**
  - Arm (c) restores B/S, with the background and its subtracted prediction both ×0.9, without changing the
    estimator.
  - Arm (b) removes the background, and arm (b0) gives (b) its own reference. Without (b0), (b) would be confounded
    with the purity method's nominal bias (KI 75).
  - The bitwise control on seed 204000 ties the single-experiment runs to the existing products.
- **The tools** (`mk_bkg_scaled.py`, `ki98_read.py`, `tasks.tsv`) write nothing to CFS and refuse to overwrite.
  `tasks.tsv` runs the pinned deploy's `s5c_pseudo.py` with its sha256 guard.

## Accepted limits

- Five seeds per arm resolve a shift of about k·SE. If the W ≥ 3 residual is near the 1–2.5σ the diagnosis inferred,
  UNDETERMINED is a live outcome. It is an outcome, not a failure, and it is not a reason to add seeds after seeing
  a result.
- The verdict concerns the mean shift at this grid point only: not the mechanism, other amplitudes, the q3 point,
  or coverage. That is the declaration's own "Not tested" list.

## After the run

The measurement session commits the receipts, `LEDGER.tsv` and `REPORT.md` here and opens a PR. The director
reviews and merges it, then integrates the outcome into KNOWN_ISSUES row 98, the methods paper and the note. Those
claim changes go to Joseph.
