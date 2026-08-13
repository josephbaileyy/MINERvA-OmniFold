# FINDING 2026-08-13 — a wall time is only a unit cost if you checked how many units ran inside it

**BEN-152.** Lane C (PET). Predecessor-found; **independently confirmed here by a different method**, at
ratio 2.05.

**One-line version:** the Gate-5 predeclaration's compute budget is built from a `sacct` wall time for a
job that ran **two** trainings, quoted as the cost of **one** — so the GPU budget and the family
wall-clock estimate are both ~2× high.

## The quoted number and its source

`PREDECLARATION-20260813-gate5-coherent-replicas-n50.md`, under a heading that reads
*"COST, measured from `sacct` rather than estimated"*:

| component | job measured | wall | allocation |
|---|---|---|---|
| negweight-refined target build | `56344268` | **00:55:32** | 256 CPU, 1 node, no GPU |
| full-event training | `56563761` | **06:00:36** | 32 CPU + 1×A100, 1 node |

…leading to **"Per replica: 0.93 CPU node-hours + 6.01 GPU node-hours"**, then **"At N=50: 46.3 CPU
node-hours + 300.5 GPU node-hours"**, then **"≈ 35 h wall-clock at 10 concurrent"**.

The heading is honest about method — it *was* measured from `sacct`, not guessed. **The wall time is
real; what is wrong is the number of units of work inside it.**

## The measurement that contradicts it

Taken from the live Gate-5 training array `56857233` while members 0–9 were running, using the per-step
history dumps as step boundaries:

| | replica_00 | replica_01 | replica_02 | mean |
|---|---|---|---|---|
| iter0 step1 | 35:47 | 35:18 | 35:50 | **35:38** |
| iter0 step2 | 22:15 | 21:52 | 22:14 | **22:07** |

One iteration = **57:45**. The iteration count is **enforced, not assumed**: `validate_artifact` in
`train_fullevent_replica.py` fails closed unless the realized fit counts are exactly
`(n_fits_base_lr, n_fits_annealed) == (2, 4)` — six fits, three iterations × two steps.

```
3 × 57:45           = 2:53:16
+ measured startup    0:02:55      (job start → shuffle buffer filled, from the .err log)
                    = 2:56:11  = 2.94 h    [LOWER BOUND: excludes finalisation/extraction]
```

**Ratio to the quoted figure: `6:00:36 / 2:56:11 = 2.05`.**

Two independent cross-checks on the step measurement itself:

- The training log reports `13048 training steps at reco and 7812 steps at gen`. Ratio `7812/13048 =
  0.599`, against a measured `step2/step1` of `22:07 / 35:38 = 0.621`. The two legs' durations track
  their batch counts, so the step boundaries are being read correctly.
- **The `.pkl` is the step boundary; the `.weights.h5` is not.** The `.h5` is the best-epoch
  `ModelCheckpoint` save and lands *earlier* (for `replica_00`, 05:14:53 vs the `.pkl` at 05:19:24).
  Using the `.h5` would have understated every step by minutes and produced a spuriously fast estimate.

## Why 2.05 is the finding rather than 2.94 h

A predecessor session had already flagged that `56563761`'s wall time covered two trainings, from the
job's own artifacts. This pass reached the same conclusion from **the opposite direction** — forward
from a running array's step cadence, with no reference to `56563761` at all.

**Two independent methods agreeing on ~2× is what makes it a measurement rather than a suspicion.**
Either alone invites the response "your step extrapolation is missing something" or "you misread the old
job's outputs." Together they don't.

## The generalisable failure

> **A wall time divided by nothing is not a unit cost.** `sacct` reports what the *allocation* consumed,
> not how many units of work ran inside it. Any job that loops — an ensemble member, a seed sweep, a
> two-configuration comparison — reports a wall time that is a multiple of the per-unit cost, and the
> multiple is invisible in `sacct` output.

The trap is sharpened by *doing the right thing*: the predeclaration author deliberately measured
instead of estimating, and labelled the section to say so. **Citing a measurement is not the same as
citing a measurement of the quantity you need**, and the citation makes the number harder to question,
not easier — a figure headed "measured from `sacct`" invites no arithmetic from its readers.

**The check, which costs one command:** before quoting a job's wall time as a unit cost, count the units
in its output — `ls` its artifact directory, or grep its log for the loop banner. If the count is not 1,
divide.

## Consequences, bounded

- **No scientific impact.** Nothing in `C_stat` depends on it. The predeclaration's
  `PASS`/`BLOCK`/`UNRESOLVED` criteria are untouched — none of them reference cost.
- **Scheduling and allocation do depend on it.** Corrected family estimate: **~14.7 h** at 10
  concurrent, not ~35 h; **~150 GPU node-hours**, not 300.5. The measured family projection lands at
  **~19:20–20:10 PDT 2026-08-13**.
- The per-member walltime request of `08:00:00` was sized against the inflated figure and is therefore
  generous rather than tight — the error was in the safe direction for job survival, which is also why
  nothing failed and drew attention to it.

## Deliberately NOT corrected in the predeclaration text

A predeclaration's entire value is that it is fixed before the result is known. Editing its cost table
after the fact would damage the one property that makes the document worth having — and a referee who
finds an edited predeclaration has to discount all of it, not just the edited row.

The correction lives here, in
[`state/gate5-family-reconciliation-20260813.json`](state/gate5-family-reconciliation-20260813.json),
and on Joseph's list. The second uncorrected figure from the same list — 46.3 CPU node-hours, built by
assuming one node per serial 55-minute target build — is the same shape and is **also** contradicted by
this campaign's measurement: target builds are running at ~39 min (mean 2348.3 s over 16 replicas), not
55:32.

## Related

- `BEN-025` — do not let a small-sample estimate overturn a decision; different mechanism, same family
  of "the number was measured, but not of the thing you needed."
- `BEN-077` / `CONVENTION-receipt-ingredients.md` — ship the ingredients, so a derived figure can be
  contradicted by its own operands. A per-unit cost that shipped its unit count could not have done
  this.
