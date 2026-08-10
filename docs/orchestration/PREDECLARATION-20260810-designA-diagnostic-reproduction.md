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
