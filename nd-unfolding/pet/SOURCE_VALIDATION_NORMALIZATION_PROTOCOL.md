# PET v2 source-validation and normalization protocol

**Prepared 2026-09-10; execution not authorized.** This protocol continues
`pet-prong-semantics` at software base
`529f26ae8dd739445ccb6aac96e96d5575117112`. Preparation and local synthetic checks
are authorized. ROOT access, scientific training and cluster compute are not.
The proposed stages below need separate, named execution authorization; neither
this document nor a successful stage supplies that authorization.

The locally measured `pet-typed-descriptors-v2` schema SHA-256 at that base is
`102a409635e422c6688ee9fa7d98206c1048ae87199679b1a8d5d59c46f1e879`.
Pin it alongside the code in any future launcher; a schema change requires a
revised protocol binding.

The measurement is whether the v2 mapper preserves the specified source rows,
implements the documented field masks, and exposes discrepancies with the prong
correspondence. A later normalization pilot measures whether training-only
statistics and a frozen count/pooling policy can be reproduced without leakage.
Neither measurement establishes population support, calibrated particle
identification, improved unfolding, uncertainty coverage or publication readiness.

Implementation preparation is now recorded in
[SOURCE_AUDIT_RUNBOOK.md](SOURCE_AUDIT_RUNBOOK.md), with machine-readable
[SOURCE_AUDIT_BINDINGS.json](SOURCE_AUDIT_BINDINGS.json). That runbook specifies
metadata compatibility where the historical receipt has no type/shape snapshot,
raw digest framing, resource failure behavior and the exact terminal artifacts.
This addition changes no source identity, branch, entry interval or execution
authorization.

## 1. Source identities and bounded access proposal

Identity anchors come from the committed
[fixed-source receipt](../../docs/orchestration/state/pet-typed-descriptor-fixed-source-smoke-20260901.json)
and `FIXED_SOURCES` in [the mapper](typed_descriptor_source_smoke.py). The two
manifest byte digests were checked locally during preparation. UUIDs below are
historical receipt values, not newly observed ROOT identities. A matching UUID
is not a content checksum or proof of a tuple release.

| Binding | Data | Reco MC |
|---|---|---|
| Playlist | `1B` | `1A` |
| Manifest | `2d-unfolding/playlist_manifests/1B_Data.txt` | `2d-unfolding/playlist_manifests/1A_MC.txt` |
| Physical manifest line | `1` | `1` |
| Basename | `MasterAnaDev_data_AnaTuple_run00010068_Playlist.root` | `MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root` |
| ROOT UUID | `bcd43694-ef17-11f0-9717-17a6e183beef` | `c0347da6-2a99-11ef-9717-31a7e183beef` |
| Manifest SHA-256 | `91fa4a24774bfa800cd021dd712e61c777f600a7fa0c77ef1f54dad289764b1e` | `4100dca453de1beef0213a0feac1fe4faa77d769f2dd5f36f4e11c6cea4894f8` |
| Tree | `MasterAnaDev` | `MasterAnaDev` |
| Proposed source-audit entries | `[0, 4096)` | `[0, 4096)` |

Intervals are zero-based and half-open: exactly 4,096 requested entries per
source, 8,192 total. Entries `[0, 16)` are the historical anchor subset; report
them separately from `[16, 4096)`. This is a deterministic convenience sample,
not a representative playlist sample or a data/MC population comparison. Do not
replace either file, take another manifest line, scan a directory, follow a P8
replacement, or extend the range to find a rare object. A short tree terminates
the proposed run as incomplete; do not backfill.

The source stage reads only the 75 ordered `REQUIRED_BRANCHES` at the software
base, plus ROOT file/tree metadata. Their ordered-name digest is
`a5704bb33229b51d7ed3e185374032d487427133a186c7198eaee29e52b21f69`
under the existing receipt's digest convention. Pin the actual branch list and
digest again in the future launcher. This includes source event keys, the
13-column event mapper, generic P12 inputs and all photon/blob/prong fields;
it does not include `prong_nParticles`, dedicated candidate associations,
truth branches, weights or a `pass_reco` decision.

Before payload access in an authorized run, require the manifest hash, exact
line/basename, UUID, tree, entry count and branch names/types/shapes to agree.
Record metadata and any available producer release/build/configuration markers
verbatim. Archive an already available publisher checksum if present; do not
invent one or perform an unbudgeted whole-file checksum scan. Bind what was
actually read with a canonical bounded-payload SHA-256 (ordered role, UUID,
tree, entry, branch name, dtype/shape and raw bytes), metadata digest and
per-branch digests. Preserve raw non-finite values in this audit archive before
the mapper replaces them in storage. Do not call the bounded digest a file hash.

**Release applicability remains unresolved.** P7/P8 assignment needs a producer
identifier or a versioned producer attestation covering these exact identities,
the PID enumeration, tuple filler and reconstruction configuration. The
[correspondence](PRONG_BRANCH_SEMANTICS.md) and a downstream analysis commit do
not provide that binding. Missing release evidence permits a bounded telemetry
report with `RELEASE_UNVERIFIED`; it cannot pass the release gate. No external
correspondence is sent as part of this preparation.

## 2. Semantic checks and verdicts

Every table reports data and MC separately, with eligible denominators, missing
denominators, and source-entry/token indices for exceptions. Keep source order.
Unexpected values remain in the archive and raw typed storage where
representable; never filter them to make a check pass. A zero denominator is
`NOT_TESTED`, not a pass. Separate mechanical `FAIL` from a correspondence
`DISCREPANCY` and an unanswered `UNRESOLVED` question.

| Check | Required observation and acceptance criterion |
|---|---|
| Source-to-row alignment | Exactly one record per requested role/UUID/tree/entry; event keys `ev_run/ev_subrun/ev_gate` retained. Offsets monotonic, counted-vector lengths equal their declared counts, prong position and four-momentum width four. No sorting, dropped rows or truncation. Zero discrepancies for mechanical PASS. Duplicate event keys are recorded for grouped splitting, not silently removed. |
| Raw prong membership | Typed rows per event equal `n_prongs`, including index zero, PID 0, unfilled PID and low/zero-energy rows. Structural presence, field validity and family enablement remain different objects. Zero membership discrepancies. |
| PID support | Tabulate every raw code, sentinel, noninteger and non-finite value by source and prong index zero versus later indices. Compare with tentative emitted support `{-999, 0, 3, 8, 13}`; code 9 is in the v2 vocabulary but its emission is unverified. Other enumeration codes use the unknown-category channel if valid. Unexpected support is a discrepancy requiring source explanation, never a new PDG mapping. |
| Charge applicability | Cross-tabulate raw PID/charge and resulting masks. Only valid PID 3 may have valid charge; 0/1/2 mean undetermined/positive/negative. Valid unexpected muon codes use the unknown channel. Non-muon zero fills and all invalid-PID charge fields are masked. Require exact agreement with the v2 mask rule; raw-code expectations are checked separately. |
| Sentinel combinations | Cross-tabulate PID, score, mass and charge, retaining simultaneous exceptions. Compare with the five-row PID/score/mass/charge table in the semantic reference. Mask score -1 and mass -1 independently of token presence, plus the schema's -999/-9999 and non-finite rules. PID 0 and its score 0 remain valid. No blanket zero mask. Exact mask agreement is required. |
| Score and hypothesis mass | Report score range by PID; flag values outside [0,1] for PID 8/13 and deviation from score 1 for PID 3 or 0 for PID 0 (`abs_tol=1e-6`). Flag PID 3/8 masses differing from 105.658/938.272 MeV by more than 0.01 MeV. These are correspondence checks, not physical cuts. Native scores and identity scaling must be bitwise preserved after float32 storage; masses remain redundant hypothesis inputs. |
| Units and primary ordering | Record prong position/time/four-momentum/dE/dx ranges without conversion. Flag valid time outside [0,10000] ns. For every nonempty event tabulate index-zero PID and compare its raw vector with `MasterAnaDev_leptonE` in tuple coordinates (component agreement diagnostic: `rtol=1e-5`, `atol=0.01` in native momentum/energy units). Also tabulate residuals for later prongs. A vector match supports redundancy in these rows; lack of a match is not proof of misordering, since reconstruction hypotheses/accessors can differ. Producer ordering evidence is still required; never compare detector-frame prongs directly to the beam-frame event muon as if identical. |
| Round trip and software controls | Save/reload v2 typed shard and provenance with exact equality of values, masks, counts, offsets and row identity. Reproduce raw-to-field mapping through a separate table-based check, not only a call to the same mapper. Require finite NumPy/Keras outputs and agreement at `rtol=1e-5`, `atol=1e-6`; C0 has exactly zero 51 descriptor columns and C0/C1 both have 13+51 conditioning columns. v1 artifacts remain rejected. |

The source audit is unselected: do not infer `pass_reco` from a finite event
block, a MINOS-match flag, prong presence or a successful mapper call. Preserve
the offending raw row if mapping fails; a failed event block cannot be skipped
to obtain a successful aligned shard. Mechanical PASS does not imply that the
correspondence checks passed or that the remaining families are understood.

For source-stage forward checks only, construct an explicitly labeled identity
normalization (all continuous means 0/scales 1) and fixed reference projectors
with seed 0 and default width 16. Fit no statistics or model weights. This
temporary diagnostic config is not a normalization-pilot output and cannot be
used for training. The existing smoke CLI both fixes 16 entries and fits
smoke-only MC statistics; it is not the proposed audit launcher. Preparation of
a separate bounded, raw-preserving checker/launcher and its synthetic failure
checks must precede the source execution request.

The terminal receipt carries separate mapping, correspondence, release and
object-family verdicts. Any unexplained correspondence discrepancy blocks a
semantic PASS. Release or family evidence absent from this sample remains
unresolved even when every software check succeeds. A later diagnostic run card
must explicitly retain those limitations; no stage promotes a production-ready
representation while these gates remain open.

## 3. Object-family questions that this source sample cannot settle

| Family/question | Bounded check | Evidence still required before the corresponding production claim |
|---|---|---|
| Photons | Record both raw gamma slots before membership filtering. Count absent/thresholded (`E <= 1e-5`), present, and non-finite/ambiguous slots separately; ambiguous presence is a mapper failure. Report direction validity and norm (flag `abs(norm-1)>1e-4`), energy/evis zero/sentinel patterns and subsystem sums without interpreting them as an energy balance. | Producer definitions of slot ordering, presence threshold, direction frame, dE/dx/time units, energy versus visible-energy calibration and subsystem overlap. The two slots do not establish a complete photon census. |
| Blobs | Check all `_sz` vectors align; tabulate raw `Is3D`, `TPos`, positions, total energy and cluster count, including zeros conditional on `Is3D`. Flag negative/noninteger valid cluster counts. | Meaning and units of `TPos`, structural zero versus missing coordinate, `Is3D` codes, calibration and cluster membership. A zero is retained under v2 unless a documented mask says otherwise. |
| Prong hypotheses | Preserve all rows and tool-dependent scores, report sentinel combinations and index-zero behavior. | Versioned best-particle selection/filling functions, priorities, tie/default rules and why unknown differs from unfilled. Highest-score selection is tentative and must not be implemented. `prong_nParticles` is hypothesis multiplicity, not particle count; adding it needs a new branch proposal. |
| Shared objects/primary lepton | Record co-occurring family counts and index-zero/event-lepton residuals only. | Association identifiers or producer cluster-membership definitions linking generic prongs, photons, blobs and dedicated muon/proton/pion candidates; dedicated proton thresholds. Similar coordinates or energies cannot prove shared or disjoint deposits. |

The baseline retains every raw prong including the primary lepton in the
permutation-invariant pool and keeps the event muon separately. No role label,
primary removal, cross-family deduplication, energy sum interpreted as total
recoil, score/energy cut or dedicated-branch feature is introduced here.
Filtered membership, primary removal/role encoding and family ablations are
distinct later comparisons, each with fixed source rows and normalization.
Unresolved overlap prevents a disjoint-particle or calibrated full-event claim;
it does not erase a bounded software result.

## 4. Training-only normalization inventory and split proposal

The first normalization artifact is explicitly a **single-file diagnostic
pilot**, never production normalization. Its sole proposed reco-MC inventory
is the MC identity in section 1, entries `[16,4096)`, intersected with a bound
`pass_reco` selection. No truth-side inventory, data row, lateral universe,
bootstrap replica, legacy PET product or additional file may enter the fit.
All reconstructed MC event classes passing that detector selection are eligible;
do not impose `pass_truth`, signal-only membership or a physics-weight cut.

**Selection prerequisite:** the 75-branch source audit does not provide
`pass_reco`. Before requesting a normalization run, commit a row-aligned
selection sidecar specification and receipt identifying its producer code,
exact detector predicate/configuration, branch dependencies, source identities,
entry keys and checksum. It must agree with the intended detector selection
routed by [the full-event contract](FULL_EVENT_FEATURE_CONTRACT.md), including
the reco-pass versus truth-pass distinction. No sidecar is asserted to exist
here. Producing one from ROOT requires a separately authorized exact branch
allowlist and budget; the source-stage grant must not be stretched to cover it.
Missing or unmatched selection entries block fitting; an all-true stand-in is
forbidden. This prerequisite makes the proposal concrete without claiming a
production inventory or selection that has not been measured.

Freeze the split before inspecting values or fitting anything:

1. Group by `(role, playlist, ev_run, ev_subrun, ev_gate)`, with integer key
   values. Keep every tuple row and every object belonging to a group together.
   Missing keys block splitting. Duplicate group keys are allowed within one
   split and explicitly counted; duplicate source UUID/tree/entry rows are not.
2. Any group appearing in historical entries `[0,16)` is reserved in its
   entirety, including later entries sharing its key. Reserved groups are
   audit-only and never used for fit, tuning or the held-out comparison.
3. For every other group form the ASCII string
   `pet-v2-norm-split-20260910|ROLE|PLAYLIST|RUN|SUBRUN|GATE`, with `ROLE` equal
   to `data` or `mc`, no spaces/newline, and decimal integer key fields with no
   leading zeros. Let `b = int(SHA256(string).hexdigest(), 16) % 10`.
   Buckets 0–7 are training, 8 validation and 9 held-out test. This is an
   approximately 80/10/10 group split, not a promise of exact event counts.
4. The normalization fit includes only training MC rows with `pass_reco=true`.
   Split data by the same rule for a later matched comparison, but never fit
   statistics from it. Validation/test values cannot choose a transform,
   clipping bound, missingness rule, feature or seed. No split retry for balance.
5. Canonically sort the full inventory/split table by role, playlist, UUID,
   tree and entry; record group keys, bucket/reservation, pass flag and fit
   membership. Serialize canonical JSON (sorted keys, compact separators,
   ASCII, no trailing newline) and SHA-256 it. Bind the table, selection
   sidecar, protocol, software/schema and normalization hashes in the receipt.

Minimum pilot support: 100 distinct training MC groups passing selection;
20 selected MC groups in each validation/test partition; and, for each fitted
component, at least 20 valid tokens from at least 10 training groups. Report
actual support per family/component; failure is `INSUFFICIENT_SUPPORT`, with no
automatic sample widening or family removal. These are pilot feasibility
thresholds, not guarantees of calibration, generalization or statistical power.
Production requires a separately enumerated multi-file/release inventory and
its own authorization; this one-file artifact cannot be relabeled for it.

### Exact continuous fitting policy

Use one shared, unweighted token-level fit per family/component on eligible
training MC only. Apply structural token masks and field validity, including
muon-charge applicability where relevant and all-component masks for vectors.
Family enablement must not change which training observations fit statistics:
fit once before setting C0/C1 enable flags. Do not fit each minibatch, PID class,
data sample, validation split, seed or control arm separately.

| Family | Standardize with valid-only training mean and population standard deviation |
|---|---|
| Photons | Direction x/y/z; dE/dx; time; five `energy_*` and five `evis_*` components, each separately. Native unresolved units remain labeled unresolved. |
| Blobs | Position x/y/z; time; time-position; total energy; cluster count. The last is a per-blob continuous feature, distinct from the event's blob count. |
| Prongs | Position x/y/z; time; four-momentum px/py/pz/E; dE/dx; hypothesis mass. Undefined mass -1 is excluded. |

Prong score has exact mean 0 and scale 1, preserving its native value beside
raw PID; no pooled score standardization or probability calibration. Categorical
PID/charge/Is3D and every mask are never standardized. Physical unit conversion,
clipping, winsorization and class/physics/loss weighting are not part of this fit.
The existing 13-column event transform and generic P12 preprocessing are separate
contracts: this artifact does not normalize them or certify their training-only
provenance. Their fit lineage must be frozen and checked before any training.

Accumulate means and population variance (`ddof=0`) in float64 over the
canonical token order; store float32 means/scales as the adapter requires.
For a supported constant component, store its mean and scale 1 and flag it
`CONSTANT`; it contributes zero on identical valid observations. Empty or
under-supported components block acceptance even though the smoke helper can
return identity defaults. Non-finite statistics, nonpositive scales or float32
overflow block the artifact. Invalid components stay zero after normalization
and their masks remain available. Report train-only valid counts, group counts,
mean, scale, min/max and constant flags; report held-out transformed ranges
without refitting or clipping them.

Freeze one versioned `FrozenNormalization` artifact with
`fit_inventory_row_selection_digest`, `fitting_policy` and the v2 schema digest,
plus a receipt carrying the component support and selection bindings. Reload
it in a fresh process, compare all arrays exactly, and independently recompute
the float64 statistics from the fit table (`rtol=1e-10`, `atol=1e-12` before
float32 storage). Require NumPy/Keras features to agree at `rtol=1e-5`,
`atol=1e-6`. Reject schema/row-selection/digest mismatches and identity-fitted
smoke artifacts. Freeze and reuse this same artifact across data, validation,
test, inference, C0/C1 and all declared seeds; consumers never call the smoke
fitter to fill missing statistics.

## 5. Count and pooling decision

**Current v2 behavior, preserved for source validation:** uncapped masked
segment sum with a raw event-level object-count column per family. At default
projection width 16 this gives `3 * (16 + 1) = 51` descriptor columns.
Raw integer counts, offsets and masks remain in storage for every future
representation. A zero-field/unknown prong can still be a present token.

**Proposed normalization-pilot representation, requiring implementation and
separate approval before use:** per-family masked mean plus a scaled log count.
For enabled family f with n structurally present tokens and projected tokens
h, use `sum(h) / max(n,1)` and `log1p(n) / s_f`; force both to zero for n=0
or a disabled family. Fit `s_f` as the population standard deviation of
`log1p(n)` over all selected training MC events, including zero-count events,
with no centering so empty counts stay zero. A supported constant count uses
scale 1 and a constant flag. Require the same 100 training groups and at least
10 nonempty groups per family; otherwise block this candidate. This policy
retains count information while removing the explicit linear multiplicity
factor in the token sum. It does not prove insensitivity to detector multiplicity.

Count scales are event-level parameters; they do not belong in per-token
`FamilyNormalization`. Freeze them, the pooling mode and a representation
version/digest in a separately serialized adapter configuration/receipt. The
current v2 adapter has no such implementation: do not claim an existing saved
v2 model supports this proposal or silently reinterpret its sum/count columns.
Require config round-trip, stale-config rejection and synthetic NumPy/Keras
agreement before any real-input use. Output width stays 64 at default settings;
C0 zeros all 51 descriptor columns after transformation.

Before training, synthetic repetition by factors 1, 2 and 8 must leave mean
features unchanged and change the count feature by exactly the stated formula
(floating comparison `rtol=1e-5`, `atol=1e-6`). Include empty, disabled,
all-invalid-but-present, unknown-code and one high-multiplicity event; no token
cap or silent truncation. Record frozen-reference pooled norms against counts
in bins 0, 1, 2–4, 5–16, 17–64 and >=65 on the bounded sample, with empty bins
marked untested. Sum/count versus mean/log-count is a later matched sensitivity
comparison if authorized; do not select a winner using the held-out test set.

## 6. Proposed stages, budget and terminal artifacts

These are hard proposed ceilings, not resource measurements or standing grants.
Memory/output/wall-time exhaustion stops with a partial receipt; no automatic
retry, truncation, new file, extra entry or cluster escalation is permitted.

| Stage | Proposed budget and inputs | Acceptance and terminal boundary |
|---|---|---|
| Local preparation (authorized) | Documents and existing synthetic tests only; zero ROOT opens, training jobs, GPU use or cluster submissions. | Protocol links and pinned manifest/branch identities agree; local checks logged. No source or normalization result. |
| Source audit (not authorized) | One CPU process, <=2 threads, <=8 GiB RAM, <=30 minutes wall (<=1 CPU-hour), <=1 GiB new output; exactly two source opens and <=8,192 requested entries, 75 branches. ROOT may decompress whole baskets; the bound is on requested entries, not a claim that storage reads only those bytes. | Section 2 mechanical checks all pass, no unreported exception; semantic/release questions retain separate verdicts. Only fixed-source telemetry and mapping acceptance. No fit, scientific training or production adoption. |
| Normalization pilot (not authorized; selection sidecar and count/pooling implementation are prerequisites) | One CPU process, <=2 threads, <=8 GiB RAM, <=15 minutes wall (<=0.5 CPU-hour), <=256 MiB output; only bound source-audit shards and the separately approved selection sidecar, zero new ROOT access. | Section 4 support, split disjointness, independent fit and reload pass; section 5 synthetic properties pass. A diagnostic pilot artifact only. The missing selection-producer run is outside this budget and requires a concrete addendum before approval. |
| Later matched C0/C1 comparison (not authorized; needs its own full training run card) | Planning ceiling: two arms at `m_reco(num_evt=64)`, three paired seeds 17/29/43, at most 10 epochs per fit, six fits total, <=2 GPU-hours aggregate and <=2 GiB outputs. Use only the frozen selected pilot rows/split and normalization. No OmniFold loop, bootstrap or covariance ensemble. | Require common event inputs, rows/order, split, loss/weights, optimizer, batch size, stopping/checkpoint rule and seed-matched shared initialization; only typed-family enablement differs. Report every seed's held-out loss and paired difference plus multiplicity/missingness diagnostics; no best-seed selection or improvement threshold inferred after seeing results. A diagnostic classifier comparison cannot establish unfolding closure, bias, coverage or publication uncertainty. |

For the later training run card, pin the actual task/labels, event/P12
normalization, model/loss implementation, background and weight treatment,
hyperparameters, checkpoint rule, hardware request and environment after the
source and normalization gates. None is inherited from a Gate-6 launcher.
The budget above is a ceiling for planning, not a runnable training specification.
The data and MC inputs use different playlists and only one file each; any
classifier difference is conditional on those sources and cannot distinguish
representation benefit from release/playlist or detector-modeling effects.
Any cluster proposal must follow the fresh-state, scheduler, environment and
`nd-unfolding/mnv_guarded_run.py` routes before launch.

A future receipt must include authorization and code/protocol digests; actual
identity observations and release qualifications; requested/attempted/completed
entry lists; raw payload/metadata/branch/schema hashes; ordered source-row keys;
all semantic tables and exceptions; stdout/stderr and resource accounting;
per-check verdicts with denominators; closed-file artifact digests; and the
terminal non-claims. Normalization adds the selection/split/fit tables and
count/pooling configuration. Write new v2 artifacts in a distinct namespace;
never overwrite the v1 source-smoke or semantic-evidence packet. Commit the
receipt and required RUN_LOG/STATUS records before citing a result. Independent
verification must trace to a separate calculation/source check; a round trip
or repeated use of the mapper alone is not independent semantic verification.

## 7. Preserved scientific restrictions

PET remains diagnostic/method-development under
[OI-126](../../docs/OPEN_ITEMS.md). The existing `C_stat` construction is
unverified and its pairing with P5A was declined; no PET total covariance is
adopted. This protocol supplies neither estimator-equivalence nor coverage
evidence and does not reopen the completed containment, tail-geometry,
target-factor, extraction or occupancy probes.

The exact `prohibitions_applied` entries from
[the Gate-6 receipt](../../docs/orchestration/state/gate6-member-trajectories-result-56847059.json)
remain:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

No stage here clears Gate 6, constructs `C_ML`, moves a central value, adopts
uncertainty or changes the scalar publication workstream.
