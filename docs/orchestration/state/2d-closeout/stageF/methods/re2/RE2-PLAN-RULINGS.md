# Director's rulings on RE2-PLAN (2026-10-23)

**By** the paper-tighten lane, as director. **On** [`RE2-PLAN.md`](RE2-PLAN.md), merged in PR #275 (`c97ade35`),
under DECISION-20261023-joseph-2d-refined-integrate-ci item 1 and
`AUTHORIZATION-20261012-2d-closeout-delegation.md` §3 item 2.

1. **The plan is accepted as the basis for a declaration.** Nothing runs on the plan alone. The next step is
   `RE2-DECLARATION.md`: code shas, seeds, inputs with sha256, the controls and rules fixed now, and the J0 pilot.
   The director binds that declaration before any job.
2. **Grant, in principle.** At most 90 CPU node-h under the 2D closeout ceiling (39.4714 spent by the plan's
   re-derivation; 660.53 left), gated by J0. If J0 shows that the all-branch universe read is needed, the plan's
   ≤ 165 needs a fresh binding by the director. Both fit the remaining ceiling. Today's measured slowdown applies
   (`state/gpu-timing-20261023/REPORT.md`: the K = 5 unit is about 1.4× slower than its September record), so the
   J0 units, not historical ones, set the job limits.
3. **R4, the estimator.** The refined 2D estimator ((a) with the 400/31 refinement at `random_state` 45; C2's refined
   arm and D2) is registered by the re-1 lane in its declaration PR, as `a-refined-400-31` or similar. Its aliases
   must cite their source lines, and the registry checks must pass.
4. **R6, the ledgers.** RE-1's 1.68 node-h was charged under RE-1's own grant (RE1-SPEC, DECISION-20261020) and is
   not re-booked under the 700. RE-2's jobs are booked under the 700.
5. **R8 and R9 go to Joseph.** The director's recommendations:
   - **R8.** Rebuild 2D only. The extended-fiducial value stays on its purity N-D pipeline, labelled. When `E_R`
     lands, `sec_fps.tex:47-52`'s "reproduces \sigTwoD" is re-evaluated against the new value, and the result is
     printed either way. The 5D covariance stays (a) (DECISION-20261023 third, item 1).
   - **R9.** Durable copies of RE-2's final products go to HPSS (CFS is closed), after a size estimate. The
     intermediates stay on pscratch until the integration.
