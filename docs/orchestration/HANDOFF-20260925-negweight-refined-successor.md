# Scalar-5D negweight-refined successor

Draft; no compute or adoption activated. The owner sends the companion
GOAL-20260925-negweight-refined-successor.txt to activate it. Commit the actual
authorization and document identities first. Both attachments are uncommitted.

## Durable starting point

The completed scalar campaign is at main commit
3905893f948bf87526f3dc4d3e1d60d91da620c8; standalone note main is
7739089b418ff92ae691febaeeaf195070ec2c41. Refresh these verified-at-preparation
heads. Shared local main may lag; use an isolated worktree from current origin/main.

Read root AGENTS.md and routed current-work records, then these paths under
docs/orchestration/:
- CAMPAIGN-s5c-20260924-index.md (closeout, OI-190/OI-191, state routes).
- OUTCOME-20260925-s5c-tier-s-futility-fail.md.
- OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md.
- state/s5c/review-3-disposition.json and FEASIBILITY-20260925-s5c-scalar5d-measurement-and-inference.md.
- AUTHORIZATION-20260924-scalar5d-campaign-activation.md and the approved
  PLAN-scalar5d-reportable-uncertainties-and-inference.md, blob
  8b0617b6e044a55a9b5870b46e5d90a15a6ced7a. Keep that historical plan unchanged.
- HANDOFF-20260924-preparation-for-scalar5d-campaign.md and its recovery routes.
Also read VALIDATION_LEDGER.md VL146-VL150, KNOWN_ISSUES.md 75-76, and OI-191.

## What changed scientifically

The standard scalar chain and failed coverage campaign used purity, not
negweight-refined. F1 failed seed stability. F2's bias-corrected statistical
intervals failed coverage on nominal and E_avail-varied truth. The invalid q3
point is excluded; its sentinel bug was repaired. No successor qualified.

Background-inclusive pseudo-data expose purity-method bias, absent in the
signal-only control. Background sampling is missing from the tested statistical
sigma, and a nominal bias correction does not transfer. That correction was not
applied to the real-data result. These facts require a method-level successor.

Do not call purity-versus-negweight differences on data a measured bias: they
measure method dependence. Known-truth closure establishes bias in its tested
model only. Neither negative weights nor deterministic execution proves validity.
The old adopted-under-exception bytes and failures remain unchanged.

## Implementation and validation priorities

nd-unfolding/unfold_nd_omnifold_unbinned.py supports --bkg-mode negweight-refined:
data and negative background events form a signed target, refined to nonnegative
weights before step 1. Verify this branch actually executes in EVERY successor
path. A flag on the central launcher cannot convert stored purity-weighted inputs.
Audit s5c_pseudo.py, bootstrap_nd.py, the universe/throw/lateral producers and all
callers before reuse. Propagate the mode, seeds and refinement through nominal,
bootstrap, systematic and closure paths with matched normalization and masks.

Rebuild refinement after each applicable resampling/nuisance change. Distinguish
observed mixture fluctuations, background-template MC uncertainty and nuisance
uncertainty with their correlations. Avoid double counting or using truth labels
unavailable on data. Validate the exact estimator AND intervals reported on data.

Begin with known-truth background-inclusive development controls, actual
E_avail shape departures and repaired q3 conditional departures. Verify amplitude,
support and any claimed marginal preservation from operands. The earlier
E_avail tilt was mostly normalization. Freeze gates before fresh validation.
Require coverage, useful widths, complete seed tests and physical-systematic
scope; Tier-S statistical coverage alone does not validate total uncertainty.

Reuse preservation. No architecture search, PET, general cleanup or joint-inference
production. First earn a qualified measurement; price later inference separately.
Persist contract, budget, jobs and next action; report the four statuses separately.
