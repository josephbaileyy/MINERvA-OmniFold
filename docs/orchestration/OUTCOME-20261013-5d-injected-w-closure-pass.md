# Outcome: corrected 5D injected-W-shape closure — PASS, narrow margin (2026-10-13)

Plan: [`PREREG-20261012-5d-injected-w-closure.md`](PREREG-20261012-5d-injected-w-closure.md),
committed at `b11ff40d` on 2026-10-12 15:28:41 PT and pushed before submission. The job was
submitted at 15:30:48 PT. The plan was not edited after submission. Ledger: `VL176`.
Evidence: [`state/wclosure-5d-20261012/`](state/wclosure-5d-20261012/).

## CITABLE FOR

- The production 5D estimator (lgbm, five iterations, seed 42, `--use-weights`) recovers a +30%
  Gaussian bump in truth W at 1.23 GeV (σ 0.15 GeV) in the **W marginal**. In the one feature bin
  (W 1.1–1.4 GeV) the injected deviation is 23.1% and the residual 4.2%, a bottom-line ratio of
  **0.180** against the predeclared **0.20**. Verdict **PASS**.
- That the June 2026 5D "injected-W" result (job `54062313`) is superseded. It was a null test.

## NOT CITABLE FOR

- Joint (E_avail, W) recovery. Cells in the peak W column come out 2.2–9.4% low, and no rule
  was set for them.
- Generator-shaped or correlated deformations, coverage, response mismatch, or background. The
  test is signal-only (`--closure`: pseudo-data are simulated signal reco, completeness 1).
- A margin. The ratio rests on one feature bin, and its distance from the threshold (0.020) was
  not compared with seed-to-seed scatter. No repeat was run.
- Any central value, covariance, uncertainty or significance. None changes.
- Wording in the article. `main_paper.tex` and `paper_body.tex` still limit the injected-shape
  claim to 3D/4D. Whether to add 5D is Joseph's decision.

## Run

| field | value |
|---|---|
| job | `59719296`, `sacct` State **COMPLETED**, exit 0:0, Elapsed **00:37:34** (start 02:06:36, end 02:44:10 PT 2026-10-13), 52 CPUs, `shared_milan_ss11`, `nid004103`, CPUTime 1-08:33:28 |
| code | `/pscratch/sd/j/josephrb/MINERvA-OmniFold-wclosure-20261012` detached at `b11ff40d`. Each step ran under `mnv_guarded_run.py --expect-root`, and the inventories show 0 modules outside it |
| omnifile | `runEventLoopOmniFold_5D_MEFHC.root` sha256 `b6d2651c…5175a` (same as s5c) |
| flux MC | `runEventLoopMC_MEFHC.root` sha256 `d40aea69…f316` |
| outputs | injected `2ece46ab…2ae3`, null `29038e1b…0555`, score JSON `5141558b…6888` (scratch and committed copy agree) |
| retries | none |

## Numbers (from `closure_5d_w_bottom_line.json` and the driver logs)

**Positive control.** The injected truth-pass mean weight factor is **1.0529**, at or above
1.01, so it is OK. The 5D integral ratio injected/null is 2.847e-38 / 2.706e-38 = 1.052, which
agrees.

Each W bin (edges 0, 1.1, 1.4, 1.8, 2.2, 3.0, 100 GeV) has an injected deviation ref/nom − 1 and an
unfolded/reference ratio (the driver's `W 1D ratios`):

| W bin (GeV) | injected | unfolded/reference |
|---|---|---|
| 0–1.1 | +3.81% | 1.031 |
| 1.1–1.4 | **+23.10%** | **0.958** |
| 1.4–1.8 | +1.11% | 1.027 |
| 1.8–2.2 | 8.5e-9 | 0.998 |
| 2.2–3.0 | 0 | 1.000 |
| 3.0–100 | 0 | 1.000 |

**Primary statistic.** `bottom_line_ratio` from `2d-unfolding/uq/bottom_line_test.py` is the
instrument behind the 2D 0.098 and the 3D 0.102. Over all bins, injected RMS is 9.57% and
residual RMS 2.38% (ratio 0.249, reported but not part of the rule). Only bin 1.1–1.4 has
|injected| above 9.57%, so it is the single feature bin. There injected is 23.10%, residual
4.16%, and the **ratio is 0.1799, under 0.20: PASS**. The ratio was recomputed by hand from the
per-bin values: 0.04155 / 0.23102 = 0.1799.

**5D per-bin** (`unf/ref`, 10,694 bins): the injected arm has median 1.0070, std 0.0371 and
max|dev| 0.1515. The null arm is exactly 1.0000, 0.0000 and 0.0000. The plain closure returns the
prior to the last printed digit, so by itself it has no power. Here it only supplies `nom`.

**Secondary, descriptive only.** Over the 42 joint (E_avail, W) cells, the median `unf/ref` is
1.0093 and the max|dev| 0.094. The peak column (W 1.1–1.4) runs 0.906, 0.968, 0.978, 0.956,
0.920, 0.917, 0.915 from the lowest E_avail bin up, against injected 1.21–1.25. The highest-W
column (W > 3 GeV) runs 1.007, 1.011, 1.018, 1.012, 0.999, 0.999, 1.000.

## Reading

Of the 23.1% injected excess in the peak bin, the unfold recovers 18.0%, about 78%. Some of the
remainder shows up as excess in the two neighbouring W bins: unfolded/nominal is 1.070 against
1.038 injected below the peak, and 1.038 against 1.011 above it. This pattern fits partial
retention of the prior plus migration across W bins at five iterations. The mechanism was not
tested. The 3D E_avail analogue recovered to 0.102. The 5D W ratio is about 1.8 times worse and
close to the threshold.

**Would this support restoring a 5D injected-shape claim?** It would support a narrow one: "the
five-observable central value recovers a smooth injected W bump in the W marginal (ratio 0.18,
threshold 0.20)". It would not support a claim about joint cells or about the generator-shaped
deformations that bound the 5D result. Whether to say even the narrow claim in the article is
Joseph's call.

## Deviations and incidents

- The operand of the 3D instrument differs, as the plan declared in §4.2. Here `nom` is the
  nominal MC truth, not a data unfold.
- My first background poll loop exited at once, apparently because `sleep` was refused in the
  background shell. It reported PENDING as its final line. The job was then watched with a
  `Monitor` on `sacct` State. No job state was affected.
- No independent reviewer. This is stated in the plan as a limitation.
