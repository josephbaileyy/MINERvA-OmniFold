# Production commands

This interface adapts standard scalar ROOT inputs and supports explicit nominal
and cached LightGBM estimators, statistical replicas, single-band systematic diagnostics, training-split diagnostics,
strict MC closure, and linear projection.
It also plans per-playlist ROOT preparation and exposes retained guarded PET
diagnostic training, full-inventory inference and extraction. Local fixture equivalence does not authorize a production
switchover, retirement of a frozen reference, or scientific adoption.

## Local smoke

Use Python 3.11 or newer. Install the CPU dependencies in an isolated environment:

```sh
python3 -m venv .venv-production
.venv-production/bin/python -m pip install -r production/requirements.txt
```

Run from the repository root, choosing a fresh output directory:

```sh
PYTHON=.venv-production/bin/python bash production/smoke.sh /tmp/omnifold-smoke
.venv-production/bin/python -m pytest -q production/tests
```

The smoke script contains the six exact Python invocations: event generation,
nominal training, three statistical members in one process, covariance assembly,
closure, and projection. All unfolding uses real LightGBM, 800 synthetic events,
100 trees per fit, two iterations, weighted events, reconstruction misses, and
truth cuts. ROOT and TensorFlow are unnecessary. LightGBM also needs its platform
OpenMP runtime. This is a functionality test, not a production performance test.

Every entry point accepts `--config`, `--input`, `--output`, and `--plan`; synthetic
preparation omits `--input`. Help needs only the standard library. Plans read small
JSON files and check path existence, without loading event arrays or writing
outputs. Scalar execution installs `mnv_guarded_run.py` before training; numerical
package initialization and hardware discovery occur in read-only preflight.
External cluster execution still needs the governing launcher and authorization.

## Calculation and input contract

### Standard scalar production input

ROOT adaptation and `nominal-lgbm-v1` use the established `root_6_28` conda
environment with NumPy and LightGBM. Activate it using the conda hook and full
environment prefix in `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`; the pure Python
scalar adapter does not need the compiled RooUnfold wrapper. The per-playlist C++
event loop still requires the separately built ROOT/MAT environment. Do not run
full-file preparation, training or ensembles on a login node. The following are
commands for a **separately authorized allocation**, not a grant to launch one.

Edit `examples/scalar_root.json` to name the independent baseline flux file. It
accepts the native axis sets `eavail`, `eavail,q3` and `eavail,q3,W`; standard
muon phase space and purity background treatment are fixed. Starting from the
merged `events.root` named by the per-playlist preparation plan:

```sh
python production/prepare_events --config production/examples/scalar_root.json --input /data/prepared/events.root --output /data/scalar_5d.npz
python production/unfold_gbdt.py --config production/examples/nominal_5d.json --input /data/scalar_5d.npz --output /data/scalar_nominal
python production/uncertainties.py run --source statistical --mode data-plus-mc --seeds 7 8 9 --config production/examples/nominal_5d.json --input /data/scalar_5d.npz --nominal /data/scalar_nominal --output /data/scalar_members
python production/uncertainties.py combine --source statistical --mode data-plus-mc --seeds 7 8 9 --config production/examples/nominal_5d.json --input /data/scalar_members --nominal /data/scalar_nominal --output /data/scalar_covariance
python production/project.py --config production/examples/project_5d.json --input /data/scalar_covariance --output /data/scalar_4d_projection
python production/closure.py --config production/examples/nominal_5d.json --input /data/scalar_5d.npz --output /data/scalar_closure
```

Three seeds illustrate command wiring, not a sufficient scientific ensemble.
For 3D/4D, change the preparation axis list, scalar features and projection axes
together. Add `--plan` to resolve prerequisites without reading event arrays.
The adapter reuses the retained collectors, POT/flux loaders and purity builder.
The source entry index travels through those same collectors as an extra finite
coordinate and is removed before binning/training. IDs are actual
`source-file SHA256 / tree / entry` identities, **not** invented run/event numbers
or claims of identity across separately merged files. Reco and truth share one
signal-tree entry, including native misses. Geometry normalization comes from the
retained tracker constant, never summed ROOT nucleon metadata. The full Git
revision, source hashes, original paths and producer configuration are recorded.

### Estimator variants

`examples/scalar.json` selects features in training order. The backend is
`cached-lgbm-v1`, with fixed-final iteration policy, no feature scaling, and one
seed shared by both classifiers and the miss regressor. The model settings are
100 estimators, eight leaves, learning rate 0.1. The resolved configuration and
dependency versions and complete runtime estimator parameters are recorded.
Training-split studies set `train_fraction < 1`
in the nominal configuration; `--source ml` varies only `split_seed`.

`examples/nominal_5d.json` instead selects `nominal-lgbm-v1`: it calls the exact
`OmniFold_helper_functions.omnifold` used by the retained N-D nominal driver,
with classifier/regressor seeds `s,s+1,s+2`, all training rows and no feature
scaling. Its nominal, statistical members and strict closure use that same
engine. The cached variant calls `omnifold_nn_core.omnifold_loop` with `s,s,s`
and supports explicit split studies. Both retain 100 trees, eight leaves,
learning rate 0.1, native masks and miss regression. Neither variant replaces or
adopts the other. The split variant cannot provide ML uncertainty for the
all-row nominal merely because its output dimensions agree.

An event NPZ must contain the following, with no pickle objects:

| Fields | Meaning |
|---|---|
| `MCgen`, `MCreco`, `measured` | Finite `(events, features)` matrices, with names in metadata |
| `truth_id`, `reco_id`, `data_id` | Unique stable event IDs; truth/reco IDs must agree row for row |
| `pass_truth`, `pass_reco`, `meas_pass_reco` | Explicit boolean selection masks |
| `w_truth`, `w_reco`, `measured_weights` | Aligned nonnegative weights, already POT scaled as required by the input procedure |
| `denom_nd`, `flux`, `data_pot`, `n_nucleons` | Full denominator grid, per-flux-axis integrals in m^-2/POT, POT, and geometry normalization |
| `metadata` | JSON scalar with selection/background identity, feature names/units, normalization units/source, flux axis, fixed denominator policy, and output contract |

The output contract declares ordered named axes, units, edges, C flattening,
full-grid boolean support, density/yield meaning, and base value units. Scalar
densities use `cm^2/nucleon` divided by the product of declared axis units. The
synthetic preparation code is an input-format example. `scalar-root` establishes
these fields from the native source; unidentified historical caches are not
accepted as substitutes for that source.

`signal-only` and already `preweighted-purity` inputs are supported. Signed and
refined targets retain their original drivers. Statistical mode is mandatory:
`--mode data-only` varies measured weights; `--mode data-plus-mc` additionally
applies one MC Poisson draw to both truth and reco. The MC stream uses bootstrap
seed + 10,000,000. The denominator stays fixed and completeness is recomputed,
matching `bootstrap_nd.py`. This convention is explicit, not a new UQ adoption.

Statistical/ML `uncertainties.py combine` requires the exact nominal, member seeds,
code, configuration and support. It uses mean-centered sample covariance with
divisor `N-1` and reports the mean shift separately. PET statistical/ML products
and cross-source totals are not exposed.

### Systematic families

Edit `examples/systematic.json` to declare a complete native band inventory.
Paths are relative to `--input` during `run` (absolute paths also work). Both
operations require the same inventory and an unshifted `scalar-root` nominal
produced with matching adapter dependencies, data, baseline flux and estimator.
In the ROOT environment and a separately authorized allocation:

```sh
python production/uncertainties.py run --source systematic --inventory production/examples/systematic.json --config production/examples/nominal_5d.json --input /data/universes --nominal /data/scalar_nominal --output /data/systematic_members
python production/uncertainties.py combine --source systematic --inventory production/examples/systematic.json --config production/examples/nominal_5d.json --input /data/systematic_members --nominal /data/scalar_nominal --output /data/systematic_covariance
python production/project.py --config production/examples/project_5d.json --input /data/systematic_covariance --output /data/systematic_4d
```

Lateral bands require per-playlist active-universe ordinary trees, exact native
band/index metadata, all four migration counts and finite-support denominator
closure. Dump-all CV-support lateral branches are refused. Vertical bands reuse
the native signal, truth-denominator and background weight branches together;
purity is rebuilt per universe. `Flux` additionally requires `flux_universe_file`
in the inventory, with the native `hFluxCV`/`hFluxUniv` table: the same universe
index varies both event weights and flux, and the table CV must match baseline.
Temporary prepared caches are removed after each member; member products bind
the raw sources and retain preparation metadata and source support.

Combination is **one declared band only**: native MAT mean-centered `1/N`
covariance, CV-centered second moment and common shift are all retained. Both
covariance variants project with the same linear map. These are quarantined
diagnostics, not an adopted scalar-5D uncertainty; mean-centering alone does not
resolve its gate. No block sum, unified-throw total or PET covariance is inferred.
Neither inventory completeness nor successful execution supplies adoption.

Closure copies selected signal reco rows and weights into pseudo-data and compares
the reused calculation with the known truth extraction. Nominal-driver closure
uses unity completeness, including when the real-data input has a purity target;
cached signal-only closure retains its declared denominator convention. These are
strict signal-MC closures, not independent pseudo-experiment coverage. Projection applies `P x` and
`P C P.T`, including off-diagonal terms and integrated-axis widths for densities.
Reordered axes are supported. Native scalar inputs declare `reported-source`
projection, matching `project_cov_nd.py`: each destination receives the supported
source cells with their widths, and partial fibers are explicitly marked. This
does not claim a full-domain marginal over unreported cells. Inputs without that
contract require complete fibers. Normalized-shape propagation is unsupported.
Empty resampled bins keep the nominal support with the retained zero result and
an `empty_supported_bins` flag; the interface does not silently select a new mask.

Scalar outputs are fresh directories with `result.npz` and a final `record.json`.
Only supported bins enter `xsec`; intermediate histograms retain the full grid.
`--resume` checks complete status, payload digest, resolved configuration, input
digest, calculation-scoped source digests and dependency versions. Full Git
revision is recorded separately as provenance: documentation and unrelated PET
changes do not invalidate scalar resume or member assembly. Relevant engine,
extraction, perturbation and guard changes still reject reuse. Schema-1 products
from the initial interface remain historical and are not resumed as schema-2
products; no bypass is provided. Partial outputs require
a fresh destination. Members load and hash the event input once per invocation.
Completion means software execution succeeded, and carries no scientific adoption.

## ROOT and PET environments

Plan event preparation using an explicit playlist inventory and separate flux:

```sh
python production/prepare_events --config production/examples/prepare_root.json --input production/examples/playlists.json --output /data/prepared --plan
python production/unfold_pet.py train --config production/examples/pet.json --input /data/full_event.npz --output /data/pet_diagnostic --plan
```

Replace the example paths with actual prerequisites. `root-plan` always plans; it
never executes a C++ binary or submits a job. Each manifest pair must belong to
one playlist. Run the resulting commands in the established ROOT/MAT environment
under its governing launcher. The safe merger handles large TTrees. Prepare flux
with the baseline event loop and `combine_flux_MEFHC.py` separately; do not use
summed nucleon metadata from a merged file.

For a separately authorized PET diagnostic run, edit the three example JSON files
to use immutable inputs. In the established TensorFlow environment, train and then
infer over the **full** inventory, not just the training subsample:

```sh
python production/unfold_pet.py train --config production/examples/pet.json --input /data/full_event.npz --output /data/pet_diagnostic
python production/unfold_pet.py infer --config production/examples/pet_infer.json --input /data/full_event.npz --output /data/pet_inference
```

The inference config points to `/data/pet_diagnostic/weights.npz`; the weights'
native inference contract supplies architecture, checkpoint and fitted scaling.
Training requires the certified target NPY, target receipt and Gate-3 manifest.
The existing annealed training policy and inference agreement tolerance are fixed.

In a separate established ROOT/MAT process (`source setup_salloc_env.sh` from the
repository root), extract with the independent baseline-flux product:

```sh
python production/unfold_pet.py extract --config production/examples/pet_extract.json --input /data/full_event.npz --output /data/pet_extraction
```

The extraction config consumes `/data/pet_inference/push.npz`. Each stage accepts
`--plan` without loading arrays or either numerical runtime. Outputs are fresh
directories holding native NPZ/`.done` products and `production.json`; extraction
also writes `summary.json`. The supplied inventory must match the weights/push
content digest. The checkout guard remains mandatory and rejects imports from
another checkout; no checkpoint override or overwrite is exposed. These commands
do not submit jobs, authorize compute, construct PET uncertainty or promote a
result. PET remains diagnostic with its central/statistical pairing declined.

## Compatibility and workflow size

| Retained route | Interface for the migrated scope |
|---|---|
| Per-playlist C++ event loop and separate flux preparation | `prepare_events --config ... --plan` |
| `nn_dump_inputs.py` / N-D collectors | `prepare_events` with `scalar-root`, retaining source-entry identity and native double precision |
| `unfold_nd_omnifold_unbinned.py` | `unfold_gbdt.py` with explicit `nominal-lgbm-v1` |
| `bootstrap_nd.py`, `combine_cov_nd.py` | `uncertainties.py run`, then `combine` |
| `train_fullevent_nominal.py` | `unfold_pet.py`, preserving guarded native execution |
| `extract_fullevent_fps.py --stage push`, then `--stage xsec` | `unfold_pet.py infer`, then `extract` in separate environments |
| N-D `--closure` | `closure.py` for strict signal-MC closure |
| `project_cov_nd.py`, `xsec_nd.py` | `project.py` for compatible interface products |

The retained nominal driver calls `OmniFold_helper_functions.omnifold` and uses
seeds `s,s+1,s+2`. Cached replicas call `omnifold_nn_core.omnifold_loop` with
`s,s,s`. They are explicit variants. Here nominal, statistical members, training
members, and closure all call `scalar.calculate`, which owns extraction and calls
the selected retained engine. No new unfolding loop or selection implementation
was copied. Receipt-bound engines and collectors are retained; the adapter adds
source identity without editing them. The frozen 2D path
and all existing files remain intact.

For three cached replicas plus assembly, retained commands require four Python
invocations (three `bootstrap_nd.py`, one `combine_cov_nd.py`); this interface
requires two. The complete local smoke has one user command and six internal
Python invocations. There was no complete bounded local recipe to count before.
Operational references for those cached tasks were four implementation files
(nominal, bootstrap, combine, projection); the supported fixture uses this guide.
This is not a reduction of mandatory instruction context: `AGENTS.md` (145 lines
at the migration base), `docs/CURRENT_WORK.md` (35 lines), the governing OI record,
and supplied session instructions remain required, with `production/AGENTS.md`
added. Workstream status/reference routes still apply to production. No speedup
or context-token reduction is inferred from these command/document counts.
