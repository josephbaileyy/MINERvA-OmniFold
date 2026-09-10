# The smallest real-input Z build — a PREPARED PACKET, not a request to run

**PREPARED 2026-09-10 against `origin/main` `ceb474cc`, driver at `bf2b7499`
(`lane/z-build-integration`, NOT merged). Nothing here is a launch, a bid, a reservation, or a
request for one.** It states what a real-input build would need, what it would produce, and what
it still could not conclude.

**AUTHORIZES NOTHING ITSELF.** The governing committed stage gate is
`DECISION-20260906-joseph-authorizes-z-specification-only` (iv): *"This authorizes no
implementation, construction, compute, grading, adoption, or publication change. Each of those
requires its own committed authorization."* No later **committed** record supersedes it — checked
against every DECISION/AUTHORIZATION/RULING after 2026-09-06.

**THE AUTHORIZATIONS THAT DO EXIST, recorded exactly and read narrowly.**

1. **An in-session instruction to BUILD, 2026-09-09.** Joseph directly asked a peer session to
   implement the end-to-end Z integration, relayed and acted on. That is why `z_build.py` exists
   and it is a real instruction — but it is a session instruction, not a committed record, and it
   authorized *writing code and nothing else*. It did not authorize merging, running, adopting or
   grading, and no such permission may be inferred from it.
2. **A merge authorization, 2026-09-10.** Joseph authorized merging the reviewed integration and
   this packet, *conditional on targeted reviewer confirmation passing*, after normal merge
   checks, with an explicit instruction to identify and review any delta if the tip moved. He
   scoped it in terms: **implementation landing only — not cluster execution, scientific
   acceptance, adoption, or publication use.**

**What follows from (2) and what does not.** It makes the code committed and citable, which is
itself a prerequisite for the code leg. It does **not** license a real-input build, does not touch
any of §4b, and leaves `DECISION-20260906` (iv) standing for everything except implementation
landing. The resource authorization in §5 is still required and is still absent.

---

## 0. THE FINDING THAT SIZES EVERYTHING ELSE: there is no read-only smallest build

`z_build` requires a `null` source: an `.npz` carrying `x_cv`, `x_cv2` and `support_mask`
(`z_receipt.load_null_operands:455`), and `REQUIREMENTS["null"]` says they must be *"persist[ed]
… at throw creation"*.

**They do not exist in any committed product.** Measured on the cluster:

```
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/unified_throw_cov_5d.root   2.49 GB
  9 keys: C_unified, C_blocksum, C_cross, sqrt_tr_unified, sqrt_tr_block,
          joint_mean_shift_norm, fixed_seed_null_norm, n_throws
  x_cv present: False   x_cv2 present: False   support_mask present: False
```

This is not an oversight — §1.5's null block is *"NEW IN REV. 16, and it is a WRITER change, not
just a receipt field"*. The consequence is structural and should not be softened: **the smallest
real-input Z build is not a login-node read of eight existing files. It requires a new throw run
that persists the null operands.** Any packet that omits this is describing a synthetic build.

Two honest options, and the choice is scientific rather than technical:

- **(A) Re-run the throw with the writer change.** Compute. Arm 7 of the production round.
- **(B) Reconstruct the null operands from existing products.** No committed artifact supplies
  them, so this would be a new derivation needing its own justification — and `REQUIREMENTS["null"]`
  says *at throw creation*, which a reconstruction is not.

---

## 1. THE EIGHT DECLARED INPUTS

`z_build` requires exactly these eight `sources` keys, exact-set enforced. Digests are the
committed bindings and the 2026-09-09 capture (job `58127048`), re-measurable.

| role | artifact | identity | state |
|---|---|---|---|
| `parent` | G, `uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root` | `4f168e83eaeb…`, 0.83 GB | **available** |
| `central` | `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | `630306e20e4e…`, 0.5 MB | **available** |
| `support` | CS, `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` | `9f7b2f55d758…`, **38.59 GB**, 45 band keys | **available** |
| `active` | the p4 candidate carrying the 5 active lateral bands | not pinned in this packet | **UNRESOLVED — must be named** |
| `stat` | `uq_cov_stat_5d.root:hCov_stat5d_reported` | `6580016fa713…` | available; **reuse-vs-regenerate RESERVED, §4** |
| `ml` | `uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported` | `27b2e456f80e…` | available; **same reservation** |
| `throw` | `uq_5d/unified_throw_cov_5d.root` | 2.49 GB, 9 keys | available for `C_unified`/`C_blocksum` **diagonals only** |
| `null` | `x_cv`, `x_cv2`, `support_mask` | — | **DOES NOT EXIST — §0** |

Plus `footing.mask_sha256` and `footing.row_order_sha256`, `producing_revision`, and
`input_kind`.

## 2. UNRESOLVED BINDINGS

1. **`null` does not exist.** §0. The binding constraint on the whole packet.
2. **`active` is unnamed here.** The five active lateral bands' source file must be pinned by
   path and digest before a manifest can be written.
3. **G's production-CV input is not bound by G's own hash receipt.** Measured: G carries 13 keys
   and `hRowIndex5D` is **not** among them, so §1.3's mask and row-order digests are
   *reconstructed through the producer-input route* and tagged `NOT read_from_G`. `footing.*`
   must therefore be supplied from that route and declared as such. This is `PM-4`, and its
   phrasing needs amending by its owner.
4. **Residual band identities are never declared.** `R` is a 27-name complement; membership is
   checked by count and by `V`/`A` equality, not by name. Reviewer finding F7.
5. **Endpoint `globalCompleteness` above one.** `EP_Muon_Energy_MINOS_0` = `1.001824`,
   `_1` = `1.000521`, the other eight exactly `1.0`. Carried verbatim as
   `REQUIREMENTS["endpoint_completeness"]`; unadjudicated.

## 3. PRODUCING REVISION, ENVIRONMENT, RESOURCES, ARTIFACTS

**Revision.** `bf2b7499` on `lane/z-build-integration`, *not merged*. The driver records
`worktree_files_differing_from_revision`, which lists `z_build.py` itself while untracked — a
record, not a gate. A real-input build should run from a **committed** revision or the code leg
is unsatisfiable by construction.

**Environment.** `/global/homes/j/josephrb/.conda/envs/root_6_28`, ROOT 6.28/12, **with the
env's `bin` prepended to `PATH`** — without it cling cannot find `x86_64-conda-linux-gnu-c++`
and segfaults. That is the defect that killed job `58123269`; the fix is on `main`
(`pm_root_inspect.path_with_inner_python_bin`). Local testing used ROOT 6.36 on macOS, which is
**not** the cluster's ROOT.

**Resources.** Reading eight files and assembling two variants is small: the arithmetic is a
handful of `10,694²` operations plus two `eigvalsh` at ≈113 s each, dominated by **memory
(~2–3 GB peak), not time**, and the 38.59 GB support file is read per-band, not resident.
Replay I/O measured at **674 MB/s** on pscratch → the 41.18 GB component family is ≈61 s
(≈0.017 CPU task-h). **If option (A) is taken, the throw run dominates and this estimate is
irrelevant** — that is a production round, separately costed and separately authorized.

**Expected artifacts.** Two products (`out-cv`, `out-mean`), two receipts, one null slab. Every
destination is pre-reserved with `open("xb")`, so nothing overwrites; a hard kill can leave
empty reserved files, which is why consumers must require both receipts *and* verify product
hashes.

**Terminal outcomes.** `2` = ran to completion, science **NON-PASSING** — the only outcome this
command can produce. `1` = construction failed or the invocation was malformed, with a
`{"construction_status": "FAILED"}` stderr envelope. `0` only from `--help`. **Exit 2 is not a
success code and is not proof the artifacts exist.**

---

## 4. THE SPLIT JOSEPH ASKED FOR

### 4a. Prerequisites for a MEASUREMENT-ONLY, NON-PASSING build

What it would establish: that the declared real inputs can be read, that the gates run against
real bytes, and that a receipt records what was actually there. **No scientific question is
answered and no cause is discharged.**

1. The `null` operands must exist — §0, and this is the only hard blocker.
2. `active` named and pinned.
3. `footing.*` supplied from the producer-input route and declared as reconstructed.
4. A committed producing revision.
5. The `root_6_28` environment with `PATH` prepared.
6. **An authorization to run it at all** — §5.

**None of the four withheld boundaries is needed.** None of the seven causes needs a disposition.
No threshold, no criteria owner. The build is designed to be non-passing and will be.

### 4b. Additional prerequisites for SCIENTIFIC ACCEPTANCE

Everything in 4a, plus — and none of these is code:

1. **The four withheld boundaries declared**: `null_epsilon` (needs an operating-error bound `B`,
   a scientific cap `S`, `B ≤ S`, and ε argued within `[B, S]` — none established),
   `cause3_agg`, `cause3_med`, `cause3_corr`.
2. **A criteria owner.** `owners.tsv` has twelve rows and none is scientific acceptance criteria.
3. **The reuse-versus-regeneration decision** for `C_stat` and `C_ML` — §5.
4. **All seven causes disposed for Z specifically.** Discharge is a property of a
   `(cause × artifact)` pair; **Z inherits nothing from G**. That is 28 `(cause × leg)` cells.
5. The twelve `REQUIREMENTS` the driver carries in every receipt — parent lineage, component
   footing, causes 1–7, null, code and run, endpoint completeness, runtime.
6. `PM-4`'s phrasing amended by its owner.
7. For any **significance**: the projection map designated (three implementations exist; two are
   byte-identical on canonical edges but take **opposite** actions where support masks do not
   nest — `FINDING-20260910`), the `ndf` and `norm.isf` conventions declared, and a decision
   threshold and margin, which exist nowhere in the tree.

---

## 5. RESERVED, AND THE EXACT AUTHORIZATION NEEDED NEXT

**Reuse versus regeneration of `C_stat` and `C_ML` is RESERVED, not authorized.** §1.1 records it
as *"an open scientific question, not a settled requirement"*; §(v) reserves criterion changes for
Joseph's separate decision; no committed record resolves it.

**⚠ CORRECTED. An earlier revision of this packet said the manifest's file inputs mean "the
architecture can only reuse them" and that the question was "settled by construction". That is
wrong, and Joseph caught it.** Requiring a *file* says nothing about that file's *provenance*.
Measured in the driver: `sources["stat"]` is a path and `manifest["stat_key"]` an object name;
`z_build.py:558-559` reads an `(n, n)` matrix and applies **no** lineage, provenance or identity
constraint on which file it is. A freshly regenerated `C_stat`, written to a new path and
declared in the manifest, is consumed identically to the historical one.

So the driver **neither reuses nor regenerates** — it consumes a declared matrix. The decision
lives **upstream of `z_build`**, in which file a manifest names, and it remains reserved rather
than foreclosed. Nothing in the architecture settles it, and no code change is required to take
either branch. The spec's author and I both over-read this in the same direction; the correction
is Joseph's.

**THE EXACT AUTHORIZATION NEEDED NEXT — one committed record, and it is narrow.**

A committed `AUTHORIZATION-*` or `DECISION-*` that supersedes `DECISION-20260906` (iv) *for
implementation only*, stating:

1. That the reviewed integration at `bf2b7499` **may be merged to `main`** as implementation.
   This alone unblocks nothing operationally — it makes the code citable and committed, which is
   itself a prerequisite for the code leg.
2. Separately and **only if** a real-input build is wanted: whether option **(A)** — re-run the
   throw with the writer change, which is **compute and needs its own resource authorization** —
   or option **(B)** — a justified reconstruction of the null operands — is taken.
3. Explicitly, that it authorizes **no adoption, no grading, no discharge, no projection and no
   publication use**, so the specification-only stage gate survives for everything except the two
   items named.

**What does NOT need authorizing:** anything in §4b. Those are scientific decisions and resource
questions, and none is unblocked by a merge.

**Recommended order.** (1) merge authorization for `bf2b7499`; (2) the reuse-versus-regeneration
decision, because it determines whether `stat`/`ml` are inputs at all and therefore what a
manifest can even declare; (3) only then the null-operand route and its resource authorization.
Doing (3) first would spend compute against a manifest whose input set is not yet decided.
