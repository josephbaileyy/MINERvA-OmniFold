# AUTHORIZATION 2026-10-11 — XR recovery: amendment of the 2026-10-10 XR grant (repair, preflight, the five runs)

**CITABLE FOR:** the exact text, date and scope of Joseph's amendment of the XR grant. It covers:
- repairing the XR launch package;
- one independent admission review;
- one in-allocation preflight;
- the five original XR runs, after admission and the preflight pass.

It is bound to one package commit and one manifest digest.

**NOT CITABLE FOR:**
- any XR result, seed invariance, or a resolution of the 2D pairing;
- a transfer measurement, an uncertainty production, N2, a KI-85 lift, a re-quote or an adoption;
- other compute.

This record launches nothing itself. The execution record is
`state/next-preparation-20261009/xr-recovery/REPORT.md`.

## 1. Binding (named in full)

| item | value |
|---|---|
| package commit | `07428e5dec9fecd2e1148d8a2bdabc139a35138f` |
| manifest SHA256 (`state/next-preparation-20261009/two-d-followup/xr/manifest/expected-code.json`) | `07a74b914329c8286b1434619976c246a7543e7643f3f8b2f4792a7ad0a950d6` |
| amends | [`AUTHORIZATION-20261010-xr.md`](AUTHORIZATION-20261010-xr.md) (package `06eae0fede3508419f235f8cbe61954b33de8497`): its package, attempt allowance, output namespace and review budget |
| package | `state/next-preparation-20261009/two-d-followup/xr/`, repaired in place; the old package is preserved at `06eae0fe`. `manifest/runs.json` defines the preflight PF and the five runs, the inputs, the kinds, the 1e-8 criterion, the comparisons and the control. The criterion, the comparisons and the control are unchanged |
| output namespace | `/pscratch/sd/j/josephrb/xr-recovery-20261011` (new; the prior outroot `/pscratch/sd/j/josephrb/xr-two-d-followup-20261010` is kept unchanged) |
| cap | **6.4 charged CPU node-hours on m3246 in total, cumulative with the prior grant's five failed jobs (0.0013498263888889 node-h, recomputed from sacct by every ledger); zero GPU** |
| planned ceiling | 6.3802560763888889 node-h, made of: prior 0.0013498263888889; 1 preflight × 5 min × 12/256 (0.00390625); 4 exact × 30 h × 12/256 (5.625); 3 LightGBM × 1 h × 64/256 (0.75) |
| admission review | ADMIT WITH CHANGES at `57b7403c` (`state/next-preparation-20261009/xr-recovery/review/admission-review-57b7403c.md`); one repair batch (`07428e5d`); focused re-review **ADMIT** at `07428e5d` (`review/rereview-07428e5d.md`; N-1 MINOR recorded, not repaired) |

## 2. Scope and exclusions

- **Authorized:**
  - The narrowly scoped repair of the XR launch package and its tests.
  - One fresh read-only reviewer for this assignment, with at most: one admission review, one final
    independent numerical verification, and one focused repair/re-review.
  - After admission: **one** preflight job (`PF`). It runs on shared QOS, at ≤ 12/256 billing, for ≤ 5
    minutes, with no fit.
  - After the preflight passes: L0 first. Once L0 has a complete, comparable receipt: X0, X0′ (`X0p`), X1
    and L1.
  - Totals in this amendment: ≤ 4 exact jobs (each ≤ 30 h at ≤ 12/256) and ≤ 3 LightGBM jobs (each ≤ 1 h at
    ≤ 64/256), retries included. That is one extra exact attempt across the three exact arms, and one extra
    LightGBM attempt across the two LightGBM arms.
  - Shared QOS only, from an isolated detached checkout at the commit carrying this record.
- **Excluded:**
  - GPU and full-node substitution;
  - transfer experiments and uncertainty production;
  - N2, a KI-85 lift, a re-quote or an adoption;
  - changes to the scientific comparisons, tolerances, references, cell identities or missing-result rules;
  - edits to shared scientific status, publication sources, the production driver, the pinned OmniFold
    helper or SB1's package;
  - any other compute.
- **Stop rules:**
  - A failed preflight stops all dependent execution.
  - A new 72-hour window starts at the preflight submission. Only this assignment's unfinished jobs are
    cancelled, by verified id.
  - Missing comparisons are INCONCLUSIVE.
  - PASS, FAIL and INCONCLUSIVE are all valid terminal outcomes. No subsequent experiment starts
    automatically.

## 3. The actual authorization

Sent by Joseph as a session message, recorded in the session at `2026-10-11T00:52:24Z`. The text below is
verbatim (sha256 of the text, newline-terminated: `f9d02f65f4da456dde68d0b42e40d3e0c36ae67b20cd8fd5632065709aa2d256`).

> Please complete a bounded XR infrastructure recovery and retry. Do not reopen the methodological study or change the scientific comparisons.
>
> AUTHORIZATION
> I authorize repairing the failed XR launch package, independently reviewing the repair, running one in-allocation preflight, and then executing the five original XR runs if admission and preflight pass.
>
> This amends the previous XR grant’s package, attempt allowance, output namespace and review budget. The cumulative CPU-node-hour ceiling remains 6.4, INCLUDING the previous failed jobs, preflight, new runs, failures and verification. No GPU, full-node substitution, transfer experiment, uncertainty production, N2, KI-85 lift, re-quote or adoption.
>
> BASELINE AND OWNERSHIP
> Read AGENTS.md, the campaign review, CURRENT_WORK and governing records, the committed XR authorization, and:
> docs/orchestration/state/next-preparation-20261009/two-d-followup/REPORT.md
> especially B7–B8 and E.3, plus its final verification.
>
> Refresh remote main and the completed follow-up branch. Use an isolated worktree. Preserve the old package, failed-run records, outputs and reviews at their existing commits.
>
> Own the XR package’s narrowly scoped repair and tests, and a new recovery record under:
> docs/orchestration/state/next-preparation-20261009/xr-recovery/
>
> You may create a dedicated authorization-amendment record quoting this grant, with the scoped registration required by repository policy. Do not rewrite shared scientific status, publication sources, the production driver, pinned OmniFold helper or SB1’s package.
>
> DECISION
> Can the repaired, correctly admitted package answer the original central-reproduction and one-seed comparison questions?
>
> REPAIR
> 1. Parse actual granted billing from AllocTRES in recorded Perlmutter scontrol output. Remain fail-closed when the field is absent, null, malformed or exceeds the cap. Parse the named field explicitly.
>
> 2. Replace the self-confirming scheduler fixture with captured real scheduler formats. Test a valid allocation, excessive billing, pending/null allocation and malformed output. Require a regression test that fails when the old TRES parser is restored. Check the other scheduler parsers against recorded real output.
>
> 3. Add a preflight mode through the actual xr_job.sbatch path: allocation check, admission verification, environment setup, input hashing, guard, pinned driver/helper loading and the relevant environment/core-count setup. Stop before any fit. Its receipt must be unmistakably a preflight receipt and must never satisfy a scientific comparison.
>
> 4. Freeze a new package commit, manifest and output namespace. Preserve all original scientific arguments, references, cell identities, comparison tolerances and missing-result rules.
>
> 5. Make attempt accounting distinguish this amendment’s jobs while retaining the old jobs and their charges in the cumulative ledger. A new package, outroot or date must not reset the 6.4-node-hour ceiling.
>
> REVIEW AND RELEASE
> Use one fresh read-only reviewer, explicitly authorized. Maximum:
> - one admission review of the repair and executable package;
> - one final independent numerical verification;
> - one focused repair/re-review across this assignment.
>
> The reviewer must inspect actual scheduler operands and negative controls. Do not repeat the completed methodological review.
>
> After admission passes, run ONE preflight job: shared QOS, at most 12 billing CPUs, at most five minutes, no fits. If it fails, stop dependent execution and deliver the exact defect; do not launch the five runs.
>
> After preflight passes, run L0 first. Confirm successful guarded execution and a complete, comparable receipt before releasing the remaining runs. A scientifically meaningful comparison failure is a result, not automatically an infrastructure failure; preserve the frozen outcome rules.
>
> RESOURCE LIMITS
> Re-measure current scheduler billing and allocation before launch.
>
> The amendment permits:
> - one five-minute preflight at <=12/256 node billing;
> - at most FOUR exact jobs total at <=30 hours and <=12/256 billing each;
> - at most THREE LightGBM jobs total at <=1 hour and <=64/256 billing each.
>
> These totals include retries: only one additional exact attempt across the three exact arms and one additional LightGBM attempt across the two LightGBM arms.
>
> The previous recorded charge was 0.0013498264 node-hours; verify it. With the stated ceilings, cumulative planned maximum is about 6.3803 node-hours. Refuse any settings that would exceed 6.4. No automatic resource expansion.
>
> Use a new 72-hour execution window beginning with the preflight submission. Enforce the stop and cancel only this assignment’s unfinished jobs. Record missing comparisons as INCONCLUSIVE.
>
> DEPLOYMENT
> Keep SB1’s running checkout, package, environment and outputs untouched. Use an isolated pinned deployment. Inspect scheduler state directly; do not infer it from an old report. If safe coexistence cannot be established, serialize within the budget or finish the dependent work as INCONCLUSIVE.
>
> LOCAL BUDGET
> Six active hours including review and delivery; three local CPU core-hours; two local compute threads; 8 GiB RAM; 3 GiB new local scratch beyond worktrees; 20 MiB tracked evidence. Protect the final quarter for verification and delivery.
>
> DELIVERY
> Independently reproduce the consequential comparisons from output histograms and verified references, and recompute charges from scheduler records. Report admission, preflight, execution and each scientific comparison separately.
>
> Push a reviewable branch/PR with exact package/input/result refs, actual resources and remaining limitations. Do not merge or change scientific status. Complete unaffected work when blocked.
>
> PASS, FAIL and INCONCLUSIVE are all valid terminal scientific outcomes. No subsequent experiment starts automatically, and no further routine permission is needed within this grant.
