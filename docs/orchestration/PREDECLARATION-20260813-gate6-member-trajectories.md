# Gate 6 Leg 1 — five-member checkpoint trajectories

**Fixed at 2026-08-13T08:32Z, before any member trajectory was evaluated.**

## Question and inventory

Gate 6's five-member run completed, but members 2, 4, and 5 exceed the
Gate-4 nominal fold-forward deviation bar and dominate the observed spread.
The literal Gate-6 comparison therefore does not establish whether the spread
is estimator variation or an unconverged iteration trajectory.

This control reads the already-written checkpoints for **all five** members
from array `56834281`; it trains nothing and may neither select nor exclude a
member.  The fixed seed/subsample pairs remain `(42,0)`, `(43,1)`, `(44,2)`,
`(45,3)`, `(46,4)`.  Before this declaration, a read-only inventory established
that every member has an isolated `w_nominal` directory containing exactly the
six best-epoch and two final checkpoints required for three iterations.  No
trajectory value had been calculated.

The artifacts embed the former canonical path of the Gate-2 normalized target,
which has since been archived.  The diagnostic must not recreate or repoint the
canonical path.  It may read only the archived file with SHA-256
`544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9`,
through a new explicit hash-bound override recorded in every output.

## Fixed rule

For member `m` and iterations `k=0,1,2`, read only the numeric field
`end_to_end_achieved_over_required` from `step1_increment_trajectory.py` and
define

`d[m,k] = abs(end_to_end_achieved_over_required[m,k] - 1)`.

A member is converged at the frozen `niter=3` only when both conditions hold:

1. `d[m,0] >= d[m,1] >= d[m,2]` (non-increasing at every step); and
2. `d[m,2] <= 0.10` (the existing trajectory harness band).

The printed categorical trajectory label is direction-blind and is **not**
evidence.  Record the signed numeric `push_dev_vs_R` at every iteration so a
monotone one-sided drift can be distinguished from two-sided scatter.

- If any member fails an input/provenance gate or either convergence condition,
  the five-member inventory is not established as a converged estimator family.
  Hold `C_ML`; do not promote a passing subset and do not retry unchanged.
- If all five pass, this leg licenses the next predeclared control: five total
  across-process draws of the fixed member-1 policy `(42,0)`, including four new
  runs with persisted execution-environment identity.  It does not itself
  construct `C_ML`.

In either branch, ensemble-mean centering is only a covariance convention.  It
does not move the promoted nominal central.  Gate 4's estimator-arm disposition
remains an independent user decision and blocks construction regardless of this
control's outcome.

**SOURCED 2026-08-13 by Session A, at the mediator's request — this sentence is a
DEMONSTRATED property of this repo's established practice, not a framing assertion.**
It was unsourced, and a predeclaration is precisely the document a later reader treats as
fixed and authoritative, so a true-but-unsourced claim inside one inherits that authority
for free. The evidence:

- **`docs/ESTIMATOR_REGISTRY.md:29`** carries the central and the covariance in *separate*
  columns for the adopted `omnifold-5d-lgbm`: central `products/5d/xsec_5d_MEFHC_5iter_lgbm.root`,
  and **two centering variants of the same covariance coexisting against that one unchanged
  central** — adopted mean-centered `√tr 5.8077e-38` and CV-centered variant `6.2367e-38`.
- **The centering shift is carried as its OWN term, not applied**: the registry records
  `(mean shift 1.654e-38 separate)`, and the note quotes `\gbdtFiveAdoptTrace`,
  `\gbdtFiveCVTrace` and `\gbdtFiveMeanShift` as three separate macros —
  *"exactly 'report the shift either way, do not silently drop'"*
  (`docs/OPEN_ITEMS-ARCHIVE-2026-08.md:691-693`).
- **`VL63`** settles centering as a *presentation* question — "mean-centered headline,
  CV-centered conservative variant" — under uncertainty construction, not as a change of
  central value.

**The load-bearing part is the third bullet's mechanism:** if centering could move the
central, the shift would be *applied* to it rather than reported beside two covariance
variants of one unchanged product. Recording it separately is the demonstration.

**WHAT THIS DOES AND DOES NOT SETTLE, because Session A's earlier framing overstated it.**
Session A wrote that the nominal sitting low against an ensemble mean of ~0.118 meant
"whether the adopted central should move follows from" the centred-on-the-ensemble-mean
sentence, and that framing is what put a central-value question on Joseph's list. **It was
wrong on the mechanism: centering the component does not move the central, and that half of
the escalation is withdrawn.** What survives is a different and narrower observation —
the adopted estimator is *atypical among its own seed-siblings* (dev 0.0356 against a member
range of 0.019–0.247) — which is a question about the nominal's representativeness, not
about centering, and it still depends on the convergence call.

## Execution

Run the three existing no-training stages (Gate A/B, pull/push decomposition,
trajectory) in a five-task, one-GPU-per-member array using
`nd-unfolding/pet/sbatch_gate6_member_trajectory_array.sh`.  Outputs are
member- and job-scoped; no two tasks share a final path.  Batch is the primary
route because all five independent 2M-event inference arms can run in parallel,
each needs up to the four-hour GPU wall, and no interactive allocation existed
at preflight.
