# AUTHORIZATION 2026-09-22 — PET improvement campaign

**Granted by:** Joseph, directly, in the orchestrating Claude session of 2026-09-22 (a `/goal`
directive). Recorded here verbatim so later lanes can read the grant rather than a paraphrase of it.

**Detailed scope:** `nd-unfolding/pet/improvement_campaign/SCOPE-HANDOFF-20260922.md` (a byte copy of
the handoff Joseph pointed the goal at, `HANDOFF-20260922-pet-improvement.md`). The goal names that
document as "the detailed scope and handoff for this goal".

**Branch:** `pet-improvement-20260922`, created from `origin/pet-direct-token-comparison` at
`7090fcc12ce8119f7a5fc4fa05265a8486f9049a` (remote head verified by `git ls-remote` on 2026-09-22).
The comparison branch and its report, deck, thresholds and verdict are preserved unmodified.

## The grant, verbatim

> Read /Users/josephbailey/local-research/MINERvA-OmniFold/HANDOFF-20260922-pet-improvement.md in
> full and execute its PET improvement campaign through implementation, experiments, independent review,
> and final delivery. Treat that document as the detailed scope and handoff for this goal.
>
> I am Joseph. I explicitly authorize all compute reasonably necessary for every stage defined there,
> using my existing authorized accounts and allocations: CPU/GPU runs, larger samples, source extraction,
> preprocessing, tuning, ablations, learning curves, physics stress tests, simulation-only bias/coverage
> ensembles, justified alternative-method trials, retries, and preservation. There is no additional
> campaign-specific GPU-hour or CPU-hour cap; this supersedes the old PET comparison's 1,000 GPU-hour
> ceiling and narrower per-stage approvals. Do not repeatedly ask permission for these stages. Measure
> costs, track cumulative usage, and scale adaptively. Respect actual quotas, available allocations, and
> other campaigns; no new purchases or interference with other lanes' jobs.
>
> I authorize isolated worktrees/branches, code changes, tests, parallel specialist agents, independent
> reviewers, campaign commits and pushes, and a draft PR. Record this authorization in the campaign and
> satisfy the provenance/execution guards.
>
> Start by verifying the suspected optimizer and shared-step-2 recipe discrepancies at runtime. They are
> hypotheses, not established causes. Preserve the historical comparison and verdict. Then execute the
> handoff's prioritized feature studies, stepwise diagnostics, sample-size/compute scaling, physics
> validation, and justified alternatives.
>
> Keep PET diagnostic. Do not reopen OI-126, perform Gate-6 actions, construct production uncertainty
> products, change publication results or the adopted scalar-5D covariance, unfold real data into a new
> central result, message collaborators, or merge automatically. New simulation-only validation ensembles
> are expressly authorized.
>
> Do not lower historical thresholds to manufacture a pass. Finish with either an independently validated
> improvement or a decision-resolving diagnosis with measured limits. Deliver reproducible code/
> configurations, receipts, machine-readable results, report, new PDF/TeX slides, claim-evidence index,
> resource accounting, required records, pushed branch/draft PR, and a durable handoff.
>
> Persist through queue waits and context resets. Do not stop at a plan or submitted jobs. Ask only for
> genuinely out-of-scope decisions, unavailable access/resources, or indispensable scientific
> clarification.

## What this grant covers (read against the scope document §1)

- Compute: all CPU/GPU/memory/temporary-storage work reasonably necessary for the stages of the scope
  document, on Joseph's existing accounts and allocations (Perlmutter `m3246`, `m3246_g`). **No
  campaign-specific GPU-hour or CPU-hour ceiling.** It supersedes the comparison's 1,000 GPU-h ceiling
  and its per-stage approvals *for this campaign only*.
- Source extraction of additional existing branches, after a committed branch/source manifest.
- Simulation-only statistical/seed ensembles and bias/coverage calculations for new candidates.
- Isolated worktrees and branches, code, tests, parallel agents, independent reviewers, commits and
  pushes of campaign branches, and a **draft** PR.

## What it does not cover

- Purchases, new allocations, exceeding site quotas, or cancelling/holding/altering another lane's jobs.
- `OI-126` (not reopened; its completed probes are not repeated), Gate-6 actions, `C_stat`/`C_ML` or any
  production uncertainty product, publication adoption, changes to publication central estimators or to
  the adopted scalar-5D covariance `3d7465f6…`.
- Unfolding real measured data into a new central result. Development and validation use simulated
  pseudodata only.
- Changes to the note, primer or paper; messages to collaborators (email, Slack, Peer Mesh); merging.
- Lowering or re-deriving the historical thresholds (`0.8` adequacy fraction, `0.6` regional fraction,
  `0.02` non-inferiority, `0.04` switching) to manufacture a pass. A new reference is a prospective
  recommendation only.

## Enforcement

The campaign's scope guard is `nd-unfolding/pet/improvement_campaign/authorization_scope.py`, which
refuses real-data inputs to any unfolding stage, the historical comparison's output directory as a write
target, and thresholds other than the historical ones for like-for-like verdicts. Compute routes through
`nd-unfolding/mnv_guarded_run.py` with a clean checkout pinned to a commit.
