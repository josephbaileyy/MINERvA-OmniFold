# Gregor PET2 and typed-object representations for MINERvA OmniFold

**Campaign:** `codex/gregor-pet2-omnifold`
**Evidence freeze:** 2026-07-23
**Status:** experimental assessment; publication G2 input unavailable

Verified campaign numbers belong in `VALIDATION_LEDGER.md`. This assessment
interprets them and points to the exact code, receipts, and orchestration
record; it does not create a second numerical authority.

## 1. Executive recommendation

The final recommendation is gated on the committed pilot summaries and final
auditor reassessment. Regardless of pilot outcome, this campaign cannot
authorize a publication-estimator replacement because the literal G2
publication NPZ and its bound target payload are unavailable.

The decision categories used below are:

- **include:** contract-safe and supported by the available evidence;
- **experimental:** useful to retain behind an opt-in interface, not a
  publication default;
- **neutral:** no material benefit at the preregistered pilot sensitivity;
- **harmful:** worse closure, stability, tails, ESS, or operational behavior;
- **defer:** plausible but missing required input/evidence;
- **exclude:** incompatible with the reco/data/background or OmniFold contract.

## 2. Scope and evidence levels

The campaign keeps five evidence compartments separate:

1. code-contract;
2. synthetic/fixture;
3. public Gregor dataset;
4. recoil-input pilot;
5. publication G2.

Only the fifth could support a publication-level choice. The exact
preregistration is
`docs/orchestration/gregor-pet2/EXPERIMENT_PREREGISTRATION.md`; orchestration
history and deviations are in
`docs/orchestration/gregor-pet2/CAMPAIGN_LEDGER.md`.

## 3. Exact sources and implementations inspected

### Gregor repository

- Repository: `gregorkrz/minerva-ml`.
- Requested pin:
  `af5d92ed2b3b448a09b6b7cf6b4f179e5757b4ed`.
- Upstream head at inspection:
  `fc9a099d3c9c060f03cef293c294f9de4eb019cd`.
- Inspection time: 2026-07-23T12:52Z.
- The model, preprocessing, dataloader, training, and checkpoint-loading
  sources relevant here are byte-identical at the pin and inspected head. The
  16 changed files are evaluation, plotting, jobs, or tests.
- Detailed file/line archaeology:
  `docs/orchestration/gregor-pet2/round1-gregor-source-archaeologist-FINDINGS.md`.

### Public dataset

- Dataset: `gregorkrzmanc/minerva-ml`.
- Immutable revision:
  `32e2f5040ff2678a2ef7ca1bc0b450b324f4fd83`.
- Public and ungated; dataset-card license CC-BY-4.0.
- Contains prepared 1A/1B MC-oriented ML rows. It has no complete real-data,
  background, miss/fake, physics-weight, or event-identity legs and is not an
  unfolding input.

### Experimental MINERvA implementation

- Package: `nd-unfolding/pet2_torch/`.
- Architecture label:
  `independent-pet2-small-concept-match-v1`.
- This is a clean, independent point-edge/attention implementation. It uses
  general architecture ideas, not copied Gregor/OmniLearned/HyperScale source,
  and is not checkpoint-compatible by name.
- The TensorFlow/Keras and recoil-only paths remain unchanged defaults.

## 4. Current MINERvA baselines

### A. Recoil-only PET

The current point-cloud estimator consumes reconstructed recoil tokens and
does not expose the reconstructed muon to the classifier. It remains a
cross-check, not a full-event publication result. `KNOWN_ISSUES.md` #19 is the
canonical status.

### B. TensorFlow/Keras full-event adapter

The existing adapter adds a continuous reconstructed-muon/event block to the
recoil cloud and conditions the PET classifier on it. Its full-event feature
and data contract is canonical in
`nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md`. The missing publication G2
payload prevents a matched full-statistics B comparison in this campaign.

### C–F. New experimental arms

- **C:** PyTorch PET2-family, random initialization, generic tokens, B-matched
  numeric footing where the input exists.
- **D-view:** C plus the already-dumped reconstructed detector-view category.
- **D-typed:** C plus real reconstructed object types. Unavailable in G2.
- **E-muon:** isolate reconstructed-muon globals.
- **E-rich:** add separately audited detector-observable globals.
- **F:** a bit-identical random parent initialized from an eligible
  checkpoint. Gregor's advertised weights are currently unavailable,
  unlicensed as weights, unpinned by checksum, and dimensionally unverified;
  no random or partial-load fallback is permitted.

## 5. Gregor PET2 architecture and representation

Gregor's `PET2` implementation lives under
`src/models/omnilearned/network.py`. The inspected small/medium/large presets
use base dimensions 128/512/1024, 8/16/32 heads, and 8/12/28 transformer
blocks. The MINERvA wiring supplies four kinematic values, a categorical PID,
five auxiliary token values, and a conditional global vector.

The prepared per-object row has ten columns:

1. eta;
2. phi;
3. `log(pT + 1e-6)`;
4. `log(E + 1e-6)`;
5. object/PID category;
6. transformed dE/dx;
7. x;
8. y;
9. z;
10. time.

The inspected object vocabulary is muon, photon, blob, three prong
hypotheses, aggregate blob, and aggregate prong. The sixteen global values
combine calorimetric/recoil summaries, Michel count, reconstructed-muon
presence, gamma-gamma invariant mass, charged-pion-prong count, and six
per-category energy sums.

These rows were built for supervised MC tasks. Their truth labels,
interaction categories, and prepared selection are not reco-side OmniFold
features.

### Upstream hazards that must not be copied

- The real muon uses PID 0 while the embedding declares
  `padding_idx=0`. The muon therefore shares the frozen padding row.
- The model reconstructs its attention mask from
  `log(pT + 1e-6) != 0`. A real object near the zero of that transform can be
  false-padded, and a muon-kinematics ablation can remove the token instead of
  only its kinematics.
- The prepared rows do not carry a stable event identity, physics weights,
  pass-reco/pass-truth, literal backgrounds, or native misses.

The experimental backend instead uses an explicit boolean mask and reserves
category 0 only for padding/unknown; every real category starts at 1.

## 6. Feature provenance, availability, and decision table

`reco` below means detector-observable Step-1 use. Truth-only fields may be
used only in Step 2.

| Candidate | Definition / units | Source and availability | Normalization / missing behavior | Risk and decision |
|---|---|---|---|---|
| Recoil token energy | Cluster energy; source MeV, adapter GeV | `part_reco_E`; signal/data/background | Explicit mask; pads zero after fitted train-only transform | Current baseline; **include** |
| Recoil position and z | Detector coordinates; source mm, adapter m | `part_reco_pos`, `part_reco_z`; all three reco inventories | Train-only fitted transform; no sentinel as physics | Current KNN geometry; **include** |
| Detector view | X/U/V reconstructed category | `part_reco_view`; all three reco inventories | 0 pad; real categories shifted/checked | Safe categorical ablation; **experimental D-view** |
| Recoil time | Reconstructed token time; exact unit/reference not audited | `part_reco_time`; all three inventories | Must define t0, unit, sentinel, universes | Modeling/leakage through missingness; **defer** |
| Reco muon momentum | px,py,pz,E in source MeV; phi in rad | `mu_reco_*`; signal/data/background | Missing reco rows mask the muon; never pass -9999 | Detector-observable; globals **include experimentally**; token form separate |
| Muon charge/q-p | sign and q/p convention | `mu_reco_qp`; all three inventories | Unit/zero convention unresolved | **defer** until unit audit |
| MINOS quality bit | reconstructed fit/match indicator | `mu_reco_minos_ok`; all reco inventories | Boolean; no manufactured truth counterpart | Detector-observable, systematics-sensitive; **include experimentally** |
| Reco vertex | x,y,z; source mm, adapter m | `vtx_reco_*`; all reco inventories | Missing reco masked; train-only fitted transform | Detector-observable but detector-model sensitive; **experimental** |
| Muon pT, p-parallel | reconstructed scalars in GeV | `sim*` / `measured*` cols 0–1 | Reco-pass fit; misses neutral-masked | Current full-event footing; **include** |
| Reco Eavail, q3 | reconstructed scalars in GeV | scalar cols 2–3 for all reco inventories | Same detector schema; reporting edges never inputs | Potential circular/model sensitivity; **experimental E-rich**, audit projections |
| Reco photon/blob/prong type | reconstructed object class | **not present in G2** | No legal missing-value fabrication | Core Gregor proposal; **defer D-typed** pending symmetric dump |
| Reco particle/PID hypothesis | dE/dx/tracking-derived hypothesis | **not present in G2** | Must reserve pad and define OOV | Generator/leakage risk if truth-derived; **defer if reco**, **exclude if truth** |
| Per-token dE/dx | reconstructed energy loss | **not present in G2**; upstream physical unit undeclared | Needs finite range, unit, missing semantics | Calibration/systematic sensitivity; **defer** |
| Michel summary | reconstructed delayed activity | **not present in G2** | Needs all-inventory parity and universes | Useful pion sensitivity; **defer** |
| Pion-prong summary | reconstructed track hypothesis only | **not present in G2** | Truth-derived versions forbidden | High leakage/generator risk; **defer or exclude** |
| Overflow aggregate | count plus conserved discarded energy | Current G2 silently top-N truncates; pre-truncation evidence absent | Aggregate token requires type≥1, count, conserved sums | Preferable to silent truncation; **defer** pending dump |
| Per-type energy sums | sums over real reco types | Types absent in G2 | Must derive identically for data/MC/background | Strong category/multiplicity dependence; **defer** |
| Truth particle cloud | E,px,py,pz,PDG; source MeV | `part_gen`; MC truth only | Explicit truth mask; periodic angular coords | Step 2 only; **include** |
| Interaction/current labels | generator categories | MC-only audit branches | No data counterpart | Direct truth leakage; **exclude permanently** |
| Target/source labels | data/MC/background bookkeeping | training/audit only | Never a feature | Accidental-label leakage; **exclude permanently** |

## 7. Why richer inputs may help—and why they may hurt

### Potential benefit

- The reconstructed muon can resolve a conditional data/MC difference that is
  invisible after marginalizing over recoil.
- Reco object type, view, dE/dx, timing, topology, and overflow conservation
  can distinguish detector-response submanifolds that a generic energy cloud
  merges.
- Rich globals can supply low-dimensional summaries that a small point-cloud
  model would otherwise learn inefficiently.
- A compatible pretrained representation could reduce optimization variance
  at limited training statistics.

### Failure modes

- More features can expose mismodeled detector effects, reduce ESS, amplify
  high-weight tails, or make systematic retraining more material.
- Missingness, padding, token count, overflow, ordering, or a missing-muon bit
  can become a proxy label.
- A reconstructed category trained on MC truth can leak generator information
  into Step 1 even if its name sounds detector-level.
- Adding Eavail/q3 or category energy sums can improve classification while
  worsening closure or circularly sharpening a reported projection.
- Pretraining from collider coordinates and a different Eavail definition may
  import the wrong inductive bias. Partial checkpoint loading confounds
  architecture, initialization, and random replacement.
- Framework/engine changes between B and C are not representation evidence
  unless the density-ratio convention is independently matched.

## 8. Experimental design and acceptance criteria

The frozen comparison requires common rows, splits, estimator seeds, optimizer
budgets, and evaluation metrics. A richer arm is beneficial only if it passes
every contract gate, improves the direct parent's injected-closure residual by
more than 5%, does not reduce global or tail ESS by more than 10%, does not
increase extreme-tail/cap sensitivity, and reproduces the effect across
seeds. Training AUC is diagnostic only.

Exact criteria and evidence downgrades:
`docs/orchestration/gregor-pet2/EXPERIMENT_PREREGISTRATION.md`.

## 9. Results and ablations

Result tables are inserted only after the result-bearing commit carries the
machine-readable products and matching `VALIDATION_LEDGER.md`,
`ND_OMNIFOLD_RUN_LOG.md`, and `ND_OMNIFOLD_STATUS.md` updates.

## 10. Compute and maintenance cost

The new backend is isolated from ROOT and TensorFlow and targets the Delta
`pytorch-conda/2.8` module plus safetensors. Receipts record software, GPU,
seeds, source hashes, configuration, weights, ESS, tails, runtime, and memory.
The operational cost still includes a second framework, separate environment,
new checkpoint/artifact validation, and duplicated estimator-systematic
validation.

## 11. Licensing and provenance decision

- `gregorkrz/minerva-ml`: MIT.
- upstream OmniLearned concept/source: MIT; attribution required.
- public prepared dataset: CC-BY-4.0.
- HyperScale source/license: unavailable; no code reused.
- Gregor pretrained weights: no verified weight license, immutable checksum,
  or accessible artifact; no weights reused.
- Experimental backend: independent implementation with explicit attribution.

## 12. Auditor findings, responses, and dissent

The durable source archaeologist accepted the implementation as independent
and correctly attributed, subject to labeling absent-G2 unit assumptions and
listing dependency SPDX identifiers.

The durable OmniFold contract auditor accepted only the synthetic path before
revision. It blocked real-G2 use on periodic truth coordinates, POT-scale
wiring, eager full-array loading, missing closure/cross-engine tests, and the
Gate-2 telemetry-unit bug. The same implementation role received all findings
for correction.

Final evidence and writeup reassessments are recorded here without averaging
away dissent.

## 13. Final include / exclude / defer decisions

Populated after the final auditor round and result commit.

## 14. Exact next steps when G2 becomes available

1. Stage and hash-verify the literal G2 NPZ, target weights, and receipts.
2. Convert the compressed production inventory once into a receipt-bound
   chunked or `.npy`/memmap representation; do not eagerly load 49M events.
3. Persist or independently build a hash-bound event-key sidecar for
   cross-universe correspondence.
4. Verify `w_reco` versus `w_truth`, target raw mass, POT scale, all units,
   all-playlist categories, native misses, and empty fake inventory.
5. Regenerate the source dump if typed objects, dE/dx, time, PID, Michel,
   pion-prong, or overflow fields are promoted. Require identical
   signal/data/background semantics and systematic behavior.
6. Run matched A/B/C/D-view/E-muon/E-rich seeds on identical rows and budgets.
7. Run ordinary and injected closure, cap scans, ESS/tail diagnostics,
   retraining spread, and 2D/3D/5D projections.
8. Only then reconsider D-typed or a licensed, hash-pinned, exactly compatible
   initialization arm.
