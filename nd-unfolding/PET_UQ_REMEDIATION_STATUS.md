# Publication PET UQ remediation status and ordered DAG

**Scope:** the publication full-event PET estimator
`pet-fullevent-fps-v1`. Current completion remains indexed in
`../docs/OPEN_ITEMS.md` and `ND_OMNIFOLD_STATUS.md`; verified numbers belong
only in `../VALIDATION_LEDGER.md`; chronology belongs in
`ND_OMNIFOLD_RUN_LOG.md`.

This file is an execution gate, not proof that a node passed. The exact feature
schema and joint-UQ definition are in
`pet/FULL_EVENT_FEATURE_CONTRACT.md`; the packet/commit contract is in
`../docs/PUBLICATION_COMPLETION_RUNBOOK.md`.

## Legacy boundary

The completed recoil-only PET nominal, floor, ensembles, and covariance are a
non-publication representation cross-check. Existing recoil inputs and scalar
purity-weight targets are not inputs to this DAG. Optional legacy replica work
uses its own namespace and cannot satisfy, feed, or delay any gate below. Do not
rerun completed legacy products to repair documentation.

The reduced full-event interface estimator `pet-reduced-fps-cross` is likewise
an interface/stress-closure cross-check. It cannot provide a central value,
lateral endpoint, or covariance component for `pet-fullevent-fps-v1`.

## Gate 0 — durable controls and ownership

Before any publication PET compute:

1. The locked background decision, full-event contract, dependency map, and
   runbook are committed and independently verified.
2. G2 has a named C++ owner. Existing event-loop jobs using the current binary
   have drained, the owner has handed off the source, and only one coordinated
   installed-binary rebuild is planned.
3. Output namespaces distinguish reduced/recoil controls, purity controls,
   full-schema candidates, and adopted products.
4. Every launch has an interactive-versus-batch decision based on live queue,
   resource, dependency, remaining-wall, and output-ownership evidence. No two
   jobs may write one namespace.

**Gate:** scoped control commit and independent publication-plan PASS.

## Gate 1 — G2 full-schema FPS CV input

**Current (2026-07-19): Gate 1 PASS.** Gate 1A per-playlist production and the
Gate-1B merged ROOT/full-schema NPZ are complete. Recovery job `56120687`
published the receipt-last P=12 NPZ; an independent validator recomputed its
SHA-256, all 42 member headers, three inventory identities, retained-domain
predicates, miss sentinels, extended edges, POT relationship, and source/code
bindings with zero failures. All twelve hash-bound ROOT/receipt pairs passed one
terminal validation, including exhaustive retained-domain receipts for recovered
1D/1E/1F/1P. Aggregate truth and signal rows are exactly equal at 49,906,108.
The no-clobber MEFHC merge passed exhaustive validation and binds 21,797 finite
out-of-domain rows for exclusion; the independently reviewed dumper enforces
`[0,30] x [0,120]` GeV before inventory construction. Gate-1B inventories are
49,152,885 signal, 4,116,128 data, and 564,591 background rows. Evidence:
`nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json` and
`docs/orchestration/state/g2-gate1b-npz-validation-20260719.json`. Next: Gate 2
literal `negweight-refined` target construction only; PET training remains blocked.

Regenerate the FPS CV point-cloud event loops and derived inputs with the exact
`pet-fullevent-fps-v1` schema. The source must include aligned data, signal MC,
truth MC, and background MC clouds plus event scalars/features, event keys,
masks/types, POT/weights, native misses, extended-FPS edges, and schema/binary
provenance.

Required proofs:

- `MNV101_FULL_PHASE_SPACE=1` and the declared full-event dump are embedded and
  verified;
- data/reco observable schema parity and distinct truth schema;
- event-key and row alignment, uniqueness, denominator/miss consistency, and
  reconstructed-selection identity;
- exact extended-FPS edges and reported-bin order;
- no truth-only feature enters step 1;
- background clouds carry the same reco schema needed for data-side injection,
  along with aligned `w_bkg`; and
- full-schema fingerprint differs from the reduced/recoil fingerprints.

**Gate:** committed G2 roots/inputs, content summary, interface tests, ledger,
RUN_LOG, and STATUS evidence. Present `xps2` recoil tensors remain scaffolding.

## Gate 2 — literal `negweight-refined` target

**Current (2026-07-19): Gate 2 PASS; Gate 3 not started.** The exact canonical
`u2d.refine_stay_positive` ran on the complete production G2 data-plus-literal-
background inventory. Receipt-last publication, an independent hash/configuration/
binned-telemetry validator, and the preserved agy promotion verifier all PASS.
The published target has 4,680,719 finite nonnegative rows, including 20 zeros,
and is bound to the frozen input and configuration. Evidence:
`nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json`,
`docs/orchestration/state/g2-gate2-runtime-independent-validation-20260719.json`,
and `docs/orchestration/state/g2-gate2-verifier-20260719.json`.

Build the measured-side training inventory from:

- aligned data events with their positive data weights; and
- aligned background clouds with negative POT-scaled `w_bkg`.

Apply the Stay-Positive refinement to that complete signed inventory. Do not
copy scalar purity weights, silently downweight only the data rows, or reuse a
nominal refined target in a bootstrap replica.

The target summary records:

- ordered data and background manifests and event-key alignment;
- POT scale and raw positive/negative sums;
- refinement configuration/fingerprint;
- refined normalization and clipping/floor telemetry;
- finite/non-negative post-refinement weights; and
- estimator ID, feature schema, extended edges, input hashes, and target mode
  `negweight-refined`.

**Gate:** an end-to-end fixture reaches training and extraction; signed and
refined targets reproduce their independently constructed binned checks; all
invalid/missing/misaligned background inputs fail closed.

## Gate 3 — committed full-schema P3F-PET source inventory

**Current (2026-07-20): Gate 3 PROMOTED PASS.** Slurm array `56169838`
(`0-119%16`) reached terminal state with all 120 elements COMPLETED/0:0.
Independent reconciliation confirmed the ownership bijection (120 receipt
JobIDRaw == 120 sacct JobIDRaw, no foreign/missing writer), all 120 PASS
ROOT/receipt pairs (superseded muon-validity checks confined to the frozen
validator's allowed set on playlists 1D/1E/1F/1P), on-disk validator/launcher
hashes matching the bindings, and complete per-task locks/logs/DONE markers.
The complete aggregate manifest
(`docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json`,
sha256 `306e5459`) is committed PASS and independently verified by the
owner-neutral agy verifier (rc=0, VERDICT PASS, concurring with the
orchestrator audit). Promotion receipt:
`docs/orchestration/state/p3f-pet-gate3-promotion-56169838.json`.
Nominal PET (Gate 4) remains prohibited pending its own launch-code gate and
explicit user authorization.

Before the publication nominal, regenerate and validate the complete
selection-shifted source inventory under the G2 full schema: five declared
kinematic bands by two endpoints by twelve playlists. Require exact event,
cloud, and background joins; selection/migration census; native-miss and
denominator evidence; source/input hashes; schema and estimator identity;
endpoint/playlist completeness; atomic content validation; and the scoped
commit receipt.

P3S standard endpoints, scalar-FPS purity unfolds, reduced-schema P3F, and
uncommitted full-schema files are controls only. This gate produces validated
shifted inputs, not endpoint-trained covariance. The latter follows the nominal
at Gate 8.

## Gate 4 — nominal and GPU floor

Train and extract one unbootstrapped publication nominal from the Gate-2 target
using the frozen estimator fingerprint. Freeze its central vector, reported-bin
mask/order, phase-space edges, seed/config policy, and extraction normalization.

Run one matched repeat to bound GPU nondeterminism before interpreting either
statistical or ML ensembles.

Required validation includes ordinary closure, the omitted-muon stress closure,
finite full-coverage weights, strict MC index/order, cap-sensitivity telemetry,
normalization, exact lower-dimensional marginals, and the acceptance-supported
versus prior-dominated reporting split.

**Gate:** committed nominal and floor packets. No UQ component may use a
different central/mask/order/fingerprint.

## Gate 5 — F7 coherent statistical replicas

For every replica, in this exact order:

1. Enumerate complete, ordered data, signal-MC, and background-MC inventories
   before any training subset. Each replica is an independent single-rank job;
   Horovod and distributed rank slicing are prohibited.
2. Draw one coherent Poisson factor per inventory member from a persisted,
   replayable replica seed policy.
3. Apply data factors to data weights, signal factors everywhere signal MC is
   used, and background factors to the negative background injection.
4. Run a fresh Stay-Positive refinement for that replica after applying the
   background factors.
5. Select the training subset without redrawing, shortening, or reindexing the
   full factors.
6. Reuse the exact applicable signal/background factors during full extraction
   and completeness/count construction.

Persist full inventory hashes, seeds, factor hashes or replayable factors,
subset indices, train/extract identity checks, target/refinement telemetry, and
completion status. A missing unit invalidates the replica; a missing replica
invalidates the declared ensemble manifest. Center `C_stat` on the accepted
replica mean.

Run a small pilot only to validate the machinery. Declare the publication
replica inventory before viewing its covariance and compare its spread with the
Gate-4 floor.

## Gate 6 — PET-specific ML ensemble

Use the nominal target with no Poisson fluctuation. Vary only the predeclared
crossed training/subsample/split and estimator seeds. Persist all seeds and
completed extractions; center on the ensemble mean and compare with the GPU
floor. Scalar GBDT ML ensembles do not substitute for this component.

## Gate 7 — targeted joint systematic retraining decision

Publication vertical/flux systematics are joint end-to-end variations. For a
nuisance `u` that can change the learned mapping:

```text
delta_u = x_u(varied physical input + universe-specific background refinement
              + retrained estimator) - x_CV
```

The component is constructed directly from the declared joint shifts. Do not
build or add separate frozen-map and retraining covariances for the same
nuisance; they share the nuisance and would omit/corrupt their cross term.

First run a predeclared targeted set spanning dominant model, flux, and
kinematic behaviors. Compare the joint retrained displacement with the matched
frozen-map diagnostic only to decide expansion. Declare trace and tail
materiality thresholds before looking at results and bound the GPU floor.

- If the learned-map response is immaterial for a documented nuisance, a
  frozen-map-only treatment is allowed only with the proof and bound in its
  component summary.
- If material for selected bands, expand those complete bands/endpoints.
- If broadly material, expand to the full applicable universe inventory.

This gate controls cost, not estimator definition: every adopted endpoint is
still a complete joint variation, and every universe repeats the literal
background injection plus Stay-Positive construction.

## Gate 8 — full-schema selection-complete laterals

Consumes only the committed Gate-3 P3F-PET source manifest. For every declared
lateral endpoint, carry its shifted selection, event membership, background
target, native misses, and full-event input into joint background refinement,
retraining, and extraction.

P3S standard endpoints, scalar-FPS purity unfolds, and reduced-schema P3F
artifacts are controls only. Every accepted endpoint must share the nominal
estimator fingerprint and differ only by the declared physical variation.
Build the lateral component from the complete asymmetric endpoint inventory
under the experiment's declared centering convention, with a separate mean
shift record.

## Gate 9 — adoption and exact projections

Declare nuisance ownership and independence/coupling before covariance
assembly. On one matched central/mask/order/fingerprint, assemble only:

```text
C_total = C_stat + C_ML + C_syst_joint + C_lateral_joint
```

There is no separate additive `C_retrain`. Require exact component/block
reconstruction, common central and ordering, symmetry, PSD/eigen diagnostics,
finite diagonal, mean-shift diagnostics, extended-edge validation, and exact
5D-to-4D covariance projection.

Adoption also requires acceptance-supported/prior-dominated tier outputs,
coverage and prior-envelope controls, scalar/PET comparison only on a common
measurement domain, tracked product summary, and ledger/RUN_LOG/STATUS entries
in the same commit.

Until Gate 9 lands, label outputs by component and candidate fingerprint; do
not call them the final PET budget.

## Reuse/rerun matrix

| Item | Disposition |
|---|---|
| Recoil-only PET products and copied scalar purity targets | `QUARANTINE` cross-check; no transfer |
| Reduced full-event interface/stress products | `QUARANTINE` interface cross-check; no transfer |
| Extended-edge and reporting conventions | `REUSE` after exact contract/hash validation |
| Raw source AnaTuple inputs and per-playlist manifests | `REUSE` after provenance/availability checks |
| Existing FPS event-loop roots lacking full schema/background clouds | Insufficient for G2; do not relabel |
| G2 full-schema FPS CV roots/NPZ | `BUILD` once after binary drain/ownership gate |
| Literal signed/refined nominal target | `BUILD` from G2 inventories |
| Publication nominal and GPU floor | `BUILD` under one fingerprint |
| `C_stat` | `BUILD` with F7 full data/signal/background draws |
| PET `C_ML` | `BUILD` independently with no Poisson |
| Vertical/flux systematic component | `BUILD` from adopted joint end-to-end universes |
| P3F-PET source inventory | `BUILD` and commit after G2, before nominal |
| P3F-PET endpoint retraining/laterals | `BUILD` after nominal from Gate-3 inputs |
| Full per-universe retraining | `GATED` by targeted materiality, never assumed unnecessary |

## Atomicity and scheduler gate

Every unit writes a unique temporary artifact, runs its content validator, and
atomically renames only on success. Resume logic checks manifest completeness,
schema/fingerprint, and content—not file size. Partial artifacts are
quarantined.

Before each launch, inspect existing allocations and queues. Use an owner-held
interactive node for single-node work that fits its remaining wall; queue
dependency-safe arrays, long/GPU jobs, or work that must outlive the shell early.
Never duplicate a queued/running writer, and never cancel another worker's job
or allocation.
