# Migration verification

Operational commands belong in [the production guide](../README.md). Tests prove
software behavior, not estimator equivalence on real inputs, coverage or adoption.
Historical verification at the initial interface is preserved in Git at
`972face8:production/tests/README.md`.

## Lightweight checks

These checks perform no training, event-file scans, ROOT jobs or GPU work:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest -q production/tests/test_compatibility.py production/tests/test_pet_stages.py production/tests/test_projection.py production/tests/test_nominal_backend.py production/tests/test_root_input.py
python -m ruff check production
python -m black --check --workers 1 production
python -m mypy --strict production/minerva_production
```

The first command passes 32 tests on Python 3.11, NumPy 2.4.6 and pytest 9.1.1.
Compatibility tests mutate actual dependency-file copies and exercise resume and
covariance assembly: unrelated PET/document changes remain compatible; relevant
engine, extraction, perturbation and guard changes fail. Full revisions remain
in provenance. PET tests cover guarded argv, runtime separation, full-inventory
digest binding, fixed policy and native completion handling using a stand-in
subprocess, **not** a PET backend execution. Projection tests check unequal bin
widths, source correlations, support and reordered axes independently.

The six no-fit command tests and six-entrypoint standard-library-only help check
also pass. Run subprocess checks outside a sandbox that denies the site's MUNGE
socket: its authentication error can pollute JSON stdout. Ruff, Black and strict
mypy pass. This does not certify retained production runtimes.

In the activated ROOT 6.28/12 environment, the following additional no-fit check
passes using six-row in-memory trees and a temporary ROOT/NPZ fixture:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m production.tests.root_adapter_check
```

All four retained collectors return exactly the same arrays with and without
entry-index transport; selected identities are checked against explicit source
rows. The full adapter output passes scalar input validation, including paired
IDs, POT scaling, native nucleon normalization and purity weights. These are
synthetic protocol fixtures, **not** real-input parity. No fit runs in this check.
Nominal backend tests inspect dispatch to the original engine, seeds, inputs,
weights and closure normalization using a no-fit stand-in. Actual training parity
still needs an authorized compute allocation.

Sparse reported-source projection is compared exactly against the retained
`project_cov_nd.build_projection`, including cross-bin covariance. Generic inputs
without that domain declaration still reject partial marginals. Empty resampled
bins retain the nominal support and the retained extractor's zero result.

The full `python -m pytest -q production/tests` includes LightGBM fits and the
six-stage synthetic smoke. Run it only where compute is authorized; no allocation
is granted by this migration. Synthetic tests do not replace real-input parity.

## Continuation checklist

Work on `feat/production-interface`, starting from `972face8`; keep the shared
canonical checkout and its products untouched. The external migration goal remains
the scope; this checklist is a progress record, not authorization.

| Requirement | Current implementation / remaining verification |
|---|---|
| Real inputs | `scalar-root` adapter implemented for standard 3D/4D/5D inputs; native collector and complete tiny ROOT fixture checks pass; real-input execution remains unmet |
| Intended estimator | Explicit original nominal and cached engines share dispatch and extraction across nominal/members/closure; no-fit tests pass; authorized training parity remains unmet |
| PET operations | Implemented train/infer/extract routing; actual TensorFlow/ROOT execution remains unverified and needs the named compute authority |
| Uncertainty operations | Cached statistical/split diagnostics exist; governing systematic and established combination operations still need integration, without adopting quarantined products |
| Compatibility | Scoped dependency hashes bind the selected engine only; full revision is separate provenance, including ROOT preparation |
| Operational burden | Standard scalar and PET commands live in the operational guide; finish uncertainty commands and final guidance/ownership cleanup |
| Demonstration | Real-input bounded parity remains unmet; requires data/runtime and exact existing allocation authority, never a login-node fit |

Next implement the applicable systematic and established uncertainty-combination
operations from their exact governing contracts. Do not substitute a weight-only
cache for selection-complete lateral inputs or mix the original nominal with the
cached split estimator. Preserve receipt-bound engines and historical evidence.
No scientific result, pairing or gate has changed. The standard ROOT path is
implemented but has not read a real production event file or run training.
