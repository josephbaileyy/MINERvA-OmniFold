# Migration takeover status — fe-fps campaign

Live orchestration checklist for the Codex takeover. This file records only
ownership, dependency state, and evidence pointers; verified scientific
numbers remain canonical in `VALIDATION_LEDGER.md`, and round receipts remain
canonical in `RUNS.tsv`.

Last reconciled: 2026-07-18 10:13 UTC. Registry:
`state/sessions.json`. Immutable source snapshot: `MIGRATION-HANDOFF.md` plus
`MIGRATION-DELTA.md`.

| ID | Handoff item | Durable owner | State | Evidence / next gate |
|---|---|---|---|---|
| T0 | Adopt migrated delegates and prove provider continuity | orchestrator | CLOSED | Exact A/B/C UUIDs adopted; one memory-only continuity response each; `RUNS.tsv` `MIG-CONT-{A,B,C}`; commit `42c1fd7`. Old root is a file handoff; Agent D was not adopted because its UUID is unconfirmed. |
| T1 | FPS P4/P6 final adoption (handoff X5) | `agent-C-fps` / UUID `4580f42d-…` | PROVIDER-PAUSED | Merge/audit closed; all 10 endpoint unfolds independently content-validated at 10:12 UTC. Final-adopt action returned HTTP 429 before work, reset 13:00 UTC; raw receipt `RUNS.tsv` `MIG-C1`. Same UUID and products preserved. Next: cov → validate → PSD-safe swap → final adopt → independent verification → X5 PASS + commit/push. |
| T2 | Standard P4 selection-complete lateral candidate (handoff X6) | `agent-A-standard` / UUID `14951826-…` | ACTIVE | Merge/audit closed; prior holder walled with 0/10 unfolds. Same A worker acquired 56082262 and launched exactly ten missing seed-42 unfolds; `RUNS.tsv` `MIG-A1`, commit `12c8b50`. Gate: 10/10 content-valid → cov → validate → CANDIDATE only. |
| T3 | Replace the support-limited lateral in the repaired R1 corrected-4D candidate | unassigned in handoff; orchestrator must assign without changing A/C ownership | DEPENDENCY-BLOCKED | Requires T2's validated standard active-lateral block. The handoff explicitly records this follow-on as unassigned; no adoption or promotion before T2 closes. |
| T4 | Consolidated BEN note for the four recurring operational failures | orchestrator | OPEN | Write after T1/T2 receipts so the note includes the final wall/holder outcomes: interactive-QOS latency; explicit job-ID/node ownership; detached drivers (BEN-024); completeness-validated resume (BEN-023). |
| T5 | F7 coherent global Poisson bootstrap before any P5B C_stat replica | `agent-B-p5b` / UUID `46e4af3e-…` | PROVIDER-PAUSED | First action attempt returned HTTP 429, reset 06:00 America/Los_Angeles (13:00 UTC); raw receipt `RUNS.tsv` `MIG-B1`. Same UUID preserved; one incomplete owned import remains uncommitted. Retry the same role after reset; no replacement. |
| T6 | G2 full-event C++ dump branches plus regenerated FPS CV point-cloud loops | Agent B interface ownership; coordinate C++ work only after active arrays drain | DEPENDENCY-BLOCKED | `FULL_EVENT_FEATURE_CONTRACT.md` G2 and `FULL_EVENT_INTERFACE_REQUEST.md`; current binary is frozen while T1/T2 run. Gate requires full muon/event/recoil schema, stable keys, `MNV101_FULL_PHASE_SPACE=1`, and regenerated CV input. |
| T7 | Fresh full-schema P3F endpoints for publication PET laterals | `agent-C-fps` after T6, preserving its FPS ownership | DEPENDENCY-BLOCKED | Current P3F endpoints are reduced-schema and may only feed `pet-reduced-fps-cross`; `P5B_LATERAL_SOURCE_DECISION.md` adopts fresh option (b) for `pet-fullevent-fps-v1`. Requires T6, then 5×2×12 regenerated endpoints and proof battery. |
| T8 | P5B publication full-event FPS nominal and UQ chain | `agent-B-p5b` | DEPENDENCY-BLOCKED | Requires T5, T6, and T7. Execute the eight ordered gates in `FULL_EVENT_FEATURE_CONTRACT.md`: nominal, floor, coherent C_stat, PET C_ML, joint vertical/flux response, selection-complete laterals, matched total covariance, projections/comparisons. No recoil-PET block transfers. |
| T9 | Rebuild final projections/significances | owner to be assigned after upstream closure | DEPENDENCY-BLOCKED | Publication runbook P7; requires corrected scalar adoption (T1/T3) and P5B (T8), with exact `M C M^T`, PSD/order/rank checks and committed summaries. |
| T10 | Publication document closeout and freeze candidate | note/Overleaf role only after production closes | DEPENDENCY-BLOCKED | Publication runbook P8; requires T9 plus no unresolved publication blocker, clean note/primer/paper builds, provenance audit, and committed document closeout. |
| T11 | Optional negweight and Gregor representation refinements | not on critical path | EXPLICITLY DEFERRED | `ROLLOUT-PLAN.md` Stages 4–5 label these optional/gated after the Stage-3 baseline. They do not substitute for or block T8. |

## Routing invariants

- Use `agentctl.py send` for every later turn; never `--last`, `--continue`, or
  a raw provider shortcut.
- Never replace a capped or failed named worker. Record the failure and resume
  the same registry role after its reset or after the evidenced failure is
  repaired.
- Agent A owns standard paths; Agent C owns FPS paths; neither may cancel or
  use the other's holder. The C++ binary stays frozen while their active arrays
  run.
- Update `RUNS.tsv` after every worker round and land each campaign result with
  its required STATUS/RUN_LOG/ledger receipts in the same commit.
