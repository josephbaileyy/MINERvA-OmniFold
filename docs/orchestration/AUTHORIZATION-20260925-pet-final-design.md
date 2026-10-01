# AUTHORIZATION 2026-09-25 — PET final-design selection study

**Granted by:** Joseph, directly, in the orchestrating Claude session of 2026-09-25 (a `/goal`
directive). Recorded here verbatim so later lanes read the grant rather than a paraphrase of it.

**Detailed scope:** `nd-unfolding/pet/final_design/SCOPE-HANDOFF-20260925.md`, a byte copy of
`HANDOFF-20260925-pet-final-design.md`, the brief the goal names (the goal text itself is also kept
byte-for-byte at `nd-unfolding/pet/final_design/GOAL-20260925-pet-final-design.txt`).

**Branch:** `pet-final-design-20260925`, created from `origin/pet-improvement-20260922` at
`9368ec9e55eb486109498772753825fc24616851` (remote head verified by `git ls-remote` on 2026-09-25
21:45Z, together with `pet-direct-token-comparison` at `7090fcc12ce8119f7a5fc4fa05265a8486f9049a` and
`main` at `cac87cedf96c258663748c234dd6b82003cdc8ba`). The predecessor campaign, its protocol, verdicts,
thresholds and terminal disposition are preserved unmodified.

## The grant, verbatim

> Execute the study in HANDOFF-20260925-pet-final-design.md at the MINERvA-OmniFold repository root. Read the complete handoff and current canonical instructions first. Obtain the handoff before starting in a fresh clone. The completed predecessor is pet-improvement-20260922 at 9368ec9e55eb486109498772753825fc24616851; recover its evidence and verify remote heads.
>
> I authorize this study, including implementation, existing-source extraction, CPU/GPU training and inference, scaling, simulated bias/coverage ensembles, parallel specialists, independent read-only reviews, repairs/retries, preservation, commits, pushes and a draft PR. Use existing authorized accounts and allocations. There is no new arbitrary compute ceiling: substantial available compute use is welcome when it resolves the decision. Measure allocations and competing commitments, reserve resources for final validation, track costs, and do not purchase resources, exceed quotas, exhaust a shared allocation or interfere with other work. Routine work and prospective amendments within scope do not need repeated permission.
>
> The objective is a defensible final choice of the best complete design among meaningfully tested contenders, with a validated simulation-only uncertainty procedure. Prefer our smaller network ONLY if it is demonstrably comparable and substantially cheaper. Otherwise choose the stronger larger/pretrained design when feasible. Adopt the handoff's proposed methodological defaults: simultaneous one-sided 95% non-inferiority at a 0.02 recovery margin and at least twofold total-cost savings for a cost-based small-model choice, plus the separately predeclared scientific eligibility requirements. Freeze the remaining numeric decision table before successor performance is inspected.
>
> First establish fresh-event capacity and honest independence. Prior FINAL/STRESS data may inform development but are not untouched validation. Locate the proton/neutron failure through detector ratios, truth projection, missed-event extrapolation and iteration trajectories. Test controlled hybrid improvements around C at three iterations; B and C were separate interventions, not a measured combined design. Include a genuinely trained larger-model contender and PET2 pretrained-versus-scratch controls. Separate representation, architecture, pretraining and truth-step effects. Give justified alternatives such as AUSSIE a bounded matched stress test before costly escalation. Do not assume the network is irrelevant or that more iterations are safer.
>
> Use staged development, meaningful learning curves, independent sizing, frozen finalists, fresh confirmation/stress tests, and coverage at the exact final configuration. Require useful regional/topology accuracy, not merely no negative recovery. Include cost, uncertainty width and stability. Increase precision when it can resolve selection; do not call a nonsignificant difference equivalence. Follow the handoff's sequential-testing, failed-final repair and selection safeguards.
>
> PET remains diagnostic. No real-data unfolding, publication adoption, production C_stat/C_ML, Gate-6 work, reopening OI-126, scalar-5D covariance changes, note/primer/paper edits, collaborator messages or automatic merge. Preserve historical thresholds and verdicts. Route compute through the current guard and verify scheduler/source state directly.
>
> Persist through execution, independent review and delivery. Produce one executable recommended configuration, report/deck, original results and manifests, decision record, resource ledger, required ledger/run-log/status commits, recovery handoff and pushed draft PR. A no-eligible-design or unresolved result is acceptable only after the discriminating tests or quantified practical limits are exhausted; never manufacture a winner. Do not stop at a plan, job submission, promising mean, or deferred coverage while authorized decisive work remains feasible.

## What this grant covers (read against the scope document)

- Compute on Joseph's existing allocations (Perlmutter `m3246`, `m3246_g`): implementation, existing-source
  extraction, CPU/GPU training and inference, scaling, simulated bias/coverage ensembles, retries.
  **No new arbitrary compute ceiling**; allocations, quotas and competing commitments are measured and
  recorded in the study's resource ledger, and resources are reserved for final validation.
- Parallel specialist agents, independent read-only reviews, repairs, preservation, commits and pushes
  of the study branch, and a **draft** PR.
- Routine work and prospective protocol amendments within scope, without repeated permission.
- The methodological defaults the goal adopts: simultaneous one-sided 95 % non-inferiority at a 0.02
  recovery margin, at least twofold total-cost saving for a cost-based small-model choice, plus the
  separately predeclared scientific eligibility requirements; the remaining numeric decision table is
  frozen before successor performance is inspected.

## What it does not cover

- Purchases, exceeding quotas, exhausting a shared allocation, or interfering with other work
  (including cancelling or reprioritizing another lane's jobs).
- Real-data unfolding; publication adoption; production `C_stat`/`C_ML`; Gate-6 work; reopening `OI-126`;
  changes to the adopted scalar-5D covariance; note/primer/paper edits; collaborator messages; automatic
  merge.
- Changing historical thresholds or verdicts (`0.8` adequacy fraction, `0.6` regional fraction, `0.02`
  non-inferiority, `0.04` switching; the comparison's `NEITHER_ELIGIBLE / NO_SELECTION`; the predecessor
  campaign's terminal disposition).

## Enforcement

Compute routes through `nd-unfolding/mnv_guarded_run.py` from clean pinned checkouts. The study reuses the
predecessor's scope guard (`nd-unfolding/pet/improvement_campaign/authorization_scope.py`, which refuses
real-data inputs to any unfolding stage and the historical comparison's output directory as a write target)
through the study's own entry points, which additionally refuse any pool not released by the study's
protocol.
