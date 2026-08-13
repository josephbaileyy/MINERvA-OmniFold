# PREDECLARATION — Design A: does the DIAGNOSTIC arm (`56534117`) reproduce at all?

**Committed BEFORE submission.** Authorized by Joseph 2026-08-10 22:04:41Z (*"you can submit any compute jobs
you'd like"*) and 22:17:16Z (*"you can ask the overnight session for a decision and if you agree with it, go
ahead"*). The oversight session recommended Design A; I independently agree, and the agreement is the
condition he set. **Neither mail authorizes promotion of any arm, and none is taken.**

## The question, and why it comes before the bisect

The reproduction FINDING says the driver and diagnostic code paths disagree: `−0.035609` vs `−0.011724`,
a gap of `0.023885`. Every argument built on it — including the "188×" framing — assumes **`−0.011724` is a
property of that configuration rather than of that one job.** That has never been tested. `56534117` ran
**once**.

Stated plainly, because it is the weak link: the `0.000126775` scatter is measured on the **production**
configuration, **n=2**. The diagnostic configuration has **n=1**. "188× the scatter" therefore silently
assumes the two configurations scatter alike, on **zero measurements** of the second. Design A tests exactly
that assumption; the alternative design (isolating the subclass overrides) *assumes* it.

## What is held fixed, verified rather than asserted

    omnifold.py                     UNCHANGED between 8f2bcb0 and HEAD  (git diff --stat: no entry)
    fullevent_fps_dataloader.py     UNCHANGED between 8f2bcb0 and HEAD  (git diff --stat: no entry)
    diagnose_step1_annealed_lr.py   single commit 0144d21 @ 2026-08-09T11:03Z, BEFORE the 12:14Z run
    inputs                          G2_FPS_MEFHC_P12.npz sha fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625
    seed policy                     estimator_seed 42, subsample_seed 0, niter 3, epochs 8,
                                    train_events 2000000, batch_size 512  (identical in both artifacts)

So there is **no third delta**: the engine and loader are byte-identical across the two runs, and the harness
has not drifted since it ran. The run re-stages the driver at **`8f2bcb0`** — the version `56534117` actually
executed, which constructs a plain `MultiFold` and takes its anneal entirely from the harness monkeypatch.

## THE READING, fixed in advance — THREE outcomes, not two

    quantity   fold-forward deviation  dev = (sum_w_push_reco / sum_w_reco) / R - 1,  R = 1.1240802949941018
    tolerance  3 x 0.000126775 = 0.0003803

| outcome | window | reading |
|---|---|---|
| **REPRODUCED** | `[-0.0121046, -0.0113440]` | `−0.011724` is a property of the configuration. The delta is real, the code paths genuinely differ, and the subclass-isolation run becomes a clean one-variable follow-up. |
| **DISSOLVED** | `[-0.0359893, -0.0352286]` | `56534117` was never reproducible. The 188× framing collapses, and **the finding becomes the annealed-scatter generalisation itself** — i.e. that I extended a production-configuration scatter to a configuration where it was never measured. |
| **UNRESOLVED** | anything else | The diagnostic configuration has large run-to-run scatter and **neither conclusion follows.** Not "closer to X, therefore X". |

**The two windows are separated by 63× the tolerance**, so the UNRESOLVED region is wide and this is a real
third branch rather than a formality.

**On UNRESOLVED the next step is a SECOND REPEAT OF DESIGN A, not the subclass-isolation run.** At n=2 with a
mid-range value there is nothing to isolate yet, and proceeding would measure noise.

### The tolerance is BORROWED, and that is the assumption under test

`0.000126775` is the **production** configuration's scatter. I am using it as the diagnostic configuration's
tolerance because the diagnostic's own scatter is unmeasured — **which is precisely the thing this run
exists to test.** So the tolerance is provisional by construction and I am flagging it rather than letting it
read as measured. If the result lands UNRESOLVED, the borrowed tolerance is the first thing to discard, not
the finding.

*Raised by the oversight session, which pointed out that a two-outcome reading would have let a mid-range
value be rationalised toward whichever end it sat nearer. That is the correction that made this document
honest, and it came from outside this lane.*

## Explicitly forbidden by this predeclaration

Averaging arms; re-running until a value lands in a window; widening the tolerance after seeing the number;
reading UNRESOLVED as weak support for either side; and **any promotion, threshold change, extraction, cross
section, or `niter` change.** `niter` stays 3. Branch C stays closed. The 2026-08-08 baseline is not touched.

## Governance

- Staged **outside the repository** (`/pscratch/sd/j/josephrb/bisect_designA/`) so that re-staging an old
  driver cannot read as corpus drift to the GBDT lane's sweep guard, which is mid-PB3. That lane is told the
  path and that it is transient.
- The 2026-08-08 canonical baseline `58f664cdef266d09` is asserted unchanged before and after.
- `wakerctl` cron is live again (two ticks, `297 s` apart) but **zero watches are armed**; one is armed at
  submission, which also exercises the restored cron end to end for the first time.

## Provenance

- `−0.011724321` — job `56534117`, from **both** its in-loop `push_mean_w_reco` and the driver-format
  artifact `slurm-56534117/weights.npz` it wrote (the two agree exactly, which is what killed the
  measurement-point hypothesis)
- `−0.035608971` / `−0.035482196` — job `56563761` nominal and floor arms
- `0.000126775` — the `56563761` matched pair, production configuration, n=2
- `R = 1.1240802949941018` — `target.step1_class_ratio`, each artifact's own

---

## RESULT — three runs, and the answer is NOT the band's

**Band verdict, as predeclared and not adjusted: UNRESOLVED** (`56611394`, `dev = -0.052174875`, outside both
windows). Reported first and unmodified, because a tolerance changed after seeing the number is fitting
whatever the justification.

**The band was MIS-SPECIFIED, and this is a separate finding from the verdict.** Its tolerance was
`3 × 1.27e-4`, **borrowed from the production configuration** — §"Why ±0.010" said so at the time and flagged
it as provisional. `56611837` later showed that borrowing a scatter across configurations is wrong by ~10×,
and the diagnostic configuration's own sd is now measured at `0.0247`, so the band was **65× too narrow.**
Almost any result would have returned UNRESOLVED. **Do not read this UNRESOLVED as physics ambiguity — it is a
tolerance drawn from the wrong population**, the same defect as the `188×` framing and the `142 production
scatters` claim, this time sitting inside a predeclaration rather than a report. *Raised by the oversight
session before the number was read, which is the only time it could be raised honestly.*

**THE MEASUREMENT, which answers the question the band could not:**

    56534117  -0.011724321   in-loop [1.0107, 1.1214, 1.1109]
    56586368  -0.007386682   in-loop [1.4555, 1.2322, 1.1158]
    56611394  -0.052174875   in-loop [1.0240, 1.0820, 1.0654]
    mean -0.023761959   sd 0.024701703   range 0.044788193   |   sd/prod = 195x, range/prod = 353x (labels corrected 2026-08-11)

**The question this document asked — is `-0.011724` a property of the configuration? — is answered NO,
definitively.** The configuration has no stable point value. Three runs of byte-identical code at identical
seeds span `0.0448` in deviation with qualitatively different trajectories.

**And it REFUTES the finding this whole line of work was chasing.** The production value `-0.035546` sits
**inside** the diagnostic range, `0.48` diagnostic sd from its mean. The code-path gap by denominator:
`188×` (production scatter, wrong population) → `6.0×` (two-point difference) → **`0.97×` (gap ÷ the
three-point sd `0.024701703`)**. **LABEL CORRECTED 2026-08-13:** this line previously ended `0.48× (three-point
sd)`, which attached the *distance-from-mean* value to the *gap-over-sd* derivation — `0.023884971 / 0.024701703
= 0.96694`, not `0.48`. Both quantities are real and both are under one sd; only the stated relationship was
wrong. Line 115 above had it right (`0.48` sd **from its mean**), so this file was internally inconsistent.
**The two figures that need no n=3 sd at all are the better ones to quote: the `2.239×` range-to-window ratio
and the `1 of 3` realized containment.** Found by Session D in the retraction index, fixed there by Session C,
traced to this line — the origin — by Session A.
There is no established code-path difference. Retracted in `KNOWN_ISSUES.md`.

**No fourth run.** The predeclared next step on UNRESOLVED was *a second repeat of Design A*, which this was;
n=3 now gives a spread, and the spread answers the question definitively rather than ambiguously. A fourth run
would refine `sd 0.0247` without changing any decision.

**In-run assertions held:** 8 pins, `resolved sha256 66aa1f8f…` (the staged 08-09 driver, not HEAD's),
baseline `58f664cdef266d09` unchanged before and after.
