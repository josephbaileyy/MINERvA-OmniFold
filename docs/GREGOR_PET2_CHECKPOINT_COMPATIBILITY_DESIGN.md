# Gregor PET2 checkpoint-compatibility design

**Status:** design specification only; no compatible checkpoint was available,
licensed, or hash-pinned. This document is not pretrained-transfer evidence.

This design is for a future backend with estimator family
`gregor-pet2-checkpoint-compat-v1`. It is separate from, and must never be
cross-loaded with, the campaign's independently implemented
`independent-pet2-small-concept-match-v1`.

## Audited source footing

- requested `gregorkrz/minerva-ml` commit:
  `af5d92ed2b3b448a09b6b7cf6b4f179e5757b4ed`;
- inspected upstream:
  `fc9a099d3c9c060f03cef293c294f9de4eb019cd`;
- relevant model, preprocessing, dataloader and training files are
  byte-identical between those commits.

Exact source-audit response:
`docs/orchestration/runs/gregor_source_archaeologist/20260723T232810Z-send-d6711628.json`.

## Required upstream implementation surface

A source-compatible implementation must vendor under MIT with attribution, or
independently reproduce and test, these exact symbols:

| File | Load-bearing symbols |
|---|---|
| `src/models/omnilearned/network.py` | `PET2`, `PET_body`, `PET_classifier`; `PET_generator` for pretrain/ftag/segmentation only |
| `src/models/omnilearned/layers.py` | `MLP`, `DynamicTanh`, `NoScaleDropout`, `InputBlock`, `InteractionBlock`, `LocalEmbeddingBlock`, `AttBlock`, `TokenAttBlock`, `mask_outer`; `LayerScale` is defined but unused at this revision |
| `src/models/omnilearned/diffusion.py` | `MPFourier`, `perturb`, `get_logsnr_alpha_sigma`; the last is called unconditionally by `PET2.forward` |
| `src/models/omnilearned/utils.py` | `get_model_parameters` plus a replacement for the unsafe partial checkpoint loader |
| `src/scripts/train.py` | `create_omnilearned_model`, `prepare_batch_omnilearned`, `zero_muon_kinematics`, medium-backbone freeze policy, learning-rate schedule and seed policy |
| `src/dataset/preprocessing.py` | four-momentum conversion, dE/dx transform, coordinate/time scaling, PID assignment, overflow aggregation, globals and truth preparation |
| `src/dataset/dataloader.py` | pad/truncate, collate and `pid`/`add_info`/`cond` assembly |
| `src/constants/dataset.py` | `GLOBAL_COND_BASE_DIM = 10` |

Gregor's presets use four learned readout tokens and MLP ratio two:

| Preset | base dimension | heads | body blocks | head blocks |
|---|---:|---:|---:|---:|
| small | 128 | 8 | 8 | 2 |
| medium | 512 | 16 | 12 | 2 |
| large | 1024 | 32 | 28 | 4 |

The audited MINERvA defaults are four kinematic inputs, five auxiliary token
features, conditional width 10, PID width 8, coordinate dimension 2,
`use_pid=True`, no local/global interaction block, LHC interaction type,
KNN `K=10`, and classifier/regression mode as appropriate.

## Exact tensor contract

`PET2.forward(x, y, cond=None, pid=None, add_info=None)` expects:

| Tensor | Shape | Dtype | Meaning |
|---|---|---|---|
| `x` | `(B,N,4)` | float32 | eta, phi, `log(pT+1e-6)`, `log(E+1e-6)` |
| `pid` | `(B,N)` | int64 | upstream raw object/PID category 0–7 |
| `add_info` | `(B,N,5)` | float32 | transformed dE/dx, x/1e4, y/1e4, z/1e4, time/1e4 |
| `cond` | `(B,10)` or manifest-bound 13/16-wide extension | float32 | reconstructed global block; stored width and `--include-E-sum` must agree |
| `y` | `(B,)` | long/float | task label; never a reco-side OmniFold input |

The pinned dataloader pads or truncates a batch to the first 33 tokens without
an energy re-sort, even though preprocessing can retain up to 150 tokens by
default. Token ordering and both limits are therefore checkpoint inputs. The
body adds PID and auxiliary embeddings, prepends one conditional token, then
prepends four learned readout tokens. The classifier first runs its
`TokenAttBlock` head stack, flattens the four readout tokens, and applies its
MLP. Regression yields one logit; upstream classification yields
`len(task.class_idx)` logits. The OmniFold adapter requires the one-logit
binary-ratio head.

The prepared global block can be 16-wide while `ol_num_cond` defaults to 10;
the training code also accepts widths 10, 13, or 16 through a permissive
branch. A compatibility manifest must bind the stored conditional width,
feature ordering, `ol_num_cond`, and `--include-E-sum` together. A width
mismatch is fatal rather than a tolerated semantic variant.

The checkpoint is a two-level mapping. The future manifest must enumerate
every top-level component and every inner state-dict key and shape. Important
inner prefixes are:

- `checkpoint["body"]`: `embed.*`, `local_physics.*`,
  `cond_embed.0.*`, `add_embed.0.*`, `pid_embed.0.weight`, `token`,
  `in_blocks.{i}.*`, and `norm.*`;
- `checkpoint["body"]`: `interaction.*` only when `use_int=True`; these keys
  are absent under the audited MINERvA default;
- `checkpoint["classifier_head"]`: `in_blocks.{i}.*`, `fc.*`, and `out.*`;
- `checkpoint["generator_head"]`: only when the task/configuration actually
  instantiates the generator head.

`DynamicTanh` contributes `alpha` and `weight`, with no bias.
`nn.MultiheadAttention` was created with `bias=False`, so attention projection
bias keys must not be invented.

## MINERvA adapter boundary

The adapter may consume only symmetric reconstructed signal/data/background
objects for Step 1. It must build muon, photon, blob, prong and overflow
tokens under one documented reconstruction vocabulary. Truth labels,
interaction categories and prepared MC task labels remain bookkeeping or
Step-2-only information.

The pinned transforms include:

- eta clipped to `[-10,10]`;
- phi from `atan2(py,px)`;
- `log(pT+1e-6)` and `log(E+1e-6)` in the declared raw units;
- dE/dx as `log(abs(value)+0.1)` after sentinel handling and clipping;
- position and time divided by 10000;
- global calorimetry, passive recoil, Michel count, reco-muon presence,
  gamma-gamma mass, charged-pion-prong count, and per-category energy sums.

Units, missing values, type vocabulary, overflow conservation, token ordering,
and masks must be receipt-bound independently for signal, data and literal
backgrounds. Gregor's prepared public `.pb` rows cannot satisfy this boundary:
they lack the data/background/miss legs, physics weights and stable event
identity required by OmniFold.

## Two incompatible compatibility paths

### L: legacy-exact reproduction

`gregor-pet2-legacy-exact-v1` reproduces the pinned forward behavior,
including its known hazards:

1. real muon PID 0 collides with `padding_idx=0`;
2. padding is inferred from transformed `log(pT) != 0`;
3. a muon-kinematics ablation may therefore remove the token.

It may strictly load an exactly matching legacy checkpoint, subject to the
constructibility boundary below. Its purpose is reproduction/provenance
diagnosis only. It is not eligible for physics conclusions or publication
OmniFold.

### K: corrected compatibility

`gregor-pet2-corrected-v1` must:

- reserve PID 0 for padding, shift every real PID by one, and widen the
  embedding from 8 to 9 entries;
- pass an explicit boolean token mask through body and heads;
- choose and receipt whether a muon ablation keeps a blank-but-present token
  or removes it.

The mask correction preserves parameter shapes but changes forward semantics.
The PID correction changes only `pid_embed.0.weight`. A permitted,
information-preserving migration is:

```text
new[0] = 0
new[1:9] = old[0:8]
```

Every other tensor must load with an exact key and shape. The migration
receipt must enumerate loaded, remapped, skipped and mismatched keys.
Unlisted skips or mismatches are fatal.

L and K have distinct architecture/preprocessing fingerprints, output
namespaces and experimental cells. Their results may not be pooled.

## Advertised-checkpoint availability boundary

The only advertised artifacts found in the inspected source are
`best_model_pretrain_s.pt` and `best_model_pretrain_m.pt`. They are generic
OmniLearned jet-pretrained weights, not published MINERvA-fine-tuned
checkpoints. No MINERvA-fine-tuned weight artifact was found.

The upstream MINERvA path historically consumed those generic artifacts
through a shape-filtered partial load. That was necessary because the target
configuration can differ in PID width (`ol_pid_dim=8` versus PET2's default
9), `input_dim=4`, `add_dim=5`, and `cond_dim=10/13/16`. Consequently
`pid_embed`, `embed`, `add_embed`, and `cond_embed` may never have transferred;
the exact surviving keys are unknown.

If an advertised artifact does not exactly match the frozen L schema, the
strict L-P cell is **unconstructible**. The acceptable paths are:

1. obtain a licensed, hash-bound, exactly matching checkpoint; or
2. run an explicitly named diagnostic partial-transfer cell whose complete
   loaded/skipped/mismatched key inventory and loaded-parameter fraction are
   receipted and which is forbidden from carrying initialization evidence.

The diagnostic cell is not L-P or K-P and may not be promoted by relabeling.
The loaded-parameter fraction and exact key set must be reported before any
transfer result is interpreted.

## Strict checkpoint manifest

Every field below is required before weight bytes are opened:

```text
source_repo_url
source_commit_sha
vendored_files[] {path, sha256, upstream_url, license, copyright_holder}
architecture_variant
architecture_config
architecture_fingerprint
hazard_policy {pid_shift, mask_source, muon_ablation_policy}
preprocessing_revision
preprocessing_fingerprint
tensor_schema
categorical_vocabulary
state_dict_schema {top_level_keys, per_key_shapes, dtypes}
load_receipt_schema {load_mode, terminal_state, loaded, remapped, skipped,
                     mismatched, parameter_fraction}
checkpoint_sha256
checkpoint_size_bytes
weight_license
weight_redistribution_permitted
weight_provenance {url, publisher, retrieved_at, retrieved_sha256}
framework_versions
determinism_policy {seed, deterministic_algorithms, cudnn_policy}
safe_loading_policy
```

The loader must:

- verify size and SHA-256 before deserialization;
- use safetensors when available, or `torch.load(weights_only=True)` only for
  a declared legacy artifact;
- reject pickle execution;
- reject missing, extra or wrong-shaped tensors;
- forbid `strict=False`, heuristic transpose, random fallback, or an
  unreceipted partial load;
- reject a checkpoint whose architecture family differs from the requested
  backend;
- bind `load_mode` to either `strict` or `diagnostic_partial`;
- return only `eligible`, `diagnostic_only`, or `unavailable` with exact
  reasons. `diagnostic_only` is valid only for `diagnostic_partial`, and may
  never be relabeled as `eligible`.

Gregor's current `_filter_partial_state` silently drops output tensors and
shape mismatches. It must not be used for evidence-bearing transfer.

## Matched future experiment

Architecture, preprocessing and initialization must be separated:

| Cell | Architecture | Preprocessing | Initialization |
|---|---|---|---|
| L-R | legacy exact | pinned legacy | random |
| L-P [availability boundary](#advertised-checkpoint-availability-boundary) | legacy exact | pinned legacy | strictly compatible checkpoint |
| K-R | corrected | pinned/corrected receipt | random |
| K-P | corrected | pinned/corrected receipt | checkpoint plus explicit PID remap |
| K-R′ | corrected | one declared preprocessing variant | random |

Required negative controls are shape-preserving tensor permutation,
random initialization matched to checkpoint tensor statistics, and a
separately labeled trunk-only transfer. Loaded parameter fractions and exact
key sets are mandatory. Full fine-tuning and frozen-body fine-tuning are
different cells.

Only L-P minus L-R, or K-P minus K-R, on identical rows, seeds and budgets can
speak to initialization—and only if the weight license, checksum and negative
controls pass. No such evidence currently exists.

## Licensing and unresolved checkpoint facts

`gregorkrz/minerva-ml` is MIT-licensed. The upstream
`ViniciusMikuni/OmniLearned` project declares MIT in `pyproject.toml` but has
no standalone LICENSE file at the inspected revision; a vendored
implementation must preserve both projects' notices and attribution. The
public dataset is CC-BY-4.0. HyperScale is unavailable with unverifiable
licensing and is excluded.

The raw ingestion script hard-imports ROOT/PyROOT, whose LGPL/GPL obligations
are separate from the MIT model code. A clean integration should consume an
already authorized dataset or independently implement only the documented
array transforms, avoiding a vendored copy of the ROOT ingestion path unless
its licensing and distribution obligations are reviewed explicitly.

The advertised generic checkpoint files remain inaccessible and have no
verified artifact license or checksum. No MINERvA-fine-tuned checkpoint is
published. A real manifest or author response is still needed to establish:

- released PID dimension and exact input/additional/conditional widths;
- which keys actually survived Gregor's historical partial loader;
- pretraining interaction-block and head configuration;
- checkpoint SHA-256, size, license and redistribution permission;
- exact preprocessing units and conditional feature width;
- whether PID-0/padding and muon-ablation behaviors were intended.

Until all are resolved, arm F remains `unavailable`; building this design does
not change that status.
