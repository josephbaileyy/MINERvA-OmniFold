# IBUKT review handoff

MINERvA-OmniFold measures a two-dimensional muon cross section using unbinned OmniFold. Binned IBU on the same inputs differs from it; agreement of IBU with the published IBU result does not establish which method is closer to truth. IBUKT is a proposed paired known-truth recovery screen, implemented in Python with the existing ROOT, RooUnfold and LightGBM pipeline. Local tests use synthetic arrays; production inputs and fits require a separately approved CPU execution binding.

## Durable state and scope

- PR: https://github.com/josephbaileyy/MINERvA-OmniFold/pull/1215
- Branch: `lane/2d-ibukt-declaration-20261117-investigator`.
- Initial declaration/code: `d6ac2f29bd7f70068ba769d6341c46b729affd1c`.
- Revision 1 audit repairs: `9b21bb3fec06a1fd6923ace8a2764f019bfde064`.
- Revision 2 is the commit titled `[ibukt] Use engineering tolerance for nominal recovery`, which includes this handoff. Resolve its actual SHA from the PR and verify the remote head before work; do not assume the branch has stayed unchanged.
- Governing declaration: `docs/orchestration/state/2d-closeout/IBUKT-DECLARATION.md`. Read it in full after AGENTS.md, CLAUDE.md, the routed current work and campaign review.

These changes are not confirmed merged. Recover the branch from the repository remote and compare it with the specifications below. If any change is absent, reproduce it from this description only within an authorized repair request. No cluster connection or job was performed by this lane. No execution binding is approved. Manuscript sources are untouched.

The director requested the declaration/code and independent audit. The first audit of d6ac2f29 was PASS WITH FIXES; revision 1 repaired the launch, pricing, truth controls, tests and method labeling. The director then explicitly changed the noise-free nominal recovery gate from 1e-8 to the screen's 2% engineering tolerance before any execution. Revision 2 implements that instruction. Neither an earlier audit nor local tests admit these bytes for execution.

## What is fixed in the experiment

Seven truths: nominal, existing pinned GENIE+MEC and NuWro coarse ratio maps, a pT bump, a p_parallel tilt, and two opposite fractional-pT within-bin tilts. Five fixed Poisson realizations per truth give 35 paired recoveries. Learner seeds and simulation bank remain fixed; these are conditional data-counting draws, not independent MC partitions or detector-model validation. Both methods get the same refined target. C2 uses that same refinement, not a separate purity subtraction.

Both primary estimators use K=5. IBU K=10 is secondary in readout schema v2. The grid is the actual driver grid, 14 by 16, with 205 reporting cells. Per-cell signed recovery uses the fixed 2% tolerance and a descriptive five-draw noise guard; it does not select a global winner or supply coverage. Read the declaration's outcome-license table. In particular, this screen cannot separate missed-event regression from classifier capacity or identify the cause of the data difference.

`prepare` reproduces recorded E_R and C2, checks full-truth completeness, requires the two within-bin truth histograms to equal nominal to 1e-8, and requires each changed expected reco signal histogram to move. The noise-free nominal pair then uses the same refinement and unfolding code as the Poisson pairs. Revision 2 requires abs(estimate/truth - 1) <= 0.02 in every reported cell for both primary methods, without a noise guard. It records the tolerance and maximum residuals, and each Poisson pair rechecks the control product. The exact integral identity retains 1e-8. Existing recorded-input equality controls remain unchanged.

## Launch and resource contract

J1's 910-second wall was the relevant pricing evidence; packed per-unfold charge shares were not lane wall times. The proposed screen allocation is one exclusive CPU node with `--time=05:15:00`. Steps use `srun -n1 -c 64 --exact --mem=121920M --mem-bind=local`, with no step-level exclusive/node request. Each pair asserts 64 CPUs of affinity. At most two steps run concurrently.

The total cap remains 5.90 CPU node-hours, including failed attempts and controls. Screen admission reserves 5.25 plus 0.10 for scoring, so prior spend/reservations must be <=0.55. Individual stage maxima cannot all be spent. After the noise-free control, nominal-0 is timed and retained among the 35. The remaining 34 are refused unless 18 measured lane walls fit both the remaining allocation time and total cap, with scoring and a minute of overhead reserved. A stopped or partial ensemble cannot be scored; no automatic retry or reduced ensemble is authorized.

Before any future connect, obtain the director's approval on the exact script SHA and the required cov2d/tier3-design fence acknowledgments. Follow the routed rules: sacct only, protected reads through O_NOATIME, fresh scratch writes, no CFS writes, CPU only, guarded imports. Contact the director for coordination; no coauthor contact is authorized.

## Verification and next steps

Revision 2's local suite has 37 passing tests. It includes 1% nominal recovery acceptance, both signs outside 2% rejection, unchanged strict integral identity, planted control failures, exact signed signal weights, all seeds/settings, multi-cell conservation, real ratio-map indexing, shared targets and budget refusals. Re-run the focused suite after code changes:

`python -m pytest -q 2d-unfolding/ibukt/test_ibukt.py`

Use an external local environment with NumPy and pytest; ROOT fits and Linux O_NOATIME paths remain unexecuted. Run the repository hooks for staged changes, and check CI on the actual remote head. The earlier import-path suites passed 17 tests and 27 subtests; neither revision changes import-path insertion.

1. Confirm the PR head, working-tree cleanliness, CI and latest director instructions.
2. Tell the director the lane has transferred; receive the independent review of revision 2. Address only concrete authorized findings.
3. Prepare an execution binding only when instructed. A clean audit is not itself cluster approval.
4. Preserve the current estimator settings and thresholds until a separately reviewed amendment exists.

Do not revive the 1e-8 fitted-recovery gate, the five-hour launch, step-level exclusive packing, or the packed-share runtime estimate. Weighted missed-event regression and oracle interventions stay deferred: tier3-design coordinated the RSN/T3 definitions (W uses w_push*w_truth; the miss oracle predicts r/w_push), but those arms have no implementation/execution authority here. Capacity and iteration interventions also remain outside the current screen.

Use explicit git staging paths; never stash, rebase or force-push. Work in an isolated task worktree with one active writer, never the shared checkout. Do not edit the paper or note. The repository's front door and generated views are routing surfaces, not scientific evidence or compute authorization.
