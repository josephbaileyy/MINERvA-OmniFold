# Verification and integration limits

The software tests exercise actual CPU LightGBM fits. They do not establish
production equivalence, coverage, central pairing, or publication adoption.

Run the interface checks from the repository root:

```sh
python -m pytest -q production/tests
python -m ruff check production
python -m black --check production
python -m mypy --strict production/minerva_production
```

The delivered interface suite passes 23 tests with one optional ROOT import check
skipped on Python 3.14, NumPy 2.5.3, LightGBM 4.7.0, scikit-learn 1.9.1 and
pytest 9.1.1. Ruff, Black and strict mypy pass. The smoke runs as part of the suite;
its exact standalone invocation is in the production guide.

The interface plus N-D extraction, annealed-estimator and PET nominal-launcher
checks also pass on Python 3.11 with NumPy 1.26.4, LightGBM 4.6.0,
scikit-learn 1.6.1 and pytest 8.4.2: 69 passed, two optional checks skipped.
This dependency combination emits scikit-learn feature-name warnings for the
retained LightGBM array interface; the numerical comparisons pass unchanged.

| Requirement | Evidence |
|---|---|
| Six useful entry points and cheap help | All six `--help` commands run under `python -S`, without site packages |
| Shared nominal/member calculation | Nominal, statistical members, ML split members and closure call `scalar.calculate`; actual LightGBM output varies with the data |
| Matched cached-replica behavior | `test_legacy_nominal_and_bootstrap_equivalence` runs the retained `bootstrap_nd.py` executable on the same selected rows and seed |
| Alignment and normalization | Exact identity/mask/paired-weight checks; independent prior, unfolded-count, completeness, density and total calculations |
| Numerical tolerance | Relative `1e-12`, absolute zero, fixed before comparisons; it cannot accept arbitrary differences at cross-section scales |
| Projection arithmetic | Hand-calculated unequal-width examples with correlations, reordered axes, density/yield semantics and missing support; metadata round-trip |
| Resume and family assembly | Changed config, partial output, corrupt payload, wrong perturbation and missing member fail; compatible complete nominal resumes |
| Preserved references | All changes are additions under `production/`; retained engines, entry points and evidence bytes are untouched |

## Reused-contract suites

The following broader check was also run:

```sh
python -m pytest -q nd-unfolding/xsec_nd.py nd-unfolding/tests/test_uq_remediation.py nd-unfolding/tests/test_annealed_estimator.py nd-unfolding/tests/test_pet_fullevent_nominal_launcher.py nd-unfolding/tests/test_mnv_guarded_run.py
```

On Python 3.14 it reports 546 passed, 4 skipped, and 11 failures (including two
mutation subtests). Every failing case also reproduces in an untouched, detached
checkout of base `77a4af38c259f51ed2ad044d8c3fc8e1f40e2c3c`:

- Two UQ mutation subtests execute source without `__file__` and fail with
  `NameError: name '__file__' is not defined`.
- Two launcher inventory tests expect an older inventory: the additional
  `sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh` and `217 != 216` already fail on base.
- One shell-path assertion compares macOS `/private/var` with `/var` after
  normalizing only one operand.
- Six guard tests exercise interpreter-specific subprocess internals; their
  Python 3.14 failures include `TypeError: fork_exec expected 22 arguments, got 23`.
  The 36 tests in those three guard classes all pass under Python 3.11.

The migration does not edit these contracts or suppress their failures. The
N-D extraction self-tests, annealed-estimator tests, and retained PET nominal
launcher tests pass within that run. The complete repository suite, which includes
cluster/data-dependent campaigns, was not run.

## Production checks not run

- C++/ROOT/MAT event-loop execution, per-playlist normalization reconstruction,
  large ROOT merging, and parity against the frozen 2D production reference:
  require the ROOT/MAT runtime and original event/flux inputs.
- PET training, full-inventory inference and ROOT extraction: require TensorFlow,
  certified full-event inputs/target/manifest, compatible guarded import roots,
  and the named compute authorization. Local plan/prerequisite tests are not PET
  backend execution evidence.
- Full-data scalar nominal/replica equivalence and any production campaign:
  require the matching production environment, data, configuration and authority.
- Selection-complete systematic construction, total-covariance assembly, PET
  statistical/ML products, normalized-shape propagation and coverage are outside
  this supported interface. Unsupported operations fail explicitly. No candidate
  covariance is promoted or treated as the adopted scalar-5D trunk.

For an authorized PET diagnostic run, the public training command preserves the
native `weights.npz` and its `.done` marker. It also writes `production.json` with
the resolved adapter plan, source identity and status. Use the retained extractor
for the two different runtime stages; substitute actual immutable paths below.

In the established TensorFlow environment, infer the full-inventory push:

```sh
python nd-unfolding/mnv_guarded_run.py --expect-root "$PWD" -- nd-unfolding/pet/extract_fullevent_fps.py --stage push --weights /data/pet_diagnostic/weights.npz --inputs /data/full_event.npz --push-out /data/pet_full_push.npz
```

In the established ROOT environment, extract using that complete push:

```sh
python nd-unfolding/mnv_guarded_run.py --expect-root "$PWD" -- nd-unfolding/pet/extract_fullevent_fps.py --stage xsec --inputs /data/full_event.npz --push-out /data/pet_full_push.npz --out /data/pet_xsec.npz --summary /data/pet_xsec.json --mcfile /data/baseline_flux/runEventLoopMC_MEFHC.root --flux-hist pTmu_reweightedflux_integrated --n-nucleons 3.2353e30
```

These commands are prepared reproduction instructions, not measured integration
results or permission to launch. Use the exact current source/launcher bindings.
The guard must continue to refuse legacy imports resolving to another checkout.
PET remains diagnostic, and its declined central/statistical pairing is unchanged.
