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
| distance | **75.8 draw-sd** — gap `0.030253` ÷ arm-0 3-draw sd `0.000399` (`VL134`) |
| sign of `ratio − 1` | **FLIPPED** |

> **CORRECTION 2026-08-16, twice — and the second correction retracts the first.**
>
> **First pass (lane B, `BEN-342`).** This cell read `~105 draw-sd`. `0.981165 − 1.011418 = −0.030253`;
> over the **final-push** 3-draw sd `0.000399` (`VL134`) that is **`75.8`**, and over the standard error
> `0.000399/√3` it is **`131.3`**. `75.8` is the right figure, because the prediction being compared is
> a final-push quantity. **That part stands.**
>
> **Second pass (Assistant lane) — and my first correction was itself wrong.** I wrote that `105`
> *"derives from nothing"* and that the sd yielding it, `0.000288`, *"appears in no artifact."* **Both
> claims are false.** It is in the receipt, at `:23`:
>
> ```
> "sd": 0.0002888930898171582,
> "predicted_minus_this": 0.030252362049327908,
> "in_draw_sd_of_that_row": 104.7181920082435,
> ```
>
> **`104.7` is real, correctly computed, and correctly labelled by its own key — `in_draw_sd_of_that_row`.**
> The sd is the spread of the **substituted rows**, i.e. of the *consumed* push. So the figure was
> **MIS-NORMALISED, NOT FABRICATED**: divided by the sd of the very quantity that was the mistake.
> Those have different fixes, and *"derives from nothing"* invites a later reader to conclude the number
> was invented.
>
> **This is `BEN-360`'s own shape a third time, now with me as the reader.** The receipt disambiguated
> itself in a key sitting beside the number — exactly as `push_entering_this_iteration_left_by` did —
> and I dropped the qualifier `of_that_row`, quoted the bare `105`, and then, correcting it, asserted
> the operand did not exist **without grepping for it**.
>
> Found by lane B while checking the successor instrument; the retraction of my own correction by the
> Assistant lane; both re-derived independently here before acceptance.
> **It propagated to eight sites**, four of them in code and two in this finding and its sibling.
> `BEN-361`, stated one document over, is the rule *"re-derive a predeclaration's own amplitude
> estimate from the run's realized operands before repeating it"* — **and this document repeated an
> underived number while stating it.** The corrected value is now carried with its operands so the next
> reader can contradict it (`CONVENTION-receipt-ingredients.md`, `BEN-077`).

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
