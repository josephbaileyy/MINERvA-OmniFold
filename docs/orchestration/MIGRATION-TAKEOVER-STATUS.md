# Migration takeover status — fe-fps campaign

Live orchestration checklist for the Codex takeover. This file records only
ownership, dependency state, and evidence pointers; verified scientific
numbers remain canonical in `VALIDATION_LEDGER.md`, and round receipts remain
canonical in `RUNS.tsv`.

Last reconciled: 2026-07-18 21:24 UTC. Registry:
`state/sessions.json`. Immutable source snapshot: `MIGRATION-HANDOFF.md` plus
`MIGRATION-DELTA.md`.

| ID | Handoff item | Durable owner | State | Evidence / next gate |
|---|---|---|---|---|
| T0 | Adopt migrated delegates and prove provider continuity | orchestrator | CLOSED | Exact A/B/C UUIDs adopted; one memory-only continuity response each; `RUNS.tsv` `MIG-CONT-{A,B,C}`; commit `42c1fd7`. Old root is a file handoff; Agent D was not adopted because its UUID is unconfirmed. |
| T1 | FPS P4/P6 final adoption (handoff X5) | `agent-C-fps` / UUID `4580f42d-…`; independent verifier `fps-adopt-verifier` / `019f74bb-…` | PURITY QUARANTINED; REPAIR-2 VERIFIER-BLOCKED | C committed/pushed repair-2 `fdf6238`: 41/41 helper tests, full merged hashes, exact 266/285 mask, purity controls quarantined, and no production. The same verifier returned rc=0/BLOCK: manifest-builder incompatibility, non-recomputed artifact hashes, optional/under-bound transition receipts, unsafe batch/interactive launchers, incomplete unified mean/mask/central binding, and insufficient CLI/durability tests. No negweight-refined endpoint, covariance, or adoption is authorized; resume only the same C UUID for repair-3. |
| T2 | Standard P4 selection-complete lateral candidate (handoff X6) | `agent-A-standard` / UUID `14951826-…`; independent verifier `standard-p4-verifier` / `019f74cb-…` | 10/10 VALID; REPAIR-3 VERIFIER-BLOCKED | A committed/pushed repair-3 `74fa362`: 28/28 helper tests and no candidate/product. The same verifier returned rc=0/BLOCK: disconnected driver and stale CLIs, unsafe merge/unfold resume receipts, internally inconsistent manifest with a dirty-source hash, separable candidate/adoption provenance, incomplete projection geometry binding, and missing real-driver integration tests. No candidate is authorized; resume only the same A UUID for repair-4. |
| T3 | Replace the support-limited lateral in the repaired R1 corrected-4D candidate | unassigned in handoff; orchestrator must assign without changing A/C ownership | DEPENDENCY-BLOCKED | Requires T2's validated standard active-lateral block. The handoff explicitly records this follow-on as unassigned; no adoption or promotion before T2 closes. |
| T4 | Consolidated BEN note for the four recurring operational failures | orchestrator | OPEN | Write after T1/T2 receipts so the note includes the final wall/holder outcomes: interactive-QOS latency; explicit job-ID/node ownership; detached drivers (BEN-024); completeness-validated resume (BEN-023). |
| T5 | F7 coherent global Poisson bootstrap before any P5B C_stat replica | `agent-B-p5b` / UUID `46e4af3e-…` | CODE/STATIC INTERFACE PASS; RUNTIME EVIDENCE BLOCKED | B committed/pushed `0c7c26d`; 35/35 ROOT-free tests cover background tamper/omission, exact data/signal/background global-before-subset replay, G2-only schema/alignment/order, atomic NPZ output, and fail-closed publication config. The same agy session returned rc=0/PASS for that static scope. Runtime remains fail-closed until Agent E builds/smokes the G2 background-cloud ROOT and B creates an aligned full-schema NPZ with literal background clouds/scalars/`w_bkg`. No PET nominal or replica is authorized. |
| T6 | G2 full-event C++ dump branches plus regenerated FPS CV point-cloud loops | `agent-E-g2-source` / UUID `44b634fc-…` (Claude-personal) owns C++ source; Agent B retains Python/PET interface | SOURCE PASS; OWNER PROVIDER-CAPPED; RUNTIME/PRODUCTION BLOCKED | E committed/pushed exact four-file source packet `486e53e`; 474 static checks PASS and independent agy source review PASS. The same-UUID interactive build/smoke turn then hit an explicit Claude-personal monthly spend limit before acquiring an allocation; no reset time was supplied and no state changed. Preserve E and resume it when that provider is available/limit is raised. No replacement, 12-playlist batch, MEFHC NPZ, or PET training. |
| T7 | Fresh full-schema P3F endpoints for publication PET laterals | `agent-C-fps` after T6, preserving its FPS ownership | DEPENDENCY-BLOCKED | Current P3F endpoints are reduced-schema and may only feed `pet-reduced-fps-cross`; `P5B_LATERAL_SOURCE_DECISION.md` adopts fresh option (b) for `pet-fullevent-fps-v1`. Requires T6, then 5×2×12 regenerated endpoints and proof battery. |
| T8 | P5B publication full-event FPS nominal and UQ chain | `agent-B-p5b` | DEPENDENCY-BLOCKED | Requires T5, T6, T7, and the recovered hard background-treatment gate: the user's locked 2026-07-11 choice is literal background-cloud injection plus Stay-Positive (`negweight-refined`), with purity only as a matched control. The current dumper/launcher path is now explicitly BLOCKED until it carries the aligned background inventory and rejects recoil/purity inputs. Freeze and prove that target before nominal; then execute floor, coherent C_stat, PET C_ML, joint vertical/flux response, selection-complete laterals, matched total covariance, and projections/comparisons. No recoil-PET block transfers. |
| T9 | Rebuild final projections/significances | owner to be assigned after upstream closure | DEPENDENCY-BLOCKED | Publication runbook P7; requires corrected scalar adoption (T1/T3) and P5B (T8), with exact `M C M^T`, PSD/order/rank checks and committed summaries. |
| T10 | Publication document closeout and freeze candidate | note/Overleaf role only after production closes | DEPENDENCY-BLOCKED | Publication runbook P8; requires T9 plus no unresolved publication blocker, clean note/primer/paper builds, provenance audit, and committed document closeout. |
| T11 | Negweight background treatment and optional Gregor representation refinement | negweight: `agent-B-p5b`; Gregor: unassigned | SPLIT: NEGWEIGHT HARD-GATED; GREGOR DEFERRED | `bkg_negweight_state.md` proves the user already chose full PET injection + Stay-Positive on 2026-07-11. The migration plan's optional/post-baseline placement was stale and is corrected by `MIG-DEC-NW`: negweight now blocks T8 nominal. Gregor remains explicitly deferred and cannot substitute for T8. |

Reset routing: both the 13:00 and 18:00 A→C→B waves completed without replacement.
The 18:00 producer snapshotted and heartbeat-checked the shared school account before
each role, returned `overall_rc=0` at 18:56 UTC, and released its advisory lock. A
real reset-log event triggered exactly one external `codex exec resume`; it exited 0.
The quiet mechanism generated no autonomous LLM turns after goals were blocked. A,
C, and B all returned rc=0 under their original UUIDs; the same standard/FPS verifiers
returned BLOCK and the same agy PET verifier returned static-scope PASS. Receipt:
`state/qp4-closure-20260718.json`; ledger rows `MIG-A4`, `MIG-V2R3`, `MIG-C3`,
`MIG-V1R2`, `MIG-B3`, `MIG-AGY19`, and `MIG-QP4`.

Scheduling is now an explicit workstream in `SCHEDULING-STRATEGY.md`.
`MIG-AGY15` identifies the publication critical path and independent lanes.
The first-start-wins hash experiment selected interactive job 56090877; its
pending batch loser was canceled. The winner completed 20/20 full SHA256s over
the exact standard/FPS merged inventories (1,286,623,855,676 bytes) in 25m25s.
Paths, pre/post size+mtime inventories, unique digests and clean skip validate;
launcher, atomic receipt, validation, RUNS/STATUS and A/C reuse instructions
land together under the commit gate.
Placement postmortem: the original shared job had already started before it was
canceled to retrofit the hedge. That was a routing error, not a compute/result
error. The policy now treats any healthy RUNNING route as the winner and favors
one-shot batch when a held node has no ready follow-on workload.
Historical `sacct` telemetry is now reproducible (`MIG-SCHED3`): across 1,460
task-weighted rows, eligible-queue p50/p90 were 0/0.4s interactive,
1,527/5,432s regular CPU, 5,087/22,418s shared GPU, and 8,785/46,685s shared
CPU. These observations drive queue-early placement but are not ETA promises.
Provider/account telemetry is also reproducible (`MIG-SCHED4`): agy is the
fastest cheap preflight/red-team route but had two rejected ownership
overclaims; Codex accounts remain the deep continuity verifiers; shared Claude
remains the A/B/C implementation lane; capped Claude-personal E is preserved.
Successful turns are availability evidence only, never invented capacity.

PG0 ownership was re-audited fail-closed (`MIG-AGY16`–`MIG-AGY18`,
`MIG-PG0-ADJ`). Two agy PASS recommendations were rejected because they
mistook a read-only verifier's file readback for authorship. Direct prompt/log
and mtime evidence proves the four-file canonical/reorganization packet predates
that verifier and has no durable writer UUID or write receipt. Those files stay
untouched; every active worker uses exact-path staging and co-located receipts.

## Dispatch preflight — providers and compute placement

Before every provider dispatch wave, run the complete unfiltered `usagectl.py snapshot --json`;
preserve the one remaining August-12 personal Codex Full reset credit, treat missing/stale
Claude and agy percentages as unknown,
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
4. Never use another worker's holder, start a second uncoordinated allocation, or interpret
   empty buffered stdout as a stalled job. Monitor artifacts, processes, and scheduler state.

Every launch receipt records interactive-versus-batch rationale, job/holder ID, owner,
dependency footing, and output paths. `MIG-DISPATCH1` makes this a campaign gate rather than
an informal preference.

Usage-helper implementation status: **SAME-VERIFIER PASS; COMMITTED AND PUSHED**
(`MIG-V4R`, base hardening `0d6c4dc`; shared-school alias hardening `cf89afb`).
The repaired helper is fail-closed on reserve uncertainty and required-account errors,
strictly validates provider shapes/numerics/epochs, bounds nonblocking app-server I/O,
tracks integrity-protected per-window Claude freshness, confines distinct account homes,
protects existing status-line settings, records rolling changes, pins `/usr/bin/python3.11`,
and passes the expanded 38-test battery. After live personal usage reached 0%, the explicitly
authorized July-31 credit was consumed and the policy was advanced to protect the sole
August-12 reserve. The 21:20 UTC unfiltered live gate reports personal at 73% remaining
with exact reset 2026-07-25 14:36:14 UTC; the August-12 Full reset remains available and
protected. The consumed July-31 credit and available August-12 credit are the exact statuses
of the two historical Full reset credits; no further reset action is authorized.

### Measured provider routing

| Account/provider | Current measured behavior | Campaign routing rule |
|---|---|---|
| Claude school (`claude-school` + `claude-school-legacy`) | One shared account, not two. Cache is stale, hence percentage unknown; all four disposable heartbeats in the completed 18:00 wave succeeded. | Continuity-bound A/B/C only; use a disposable flat-home heartbeat before each substantial legacy-role turn while percentage remains unknown. Never sum aliases. |
| Claude personal | Percentage cache is stale/unknown. E completed source at 14:32 UTC, then the 14:42 runtime turn hit an explicit monthly spend limit with no reset time. | Provider-constrained: preserve `agent-E-g2-source` and its UUID; do not replace/fork. Resume build/smoke only after a successful same-account availability check or the user raises the monthly limit. |
| Codex personal | 73% seven-day remaining at 21:20 UTC; exact reset 2026-07-25 14:36:14 UTC; five-hour window absent/unknown. July-31 Full reset is consumed under prior explicit authorization; August-12 Full reset is available/protected. | Preserve for orchestration/synthesis and same-verifier continuity. No reset credit is authorized for consumption. |
| Codex school | 19% seven-day remaining; exact reset 2026-07-24 02:51:01 UTC; five-hour window absent/unknown. | Constrained: use only where same-verifier continuity is scientifically material, after an agy preflight reduces wasted turns. |
| agy | No percentage API; nineteen persistent-session audits/rechecks completed without a cap signal. Its first two PG0 ownership verdicts overclaimed provenance and were rejected; the same session corrected to BLOCK on direct evidence. | Availability evidenced by the successful 18:56 PET recheck. Use for orthogonal red-team, gap audits, scheduling studies, and cheap preflight, but independently validate ownership/authorization claims; it never substitutes for a named continuity-bound owner/verifier. |

## Publication-grade evidence audit

This table is an index and verdict layer, not a second home for scientific facts.
Canonical requirements remain in `KNOWN_ISSUES.md`, `docs/OPEN_ITEMS.md`, the P0–P8
publication runbook, `pet/FULL_EVENT_FEATURE_CONTRACT.md`, and the workstream STATUS/RUN_LOG
files. A gate is PASS only when its direct evidence and repository-mandated receipt are
committed and pushed. A successful job, readable ROOT, plausible number, or uncommitted plan
is insufficient.

| Gate | Current verdict | Direct evidence required for PASS | Durable owner / pointer |
|---|---|---|---|
| PG0 — provenance and worktree reconciliation | **CONTROL LOGIC PASS; CANONICAL INDEX/DURABILITY EVIDENCE-BLOCKED** | The same `publication-plan-verifier` PASSed the repaired runbook/DAG. Direct audit shows dirty `OPEN_ITEMS`, `KNOWN_ISSUES`, ND STATUS, and untracked `POST_PUBLICATION_REORG_PLAN.md` have no durable writer UUID/write receipt; their mtimes predate the read-only verifier that later observed them. Two agy ownership PASSes were rejected and corrected to BLOCK. Preserve all four untouched; exact-path staging and co-located receipts only. Publication-final remains prohibited pending real owner evidence or explicit user reconciliation authority. | orchestrator + unknown historical file owners; runbook PG0; `MIG-PUB-AUDIT1`, `MIG-AGY16`–`MIG-AGY18`, `MIG-PG0-ADJ` |
| PG1 — estimator/domain/background definition | **PARTIAL; PRODUCTION BLOCKED** | One frozen `pet-fullevent-fps-v1` contract: extended FPS domain, full schema, explicit `negweight-refined`, literal aligned background injection, Stay-Positive, seed/config/fingerprint policy shared by central and every covariance component. | Agent B; `ROLLOUT-PLAN.md` Stage 2.5; `pet/FULL_EVENT_FEATURE_CONTRACT.md`; `MIG-DEC-NW{,-FPS}` |
| PG2 — PET engine correctness | **F7 CODE/STATIC INTERFACE PASS; FULL-SCHEMA RUNTIME EVIDENCE BLOCKED** | F2/F3 GPU regression and cap sensitivity; F7 factors drawn over full data/signal/background inventories before subsetting; background draw before per-replica refinement; exact replay/extraction identity; no Horovod path. Commit `0c7c26d` and same-agy static PASS are durable; G2 literal background ROOT/NPZ runtime evidence remains. | Agent B; T5; feature contract CLM-008; `MIG-B3`/`MIG-AGY19` |
| PG3S — standard selection-complete scalar lateral | **10/10 VALID; REPAIR-3 VERIFIER-BLOCKED** | Exact 10-endpoint inventory/config/migration/order proofs; atomic completion; pure named components; deterministic projection; same-verifier PASS; scoped candidate commit. Repair `74fa362` is durable but the same verifier found six executable/provenance/integration defects. No candidate. | Agent A + `standard-p4-verifier`; T2 / `MIG-A4`/`MIG-V2R3` |
| PG3F — scalar FPS selection-complete lateral | **PURITY QUARANTINED; REPAIR-2 VERIFIER-BLOCKED** | Separate 10-endpoint `negweight-refined` inventory with mode-stamped atomic outputs; full merged hashes; exact mask/order/config; five nonzero components; mandatory downstream manifests; same-verifier PASS. Repair `fdf6238` is durable but the same verifier found six fail-closed transition/launcher/provenance defects. | Agent C + `fps-adopt-verifier`; T1 / `MIG-C3`/`MIG-V1R2` |
| PG4 — corrected scalar adoption/projection | **DEPENDENCY-BLOCKED** | Pure-component replacement without subtraction ambiguity; exact component identity; reproducible unified adoption; nonmutation hashes; exact width-weighted `M C M^T`; PSD/symmetry/finite gates. | T3 plus T1/T2 owners; runbook P4/P6 |
| PG5A — publication full-event FPS CV/nominal | **G2 SOURCE PASS; RUNTIME/INPUT DEPENDENCY-BLOCKED** | G2 source `486e53e` and independent review are durable. Still required: canonical compile plus 1A runtime smoke, regenerated CV input with background clouds/scalars/weights, exact alignment/native-miss/edge/order proofs, negweight-refined pilot, stress and ordinary closure, nominal/floor manifest and commit. | Agent E runtime source gate then Agent B interface/estimator; T6 and Stage 2.5; runbook P5A |
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
  use the other's holder. Only Agent E may mutate the canonical C++ binary, and
  only after live evidence shows no active A/C/production writer; freeze it again
  before any playlist array starts.
- Update `RUNS.tsv` after every worker round and land each campaign result with
  its required STATUS/RUN_LOG/ledger receipts in the same commit.
