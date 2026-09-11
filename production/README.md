# Production commands

This interface supports a matched cached-input LightGBM calculation, statistical
replicas, training-split diagnostics, strict MC closure, and linear projection.
It also plans per-playlist ROOT preparation and invokes the retained guarded PET
diagnostic trainer. Local fixture equivalence does not authorize a production
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

`examples/scalar.json` selects features in training order. The backend is
`cached-lgbm-v1`, with fixed-final iteration policy, no feature scaling, and one
seed shared by both classifiers and the miss regressor. The model settings are
100 estimators, eight leaves, learning rate 0.1. The resolved configuration and
dependency versions and complete runtime estimator parameters are recorded.
Training-split studies set `train_fraction < 1`
in the nominal configuration; `--source ml` varies only `split_seed`.

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
synthetic preparation code is a complete input-format example. There is no
automatic conversion from unidentified historical row caches: a real-data adapter
must establish IDs, selections, background, normalization and support first.

`signal-only` and already `preweighted-purity` inputs are supported. Signed and
refined targets retain their original drivers. Statistical mode is mandatory:
`--mode data-only` varies measured weights; `--mode data-plus-mc` additionally
applies one MC Poisson draw to both truth and reco. The MC stream uses bootstrap
seed + 10,000,000. The denominator stays fixed and completeness is recomputed,
matching `bootstrap_nd.py`. This convention is explicit, not a new UQ adoption.

`uncertainties.py combine` requires the exact nominal, member seeds, code,
configuration, and support. It assembles one source using the retained
mean-centered sample covariance with divisor `N-1`, and records the mean shift
separately. It does not sum covariance families. Cached systematic execution is
refused: selection-complete lateral inputs, per-universe background, and the
governing construction are required. PET statistical/ML products are not exposed.

Closure copies selected signal reco rows and weights into pseudo-data and compares
the reused calculation with the known truth extraction. It is strict signal-MC
closure, not independent pseudo-experiment coverage. Projection applies `P x` and
`P C P.T`, including off-diagonal terms and integrated-axis widths for densities.
Reordered axes are supported. Entire excluded fibers remain excluded; partial
fibers fail explicitly. Normalized-shape propagation is unsupported.

Scalar outputs are fresh directories with `result.npz` and a final `record.json`.
Only supported bins enter `xsec`; intermediate histograms retain the full grid.
`--resume` checks complete status, payload digest, resolved configuration, input
digest, source digests, revision, and dependency versions. Partial outputs require
a fresh destination. Members load and hash the event input once per invocation.
Completion means software execution succeeded, and carries no scientific adoption.

## ROOT and PET environments

Plan event preparation using an explicit playlist inventory and separate flux:

```sh
python production/prepare_events --config production/examples/prepare_root.json --input production/examples/playlists.json --output /data/prepared --plan
python production/unfold_pet.py --config production/examples/pet.json --input /data/full_event.npz --output /data/pet_diagnostic --plan
```

Replace the example paths with actual prerequisites. `root-plan` always plans; it
never executes a C++ binary or submits a job. Each manifest pair must belong to
one playlist. Run the resulting commands in the established ROOT/MAT environment
under its governing launcher. The safe merger handles large TTrees. Prepare flux
with the baseline event loop and `combine_flux_MEFHC.py` separately; do not use
summed nucleon metadata from a merged file.

PET execution uses the same command without `--plan` in the TensorFlow environment,
after the named run is authorized. It requires the certified target NPY, target
receipt, full-event input, and Gate-3 manifest. It retains the existing full-event
representation, annealed training policy, native weights/marker formats, and import
guard. A legacy import resolving to another checkout is a prerequisite failure;
the adapter does not bypass it. PET output is training weights, not a cross section.
Full-inventory inference and ROOT extraction remain separate stages; exact
commands and unavailable checks are in [tests/README.md](tests/README.md).

## Compatibility and workflow size

| Retained route | Interface for the migrated scope |
|---|---|
| Per-playlist C++ event loop and separate flux preparation | `prepare_events --config ... --plan` |
| `unfold_nd_omnifold_unbinned.py` | `unfold_gbdt.py` for explicitly contracted caches |
| `bootstrap_nd.py`, `combine_cov_nd.py` | `uncertainties.py run`, then `combine` |
| `train_fullevent_nominal.py` | `unfold_pet.py`, preserving guarded native execution |
| N-D `--closure` | `closure.py` for strict signal-MC closure |
| `project_cov_nd.py`, `xsec_nd.py` | `project.py` for compatible interface products |

The retained nominal driver calls `OmniFold_helper_functions.omnifold` and uses
seeds `s,s+1,s+2`. Cached replicas call `omnifold_nn_core.omnifold_loop` with
`s,s,s`. They are explicit variants. Here nominal, statistical members, training
members, and closure all call `scalar.calculate`, which owns extraction and calls
the existing cached loop. No new unfolding loop was copied. The frozen 2D path
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
