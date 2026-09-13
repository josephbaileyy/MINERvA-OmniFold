# Production workflows

Run from the repository root. These commands grant **no compute authority**:
full-file preparation, fits and ensembles need a separately authorized allocation,
not a login node. Keep the governing workstream/OI routes and checkout guard.
PET remains diagnostic with central/statistical pairing declined; non-2D
covariances remain quarantined. Successful execution is not adoption.

## Environments and inputs

- Scalar ROOT preparation and `nominal-lgbm-v1`: Python 3.11, ROOT 6.28,
  NumPy and LightGBM. The pure-Python adapter needs no compiled RooUnfold wrapper.
- Cached fits, covariance assembly and projection: Python 3.11 and
  `production/requirements.txt`; LightGBM also needs its OpenMP runtime.
- C++ event preparation and PET extraction: built ROOT/MAT environment,
  initialized by `source setup_salloc_env.sh` from this checkout.
- PET training/inference: the established `tensorflow/2.15.0` module, in a
  separate process from ROOT extraction. Do not load TensorFlow into a ROOT
  extraction process or borrow another checkout's Python modules.

Activate the scalar ROOT environment on Perlmutter (without `set -u`):

```sh
source /global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/etc/profile.d/conda.sh
conda activate "${ROOT628_PREFIX:-$HOME/.conda/envs/root_6_28}"
```

All six entry points accept `--config`, `--input`, `--output` and `--plan`;
synthetic preparation omits `--input`. Help needs only the standard library.
Plans read configuration and check paths, never scan arrays or write products.
Replace example `/data` paths with immutable prerequisites. Outputs must be fresh.

## Scalar nominal → members → covariance → projection

Edit `production/examples/scalar_root.json` for the **independent baseline flux** file.
It reads the native merged ROOT inventory with signal, data, background and
truth-denominator trees. Supported extra axes are `eavail`, `eavail,q3` and
`eavail,q3,W`; standard muon phase space and native purity treatment are fixed.

Execute the standard 5D path in an authorized allocation:

```sh
python production/prepare_events --config production/examples/scalar_root.json --input /data/prepared/events.root --output /data/scalar_5d.npz
python production/unfold_gbdt.py --config production/examples/nominal_5d.json --input /data/scalar_5d.npz --output /data/scalar_nominal
python production/uncertainties.py run --source statistical --mode data-plus-mc --seeds 7 8 9 --config production/examples/nominal_5d.json --input /data/scalar_5d.npz --nominal /data/scalar_nominal --output /data/scalar_members
python production/uncertainties.py combine --source statistical --mode data-plus-mc --seeds 7 8 9 --config production/examples/nominal_5d.json --input /data/scalar_members --nominal /data/scalar_nominal --output /data/scalar_covariance
python production/project.py --config production/examples/project_5d.json --input /data/scalar_covariance --output /data/scalar_4d_projection
python production/closure.py --config production/examples/nominal_5d.json --input /data/scalar_5d.npz --output /data/scalar_closure
```

Three seeds demonstrate wiring, not adequate scientific ensemble size. For 3D/4D,
change preparation axes, training features and projection axes together.
Statistical mode is explicit: `data-only` resamples measured weights;
`data-plus-mc` additionally applies the same Poisson factor to paired truth/reco
MC, using seed + 10,000,000. The denominator and background remain fixed under
this two-stream bootstrap; completeness is recomputed. This is not a new UQ model.

### Estimators and split diagnostics

| Backend | Retained implementation and policy |
|---|---|
| `nominal-lgbm-v1` | Original `OmniFold_helper_functions.omnifold`; classifier/regressor seeds `s,s+1,s+2`; all rows |
| `cached-lgbm-v1` | `omnifold_nn_core.omnifold_loop`; seeds `s,s,s`; optional explicit training split |

Both preserve 100 trees, eight leaves, learning rate 0.1, native masks, miss
regression, no feature scaling and fixed-final iteration choice. Nominal,
replicas and closure call the same selected engine and shared extraction.
Resolved settings and runtime estimator parameters are recorded.

ML split diagnostics require their **own matching split nominal**, never the
all-row nominal above. The example sets `train_fraction=0.8`; only
`split_seed` changes across these members:

```sh
python production/unfold_gbdt.py --config production/examples/cached_split_5d.json --input /data/scalar_5d.npz --output /data/split_nominal
python production/uncertainties.py run --source ml --seeds 7 8 9 --config production/examples/cached_split_5d.json --input /data/scalar_5d.npz --nominal /data/split_nominal --output /data/split_members
python production/uncertainties.py combine --source ml --seeds 7 8 9 --config production/examples/cached_split_5d.json --input /data/split_members --nominal /data/split_nominal --output /data/split_covariance
```

Statistical/ML assembly uses mean-centered `1/(N-1)` sample covariance and
reports the mean shift separately. Identical shape does not authorize pairing a
split covariance with a different estimator. No cross-source total is exposed.

### Systematic families

Edit `production/examples/systematic.json` to declare one complete native band inventory.
Member paths are relative to `--input` during `run` (absolute paths also work).
Use the same inventory for assembly and a matching, unshifted `scalar-root`
nominal. Run in the scalar ROOT environment:

```sh
python production/uncertainties.py run --source systematic --inventory production/examples/systematic.json --config production/examples/nominal_5d.json --input /data/universes --nominal /data/scalar_nominal --output /data/systematic_members
python production/uncertainties.py combine --source systematic --inventory production/examples/systematic.json --config production/examples/nominal_5d.json --input /data/systematic_members --nominal /data/scalar_nominal --output /data/systematic_covariance
python production/project.py --config production/examples/project_5d.json --input /data/systematic_covariance --output /data/systematic_4d
```

- Lateral bands require active-universe ordinary trees, exact native band/index,
  all four migration counts, native misses and finite-support denominator closure.
  Dump-all CV-support lateral branches are refused.
- Vertical bands vary native signal, denominator and background weights together;
  purity is rebuilt. `Flux` also requires `flux_universe_file` in the inventory:
  native `hFluxCV`/`hFluxUniv` arrays, the same universe index as event weights,
  and a table CV matching baseline flux.
- Assembly is **one declared band only**: native MAT mean-centered `1/N`
  covariance, CV-centered second moment and common shift are all retained.
  Neither centering is adopted; mean-centering alone cannot resolve the 5D gate.
  No block-sum, unified-throw total or PET uncertainty is inferred.
- Temporary prepared caches are removed per member. Results retain source
  hashes, preparation metadata and source support; extraction uses nominal support.

## Preparation and PET stages

Plan per-playlist C++ preparation with separate baseline-flux normalization:

```sh
python production/prepare_events --config production/examples/prepare_root.json --input production/examples/playlists.json --output /data/prepared --plan
```

`root-plan` never runs a binary or submits a job. Execute its returned commands
only under the governing ROOT/MAT launcher: one playlist per manifest pair,
installed event-loop binary, safe merger. Its `events.root` output feeds the
scalar adapter above. Prepare flux separately with the baseline event loop and
`combine_flux_MEFHC.py`; merged nucleon metadata is not geometry normalization.

For authorized PET work, edit `production/examples/pet.json`,
`production/examples/pet_infer.json` and `production/examples/pet_extract.json`.
Training requires the certified target NPY, receipt and
Gate-3 manifest. In the established TensorFlow shell, run training and
**full-inventory** inference, not inference on only the training subsample:

```sh
module load tensorflow/2.15.0
python production/unfold_pet.py train --config production/examples/pet.json --input /data/full_event.npz --output /data/pet_diagnostic
python production/unfold_pet.py infer --config production/examples/pet_infer.json --input /data/full_event.npz --output /data/pet_inference
```

In a separate ROOT/MAT shell, extract using the independent baseline flux:

```sh
source setup_salloc_env.sh
python production/unfold_pet.py extract --config production/examples/pet_extract.json --input /data/full_event.npz --output /data/pet_extraction
```

Inference consumes `pet_diagnostic/weights.npz` and its native architecture,
checkpoint and fitted scaling contract. Extraction consumes
`pet_inference/push.npz`. Inventory digests must match. The annealed training
policy, inference tolerance, native completion checks and checkout guard remain
mandatory. No overwrite, checkpoint override, PET covariance or Gate-6 action
is exposed. Native products and `production.json` remain in each output directory.

## Contracts, resume and validation

The scalar adapter reuses native collectors, selections, POT/flux loaders and
purity construction. IDs are actual `source-file SHA256/tree/entry`; paired
truth/reco entries include misses. They are not invented run/event identities or
cross-merge identity claims. Source-entry transport is removed before training.
Geometry uses the retained tracker constant.

NPZ inputs contain aligned feature matrices/weights/masks/IDs, denominator,
flux/POT/nucleons and JSON metadata declaring selection, background, units,
normalization source and full-grid output support. Unidentified old caches are
not substitutes. Signed/refined scalar targets retain their original drivers.

Products contain `result.npz` and final `record.json`. `--resume` requires
complete status, payload digest, inputs, resolved settings, relevant code/runtime
dependencies and compatible contracts. Full Git revision is separate provenance:
docs and unrelated PET changes do not invalidate scalar reuse. Partial outputs
need fresh destinations; schema-1 products cannot resume as schema-2. No bypass.

Projection applies `P x` and `P C P.T`, including correlations and integrated
axis widths. Native inputs use reported-source marginals and mark partial fibers;
generic inputs require complete fibers. Empty varied bins keep nominal support
and an explicit flag. Normalized-shape propagation is unsupported. Closure is
strict signal-MC closure (native nominal unity completeness; cached signal-only
denominator convention), not coverage.

For synthetic smoke in an authorized compute environment:

```sh
python3 -m venv .venv-production
.venv-production/bin/python -m pip install -r production/requirements.txt
PYTHON=.venv-production/bin/python bash production/smoke.sh /tmp/omnifold-smoke
.venv-production/bin/python -m pytest -q production/tests
```

The smoke runs real LightGBM on 800 synthetic events. For measured no-fit checks
and precise outstanding real-input parity, see [tests/README.md](tests/README.md).
Synthetic checks cannot substitute for real-input or trained-chain evidence.

## Old-to-new map and execution ownership

| Retained command / implementation | Migrated operation |
|---|---|
| Per-playlist C++ loop + independent flux preparation | `prepare_events --plan` |
| `nn_dump_inputs.py` / native N-D collectors | `prepare_events` scalar-root mode, preserving native double precision |
| `unfold_nd_omnifold_unbinned.py` | `unfold_gbdt.py`, explicit nominal backend |
| `bootstrap_nd.py`, `combine_cov_nd.py` | `uncertainties.py run/combine` |
| N-D `--universe` + native MAT covariance math | `uncertainties.py --source systematic` |
| N-D `--closure`, `project_cov_nd.py` | `closure.py`, `project.py` |
| `train_fullevent_nominal.py` | `unfold_pet.py train` |
| `extract_fullevent_fps.py --stage push/xsec` | `unfold_pet.py infer/extract` |

The previous cached-member recipe, with its own native cache and ROOT CV, was:

```sh
for seed in 7 8 9; do
  python nd-unfolding/bootstrap_nd.py --npz /data/legacy/of_inputs_5d.npz --seed "$seed" --iters 5 --estimator-seed 42 --out "/data/legacy/members/res_boot_${seed}.npz"
done
python nd-unfolding/combine_cov_nd.py --glob '/data/legacy/members/res_boot_*.npz' --expected-ids 7-9 --cv /data/legacy/cached_cv.root --tag stat5d --out /data/legacy/covariance.root
```

The statistical `run`/`combine` commands above replace those four Python
invocations with two. To retain the cached estimator, set `backend` to
`cached-lgbm-v1` in the same all-row config for its nominal and members; the
split example defines a different estimator. Old anonymous caches and ROOT
products are not interface inputs. This command count does not establish parity.
PET still uses three runtime-separated invocations but one
command interface. Operational recipes live here, not across nominal, bootstrap,
combine, projection and PET verification files. Mandatory AGENTS/workstream/OI
routes are unchanged; no context-token or runtime-speedup claim follows.

Scalar operations share `scalar.calculate`; there is no copied unfolding loop or
selection implementation. Native engines, collectors, math and receipt-bound
launchers retain calculation ownership and remain intact, including frozen 2D
reproduction. They are dependencies, not newly competing production recipes.
Historical interface guidance is recoverable at `972face8:production/README.md`.
