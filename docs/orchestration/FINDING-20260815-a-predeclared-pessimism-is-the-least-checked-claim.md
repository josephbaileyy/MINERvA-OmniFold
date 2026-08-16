# FINDING 2026-08-15 — a predeclared *pessimism* is the least-checked claim in a predeclaration

**`BEN-361`.** Authored by the fold-forward closure lane; landed by the mediator after that lane's
account hit a session limit mid-commit. Receipt:
`state/RECEIPT-foldforward-instrumented-closure-20260815.json`.

## One error, two opposite-signed reading failures

`BEN-360` records that the fold-forward instrument recorded the **consumed** push rather than the
**end-of-run** one. That single conflation produced **two** wrong readings with opposite signs:

1. **§2 looked REFUTED** — a ~105-draw-sd disagreement with the sign flipped. Loud, and therefore
   certain to be investigated.
2. **§6 looked CONSERVATIVE** — quiet, plausible, and **the one that would have been believed.**

## What §6 declared in advance

> arm 1's correction is *"a rescale of order 1%"*, because *"this closure's fold-forward ratio is
> ≈ `1.011418`"* — therefore arm 1 is likely **underpowered by construction**, and *"the honest report
> is a BOUND, not a null."*

**That premise sizes the perturbation off the END-OF-RUN ratio. The correction is applied to the
CONSUMED one** — `R/ratio` at the ratio entering each iteration
(`closure_foldforward_instrumented.py:141-167`).

## Measured from the receipts' own operands

| quantity | value |
|---|---|
| `applied_correction_factor`, iteration 1 | **`1.046109`** — a **4.61%** rescale |
| declared amplitude | "of order 1%" |
| ratio | **`4.04×` the declared amplitude** |
| realized `\|Δrecovery\|` | **`0.006888`** |
| vs pooled within-arm sd (`0.000424`) | **`16.2×`** |
| arm ranges | **disjoint** |
| realized pairwise exceedance | **9 of 9** (`BEN-025`: realized, not a fitted tail) |

**So arm 1 is NOT underpowered, and the honest report is a measured effect — not a bound and not a
null.**

## Why this needs an id separately from `BEN-360`

**A predeclared limitation is the one thing a later reader will not re-derive.**

- It is **written to be trusted** — its entire value is its timestamp.
- *"§6 said this would be underpowered"* is exactly the sentence that **survives a relay while its
  arithmetic does not.**
- A pre-committed **pessimism** is as falsifiable as a pre-committed prediction, and **gets checked far
  less often** — because **a result that beats its declared limitation looks like good news rather than
  like a discrepancy.**

A refuted prediction triggers an investigation. A surpassed limitation triggers nothing at all. **The
failure mode is silence, which is why it needs its own id rather than living as a clause inside
`BEN-360`.**

## THE RULE

> **Re-derive a predeclaration's own amplitude estimate from the run's realized operands before
> repeating it — including, especially, when the run cleared it.**

Related: `BEN-360`, `BEN-025`, `BEN-244`, `OI-125`.
