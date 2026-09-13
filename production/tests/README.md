# Migration verification

Operational commands belong in [the production guide](../README.md). Tests prove
software behavior, not estimator equivalence on real inputs, coverage or adoption.
Historical verification at the initial interface is preserved in Git at
`972face8:production/tests/README.md`.

## Lightweight checks

These checks perform no training, event-file scans, ROOT jobs or GPU work:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest -q production/tests/test_compatibility.py production/tests/test_pet_stages.py production/tests/test_projection.py production/tests/test_nominal_backend.py production/tests/test_root_input.py production/tests/test_systematics.py production/tests/test_uncertainty_run.py
python -m ruff check production
python -m black --check --workers 1 production
python -m mypy --strict production/minerva_production
```

The six-file checkpoint passed 46 tests on Python 3.11, NumPy 2.4.6 and pytest
9.1.1. The final run-stage additions pass another 14 no-fit cases: nine systematic
cases and five scalar statistical/ML cases. Unchanged checks are not rerun merely
for documentation edits.
Compatibility tests mutate actual dependency-file copies and exercise resume and
covariance assembly: unrelated PET/document changes remain compatible; relevant
engine, extraction, perturbation and guard changes fail. Full revisions remain
in provenance. PET tests cover guarded argv, runtime separation, full-inventory
digest binding, fixed policy and native completion handling using a stand-in
subprocess, **not** a PET backend execution. Projection tests check unequal bin
widths, source correlations, support and reordered axes independently.

The seven no-fit command tests and six-entrypoint standard-library-only help check
also pass at the implementation checkpoint. The final guide's 16 workflow
commands additionally pass `--plan` with their checked-in example configurations;
these plans read no event arrays and create no products. Run subprocess checks
outside a sandbox that denies the site's MUNGE
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
The same fixture also passes native vertical truth/reco/denominator/background
branch swaps, same-index Flux table normalization and active-universe ordinary-tree
routing. Systematic unit tests reject missing or mismatched migration metadata,
dump-all lateral substitutions, incomplete inventories and nominal pairing drift.
They compare MAT `1/N` covariance, its common shift and the CV-centered second
moment; neither numerical variant is an adopted product. Member assembly/resume
binds its nominal, declared inventory and calculation dependencies. These checks
do not yet exercise end-to-end systematic training or a real migration census.
Run-stage tests exercise cache IO, nominal-to-member-to-assembly wiring for both
scalar engines, both statistical modes and the cached split policy. Systematic
run tests cover lateral, vertical and Flux routing, preservation of nominal
support, changed-input resume refusal, and cache removal on success, source
mismatch or fit failure. Their preparation/training stand-ins never read ROOT
events or fit models; they supplement the native fixtures, not replace them.
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
| Uncertainty operations | Statistical/split and native systematic single-band operations implemented, including background/flux variations and active selections; native tiny ROOT and no-fit assembly tests pass; full training and scientific integration remain unverified; totals stay blocked |
| Compatibility | Scoped dependency hashes bind the selected engine only; full revision is separate provenance, including ROOT preparation |
| Operational burden | Guide contains scalar, statistical, split, systematic and PET commands, environments, old/new mapping and retained ownership; historical guide remains in Git |
| Demonstration | Real-input bounded parity remains unmet; requires data/runtime and exact existing allocation authority, never a login-node fit |

All seven requirements have software implementations or, for integration evidence,
the explicit external checks below. No required adapter or operation is left as
a software plan. Frozen 2D, signed/refined targets and receipt-bound launchers
retain their original execution routes. The single-band boundary does not expose
quarantined block sums, unified throws or PET covariance. No scientific result,
pairing or gate has changed, and production replacement is not verified.

## Remaining external integration checks

The migration instruction grants no allocation or training campaign. No real
production event file was scanned and no fit was run during this continuation.
Existing authorization for a named research campaign cannot be borrowed for
migration parity. These checks remain **unmet**, including real-input preparation:

1. Supply an immutable, bounded native ROOT inventory with signal, data,
   background, truth denominator and the independent baseline flux, plus exact
   authorization for its preparation and CPU fits. Define any subsampling before
   running it, including denominator/support treatment; do not truncate unrelated
   trees independently or invent missing identities. Run the guide's adapter in
   the ROOT environment. Compare native collectors against prepared arrays for
   entry IDs, row order, masks, truth/reco pairing, features, weights, purity,
   denominator, flux, POT, nucleons and reported support. The existing native
   fixture check uses exact equality for transported collector arrays.
2. On those same inputs, execute the guide's nominal, seeds 7/8/9, covariance,
   projection and closure sequence. Compare the original nominal engine with
   `nominal-lgbm-v1`, and the cached engine with `cached-lgbm-v1`, separately.
   Hold training settings, runtime, thread count, masks and draw order fixed.
   Compare pull/push weights before cross sections, then unfolded yields,
   completeness, cross sections, common shifts and full covariance. Use
   `rtol=1e-12, atol=0` for deterministic same-runtime calculations (as in
   `test_scalar.py`), exact equality for identities/masks/support, and investigate
   failures without widening tolerances after seeing them. Verify projections
   independently with native bin-width factors and `P C P.T`. A comparison of
   cached replicas against the distinct nominal engine cannot establish parity.
3. With a separately authorized complete native band, execute systematic
   `run`/`combine` and compare varied signal/background/denominator weights,
   lateral migration census, Flux universe index/normalization, both covariance
   centerings and common shift against retained calculations. A weight-only
   lateral cache cannot satisfy this check. No total covariance is authorized.
4. PET wiring is covered by stand-in processes only. Actual train/infer/extract
   requires its own named authority, certified target and full inventory in the
   separate TensorFlow/ROOT runtimes. Verify the native checkpoints, completion
   products and inference contract; preserve diagnostic status and all gates.

Retain commands, input/code digests, resolved settings, intermediate comparisons,
tolerances and terminal outcomes with any future integration evidence. A passing
software chain would still establish neither coverage nor scientific adoption.
