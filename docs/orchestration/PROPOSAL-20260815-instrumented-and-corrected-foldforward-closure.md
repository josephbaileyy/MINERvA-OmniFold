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

**(a) INSTRUMENT — WRITTEN, TESTED, AND LANDED. Not a promise.**
`nd-unfolding/pet/closure_foldforward_instrumented.py` +
`nd-unfolding/tests/test_closure_foldforward_recording.py` (12 tests). It records
`sum_w_push_reco`, `sum_w_reco`, `n_pass_reco`, `step1_class_ratio` and `deviation_from_R`
**per iteration**, on the reco leg per D1, at the point `RunStep1(i)` consumes them.

> **IT IS A SEPARATE MODULE BECAUSE THE DRIVER IS PINNED, AND THAT WAS LEARNED THE HARD WAY.** The
> first version edited `closure_powered_truth_reweight.py` in place. That file hashes to
> `a45fae7c…6090fd48`, pinned by **four** launchers and bound by run receipts including the 47/47
> `NONQUOTABLE-DIAGNOSTIC.INDEPENDENT_VALIDATION.slurm-56562169.json`'s `hash:source-driver`. Two
> tests went red immediately — `test_hash_bindings::test_no_new_broken_hash_bindings` and
> `test_powered_closure_preflight::…code_pins_are_discoverable…` (*"pin is stale"*) — and repinning to
> clear them is prohibited while receipts bind it (`BEN-270`, `OI-123`). So the instrumentation follows
> the pattern the campaign already uses for exactly this problem: `closure_powered_annealed_lr.py`
> adds the LR anneal by rebinding `omnifold.MultiFold` to a subclass and delegating to `cpt.main`,
> touching neither engine nor driver. This composes **with** that one — MRO recorder → annealed →
> engine — and the records are merged into the report afterwards, the same post-hoc rewrite the
> annealed driver already performs on the same file. **The driver is byte-identical; verified.**
>
> **No new `BEN` row for this.** `BEN-270` already covers pinned-source freezing, the repo's own test
> caught it in seconds, and `CLAUDE.md` prefers the executable form of a rule over another written
> one. The constraint is therefore recorded where someone will trip over it: two tests
> (`PinnedDriverUntouchedTest`) that assert the driver still matches its pinned digest **and** that
> the instrumentation is not in it.

Change (a) alone closes `OI-125` and turns the executor lane's `1.011418` from a reconstruction into a
recorded value. **It changes no weight, model or metric** — it reads two arrays per iteration and
delegates — so arm 0 must reproduce the existing draws within their measured spread, which is the
control in §4. Guards power-tested by mutation, each caught by exactly one test: truth leg for reco leg
(2 tests), delegation dropped (1), and a hardcoded base instead of the class handed in (1) — the last
being the one that would have silently un-annealed the run.

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
4b. **THE CORRECTION IS SCALE-ONLY, AND THIS CLAUSE IS THE PREDECLARATION OF IT — not a note in a
   proposal.** Arm 1 rescales the pushed reco-leg weight by ONE per-iteration global factor to restore
   `sum(w_reco·push)/sum(w_reco) = R`. **A per-cell correction is REFUSED, and the reason is measured,
   not stylistic:** any per-cell field built from `push` is the unfolding's own per-cell output —
   `ratio[c]` agrees with `h_unfolded[c]/h_prior[c]` at Pearson `0.99973`/`0.99987` — so dividing one
   out is a **de-unfolding**, which returns recovery to `≈ 0` by construction (`BEN-310`;
   `α = -1` measured at `-0.000808`, landing 2.4% from `h_prior`). **A later reader will be tempted to
   "improve" this to per-cell.** Refuse it unless they can name a per-cell reference the record
   contains, which as of 2026-08-15 it does not — `R` is one scalar. A scale-only correction also keeps
   `Δrecovery` attributable: it cannot move a unit-normalized spectrum's shape at all, so any shape
   change observed in arm 1 is the estimator responding to a different training trajectory, which is
   the quantity of interest.
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
