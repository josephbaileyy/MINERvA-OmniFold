# OUTCOME 2026-10-05 — Fixed-truth coverage of the 2D statistical band: FAIL-undercoverage (futility), independently reproduced

**CITABLE FOR:** the pre-registered verdict on whether the production 2D MEFHC statistical band
(VL162: 300 pure-Poisson bootstrap replicas, `--seed 1`, per-bin σ/mean) covers a fixed truth at
its nominal rate. The test uses fixed-truth closure toys: Poisson pseudo-data drawn from the MC
reco weights, the production MC bootstrap stream, and the unfluctuated MC truth as the fixed
reference.

The verdict is **FAIL-undercoverage**, by the interim futility rule at toys 1–100. The record
also covers the per-bin pattern (descriptive) and the pre-registered attribution secondary.

**NOT CITABLE FOR:**

- any change to the 2D central value, its estimator, or any adopted or quoted uncertainty;
- the coverage of the systematic or total uncertainty;
- the 5D products;
- the MC-stream part of the bootstrap principle (Amendment 1, A1.3: the toys' MC scatter uses the
  same resampling that built the band);
- a corrected band. No band was rebuilt or tested.

Ledger: `VL169`. This study's earlier commits call it VL164, then VL168. `main` took VL164–VL167
for the PET final-design rows and VL168 for the PET-vs-GBDT row in the meantime. Pre-registration: [`PREREG-20261005-2d-fixed-truth-coverage.md`](PREREG-20261005-2d-fixed-truth-coverage.md).
It was committed at `e12af23e` before any toy ran. Amendment 1, with the pilot, is `37a0cf8c`;
Amendment 2, operational, is `ae1f91f3`. Both were committed before any full-run toy output was
read. Amendment 2 was written during wave 1, although the pre-registration's header allows
amendments "before the full run". It is operational and changes no criterion. Receipts: [`state/coverage-2d-20261005/`](state/coverage-2d-20261005/).

## 1. The look

All 100 wave-1 toys finished with a resume-guard `.done` marker and none failed: 17 ran on
regular, 33 on debug and 50 on shared (A2.1). `extract_toys.py` and `score_coverage.py --stage
interim` ran at the Perlmutter worktree's commit `37a0cf8c` on 2026-10-05 ~20:00 UTC. The fixed
truth is bit-identical across all 100 toys (`T_max_abs_diff` ≡ 0).

| statistic (205 reported bins × 100 toys) | point | 99.5 % toy-bootstrap interval | window | class |
|---|---|---|---|---|
| C1 = P(\|z\| ≤ 1) | **0.6794** | [0.6693, 0.6899] | [0.6319, 0.7287] | inside |
| C2 = P(\|z\| ≤ 2) | **0.9121** | [0.9065, 0.9179] | [0.9281, 0.9722] | **below** |
| pull RMS | 1.597 | [1.484, 1.723] | — | secondary |
| pull mean | −0.034 | [−0.082, +0.015] | — | secondary |

Nominal coverage is 0.6827 at 1σ and 0.9545 at 2σ. One interval lies entirely below its window
and none lies above, so the verdict is **FAIL-undercoverage**. Under §5 an interim FAIL stops the
study and is the verdict. **Toys 101–200 were not run.** Receipt:
[`interim_score.json`](state/coverage-2d-20261005/interim_score.json); the npz and its manifest
are alongside.

**Positive control (§6): passes.** The same toys were scored with the band scaled by ×0.7 and
×1.3.

| band scale | C1 (99.5 % interval) | C2 (99.5 % interval) | verdict |
|---|---|---|---|
| ×0.7 | 0.524 [0.512, 0.536] | 0.809 [0.801, 0.817] | FAIL-undercoverage |
| ×1.3 | 0.785 [0.776, 0.794] | 0.955 [0.951, 0.958] | FAIL-overcoverage |

Both directions are detected: each ×0.7 interval lies below the ×1.0 point estimates, and each
×1.3 interval lies above them.

## 2. Independent recomputation

A fresh read-only reviewer (an Opus 5.5 subagent) recomputed the look with its own numpy code,
from the npz and the pre-registration, using its own resampling stream (seed 987654321, 40,000
resamples). It was not shown this record's numbers. Results:

- Every point estimate agrees exactly (difference 0).
- The C1 and C2 interval endpoints agree within 5.4e-4. The pull RMS and pull-mean endpoints
  agree within 1.7e-3. All are inside the pre-registered allowance of 3e-3.
- Its verdict, positive-control result and interim decision are the same.

The comparison is in
[`recompute_comparison.json`](state/coverage-2d-20261005/recompute/recompute_comparison.json).
It covers the pooled statistics, intervals, controls and replica form. The per-bin descriptives
in §3 and the lane split were re-derived separately by a second read-only reviewer, whose
claim review of this branch agreed with them.

Script, with its print precision raised to 17 digits, and output:
[`recompute/recompute_independent.py`](state/coverage-2d-20261005/recompute/recompute_independent.py),
[`recompute_independent_output.txt`](state/coverage-2d-20261005/recompute/recompute_independent_output.txt).

## 3. What the verdict rests on

- **Width, not bias.** The pull mean is consistent with zero. The no-fluctuation run reproduces
  T exactly (A1.7, P1), so the seed-1 estimator carries no closure offset into the toys.
- **Per-bin pattern (descriptive, post hoc, no verdict role).** C1 is nominal while C2 is low
  and the pull RMS is 1.6. The band's per-bin calibration is uneven in both directions:
  - Per-bin pull RMS is below 0.9 in 82 bins, within 0.9–1.1 in 52 and above 1.1 in 71. The
    16th–84th percentile range is 0.72–1.44 and the median is 0.97. The pooled C1 is nominal
    partly because over- and under-covering bins cancel.
  - 35 bins have a per-bin C2 below 0.85. Under nominal coverage, each such bin has probability
    1.2e-5 over 100 toys (binomial, at most 84 of 100). Of these 35:
    - 21 form a contiguous block at p_∥ ≥ 15 GeV/c and p_T < 0.55 GeV/c;
    - 6 lie in the highest-p_T row (2.5–4.5 GeV/c) at p_∥ 6–20 GeV/c;
    - 4 adjoin the block at p_∥ 9–15 GeV/c;
    - 4 are scattered.
  - 14 bins have a per-bin pull RMS above 2. Their deficit sums to 72 % of the pooled C2 deficit.
    The worst is p_T 2.5–4.5, p_∥ 6–7 GeV/c, at 14.6. Eleven of the 14 are at the phase-space
    edges; three, at p_∥ 15–20 GeV/c and p_T 0.33–0.47 GeV/c, are interior.
  - With the 10 worst bins removed, C2 is 0.935.
- **Lane independence (A2.2, descriptive).** C2 is 0.918 on regular (17 toys), 0.915 on debug
  (33) and 0.908 on shared (50, run with 64 threads).
- **Attribution secondary (A1.1 and A1.8, no verdict role).** Each toy was rescored in the
  replica form `U·T/P`, which applies the bootstrapped-completeness division the VL162 replicas
  carry. That gives C1 0.833 [0.819, 0.846], above its window, which drives the
  FAIL-**over**coverage. C2 is 0.974 [0.968, 0.979], straddling the window's upper edge, and the
  pull RMS is 0.81.
  - The secondary was added by Amendment 1 after the pilot ran.
  - Its undercoverage branch (A1.8) was written after the pilot pulls had been seen; those pulls
    already pointed this way.
  - Both were fixed before the full run.

  Under that rule, the primary undercoverage is **attributed to the completeness term**: the VL162 replicas divide by a per-replica
  completeness `P/T` that the central value (c ≡ 1) does not carry. That division cancels part of
  the MC-driven scatter, so the band understates the scatter of the estimator that produces the
  central value. The attribution is partial in two ways:
  - The replica form overcovering means the band does not match that form either.
  - In the replica form, the p_∥ 40–60 GeV/c column at p_T < 0.47 GeV/c still undercovers, with
    per-bin C2 of 0.72–0.89 and RMS up to 2.2.

  The band transfer is a disclosed difference between the data band and the MC-truth toys. Under
  A1.2, `prod_mean/T` has a median of 1.145 and is 1.2–1.3 in most of the worst bins.

## 4. Cost

Total charge is 13.33 CPU node-h on m3246, against the 60 node-h cap:

| stage | jobs | node-h |
|---|---|---|
| pilot | 3 | 0.594 |
| equivalence | 2 | 0.204 |
| wave 1 | 101 | 12.53 |

Wave 1's 101 accounting records are the 100 completed toys plus one CANCELLED record at 0 s.
That record is index 67, a pending regular task moved to the shared lane, which then completed
it. Other cancelled pending tasks, including index 100 (A2.4), leave no `sacct` record. All jobs ran under
regular, debug or shared QOS at usage factor 1.0, with no premium and no overrun. The account
balance was measured before and after. The ledger is in
[`budget.json`](state/coverage-2d-20261005/budget.json).

## 5. What follows, and what does not

- The note no longer says the 2D statistical band's coverage is untested. It now says the band,
  as built, undercovers a fixed truth in its tails. It also says the per-bin calibration is
  uneven, and that the 2σ deficit is concentrated at high p_∥ and low p_T and in the
  highest-p_T row.
- The quoted 2D statistical uncertainty and covariance are **unchanged**. A coverage result
  cannot change an adopted or quoted uncertainty. Whether to rebuild the band without the
  bootstrapped completeness, and then re-test it, is a separate decision for Joseph
  (`KNOWN_ISSUES.md` 84).
- Nothing here bears on the systematic, total or 5D uncertainties.
