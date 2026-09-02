# PET typed-descriptor fixed-sample semantic evidence packet

**CITABLE FOR:** the exact fixed-sample observations and external source
comparison recorded here at repository base
`d8a59358be65fc924a05f707b8760cb5aff79bf4`.

**NOT CITABLE FOR:** population frequencies, physical units or calibration,
production normalization, a final categorical or sentinel interpretation,
training readiness, scientific performance, uncertainty, coverage, or a
publication result.

## Outcome - BLOCKED, NARROWED

The field-semantics gate does not pass. The evidence removes several tempting
assumptions but does not supply authoritative replacements:

1. The external paper and its linked source disagree about the meaning of raw
   prong PID `8`, so that source cannot settle raw PID provenance.
2. The fixed sample contains 22 valid prongs with raw charge code `2`, outside
   the typed contract's declared `[-1, 0, 1]` categories.
3. The typed source mapper retains several prongs that the linked preprocessing
   filters before constructing its event representation.

No category, sentinel, filtering, or unit change is made from this evidence.
Choosing one would turn a measured ambiguity into an invented semantic rule.

## Evidence boundary

The fixed-sample evidence and the M60 archive are distinct layers:

| Layer | What it establishes | Boundary |
|---|---|---|
| committed fixed-source smoke | the two bound source files, entries 0--15, map and round-trip through the current 51-column typed contract | software/source-mapping smoke only |
| archived fixed-sample probe | exact masks, raw code support, raw-scale telemetry, and field hashes for those 32 rows | not population support or semantic adoption |
| arXiv v2 plus its linked source commit | one downstream event-representation convention for the same branch names | not authoritative tuple-producer metadata |
| separate M60 raw archive | exact surviving M60 scripts, command record, stdout, and JSON | not imported into this packet and not routed for citation |

The source-smoke authority is
`docs/orchestration/state/pet-typed-descriptor-fixed-source-smoke-20260901.json`.
The new probe archive is
`docs/orchestration/runs/pet-typed-semantic-evidence-20260901/`.
The separate M60 preservation layer is its `m60/` subdirectory.

## Fixed-sample measurements

The deterministic probe read the already-bound 16 data and 16 MC rows. It did
not widen the source or entry scope.

The preceding documentation-only task did not authorize the ROOT access used
to recreate the shard. That execution-scope deviation, the exact command, and
the later ROOT-free replay command are disclosed in the fixed-sample
provenance.

That disclosure does not retroactively authorize the ROOT access. The archived
output may document the exact bounded observation and the execution-scope
deviation. It cannot authorize schema ratification, production integration,
additional ROOT access, or any widening of the bounded sample.

This 32-row packet does not support the photon three-state rates, playlist
claims, blob structural-zero rates, or broad prong findings reported by M60.
Those require the separate M60 preservation layer and remain outside this
fixed-sample packet.

| Observation | Data | MC | Interpretation allowed here |
|---|---:|---:|---|
| blob tokens | 208 | 155 | exact fixed-sample count |
| maximum blobs in one row | 90 | 42 | a fixed cap would be a downstream representation choice |
| photon tokens | 8 | 3 | exact fixed-sample count |
| prong tokens | 23 | 29 | current mapper retains all `n_prongs` rows |
| present prongs with invalid raw PID | 2 | 0 | current field mask marks the PID invalid, but token remains present |
| present prongs with valid raw PID `0` | 0 | 2 | PID `0` is not currently a contract sentinel |
| present prongs with valid energy `<= 1e-6` | 2 | 2 | current mapper does not apply the linked preprocessing filter |
| present prongs with valid mass `-1` | 6 | 6 | exposes an unresolved sentinel-policy question |
| present prongs with valid score `-1` | 2 | 0 | exposes an unresolved sentinel-policy question |

The prong rows in the last five lines can overlap; those counts must not be
added and called a number of affected tokens.

Across the 50 prongs whose raw charge field is valid, observed code counts are
`0: 25`, `1: 3`, and `2: 22`. The declared typed categories are
`[-1, 0, 1]`. This proves a support mismatch in the fixed sample; it does not
prove what code `2` means or how any code should be embedded.

All 11 valid photon direction vectors have norms between
`0.9999999723394454` and `1.0000000295710847`. That supports the numerical
unit-vector interpretation for these fixed rows only. It does not establish
branch calibration or physical units for the other photon fields.

## External source comparison

The comparison is pinned to
[arXiv:2604.12364v2](https://arxiv.org/abs/2604.12364v2) and
[`gregorkrz/minerva-ml` commit `78ebc0d6`](https://github.com/gregorkrz/minerva-ml/tree/78ebc0d6af04a5b6ab8114a9560dcc9c2a0b99bb).
The complete digests are recorded in the archived provenance.

### Raw prong PID is not resolved

- The paper's Appendix A describes pion, electromagnetic-shower, and muon-like
  prongs and sends the complete feature definition to `DATASET.md`.
- The paper's Appendix F says charged prongs have raw `prong_part_pid = 8`.
- `DATASET.md` maps raw codes `3`, `8`, and `13` to pion, EM-shower, and
  muon-like hypotheses, respectively.
- The same repository defines charged-pion PIDs as `{8, 9}` in
  `src/scripts/extract_baselines.py` and repeats that convention in
  `DATASET.md`.

These statements cannot all serve as one raw-PID semantic map. The contradiction
is recorded, not adjudicated. An original tuple-producer dictionary or an
equivalent authoritative reconstruction source is still required.

### Prong membership differs by construction

The linked preprocessing calls `get_dense(..., filter_prongs=True)` and drops
raw PID `-999`, raw PID `0`, and four-vector energy `<= 1e-6`. The current typed
source mapper instead preserves the `n_prongs` token structure and applies
field-level validity masks. The fixed-sample counts above prove that this is a
real structural difference, not merely a dormant code-path difference.

Neither policy is adopted here. A future production contract must state whether
the typed object set represents raw reconstruction rows or the downstream
paper's filtered object set, and then test that choice explicitly.

### Downstream transforms do not prove raw units

The linked source divides coordinates and time by 10,000 and constructs its own
transformed event features. That documents a consumer transform. Without the
raw tuple-producer contract it does not establish the physical units or
calibration of all 51 typed fields, particularly photon subsystem energy/evis,
blob `TPos`/`Is3D`/cluster-count, and prong score/mass/charge.

## Surviving gate

The unresolved PET typed-descriptor gates are now sharper:

- authoritative raw branch semantics and calibration;
- authoritative raw prong-PID and charge-code provenance;
- an explicit raw-row versus filtered-object membership decision;
- production normalization;
- raw-count scaling and multiplicity-dependent segment-sum behavior.

This packet authorizes no training, compute, GPU use, Gate-6 action, `C_ML`
construction, central/statistical pairing, central-value move, or publication
claim. PET remains diagnostic and method-development only.
