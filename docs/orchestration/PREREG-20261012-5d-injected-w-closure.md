# Pre-registration: corrected 5D injected-W-shape closure (2026-10-12)

**Status: PRE-REGISTERED, committed and pushed before submission.** §3–§5 do not change after the
job starts. Any deviation is recorded in the outcome record as a deviation, not edited in here.

Authorization: Joseph, 2026-10-12 ("just do the injected shape closure"), also within his standing
approval for single jobs under 12 h (`standing-compute-approval-12h`). One CPU job on `m3246`,
`shared` QOS, walltime cap 6 h; expected well under one node-hour.

## 1. Why this test, and what an answer cannot license

The 2026-06-07 5D "injected-W closure" (job `54062313`, run log commit `aecd0d22`) used the driver's
default bump centre `--closure-center 0.3` with sigma 0.15 GeV. Physical W is above about 0.94 GeV,
so the bump's weight change was below 1e-8 (the run printed `injected mean factor=1.0000`). It was a
null self-closure, recorded as a pass because no threshold was fixed in advance and nothing checked
that the injection was nonzero (note Sec. 5.1, Table 4; PR #102, #103). No 5D injected-shape
recovery test exists. This job supplies one.

**Scope.** Signal-only closure as the driver's `--closure` mode defines it: pseudo-data are the
simulated signal reco events (`pass_reco & pass_truth`), completeness is 1, and the background and
its subtraction are outside the test. The detector response is the simulated MINERvA response on
both sides. A PASS shows only that one smooth W bump at the Delta peak is recovered in the W
marginal. It does not test generator-shaped deformations (16–74% residuals, note Sec. 9), joint
(E_avail, W) accuracy, coverage, response mismatch or background. It changes no central value,
covariance or quoted number. Restoring a 5D injected-shape claim in the article is Joseph's
decision.

**Campaign choice (`CAMPAIGN-REVIEW-20260929.md`).** Owner: this Opus 5.5 lane, end to end. No
independent reviewer: a single closure with a frozen rule and a reused instrument. This is stated as
a limitation. Terminal outcomes: PASS, FAIL or INVALID, each recorded. Repair budget: at most one
resubmission, for an infrastructure failure only (node failure, preemption, TIMEOUT before any
output). None for a scientific result.

## 2. Inputs and code

- Driver: `nd-unfolding/unfold_nd_omnifold_unbinned.py` at this commit. It runs from a dedicated
  Perlmutter worktree `/pscratch/sd/j/josephrb/MINERvA-OmniFold-wclosure-20261012` pinned to this
  commit, under `mnv_guarded_run.py --expect-root` (OI-136).
- Launcher: `nd-unfolding/sbatch_closure_5d_wbump_20261012.sh`.
- Omnifile: `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_MEFHC.root`
  (4,825,716,683 B). It is the 5D input whose sha256 `b6d2651c…` the s5c campaign recorded
  (`state/s5c/p2/bkg_dump_step.log`). The job records its sha256.
- Flux MC: `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root`.
- Production flags (as in `sbatch_eavail_scale_study.sh`'s 5D control and `run_p4_unfold_std.sh`):
  `--axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed 42 --bkg-mode purity`.
  With `--closure`, `--bkg-mode purity` does not act on the pseudo-data.

## 3. Arms

| arm | added flags | role |
|---|---|---|
| I | `--closure --closure-reweight-axis W --closure-amplitude 0.3 --closure-center 1.23 --closure-sigma 0.15` | injected: truth weights × (1 + 0.3 exp(−((W−1.23)/0.15)²)) on pseudo-data and reference |
| N | `--closure` | plain closure; its `hClosureRefND` is the nominal truth (`nom`) and its residual is a control |

## 4. Statistics and rules

Scored by `nd-unfolding/closure_5d_w_bottom_line.py`.

1. **Positive control (validity).** The injected arm's truth-pass mean weight factor, parsed from
   the driver's `injected mean factor=` line, must be **≥ 1.01**. Otherwise the verdict is
   **INVALID**. The per-bin W-marginal injected deviation `ref/nom − 1` is reported.
2. **Primary (PASS/FAIL).** The statistic is the bottom-line recovery ratio from
   `2d-unfolding/uq/bottom_line_test.py`. Its computation is moved unchanged into
   `bottom_line_ratio()` so that the 5D score calls the same code as the 2D and 3D recoveries:
   `RMS((unf−ref)/ref) / RMS((ref−nom)/nom)` over the feature bins, those whose
   `|ref/nom − 1|` exceeds the all-bin injected RMS. It is applied to the W-marginal projections
   (driver's `project_axis`) of the injected arm's unfolded `hXSecND` and reference
   `hClosureRefND`, and of arm N's `hClosureRefND`. **PASS iff ratio < 0.20**, the instrument's
   default tolerance (residual at least 5× smaller than the feature). One deviation from the 3D
   operand: 3D's `nom` was the data-unfolded 3D projection; here `nom` is the nominal MC truth,
   which is the instrument's documented definition `(hTruthRew − hTruth)/hTruth`.
3. **Reported, no rule.** The 5D per-bin `unf/ref` median, std and max|dev| for both arms, as the
   driver prints them.
4. **Secondary, descriptive only.** The joint (E_avail, W) projection (7 × 6 = 42 cells, the grid of
   the note's (E_avail, W) results): `unf/ref` median and max|dev|, the highest-W column, and the
   injected map `ref/nom`. These cells carry no pass/fail.

## 5. Recording

The outcome record carries CITABLE FOR / NOT CITABLE FOR, with a `VALIDATION_LEDGER.md` row, an
`ND_OMNIFOLD_RUN_LOG.md` entry (job id, `sacct` State/Elapsed, sha, input digests, numbers),
corrections to the 5D rows of `ND_OMNIFOLD_STATUS.md` and `AGENTS.md`, and the note's Table 4
"Injected W" row. Outputs go to `/pscratch/sd/j/josephrb/wclosure_5d_20261012/` with `SHA256SUMS`;
the score JSON is committed under `docs/orchestration/state/wclosure-5d-20261012/`.
