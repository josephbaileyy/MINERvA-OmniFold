# Migration verification

Operational commands belong in [the production guide](../README.md). Tests prove
software behavior, not estimator equivalence on real inputs, coverage or adoption.
Historical verification at the initial interface is preserved in Git at
`972face8:production/tests/README.md`.

## Lightweight checks

These checks perform no training, event-file scans, ROOT jobs or GPU work:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest -q production/tests/test_compatibility.py production/tests/test_pet_stages.py production/tests/test_projection.py
python -m ruff check production
python -m black --check --workers 1 production
python -m mypy --strict production/minerva_production
```

The first command passes 21 tests on Python 3.11, NumPy 2.4.6 and pytest 9.1.1.
Compatibility tests mutate actual dependency-file copies and exercise resume and
covariance assembly: unrelated PET/document changes remain compatible; relevant
engine, extraction, perturbation and guard changes fail. Full revisions remain
in provenance. PET tests cover guarded argv, runtime separation, full-inventory
digest binding, fixed policy and native completion handling using a stand-in
subprocess, **not** a PET backend execution. Projection tests check unequal bin
widths, source correlations, support and reordered axes independently.

The four no-fit command tests and six-entrypoint standard-library-only help check
also pass. Run subprocess checks outside a sandbox that denies the site's MUNGE
socket: its authentication error can pollute JSON stdout. Ruff, Black and strict
mypy pass. This does not certify retained production runtimes.

The full `python -m pytest -q production/tests` includes LightGBM fits and the
six-stage synthetic smoke. Run it only where compute is authorized; no allocation
is granted by this migration. Synthetic tests do not replace real-input parity.

## Continuation checklist

Work on `feat/production-interface`, starting from `972face8`; keep the shared
canonical checkout and its products untouched. The external migration goal remains
the scope; this checklist is a progress record, not authorization.

| Requirement | Current implementation / remaining verification |
|---|---|
| Real inputs | Still missing: adapter from supported scalar source with identity, selection, background and normalization; connect ROOT preparation output |
| Intended estimator | Still missing: nominal `OmniFold_helper_functions.omnifold` variant alongside the explicitly different cached engine, shared by each variant's nominal/members/closure |
| PET operations | Implemented train/infer/extract routing; actual TensorFlow/ROOT execution remains unverified and needs the named compute authority |
| Uncertainty operations | Cached statistical/split diagnostics exist; governing systematic and established combination operations still need integration, without adopting quarantined products |
| Compatibility | Implemented scoped dependencies and separate full-revision provenance; expand dependency bindings when adding adapters/estimators |
| Operational burden | PET commands now live in one operational guide; finish real-scalar commands and execution-ownership cleanup as those paths land |
| Demonstration | Real-input bounded parity remains unmet; requires data/runtime and exact existing allocation authority, never a login-node fit |

Next inspect the retained N-D collector and nominal calls in
`nd-unfolding/unfold_nd_omnifold_unbinned.py`, its callers and hash bindings, then
the actual ROOT event identity fields. The nominal uses seeds `s,s+1,s+2`; the
cached loop uses `s,s,s`. Do not substitute one for the other. Preserve receipt-bound
engines and historical evidence. No scientific result, pairing or gate has changed.
