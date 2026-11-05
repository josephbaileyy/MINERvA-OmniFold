# OUTCOME 2026-11-05 — the B4 stabilisation probe: NONE_PASS

**Recorded by** the paper-tighten lane, as director.

**The record:** `state/measurement-paper/5d-community-20261024/fd/receipts-stab-a1r/readout/readout-2/fd_stab.json`,
sha256 `653356ae56087ea74621e61a60c829d63be9a9f15b0b35941e641b22f0be8ea3`. It was produced by the bound
`estimator_stability_analyze.py` (blob `0e471890`, at M_A1 `cc54d86f`) over the full run's products (job 60837713,
DONE 128/128, receipts #782 at `75a81b27`). The director read it from main.

**The probe:** `FD-STAB-DECLARATION.md`, under addendum A1, bindings 1, 1-A1 (with its correction) and 2.
- **What it tests:** whether 2-fold cross-fitting (B2) or tree regularisation (B3a, B3b) brings configuration (e)'s
  rounding-scale spread under the predeclared bar without worsening its bias at any of 17 F0b truths.
- **The bar:** mean median ≤ 0.3 and mean maximum ≤ 1.0 statistical σ, over 25 disjoint jitter pairs.
- **Pseudo-data only;** no data was read.
- **The cost:** 4.86 of the 8.0 CPU node-h cap, including the invalid first dry run, which was the director's
  time-format error.

## The verdict, as the record states it

**`NONE_PASS`, with no winners and no passers.** G0 holds (`g0_informative: true`): the control fails the bar, so the
probe could discriminate.

| | mean median | mean max | passes the bar | no worse at all 17 truths |
|---|---:|---:|---|---|
| control (e) | 0.759 (SE 0.022) | 6.83 (SE 0.29) | no | — |
| B2, 2-fold cross-fitting | 0.528 (SE 0.014) | 4.22 (SE 0.24) | no | no: worse at W3, stage0c_gibuu, closure_nuwro |
| B3a | 0.851 (SE 0.022) | 6.35 (SE 0.26) | no | yes |
| B3b | 0.861 (SE 0.022) | 6.67 (SE 0.23) | no | no: worse at A7_genie_cv |

- **The data-σ-equivalent.** The record's `data_sigma_equivalent_factor` is 1.569: the bars here are stricter than on
  data by up to that factor (§4.2). Dividing by it is the director's arithmetic, not a field of the record. That gives
  control 0.48 / 4.35, B2 0.34 / 2.69, B3a 0.54 / 4.04 and B3b 0.55 / 4.25. Every candidate still exceeds both bars, so
  the verdict does not depend on that factor.
- **The GiBUU readout is descriptive and is used by no criterion** (§5.3). At A7_gibuu the control's RMS fractional
  bias (b = X / X_true − 1, §5.1) over the 16 cells is 0.130 and its maximum |b| is 0.365. Across the three candidates
  the RMS is 0.128–0.130 and the maximum 0.353–0.362, a change of at most 0.012.

## What follows, as already decided

`FD-STAB-DECLARATION.md` §6: "**NONE_PASS:** no candidate passes. **Terminal**, with the same consequences" as
UNINFORMATIVE: "No estimator change proceeds from this probe. IV G stays as stated, and 1B stage 1 launches on the
current estimator, as decided."
- **No estimator is adopted.** `DECISION-20261102-joseph-bias-and-stabilisation-routes.md` item 2 does not arise.
- **1B stage 1 launches on configuration (e) as planned** (that decision's item 3), after binding 3.
- **The paper's rounding-instability statement stays as stated.**
- **Still open for Joseph** (that decision's item 5): B0's reconciliation sentence (seeds inert; the bootstrap
  already carries the rounding spread). The paper lane drafts it, with this outcome, through a PRD-referee read of
  the exact wording.

## What this outcome is not

- It is not a measurement on data, a coverage statement, or a statement of any candidate's statistical σ (§1).
- B2's lower spread is not a passing result. It fails the bar, and it is worse at three truths by the measured
  floor. No sentence may present it as an improvement found.

Nothing is submitted, deposited or tagged.
