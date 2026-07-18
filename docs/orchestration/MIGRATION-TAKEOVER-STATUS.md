# Migration takeover status — fe-fps campaign

Live orchestration checklist for the Codex takeover. This file records only
ownership, dependency state, and evidence pointers; verified scientific
numbers remain canonical in `VALIDATION_LEDGER.md`, and round receipts remain
canonical in `RUNS.tsv`.

Last reconciled: 2026-07-18 11:02 UTC. Registry:
`state/sessions.json`. Immutable source snapshot: `MIGRATION-HANDOFF.md` plus
`MIGRATION-DELTA.md`.

| ID | Handoff item | Durable owner | State | Evidence / next gate |
|---|---|---|---|---|
| T0 | Adopt migrated delegates and prove provider continuity | orchestrator | CLOSED | Exact A/B/C UUIDs adopted; one memory-only continuity response each; `RUNS.tsv` `MIG-CONT-{A,B,C}`; commit `42c1fd7`. Old root is a file handoff; Agent D was not adopted because its UUID is unconfirmed. |
| T1 | FPS P4/P6 final adoption (handoff X5) | `agent-C-fps` / UUID `4580f42d-…`; independent verifier `fps-adopt-verifier` / `019f74bb-…` | BACKGROUND-MODE/PREFLIGHT-BLOCKED | The 10/10 content-valid endpoint unfolds are now proven purity controls: both launchers omit `--bkg-mode`, and the ND driver defaults to `purity`. They cannot feed the user's selected `negweight-refined` FPS/PET result. At reset C repairs exact mode-stamped manifests/validators and a separate atomic publication runner; no production. The same verifier must PASS before a 10-endpoint negweight-refined rerun, covariance, and adoption. |
| T2 | Standard P4 selection-complete lateral candidate (handoff X6) | `agent-A-standard` / UUID `14951826-…`; independent verifier `standard-p4-verifier` / `019f74cb-…` | PREFLIGHT-BLOCKED; COMPUTE ACTIVE | Same A worker's holder 56082262 is still producing the ten seed-42 unfolds. Read-only preflight `MIG-V2` found the endpoint physics/MAT formula sound but the chain not fail-closed for merged migration evidence, atomic completion/config, exact inventory/order, support, component adoption, projection, and commit durability. At reset A performs repair only; the same verifier must PASS before candidate construction. |
| T3 | Replace the support-limited lateral in the repaired R1 corrected-4D candidate | unassigned in handoff; orchestrator must assign without changing A/C ownership | DEPENDENCY-BLOCKED | Requires T2's validated standard active-lateral block. The handoff explicitly records this follow-on as unassigned; no adoption or promotion before T2 closes. |
| T4 | Consolidated BEN note for the four recurring operational failures | orchestrator | OPEN | Write after T1/T2 receipts so the note includes the final wall/holder outcomes: interactive-QOS latency; explicit job-ID/node ownership; detached drivers (BEN-024); completeness-validated resume (BEN-023). |
| T5 | F7 coherent global Poisson bootstrap before any P5B C_stat replica | `agent-B-p5b` / UUID `46e4af3e-…` | PROVIDER-PAUSED | First action attempt returned HTTP 429, reset 13:00 UTC; same UUID and partial edit are preserved. Evidence reconciliation `MIG-DEC-NW` expands F7 to full data, signal-MC, and background-MC inventories; the background factor applies before per-replica Stay-Positive refinement. Retry the same role after reset; no replacement. |
| T6 | G2 full-event C++ dump branches plus regenerated FPS CV point-cloud loops | Agent B interface ownership; coordinate C++ work only after active arrays drain | DEPENDENCY-BLOCKED | `FULL_EVENT_FEATURE_CONTRACT.md` G2 and `FULL_EVENT_INTERFACE_REQUEST.md`; current binary is frozen while T1/T2 run. Gate requires full muon/event/recoil schema, stable keys, `MNV101_FULL_PHASE_SPACE=1`, and regenerated CV input. |
| T7 | Fresh full-schema P3F endpoints for publication PET laterals | `agent-C-fps` after T6, preserving its FPS ownership | DEPENDENCY-BLOCKED | Current P3F endpoints are reduced-schema and may only feed `pet-reduced-fps-cross`; `P5B_LATERAL_SOURCE_DECISION.md` adopts fresh option (b) for `pet-fullevent-fps-v1`. Requires T6, then 5×2×12 regenerated endpoints and proof battery. |
| T8 | P5B publication full-event FPS nominal and UQ chain | `agent-B-p5b` | DEPENDENCY-BLOCKED | Requires T5, T6, T7, and the recovered hard background-treatment gate: the user's locked 2026-07-11 choice is literal background-cloud injection plus Stay-Positive (`negweight-refined`), with purity only as a matched control. Freeze and prove that target before nominal; then execute floor, coherent C_stat, PET C_ML, joint vertical/flux response, selection-complete laterals, matched total covariance, and projections/comparisons. No recoil-PET block transfers. |
| T9 | Rebuild final projections/significances | owner to be assigned after upstream closure | DEPENDENCY-BLOCKED | Publication runbook P7; requires corrected scalar adoption (T1/T3) and P5B (T8), with exact `M C M^T`, PSD/order/rank checks and committed summaries. |
| T10 | Publication document closeout and freeze candidate | note/Overleaf role only after production closes | DEPENDENCY-BLOCKED | Publication runbook P8; requires T9 plus no unresolved publication blocker, clean note/primer/paper builds, provenance audit, and committed document closeout. |
| T11 | Negweight background treatment and optional Gregor representation refinement | negweight: `agent-B-p5b`; Gregor: unassigned | SPLIT: NEGWEIGHT HARD-GATED; GREGOR DEFERRED | `bkg_negweight_state.md` proves the user already chose full PET injection + Stay-Positive on 2026-07-11. The migration plan's optional/post-baseline placement was stale and is corrected by `MIG-DEC-NW`: negweight now blocks T8 nominal. Gregor remains explicitly deferred and cannot substitute for T8. |

Reset routing: one flock-protected watcher is armed for 2026-07-18 13:00:30
UTC via `resume_after_school_reset.sh`. It resumes the existing registry roles
in critical-path order C repair-only → A → B and records provider artifacts through
`agentctl.py`; it does not create or substitute a worker.

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
