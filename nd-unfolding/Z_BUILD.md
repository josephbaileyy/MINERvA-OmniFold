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

**THAT PRODUCER REQUIREMENT IS NOW MET, AND THE SENTENCE ABOVE IS BANNER-CORRECTED RATHER THAN
REWRITTEN so the limitation is visible as the one it was.** The prospective Z precursor
`z_precursor_20260914` (completed 2026-09-14, campaign digest `e6426e25ec06`) persists
`hCvExecution0`, `hCvExecution1` and `hCvSupportMask` with `cv_support_predicate = "x_cv > 0"`,
bound by `cv_code_revision` and `cv_producer_sha256`. `n_cv_executions = 2` and the two vectors
are **not bitwise identical**, which is what separates two executions from one result written
twice. What is still missing is the APPROVAL, not the capture: `B`, `S`, `B <= S` and an argued
`epsilon` in `[B, S]` remain unapproved, so requirement 3 below is **half discharged** and no
tolerance has been invented in its place.

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

## The assembly/spectrum pilot

Four files connect a completed precursor product to this build. None changes a construction gate,
a criterion, a tolerance or an assembly step, and no existing module was modified.

| File | What it adds | What it reuses |
| --- | --- | --- |
| `z_null_bridge.py` | ROOT → versioned-NPZ transcription of the producer's null operands | `z_build.Source`, `z_receipt.persist_null_operands`, `z_statistics.support_mask`, `z_build_path.preservation_guard` |
| `z_pilot_manifest_cli.py` | The manifest entry point, separate from the consumer | `z_pilot.build_manifest` |
| `z_pilot.py` | Digest-bound manifest, exit-code validation, spectrum persistence | `z_build.build_z` via its CLI, `z_contract.check_band_partition`, `p4_lib` donor keys |
| `sbatch_z_pilot_5d.sh` | Guarded launcher, fresh outputs, `--no-requeue`, receipt-last check | the existing env preflight/pathcheck/source-manifest/env-provenance closure |

**THE BRIDGE TRANSCRIBES AND NEVER REPAIRS.** The mask's values must be exactly `{0, 1}` *before*
any bool cast, because `np.asarray(x, bool)` maps every non-zero to `True` and a `TH1I` holding a
count would otherwise be laundered into a plausible predicate — a control measures that hazard
directly rather than only asserting the refusal. The predicate is recomputed and the producer's
must agree exactly, the four recorded counts are checked against the arrays, and the slab carries
the **producer's** code identity. `z_build` then re-stamps its own copy with the **assembling**
revision, so the two revisions stay distinct and the precursor's remains the evidence for where
the numbers came from.

**EXIT 2 IS NEITHER SUCCESS NOR FAILURE, AND IT IS NOT CONVERTED.** `z_pilot.py` requires exit 2
*and* stdout JSON reporting `CHECKED`/`NON-PASSING`/`adoptable: false` *and* both products, both
receipts and the null slab on disk, *and* each receipt's recorded product digest to match the file
beside it — matched **by path**, because a receipt carries both variants' stamps and selecting by
position would compare the cv product against the mean product's digest and pass either way. Its
own exit code stays 2: returning 0 would tell a launcher the science passed.

**THE SPECTRUM IS REPORTED, NOT CLIPPED.** `spectrum_diagnostics` records the extrema, fixed
quantiles, the negative tail's count and its magnitude relative to `lambda_max` — the same ratio
`z_assembly.gate_symmetry_psd` uses for its scale-free verdict, so a reader can apply that
criterion to this measurement. It states **no verdict of its own**; the PSD gate keeps sole
ownership. No `kappa`, null tolerance, eigenvalue floor or regularization is introduced. It is a
deliberate **second, independent** `eigvalsh` on the closed artifact rather than a harvest of the
gate's internal decomposition: threading a sink through `build_z` and `_verify_products` would
change a function every existing Z test exercises, and measuring the shipped bytes is the stronger
check. The extra decomposition per variant is the cost requirement 8 defers to a resource plan, and
it is priced in the execution request rather than absorbed silently.

**Test counts, with the interpreter.** `tests/test_z_pilot.py` reports **50 passed / 4 skipped**
under the repository default `python3`; the 4 skips are the PyROOT-gated ROOT round trip. Run
separately under ROOT 6.28/12 / Python 3.11.14 on Perlmutter, the ROOT, accessor, identity,
transcription and spectrum classes report **29 of 29 OK**. Every refusal in the transcription is
also exercised over plain arrays by `validate_transcription`, and `_named`/`_count` are exercised
through a stub store, so no refusal depends on a skipping test.

**What independent review changed (2026-09-14).** Three blockers and five should-fixes, all landed:
the launcher's last statement was an `echo`, so the job exited **0** for a NON-PASSING
construction — it now ends `exit "$PILOT_RC"`, and the test that was supposed to forbid this was a
spelling check (`"exit 0" not in text`) blind to an exit code reached by falling off the end, so it
was replaced by one that RUNS the launcher's own `case` block. `--no-requeue` and the fresh-output
refusal were asserted by string presence and both survived deletion of the mechanism; they are now
anchored on the directive and executed as a fragment. `_named` accepted any `TNamed` **subclass**
(`TH1`, `TTree`, `TGraph` all qualify), so a histogram named `cv_code_revision` could supply its
title as the producer's revision; the class is now exact. The producer's revision was held to a
weaker standard than the assembling one — non-empty string versus 40 hex characters — and the
weaker check guarded the more important field; both are 40-hex now. `OMP_NUM_THREADS` was unset:
**measured 0.480 s versus 4.248 s at n=2800** on a 244-core node, ~9× the wrong way, so the cap is
now explicit. The output-freshness check ended `2>/dev/null`, turning "cannot look" into "empty";
it now reads `ls`'s status directly, unpiped. And scope item 7 — the producer's revision must
differ from the assembling one — was asserted in three docstrings and enforced nowhere; it is now
one `contract.require`, reading the producer's revision from the **declared input slab** rather
than from `out_null`, which `z_build` re-stamps with the assembling identity by design.

## Remaining real-input and authorization requirements

These are carried under `remaining_requirements` in every receipt and command
result. They are obligations, not approvals or completed gates.

1. Bind G's exact identity, actual `combined_source` and production-CV input;
   independently establish their lineage. G's file does not supply its row index.
2. Supply Z's own corrected V/R components, five selection-complete active blocks,
   statistical block, ML block and unified-throw operands. Verify matching row
   ordering, full-grid mask, normalization, estimator and background treatment for
   every input. A same-sized matrix or a matching declared hash is insufficient.
3. **PERSISTENCE DISCHARGED 2026-09-14; APPROVAL OUTSTANDING.** Capture both same-run internal
   fixed-seed CV vectors and the predicate in the throw producer — done by
   `z_precursor_20260914`, product sha256 `09a029ed…`, and transcribed into the reader's schema by
   `z_null_bridge.py`. Their seed/run provenance is bound (`cv_code_revision`,
   `cv_producer_file`, `cv_producer_sha256`); copying an external CV into either slot is still not
   a substitute, and the bridge refuses a mask that disagrees with `x_cv > 0` recomputed from the
   persisted CV rather than correcting it. **STILL REQUIRED:** approve the null construction `B`,
   `S`, `B <= S` and an argued `epsilon` in `[B, S]` before production. The measured agreement
   (relative L2 4.452e-14 over the support) is RECORDED for that approver and is NOT a verdict.
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
