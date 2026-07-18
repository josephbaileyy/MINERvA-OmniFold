# Migration takeover status — fe-fps campaign

Live orchestration checklist for the Codex takeover. This file records only
ownership, dependency state, and evidence pointers; verified scientific
numbers remain canonical in `VALIDATION_LEDGER.md`, and round receipts remain
canonical in `RUNS.tsv`.

Last reconciled: 2026-07-18 11:29 UTC. Registry:
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
in holder-deadline order A repair/reconcile → C repair-only → B F7 and records
provider artifacts through `agentctl.py`; it does not create or substitute a worker.
The order changed in `MIG-WAKE2` after the negweight audit made C production ineligible
while A's holder retained a 13:50 UTC wall.

## Dispatch preflight — providers and compute placement

Before every provider dispatch wave, run `usagectl.py snapshot --json`; preserve both
personal Codex Full reset credits, treat missing/stale Claude and agy percentages as unknown,
and ledger any changed personal seven-day reset time. Usage monitoring never replaces,
forks, or concurrently messages a durable worker.

Before every compute launch, record a placement decision from current evidence:

1. Inspect `squeue`, the shared-allocation status, job ownership, remaining wall, resource
   fit, prerequisites, and output namespace.
2. Prefer the already-running **owner's** interactive holder for a single-node job that fits
   its remaining resources/wall. If an equivalent batch job was queued, cancel that exact
   duplicate before interactive execution so two writers cannot race.
3. Submit batch early when the job is a large array, multi-node, multi-hour beyond the holder,
   must outlive the session, or when a dependency-safe queue wait can overlap upstream work.
   Early submission is permitted only with immutable prerequisites or explicit scheduler
   dependencies and collision-free outputs; it cannot bypass a scientific/preflight gate.
4. Never use another worker's holder, start a second uncoordinated allocation, or interpret
   empty buffered stdout as a stalled job. Monitor artifacts, processes, and scheduler state.

Every launch receipt records interactive-versus-batch rationale, job/holder ID, owner,
dependency footing, and output paths. `MIG-DISPATCH1` makes this a campaign gate rather than
an informal preference.

Usage-helper implementation status: **VERIFIER-BLOCKED** (`MIG-V4`). Its two live Codex
reads are advisory evidence only; it is uncommitted and is not yet wired into the reset
watcher. The independent verifier confirmed no reset-credit mutation path, but found the
reserve/exit gate, numeric validation, subprocess I/O, Claude cache freshness, account-home
confinement, installer replacement guard, change tracking, Python invocation, and regression
suite insufficient. The same `usage-helper-verifier` session must PASS the repaired helper
before it becomes the sole automated pre-dispatch gate.

## Publication-grade evidence audit

This table is an index and verdict layer, not a second home for scientific facts.
Canonical requirements remain in `KNOWN_ISSUES.md`, `docs/OPEN_ITEMS.md`, the P0–P8
publication runbook, `pet/FULL_EVENT_FEATURE_CONTRACT.md`, and the workstream STATUS/RUN_LOG
files. A gate is PASS only when its direct evidence and repository-mandated receipt are
committed and pushed. A successful job, readable ROOT, plausible number, or uncommitted plan
is insufficient.

| Gate | Current verdict | Direct evidence required for PASS | Durable owner / pointer |
|---|---|---|---|
| PG0 — provenance and worktree reconciliation | **PLAN-VERIFIER BLOCKED** | Exact ownership/inventory/hashes for every reusable input and active output; no ambiguous writer; repaired runbook/dependency/remediation controls committed. `MIG-V3` independently found nine publication-material defects in the untracked controls: stale FPS/PET background footing, F7/G2/P3F/estimator ambiguity, additive PET-UQ ambiguity, legacy remediation masquerading as publication, stale 4D frontier, missing final-5D adoption, and canonical-home/durability violations. Same verifier must PASS the repairs. | orchestrator + file owners; runbook P0; `MIG-PUB-AUDIT1`, `MIG-V3` |
| PG1 — estimator/domain/background definition | **PARTIAL; PRODUCTION BLOCKED** | One frozen `pet-fullevent-fps-v1` contract: extended FPS domain, full schema, explicit `negweight-refined`, literal aligned background injection, Stay-Positive, seed/config/fingerprint policy shared by central and every covariance component. | Agent B; `ROLLOUT-PLAN.md` Stage 2.5; `pet/FULL_EVENT_FEATURE_CONTRACT.md`; `MIG-DEC-NW{,-FPS}` |
| PG2 — PET engine correctness | **BLOCKED ON F7 + TARGET INTEGRATION** | F2/F3 GPU regression and cap sensitivity; F7 factors drawn over full data/signal/background inventories before subsetting; background draw before per-replica refinement; exact replay/extraction identity; no Horovod path. | Agent B; T5; feature contract CLM-008 |
| PG3S — standard selection-complete scalar lateral | **PREFLIGHT-BLOCKED; COMPUTE ACTIVE** | Exact 10-endpoint inventory/config/migration/order proofs; atomic completion; five MAT components; complete support comparison; same-verifier PASS; scoped candidate commit. | Agent A + `standard-p4-verifier`; T2 / `MIG-V2` |
| PG3F — scalar FPS selection-complete lateral | **BACKGROUND-MODE/PREFLIGHT-BLOCKED** | Separate 10-endpoint `negweight-refined` inventory with mode-stamped atomic outputs; exact mask/order/config; five nonzero components; same-verifier PASS; purity controls excluded. | Agent C + `fps-adopt-verifier`; T1 / `MIG-V1`, `MIG-DEC-NW-FPS` |
| PG4 — corrected scalar adoption/projection | **DEPENDENCY-BLOCKED** | Pure-component replacement without subtraction ambiguity; exact component identity; reproducible unified adoption; nonmutation hashes; exact width-weighted `M C M^T`; PSD/symmetry/finite gates. | T3 plus T1/T2 owners; runbook P4/P6 |
| PG5A — publication full-event FPS CV/nominal | **DEPENDENCY-BLOCKED** | G2 full-schema branches and stable keys; regenerated CV input with background clouds/scalars/weights; exact alignment/native-miss/edge/order proofs; negweight-refined pilot, stress and ordinary closure; nominal/floor manifest and commit. | Agent B interface/estimator; T6 and Stage 2.5; runbook P5A |
| PG5B-source — full-schema shifted endpoints | **DEPENDENCY-BLOCKED** | Fresh five-band × two-endpoint × twelve-playlist full-schema P3F products after G2; exact event/cloud/background joins, migration census, hashes, and commit. Reduced-schema endpoints remain controls. | Agent C after G2; T7; runbook P3F/P5B |
| PG5B-UQ — publication PET covariance | **DEPENDENCY-BLOCKED** | Fresh coherent C_stat, crossed C_ML, joint end-to-end vertical/flux response, selection-complete lateral retraining, common fingerprint/mask/order/central, complete manifests, no recoil/P1 component transfer. | Agent B; T8; runbook P5B |
| PG6 — covariance mathematics and assembly | **NOT YET TESTABLE ON FINAL PRODUCTS** | Exact component inventories and sums; declared mean centering/mean shifts; finite/symmetric/PSD/rank gates; no double count; exact 5D→4D projection; independent reconstruction from final products/manifests. | owning producer + independent verifier; runbook P4–P7 |
| PG7 — physics comparisons/coverage | **DEPENDENCY-BLOCKED** | Frozen central/covariance provenance; supported/dead-cell tiering; prior envelope and coverage; matched-domain scalar/PET comparisons; generator significances with full covariance. | future P7 owner; T9 |
| PG8 — publication freeze | **DEPENDENCY-BLOCKED** | Ledger/RUN_LOG/STATUS receipts for every result; clean note/primer/paper builds; figure/value provenance; Overleaf/GitHub synchronization; no unresolved publication blocker. | future document owner; T10; runbook P8 |

Publication-final is prohibited until every PG gate is PASS. Evidence-blocked gates remain
visible; they are never waived by downstream numerical agreement.

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
