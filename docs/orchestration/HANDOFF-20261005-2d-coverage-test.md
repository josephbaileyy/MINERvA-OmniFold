# Handoff: test whether the 2D statistical band covers a fixed truth (2026-10-05)

## Objective

Measure the frequentist coverage of the **production 2D statistical uncertainty band** for the
MEFHC (p_T, p_parallel) measurement, using closure toys scored against a **fixed, unfluctuated
truth**. Today the analysis note says no 2D coverage number is quoted. The paper says "its coverage
is untested". This run is meant to replace those statements with a measured result at its proper
scope, whether it passes or fails.

## Authorization (Joseph, 2026-10-05): this run is autonomous

Joseph asked for this test on 2026-10-05 and refreshed the NERSC sshproxy certificate. He starts
this session with `/goal` pointing at `GOAL-20261005-2d-coverage-test.txt`, which carries his
authorization in his own words. **That launch is his direct word for everything listed below. Do
not stop to ask for it again.**

### Granted

- **Compute.** Up to **60 CPU node-hours** on account `m3246`, including the pilot, retries and
  re-runs. Use regular, shared or debug QOS. Never use premium or overrun. The estimate is about 45:
  200 toys × ~0.22 node-h. One 5-iteration lgbm 2D unfold takes 13m24s on a 128-CPU node, per
  `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md` "Runtime budget". Charge this outside the s5p campaign's
  pool, and measure the account balance first.
- **Code.** Changes to the 2D toy, driver and scorer code on a new branch, with tests.
- **Records.** Commits, including the pre-registration record, ledger, STATUS and KNOWN_ISSUES rows,
  and receipts.
- **Pre-registration amendments.** Allowed after the pilot and before the full run, each recorded
  as a dated amendment.
- **Review.** Independent read-only review on claude-school (`claude -p --model claude-opus-5-5
  --effort high`) or with your own subagents. Codex needs Joseph's separate approval; don't use it.
- **Deliverables.** Note, paper and primer edits limited to the 2D coverage statements and what
  follows from them directly.
- **Publication.**
  - Push the branch and open a PR.
  - **Merge it into `main`** once all of these hold: `build_all.sh` reports `RESULT :: PASS`, all
    tests pass, and an independent recomputation reproduces the headline numbers.
  - Then sync, build and push the standalone note repository.

### Limits that still apply

- **The test measures** whether the production statistical band covers toy-to-toy scatter around a
  fixed truth at its nominal rate.
- **A result, pass or fail, cannot authorize:**
  - any change to the 2D central value, its estimator, or any adopted or quoted uncertainty;
  - any statement about systematic or total-uncertainty coverage;
  - any statement about the 5D products.
- A failure is a valid result. Record it as plainly as a pass.
- **Do not touch other work.** Leave alone the s5p campaign's worktree, jobs, state and budget; any
  other session's checkout; and note sections unrelated to coverage.
- **No post-hoc changes.** Never change the pre-registered criteria after any full-run result has
  been seen.
- **Stop and report** instead of improvising if:
  - a revised cost estimate exceeds 60 node-hours (or, before the full run, cut the toy count to the
    pre-registered minimum and record that as an amendment);
  - the NERSC certificate expires, since renewal needs Joseph's MFA;
  - the design turns out to need a change to production code that other results depend on;
  - a check fails twice after repair.
- The public origin is harvested continuously, so a push publishes. Push only through the gated
  merge path above, and stage files with explicit pathspecs. Never use `git add -A`.

## Read first (routes, in order)

1. `AGENTS.md`, `docs/CURRENT_WORK.md`.
2. `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md` and `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`. These hold
   the environment, the launcher rules and the runtime table. Follow their compute rules: fresh
   live-state check, direct scheduler observation, receipt-bound launchers.
3. What the note says now:
   - `docs/analysis-note/sec_validation.tex`, the paragraph labelled `sec:coverage`;
   - `docs/analysis-note/app_history.tex`, "From §sec:coverage, the 2D coverage test" (the withdrawn
     split-sample reading);
   - `docs/analysis-note/values.tex`, the comment on `\pullFrac`.
4. The production statistical band:
   - `VALIDATION_LEDGER.md` row `VL162`: 300 pure-Poisson replicas, `--seed 1`; per-bin median
     0.5494 %;
   - `docs/orchestration/state/note-boot-20261003/` (`boot_spreads.py` and its README) for the exact
     σ definitions;
   - App. A's bootstrap subsection (`sec:bootstrap` in `app_statmethods.tex`).
5. Design template, the 5D independent-truth test:
   - `docs/orchestration/OUTCOME-20260925-s5c-tier-s-futility-fail.md` and ledger `VL150`. Copy its
     discipline: predeclared criteria, a futility rule, a pilot.

## Existing pieces, and why they don't measure coverage

- `2d-unfolding/sbatch_coverage_toys_MEFHC_200.sh`: array `21-200%30`, 1 h, 128 CPU, regular QOS.
- `2d-unfolding/unfold_2d_omnifold_unbinned.py --closure --bootstrap-seed k`: the pseudo-data are
  weighted MC reco, and the truth marginal is written to `hTruthXSec2D`.
- `2d-unfolding/uq/coverage_toys.py` (the rollup).
- The defect: the MC bootstrap multiplies `w_truth`. The stored truth therefore fluctuates from toy
  to toy (all 205 reported bins), and σ was estimated from the same toys being scored. The result
  (68.71 %) checks Gaussianity; it is not coverage.

## Design: finalize and pre-register before any launch

1. **Fixed truth.** Store one unfluctuated truth marginal, identical in every toy, in the same
   cross-section units and binning as the unfolded output. Prove it is identical across two pilot
   toys.
2. **Fluctuate what the production band represents, and nothing else.** Find out exactly where the
   production bootstrap applies its Poisson(1) weights: data side only, or data and MC. Mirror that
   in the toys. State the mapping explicitly.
3. **Independence.** Decide whether the pseudo-data must be statistically independent of the MC
   used for training and the response (a split sample, as the 5D test did), and justify the choice.
   A same-sample design can bias coverage either way.
4. **Estimator.** Use lgbm with 5 iterations, which is the estimator the production statistical
   ensemble uses, not the `exact` backend. An `exact` central unfold takes about 19 h.
5. **Scoring.** Score against the production σ (`VL162`):
   - per-bin and pooled fractions with |U − T| ≤ σ and ≤ 2σ;
   - pull RMS;
   - intervals that respect bin correlations (resample toys, not bins);
   - a minimum toy count;
   - **pass, fail and futility criteria, written and committed before any full-run result is
     seen.**
6. **Positive control.** Show that the scorer flags miscoverage when the band is deliberately scaled
   (e.g. ×0.7 and ×1.3), on the real toy outputs, not on a synthetic fixture.
7. **Seeds.** No collision with production replicas or the old toys.
8. **Size.** A 2–3 toy pilot, then 200 toys.

## Steps

1. Read the routes. Draft the design and pre-registration as a record under `docs/orchestration/`
   on a new branch from current `origin/main`, in an isolated worktree. Commit it before launching.
2. Make the minimal code change: a truth-fixing option, or a new toy driver if cleaner. Add a test,
   and run the existing 2D tests.
3. Pilot. Check the fixed-truth identity, the units, the runtime, and the scorer on the pilot.
   Revise the cost estimate.
4. If the pilot passes its checks, launch the full array. No further approval is needed. Monitor it
   without tight polling loops, and keep receipts.
5. Score with the committed scorer. Get an independent recomputation of the headline numbers, from a
   fresh read-only reviewer or a second script.
6. Records:
   - a `VALIDATION_LEDGER.md` row with the **next free VL id**. Check across `origin/main` and every
     remote branch (`git grep -ohE 'VL[0-9]{3}' $(git for-each-ref --format='%(refname)' refs/remotes)`).
     The highest today is `VL163`; a VL161 collision happened on 2026-10-04.
   - `2D_OMNIFOLD_STUDY_STATUS.md`, and `KNOWN_ISSUES.md` if anything opens.
7. Deliverables:
   - In the note, update §6 `sec:coverage` with the result at its scope (statistical band only,
     fixed-truth closure toys). Add `values.tex` macros for the new numbers. Repository paths go in
     App. E tables, not the body. Superseded statements go to App. H.
   - Update the executive summary's "What is not claimed" coverage item, the paper's "its coverage
     is untested", and the primer's equivalent.
   - Run `bash build_all.sh` and require `RESULT :: PASS`.
   - Run the standalone sync (procedure: `docs/orchestration/HANDOFF-20260928-s5p-analysis-note-sync.md`
     "Next synchronization"). Record both remote heads.
8. Open a PR, and merge it once the gate in "Granted" (Publication) is met. Then do the standalone
   sync.

Note layout, since PR #13/#14:
- §6 is 2D-only.
- The five-axis validation is at the end of §8 (`sec:val-fiveaxis`).
- §9 is FPS and §10 is PET.
- App. E has `tab:prov-paths` and `tab:prov-trackers`.

## Report to Joseph at the end

- The pre-registered criteria, and the verdict against them.
- Coverage at 1σ and 2σ with intervals, and the positive-control result.
- Node-hours spent against the 60 cap.
- Commits, PR, and both remote heads.
- What the result does not license.
