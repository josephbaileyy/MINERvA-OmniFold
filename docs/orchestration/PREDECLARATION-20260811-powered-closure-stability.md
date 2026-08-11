# PREDECLARATION — is `0.5126033` a point estimate or one draw? (powered-closure stability, n=2)

**Committed BEFORE submission.** Compute authorized by Joseph 2026-08-10 22:04:41Z. Recommended by the
oversight session; I independently agree, which is the condition he set (22:17:16Z). **No promotion, no
threshold change, `niter` 3, Branch C closed.**

## The question, and why an inference is not good enough here

`0.5126033` is the D2 recovery that **passed** the adopted CLM-012 criterion with margin `+0.0180209`. It is
on Joseph's record as a settled pass, and the queued k=3 restatement will **re-derive** from it.

I established by code reading (`8b8f238`) that its wrapper carries **exactly the production override set** —
`__init__`, `CompileModel`, `RunModel` — and therefore belongs to the family measured at `1.27e-4`, not the
diagnostic family measured at `4.34e-3`. That reading stands. **But it is an inference with a confound:** the
two measured families differ in *both* override set **and** driver version, so attributing the stability to
the override set is exactly the two-variable attribution this campaign has spent a night catching in other
arguments. Measuring is what removes the label.

**What rides on it, stated as the asymmetry it is:**

    margin over the adopted bar = +0.0180209
      = 142 production scatters   (stable family -> the pass is overwhelming)
      =   4.2 diagnostic spreads  (unstable family -> the pass is one draw from an unsampled distribution)

Stable outcome: nothing changes. Unstable outcome: the D2 PASS, CLM-012's adoption margin, and the
`−0.03424972` secondary trade-off figure all rest on single draws and need n≥2 before anything quotes them
further. ~2 GPU-h against that is not a close trade.

**Why now rather than at the gate:** queue waits here have run 3 h to 28 h, so "now" and "when the restatement
needs it" are not the same wall-clock. Starting now means the answer exists when the gate arrives instead of
the gate waiting on the queue.

## THE TEST, fixed in advance

Repeat `56552326` — same launcher, same pins, same inputs, same seeds — and compare the **recovery**.

    quantity   metrics.recovery from POWERED_CLOSURE_ANNEALED.slurm-<job>.json
    reference  0.5126032761517403   (job 56552326, validated by finalizer 56562169 at 31/31)
    delta      |recovery_repeat - 0.5126032761517403|

| outcome | condition | reading |
|---|---|---|
| **STABLE CONFIRMED** | `delta <= 0.0003803` | The override-set attribution is right and **retired as an inference**. The D2 pass stands as recorded, margin is ~142 scatters, and the k=3 restatement may re-derive from `0.5126033` freely. |
| **DIAGNOSTIC-SCALE** | `delta >= 0.0014459` | The override-set attribution is **wrong**. `0.5126033` is one draw; the D2 PASS, the `+0.0180209` margin and the `−0.03424972` trade-off all require n≥2 before being quoted, and the restatement must not consume any of them until then. |
| **UNRESOLVED** | `0.0003803 < delta < 0.0014459` | Neither follows. State it as unresolved; the next step is a **third** powered-closure run, not a re-reading of these two. |

**Thresholds, justified:** `0.0003803` is `3 ×` the measured production scatter (`0.000126775`); `0.0014459`
is `⅓ ×` the measured diagnostic spread (`0.004337639`). Both are scaled from measurements rather than
picked, they leave a genuine `3.8×`-wide UNRESOLVED band between them, and neither is the tolerance of a
gate — this run changes no threshold.

**Three branches, not two, because two branches failed once already tonight.** Design A returned
`−0.007386682`, outside both of its bands and 11.4 tolerances from the nearer one, and a two-branch reading
would have recorded it as "reproduced". *That correction came from the oversight session and it changed a
conclusion, not a wording.*

## An expected non-zero exit, declared in advance so it is not read as a failure

`closure_powered_truth_reweight.py:105` hardcodes `RESIDUAL_OVER_GAP_MAX = 0.20` — the bar **CLM-012 retired
on 2026-08-09** — and exits **3** when its own literal is not met. `56552326` therefore shows `FAILED` in
`sacct` despite completing, writing its report and artifact, and verifying its LR pattern (KNOWN_ISSUES:
*"The powered closure's `recovery_criteria_met` is computed against the RETIRED bar"*).

So this launcher **tolerates exit 3 and only exit 3**, then asserts the report exists and carries a numeric
`metrics.recovery`. Any other non-zero exit is fatal. **This is not a tolerance being raised to make a check
pass** — no threshold is altered, the retired bar is not consulted for the verdict, and the adopted criterion
is applied by the validator as always. It is a known driver exit code being handled instead of masking the
run's products, which is what happened last time.

## Explicitly forbidden

Averaging the two recoveries into a "best estimate"; re-running until a delta lands in a band; widening either
threshold after seeing the number; reading UNRESOLVED as weak support for stability; promoting any arm;
changing `niter`; touching FROZEN.

## Provenance

- `0.5126032761517403`, margin `+0.0180209` vs bar `0.4945824` — job `56552326`, finalizer `56562169`
  (exit 0, 31/31 authoritative validator checks, 8/8 hash checks)
- `0.000126775` — production matched pair, job `56563761`, n=2
- `0.004337639` — diagnostic pair, jobs `56534117` and `56586368`, n=2, byte-identical code and seeds
- override sets — read from `closure_powered_annealed_lr.py`, `train_fullevent_nominal.py`,
  `diagnose_step1_annealed_lr.py` at `8b8f238`
