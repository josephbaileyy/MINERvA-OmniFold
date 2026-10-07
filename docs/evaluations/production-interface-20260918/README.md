# Production interface evaluation — 2026-09-18

**Recommendation: adopt selectively for scalar software development; defer
production replacement.** The branch offers a useful explicit interface and
regression harness around retained calculations. It does not supply the missing
scalar-5D covariance construction, production parity, coverage or acceptance
criteria. Reject a wholesale workflow migration as a prerequisite for finishing
the scalar-5D work. This is a software recommendation, not scientific adoption
or execution authority.

## Scope and source identity

| Item | Evaluated identity |
| --- | --- |
| Current `main` | `ce72abbcf84793a5dc56b7c166aa9a9322266355` |
| Remote `feat/production-interface` | `7a2d9897a42c39d0413eef938cb90b6cae7239c0` |
| Common ancestor | `77a4af38c259f51ed2ad044d8c3fc8e1f40e2c3c` |
| Local feature checkout, not the evaluated tip | `972face8` — four commits behind the remote |

Both remote heads were checked directly with `git ls-remote` before and after the
evaluation. There are 18 main-only and six feature-only commits. The feature's
three-dot diff adds **46 files / 5,076 lines, entirely under `production/`**.
It changes no retained engine. Main has newer Z precursor and interrupted-output
repairs absent from the feature snapshot; those are main-side evolution, not
deletions proposed by this additive branch. Deploying the old feature checkout
as a replacement for main would nevertheless omit them.

Read at the feature revision: `production/README.md`, `production/AGENTS.md`,
`production/tests/README.md`, the nine test modules, the native ROOT fixture
checker, examples, entry points and implementation modules. Compared retained
callers including `bootstrap_nd.py`, `combine_cov_nd.py`, `project_cov_nd.py`,
the nominal and cached engines, N-D collectors and extraction, and checkout
guard. The tested cached engine, bootstrap driver, nominal engine, extraction,
projection, covariance math and guard are byte-identical between these two tips
(`git diff --quiet` on those seven paths).

Read on main: `docs/CURRENT_WORK.md`, relevant workstream/reference and known-issue
routes, the OI-173 and OI-187 records, the Z specification, `Z_BUILD.md` and
`Z_CONSTRUCTION_PLAN.md`. The current pilot route was followed to the actual
`c4baf0d2` decision-support record, especially §19, rather than treating an older
plan as current execution state. The older specification's statement that Z does
not exist is not the current outcome.

Three separate worktrees contained: the unchanged feature tip; main plus an
untracked, byte-for-byte export of only `production/`; and main for baseline
checks and this report. No audited tracked source changed. The integration
worktree's only untracked addition was that export. All test data were synthetic
and disposable. No event inventory, scheduler, queued job, production namespace,
scientific receipt, note source or hash binding was changed.

## What is worth adopting

| Capability | Concrete development benefit | Boundary |
| --- | --- | --- |
| Common config/input/output/plan commands | One documented route for preparation, nominal, members, assembly, closure and projection; all 16 documented workflow plans parse locally. | A plan can succeed with missing prerequisites; it is not execution readiness. C++ preparation remains a command plan. |
| Shared `scalar.calculate` | Nominal, replicas and closure use the selected retained engine and extraction, reducing the chance that a wrapper silently changes one arm. | Cached and nominal are explicitly different estimators: seed policies `s,s,s` and `s,s+1,s+2`. Actual nominal fits require ROOT. |
| Input/output contracts | IDs, row pairing, feature order, units, masks, support and normalization become checked data instead of assumptions distributed among scripts. | Existing anonymous caches and ROOT outputs cannot be relabelled as compliant inputs. Source-file/tree/entry identity is not cross-merge event identity. |
| Matched-family execution | Explicit statistical mode and member inventory; fixed estimator with independent data/paired-MC draws; split members require a matching split nominal. | `data-plus-mc` fixes denominator and background. It does not implement a new three-stream or coverage construction. |
| Completion and resume | Payload hashes and calculation-scoped dependency hashes reject incomplete, tampered or mismatched products; unrelated docs/PET edits do not invalidate scalar resume. | These checks establish compatibility of recorded bytes and settings, not scientific validity or a complete production runtime fingerprint. |
| Projection contracts and tests | Width-weighted `P x` and `P C P.T`, cross-bin correlations, axis ordering and partial-support semantics have explicit tests. | Output support is inferred from source fibers; the retained driver's explicit `--dst-cv` alignment is not exposed. Normalized shapes are refused. |
| Systematic/PET adapters | Single-band systematics preserve native preparation and both centerings; PET keeps runtime separation and full-inventory binding. | Useful later, but not needed for the smallest scalar development migration. Tests mostly use stand-ins; actual chains remain unverified. |

The architectural benefit is concentrated at the command and contract boundaries.
There is no new unfolding algorithm and no measured training acceleration.
The example's three cached-member launches plus assembly become two invocations,
but the fits still occur and this is not a production job-count reduction. A
second persistent cache/product protocol and its adapters add maintenance cost;
that cost is justified only for paths actually exercised by new development.

## Bounded local checks

Python **3.11.15**, NumPy **2.4.6**, LightGBM **4.7.0**, scikit-learn **1.9.1**,
SciPy **1.17.1**, pytest **9.1.1**; local macOS runtime, no PyROOT or TensorFlow.
Successful full-suite runs used `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`,
`LOKY_MAX_CPU_COUNT=1`, and unset `GIT_SSH_COMMAND` for local subprocesses.
The production guard remained installed. The environment was a fresh temporary
venv, not a modified production environment.

| Check | Measured result | What it proves |
| --- | --- | --- |
| Feature's seven documented no-fit test files | **60 passed**, 2.96 s | Contract checks, mocked dispatch/member wiring, protocol fixtures and small-array math. |
| Complete feature suite | **82 passed, 1 skipped**, 13.75 s | Also real cached-LightGBM synthetic equivalence, six-stage smoke, resume, guarded commands and standard-library-only help. |
| Same suite on main plus exported `production/` | **82 passed, 1 skipped**, 14.93 s | The additive directory works against the evaluated main for this bounded scope. This is not a merge or production integration test. |
| Guide commands with `--plan` | **16/16**, exit 0 / `plan-only` | Configurations and planning dispatch are runnable; no arrays or products are needed. |
| Feature Ruff / Black / strict mypy | **Pass / 26 files unchanged / 11 source files pass** | Local static checks, not retained-runtime certification. |
| Native ROOT fixture command | **Unavailable**, `ModuleNotFoundError: No module named 'ROOT'` | Its documented earlier ROOT success was read but not independently rerun here. |
| Main Z contract/assembly/build-path/validator/build tests | **362 passed, 2 skipped, 1 failed; 85 subtests passed**, 28.00 s | Existing baseline coverage and one local portability failure, described below. |

The skipped interface case is ROOT extraction; the two skipped Z cases also
require PyROOT. The full interface suite's nominal-backend tests substitute a
no-fit engine. Its actual cached equivalence fixture has **800 synthetic rows
and two features**, not a real five-dimensional nominal chain. PET tests use
stand-in subprocesses, and systematic run tests substitute preparation/training.
No green count upgrades these evidence classes.

The first full-suite attempt returned **78 passed, 1 skipped, 1 failed and 3
errors** in 42.33 s. The inherited `GIT_SSH_COMMAND` triggered the guard at the
read-only provenance call `git rev-parse HEAD`, with:

```text
[oi136 launch]   offending flag $GIT_SSH_COMMAND makes git run a program of the caller's choosing
```

Removing that unused SSH override from local child environments and explicitly
capping local CPU discovery allowed the unmodified suite to pass. No guard
exception or source patch was used. Keep this environment requirement visible
in a future local-development recipe.

The Z failure is
`test_z_assembly.py::EachGateFiresOnItsOwnDefect::test_a_SINGULAR_psd_matrix_is_accepted_though_cholesky_would_refuse_it`:
`AssertionError: LinAlgError not raised`. The fixture is `A @ A.T` with
`A.shape == (6, 5)`; its eigenvalue check and the actual PSD gate pass, but this
NumPy/runtime's Cholesky does not raise on the rounded singular matrix. The same
single failure reproduces on main plus the feature directory. It is a baseline
test portability issue, not evidence that the interface changes Z or that the
PSD gate fails. No test or production code was repaired by this audit.

## Comparable local performance

[benchmark.py](benchmark.py) executes main's guarded `bootstrap_nd.py` and the
feature's guarded statistical-member entry point on identical cached arrays.
The fixture has **800 MC rows, 773 selected measured rows, two features, two
iterations, 100 trees/eight leaves, estimator seed 42 and bootstrap seed 7**.
Both use the retained cached engine, the same data/MC draw order, fixed
denominator and normalization, and one CPU cap. Nominal setup is outside timing.
Each run writes a fresh output; one warm-up pair is discarded, then five pairs
alternate order. Each subprocess has a 60-second limit. Timings include process
startup, fitting, extraction, IO, guard and provenance work.

| Entry point | Median wall time | Five-sample range | One member's output bytes |
| --- | --- | --- | --- |
| Retained cached-bootstrap driver | **1.039 s** | 1.019–1.213 s | 1,440 |
| Interface statistical member | **1.271 s** | 1.250–1.307 s | 19,473 |

The interface is **0.232 s / 22.3% slower** on this tiny workload. Its output also
contains pull/push factors, identities, intermediate spectra and a JSON record;
the retained output is compact. The comparison matches the calculation, not the
amount of output or validation. Six of six paired cross-section comparisons
(including warm-up) are **elementwise identical**; integrals pass the preset
`rtol=1e-12, atol=0`. This does not compare the distinct original nominal engine.

The committed [samples and array digests](benchmark-results.json) are from a
serial run after other audit tests completed. An exploratory run overlapping the
Z tests was excluded from the headline timing. No uncertainty on the timing
ratio is inferred from five samples, and no production speedup, CPU-hour saving,
peak-memory result, ROOT scan rate or GPU performance is claimed.

At larger scale, `load_inputs` and `load_result` materialize NPZ arrays, and
member records retain event-sized factors. Covariance/projection arrays are
dense. Memory, compression, repeated source hashing and output storage need
measurement before scheduling production; `mmap_mode` would not make NPZ members
memory-mapped (KNOWN_ISSUES #58). This audit did not measure those costs.

## Fit to the planned scalar-5D work

The intended uncertainty work is still retained before publication by the OI-187
ruling, even though it upgrades the paper's claims rather than structurally
gating submission. An interface cleanup must not silently replace that work.

Main already has the Z construction stack. `Z_BUILD.md` specifies an eight-role
manifest, central/support and row-order bindings, V/R/A band partition,
statistical/ML blocks, unified-throw operands, both centering variants, inflation
checks, persisted null operands and receipts that remain non-adoptable.
The interface exposes **one statistical/ML family or one systematic band** and
does not implement this construction or its acceptance path.

| Scalar-5D need | Interface assessment |
| --- | --- |
| Retain validated central estimator and frozen evidence | Explicit nominal dispatch helps future tests, but no real-input nominal parity was established; cached parity cannot replace it. |
| Selection-complete lateral and native vertical/Flux components | Adapter code and small protocol checks exist. Real migration census, full normalization and trained single-band parity are missing. |
| Z total, V/R/A assembly, inflation and same-run null operands | Absent from the interface. Keep `z_build.py`, precursor modules and receipt-bound execution as owners. Generic mean-centering or adding component covariances is not a substitute. |
| Estimator repeatability/seed-role and acceptance criteria | Config rejects arbitrary model changes and does not expose the proposed deterministic/thread envelope. Package versions and `n_jobs=None` do not bind effective threads, native build or runtime environment. |
| Existing Z source/product compatibility | No direct importer/exporter: interface `result.npz`/schema-2 record and supported `xsec` differ from Z's named full-grid and covariance objects plus null/receipt contract. Renaming keys cannot supply missing provenance. |
| Publication projections | Linear algebra tests are useful. Exact adopted support, destination-CV alignment, target map and inference obligations still need their existing scientific route. |

The latest routed end-state is the pilot lane's decision-support §19 at
`c4baf0d29297de0d0f50d5ea1d8b869ddaf83520`. Its open question concerns transfer
of a pre-dating tolerance under SPEC §3.6a item 3 for already-produced products.
This audit makes no ruling on that question. It does not reopen the completed
precursor or pilot, infer adoption from their construction, or make a new wrapper
the remedy for a criteria gap. See main's
`docs/orchestration/NAVIGATION-20260917-z-pilot-outcome-route.md` for exact source
identities, then read the cited source rather than quoting the route as evidence.

## Smallest useful migration and remaining release evidence

Recommend one follow-up change limited to an **opt-in cached-scalar development
workflow**, based on current main. Extract the shared config/input validation,
storage/resume contract, synthetic fixture, cached calculation dispatch,
statistical member assembly, closure and projection with their applicable tests
and one short recipe. Keep the matching nominal/member rule. The concrete source
slice is `scalar.py`, `storage.py`, `uncertainty.py`, `projection.py`, the synthetic
part of `preparation.py`, the corresponding five scalar command entry points and
their CLI branches. Make the cached backend explicit in that recipe. Do not
cherry-pick an early commit merely because it is smaller; later parity and
compatibility fixes must travel with their consumers.

The first slice should omit ROOT preparation, systematic execution and PET
dispatch rather than landing unused adapters as a production promise. It needs
no retained-engine rewrite, input conversion campaign, launcher modification,
new default command, archived-product restamping or downstream consumer change.
Its acceptance test is the existing cached synthetic chain plus the current-main
comparison above; deletion of the opt-in directory is sufficient rollback.
This is the recommended scope of a future implementation, not an extraction
already performed by this evaluation.

**Defer production migration** until these distinct checks have evidence:

1. A named immutable real ROOT inventory in the retained ROOT/MAT environment:
   exact selected IDs/order/masks/truth-reco pairing and comparisons of native
   features, weights, purity, denominator, flux, POT, nucleons and support. Fix
   bounded sampling and tolerances before execution; do not independently trim
   trees and then claim equivalence.
2. Matched actual nominal and cached chains, separately: pull/push factors first,
   then yields/completeness/cross sections, bootstrap members, shifts, full
   covariance, closure and independent projections. Synthetic cached success and
   mocked nominal calls cannot supply this check.
3. A complete real single-band family, including native lateral entrants/exits
   and misses, vertical background/denominator variation and same-index Flux
   normalization; verify both covariance centerings against retained math.
4. Production runtime/import identity, effective thread policy and native library
   builds; interrupted-output/restart behavior at representative size; measured
   time, memory and storage. Preserve existing guard and receipt bindings.
5. Any eventual Z integration must preserve its manifest, mask/order/parent and
   seed-role contracts, null operands, independent verification and scientific
   acceptance. A software interface release does not authorize adoption.
6. PET remains a separate diagnostic path: actual TensorFlow training/inference
   and ROOT extraction with certified inputs remain unverified here. OI-126's
   declined pairing and the exact Gate-6 receipt restrictions are unchanged.

The feature's `production/tests/README.md` gives the detailed future parity
procedure. Those checks require the existing named authority and runtime/data;
this evaluation provides no production allocation. Current evidence supports a
small development aid and continued use of the retained scalar-5D construction.

## Reproduction

Use clean worktrees at the two full revisions above and a temporary Python 3.11
venv. Install the feature's `production/requirements.txt` and the audit's static
tools. For exact dependency versions and commands see [checks.txt](checks.txt)
and [benchmark-results.json](benchmark-results.json). The feature requirements
have lower bounds, so an unconstrained future installation may differ.

For the integration check, export only `production/` from the feature revision
into a disposable main checkout; do not merge it or edit either source tree.
From each tested root run:

```sh
env -u GIT_SSH_COMMAND OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 LOKY_MAX_CPU_COUNT=1 \
  "$AUDIT_PYTHON" -m pytest -q -rs production/tests
```

Run the benchmark after other local audit checks have finished, with a fresh
output directory (the script and result live beside this report):

```sh
env -u GIT_SSH_COMMAND OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 LOKY_MAX_CPU_COUNT=1 \
  "$AUDIT_PYTHON" docs/evaluations/production-interface-20260918/benchmark.py \
  --main "$MAIN_CHECKOUT" --feature "$FEATURE_CHECKOUT" --output "$NEW_SCRATCH"
```

No performance threshold or scientific criterion is introduced by these commands.
