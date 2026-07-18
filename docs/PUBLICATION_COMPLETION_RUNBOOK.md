# Publication completion runbook

**Instructions only; never a run receipt.** Current completion state belongs in
`OPEN_ITEMS.md` and the dimensional STATUS files, verified numbers in
`../VALIDATION_LEDGER.md`, bugs in `../KNOWN_ISSUES.md`, and chronology in the
RUN_LOGs. This runbook defines gates and packet boundaries only.

No packet below is authorized until PG0 ownership and durability pass: every
input campaign needed by that packet must have a scoped commit, and no result
may be consumed before its summary, ledger entry, RUN_LOG entry, and STATUS
one-liner land in the same commit as its launcher/code. An uncommitted artifact
is provisional even if it is complete on disk.

## Locked estimator decisions

These are preconditions, not choices left to an executing worker.

1. Scalar FPS/N-D production uses explicit `--bkg-mode negweight-refined`.
   Every launcher, manifest, summary, output namespace, and covariance component
   must record that mode. Purity products are matched controls only.
2. Publication PET uses estimator ID `pet-fullevent-fps-v1` and literal aligned
   background-cloud injection at negative POT-scaled `w_bkg`, followed by the
   Stay-Positive refinement. `pet-reduced-fps-cross` and all recoil-only PET
   products are cross-checks, not sources for the publication covariance.
3. PET statistical replicas obey F7: draw coherent Poisson factors over the
   complete data, signal-MC, and background-MC inventories before any training
   subset is selected; apply the background factor before each replica's
   Stay-Positive refinement; reuse every applicable factor exactly at training
   and extraction; persist seeds, factors or replayable factor hashes, and full
   inventory manifests. Nominal refined weights may not be reused by a replica.
4. PET vertical, flux, and detector components use complete joint physical
   variation plus retraining where the nuisance can change the learned map.
   There is no additive `C_syst(frozen map) + C_retrain` construction for the
   same nuisance.

The locked background decision is indexed in
`../2d-unfolding/HANDOFF_bkg_negweight/bkg_negweight_state.md`; the PET feature
and joint-UQ contract is in
`../nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md`.

## Execution preflight for every packet

Before launch, resume, merge, or adoption:

1. Read `../KNOWN_ISSUES.md`,
   `../2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, the relevant STATUS and production
   tracker, and `RESULT_DEPENDENCY_AND_RERUN_MAP.md`. PET work also reads
   `../nd-unfolding/PET_UQ_REMEDIATION_STATUS.md` and the full-event contract.
2. Record source commit, dirty-path ownership, input manifests, estimator and
   background-mode fingerprints, target namespace, and output validation
   command. Never stage another session's changes.
3. Inspect `squeue`, `sacct`, and existing allocation receipts. Decide from live
   evidence whether the work belongs on an existing owner-held interactive node
   or in batch. Use interactive for a single-node task that fits the remaining
   wall; queue dependency-safe arrays, multi-hour, multi-node, GPU, or
   shell-independent work early. Never launch two writers for one namespace.
4. Refuse a nonempty output target unless a content validator proves it is the
   exact completed unit expected by the current manifest. A size-only
   `skip-if-exists` is forbidden. Producers write to a unique temporary path and
   atomically rename only after validation.
5. Use the installed event-loop binary, per-playlist execution, and the canonical
   environment. Do not use a build-tree binary or a combined MEFHC event-loop
   manifest.
6. Keep old, control, and candidate outputs in distinct namespaces. Promotion is
   a validated adoption action, never an overwrite or relabel.

## Packet PG0 — ownership, provenance, and control freeze

**Purpose:** make the plan itself durable before dependent production.

- Attribute every dirty/untracked campaign path to an owner.
- Reconcile completed campaigns one at a time; do not rerun physics to repair a
  missing summary.
- Commit the locked negweight/PET decisions and the canonical OPEN_ITEMS/STATUS
  indexes before a descendant relies on them.
- Independent gate: the publication-plan verifier must return PASS on this
  runbook, the dependency map, and the PET remediation DAG.

**Output:** scoped control commit(s), with no scientific promotion.

## Packet P3S — selection-complete standard lateral endpoints

**Purpose:** replace only the support-limited standard lateral component used by
the scalar 5D chain.

- Promote each declared kinematic endpoint through selection, IDs,
  backgrounds, native misses, merge, and unfold.
- Require an exact endpoint inventory, asymmetric endpoint identity, universe
  metadata, central/config fingerprint, nonempty-tree checks, and a hardened
  content validator.
- Existing central, vertical, statistical, ML, and corrected joint-throw
  components are read-only inputs after their hashes and summaries validate.

**Output:** a committed standard lateral-component packet. It does not itself
adopt final 5D or 4D covariance.

## Packet P3F-scalar — scalar FPS `negweight-refined` production

**Purpose:** build the scalar FPS central and selection-complete endpoints on the
locked background footing.

- Existing purity-footed FPS central/component/unfold files are quarantined
  matched controls. Their event-loop inputs may be reused only if a validator
  proves they contain the required signal, data, background, universe,
  phase-space, and provenance information.
- Every unfold command explicitly passes `--bkg-mode negweight-refined`; no
  reliance on a default is allowed.
- Use a separate mode-stamped namespace and atomic output protocol. The manifest
  includes mode, phase-space edges, source ROOT hashes/content fingerprints,
  endpoint identities, estimator seed/config, and expected output set.
- Validate the Stay-Positive telemetry, target normalization, finite weights,
  reported-bin order, completeness, endpoint pairing, and exact inventory.

**Output:** committed scalar FPS central and component packets on the
`negweight-refined` footing. Purity artifacts remain controls.

## Packet G2 — full-event binary ownership and FPS-CV regeneration

**Purpose:** create the publication PET input schema without racing active C++
owners.

- Wait for all event-loop jobs using the frozen binary to drain and for the C++
  owner to hand off the file. Apply one coordinated branch/interface change and
  one installed-binary rebuild.
- Regenerate per-playlist FPS CV full-event point-cloud ROOTs with the extended
  FPS gate and the background clouds, scalars, keys, `w_bkg`, muon/event
  features, masks/types, and provenance required by
  `pet-fullevent-fps-v1`.
- Prove event-key and row alignment across data, signal, truth, and background;
  validate misses, denominator, reconstructed selection, exact extended edges,
  schema parity, no truth leakage in step 1, and installed-binary identity.
- The present reduced/recoil `xps2` inputs remain scaffolding/cross-checks.

**Output:** committed full-schema FPS CV roots/inputs and a frozen estimator
fingerprint. Neither PET nominal nor PET laterals may precede this packet.

## Packet P3F-PET — full-schema shifted PET inputs

**Purpose:** provide selection-complete detector endpoints for the same
publication PET estimator.

- Starts only after G2 and a committed P3F-scalar interface inventory.
- Regenerate shifted full-event clouds with the G2 schema; do not attach reduced
  clouds to a full-schema fingerprint.
- Require the same estimator feature schema, preprocessing, extended edges,
  background mode, key ordering, and input fingerprint as the publication CV,
  differing only by the declared endpoint.
- Before any publication nominal launch, require the exact five-band by
  two-endpoint by twelve-playlist inventory, event/cloud/background joins,
  migration census, hashes, schema identity, content validation, and commit
  receipt.
- P3S standard outputs and purity-footed FPS outputs are regression controls
  only.

**Output:** committed, complete P3F-PET endpoint manifest and validated shifted
inputs.

## Packet P4 — scalar covariance adoption

### P4-5D

Assemble the final scalar 5D covariance from the already committed, validated
non-lateral components plus the P3S lateral replacement. The adoption packet
must contain:

- common central, reported-bin mask/order, estimator/background fingerprint,
  and component inventory;
- pre/post hashes proving no frozen component changed;
- exact block-sum/reconstruction checks, symmetry, PSD/eigen diagnostics,
  finite diagonal, and mean-shift records;
- tracked product summary plus ledger, RUN_LOG, and STATUS updates in the same
  commit.

### P4-4D

Do not rerun the corrected R1 4D throws or non-lateral components. Replace only
the selection-complete lateral component after P3S, then validate and re-adopt
the independent 4D covariance. If publication instead uses the exact 5D
marginal, label the independent 4D result as a cross-check.

### P4-FPS

Assemble scalar FPS covariance only from `negweight-refined`, mode-stamped
components produced or explicitly validated under P3F-scalar. No purity central
or purity covariance component may enter the adoption packet.

**Output:** separate committed adoption packets for each promoted estimator.

## Packet P5A — publication PET nominal and floor

**Prerequisites:** PG0, G2, the complete committed P3F-PET source manifest,
frozen `pet-fullevent-fps-v1` contract, and a validated literal-negweight target
builder. P3F-PET source production/validation precedes the nominal; endpoint
retraining and covariance construction follow the nominal.

Construct the measured target from aligned data events at positive data weight
and aligned background clouds at negative POT-scaled `w_bkg`, then run the
Stay-Positive refinement over the complete nominal target. Persist full
inventories, alignment proof, signed and refined normalization, clipped/floored
telemetry, and background-mode fingerprint.

Train and extract the full-event nominal; freeze its estimator fingerprint,
central vector, reported-bin mask/order, and extended-FPS edges. Run one matched
GPU-floor repeat before interpreting ensemble spreads. Ordinary closure,
omitted-muon stress closure, finite/full-coverage weights, exact marginals,
normalization, and cap-sensitivity gates must pass.

**Output:** committed nominal and floor. No reduced, recoil-only, or purity
component transfers.

## Packet P5B — publication PET uncertainty campaign

Every component uses the P5A central/mask/order and exact
`pet-fullevent-fps-v1` fingerprint.

1. **F7 `C_stat`:** generate complete data/signal/background Poisson draws
   before subsetting. Apply background factors before per-replica Stay-Positive;
   use the exact applicable MC/background factors in training and extraction;
   persist replay evidence and reject incomplete inventories. Center on the
   replica mean. Each replica is an independent single-rank job; Horovod and
   distributed rank slicing are prohibited. A pilot may test execution, but
   publication inventory size is predeclared before viewing the covariance.
2. **`C_ML`:** no Poisson variation. Use a predeclared crossed seed design and
   compare with the P5A floor.
3. **Vertical/flux `C_syst`:** for every nuisance that can alter the learned
   mapping, vary physical inputs and retrain jointly, then build covariance from
   those complete joint displacements. A frozen-map-only exception requires an
   explicit proof that the nuisance cannot change the mapping. Never add a
   separate retraining covariance for the same nuisance.
4. **Selection-complete `C_lateral`:** use only P3F-PET shifted full-schema
   inputs; perform the endpoint's physical variation, background refinement,
   retraining, and extraction jointly.
5. **Assembly:** declare nuisance ownership and independence/coupling before
   summation. Require exact component reconstruction, mean shifts, symmetry,
   PSD/eigen diagnostics, finite diagonal, and exact 5D-to-4D marginal checks.

The ordered targeted-versus-full universe decision is defined in
`../nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`; it may reduce unnecessary work
but may not weaken the joint-universe contract.

**Output:** committed PET component packets and final adoption packet. There is
no standalone additive `C_retrain` block.

## Packet P6 — projections and covariance-dependent analysis

Starts only from committed P4/P5B adoption summaries.

- Rebuild exact 2D, 3D, 4D, `(Eavail,W)`, and declared FPS/PET marginals using
  explicit projection matrices and bin-volume conventions.
- Validate `M C M^T` against direct block sums, order/mask metadata, symmetry,
  PSD, and normalization.
- Recompute generator comparisons and significances only from the governing
  adopted covariance. Preserve old values as provenance, not live claims.
- PET/scalar comparisons require the same extended FPS measurement domain and
  separate acceptance-supported versus prior-dominated reporting tiers.

## Packet P7 — publication documents and release freeze

- Update note, primer, paper, figures, tables, and release manifests only from
  committed summaries and the validation ledger.
- Build all three analysis-note targets and run link/reference/provenance checks.
- Complete blinded/full-author review, collaboration approvals, and external
  questions tracked in `OPEN_ITEMS.md`.
- Tag the immutable publication-results tree only after every cited artifact is
  reachable from a commit and release manifest.

Post-publication reorganization is outside this runbook and starts only after
that tag.

## Legacy recoil-PET boundary

Existing recoil-only nominal, floor, replicas, and covariance products remain a
labeled representation cross-check. Optional completion of its replica
inventory must use a legacy-only namespace and cannot satisfy, feed, or delay
P5A/P5B. Do not rerun completed legacy products merely to repair documentation.

## Independent final audit

Before publication synthesis, an independent verifier must confirm:

- all scalar FPS promoted inputs/components are `negweight-refined` and purity
  is control-only;
- PET uses literal background clouds, Stay-Positive, F7, full-schema G2/P3F,
  and one estimator fingerprint;
- joint PET nuisances contain retraining with no additive double count;
- corrected 4D non-lateral components were not rerun;
- explicit final 5D, 4D, FPS, and PET adoption packets exist;
- every skip was content-validated or atomic; and
- every scientific claim is committed with its canonical ledger/RUN_LOG/STATUS
  evidence.
