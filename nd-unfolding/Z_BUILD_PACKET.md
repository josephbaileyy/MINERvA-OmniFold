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
| `active` | **S**, `nd-unfolding/active_universe_5d/standard/candidate/std_final5_candidate.root` | `950f8cb15c5a…`, **42,326,607,877 B**, 49 keys | **RESOLVED — §1a** |
| `stat` | `uq_cov_stat_5d.root:hCov_stat5d_reported` | `6580016fa713…` | available; **reuse-vs-regenerate RESERVED, §4** |
| `ml` | `uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported` | `27b2e456f80e…` | available; **same reservation** |
| `throw` | `uq_5d/unified_throw_cov_5d.root` | 2.49 GB, 9 keys | available; supplies `C_unified`/`C_blocksum` **diagonals** and `hJointMeanShift` |
| `null` | `x_cv`, `x_cv2`, `support_mask` | — | **DOES NOT EXIST — §0** |

Plus `footing.mask_sha256` and `footing.row_order_sha256`, `producing_revision`, and
`input_kind`.

### 1a. `active` and `footing` — RESOLVED 2026-09-10, measured

**`active` = S.** `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/candidate/std_final5_candidate.root`,
sha256 `950f8cb15c5a0bd785d65e7f85f4cb40fa86e27383973f82ef15c7ef525c1263`, 42,326,607,877 B,
49 keys. All five band keys plus `hCov_active5d_total` present, every one `TH2D` 10694×10694 —
the shape `z_build.py:545` demands. The five band names come from `p4_lib.BANDS` (imported, never
retyped): `BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`,
`Muon_Energy_MINOS`, each under `hCov_active5d_<band>`. Per-band traces reproduce
`std_component_manifest.json`'s `active_traces` to every printed digit and sum to the recorded
total, so `p4_lib.check_component_sum` will find it consistent at trace level.

The pin is committed in seven places — `std_component_manifest.json`, `p4_standard_validation.json`,
`std_proj4d_candidate_projmanifest.json`, SPEC §1.1, `PUBLICATION-READINESS-20260822.md`, and two
2026-08-16 receipts — and **matches disk today**.

**⚠ A SAME-SHAPED TRAP, NAMED SO NOBODY DECLARES THE WRONG ONE.** `p4_build_components.py` opens
`--out` with `RECREATE`, and the Aug-16 rebuild is **not** byte-identical to the audited Aug-9
object. Both exist:

| | path | size | sha256 |
|---|---|---|---|
| live (Aug-16) | `…/standard/candidate/std_final5_candidate.root` | 42,326,607,877 | `950f8cb1…` |
| preserved (Aug-9) | `/pscratch/sd/j/josephrb/PRESERVE-p4-candidate-20260816/…` | 42,326,583,908 | `602bbcf2…` |

A manifest must name the digest, not the path alone.

**`footing.*` — computed, and they are digests of the CENTRAL, not of G or of `active`.**
`z_build` derives `mask = central > 0` over the full 65,856-bin grid and
`rows = flatnonzero(mask).astype(int64)` (10,694 entries), then hashes each with
`z_receipt.sha256_array`, which folds `dtype.str` and `shape` in before the buffer:

```
footing.mask_sha256      = eed021e93fd7ccc17330b3fcddbb326e3c0f2186309aed3a70c2ba31cae750e2
footing.row_order_sha256 = 61a7c9fd70d7c7718d396afa5c92b6b1bb0b94e7280245d35c9f8c4117f8b461
```

computed from `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` (`630306e20e4e…`, 479,553 B), with
three controls: the inline hasher proved equivalent to `receipt.sha256_array` including a
negative control; the same array in `pm_root_inspect`'s spelling reproduces the committed
`S_ROW_INDEX_SHA256` / `S_REPORTED_MASK_HASH` exactly; and S's independently stored
`hRowIndex5D` hashes identically. **These can be written into a manifest now.**

**⚠ THE INSPECTION REPORT'S DIGESTS ARE NOT THESE, and pasting them in would fail the gate.**
`pm-root-inspection-20260909c-report-58127048.json` computes `sha256(idx.tobytes()+b"|C")` and
`sha256(idx.tobytes())` — over the int64 **index array**, with no `dtype|shape|` prefix and a
trailing `|C` tag. `z_build` wants `sha256_array` over the 65,856-entry **boolean**. Different
algorithm, different operand. Using them raises `central: mask_sha256 mismatch`. They are the
S-family spelling and correct for what they are.

**And the `NOT read_from_G` tag does NOT disqualify them for `footing` — that reading would be
an error.** `z_build` never claims `footing` comes from G; it writes
`row_order_basis: "…reconstructed from declared production CV; NOT read_from_G"` into every
receipt. The producer-input route is the sanctioned one (SPEC §1.3d). What the tag disqualifies
is any claim that these digests are evidence about **G**.

**What actually remains on PM-4.** The producer input IS identified and pinned — it is
`adopt_unified_5d.py:79`'s argparse default, invoked without `--prod` by
`sbatch_adopt_stamped_footing.sh`. What is not established is that **G consumed those bytes**:
G's build receipt binds four files and not this one. Closing it needs a committed record binding
G's `--prod` input by digest at build time, or a re-run under a receipt that does.
*(SPEC §1.3d cites `sbatch_adopt_stamped_footing.sh:29` as the supplying site; line 29 is a `cd`.
The naming site is `adopt_unified_5d.py:79`. Worth correcting when PM-4 is amended.)*

**A limit on what `footing` proves.** `z_build` derives the mask from the `central` it was given
and compares it to the manifest, so the gate catches a manifest inconsistent with its own named
central — swap the central and rewrite both digests and it passes. `footing` is self-consistency;
the scientific weight rests on the unbound PM-4 claim.

## 2. UNRESOLVED BINDINGS

1. **`null` does not exist.** §0. The binding constraint on the whole packet.
2. ~~**`active` is unnamed here.**~~ **RESOLVED — §1a.**
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

**Revision. ⚠ THIS GAP CLOSED WHILE THE INVESTIGATIONS RAN.** `_code_identity` at
`z_build.py:260-266` requires `producing_revision` to EQUAL the executing checkout's `HEAD` and
refuses otherwise. While the driver sat unmerged on `lane/z-build-integration`, that was
unsatisfiable from any clean checkout: the code did not exist at any `HEAD`. It landed on `main`
at **`93021448`** under Joseph's implementation-landing authorization, so a real-input build can
now declare a committed `producing_revision` and the code leg stops being unsatisfiable by
construction. The driver still records `worktree_files_differing_from_revision`, which is a
record and not a gate — a build from a dirty checkout proceeds and says so.

**Environment.** `/global/homes/j/josephrb/.conda/envs/root_6_28`, ROOT 6.28/12, **with the
env's `bin` prepended to `PATH`** — without it cling cannot find `x86_64-conda-linux-gnu-c++`
and segfaults. That is the defect that killed job `58123269`; the fix is on `main`
(`pm_root_inspect.path_with_inner_python_bin`). Local testing used ROOT 6.36 on macOS, which is
**not** the cluster's ROOT.

**Resources.** ⚠ **The memory figure below is CORRECTED UPWARD and is still not measured.** An
earlier revision said ~2–3 GB peak. `z_build.py:544-549` holds all five active bands **plus** the
total simultaneously — six `10,694²` float64 matrices ≈ **5.5 GB for `active` alone**, before the
lateral sum, the two support sums, `cov_stat` and `cov_ml`. Reading eight files and assembling two
variants is still small in TIME — a handful of `10,694²` operations plus two `eigvalsh` at ≈113 s
each — but it is **memory-bound and the peak has not been measured**, and the 38.59 GB support file is read per-band, not resident.
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
