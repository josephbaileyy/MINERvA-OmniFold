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

## THE COLLISION IS DORMANT ON THE NOMINAL PATH — which is why nobody found it

Asked directly whether this touches the **adopted** `R`, the answer is **no**, and it is worth recording
how that was established, because "three numbers and I don't know which is which" is exactly the state
this defect creates.

The three numbers in play:

| value | what it is |
|---|---|
| `1.1240802949941018` | **the adopted Gate-2 / Gate-4 nominal `R`**, reproduced to 17 digits |
| `1.1253110723074478` | **`replica_00`'s own `R`** — a different quantity, one replica's measured draw |
| `1.124623` | **only ever a deliberate wrong-operand derivation** for `replica_00`; published nowhere |

**Measured in the Gate-2 promoted receipt** (`G2_GATE2_TARGET_RUNTIME_RECEIPT.json`):

```
outer  sum_w_reco_pass_reco_raw              = 16780549.17866151
nested sum_w_reco_pass_reco_raw              = 16780549.17866151
nested sum_w_reco_pass_reco_replica_scaled   = 16780549.17866151
```

**All three are the same number, and all three re-derive `1.1240802949941018` exactly.** On the nominal
path there is no replica scaling, so `_raw` and `_replica_scaled` *are* the same quantity — no choice of
operand could have produced a wrong nominal `R`. `is_bootstrap_replica` is `False` there and
`bootstrap_seed` is absent.

So the field names were harmless for as long as nothing was scaled. **The replica path introduced a
scaled variant and activated a latent naming defect** — the collision did not exist when the names were
chosen, which is why no earlier review could have caught it.

### The reading was turned into a falsifiable prediction and tested

If the outer field is the replica-scaled sum and the nested `_raw` is genuinely unscaled, then the
nested `_raw` must be **constant across every replica and equal to the nominal's value**, while the outer
must vary. Measured over 20 replica receipts:

- nested `_raw`: **1 distinct value across 20**, `= 16780549.17866151`, **equal to the nominal exactly**
- outer: **20 distinct values across 20**, range `16771436.760178 … 16787860.591568`
- replica `R`: 20 distinct, `1.1229782491625557 … 1.1253110723074478`, with the nominal
  `1.1240802949941018` **strictly inside** and **equal to no replica's `R`**

The nested `_raw` is a property of the MC (`sum(w_reco[pass_reco])` before any replica scaling) and is
therefore identical across replicas and identical to the nominal — confirmed, not assumed.

## Status and scope

- **The adopted `R` is untouched.** `1.1240802949941018` re-derives identically from all three candidate
  fields in the nominal receipt, so Gate 4's reproduction does not depend on resolving the collision.
  **This is a re-derivation trap with no consequence for any quoted number.**
- **No scientific impact on the replicas either.** Each replica's `R` is correct: the producing code used
  the scaled sum, and `R = 1.1253110723074478` is reproduced exactly from the outer field for
  `replica_00`. The defect is in the *receipt's vocabulary* — a reproducibility defect, not a numerical
  one.
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
