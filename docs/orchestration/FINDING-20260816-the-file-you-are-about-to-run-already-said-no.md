# The file you are about to run already said no

**Date:** 2026-08-16 · **Lane:** OI-124 disposition lane (peer session `C`, block `330-339`)
**Row:** `BEN-334` · **Subject:** a confirm/deny on ~6–12 GPU-h that resolved inside the artifact itself

---

## What happened

The orchestrating session asked for an independent confirm/deny on running
`nd-unfolding/pet/sbatch_foldforward_instrumented_closure.sh` as modified by `67c94df`, to close
`OI-125` by producing a genuinely *recorded* end-of-run fold-forward scalar.

**That same commit's launcher carries the denial of that same run**, written the same day:

> *"NO RUN IS ATTACHED TO THIS MOVE. The 3-draw re-run was proposed and DENIED on 2026-08-16: the
> driver takes no seed flag, so a new run is a NEW SAMPLE and its recorded scalar could not validate
> VL134 — it would sit in the ledger beside it as a non-comparable number. **This lands so the next
> run that happens FOR ITS OWN REASONS carries the value for free.**"*

The instrumentation was **deliberately designed not to justify its own run.** It was re-proposed one
day later by the session that had recorded the denial, without the file being run having been read.

> **Before approving a run, read the launcher. Not the proposal for the run — the file that will
> execute.** A launcher in this repo carries its own predeclaration, its own expected exit codes, its
> own arm layout and, here, its own standing decision. None of that is in the request to run it.

## Why this is not merely "somebody forgot"

It is the same shape as `BEN-333` member 6 — **evidence assembled from memory of one's own recent
work** — but one turn worse. There the near-miss was *remembered* and mis-classified; here a written
decision was **not consulted at all**, in a file the proposal names. The remedy that failed is
`BEN-333`'s own: *before offering your own recent work, go and read what you actually did.* That rule
was filed 12 hours earlier by this lane, cited by the session that broke it, and it did not fire —
because the decision lived in a **launcher comment**, which nobody classifies as a record.

**A decision recorded only in the artifact it governs is invisible to everyone who has not opened
that artifact.** It is perfectly placed for the person executing and perfectly hidden from the person
approving, and those are different people here by design.

## The correct conclusion resting on a false mechanism — the more dangerous half

The denial's stated ground was *"the driver takes no seed flag, so a re-run produces new draws."*
**The premise is false.** `closure_powered_truth_reweight.py` calls
`tf.keras.utils.set_random_seed(int(pol["estimator_seed"]))` against a **frozen** seed policy; only
`--split-seed` is a CLI flag. The training seed is *pinned*, and the absence of a flag is not the
mechanism.

**The conclusion survives anyway, for a different reason**, and the launcher states it: the three
draws per arm are *"the SAME configuration … so the spread is training nondeterminism"*, measured at
**sd `0.000820128`** across `56552326` / `56611837` / `56626305`. Same configuration, new realization.

**What that would have cost.** Asked *"does closing this need a seed flag that does not exist?"*, the
false premise answers **yes** — and a lane would have been dispatched to build one. **A seed flag
would not have fixed comparability, because the seed is already pinned.** The missing property is
**deterministic execution**, which is a different and much larger piece of work. *A conclusion that
survives the refutation of its premise is the one most likely to send the next lane at the wrong
target*, because nothing downstream contradicts it: the verdict was right, so no one re-audits the
reason.

> **When a premise is refuted but the conclusion holds, re-derive every OTHER decision that rested on
> that premise.** Correctness of the headline is not evidence for the reasoning under it.

## The cost figure was right by accident

Quoted as *"~6 GPU-h (the prior `ff_closure` array ran 3 × ~1h57m)"*. The array is **six** tasks —
`0-2 = ARM 0`, `3-5 = ARM 1`. Measured from `sacct -j 57012031`:

```
_0 COMPLETED 01:56:11      _3 FAILED 00:02:05
_1 COMPLETED 01:56:02      _4 FAILED 00:01:57
_2 COMPLETED 01:57:06      _5 FAILED 00:02:07
```

**~6 GPU-h was correct only because arm 1 died at two minutes**, on a dtype defect since repaired
(`4e85f0e`, `BEN-314`). A working six-task array is **~12 GPU-h**. The estimate was a measurement of
a *failure*, read as a measurement of the *work* — and it would have been quoted upward as the cost
of a healthy run.

> **An elapsed time from a run that failed is not a cost estimate for a run that works.** Check the
> exit state of every task whose duration you are extrapolating from.

## The resolution cost nothing

`AUTHORIZATION-20260815-arm1-resubmit.md` already grants *"one resubmission of arm 1, 3 draws,
5.9 GPU-h. Nothing else."* **That is "the next run that happens for its own reasons."** The recorder
rides it at zero marginal cost, exactly as the launcher intended.

**But it must not be reported as closing `OI-125`.** Arm 1 is the **corrected** arm; `OI-125` is about
the **uncorrected** closure's end-of-run scalar being comparable to the nominal's recorded
`0.736746`. Recording arm 1 there is `BEN-360` repeating one level up — *the instrument records the
neighbour* — with the aggravation that the second instrument was built specifically to close the hole
the first one missed. `OI-125` closes only when an **arm-0** run happens for independent reasons.

**Found while checking that:** `AUTHORIZATION-20260815-arm1-resubmit.md` asserted arm 0 *"closes
`OI-125`"*, which the narrowing had already refuted. Corrected by its author at `a5d71af`, struck
inline rather than deleted because the document is cited elsewhere.

## What this lane got wrong, recorded because the row is about premises

Mid-investigation I concluded the orchestrator's premise was simply wrong and was briefly ready to
report *"a re-run reproduces the same draw, so the number IS comparable."* That would have inverted
the verdict and approved the run. It was the **launcher's own `:23-24`** plus the measured `sd
0.000820128` that refuted it — i.e. the same file that carried the denial also caught the error made
while adjudicating the denial. **Two of the three parties reasoned about this run without reading
that file; both were wrong in opposite directions.**

## Scope

* One proposal, one launcher. No claim about how often decisions are stranded in launcher comments —
  the transferable part is *read the file that will execute*, not a rate.
* The `sd 0.000820128` and the `sacct` durations are quoted **as recorded** in the launcher and by
  `sacct` respectively; this lane re-derived the durations over its own `ssh` and reproduced them, and
  did not re-derive the sd from the three artifacts.
* Nothing here evaluates whether the new recorder records the **right quantity** — that check was
  held by a different lane under `BEN-360`'s rule and is independent of this one.
