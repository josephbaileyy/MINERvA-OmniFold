# Local Z build integration

`z_build.py` reads declared local operands, builds both centering variants,
checks the closed artifacts, and writes one receipt per variant last. A successful
construction has `construction_status: CHECKED`, `scientific_acceptance:
NON-PASSING`, and `adoptable: false`. Its command exits **2**, even when every
construction check succeeds. A malformed input or failed construction exits **1**.

**Exit 2 means the build RAN TO COMPLETION with non-passing science — it is not a success
code and it is not, on its own, proof that the artifacts exist.** A caller must additionally
require the stdout JSON to parse with `construction_status: "CHECKED"`, or require both
receipts and the null slab on disk and verify the product hashes recorded in them.

Reviewer finding F2 was that this code used to be ambiguous: `argparse` exits **2** on a usage
error, so a single mistyped flag — or no arguments at all — produced exit 2 having written
nothing, and was indistinguishable by exit code from a finished non-passing build. Usage errors
now exit **1** with the same `{"construction_status": "FAILED"}` stderr envelope a refused build
emits, so 2 is unambiguous. `--help` exits 0 and writes nothing. An uncaught
non-`ZContractError` still exits 1, but through the interpreter's traceback rather than the
envelope, so stderr-JSON parsing is not total.

**Test counts depend on the interpreter and the difference is not cosmetic.** Under an
interpreter with PyROOT the suite reports 275 run / 274 passed / 1 skipped (LightGBM). Under the
repository's default `python3` it reports 275 run / 272 passed / 3 skipped, because the two ROOT
tests skip as `PyROOT unavailable`. Quote the interpreter with the count. This mattered
concretely: the assertion that catches a forged product label used to live only in a
PyROOT-gated test, so the default interpreter could not see it — that is F1, and the assertion
now also runs in the always-executing test.
There is no threshold override, seed default, production launcher or adoption path.

## Reconciliation with the existing implementation

Integration base: `5580d1d5b68b87d8e7e24a8ac041a39e0d7ed226`. The governing
construction is [the Z specification](../docs/orchestration/SPEC-20260906-complete-scalar5d-successor-Z.md),
especially sections 1.3a, 1.3b, 1.5 and 3.3. Its historical gate inventory describes
its original base, not the implementation present at the integration base.

| Existing implementation | Existing responsibility | New connection |
| --- | --- | --- |
| `z_contract.check_band_partition` | Imported V/A membership; disjoint, exhaustive V/R/A partition | Inventory comes from actual support-file keys; R is derived from that inventory |
| `z_assembly.derive_variant_diagonals`, `compute_g`, `assemble` | Clipping, shift, inflation and assembly algebra | Declared throw diagonals and shift feed both variants; separate V/R/A/stat/ML sums feed assembly |
| `z_assembly.run_inflation_gates` | Per-variant construction gates | Runs on constructed arrays and again on each closed output |
| `z_assembly.run_pair_gates` | Raw-operand reconstruction across both variants | Runs before output and again against both recorded inflation vectors |
| `p4_lib.check_component_sum` | Five active-band total identity | Checks the active file's recorded total against its five read components |
| `z_receipt.load_null_operands`, `persist_null_operands` | Versioned operand schema and construction metadata | Reads the declared source slab, persists a bound copy, and reads that copy back |
| `z_statistics.reconstruct_null_ratio` | Predicate reconstruction and null ratio | Reconstructs the ratio from the source and output slabs; no external denominator substitution |
| `z_validator.assess_null` | Null assessment with withheld-boundary refusal | Records the measured ratio and the explicitly non-passing assessment |
| `z_receipt.build_receipt`, `write_receipt` | Receipt construction and serialization | Records measured construction checks, input/output stamps, both product identities and unresolved requirements |

The five Z construction gates, raw-operand reconstruction, null schema, statistics
and boundary registry already existed. None was recreated or changed. Cause-3
`LegSet`/`assess`, sensitivity statistics and `z_reproducibility` also exist, but a
single covariance build supplies neither the declared seed population nor the
approved outcome criteria needed to use them as a campaign assessment. Their
absence is represented by unresolved requirements, never a singleton synthetic
population silently treated as a scientific control.

## Input manifest, version 1

The JSON object must have exactly these fields. Unknown fields, duplicate JSON
keys, unsupported versions, non-finite JSON constants and missing fields fail.

| Field | Required value |
| --- | --- |
| `schema_version` | Integer `1` |
| `input_kind` | `synthetic` or `real`; both remain non-adoptable |
| `run` | Object with nonblank `id` and `step` |
| `producing_revision` | Full commit SHA equal to the executing isolated checkout's HEAD |
| `sources` | Exactly the eight roles in the table below |
| `stat_key`, `ml_key` | Exact covariance keys in the respective source files |
| `footing` | `mask_sha256` and `row_order_sha256`, using `z_receipt.sha256_array` on the full-grid boolean mask and int64 C-order reported row indices |

Every source is `{ "path": "...", "format": "npz", "sha256": "..." }`.
Paths are explicit; relative inputs resolve against the manifest directory.
SHA-256 values must be full lowercase hex digests. Numeric sources accept `npz`
or `root`; the parent may also be `opaque`. The null source must be `npz` and
satisfy the existing versioned null-operand schema.

| Source role | Objects read |
| --- | --- |
| `parent` | File identity only; parent scientific lineage remains `UNVERIFIED` |
| `central` | Full-grid `hXSecND_flat` |
| `support` | Actual `hCov_universe5d_<band>` key inventory, excluding `hCov_universe5d_total`; matrices for V and R only |
| `active` | `p4_lib.candidate_band_key(band)` for every imported active band and `p4_lib.CANDIDATE_ACTIVE_TOTAL_KEY` |
| `stat` | Matrix named by `stat_key` |
| `ml` | Matrix named by `ml_key` |
| `throw` | Diagonals of `C_unified` and `C_blocksum`, plus `hJointMeanShift` |
| `null` | Full-grid `x_cv`, `x_cv2`, predicate and validated schema/declaration |

All covariance matrices span the same reported rows. The reader rejects wrong
shapes, nonnumeric arrays, complex arrays and non-finite entries. ROOT matrices
are TH2D; throw diagonals are read without materializing the full ROOT matrices.
NPZ arrays are loaded into memory, without claiming memory mapping. Sources are
stamped before reads and rechecked for content/replacement drift before receipts.
An input hash establishes bytes, not the scientific validity of its declaration.

`central` fixes the output CV. Its positive-support mask and C-order row indices
must match the declared digests. The persisted null predicate is reconstructed
independently and must match that support. The receipt labels the output row route
as reconstructed from the declared production CV, **NOT `read_from_G`**. It does
not infer G's missing producer-input binding. An exact comparison of the internal
null CV with the external central vector is reported as `ELEMENTWISE_EQUAL` only
when every element agrees; otherwise it is `UNRESOLVED`. Neither result supplies
the missing parent lineage or approves a null tolerance.

The integration copies an already versioned null slab; it cannot recover the
second internal CV from a historical throw file that never persisted it. The
copy's writer identity names this integration, while its source stamp binds the
original slab. Capturing the internal vectors in a future real throw run remains
a producer requirement, not a claim that this local copy ran an estimator.

## Output and provenance contract

Both `--out-cv` and `--out-mean` are required, distinct new `.npz` or `.root`
paths. `--receipt-cv`, `--receipt-mean` and `--out-null` are also required and
distinct. Existing files and resolved input/output aliases are refused. Each
destination is reserved exclusively; on a caught failure, only files reserved by
this invocation are removed. A hard process termination can leave incomplete
files; consumers must require both receipts and verify their product hashes.

Each covariance artifact contains `hCov_combined5d_total_uthrow`, `hInflation_g`,
`hPinnedMask`, `hXSecND_flat`, `hSupportMask`, `hRowIndex5D` and `metadata_json`.
Metadata binds schema, variant, input class, run/step, manifest digest, code and
non-adoptability. The output slab uses the existing null schema unchanged.

The receipt records per-object input digests, actual partition membership,
raw-operand digests, inflation summaries and reconstruction discrimination,
before/after square-root traces, closed-file closure/PSD checks, reconstructed
null norms/ratio and the per-bin diagnostic with its grid argmax. Both product
stamps are carried in each receipt. All seven causes remain `UNRESOLVED`; the
scientific outcome has no passing branch, and the unchanged boundary registry
is serialized by the existing receipt builder.

Code identity measures repository Python files loaded in the executing process,
including the driver, and records their SHA-256 values. It also records files
whose bytes differ from the named revision. A revision plus dirty file digests
does not become committed provenance; this is visible in
`worktree_files_differing_from_revision`. The real-input release still needs a
committed producing checkout and independent environment/import verification.

## Reproduce the synthetic path

The fixture writer creates an explicitly synthetic family. Its small grid,
invented residual labels and artificial covariance values are test data only.
Choose a new scratch directory for each run.

Create the synthetic inputs from the repository root:

```sh
python3 nd-unfolding/tests/test_z_build.py --write-fixture /tmp/z-build-example
```

Build and check both variants, then write their receipts:

```sh
python3 nd-unfolding/z_build.py \
  --manifest /tmp/z-build-example/manifest.json \
  --out-cv /tmp/z-build-example/result-cv.npz \
  --out-mean /tmp/z-build-example/result-mean.npz \
  --receipt-cv /tmp/z-build-example/receipt-cv.json \
  --receipt-mean /tmp/z-build-example/receipt-mean.json \
  --out-null /tmp/z-build-example/result-null.npz
```

Expected command status: **2**, with `CHECKED` construction and `NON-PASSING`
scientific acceptance. Reusing these outputs is refused instead of overwriting.

Run the existing Z suite and integration controls:

```sh
python3 -m unittest discover -s nd-unfolding/tests -p 'test_z_*.py'
```

Controls cover distinct variants, the physical covariance scale, legitimate
zero-shift equality and pinned bins. Mutations cover an improperly uninflated
closed object, dropped shift, an added unified budget, inflated residual terms,
indefiniteness at physical scale, reordered rows, malformed operands, unsupported
null schemas, missing bands, mismatched active totals, digest drift, changed
inputs, output aliases and failures during receipt writing. PyROOT controls also
exercise actual ROOT inputs and outputs and asymmetric matrix orientation; they
skip explicitly when PyROOT is unavailable. A green construction test does not
verify real-input scientific provenance.

## Remaining real-input and authorization requirements

These are carried under `remaining_requirements` in every receipt and command
result. They are obligations, not approvals or completed gates.

1. Bind G's exact identity, actual `combined_source` and production-CV input;
   independently establish their lineage. G's file does not supply its row index.
2. Supply Z's own corrected V/R components, five selection-complete active blocks,
   statistical block, ML block and unified-throw operands. Verify matching row
   ordering, full-grid mask, normalization, estimator and background treatment for
   every input. A same-sized matrix or a matching declared hash is insufficient.
3. Capture both same-run internal fixed-seed CV vectors and the predicate in the
   throw producer. Verify their seed/run provenance; copying an external CV into
   either slot is not a substitute. Approve the null construction `B`, `S`,
   `B <= S` and an argued `epsilon` in `[B, S]` before production.
4. Supply cause 1's scoped interpolation counterfactual and disclosure, cause 2's
   F7 operands and `k` provenance, and cause 4's jitter add-back value, seed and
   both operand identities.
5. Predeclare the finite cause-3 offset population `K`, both-leg estimator and
   draw seeds, binding leg set, movement/coverage requirements and permitted
   correlation-sensitive use. Obtain approved criteria and supply every complete
   member. The projection-sensitivity proposal remains unadopted.
6. Independently trace the whole input/code path for cause 5 and apply its
   artifact-specific ruling. Supply cause 6's projection operator and both
   coverage censuses. Supply cause 7's five support keys, ten endpoints,
   migration censuses, declared policies, support-scope check and counterfactual.
7. Review the committed ROOT inspection's endpoint `globalCompleteness` readings
   above one; do not normalize or silently classify them. The route is
   `docs/orchestration/state/pm-root-inspection-20260909c-report-58127048.json`.
8. Commit and pin the complete producing code, verify executable imports and the
   real environment, and repeat ROOT read/write controls in that environment.
   Synthetic ROOT and NPZ controls do not establish real-input compatibility or
   production-scale memory/runtime feasibility. Dense component sums, both variants and exact
   eigenvalue checks require a separately assessed resource plan.
9. Obtain the named production/resource authorization, independent construction
   verification and scientific decisions. This integration grants no cluster
   production, covariance adoption, lower-dimensional projection or publication
   authorization, and changes no publication source or historical result.
