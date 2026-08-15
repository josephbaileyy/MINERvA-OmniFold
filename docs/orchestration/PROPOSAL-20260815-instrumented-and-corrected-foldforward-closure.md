# PROPOSAL — an instrumented, fold-forward-corrected powered closure

**NOT AN AUTHORIZATION. NOTHING HAS BEEN SUBMITTED.** Written by the executor lane 2026-08-15 at the
mediator's request, so that the decision in front of Joseph is a concrete instrument with a price rather
than *"someone should rerun it."*

The promotion receipt's own scope clause settles who decides:
`p3f-pet-gate4-nominal-promotion-56563761.json` →
`scope_PROMOTED_IS_NOT_PROCEED.NOT_authorized` lists **`"any recovery run"`**, and
`next_step_requires: "A FRESH authorization from Joseph. 'Promoted' is not 'proceed'."`

## 1. What question this is the only instrument for

`OI-71` is now down to **one** ground. Three of the four are determined read-only
(`FINDING-20260815-the-quarantine-measured-a-different-run.md` §3); the survivor is **G4 — recovery has
never been evaluated at the promoted configuration** (`explicitly_not_claimed[2]`,
`recovery_evaluated: False`).

G4 cannot be closed by reading, at any effort, for a structural reason: **recovery is defined against an
injected truth reweight.** The closure tilts half A and measures how much of the induced gap the
estimator recovers. The promoted nominal has no tilt and no A/B split, so its weights contain no
recovery to extract.

The same run answers the question the 2026-08-15 recomputation could **not**:

> Every correction computable from disk is **post-hoc and multiplicative on `h_unfolded`**. The
> fold-forward acts in **iterations 2 and 3 of 3**, so a defect that mis-delivered weight *during*
> training is baked into `push` itself and no reweighting of `h_unfolded` can probe it.

And it supplies what `OI-125` says is simply absent: **this closure has no fold-forward number of its
own**, because `git grep 'fold_forward'` over both closure drivers returns zero hits.

**One run, three items.** That is the argument for spending the GPU time.

## 2. The two code changes, both small and both additive

**(a) INSTRUMENT — required, ~8 lines, no behaviour change.** Port
`train_fullevent_nominal.py:576-577` into `closure_powered_truth_reweight.py`: record
`fold_forward_sum_w_push_reco`, `fold_forward_sum_w_reco`, `fold_forward_n_pass_reco` and
`step1_class_ratio` **per iteration**, on the reco leg (`mc.weight_reco`, D1's rule — a step-1-space
ratio must be built from the leg step 1 consumes). Per-iteration, not once, because the fold-forward
acts in iterations 2 and 3 and a single end-of-run scalar cannot say which iteration drifted.

This alone closes `OI-125` and makes the executor lane's `1.011418` a *recorded* value instead of a
reconstruction. **It changes no weight and no metric**, so arm 0 must reproduce the existing draws
within their measured spread — which is the proposal's own control (§4).

**(b) CORRECT — the arm under test.** Normalize the pushed reco-leg weight so the fold-forward conserves
the step-1 class ratio per iteration, then re-run. **The correction must be predeclared before the run**
and its form is the one open design question here; the defensible default is the minimal one — a single
per-iteration global rescale of the pushed reco-leg weight to restore
`sum(w_reco·push)/sum(w_reco) = R`, which is **scale-only and therefore cannot be confused with a shape
correction.** Any per-cell variant reopens exactly the `BEN-310` trap (a per-cell field built from
`push` is the unfolding's own output) and should be refused unless someone can name a per-cell reference
the record does not currently contain.

**Neither change touches `omnifold.py`.** The engine is hash-pinned (`3a2022b0…`) by the Gate-2 receipt
and by active run receipts.

## 3. Cost — measured, not estimated

From `sacct -X` this session (read-only) on the three existing powered-closure draws:

| job | state | elapsed | allocation |
|---|---|---:|---|
| `56552326` | FAILED `3:0` (post-training launcher artifact) | `01:56:32` | 1× A100, 32 CPU, 57472M, 1 node |
| `56611837` | COMPLETED | `01:57:54` | same |
| `56626305` | COMPLETED | `01:57:26` | same |
| `56562169` (CPU finalizer) | COMPLETED | `00:00:41` | 36 CPU, 64G, `shared` |

**Unit cost: 1.96 GPU-hours per closure draw** (mean `01:57:17`, spread 82 s across three draws — this
is a very predictable job). The finalizer is free at 41 s on the shared queue. For reference the
promoted nominal training `56563761` took `06:00:36`; **the closure is a third of that**, so this is not
a nominal-scale ask.

| option | arms × draws | GPU-hours | what it buys |
|---|---|---:|---|
| **minimum** | 2 × 1 | **≈ 3.9** | the sign and rough size of the training-time effect; closes `OI-125` |
| **recommended** | 2 × 3 | **≈ 11.7** | the same, resolved against the known draw-to-draw spread `sd 0.000820128` |
| instrument only | 1 × 1 | ≈ 2.0 | closes `OI-125` only; does **not** touch G4 or the training-time question |

**Recommended is 2 × 3 and the reason is arithmetic, not caution.** The effect being measured must be
compared against the margin `0.01802087615174025`. The existing three-draw spread is `sd 0.000820128`,
so a single pair of draws resolves a shift only if it exceeds roughly `0.0023` (2σ on a difference of
two single draws); three draws per arm tightens that to about `0.0013`. **A one-draw-per-arm result that
came back "no change" would be indistinguishable from a change of 12% of the margin** — which is
precisely the ambiguity that would leave `OI-71` open after spending the GPU time. `BEN-025` is the
standing warning against letting a small-sample spread settle a decision of this shape.

## 4. Predeclaration — written before the run, per this campaign's convention

To be committed as a `PREDECLARATION-*` before any submission, following
`PREDECLARATION-20260810-annealed-shape-validation.md`:

1. **Control, and it is the one that makes the rest readable.** Arm 0 (instrumented, uncorrected) must
   reproduce the existing draws: recovery within the measured 3-draw band, and the four spectra
   bit-comparable at the finalizer's `1e-9`. **If arm 0 does not reproduce, stop** — the instrumentation
   changed behaviour and nothing downstream means anything.
2. **The recorded fold-forward of arm 0** is predicted to be ≈ `1.011418` (the executor lane's
   reconstruction). Agreement converts that number from reconstruction to record. **Disagreement is
   itself a result and outranks the rest of the run** — it would mean the reconstruction or the
   alignment argument is wrong.
3. **The measured quantity is `Δrecovery = recovery(arm 1) − recovery(arm 0)`**, per draw and pooled,
   reported **with** its spread and against the margin `0.01802087615174025`. Report realized
   exceedance, not a fitted gaussian tail (`BEN-025`).
4. **No threshold moves.** The adopted criterion stays `0.80 × 0.618228 = 0.49458240000000003`. A
   result that fails the criterion is a result, not a reason to revisit the bar.
5. **Both arms are `NONQUOTABLE-DIAGNOSTIC.`** until Joseph says otherwise — and, per
   `FINDING-20260815-the-quarantine-measured-a-different-run.md`, the manifest for these runs must
   name **its own** `weights_path`. The existing manifest's points at the pre-anneal nominal, which is
   how the whole confusion started.
6. **Declare the failure modes that would make the run uninformative** before it runs: arm 0 not
   reproducing (1); `|Δrecovery|` smaller than the pooled spread (underpowered — say so rather than
   reporting a sign); and the correction in (b) altering the *shape* of the pushed weight, which would
   make `Δrecovery` unattributable and is why (b) is specified scale-only.

## 5. What this proposal does not do

- **It does not resolve the nominal extraction's ~34% deficit in magnitude.** That deficit lives in the
  nominal run, and this closure — whose own ratio is ≈ 1 — does not exercise it. **Which is exactly the
  problem `FINDING-20260815-…-restatement…` §1 raises**, and it is a separate instrument: a corrected
  *nominal* run, not a corrected closure. Do not let this proposal be read as covering it.
- **It does not make `VL100` quotable.** G1–G3 are determined; G4 is what this addresses. Quotability is
  a determination for the PET lane and Joseph, and no run produces it.
- **It does not authorize itself.** Submission needs Joseph, in writing, per the promotion receipt's own
  clause quoted at the top.

## 6. Recommendation

**Run the recommended option — 2 arms × 3 draws, ≈ 11.7 GPU-hours on one A100** — with the
instrumentation and the predeclaration landed first, and arm 0 treated as a gate on reading arm 1.

If GPU time is the binding constraint, **land change (a) alone and run `1 × 1` (≈ 2.0 GPU-hours)**:
that closes `OI-125`, converts `1.011418` from reconstruction to record, and leaves G4 open honestly
rather than answering it underpowered.
