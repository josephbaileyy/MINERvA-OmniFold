# IBUKT review handoff

MINERvA-OmniFold measures a two-dimensional muon cross section using unbinned OmniFold. Binned IBU on the same inputs differs from it; agreement of IBU with the published IBU result does not establish which method is closer to truth. IBUKT is a proposed paired known-truth recovery screen, implemented in Python with the existing ROOT, RooUnfold and LightGBM pipeline. Local tests use synthetic arrays; production inputs and fits require a separately approved CPU execution binding.

## Durable state and scope

- PR: https://github.com/josephbaileyy/MINERvA-OmniFold/pull/1215
- Branch: `lane/2d-ibukt-declaration-20261117-investigator`.
- Initial declaration/code: `d6ac2f29bd7f70068ba769d6341c46b729affd1c`.
- Revision 1 audit repairs: `9b21bb3fec06a1fd6923ace8a2764f019bfde064`.
- Revision 2: `6e8a1bc5fbc8fa23f9c6007819b222c72e746e7c`, `[ibukt] Use engineering tolerance for nominal recovery`.
- Revision 3 is the commit titled `[ibukt] Verify control and bank identities before scoring`. Resolve its SHA from the PR and verify the remote head before work; do not assume the branch has stayed unchanged.
- Governing declaration: `docs/orchestration/state/2d-closeout/IBUKT-DECLARATION.md`. Read it in full after AGENTS.md, CLAUDE.md, the routed current work and campaign review.

These changes are not confirmed merged. Recover the branch from the repository remote and compare it with the specifications below. If any change is absent, reproduce it from this description only within an authorized repair request. No cluster connection or job was performed by this lane. No execution binding is approved. Manuscript sources are untouched.

The director requested the declaration/code and independent audit. The first audit of d6ac2f29 was PASS WITH FIXES; revision 1 repaired the launch, pricing, truth controls, tests and method labeling. The director then explicitly changed the noise-free nominal recovery gate from 1e-8 to the screen's 2% engineering tolerance before any execution. Revision 2 implements that instruction. Its independent audits returned PASS and PASS WITH FIXES. Revision 3 repairs the latter's two scorer findings. Neither an earlier audit nor local tests admit these bytes for execution.

The lane remains the single writer; independent reviewers remain read-only. The next decision is whether the two scorer findings are closed on the exact revision-3 bytes. One focused confirmation read is next, with reassessment of material unresolved issues after that. No cluster connection or run is authorized.

## What is fixed in the experiment

Seven truths: nominal, existing pinned GENIE+MEC and NuWro coarse ratio maps, a pT bump, a p_parallel tilt, and two opposite fractional-pT within-bin tilts. Five fixed Poisson realizations per truth give 35 paired recoveries. Learner seeds and simulation bank remain fixed; these are conditional data-counting draws, not independent MC partitions or detector-model validation. Both methods get the same refined target. C2 uses that same refinement, not a separate purity subtraction.

Both primary estimators use K=5. IBU K=10 is secondary in readout schema v2. The grid is the actual driver grid, 14 by 16, with 205 reporting cells. Per-cell signed recovery uses the fixed 2% tolerance and a descriptive five-draw noise guard; it does not select a global winner or supply coverage. Read the declaration's outcome-license table. In particular, this screen cannot separate missed-event regression from classifier capacity or identify the cause of the data difference.

`prepare` reproduces recorded E_R and C2, checks full-truth completeness, requires the two within-bin truth histograms to equal nominal to 1e-8, and requires each changed expected reco signal histogram to move. The noise-free nominal pair then uses the same refinement and unfolding code as the Poisson pairs. Revision 2 requires abs(estimate/truth - 1) <= 0.02 in every reported cell for both primary methods, without a noise guard. It records the tolerance and maximum residuals, and each Poisson pair rechecks the control product. The exact integral identity retains 1e-8. Existing recorded-input equality controls remain unchanged.

## Launch and resource contract

J1's 910-second wall was the relevant pricing evidence; packed per-unfold charge shares were not lane wall times. The proposed screen allocation is one exclusive CPU node with `--time=05:15:00`. Steps use `srun -n1 -c 64 --exact --mem=121920M --mem-bind=local`, with no step-level exclusive/node request. Each pair asserts 64 CPUs of affinity. At most two steps run concurrently.

The total cap remains 5.90 CPU node-hours, including failed attempts and controls. Screen admission reserves 5.25 plus 0.10 for scoring, so prior spend/reservations must be <=0.55. Individual stage maxima cannot all be spent. After the noise-free control, nominal-0 is timed and retained among the 35. The remaining 34 are refused unless 18 measured lane walls fit both the remaining allocation time and total cap, with scoring and a minute of overhead reserved. A stopped or partial ensemble cannot be scored; no automatic retry or reduced ensemble is authorized.

Before any future connect, obtain the director's approval on the exact script SHA and the required cov2d/tier3-design fence acknowledgments. Follow the routed rules: sacct only, protected reads through O_NOATIME, fresh scratch writes, no CFS writes, CPU only, guarded imports. Contact the director for coordination; no coauthor contact is authorized.

## Verification and next steps

Revision 3 requires scoring to receive `--bank`, `--identity` and `--control` as well as `--products`. It verifies the bank against the preparation receipt, reopens and verifies the single nominal control and its product, recomputes recovery, and checks each pair's control/bank/configuration identity. All products must match the bank's 205-cell mask, prior and named truth with full finite 224-vectors before indexing. Verified digests and control residuals survive in the readout. Synthetic refusal tests include missing/changed/mixed controls, shortened and cross-truth masks, wrong truth/prior vectors, invalid vector shapes and a changed bank. The revision-3 suite passes all 60 cases locally; Ruff, Black and Linux-targeted strict type checking of the runner pass. Production ROOT fits and protected reads remain unexecuted.

Revision 2's local suite has 37 passing tests. It includes 1% nominal recovery acceptance, both signs outside 2% rejection, unchanged strict integral identity, planted control failures, exact signed signal weights, all seeds/settings, multi-cell conservation, real ratio-map indexing, shared targets and budget refusals. Re-run the focused suite after code changes:

`python -m pytest -q 2d-unfolding/ibukt/test_ibukt.py`

Use an external local environment with NumPy and pytest; ROOT fits and Linux O_NOATIME paths remain unexecuted. Run the repository hooks for staged changes, and check CI on the actual remote head. The earlier import-path suites passed 17 tests and 27 subtests; neither revision changes import-path insertion.

1. Confirm the PR head, working-tree cleanliness, CI and latest director instructions.
2. Send the revision-3 SHA to the director for the focused confirmation read. Address only concrete authorized findings.
3. Prepare an execution binding only when instructed. A clean audit is not itself cluster approval.
4. Preserve the current estimator settings and thresholds until a separately reviewed amendment exists.

Do not revive the 1e-8 fitted-recovery gate, the five-hour launch, step-level exclusive packing, or the packed-share runtime estimate. Weighted missed-event regression and oracle interventions stay deferred: tier3-design coordinated the RSN/T3 definitions (W uses w_push*w_truth; the miss oracle predicts r/w_push), but those arms have no implementation/execution authority here. Capacity and iteration interventions also remain outside the current screen.

Use explicit git staging paths; never stash, rebase or force-push. Work in an isolated task worktree with one active writer, never the shared checkout. Do not edit the paper or note. The repository's front door and generated views are routing surfaces, not scientific evidence or compute authorization.

## Signed-target follow-up, 2026-11-19

Decision PR #1232 merged at `f0d298611df010a31c5bed7f110af96c29a323e8`.
A2 compares signed-target binned IBU with refined-target OmniFold on matched
known-truth draws. The signed-data study measures the fixed-K sensitivity of
real-data IBU to changing only its target. The two reviewed declarations control
the analyses. An inadmissible target or failed control ends the applicable
attempt and yields a STOP receipt. A partial screen cannot be scored.

The IBUKT personal lane owns implementation and operation. The director reviews
the exact bytes and coordinates one independent read before approving execution.
Reassess after that read if a material concern remains. The zero-allocation
rehearsal and signed-data study have separate reviews, as do the fresh IBUKT
envstage, prepare, screen and score. Every connect requires a fresh fence. The
IBUKT cap is 6.50 CPU node-hours including prior charges. Neither study changes
publication claims or wording.

The signed-data study requires the exact REF-C2C1 driver and helper in a separate
reference checkout at `77d76cfc2d621f8faa010b75006811868494652a`. Its production
entry point is `signed_data.py --stage STAGE --out FRESH_OUTPUT --reference REFERENCE`
through the import guard with the implementation checkout as `--expect-root`
and that specific reference checkout as `--allow`. The binding must pin the
launcher, staged inputs and login-node resource envelope before execution.
