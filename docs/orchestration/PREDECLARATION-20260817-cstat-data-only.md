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

| stream | `N` | `1/√N` | leverage | variance share |
|---|---|---|---|---|
| data | 4,116,128 | 0.0493% | 1 (unit rows) | **72.3%** |
| signal MC | 49,152,885 | 0.0143% | assumed 1 | 6.0% |
| background MC | 564,591 | 0.1331% | **0.2029 — MEASURED** | **21.7%** |

**`σ_total / σ_data ≈ 1.18×`, computed from a MEASURED injected leverage of `0.2029`.** The leverage
is measured; the ratio is a counting-floor computation from it. **Do not quote `1.18×` as measured.**

**AN EARLIER DRAFT OF THIS DOCUMENT SAID `2.89×` AND `~88% MC`, ASSUMING UNIT LEVERAGE. That was
wrong and is recorded rather than deleted.** The correction came from a second key observing that the
claim did not survive its own stated caveat, and then from measurement:

```
pot_scale                        0.212405
RAW w_bkg   n=564,591            mean 0.913923   RMS 0.955308     <- near UNITY
INJECTED w_bkg x pot_scale       mean 0.194122   RMS 0.202912     <- the leverage
```

**The raw MC background weights are essentially unity — the entire suppression is `pot_scale`.** And
refinement is *not* doing the damping, closed by measurement rather than inference: the injected
background is `2.663%` of the data rows and `2.283%` post-refinement, **a factor of 1.17, not the ~6
that would indicate refinement damping.** The ~6 is `1/pot_scale = 4.71`.

**SO THE CASE FOR THIS PRODUCT IS NOT "the published `σ_stat` is 189% too large." IT IS: "it is ~18%
too large, and reducible by generating more MC rather than more data."** That is still an external
comparability defect — still not what the field reports, still not profileable as a nuisance term —
and it is a materially smaller one. **Joseph was given this form and authorized the spend on it.**

**TWO ASSUMPTIONS REMAIN IN THE FOLD-IN, both stated:**
- **Signal leverage is still assumed unity.** Robustness checked: at signal leverage `0.2` the ratio
  moves only `1.176 → ~1.14`, because signal's counting share was `1.00%`. **The one unmeasured
  leverage cannot change the picture.**
- **The counting floor assumes the estimator responds to data and background input fluctuations with
  the SAME GAIN.** It plainly may not — they enter with opposite signs and different kinematic
  distributions, and **`OI-126` establishes this estimator's gain is strongly kinematic-dependent**.
  So the *transmitted* ratio may depart from `1.18×` in a direction nobody can sign. **This bounds the
  INJECTED variance; only the run measures the transmitted one.**

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

Implementation is driver-side (`R_dataonly / R_nominal` rescale). **The no-pinned-file property is
not asserted here — it is lane E's differential `verify_hash_bindings.py` run against the actual diff
(`7820ce5`), against D's complete baseline of 1409 resolved / 2 mismatch (`caa5d4f`): the mismatch set
did not grow.** `BEN-384` requires the gate be run against the edit intended, not the tree at hand.

## 3. Eight predicates, asserted BEFORE the artifact is written

`P1` product tag · `P2`/`P3` signal and background factors present, full-length, **explicitly ones** ·
`P4` data factor drawn and equal to its canonical form — *the coherence check surviving, re-pointed at
the stream that actually varies* · `P5a` **bit-exact zero-pattern** identity to the unthinned MC ·
`P5b` **toleranced** proportionality with the scalar derived independently · `P6` seed under its own
key · `P7` **both** `R` values plus `weights_embody` · `P8` the loader's own stamp left exactly as
written.

**These gate the ARTIFACT, not its interpretation** — asserted inside `replica_atomic` before the
write, so a thinned-MC replica never comes into existence. **30 controls, zero skipped — lane E's verification (`7820ce5`), not this document's.**

## 4. What will be computed, and how each outcome reads

Fifty replicas at **3.0235 A100-h each** — measured from the existing family's realized `sacct`,
job `56857233`, 50/50 COMPLETED, sum 151.175 A100-h (`BEN-027`: a cost that spends money names its
measurement); `C_stat^data` centred on the accepted replica mean, matching
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

**AND PSD PASSING DOES NOT ESTABLISH THE IDENTIFICATION.** If `C_total = C_data + C_MC + 2·Cov`,
then `C_total − C_data = C_MC + 2·Cov` — **a non-zero cross-term gives a PSD matrix that is not
`C_MC`**, overstating with a positive cross-term and understating with a negative one, and **both
pass**. PSD tests *"is this a valid covariance"*, never *"is this the covariance I named."* The
independence the label needs is **stated-not-proved**, structurally identical to `VL130`'s `f/√k`
assumption. **Only an MC-only third ensemble settles the identification** — which is what that
third spend would buy, not merely a rescue of a failed subtraction.

## 5. Predeclared outcomes — derived from the construction, not read off an observation

Per `BEN-403`: a prediction that restates an observation is not a prediction.

- **`σ_stat^data < σ_stat^total`** — *expected by construction*, since two variance sources are removed.
  Confirms nothing; a failure here would indicate a construction defect, not a physics result.
- **The ratio** `σ_total/σ_data` — **genuinely unmeasured.** The counting floor suggests ~2.89× but
  neither the background's negative-injection leverage nor the signal MC's estimator leverage is unit,
  **so any value is admissible and none falsifies anything.** It must be reported, not predicted.
- **A measured ratio near 1** — **NOT a construction failure, and it would RETIRE THIS PRODUCT'S
  STATED MOTIVATION.** It would mean the MC streams contribute almost nothing and the existing
  `C_stat` was already ~data-only in effect. **At a predicted `1.18×` this is close to the expected
  case rather than a remote one, and it must be reported as such.** Without this branch the run
  could not come back negative about its own reason for existing.
- **A measured ratio materially above `1.18×`** — a RESULT, not a discrepancy. The same-gain
  assumption above is exactly what would break, and `OI-126`'s kinematic gain dependence is the
  named mechanism. Do not read it as an error in this document.
- **`C_MCstat` not PSD** — a real possible outcome, and it would mean the decomposition is not
  available by subtraction. **Predeclared as informative rather than as a failure.**
- **The nominal's position relative to this family** — **PREDECLARED AS UNINTERPRETABLE.** The data
  factors are `Poisson(1)` too (`:621`), so 36.8% of *data* rows carry weight zero in every replica
  while the nominal trains on the full inventory. **Only the MC half of the nominal/replica asymmetry
  is removed here.** Non-containment in this family would mean what it means in the three-stream one:
  nothing, absent a mechanism.
  **And the tempting observation is predeclared too: a BETWEEN-FAMILY DIFFERENCE in the nominal's
  position is attributable to the MC streams — but the mechanism that would explain it (`BEN-412`,
  MC-thinning) is ALREADY REFUTED, so such a difference is an UNEXPLAINED ANOMALY to be reported:
  not an `OI-126` finding, and not a resurrection of MC-thinning.**

## 6. Scope limits, stated so they travel

- Does not supersede, discard, re-verdict or re-scope `C_stat^total`, and does not amend Gate 5 F7.
- Says nothing about OI-126, `M(ii)`, `C_ML`, or any quarantine cause.
- The reconciler's data-only verdict path is **scheduled during the run** and **gates the first read
  off the family** — it is the only family-level check, and fifty per-artifact gates cannot see
  *"all fifty are identical"* by construction.
- The measured leg is **not** bit-identical to a one-shot construction: `≲ 2·eps = 2.4e-7`,
  common-mode within a replica, against a 5.167% family spread (`VL130`). **Identity to an unreachable
  construction is explicitly waived.**
