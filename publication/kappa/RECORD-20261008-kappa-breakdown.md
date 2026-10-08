# Report-only κ-breakdown of the joint-test decisions: result (2026-10-08)

**This measures the sensitivity of the frozen decisions to rescaling the frozen sub-fine-grid shift δ_M1, along that
one direction only. It does not measure:**
- the convergence of the fine-grid null;
- the size or direction of the true residual below the fine grid, or which κ is correct;
- the effect of any other shift;
- the adequacy of the detector or hadronic-response model.

**No frozen primary decision, robustness label or condition changes.** The decisions remain amendment 7's κ = 2
decisions as recorded (`RECORD-20261005`, `joint-evaluate.json` `b9604502…`). The sub-fine residual remains
"unmeasured, potentially material" (amendment 8).

**CITABLE FOR:** the κ at which each of the ten Holm-with-determinacy decisions stops being a determinate rejection
when the M1 variants are set to ±κ·δ_M1. Each test's own status is reported, and both the frozen reading and the
recovery-union reading are given.
**NOT CITABLE FOR:** any of the exclusions above, a revised decision, an uncertainty, or a measurement.

| | |
|---|---|
| authority | Joseph, 2026-10-07 (verbatim in the spec) |
| specification | `SPEC-20261007-kappa-breakdown.md`, frozen and pushed at **`b75af4f4`** before any κ other than 2 and 3 was evaluated |
| code | `kappa_breakdown.py` (`30078dc3`, sha256 `a4196f7b…`). It imports the release replay functions (`publication/release/replay_inference.py`, sha256 `41f4af05…`, checked at run time) unchanged. |
| inputs | RC4 sufficient inputs only, every file verified against `docs/publication/release/RC4-SHA256SUMS.txt`: frozen `7bd019c6…`, recovery union `6ffed091…`. No new pseudo-experiment. |
| outputs | `KAPPA-RESULT-20261007-frozen.json` (sha256 `c33b7b53…`), `KAPPA-RESULT-20261007-recovery-union.json` (`b7e0b3e9…`), `KAPPA-SUMMARY-20261007.txt` (`ef9270b1…`) |
| cost | local macOS, Python 3.12.2 / numpy 1.26.4 / scipy 1.15.2. 1,010 s and 1,045 s wall time; 1.12 CPU core-hours in total against the spec's ≤ 4. No allocation. |
| independent reproduction | **AGREE.** A fresh agent wrote its own claim rule, Holm-with-determinacy and Clopper–Pearson code from the frozen modules and contract. It did not read the scan, the replay code or these results. Its code and outputs are in `repro/`, starting with `REPORT.md`; code sha256 `0ff74400…`. |

## 1. Reference reproductions (spec §6): all exact

- **Scan:** family A at κ = 2 reproduces every claim p, k, B and all ten decisions of `joint-evaluate.json`, and of
  `resolved-evaluate.json` for the union reading. Family B at κ = 3 reproduces `decisions_robust_kappa` and every
  `total_robust`/`shape_robust` p, k and B. There were 0 differences at rtol 1e-12 in either reading.
- **Reproducer:** the same four checks, with 0 differences.
  - It added two checks of its own. T_obs and every recorded variant's k match exactly, including m1±2 and m1±3.
  - The null medians and SDs of every variant match the frozen evaluator to 2.1e-14 relative. Because these depend
    on every pseudo-experiment's residual draw, this tests the draw convention, which k = 0 alone cannot.
- **Scan vs reproducer:**
  - 220 test-points at the reference and bracket-end κ: k, B, p, threshold, decision and own status, 0 differences.
  - 250 claim-k values on κ = 0, 0.5, …, 12: 0 differences.

## 2. Result (frozen reading; family A, with family B identical at every κ ≥ 2)

**Ranges.** Decisions are constant between grid points. Brackets are given at the spec's refinement resolution
(≤ 0.002) where the family decision changes, and at grid resolution (0.05) otherwise.

| test | k at κ = 2 / 3 | family decision stops being a determinate rejection | how | own interval first leaves "below" its threshold | own interval first lies **above** its threshold (determinate failure to reject) |
|---|---|---|---|---|---|
| GENIE 2.12.10 + MEC, shape | 0 / 0 | **κ ∈ (5.2547, 5.2563]** → undetermined | **own** (k 22 → 23) | (5.2547, 5.2563] | (5.6641, 5.6656] |
| GENIE 2.12.10 CV, shape | 0 / 0 | κ ∈ (5.2547, 5.2563] → undetermined | **inherited** through the step-down; own still below (k = 27) | (5.65, 5.6625] (grid) | (5.95, 6.00] (grid) |
| NuWro 21.09, shape | 1 / 2 | κ ∈ (6.4781, 6.4797] → undetermined | own | (6.4781, 6.4797] | (7.8406, 7.8422] |
| NuWro 21.09, total | 0 / 0 | κ ∈ (6.4781, 6.4797] → undetermined | **inherited** (from NuWro shape) | (6.50, 6.55] (grid) | (6.80, 6.85] (grid) |
| GiBUU 2019, total | 0 / 0 | κ ∈ (7.2109, 7.2125] → undetermined | own | (7.2109, 7.2125] | (7.50, 7.55] (grid) |
| GENIE 2.12.10 CV, total | 0 / 0 | κ ∈ (8.4594, 8.4609] → undetermined | own | (8.4594, 8.4609] | (8.6656, 8.6672] |
| GENIE 2.12.10 + MEC, total | 0 / 0 | κ ∈ (10.3281, 10.3297] → undetermined | own | (10.3281, 10.3297] | (10.5344, 10.5359] |
| GiBUU 2019, shape | 0 / 0 | **not lost for κ ≤ 12** (threshold > 12; k = 1 at κ = 12) | — | — | — |
| MINERvA Tune v1, total and shape | 0 / 0 | **κ-independent:** this null has no M1 variant (ρ = 1), so its rejections are as frozen | — | — | — |

**Reading:**
- All ten decisions are determinate rejections for every κ ≤ 5.2547. The first change is between 5.2547 and 5.2563,
  about 2.6 times the claim multiplier (κ = 2) and 1.75 times the robustness multiplier (κ = 3).
- The first loss is GENIE + MEC shape, on its own interval. GENIE CV shape loses its rejection at the same κ, but
  only through the Holm step-down.
- The first determinate failure to reject is GENIE + MEC shape at κ ∈ (5.6641, 5.6656].
- By κ ≈ 10.33, every κ-dependent test except GiBUU shape has lost its determinate rejection.
- **Context:** GENIE + MEC shape's claim k goes from 0 at κ = 3 to 22 at κ = 5.25. This is consistent with the
  4.6-unit margin of the closest recovered draw at κ = 3: many null draws cross T_obs soon after κ = 3. The rejection
  survives until k ≈ 23 because the determinacy rule compares the whole CP interval with its Holm threshold.

**Recovery-union reading (report-only, secondary).** It differs from the frozen reading in three places:
- the first change comes earlier, at (5.1688, 5.1703];
- the NuWro tests change later;
- NuWro total now loses on its own interval and before NuWro shape.

The other thresholds are the same:

| test | union: family decision stops being a determinate rejection |
|---|---|
| GENIE + MEC shape (own) and GENIE CV shape (inherited) | (5.1688, 5.1703] |
| NuWro total | (6.5406, 6.5422], own |
| NuWro shape | (6.8453, 6.8469], own |
| GiBUU total | (7.2109, 7.2125] |
| GENIE CV total | (8.4594, 8.4609] |
| GENIE + MEC total | (10.3281, 10.3297] |
| GiBUU shape | > 12 |
| Tune v1 | κ-independent |

## 3. Monotonicity (spec §5): checked

- **Claim k is non-decreasing in κ** for every test, at every one of the 286 (frozen) and 291 (union) evaluated
  points, grid and refinement together. The reproducer confirms this on its own 0.5-step grid.
- **No test regains a determinate rejection once lost**, in either family or reading. Each test's rejected set is
  the single interval [0, κ*].
- **Not monotone:** the family state of a test that has already lost its rejection alternates between
  "undetermined" and "not rejected" as κ changes the Holm ordering. The state carried down the step-down is set by
  whichever test fails first. Two consequences follow:
  - a single threshold for the family label "not rejected" does not exist;
  - the determinate-failure column above uses each test's **own** interval instead.

  The reproducer independently found and explained the same alternation.
- **Families A and B are identical:** because claim p never decreases with κ, the κ = 2 variants added in family B
  never set the maximum.

## 4. Limits stated with the result

- **Resolution:** brackets refined by bisection assume a single change inside each 0.05 grid cell. Changes narrower
  than the grid spacing elsewhere cannot be excluded, although k is monotone at every evaluated point.
- **Range:** the range stops at κ = 12. For GiBUU shape and the two Tune v1 tests only "> 12" or "κ-independent" is
  known.
- **Direction:** only ±κ·δ_M1 along the frozen direction was scanned. A real residual need not lie along δ_M1, so
  the true sub-fine shape could move the null differently.
- **No mapping from κ to a residual size:** this record does not translate any κ into a convergence statement. The
  frozen design's assumed residual of one to three times the last step (κ = 2 central, κ = 3 robust) is an
  assumption, and the L2 ratios do not exclude a larger residual (REVIEW-20261007 B2).
- **Both readings use the frozen process-shift variants and the frozen metric.** Nothing else was varied.
- **Inputs:** the RC4 copy given to the reproducer had its four `code/*.py` files deliberately removed, for
  independence. Every data and expected file it used verifies against `RC4-SHA256SUMS`.

## 5. Proposed article wording (NOT applied; Joseph's decision)

The article (`paper_body.tex`, Sec. VI.C) currently says: "how far beyond that the decisions would hold has not been
evaluated". Proposed replacement, with a new `@misc` citation to this record:

> "A report-only scan along the same direction~\cite{JointTestKappa2026} finds all ten decisions to be determinate
> rejections for multipliers up to 5.25 (5.17 with the recovered pseudo-experiments added); beyond that the
> GENIE~+~MEC shape test loses determinate rejection first, and by 10.3 every test except GiBUU's shape test and
> the two Tune~v1 tests has done so. The scan measures sensitivity along $\delta_{\mathrm{M1}}$ only, not the
> convergence of the null or the size of the residual."

Applying it would also add the record to the data-availability list of numbers the release does not itself
recompute. It is reproducible from RC4 with this record's code, but not by `verify_rc.py`.
