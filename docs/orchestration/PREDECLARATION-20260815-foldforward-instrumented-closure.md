# PREDECLARATION — fold-forward instrumented / corrected powered closure

**Written and committed BEFORE submission.** Its whole value is its timestamp (`BEN-244`; this campaign
has already had one declaration written after the artifact it declared). Authorization:
`AUTHORIZATION-20260815-foldforward-closure-run.md`. Launcher:
`nd-unfolding/pet/sbatch_foldforward_instrumented_closure.sh`. Code: `closure_foldforward_instrumented.py`
(landed `b372069`, 18 tests, every guard mutation-tested).

## The design

Six array tasks, one A100 each. Tasks **0–2 = ARM 0** (instrumented, uncorrected). Tasks
**3–5 = ARM 1** (scale-only corrected). Three draws per arm of the *same* configuration — the closure
driver takes no seed flag and reads `NOMINAL_SEED_POLICY`, so the spread is training nondeterminism,
exactly as the three existing draws were produced (`56552326` / `56611837` / `56626305`,
`sd 0.000820128`).

## 1. ARM 0 IS A HARD GATE ON READING ARM 1

Arm 0 must reproduce the existing draws: recovery inside the measured three-draw band, and the four
285-cell spectra comparable at the finalizer's `1e-9`. **If arm 0 does not reproduce, arm 1 is not read
at all, whatever it printed** — the instrumentation would have changed behaviour and nothing downstream
would mean anything. The gate is applied by the reader; the launcher does not decide verdicts.

## 2. The prediction that converts a reconstruction into a record

Arm 0's recorded fold-forward is **predicted to be ≈ `1.011418`** at the final iteration — the executor
lane's reconstruction from `weights_push` + `dump_rows_b` (`RECEIPT-vl100-shape-corrected-foldforward-20260815.json`).
Agreement makes that number a *recorded* value and closes `OI-125`.
**Disagreement is itself a result and outranks everything else in the run** — it would mean the
reconstruction, or the push↔row alignment argument behind it, is wrong.

## 3. The measured quantity

`Δrecovery = recovery(arm 1) − recovery(arm 0)`, per draw and pooled, reported **with** its spread and
against the margin `0.01802087615174025`. **Realized exceedance, not a fitted gaussian tail**
(`BEN-025`).

## 4. No threshold moves

The adopted criterion stays `0.80 × 0.618228 = 0.49458240000000003`. A result that fails it is a
result, not a reason to revisit the bar. The driver's own retired `RESIDUAL_OVER_GAP_MAX = 0.20`
literal is **not** consulted for any verdict; its exit 3 is tolerated for that reason and only that
reason (see the launcher header).

## 5. The correction is SCALE-ONLY

One scalar `R / ratio` per iteration, applied to `weights_push` **before** step 1 consumes it. **A
per-cell correction is refused, on measured grounds:** any per-cell field built from `push` is the
unfolding's own per-cell output (`ratio[c]` vs `h_unfolded[c]/h_prior[c]`, Pearson `0.99973` on the
nominal run and `0.99987` on this closure), so dividing it out is a **de-unfolding** and returns
recovery to `≈ 0` by construction (`BEN-310`; measured `-0.000808`). A later reader will be tempted to
"improve" this to per-cell. **Refuse it unless they can name a per-cell reference the record contains,
which as of today it does not — `R` is one scalar.** Guarded executably by
`CorrectedArmTest::test_correction_is_a_pure_scalar` and `…_applied_BEFORE_step1_consumes_it`.

## 6. THE LIMITATION THAT MUST BE DECLARED NOW, NOT DISCOVERED IN THE RESULT

**Arm 1's correction amplitude on this closure is small, and that is knowable in advance.** The
nominal run's deficit is 34% because `ratio = 0.736746` against `R = 1.124080`. **This closure's
fold-forward ratio is ≈ `1.011418`**, so unless `R` for its own A/B split is far from 1 — and both
halves are equal-size with a rate-preserving tilt, so it should not be — **the scale-only correction is
a rescale of order 1%.**

Consequences, declared before the run so a green result cannot be over-read:

- **Arm 1 measures the sensitivity of recovery to a ~1% fold-forward rescale.** It does **not** measure
  the effect of correcting a 34% deficit.
- A ~1% rescale may well move recovery by **less than the draw spread `0.00082`**, in which case
  **arm 1 is underpowered by construction and the honest report is a BOUND, not a null.** Say
  *"|Δrecovery| < X at 3 draws per arm"*, never *"the fold-forward does not affect recovery."*
- **Arm 0's value does not depend on any of this.** Arm 0 closes `OI-125` and supplies the recovery
  evaluation `OI-71` G4 asks for. That is the run's primary product.
- **The 34% deficit needs a corrected NOMINAL run, not a corrected closure.** Out of scope here, and no
  outcome of this run bears on it.

`R` is recorded per iteration by the instrumentation, so **the run self-diagnoses this**: iteration 0
has `push == 1` by construction, making its `deviation_from_R` exactly `|1/R − 1|` — read that row
first to see how large the correction could possibly have been.

## 7. Outcomes declared uninformative in advance

1. **Arm 0 fails to reproduce** → the instrumentation changed behaviour. Arm 1 unread; investigate the
   recorder, do not report a Δ.
2. **`|Δrecovery|` below the pooled spread** → underpowered. Report the bound (§6), not a sign.
3. **Arm 1's recorded correction factor ≈ 1** → there was nothing to correct on this closure. Report
   that as the finding; it is the §6 case realized, and it is informative about the closure's fitness
   as a proxy for the nominal run.
4. **Any task exiting other than 0 or 3** → not a result. The launcher refuses.

## 8. Constraints carried into the run

- Read-only outside this run's own outputs. **No `scancel`, no `scontrol update`** on anything not
  this array. `/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` untouched.
- **No repinning.** Driver `a45fae7c…`, annealed wrapper `ce9f11f4…`, engine `3a2022b0…` — all three
  asserted by digest in the launcher's `G0` and verified byte-identical between local `HEAD` and the
  cluster tree before submission. The cluster repo is **not** pulled; only the two new files are copied.
- Job ids reported from `squeue`, per-task state from a command run in the same turn, never from
  `sbatch` stdout (`BEN-027`). **`sacct` is not authoritative for an array that has not started**
  (`BEN-229`) — use `squeue -r`, and `scontrol show job <array>_<task>` for raw ids.
- **A quiet log is not a dead job** (`BEN-028`): liveness by `sstat` CPU time and produced artifacts,
  never by log growth.
- NERSC cert expires `2026-08-16T00:59:48Z`; ssh exit 255 after that is the cert, not the job, and the
  job keeps running regardless.
