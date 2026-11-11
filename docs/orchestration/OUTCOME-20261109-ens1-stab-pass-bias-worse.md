# OUTCOME 2026-11-09: ENS1, the ensemble-averaged estimator. Stage 1 STAB_PASS; stage 2 BIAS_WORSE at one truth (Stage 0c GiBUU), so E₉₆ is not a stabilised variant and the reported estimator is unchanged

**Recorded by** the director (paper-tighten lane), from the two committed analysis receipts.

**The design:** `fd/rounding-stability-20261106/ensemble/ENS1-DECLARATION.md`, bound by `ENS1-BINDING-1.md` and
`ENS1-BINDING-2.md` (addendum A1, M_A1 = `f4d2d7f3`). Step 2 of the rounding-instability work, declared before RS1's
outcome was read (`OUTCOME-20261108-rs1-rounding-mechanism.md`).

**The records:**
- stage 1: `ensemble/receipts/stage1-a1-analysis/ens1_stage1.json`, sha256 `7f5a9ce4…` (#940), after the full run's
  receipt `stage1-a1/` (#938);
- stage 2: `ensemble/receipts/stage2-a1-analysis/ens1_stage2.json`, sha256 `c2ee701d…` (#957), after the full run's
  receipt `stage2-a1/` (#956).

The director read both receipts' READMEs and their tables on main.

## The readings, as the records state them

**Stage 1 (declaration §4): `STAB_PASS`.** N = 96, 10 pairs, against FD-STAB's bars of 0.3 (median) and 1.0
(maximum):

| estimator | mean median (SE) | mean max (SE) | passes |
|---|---|---|---|
| E₉₆ | 0.0821 (0.0038) | 0.7586 (0.0723) | true |
| F_P10 | 0.7598 (0.0262) | 6.7754 (0.4183) | false |

- G0 holds (F fails at P = 10, as §4.2 requires).
- **An observation, not a gate:** E₉₆'s worst single pair has a maximum of 1.0652, above the 1.0 bar. The bound
  criterion is the 10-pair mean, which passes.

**Stage 2 (declaration §5): `BIAS_WORSE`, `worse = ["stage0c_gibuu"]`.**
- E₉₆ is no worse than F at 16 of the 17 judged truths. At `stage0c_gibuu` its RMS bias over the 16 cells is
  0.056467 against F's 0.055955: an excess of 0.000512 over a floor of 0.000418, 1.23 times the floor. Its MAX excess
  (0.000929) is within its floor (0.001783).
- Every floor is non-zero, so the verdict is not INVALID.
- At the other GiBUU truth, `A7_gibuu`, E₉₆ is better than F on both metrics.

**Why the GiBUU truth counts.** ENS1 §5.3 (`:220`): "PASS: no worse at all 17 truths", and (`:225-226`) the GiBUU
readout "is printed and used by no criterion (FD-STAB §5.3)". FD-STAB §5.3 (`:206-209`): "Neither the bias criterion
beyond 'no worse', nor any other criterion, nor the tie-break may use them." So "no worse" judges both GiBUU truths and
only their bias magnitudes are descriptive. The bound code does this; the director confirmed the reading; nothing is
reinterpreted.

**The declared familywise rate** of a false "worse" over 17 truths × 2 metrics (`:216-217`): about 0.5 % with correctly
estimated SDs, at most about 4.5 % if both SDs are underestimated by their full factors.

**The cost:** stage 1 38.9166 of its 55.0 cap; stage 2 33.1347 of its 46.0 cap.

**One teardown, accepted under the director's ruling:** task `ens1_stage0c_gibuu_k057` exited 129 (as GNU time reports
it; no cause is claimed) after both products existed. The guard re-ran it once; the re-run's `xsec_flat` and
`xtrue_flat` equal the first run's array for array. It does not bear on the verdict.

## CITABLE FOR

- **Stage 1:** "an ensemble-averaged variant of the estimator (96 fits) meets the stability bars fixed before the test
  on the declared stability input (median 0.08 and maximum 0.76, in the units of FD-STAB's statistic, against 0.3 and
  1.0), where the reported estimator does not."
- **Stage 2:** "on the declared noise-free closures at 17 truths, the ensemble-averaged variant is no worse than the
  reported estimator at 16 and worse at one (Stage 0c GiBUU, by its RMS bias), by the criterion fixed before the test;
  it is therefore not adopted."
- **The consequence:** the reported estimator, configuration (e), is unchanged.
- **Amended 2026-11-10 by Joseph's decision** ([`DECISION-20261110-joseph-ens1-deficit-licence.md`](DECISION-20261110-joseph-ens1-deficit-licence.md)),
  for this sentence only: "At the one truth where it was worse (Stage 0c GiBUU), the ensemble average's RMS closure
  bias over the 16 cells exceeded the reported estimator's by 0.000512 (0.056467 against 0.055955), 1.23 times the
  declared floor of 0.000418; its maximum-bias excess, 0.000929, was within its floor of 0.001783."

## NOT CITABLE FOR

- **That E₉₆ is a stabilised variant** (§5.3: "BIAS_WORSE: … E₉₆ is not described as a stabilised variant").
- **That the rounding instability is fixed or removed** for the reported result.
- **Any use of the GiBUU bias magnitudes** beyond "no worse" and the one amended sentence above.
- **Any statement about the real data**, or that the stage-0c excess is or is not noise. The declared familywise rate
  is a property of the criterion, not a reading of this result.
- **Any absolute statement about E₉₆'s bias**, or a ranking of the two estimators beyond the verdict.
- **A paper or note sentence.** Wording is Joseph's, through the PRD-referee read.

## What it changes, and what stands

- **The replacement question is closed for ENS1:** with BIAS_WORSE there is no stabilised variant to adopt, so the
  decision the declaration reserved for Joseph (`:221`) does not arise.
- **Unchanged:** RS1's outcome, FD-STAB's outcome, the reported estimator and its uncertainty, and every earlier record.
- **The rounding instability remains a stated limitation** of the reported result, with RS1's licensed mechanism on one
  pseudo-experiment, and the spread carried in the statistical block as before.
- **Any further remedy** would be a new declaration, chosen after this result, and is Joseph's to authorize.

Nothing is submitted, deposited or tagged.
