# PREDECLARATION 2026-08-13 — the diagonal-vs-central row-order check

**Written and committed BEFORE the check is run.** Nothing here was chosen after seeing a number.
The previous mapping test's ordering slipped and cost the *status* of a correct answer; this one is
predeclared in the tree so that cannot recur.

## The residual being tested

D found, and the mediator confirmed, that **nothing verifies that the covariance matrix's ROW ORDER
matches the mask's enumeration.** The only binding is `p4_lib.py:1300`:

```
require(M.shape[1] == C_high.shape[0], f"M cols {M.shape[1]} != C dim {C_high.shape[0]}")
```

**A shape check cannot see a permutation.** Under a consistent row+column reordering `P C Pᵀ`:
`trace`, `sqrt_tr_old`, `sqrt_tr_new` and the multiset of diagonal entries are all preserved
**exactly**, the shape check passes, and per-bin assignment is destroyed with nothing looking at it.

**Two things that must NOT be cited as covering it:**

1. The docstring on that same function says *"(preserves density/order)"*. **That is a prose assertion
   one line above a check that verifies only shape** — the same declaration-vs-evidence gap as
   `corder: "C"` in the manifest.
2. **`check_projection_validity` (`p4_lib.py:1318`) does NOT help.** It asserts `C_low` is symmetric
   and PSD, and **a consistent permutation `P C Pᵀ` of a symmetric PSD matrix is still symmetric and
   still PSD.** Every one of its assertions survives this failure mode. Recorded so a future reader
   who finds `:1318` does not conclude the order is gated.

**Why materiality does not cover it, which is where D declined the mediator's reading:**
promote-on-margin absorbs a small shared convention error — 4.4× is ample. It does **not** absorb a
permutation, because **a permutation preserves the SCALE of the projected uncertainty while destroying
its per-bin meaning.** The marginal lands plausibly inside 4.4× and is wrong anyway.

## The instrument, and why it is a third one

Correlate the covariance **diagonal** against the **central values**, bin by bin, over the 10,694
reported bins. The central values are a **third instrument**, distinct from both the mask and the 4D
chain used in the earlier checks — and they are themselves pinned (`p4_evidence.py:409`,
`central5d_sha256 == OBS["central5d"]`), so the instrument is not floating.

## PREDECLARED EXPECTATIONS — stated before the run

Let `s_i = sqrt(diag(C))_i` and `x_i = |central_i|` over the reported bins, and
`f_i = s_i / x_i` the per-bin fractional uncertainty.

**Statistic 1 — Spearman rank correlation `rho(s, x)`.**
- **Correct order: `rho > 0.90`.** Cross sections span orders of magnitude across the 5D grid and the
  per-bin fractional uncertainty is O(10%) with limited spread, so `s` must track `x` near-monotonically.
- **Permuted: `|rho| < 0.05`.** Pairing `s` with unrelated `x` destroys the rank relation; for
  n = 10,694 the sampling scatter on a null correlation is ~1/sqrt(n) ≈ 0.01.

**Statistic 2 — the median of `f`, against an independently recorded number.**
- **Correct order: `median(f)` reproduces the ledger's recorded per-bin median to within ~1 percentage
  point.** `uq_universe_5d_summary.txt` records `combined ... median rel=13.432%` over these 10,694
  bins, and `VALIDATION_LEDGER.md:1043` records `13.69%` over the 10,550 PET-common subset. This is
  the strongest arm: it is a match against a number written by a different producer at a different
  time.
- **Permuted: `median(f)` moves off that value and need not stay near it.**

**Statistic 3 — the SPREAD of `f`, which is the sharpest discriminator.**
- **Correct order: `f` is tightly clustered** — predeclared as `IQR(f) / median(f) < 1`, i.e. the
  interquartile range is smaller than the median itself.
- **Permuted: the spread explodes over orders of magnitude**, because `x` spans orders of magnitude and
  `s` is then paired with the wrong scale. Predeclared as `IQR(f)/median(f) > 3`.

## POSITIVE CONTROL — mandatory, not optional

A random consistent permutation `P C Pᵀ` will be applied and all three statistics recomputed.
**If the control does NOT collapse on all three, the check is not discriminating and the result is
VOID — not a pass.** Same rule as the amended mapping test: an exclusion or a statistic that cannot
fail proves nothing.

## ADJUDICATION, fixed in advance

| outcome | ruling |
|---|---|
| control collapses on all three AND real order passes all three | **ROW ORDER CONFIRMED** |
| control collapses AND real order fails any one | **REFUTED** — report raw, do not reinterpret |
| control does NOT collapse on all three | **VOID** — the statistic lacks power; needs a different instrument |

**Do not renegotiate these thresholds after seeing the numbers.** That is what writing them first is
for. D adjudicates; a disagreement goes to the mediator and is not resolved by either party alone.

## Scope

This tests **row order only**. It does not revisit the axis assignment (closed by the amended mask
test) or the volume weighting (closed by the 4D cross-check). A pass here would license `22.7%` for
**per-bin** use; without it, `22.7%` remains scoped to the aggregate order-of-magnitude materiality
question it was computed for, per D's ruling `9a84b6d`.
