# Orchestration read router

This file is a pointer-only router. [`MANIFEST.tsv`](MANIFEST.tsv) is the authority on classification and read policy.

## Start here

- Classification and exact-path lookup: [`MANIFEST.tsv`](MANIFEST.tsv)
- Current control-plane snapshot: [`LIVE-STATE.md`](LIVE-STATE.md)
- Multi-session operating policy: [`SESSION-WORKFLOW.md`](SESSION-WORKFLOW.md)
- Joseph-only choice register: [`USER-DECISIONS.md`](USER-DECISIONS.md)
- Agent-process failure index: [`FINDINGS.md`](FINDINGS.md)
- Physics-claim index: [`CLAIMS.md`](CLAIMS.md)
- Retracted and superseded value index: [`INDEX-retracted-and-superseded-values.md`](INDEX-retracted-and-superseded-values.md)

## Route by task

| Task | Read |
|---|---|
| Create or dispatch a bounded worker task | [`TASK-HANDOFF.template.md`](TASK-HANDOFF.template.md), [`TASK.template.md`](TASK.template.md), [`FINDINGS.md`](FINDINGS.md) |
| Operate or rotate Claude/Codex sessions | [`SESSION-WORKFLOW.md`](SESSION-WORKFLOW.md), [`USER-DECISIONS.md`](USER-DECISIONS.md) |
| Record a Joseph-only choice | [`USER-DECISIONS.md`](USER-DECISIONS.md) |
| Inspect current jobs, owners, blockers, or next action | [`LIVE-STATE.md`](LIVE-STATE.md) |
| Check provider capacity or dispatch policy | [`LIVE-USAGE.md`](LIVE-USAGE.md), [`SCHEDULING-STRATEGY.md`](SCHEDULING-STRATEGY.md) |
| Configure event-driven continuation | [`WAKER.md`](WAKER.md) |
| Verify a physics claim | [`CLAIMS.md`](CLAIMS.md), [`VALIDATION_LEDGER.md`](../../VALIDATION_LEDGER.md) |
| Quote or replace a value | [`INDEX-retracted-and-superseded-values.md`](INDEX-retracted-and-superseded-values.md), [`VALIDATION_LEDGER.md`](../../VALIDATION_LEDGER.md) |
| Apply receipt requirements | [`CONVENTION-receipt-ingredients.md`](CONVENTION-receipt-ingredients.md) |
| Verify a check is deployed / added a gate or hook check | [`CONVENTION-verifying-a-check-is-deployed.md`](CONVENTION-verifying-a-check-is-deployed.md) |
| Work on quarantine discharge | [`CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`](CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md), [`DETERMINATION-20260811-cause5-binding-half.md`](DETERMINATION-20260811-cause5-binding-half.md) |
| Work on standard-P4 provenance | [`PROVENANCE-DEBT-20260810-standard-p4.md`](PROVENANCE-DEBT-20260810-standard-p4.md), [`P4_STANDARD_STATUS.md`](../../nd-unfolding/active_universe_5d/standard/P4_STANDARD_STATUS.md) |
| Work on PET remediation | [`PET_UQ_REMEDIATION_STATUS.md`](../../nd-unfolding/PET_UQ_REMEDIATION_STATUS.md) |
| **Route PET work / find what PET is blocked on** | [`MAP-20260817-pet-critical-path.md`](MAP-20260817-pet-critical-path.md) — item-level, partitioned by blocker type; names the single decision (`OI-126`) that gates the most. Coarse July-era phase path is `SCHEDULING-STRATEGY.md:17-19`. |
| Prepare the macro update after authorization | [`PROCEDURE-gbdtFive-macro-update.md`](PROCEDURE-gbdtFive-macro-update.md), then [`RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md`](RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md) for what each macro IS, whether the 2026-08-16 rebuild moved it (no), and the three inline `\SI{}` operands outside `values.tex` |
| Audit the open cannot-fail sweep | [`CORPUS-20260811-gates-that-cannot-fail-sweep.md`](CORPUS-20260811-gates-that-cannot-fail-sweep.md) |
| Interpret covariance rank or inversion | [`RANK-AND-INVERSION-20260810.md`](RANK-AND-INVERSION-20260810.md) |
| Coordinate the current closeout sessions | [`PROMPTS-20260811-four-session-closeout.md`](PROMPTS-20260811-four-session-closeout.md) |

## History and machine artifacts

- Orchestration chronology: [`RUNS.tsv`](RUNS.tsv)
- Workstream chronology: [`ND_OMNIFOLD_RUN_LOG.md`](../../nd-unfolding/ND_OMNIFOLD_RUN_LOG.md)
- Archival or machine-artifact lookup: [`MANIFEST.tsv`](MANIFEST.tsv)
- Successor lookup for a dead path: [`MANIFEST.tsv`](MANIFEST.tsv)

## Regenerate

Run [`generate_manifest.py`](generate_manifest.py) from the repository root:

```bash
python3 docs/orchestration/generate_manifest.py
python3 docs/orchestration/generate_manifest.py --check
```
