# Review disposition: PET finalists vs GBDT on existing outputs

**Reviewer.** One fresh, read-only, independent Claude subagent working under `REVIEW_BRIEF-20261005.md`. Cycle 1
reviewed a clean detached worktree at `2b62c017`. The reviewer wrote only to a scratch directory outside every checkout,
contacted no cluster, fitted nothing, and left both checkouts clean. Its output is restated here by the owner; numbers
are quoted exactly.

**Budget.** At most two focused cycles.

## Cycle 1 verdict, quoted

> The paired numbers reproduce exactly. Pairing, budget and scope are compliant. A repair is needed before the P0
> recommendation is relied on: the comparator is described as stronger than the evidence shows, P0's cap and its run
> order conflict, and the cost model has one formula error. Nothing found overturns the paired comparison.

**Reproduced independently, all at |diff| = 0 against `comparison.json`, with the reviewer's own code:**

- the E0, E4 and E5 means;
- every paired difference at k = 3, 7 and 10, with n, the PET > GBDT counts and the bank-effect bounds;
- B2, B3 and B4;
- all 21 library cases;
- the per-bin bias and MSE splits;
- the weight statistics.

**Also confirmed:**

- all 352 replicate digests, and 14,784 injected per-bin vectors identical to PET's;
- every run listed COMPLETE in the look-1 record, with no RB or S5 runs;
- `kF0` = 7;
- the control refit;
- the ledger: 5.30627 charged and 4.42150 CPU core-h, never more than 2 concurrent tasks, plan order 352/352;
- the goal and handoff byte-identical to their originals;
- the diff confined to this directory.

## Findings and dispositions

| # | finding (operand at `2b62c017`) | disposition | evidence of the repair |
|---|---|---|---|
| 1 | P0's cap (125) conflicted with its stop (a) and its order. The NuWro closures that feed stop (d) ran last and would be cut first. | **Repaired.** New order: dev, then NuWro, then null closures, then the nominals, then an optional 10 M timing run. Stop (a) is now 1.5× the projection (11 A100-h), at which items 1–4 still fit. The cap is 165 A100-h. | REPORT §8 |
| 2 | The comparator was described as stronger than the evidence shows. On the same DEV units, binned IBU (0.945 / 0.902) and AUSSIE λ = 0 (0.870 / 0.919) beat this GBDT on the 1D tilt, so PET's lead is over this HGB OmniFold. | **Accepted; repaired.** The wording is softened in §0, §3, §5 and §9. The IBU and AUSSIE DEV context is added, IBU is added to P0's matched baselines, and the GBDT is kept as the generator-robust reference. Running IBU on FB is not done: the goal authorizes only GBDT fitting. | REPORT §0, §3, §5, §8, §9 |
| 3 | Every route was priced at a 2 M-row prior without saying so; at 10 M, costs are about 4× higher. | **Repaired.** The assumption is stated, the 10 M multiplier and totals are given, a 10 M timing unfolding is added to P0, and the prior size is made a P1 design input. | REPORT §7.2, §7.3, §8 |
| 4 | The cost model's step-1 row count was wrong. It uses all MC prior rows plus the reco-passing data side (851,831 = 600,130 + 251,701). | **Repaired** in `pgc_costs.py` and rerun. At 2 M, H2 is 7.32 and L128 7.12 A100-h (the reviewer's values); every figure using u is updated. | `results/costs.json` |
| 5 | The "muon-scale lead +0.135" mostly restated the tilt gain. | **Repaired.** R2 is reported as an E8 contrast, like R1: H2 − GBDT +0.016 [−0.005, 0.037], L128 − GBDT +0.028 [0.013, 0.043]. `pgc_compare` now computes E8 for every response case, with paired differences. | REPORT §0, §4.3, §6 |
| 6 | P1's unfolding count was never derived. | **Repaired.** P1 is priced as R4's 720 u calibration ensemble. R5 is now ≈ 5.7–7.9 k against ≈ 8.1–9.7 k for comparison-first. The reviewer notes the skip-R1 argument holds either way. | REPORT §7.3 |
| 7 | The "with a margin" bank-bound criterion was undeclared, and it was inconsistent with the E1-low wording. | **Repaired.** Every lower limit exceeds its bound except L128 E1 low; the two small margins are named. | REPORT §4.1 |
| 8 | The six-member "summed RMS" was actually Σ RMS². | **Repaired:** relabelled as summed MSE. | REPORT §4.2 |
| 9 | The D4d n-down label "injection near the floor" was wrong for its natural histogram. | **Repaired.** | REPORT §4.3 |
| 10 | Overstated wording: "equals H2", "2.5×", "low-variance". | **Repaired** to "level with" plus the paired Δ, ratios of small R values, and "small residual and DEV seed spread". | REPORT |
| 11 | Reproducing the study fit was presented as validating the cost model, but the check is circular. | **Repaired:** it is now called a consistency check. Job 56563761 is named as the one independent reference: the model gives ≈ 2.5 A100-h against ≈ 3 measured. | `pgc_costs.py`, REPORT §7.2 |
| 12 | The frozen plan's p99.9 label ("of w_truth × push") was wrong: the value is p99.9 of the push. | **Erratum recorded.** The frozen plan is not edited; the report gives the correct label. | REPORT §4.3 |
| 13 | Figure 3 mixed s.e. bars for the GBDT with 95 % bands for PET. | **Repaired:** both use 95 % t intervals. | `pgc_plots.py`, `results/figures/fig3_*` |
| 14 | The runner commit `44d135c2` landed about 7 s after the first fit began, and the runlog does not record the runner commit. | **Recorded.** The executed bytes equal `44d135c2`. The reviewer checked that the R2 repair leaves non-R2 behaviour unchanged. | `RUN_LOG.md` |
| 15 | The disposition file was missing, and the allocation number had no source. | **Repaired:** this file, plus the citation `resources/README.md:25` at `bc356b0c`. | REPORT §7.2, §10 |

**Could not verify (reviewer).**

- the push time of `5f9c5a99`, and the absence of fitting outside the ledger;
- the uncommitted per-task outputs and the copied cluster files;
- the PET-side R2 inputs, which are not stored;
- the runtime of job 56563761 and the current allocation;
- whether any collaborator message was sent;
- the governance status of the proposed real-data nominals;
- 15 of the 16 DEV re-scorings (one was spot-checked);
- the test suite, which was not run to avoid writing into the worktree.

The owner adds two facts:

- The push of `5f9c5a99` was recorded by the push output at 18:12 UTC.
- No collaborator message was sent.

## Cycle 2

{{CYCLE2}}
