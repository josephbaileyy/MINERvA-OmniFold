# FINDING 2026-08-15 — an instrument built to close a "not recorded" hole recorded the *neighbouring* quantity

**`BEN-360`.** Authored by the fold-forward closure lane; landed by the mediator after that lane's
account hit a session limit mid-commit. Receipt:
`state/RECEIPT-foldforward-instrumented-closure-20260815.json`.

## What `OI-125` asked for

`OI-125` records that the closure writes **no fold-forward scalar**, so `dev = |ratio/R − 1|` is not
formable for `VL100`'s run. An instrument was built to close exactly that hole.

## What the instrument recorded instead

`closure_foldforward_instrumented.py:115` hooks **`RunStep1`** and records the push at the point of
**consumption**. `:243-246` asserts `len(records) == niter`. At `niter=3` the series is therefore
**complete, self-consistent, and internally correct** — and it captures the push after **0, 1 and 2**
`RunStep2` passes.

**The push that `RunStep2(2)` leaves is consumed by no `RunStep1`, and so is recorded by no row.**

**That is the one `OI-125` is about.** `train_fullevent_nominal.py:576-577` computes the nominal's
recorded fold-forward from `push` **after `Unfold()`** — so the nominal's `0.736746`, the 34% deficit
the whole `OI-71` / `OI-125` argument rests on, is the **end-of-run** scalar. The like-for-like closure
number is the one no row holds.

## The cost: the receipts appear to refute their own predeclaration

Predeclaration §2 predicted `≈ 1.011418`, and pre-committed that *"disagreement is itself a result and
outranks everything else in the run."*

The last recorded row is `≈ 0.9812`. A reader keying off *"the final iteration"* therefore gets:

| | |
|---|---|
| predicted | `+1.1%` (`ratio − 1`) |
| last recorded row | `−1.9%` |
| distance | **~105 draw-sd** |
| sign of `ratio − 1` | **FLIPPED** |

**That is the loudest possible disagreement, on a predeclaration that pre-committed to disagreement
outranking everything else — and it is false.**

Recovered from `weights_push` + `dump_rows_b` under the recorder's own reduction, arm 0 gives
**`1.010879 ± 0.000399`** (3 draws), and **§2 AGREES** at `1.17` prediction-sd.

## Nothing was hidden

The receipt disambiguates itself in a key sitting **beside** the numbers:

```
/fold_forward_per_iteration/0/push_entering_this_iteration_left_by :: 'initialization (all ones)'
/fold_forward_per_iteration/1/push_entering_this_iteration_left_by :: 'RunStep2(0)'
/fold_forward_per_iteration/2/push_entering_this_iteration_left_by :: 'RunStep2(1)'
```

plus a `fold_forward_note` stating the rule in prose. **The field that disambiguates it is one a reader
has to already suspect they need.** That is the recurring shape, not the exception — this is the third
instance in two days of a qualifying fact computed, persisted, and unread beside the numbers three
documents quote (`gate_is_cross_tier`, the `bkg_mode` skip claim, this).

## THE TRANSFERABLE SHAPE

> **When you add an instrument to close "X is not recorded", write down the definition of X from the
> artifact that already records it, and check your instrument's output against THAT definition — not
> against your own reduction, which is guaranteed to agree with itself.**

Same family as `BEN-312` (*the verifier must name every object the run's behaviour depends on*), one
axis over: **here the object was named and the reduction was not.**

## Disposition

**`OI-125` is NARROWED, NOT CLOSED.** Its own instruction holds: do not close it by citing `1.011418`
**or** the recovered `1.010879`. **Both are reconstructions, not recorded values.**

Related: `BEN-312`, `BEN-310`, `BEN-227`, `BEN-361`, `OI-125`, `OI-71`.
