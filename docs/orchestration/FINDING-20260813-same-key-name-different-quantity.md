# FINDING 2026-08-13 — the same key name at two nesting levels, holding different numbers

**BEN-150.** Lane C (PET), found while re-deriving `R` from its published operands during the first
Gate-5 family reconciliation.

**One-line version:** `sum_w_reco_pass_reco_raw` exists at two nesting levels of the same telemetry
block with **different values**, and the outer one labelled `_raw` actually carries the
replica-**scaled** number. Re-deriving `R` from the wrong one gives a 6.1e-4 relative error — too small
to look like a bug, too large to be rounding.

## The measurement

From `replica_00`'s `GATE5_REPLICA_TARGET_RECEIPT.json`, inside
`runtime_target.step1_class_ratio_telemetry`:

```
step1_class_ratio_telemetry.sum_w_reco_pass_reco_raw                        = 16771436.760178246
step1_class_ratio_telemetry.b4_w_reco_vs_w_truth.sum_w_reco_pass_reco_raw   = 16780549.17866151
step1_class_ratio_telemetry.b4_w_reco_vs_w_truth.sum_w_reco_pass_reco_replica_scaled
                                                                           = 16771436.760178246
```

So the **outer** `..._raw` is byte-identical to the nested block's `..._replica_scaled`, and the nested
`..._raw` is the genuinely unscaled sum. The name `_raw` means one thing at one level and the opposite
one level down.

The receipt publishes the formula next to them:

```
"formula": "R = (n_data - pot_scale*sum(w_bkg)) / (pot_scale*sum(w_reco[pass_reco]))"
```

Reconciler output, after multiplying each candidate by `pot_scale = 0.21240500334472884`:

| key | denominator | reproduces `R`? |
|---|---|---|
| outer `sum_w_reco_pass_reco_raw` | 3562337.0811415683 | **yes** |
| nested `sum_w_reco_pass_reco_replica_scaled` | 3562337.0811415683 | yes |
| nested `sum_w_reco_pass_reco_raw` | 3564272.604419985 | **no** |

`R` recorded: `1.1253110723074478`. Re-derived from the nested `_raw`: `1.124623`.

**Relative error 6.1e-4.** That is the dangerous magnitude. It is far too large to be float
round-tripping through JSON (`~1e-16`), and far too small to look like using the wrong quantity — it
reads as "some precision or normalisation detail I don't need to chase," which is exactly the reading
that lets it through.

## Why this shape is worse than an outright wrong number

A field holding an obviously wrong value gets caught the first time someone looks. This one:

- has the **right name** for the job you are doing;
- sits in the **same block** as the formula that consumes it;
- is **nested inside** a block whose subject (`b4_w_reco_vs_w_truth`) is precisely the reco-vs-truth
  leg question you are consulting the telemetry about;
- and produces an answer that **agrees with the published `R` to three decimal places.**

Anyone re-deriving `R` by hand from that receipt has a better-than-even chance of reaching for the
nested `_raw` — it is the one whose name matches the formula's `sum(w_reco[pass_reco])` most literally,
inside the block about `w_reco`.

## How it was caught

Not by suspicion. By the mechanical application of `CONVENTION-receipt-ingredients.md` /
`BEN-077`: **every derived quantity ships its ingredients, so the reported numbers can contradict each
other.** The reconciler re-derives `R` from the published operands and, because the collision existed,
was written to try *all three* candidates and report which reproduced `R` rather than assuming one.

**This is now the second defect that heuristic has caught with nobody suspecting one.** The first was
the first-leg-vs-end-to-end metric mismatch that `BEN-077` records — found purely by failing to derive a
published ratio from published operands. That is a strong track record for a rule that costs one
division, and it argues for applying it by default rather than when something feels wrong.

## The rule

> **Two fields may share a name only if they hold the same quantity.** If a nested block needs a
> variant, the *variant* gets the qualifier, and the qualifier must describe what is actually in it —
> `_raw` must not hold a scaled value at any nesting level.

Corollary for readers, and the reason the reconciler prints the candidate set: when re-deriving a
published quantity, **try every plausible operand and report which one worked**, rather than picking the
best-named and stopping. The check costs nothing extra and it converts a silent mis-pick into a
recorded fact.

## Status and scope

- **No scientific impact.** `R` itself is correct: the producing code used the scaled sum, and
  `R = 1.1253110723074478` is reproduced exactly from the outer field. The defect is in the *receipt's
  vocabulary*, which is a reproducibility defect, not a numerical one.
- Verified across all 16 reconciled replicas: the outer field reproduces `R` in 16/16, the nested
  `_raw` in 0/16.
- **Not repaired in the producing code**, which is under a live campaign's hash pins. The fix is a
  rename in the target builder's telemetry assembly and belongs to the next launch, alongside the
  `:112` repair (`OI-57`/`OI-58`) and the loader-side data-factor persistence (`BEN-151`).
- Guarded going forward by `nd-unfolding/tests/test_reconcile_gate5_family.py`, whose fixture
  **reproduces the collision on purpose** and asserts the nested `_raw` does *not* reproduce `R` — so a
  future receipt that quietly fixes or worsens the naming will show up as a test change rather than
  silently.

## Related

- `BEN-077` / `CONVENTION-receipt-ingredients.md` — the heuristic that found this.
- `BEN-149`, `BEN-151` — same campaign, same family: a *name* that answers a question the reader would
  otherwise have asked.
- [`state/gate5-family-reconciliation-20260813.json`](state/gate5-family-reconciliation-20260813.json)
  — the reconciliation receipt carrying the measured candidate set.
