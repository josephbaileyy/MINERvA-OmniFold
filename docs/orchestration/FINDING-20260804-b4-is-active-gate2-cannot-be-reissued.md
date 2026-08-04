# FINDING 2026-08-04 — B-4 is **ACTIVE**. The first real post-restore Gate-2 run answered it, and Gate-2 cannot be re-issued until it is resolved.

*Measured on Perlmutter 2026-08-04, job 56320955, 56 minutes on `nid004156`. This is the answer the
code was written to extract, not a failure of the run. **Nothing was published; the 2026-07-19
products are byte-identical to how they were found.***

## The result

```
RuntimeError: B-4 is ACTIVE: w_reco differs from w_truth on 20573521 pass_reco rows,
so the reco leg is fed the wrong weight and R would move by a factor 1.01887079577071
```

* **All 20,573,521 `pass_reco` rows differ** — every single one, not a subset. So `w_reco` and
  `w_truth` are systematically different quantities over the whole reco leg, not a handful of edge
  cases. (20,573,521 is independently the `pass_reco` count measured for Step 7b, which
  corroborates the row accounting.)
* `reco_leg_weight_used` is `"w_truth"` (`fullevent_fps_dataloader.py:955`) — the reco leg is
  currently fed the truth weight.
* `R_shift_factor_if_B4_fixed = 1.01887079577071`. R appears with `sum_w_mc_reco_raw` in its
  denominator, and the `w_reco` sum is smaller by that factor, so **R moves by ≈ +1.9%** if the
  reco leg is switched to `w_reco`.
* The step-1 target is `1e6 · R`, so a 1.9% move in R is a 1.9% move in the publication nominal's
  step-1 normalization.

## This was designed to happen on exactly this run

`fullevent_fps_dataloader.py:832-846` says so in terms:

> `THE w_truth-vs-w_reco ASSUMPTION -- audit finding B-4, UNRESOLVED as of 2026-07-29.` … `That is
> why R is DERIVED here and never frozen as a constant: when B-4 is answered, this one` … `the
> w_reco-vs-w_truth comparison at runtime, so the first 08-03 run answers B-4 as a side effect.`

And `2026-07-31` converted B-4 from a note into a hard gate — `gate2_target_runtime.py` around the
B-4 block records why:

> B-4 is GATED here, not merely recorded. … Emitting that into `step1_class_ratio.b4_note` while
> the receipt says status PASS made the gate contradict its own telemetry, because every consumer
> reads `status`, not a note.

So the restore's first Gate-2 run did precisely its job. The gate that previously passed while
recording "resolve B-4 before freezing R" in a note now stops.

## What this says about the published 2026-07-19 PASS

The published receipt `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` carries `status: PASS` and verdict
`GATE2_CANONICAL_RUNTIME_PASS_INDEPENDENT_PROMOTION_PENDING`. It was produced **before** B-4 was
gated, so its PASS was obtained under a validator that only wrote B-4 into a note whose own text
said not to freeze R yet. That PASS therefore does not certify the current definition of the gate.

This compounds with the units defect resolved the same day
([FINDING-20260804-gate2-units-resolved-gev](FINDING-20260804-gate2-units-resolved-gev.md)): the
same receipt's "independent binned check" was also vacuous. Two independent reasons the 07-19 PASS
should not be leaned on.

## The units patch is separately confirmed CORRECT by this run

Worth stating because it is easy to lose in the failure: the run got **past** the units fix, the
domain guard, the step-1 sum check, the signed-sum-vs-telemetry check and the R-numerator
corroboration, and died only at B-4.

That is positive evidence, not merely absence of complaint. With `/1000.0` removed, if the dump
were MeV the values would sit at ~1e4–1e5, far outside `[0,30] × [0,120]`, and the domain guard at
`:515` would have died loudly on the very next statement. It did not. **The dump is GeV and
removing the divide is right**, now established against the real input by the gate's own guard
rather than by inspecting maxima.

What the run did *not* reach: the receipt write, so the occupied-bin count (expected 231/285 vs the
old degenerate 1/285) and the weights-vs-published comparison are still unmeasured.

## Why I stopped here

Resolving B-4 means deciding whether the reco leg should be fed `w_reco` instead of `w_truth`. The
comment at `gate2_target_runtime.py` notes the formula is shared with `fed.step1_class_ratio` so
"a B-4 flip is a one-body change" — the *edit* is small. The *decision* is a physics judgment that
moves the publication nominal's step-1 normalization by 1.9%, and it is explicitly the thing the
gate exists to force a human to answer. I did not flip it.

## Consequences for the restore chain

Gate-2 is now blocked by B-4, and Step 3 is independently blocked by an environment conflict
([FINDING-20260804-step3-closure-needs-root-and-tf-in-one-interpreter](FINDING-20260804-step3-closure-needs-root-and-tf-in-one-interpreter.md)):

```
B-4 unresolved      ->  Gate-2 re-issue blocked
Step 3 env conflict ->  Step 2b blocked  ->  Step 4 precondition unreachable
```

Step 4's unattended-launch authorisation was conditional on every gate passing. Two independent
walls mean that condition is not met, so **not launching is the correct execution of that
authorisation.**

## State of the published artifacts — unchanged

Verified before and after the run:

| artifact | sha256 | bytes |
|---|---|---|
| `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` | `1ef7e0d2fa8c36a6f9eabd86a21f0b41617cc7d0bb4cd6bee96d74d5334074b6` | 18,723,004 |
| `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` | `f09db8fc4b2aa177d188f456bd53fccc0e965f1ea319e0764c355051e92f8c44` | — |

No pin was edited, no product was retired, and the five pre-existing hash mismatches are still
exactly five. `test_no_new_broken_hash_bindings` remains red, which is still correct behaviour.

## Cost

56 minutes on one shared CPU node (~15 CPU-hours). Note the refiner ran roughly 5× slower than the
07-19 run's 671 s — single-threaded at ~95% of one core, RSS 3.8 GB against that run's 11.1 GB
peak. Worth setting thread counts explicitly before the next attempt rather than inheriting them.
