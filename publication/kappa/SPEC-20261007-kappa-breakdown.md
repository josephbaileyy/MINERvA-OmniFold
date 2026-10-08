# Report-only κ-breakdown of the joint-test decisions: predeclared specification (2026-10-07)

**Status: FROZEN at the commit that first adds this file, BEFORE any κ value other than the frozen 2 and 3 is
evaluated.** The spec was written after only two things had been run: the RC4 checksum verification and a timing
of one κ = 2 null evaluation for GENIE + MEC.

**Authority (Joseph, 2026-10-07, this session, verbatim):** "Authorize the report-only κ-breakdown proposed in
REVIEW-20261007 §5, using existing sufficient inputs only. Preserve all frozen primary decisions. Specify the
evaluated shift family, range, resolution, and stopping rule before computing. Re-evaluate the full ten-test family
with its multiplicity and determinacy rules; distinguish loss of a determinate rejection from failure to reject. Do
not assume monotonicity without checking it. Report thresholds or bounded ranges, reproduce the κ=2 and κ=3
reference results, and explicitly state that this measures sensitivity along the chosen shifts, not convergence or
detector-model adequacy. No new pseudo-experiments or broader campaign."

**CITABLE FOR (once the result record exists):** how the ten Holm-with-determinacy decisions behave when the
sub-fine-grid variant multiplier κ is varied along the frozen shift direction δ_M1.
**NOT CITABLE FOR:**
- any change to a frozen primary decision; those remain amendment 7's κ = 2 decisions as recorded
  (`RECORD-20261005`, `joint-evaluate.json` `b9604502…`);
- convergence of the fine-grid null;
- the size of the true sub-fine-grid residual;
- detector-model or hadronic-response adequacy;
- any other shift direction;
- a measurement.

## 1. Inputs (existing sufficient inputs only; no new pseudo-experiment)

- **Primary: reading F (frozen).** RC4 `data/frozen/inference_sufficient.npz` sha256 `7bd019c6…` with its manifest
  `e8aedfe8…`. Expected reference: RC4 `expected/joint-evaluate.json` `b9604502…`.
- **Secondary: reading (a) (recovery union, report-only).** RC4 `data/recovery-union/inference_sufficient.npz`
  `6ffed091…`, manifest `757d39f8…`. Expected reference: RC4 `expected/resolved-evaluate.json` `8503eab8…`.
- **RC4 tree:** every file is verified against `docs/publication/release/RC4-SHA256SUMS.txt` (all OK), copied from a
  local extraction of RC4 into this session's scratch space.
- **Rules:** RC4 `code/replay_inference.py` sha256 `41f4af05…`, identical to `publication/release/replay_inference.py`
  on main. It is the release's standalone restatement of the frozen rules, and the scan imports its functions
  unchanged: `statistics`, `mc_pvalue`, `holm_determined`, `cp_interval`.

## 2. Shift family

For each external null G (GENIE CV, GENIE + MEC, NuWro, GiBUU), δ_M1(G) is the frozen `d1__<G>` vector (the
noise-free fine-minus-merged-×2 difference, amendment 7 `calibration.m1_shift`). The Tune v1 null has no M1 variant
(manifest `m1: null`, ρ = 1), so its two p values do not depend on κ. It stays in the family at its frozen values.

Two variant families are evaluated, both by the frozen rule "claim p = the largest p over the family's variants",
taken separately for the total and the shape statistic:

- **Family A, pointwise:** process-shift variants {c·S, c ∈ {0, ½, 1}} ∪ {+κ·δ_M1, −κ·δ_M1}.
  - At κ = 2 this is the frozen claim rule exactly.
- **Family B, robustness-label generalization (κ ≥ 2 only):** the family-A variants at κ = 2, plus {+κ·δ_M1, −κ·δ_M1}.
  - At κ = 3 this is exactly the frozen κ = 3 robustness label: max(claim, ±3 variants).

## 3. Decision rule at each κ

All ten claim p values (two per null; Tune v1 at its frozen values) enter the frozen `holm_determined`: Holm at
familywise α = 0.05, m = 10, with the 95% Clopper–Pearson determinacy rule.

Each test's family decision is one of three states, which are reported separately:
- **"rejected":** a determinate rejection;
- **"undetermined":** the first failing step's CP interval contains its threshold, so a determinate rejection is lost
  without a determinate failure to reject;
- **"not rejected":** the first failing step's CP interval lies entirely above its threshold, a determinate failure
  to reject.

Holm propagates the first failing step's state to every later step. So for every test and κ, the scan also reports its
**own** status at its position: interval below, straddling or above its own threshold. This separates a test's own
loss from one inherited through the step-down.

## 4. Range, resolution and stopping rule

- **Grid:** κ ∈ {0.00, 0.05, 0.10, …, 12.00}, 241 points, for families A and B (B only for κ ≥ 2) and for both
  readings.
  - **Why 12:** the L2 ratios (0.50–0.86 of the coarse-to-fine change in the last step) do not exclude a residual of
    several times the last step; for example, r/(1−r) = 6.1 at r = 0.86 under a geometric assumption. 12 is twice that.
- **Stopping rule:** none adaptive. The full grid is always evaluated, whatever the results, and the grid is not
  changed after any result is seen.
- **Refinement, the only adaptive step:**
  - **When:** for each pair of adjacent grid points between which any of the ten family decisions changes.
  - **Method:** bisection on κ, re-evaluating the full ten-test family at each midpoint, until the bracket width is
    ≤ 0.002 (at most 5 bisections per bracket).
  - **What is reported:** the final bracket [κ_lo, κ_hi] at which the decision is still / no longer the frozen one.
  - **Limit:** bisection assumes a single change inside a grid cell, and changes narrower than the 0.05 grid spacing
    elsewhere cannot be excluded. Both are stated with the result.
- **Beyond the range:** if a determinate rejection survives at κ = 12, its threshold is reported as "> 12" (a lower
  bound only).

## 5. Monotonicity: checked, not assumed

For every test and family, the scan records the grid points where the claim k (and p) decreases as κ increases, and
where a family decision returns to "rejected" after being lost. Thresholds are reported in two forms:
- the first loss on the grid (the smallest κ at which the decision is no longer "rejected");
- the full set of κ intervals where it is "rejected".

If the decisions are not monotone, no single threshold is quoted; the intervals are.

## 6. Reference reproductions (required before any threshold is quoted)

Each must agree exactly: k, B and decisions equal; p to rtol 1e-12.

- **Family A at κ = 2, reading F:** every claim p, k and B, and all ten decisions, against `joint-evaluate.json`
  (`tests.<G>.total/shape`, `decisions`).
- **Family B at κ = 3, reading F:** all ten decisions against `decisions_robust_kappa`, and the per-test robust p, k
  and B against `tests.<G>.total_robust/shape_robust`.
- **The same two checks, reading (a):** against `resolved-evaluate.json`.

Any disagreement stops the scan, and the disagreement is reported instead of thresholds.

## 7. Outputs and budget

- **Outputs:**
  - `publication/kappa/kappa_breakdown.py`, the scan;
  - `publication/kappa/KAPPA-RESULT-20261007.json`, every grid and refinement point with all ten claim p, k, B,
    own status and family decision;
  - `publication/kappa/RECORD-20261007-kappa-breakdown.md`, the report.
- **Budget:** local CPU only, ≤ 4 CPU core-hours in total (two readings × about 241 points × 8 κ-dependent null
  evaluations × about 1.4 s, plus refinements). No allocation, no cluster job, no new pseudo-experiment.

## 8. What the result can and cannot say (stated with every number)

It measures the **sensitivity of the frozen decisions to rescaling the frozen sub-fine-grid shift δ_M1**, i.e. how
large a multiple of the last refinement step, applied along that one direction, the decisions tolerate. It does not
measure:
- the convergence of the fine-grid null;
- the true residual below the fine grid, its direction, or the correct κ;
- shifts along any other direction;
- the adequacy of the detector or hadronic-response model.

It changes no frozen decision, no robustness label and no condition, and the residual remains "unmeasured,
potentially material" (amendment 8). It is a report-only sensitivity of the frozen calculation.
