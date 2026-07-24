# Gregor PET2 and typed-object representations for MINERvA OmniFold

**Campaign:** `codex/gregor-pet2-omnifold`
**Evidence freeze:** 2026-07-23
**Status:** experimental assessment; publication G2 input unavailable

Verified campaign numbers belong in `VALIDATION_LEDGER.md`. This assessment
interprets them and points to the exact code, receipts, and orchestration
record; it does not create a second numerical authority.

## 1. Executive recommendation

Retain the current TensorFlow/Keras full-event estimator as the publication
default. Keep the independently implemented PyTorch PET2-family backend as an
opt-in experimental path, but do not promote it, typed reconstructed-object
tokens, the richer global block, a distinguished muon token, overflow
aggregates, or Gregor initialization from this campaign.

This is a conservative evidence decision, not a finding that the current
architecture is intrinsically superior. The completed matched synthetic
matrix injected its ratio only through reconstructed `mu_pt` and total
recoil-token energy, both already visible to arm C. It is therefore a
**baseline-sufficient null-feature test**: its sub-percent D/E/token/overflow
movements show that adding those irrelevant channels did not create a large
instability on that fixture, but they do not test whether information unique
to an enriched channel can improve ratio recovery.

Every arm in that null-feature matrix failed the implementation's descriptive
absolute density-ratio diagnostic. That threshold was not in the frozen
preregistration and is not used as an independent promotion rule here. The
current-engine TensorFlow full-event arm likewise showed only a sub-threshold,
seed-inconsistent change from its recoil-only parent. Those results still
support no promotion, but the original parent-relative ordering is not
evidence that detector view, type, rich globals, a muon token, or overflow
lacks useful conditional information.

The original synthetic matrix used 100,000 training events per inventory, a
practical pilot rather than production statistics. It cannot resolve whether
percent-level differences would persist or become significant at the
historical multi-million-event scale. “No benefit established” therefore
means both that the original injected target was parent-sufficient and that
the pilot cannot resolve percent-level real-data effects; it does not mean a
feature is intrinsically neutral or harmful.

The real typed-object vocabulary does not exist symmetrically for data,
selected signal, and background in the available MINERvA input. Gregor's
public rows are MC-only and cannot repair that omission. His advertised
initializations were unavailable, unlicensed as weight artifacts, unhashed,
and dimensionally unverified. Most importantly, the literal publication G2
payload was unavailable to this campaign. There is therefore no defensible
publication-level B-versus-C comparison and no basis for adopting the richer
representation.

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
- Implementation commit chain:
  `342343a`, `0b9217d`, `7c8d6c0`, `491dcdf`, `c7dd325`, `30e11b0`,
  `039f0a4`, `125a799`, and truth-frozen comparison source `23512b8`.
- Result-bearing commit: `d2bead0`.
- The canonical result products and their source commits are enumerated in
  `nd-unfolding/pet2_torch/products/final_campaign_summary.json`.

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

The D/E/muon-token/overflow manifests affect Step 1 only. Every arm shares a
fingerprinted `truth-frozen` Step-2 representation with generic truth tokens
and separately normalized truth-muon pT/p-parallel globals. The first pilot
launcher incorrectly reused the reco arm for truth; `KNOWN_ISSUES.md` #21
records its pre-result discovery, fix, and full comparison rerun.

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

A future checkpoint-compatible implementation is specified separately in
`docs/GREGOR_PET2_CHECKPOINT_COMPATIBILITY_DESIGN.md`. It freezes Gregor's
exact forward/tensor/state-dict contract, separates legacy-exact from
PID/mask-corrected semantics, and requires a licensed, accessible,
size-and-SHA-bound checkpoint before deserialization. It is a design, not the
independent backend and not pretrained evidence.

## 6. Feature provenance, availability, and decision table

`reco` below means detector-observable Step-1 use. Truth-only fields may be
used only in Step 2. Availability is written `D/S/B/M` for real data,
selected signal MC, literal background MC, and a native truth-only miss.
“schema” means the reviewed G2 producer/adapter contract contains the field;
the literal publication G2 file was unavailable, so it is not runtime
availability evidence. A miss has no reconstructed object: its Step-1 values
must be zero with its row/token mask false, while its MC truth remains in
Step 2.

| Candidate | Exact definition, units, source | Availability D/S/B/M | Role and normalization / missing semantics | Sensitivity and leakage risk | Decision and evidence |
|---|---|---|---|---|---|
| Recoil token energy | Reconstructed cluster `E`; `part_reco_E` → `part_reco[...,0]`; source MeV, adapter GeV (`/1000`) | schema/schema/schema/no-reco; bounded xps2 has D/S only | Step 1 detector observable; explicit `reco_view != 0` mask in PET2; masked values zero; train-only fit | Calorimetric scale/model response; energy-derived masks would leak missingness, so they are forbidden here | **include**; established baseline plus contract and xps2 runtime evidence |
| Recoil position, z | View-coordinate position and beam z; `part_reco_pos`, `part_reco_z`; source mm, adapter m | schema/schema/schema/no-reco; xps2 D/S | Step 1; KNN coordinates `(pos,z)`; explicit mask, no sentinel interpreted as physics | Alignment/resolution and view geometry systematics | **include**; current recoil geometry |
| Detector view | Reconstructed X/U/V category; `part_reco_view` → `*_view` arrays | schema/schema/schema/no-reco | Step 1 categorical; pad 0, real categories 1–3; never relabeled as object type | Detector-model sensitivity; safe only with identical category semantics across inventories/playlists | **experimental D-view**; code-contract plus synthetic ablation, G2 runtime deferred |
| Recoil time | `part_reco_time`; upstream unit and event-time reference not frozen | schema/schema/schema/no-reco | Potential Step 1 feature; must define unit, t0, valid range, mask, and sentinel first | Timing calibration and missingness can become a source label | **defer**; no unit/systematic audit |
| Muon pT, p-parallel | `reco_scalars`, `measured_scalars`, `bkg_reco_scalars` cols 0–1; GeV | schema/schema/schema/no-reco | Step 1 globals; fit on pass-reco signal, reuse on D/B; miss rows zero+masked. Truth cols 0–1 are separately fit for Step 2 | Detector response; direct measurement coordinates can increase model dependence and sharpen reported projections | **include experimentally**; current TF full-event footing |
| Muon px,py,pz,E,phi | `mu_reco_{px,py,pz,E,phi}` → `*_muon` cols 0–4; momentum/energy MeV, phi rad | schema/schema/schema/no-reco | Step 1 detector observable; `/1000` for four-vector, phi encoded as sin/cos; `-9999` never normalized; miss row neutral-masked | MINOS/reconstruction modeling; missing-muon flag can label rows | **experimental E-muon** as globals; token form is a separate ablation |
| Distinguished muon token | Same reconstructed muon object prepended with type≥1; KNN coordinates require a physical convention | schema fields exist, but physical token coordinates unaudited for D/S/B; none for M | Step 1 token only; removes its duplicated globals in the controlled ablation; explicit `muon_present` | A bad coordinate choice changes neighborhoods; missing-token presence can dominate | **synthetic-only experimental**; defer real use until coordinates and all-inventory behavior are audited |
| Muon charge / q-p | `mu_reco_qp` → muon col 5; proposed feature is sign or calibrated q/p | schema/schema/schema/no-reco | Step 1 only; zero and unit convention unresolved, so adapter does not authorize it | Curvature/range modeling, wrong-sign tails, sentinel leakage | **defer** |
| MINOS quality | `mu_reco_minos_ok` → muon col 6; boolean reconstructed match/fit-quality bit | schema/schema/schema/no-reco | Step 1 only; false on masked miss, no fabricated truth analogue | Playlist/acceptance sensitivity and strong selection correlation | **experimental E-rich**; require systematics and stability checks |
| Reco vertex | `vtx_reco_{x,y,z}` → `*_vertex`; source mm, adapter m | schema/schema/schema/no-reco | Step 1; `/1000`; pass-reco fit, D/B reuse; sentinel rejected and miss neutral-masked | Vertex resolution/fiducial-edge modeling; missingness leakage | **experimental E-rich** |
| Reco Eavail, q3 | `reco_scalars`, `measured_scalars`, `bkg_reco_scalars` cols 2–3; GeV | schema/schema/schema/no-reco | Step 1 globals; same train-only fit; reporting bin edges never inputs | Circularity in reported projections and generator/calorimetric dependence | **experimental E-rich**; accept only on closure/ESS/tails, not AUC |
| Reco photon/blob/prong type | A genuinely reconstructed object vocabulary, proposed from Gregor PID 0–7 semantics | absent/absent/absent/absent in current G2 | Would be Step 1 categorical with pad 0 and real types shifted ≥1 | Truth-derived or MC-only types are direct leakage; reconstruction categories may be strongly mismodeled | **defer D-typed** pending a symmetric D/S/B dump and systematics |
| Particle/PID hypothesis | Reco dE/dx/tracking hypothesis for prongs; exact proposed vocabulary not frozen | absent/absent/absent/absent | Step 1 only if reconstruction-derived; OOV and missing category required | Generator leakage if built from PDG/truth; category instability | **defer if reco-derived; exclude permanently if truth-derived** |
| Per-token dE/dx | Reconstructed energy loss; Gregor uses `log(abs(dE/dx)+0.1)` after clipping, but physical source unit is undeclared | absent/absent/absent/absent | Candidate Step 1 feature; needs unit, calibration, finite bounds and missing semantics | Highly calibration/systematic sensitive | **defer** |
| Michel summary | Reconstructed delayed-activity count/energy, such as `improved_nmichel` | absent/absent/absent/absent | Candidate Step 1 global, no truth analogue | Pion sensitivity but strong detector/time-window modeling | **defer** |
| Pion-prong summary | Reconstructed charged-pion-prong count/hypothesis only | absent/absent/absent/absent | Candidate Step 1 global if reconstruction-defined | High generator/leakage risk; Gregor's prepared count mixes raw PID semantics | **defer reco version; exclude truth-category version** |
| Overflow aggregate | One type≥1 token carrying pre-truncation discarded count and conserved energy/sums | pre-truncation evidence absent for D/S/B; no M reco | Step 1; mask true iff overflow exists; deterministic order; never infer from padded top-12 packet | Multiplicity/source-label leakage if inventory construction differs | **defer real use**; synthetic overflow ablation only |
| Per-type energy sums | Sum of reconstructed energy for each real reco type | unavailable because types absent | Candidate Step 1 globals derived identically for D/S/B | Correlated high-capacity category/multiplicity shortcut | **defer** |
| Truth particle cloud | `part_gen[...,0:5]` = E,px,py,pz,PDG; source MeV; PET2 uses E,pT,pz GeV and periodic `(theta,cos phi,sin phi)` | no/S/no/yes | Step 2 only; explicit `PDG != 0` mask; category made generic in current arms | Generator/model dependence is expected on truth side; forbidden in Step 1 | **include Step 2 only** |
| Interaction/current/pion truth labels | `mc_*`, interaction type/current, truth pion multiplicities and Gregor `truth_labels` | no/MC-only/audit-only/MC-only | Audit/stratification only, never estimator input | Direct truth leakage and generator-category shortcut | **exclude permanently from Step 1** |
| Target/source/event bookkeeping | data-vs-MC class, signal/background flag, pass flags, row index, event key, weights | bookkeeping in each applicable inventory | Used only for alignment, loss construction, masks and receipts; never concatenated to features | Accidental label leakage, padding/source shortcut | **exclude permanently as features; require as contract metadata** |

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

The continuation correction has its own preregistration:
`docs/orchestration/gregor-pet2/CONDITIONAL_STRESS_PREREGISTRATION.md`.
For each of detector view, reconstructed type, rich globals, additive
muon-token geometry, and pre-truncation overflow, it creates split-local
counterfactual pairs whose materialized direct-parent tensors are
byte-identical. Only the enriched carrier distinguishes the pair members and
encodes a fixed 0.5/1.5 ratio. Signal, unity-sham, and within-split
carrier-shuffle modes use matched rows, seeds, budgets, a common truth
inventory, and a truth-frozen Step 2. These fixtures test end-to-end channel
capacity only; a pass cannot establish that MINERvA data contains a useful
conditional.

## 9. Results and ablations

Exact verified values are written once in `VALIDATION_LEDGER.md`. The
machine-readable per-seed receipts and aggregates live under
`nd-unfolding/pet2_torch/products/`; this section records the evidence class
and decision rather than duplicating the numerical authority.

| Evidence compartment | Test | Outcome | Claim allowed |
|---|---|---|---|
| Code-contract | Local 67-test suite, complete A100 67-test suite, malformed-input gates | PASS; ten local skips are only absent optional PyTorch/safetensors dependencies | Experimental backend satisfies the tested contract |
| Reproducibility | Two A100 smoke jobs on different nodes | Core weights, models, preprocessing, indices, and arrays bitwise identical | Bounded deterministic execution |
| Public Gregor data | Immutable 1A jagged census | Safe `weights_only=True` load; physical PID 0 confirmed; MC-only contract remains incomplete | Schema/provenance facts only |
| TensorFlow synthetic A/B | Current-engine recoil versus full-event, three seeds | Descriptive absolute diagnostic FAIL; preregistered relative effect sub-threshold and seed-inconsistent | No A/B superiority claim |
| PyTorch synthetic C/D/E | Common 100k-event sample, truth-frozen Step 2, matched seeds and budgets; target depends only on C-visible inputs | Baseline-sufficient null-feature test: no large instability, but no unique-information challenge | No representation winner or unique-feature benefit claim |
| Muon-token/overflow synthetic | Tagged C-parent variants on the same C-sufficient target | Sub-percent movements are null/safety evidence only | No promotion; no channel-capacity conclusion |
| Recoil-input XPS2 | Three-seed bounded retraining over a fixed memmap selection | Finite weights, no cap saturation, stable throughput; no literal background, `w_reco`, full-event fields, or closure target | Engine/tail diagnostic only |
| Publication G2 | Required full-event data/signal/background/miss input | Unavailable to the campaign | No publication-estimator conclusion |

### Matched synthetic matrix

The original matrix must be read as a baseline-sufficient null-feature test.
Its known ratio is a function of reconstructed muon pT and total token energy,
both available to C. Consequently D-view, D-typed, E-rich, muon-token, and
overflow were asked primarily to ignore irrelevant extra inputs. Their
sub-percent differences cannot distinguish a channel that is useful when it
carries new information from one that is inert; the feature-conditional
continuation is the separate channel-capacity test.

The C control, D-view, D-typed, E-muon, E-rich without charge, and E-rich arms
used the same fixture rows, split seed, three estimator seeds, training budget,
parameter count, target, and fingerprinted truth-frozen Step-2 representation.
All cap-10 versus cap-30 checks were unchanged and no ratio saturated. Global
and declared-tail ESS changes remained far inside the ten-percent tolerance,
and the synthetic projection-residual subgate passed. The composite direction
diagnostic nevertheless failed for every arm because direct log-density-ratio
recovery remained outside its implementation threshold. That threshold is a
descriptive product diagnostic, not a frozen preregistration rule. No
promotion follows independently from the preregistered relative improvement,
ESS, tails, and all-seed criteria: no arm improved closure by more than five
percent.

Against C, detector view and typed tokens produced only sub-percent mean
changes. Detector view repeated the favorable direction across seeds; typed
tokens did not. Adding muon globals, the audited rich block, or charge did not
produce a reproducible benefit. Because the target contained no information
unique to those additions, these results establish only bounded null-feature
behavior. The 100k-event noise floor and the parent-sufficient target both
forbid treating the sub-percent ordering as an intrinsic architecture
ranking.

The distinguished-muon-token form was seed-inconsistent and moved the mean
residual in the wrong direction on this null-feature target. The overflow
aggregate moved all three seeds slightly favorably. Neither direction is
scientific benefit or harm evidence because C already contained the complete
injected target. Real muon-coordinate/missingness semantics and the real
pre-truncation overflow inventory also remain unavailable.

### Baseline and cross-framework limits

The TensorFlow A/B harness executed the repository's current vendored PET and
MultiFold loop. Its B full-event arm did not establish a benefit over A
recoil-only: the mean change was sub-threshold, one seed moved adversely, and
the descriptive absolute diagnostic failed. The TensorFlow harness also
retains the historical single-MC-weight limitation and lacks cap telemetry.

No direct B-versus-C architecture result is reported. The two frameworks do
not share identical splits or every optimizer/weight convention, and the
literal G2 footing was absent. Comparing their separate synthetic means would
confound framework, representation, and training engine.

### External-input evidence

The larger XPS2 pilot demonstrates bounded memmap access and practically
stable retraining on a real recoil inventory. Its pull weights have materially
longer tails than its push weights, even though no configured cap saturated.
Because it proxies missing `w_reco` with `w_truth`, consumes a precomputed
target without literal background rows, and has no full-event types or
globals, it cannot answer whether PET2 or typed tokens improve the existing
estimators.

The fixed C rerun reproduced its pre-fix push/pull arrays and model
safetensors bitwise for all three seeds. The only intended difference is its
truth-manifest/recipe provenance. The pre-fix D/E results remain quarantined
because they altered both Step 1 and Step 2.

## 10. Compute and maintenance cost

The new backend is isolated from ROOT and TensorFlow and ran with PyTorch
2.8.0+cu128, NumPy 2.2.6, safetensors 0.5.3, and Python 3.11.13 on Delta A100
GPUs. Each Step model has about 1.21 million parameters and a 4.87 MB
safetensors artifact. The largest matched pilot stayed below 0.8 GB peak GPU
memory. A PyTorch arm/seed took about four minutes of training wall time; a
sequential TensorFlow A+B seed took about ten minutes. The full campaign used
about 3.20 A100-hours, including fail-closed diagnostics and quarantined
pre-fix runs. Exact accounting is in the validation ledger and final product
summary.

Those small pilot costs do not imply cheap publication use. A second framework
requires a separate environment, artifact/checkpoint validation, framework-
specific calibration checks, duplicated per-universe retraining, extraction
compatibility, and long-term maintenance. That cost is justified for an
experimental backend and future controlled comparisons, not for a default
change unsupported by physics evidence.

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

The implementation revision added periodic truth coordinates, receipt-bound
POT scale, production-size compressed-input refusal, vectorized splits,
known-ratio closure, an analytic fixed-logit ratio-convention equivalence test,
separate D/E arms, safe public-data loading, cap telemetry, deterministic
attention, and finally a single truth-frozen Step-2 representation. The
analytic test is not an end-to-end TensorFlow-versus-PyTorch run on identical
tensors. The corrected 67-test A100 suite passes.

The final contract auditor accepted the code and every product within its
explicit code-contract, synthetic, public-schema, or recoil-input label. It
found no blocker, major issue, implementation defect, or aggregation defect.
It required the absolute RMSE diagnostic to be identified as descriptive
rather than preregistered and the fixed-logit test to be scoped as analytic
rather than a full cross-engine comparison. Both corrections are applied here
and in the validation ledger.

The final evidence auditor returned a conditional pass and dissented from any
interpretation of the 100k-event pilot as an intrinsic architecture verdict.
It described the pilot as underpowered relative to a 2M target. The frozen
preregistration does not specify 2M events, so that claimed preregistration
deviation is not sustained; 2M is a historical PET baseline elsewhere in the
repository. The substantive dissent is accepted: percent-level differences
are unresolved at 100k events and require higher-statistics G2 evaluation.
This dissent remains explicit even though it does not change the no-promotion
recommendation.

Both same-session final reassessments returned **PASS** on revision
`e530536`. No additional correction was requested. The 100k pilot-power
objection remains the sole unresolved dissent and is carried into the G2 next
steps.

## 13. Final include / exclude / defer decisions

| Candidate | Decision | Reason |
|---|---|---|
| Current TensorFlow/Keras full-event estimator | **retain as current default** | No alternative passed the acceptance gate; this is continuity, not evidence of architectural superiority |
| Independent PyTorch PET2-family backend | **include as opt-in experimental code** | Contract, deterministic runtime, artifact, and bounded-input gates pass; physics superiority is unproved |
| Existing generic recoil tokens | **retain** | Only real-input pilot available; stable bounded execution, but not a closure comparison |
| Detector-view category | **unresolved / defer promotion** | Small consistent synthetic movement below pilot resolution; G2 runtime and all-playlist systematic evidence absent |
| Typed photon/blob/prong tokens | **defer** | Small inconsistent synthetic movement; no symmetric reconstructed D/S/B inventory; public rows are MC-only |
| Truth-derived type, interaction, or target labels in Step 1 | **exclude** | Direct leakage and generator shortcut |
| Muon globals | **retain only in the current audited full-event contract** | New synthetic evidence did not establish incremental benefit; missingness and detector-response risks remain |
| Distinguished muon token | **do not adopt** | Mean synthetic closure worsened; seed direction inconsistent; real coordinates and missingness unaudited |
| Rich globals without charge | **defer** | Sub-percent, seed-inconsistent synthetic effect; Eavail/q3 circularity and detector systematics require G2 |
| Muon charge/q-p addition | **defer** | Incremental synthetic effect was slightly adverse; unit, sentinel, and wrong-sign-tail audits incomplete |
| Overflow aggregate | **unresolved / defer** | Negligible 100k-pilot movement; real pre-truncation inventory unavailable |
| Timing, dE/dx, PID, Michel, pion-prong, per-type sums | **defer reco-derived versions; exclude truth-derived versions** | Units, symmetric reconstruction semantics, and systematic response not established |
| Generic or MINERvA-fine-tuned Gregor initialization | **defer** | Weight artifact inaccessible, license/checksum absent, preprocessing and tensor compatibility unverified |

## 14. Exact next steps when G2 becomes available

1. Stage and hash-verify the literal G2 NPZ, target weights, and receipts.
2. Run the tested `g2_memmap.py` conversion on that literal receipt-bound
   file. Verify its per-array units, row families, ordered-inventory hashes,
   immutable manifest and completion marker before exposing read-only
   windows; do not eagerly load 49M events. Generated mini-packet tests are
   code-contract evidence, not execution on G2.
3. Persist or independently build a hash-bound event-key sidecar for
   cross-universe correspondence.
4. Verify `w_reco` versus `w_truth`, target raw mass, POT scale, all units,
   all-playlist categories, native misses, and empty fake inventory.
5. Regenerate the source dump if typed objects, dE/dx, time, PID, Michel,
   pion-prong, or overflow fields are promoted. Require identical
   signal/data/background semantics and systematic behavior.
6. Run matched A/B/C/D-view/E-muon/E-rich seeds on identical rows and budgets,
   including an end-to-end TensorFlow/PyTorch ratio-convention check on
   identical tensors; use substantially higher statistics than the 100k pilot.
7. Run ordinary and injected closure, cap scans, ESS/tail diagnostics,
   retraining spread, and 2D/3D/5D projections.
8. Only then reconsider D-typed or a licensed, hash-pinned, exactly compatible
   initialization arm.
