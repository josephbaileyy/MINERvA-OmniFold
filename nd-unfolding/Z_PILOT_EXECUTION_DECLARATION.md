# Z assembly/spectrum pilot — execution declaration

**CITABLE FOR:** the eight declared source roles and their measured digests; the enforced resource
limits; the provenance and scientific qualifications that travel with this execution.

**NOT CITABLE FOR:** any scientific result, any covariance adoption, any significance, any
projection, or any statement that the historical 2026-08-08 standard-P4 run was authorized. This
execution is **NON-ADOPTABLE by construction** and its scientific acceptance is **NON-PASSING**
whatever it returns.

Authorized by Joseph 2026-09-15: one execution of `sbatch_z_pilot_5d.sh`, one CPU task, 1:30 wall,
64G, four CPUs, `OMP_NUM_THREADS=4`, maximum admitted exposure **1.5 CPU task-hours** (R5's unit:
wall-hours per execution attempt), **no GPU allocation**.

## The eight source roles, bound by measured digest

Every digest below was recomputed from the file on disk with `sha256sum`, not copied from a
manifest or a receipt. Sizes are `stat -c %s`.

| role | artifact | bytes | sha256 |
|---|---|--:|---|
| `parent` (**G**) | `uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root` | 892,170,881 | `4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2` |
| `central` | `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | 479,553 | `630306e20e4e175bde8b459174842a58e4f4b5a694b8a5018e730a952820aec8` |
| `support` (**CS**) | `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` | 41,436,632,945 | `9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a` |
| `active` (**S**) | `active_universe_5d/standard/candidate/std_final5_candidate.root` | 42,326,607,877 | `950f8cb15c5a0bd785d65e7f85f4cb40fa86e27383973f82ef15c7ef525c1263` |
| `stat` | `uq_cov_stat_5d.root:hCov_stat5d_reported` | 891,732,011 | `6580016fa7136e6f98867707f4d48557350b26a91773d0c300be20113c2c6934` |
| `ml` | `uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported` | 892,078,834 | `27b2e456f80e15d8a5c4da1bcd3b01a201b80385341af68614c85b6b7f8f5374` |
| `throw` | `uq_5d/z_precursor_20260914/unified_throw_cov_5d.root` | 2,668,265,910 | `09a029ed2a7de0ffd144b1ad0ad8d3e0bf8e8b9788797b0af58693c753795560` |
| `null` | produced at run time by `z_null_bridge.py` **from `throw`** | — | digest recorded in the run's `bridge.json` and in the manifest |

`footing` is **derived from `central`, not declared** — `z_build` recomputes it and compares, so a
pasted value could only ever disagree:

```
footing.mask_sha256      = eed021e93fd7ccc17330b3fcddbb326e3c0f2186309aed3a70c2ba31cae750e2
footing.row_order_sha256 = 61a7c9fd70d7c7718d396afa5c92b6b1bb0b94e7280245d35c9f8c4117f8b461
```

⚠ **DO NOT PASTE THE INSPECTION REPORT'S DIGESTS.** `pm-root-inspection-20260909c-report-58127048.json`
hashes `sha256(idx.tobytes()+b"|C")` over the int64 **index array**; `z_build` wants
`z_receipt.sha256_array` over the 65,856-entry **boolean**, which folds `dtype.str` and `shape` in
first. Different algorithm, different operand, and using them raises `central: mask_sha256 mismatch`.

### The support donor is the corrected background-aware one, and the other is refused by name

`p4_build_components.py:28` lists `"universe_stage2_5d/uq_universe_5d_covariance_combined.root"` as
a **`SUPERSEDED_TOKEN`**, and `:93-95` refuse any `--support-family` containing one while requiring
`BKGAWARE_DIR` in the path. The donor declared here satisfies both, and its digest
`9f7b2f55…3c92a` **equals the `support_family_sha256` recorded by
`RECEIPT-20260816-p4-standard-stages456.json`** — so `active`'s components are bound to *this*
donor, not merely adjacent to it. A path change is not evidence of correction; the digest match is.

### The same-shaped trap on `active`

`p4_build_components.py` opens `--out` with `RECREATE`, and the Aug-16 rebuild is **not**
byte-identical to the Aug-9 audited object:

| | path | bytes | sha256 |
|---|---|--:|---|
| **declared here** (Aug-16) | `…/standard/candidate/std_final5_candidate.root` | 42,326,607,877 | `950f8cb1…c1263` |
| preserved (Aug-9) | `/pscratch/sd/j/josephrb/PRESERVE-p4-candidate-20260816/…` | 42,326,583,908 | `602bbcf2…f037` |

Two files, one name. The declaration names the **digest**.

## `provenance_qualifications` — unresolved, and travelling with the run

1. **`active` (S) consumes products whose authorization is UNDETERMINED.** S was built by the
   2026-08-16 stages 4–6 run, whose stages 1–2 **skipped all ten merges and all ten endpoints as
   already current** — those endpoints being the 2026-08-08 products at
   `active_universe_5d/standard/unfolds/` (ten ROOTs + ten `.done`, confirmed on disk). `OI-75`
   records that run as **unreconciled with a standing hold** scoped *"code/tests/receipts only — no
   cluster P4 run"*, and **item (1) of OI-75 remains OPEN and unanswered.**
   Joseph's 2026-09-15 ruling authorizes **consumption by this pilot only**, and states in terms
   that it *does not determine whether the historical run was authorized*, does not authorize
   committing the ROOT products, and does not approve adoption or publication use.
   **Nothing in this execution may be read as settling any of that.**
2. **The Aug-16 construction receipt authorizes nothing.** Its own text:
   `"adoption": "NONE. CANDIDATE products only. Construction is not adoption; the five Gate-6
   prohibitions at 19585b7 remain live and this receipt authorizes nothing."` A correct receipt
   attests to provenance, never to authorization.
3. **`Z_BUILD_PACKET.md` does not mention OI-75.** Its `active` = "RESOLVED — §1a" is a **technical**
   resolution (keys, dimensions, per-band traces, digest pins) and carries no permission. Recorded
   here so the packet's word "RESOLVED" cannot be read as clearance.
4. **`parent` (G) lineage is UNVERIFIED.** `z_build` binds G's file identity only; `Z_BUILD.md`
   remaining requirement 1 — bind G's exact identity, its actual `combined_source` and its
   production-CV input, and independently establish their lineage — is **not discharged**.
5. **The null's approval half is outstanding.** The precursor discharged *persistence* of both
   same-run internal fixed-seed CVs and the predicate. `B`, `S`, `B ≤ S` and an argued `epsilon` in
   `[B, S]` remain **UNAPPROVED**, and no tolerance is invented anywhere in this execution. The
   measured CV agreement is recorded with `"graded": false`.
6. **`stat` / `ml` reuse-versus-regeneration is RESERVED.** `Z_BUILD_PACKET.md` §4b lists that
   decision under **scientific acceptance**, not under the prerequisites for a measurement-only
   build — so it does not gate this execution and is **not settled by it either**.
7. **All seven causes remain `UNRESOLVED`** for Z, and there is no criteria owner: `owners.tsv` has
   twelve rows and none is scientific acceptance criteria.
8. **The invalid-ratio policy is unchanged and unvalidated.** The precursor substituted a neutral
   ratio 1 for non-finite or `≤ 0` ratios on nine physical operands (worst 576/32,849,103) and
   clipped to `(0.01, 100.0)` elsewhere (worst 387/32,849,103). **Rarity is not validation**, and
   this execution neither re-decides nor endorses that policy.

## Enforced limits and completion

- One task, `--time=01:30:00`, `--mem=64G`, `--cpus-per-task=4`, `OMP_NUM_THREADS=4`
  (`OPENBLAS_NUM_THREADS` and `MKL_NUM_THREADS` derived). Max admitted exposure **1.5 CPU
  task-hours**; 6.0 core-hours if that denomination is wanted. **No GPU.**
- `--no-requeue`, verified on the actual job with the status-aware, identity-aware, value-aware
  `scontrol` assertion (non-zero `scontrol` status is CANNOT-LOOK and refuses).
- Fresh output namespace that **refuses** a non-empty or unlistable target rather than cleaning it.
- **Exit 2 is preserved and is not success.** It means construction ran to completion with
  NON-PASSING science. The launcher requires the pilot receipt to exist before reading 2 as
  completion, because `mnv_guarded_run.py` uses exit 2 for CANNOT-LOOK and can return it without
  running the payload. Exit 1 is refusal. **Scheduler status alone is not the verdict.**
- Completion requires: both closed products readable back, each receipt's recorded product digest
  matching the file beside it **matched by path**, the null slab reloadable through
  `z_receipt.load_null_operands`, both eigenvalue spectra persisted with `clipped: false` and
  `regularized: false`, and every receipt written **after** its product.
