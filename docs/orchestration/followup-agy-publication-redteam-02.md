Resume your independent red-team context for a focused read-only verification
of Agent B's F7 commit 9d7a4c6. Do not edit files, run GPU/Slurm/C++, or message
other workers. This audit must not replace B; it is an independent challenge.

Inspect the actual diff and relevant existing full-event PET feature contract,
loader, smoke/closure code, and tests. The required F7 contract is:

- complete ordered data, signal-MC, and background-MC inventories;
- deterministic coherent global Poisson(1) factors drawn over each full
  inventory before any training subset;
- signal factor shared by the exact training and extraction paths;
- background factor applied to the literal aligned background-cloud signed
  weight before a fresh per-replica Stay-Positive refinement;
- no reuse of nominal refined weights, no post-subsample redraw, and fail-closed
  fingerprints/replay;
- purity/recoil-only paths are labeled controls and cannot be publication
  inputs.

Agent B reports 19/19 CPU tests, no compute, and an EVIDENCE-BLOCK because the
aligned full-event background-cloud artifact does not exist. It also says the
test implementation uses a closed-form binned Stay-Positive realization, while
production is expected to call the trained `refine_stay_positive` classifier.
Verify that this separation is honest and that no code path could mistake the
test surrogate for production readiness.

Return PASS or BLOCK first for **code/control readiness only**, then:

1. exact supporting or contradictory file/line evidence;
2. direct negative-case gaps in the 19 tests;
3. whether commit 9d7a4c6 meets the repo same-commit launcher/product-summary/
   ledger/RUN_LOG/STATUS gate for its actual non-result status;
4. the minimal repairs before G2/background-cloud production can begin;
5. the exact runtime evidence still necessarily blocked on future full-schema
   data.

Do not authorize PET nominal, replicas, covariance, laterals, or adoption. A
PASS may only mean the F7 interface is ready to consume a future committed
full-schema background-cloud source.
