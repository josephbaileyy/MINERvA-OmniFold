# Evidence snapshot for the scalar measurement successor proposal

This is an observation record for
[the proposal](PROPOSAL-20261005-scalar-measurement-successor.md), not a campaign
control file or a new scientific result. No training, unfolding, ensemble,
allocation, covariance replacement, or worker-control action was performed.

## Remote identities and ownership

Direct `git ls-remote` observations on 2026-10-05, approximately 14:47-14:54 UTC:

| Remote and ref | Full head | Meaning |
|---|---|---|
| Canonical `main` | `c64228dab8b4d55e3fec772b8c05c004268578b7` | Proposal baseline; scalar campaign publishes here |
| Canonical `s5p-parallel-recompute-20260928` | `be183e559176c802c6ca7e6ac98885c34cef0300` | Independent scalar recomputation owner, separate branch |
| Canonical `study/2d-coverage-test-20261005` | `37a0cf8c0d838282f7b6ec3a45fe704082392290` | 2D coverage owner; preregistration amendment and pilot, not a final coverage result |
| Canonical `pet-final-design-20260925` | `9a9a7bfb8fe0ce646a9895090a8d7b6c09568866` | Terminal decision `NO_ELIGIBLE_DESIGN` with its own review closed |
| Standalone analysis-note `main` | `97e8449f999e9098fe6c85c3c87b0547edba47f7` | Observed only; no manuscript edit or synchronization in this task |

No remote ref was returned for `campaign/s5p-precision-20260926` or the old
`analysis/gbdt-model-dependence-20261003` ref. Absence of a branch is not loss
of its work: the scalar owner pushes to main and the synthesis is present in
the pinned main tree. The local scalar and recomputation worktrees were clean
when inspected. The initial shared main was at `3ea5f06a`, six commits older,
with unrelated untracked handoffs. It was left intact; the proposal uses its
own worktree and branch `docs/scalar-measurement-successor-20261005`.

## Direct live observations

The canonical cluster checkout's prescribed freshness check returned
`FRESH :: Git: 32e403b8 == HEAD`. That checkout is behind remote main. The
check verifies only its own Git/Observed freshness, not the current campaign
science or authorization. The proposal reads governance from the newer
remote snapshot and observes the scheduler directly.

At **2026-10-05T14:53:17Z**, `squeue` returned exit 0 and these relevant rows:

| Job | Name | State |
|---|---|---|
| `59366262_[9-96]` | `cov2d_fixedtruth` | PENDING |
| `59375125_98` | `cov2d_fixedtruth` | RUNNING |
| `59349568_[23-33]` | `s5p-s5p_cal_gibuu_2019_b6` | PENDING |
| `59349568_22`, `59349568_21` | `s5p-s5p_cal_gibuu_2019_b6` | RUNNING |
| `59367892_32` | `s5p-s5p_cal_nuwro_21_09_b7` | RUNNING |

At **14:54:56Z**, direct scalar status-file reads found three finals:
GENIE CV B=1366, GENIE MEC B=1343, MnvTune B=1365, all with reason
`rule met for both tests`. The power r3 log ends `queue done` at
2026-10-04T15:42:06Z. Process observation found the GiBUU runner PID/PGID
1047841 and NuWro runner PID/PGID 1100694 alive, both PPID 1, against the
routed r3/r6 deployments. These are operational observations, not final
inference claims. The scalar checklist is not satisfied and no terminal
evaluation or recomputation was launched by this task.

No current spent-balance claim is made. Budget ceilings were read from
`state/s5p/budget.json` revision 7 and the pinned 2D worker's budget receipt.
No account credits, reservations, QOS settings, or campaign ledger were changed.

## Scientific source precedence

- `AGENTS.md`, campaign review, CURRENT_WORK, OI-193, campaign index,
  cold-start handoff and terminal checklist were read.
- Scalar decision: amendment 4, then amendment 6 corrections and its
  independent review. The original Stage-2 prose overstates the prior bound,
  the calibration mechanism and fixed-point interpretation; it is not used
  to restore those claims.
- Synthesis: `nd-unfolding/gbdt_model_dependence/{README,DELIVERY,PROPOSAL}.md`,
  original receipts/reviews, and VL163. Its 70-node-hour proposal remains
  deferred, separately authorized if ever pursued.
- 2D: current status/reference, VL162 and its direct rollup receipt;
  the coverage branch's pinned preregistration, amendment 1, equivalence and
  pilot-accounting receipts. The proposed matching algebra follows the
  production driver's bootstrap block and `compute_omnifold_completeness_2d`
  before `extract_cross_section_2d`. It is a candidate correction, not an
  independently validated statistical prescription.
- PET: only its committed terminal decision was read for the terminal label;
  no blinded or unscored PET products were opened.

No new physics reduction is claimed, so this proposal does not create a new
validation-ledger number or edit a worker's run log/status. Its own review
will be recorded separately. Original scientific verification limitations
remain attached to their sources.

## Reproducible planning arithmetic

2D pilot timing operands, from the pinned worker's
`docs/orchestration/state/coverage-2d-20261005/budget.json`:
660, 750, 730 seconds, billed fraction 256/256, regular QOS factor 1.
The arithmetic is `(660+750+730)/3/3600 = 0.1981481481` node-hours per toy.
The proposal does not infer this workload's future cost from scalar R timings.

For coverage planning, let `m=206*4*2=1648`, tail probability
`a=0.05/(2*m)`, and N=2400. A binomial count k passes a lower coverage bound L
when `Pr(Bin(N,L) >= k) <= a`; it passes an upper bound H when
`Pr(Bin(N,H) <= k) <= a`. Summing binomial probabilities directly gives:

| Nominal p | Allowed coverage [L,H] | Accepted hits [kmin,kmax] | Probability of failing at nominal p |
|---|---|---|---|
| 0.682689 | [0.60,0.80] | [1540,1836] | `8.692462e-6` |
| 0.95 | [0.90,0.99] | [2220,2352] | `5.667565e-8` |

The family assurance lower bound is
`1 - (206*4)*(8.692462e-6 + 5.667565e-8) = 0.9927907`.
This uses the union bound, so correlated cells are permitted. It assumes
independent draws within each fixed case, exactly those marginal coverages,
one final look, a frozen interval procedure and complete draws. It says
nothing about acceptance of accuracy or width. This is design arithmetic,
not a scientific coverage result.

Timing extrapolations:

- `24 * 0.1981481481 = 4.755556` node-hours; multiply by 1.25 for the explicit
  planning allowance: 5.944444; add a protected 2-node-hour reserve within 8.
- `4 * 2400 * 0.1981481481 = 1902.2222` node-hours for one unfold per draw.
  `1902.2222 * 1.25 / 0.8 = 2972.2222` includes 25% overhead and a reserve
  equal to 20% of the total, not 20% of the workload.
- An illustrative 498-fold nested repetition multiplies the last estimate
  to `1,480,166.7` node-hours. This is not a measured cost or a requested
  allocation; it exposes the missing efficient total-interval construction.

The calculations were performed locally with standard-library logarithmic
binomial probabilities, independent of campaign scorers. No ensemble was
generated and no observed-data statistic was calculated.
