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

## Execution

Run the three existing no-training stages (Gate A/B, pull/push decomposition,
trajectory) in a five-task, one-GPU-per-member array using
`nd-unfolding/pet/sbatch_gate6_member_trajectory_array.sh`.  Outputs are
member- and job-scoped; no two tasks share a final path.  Batch is the primary
route because all five independent 2M-event inference arms can run in parallel,
each needs up to the four-hour GPU wall, and no interactive allocation existed
at preflight.
