# PREDECLARATION 2026-08-17 — `C_stat^data`, a second statistical covariance built for external comparability

**Written before submission. Nothing has been run.** Authorized by Joseph at 151.17 A100-h
(`AUTHORIZATION-20260817-data-only-cstat-second-ensemble.md`, 9dae576), built by lane E (`7820ce5`),
specified by lane C across `BEN-404`, `BEN-407`, `BEN-408`, `BEN-409`. This document states what will
be computed and what each outcome would mean, **before** the family exists.

## 1. Why this product exists — and it is NOT an OI-126 instrument

**The motivation is external comparability and nothing else.**

The existing `C_stat` is **total** statistics — data, signal-MC and background-MC Poisson streams —
specified at the DAG in Gate 5 F7 (`PET_UQ_REMEDIATION_STATUS.md:738-758`, *"apply signal factors
everywhere signal MC is used"*). Lane C ruled that **correct by internal design**: no `C_MCstat`
component exists anywhere in the budget, and `C_syst` varies physics parameters rather than sample
size, so if `C_stat` did not carry the MC Poisson **nothing in the declared budget would**.

That argument is about the budget's internal consistency and is **silent on external comparability**:

| stream | `N` | `1/√N` | variance share |
|---|---|---|---|
| data | 4,116,128 | 0.0493% | **11.94%** |
| signal MC | 49,152,885 | 0.0143% | 1.00% |
| background MC | 564,591 | **0.1331%** | **87.06%** |
| quadrature | | 0.1426% | `σ(3-stream)/σ(data-only) = 2.89×` |

A published *"statistical"* uncertainty that is **~88% MC statistics by counting-floor variance** is
not comparable to MINERvA's own or to T2K / MicroBooNE / NOvA, cannot be profiled as a nuisance term
in a global fit, and is **reducible by generating more MC** — which is precisely what `σ_stat` is not.

*Limit, stated because the numbers will be quoted: these are raw `1/√N` counting fractions. Background
enters as a negative injection and signal MC through the estimator, so neither propagates with unit
leverage. **The set of contributing streams is certain; the variance shares are indicative.***

**PREDECLARED NEGATIVE: this run is not evidence about OI-126.** An earlier draft justified it partly
as a test of whether the nominal's non-containment is MC-thinning-driven. **That justification was
withdrawn before submission** on lane E's occupancy measurement (`BEN-412`): thinning is uniform in
share (surviving distinct fraction 0.63205 band / 0.63253 outside, against `1−1/e = 0.63212`), so the
mechanism required the band to be the MC-sparse end — and it is the **dense** end at every low-tail
threshold. No OI-126 conclusion may be drawn from this family.

## 2. What is built, and what makes it different

`C_stat^data` resamples the **data stream only**. Signal and background factors are explicitly unity.

**Background is excluded on fact, not convention.** It is not a measured sideband: `:568` and `:615`
say *"background-MC"*, and the factor multiplies a **POT-scaled negative injection** — an MC
prediction scaled to exposure. Its Poisson **is** MC statistics.

**The measured normalization `R` VARIES with the data draw.** This is `BEN-408` and it is the single
most consequential specification choice here. `normalize=True` makes the post-normalization measured
total exactly `1e6·R` whatever the refined target summed to — so the target's data fluctuation is
**divided back out**, and `R` is the **only** route by which the data-count fluctuation reaches the
measured normalization. Freezing it would remove the rate term **by exact cancellation**, yielding a
**shape-only** statistical uncertainty under a name the field reads as total-rate. That is `BEN-400`'s
defect reproduced inside a published `σ_stat`.

Implementation is driver-side (`R_dataonly / R_nominal` rescale), touching **no pinned file**.

## 3. Eight predicates, asserted BEFORE the artifact is written

`P1` product tag · `P2`/`P3` signal and background factors present, full-length, **explicitly ones** ·
`P4` data factor drawn and equal to its canonical form — *the coherence check surviving, re-pointed at
the stream that actually varies* · `P5a` **bit-exact zero-pattern** identity to the unthinned MC ·
`P5b` **toleranced** proportionality with the scalar derived independently · `P6` seed under its own
key · `P7` **both** `R` values plus `weights_embody` · `P8` the loader's own stamp left exactly as
written.

**These gate the ARTIFACT, not its interpretation** — asserted inside `replica_atomic` before the
write, so a thinned-MC replica never comes into existence. 30 controls, zero skipped.

## 4. What will be computed, and how each outcome reads

Fifty replicas at 3.0235 A100-h each; `C_stat^data` centred on the accepted replica mean, matching
F7 and `CSTAT-D2` — **for comparability, not deference**: different centrings make the difference
between products no longer attributable to the streams.

| quantity | meaning |
|---|---|
| `σ_stat^data` | **the published statistical uncertainty.** Comparable with other neutrino–nucleus measurements |
| `C_stat^total` | unchanged, not superseded, not re-verdicted |
| `C_MCstat := C_total − C_data` | **the component the budget has no name for** |

**`C_MCstat` MUST BE PSD-CHECKED BEFORE BEING CALLED A COVARIANCE.** Both families pass through the
same trained network, so the stream perturbations are **not** independent and `C_total ≠ C_data + C_MC`
in general. **PSD → the subtraction is the cheap route. NOT PSD → defining it needs an MC-only
ensemble, a third spend that is NOT authorized and which nothing here pre-commits to.**

## 5. Predeclared outcomes — derived from the construction, not read off an observation

Per `BEN-403`: a prediction that restates an observation is not a prediction.

- **`σ_stat^data < σ_stat^total`** — *expected by construction*, since two variance sources are removed.
  Confirms nothing; a failure here would indicate a construction defect, not a physics result.
- **The ratio** `σ_total/σ_data` — **genuinely unmeasured.** The counting floor suggests ~2.89× but
  neither the background's negative-injection leverage nor the signal MC's estimator leverage is unit,
  **so any value is admissible and none falsifies anything.** It must be reported, not predicted.
- **`C_MCstat` not PSD** — a real possible outcome, and it would mean the decomposition is not
  available by subtraction. **Predeclared as informative rather than as a failure.**
- **The nominal's position relative to this family** — **PREDECLARED AS UNINTERPRETABLE.** The data
  factors are `Poisson(1)` too (`:621`), so 36.8% of *data* rows carry weight zero in every replica
  while the nominal trains on the full inventory. **Only the MC half of the nominal/replica asymmetry
  is removed here.** Non-containment in this family would mean what it means in the three-stream one:
  nothing, absent a mechanism.

## 6. Scope limits, stated so they travel

- Does not supersede, discard, re-verdict or re-scope `C_stat^total`, and does not amend Gate 5 F7.
- Says nothing about OI-126, `M(ii)`, `C_ML`, or any quarantine cause.
- The reconciler's data-only verdict path is **scheduled during the run** and **gates the first read
  off the family** — it is the only family-level check, and fifty per-artifact gates cannot see
  *"all fifty are identical"* by construction.
- The measured leg is **not** bit-identical to a one-shot construction: `≲ 2·eps = 2.4e-7`,
  common-mode within a replica, against a 5.167% family spread. **Identity to an unreachable
  construction is explicitly waived.**
