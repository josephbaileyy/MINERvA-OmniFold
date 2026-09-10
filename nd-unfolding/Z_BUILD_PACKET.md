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
| `throw` | ⚠ **WAS `uq_5d/unified_throw_cov_5d.root` — THAT IS THE PRE-J28 OBJECT AND IS WITHDRAWN.** See §8 | — | **NO QUALIFYING CANDIDATE** |
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

---

# 7. THE INPUT PLAN — all three investigations in, 2026-09-10

Read-only throughout. No compute was launched. Nothing below is adopted, graded or decided.

## 7.1 `stat` and `ml` — **REUSE**, and the hypothesis I proposed was refuted and inverts

I asked whether the stat and ML products sit outside the bkgaware correction, in which case reuse
would mix footings inside one covariance. **Measured, and the opposite is true.**

```
hCov_combined5d_total − (hCov_universe5d_total + hCov_stat5d_reported + hCov_mlsplit5d_reported)
    max abs residual 0.0, max rel residual 0.0    diagonal AND first off-diagonal, all 10,694 rows
√Tr(hCov_combined5d_total), bkgaware support family   = 4.357790406860002e-38
```

That constant is **bit-identical** to three independent things: G's own stamp `sqrt_tr_old`
(re-verified in our committed capture, job `58127048`), SPEC §1.1's *"the footing every arm is
matched on"*, and this fresh measurement. So `C_stat` and `C_ML` are **already constituents of
G's footing**, and `adopt_unified_5d.py:6-20` carries them through untouched.

**The inversion: reuse PRESERVES the footing G's M-legs are measured against. Regeneration is
the move that introduces a footing difference relative to G** — and SPEC §3.3's `(6, Z)` cell
already lists *"replicas regenerated with no rationale"* as a reject condition.

The filename-level worry was reasonable — the files predate the bkgaware event loop, and
`sbatch_finalize_5d_bkgaware_gpu.sh:8-10` does say *"reuse existing"*. But #13 is a **per-universe**
background reweight and it does not move the nominal: `bank_uthrow_5d/cv.npz` and
`bank_uthrow_5d_bkgaware/cv.npz` are **md5-identical**, all three nominal CVs share one mask, and
the bkgaware shift (Δ integrated `+2.567e-04`) is **smaller than the same-treatment run-to-run
scatter** (`−5.657e-04`). Since `combine_cov_nd.py` uses the CV only through `rep = cv>0` and the
mask is identical, these two would be **bit-identical** had they been built against the bkgaware CV.

Both digests are **live, not stale** — `sha256sum` on disk today returns SPEC §1.1's values. Each
file holds exactly one `TH2D`, 10694 × 10694. The estimator was reproduced from raw replicas:
√Tr recomputed to `1.8063275906e-39` / `1.4934344281e-39` against on-disk
`1.8063275905782307e-39` / `1.4934344281056095e-39`.

**THREE DISCLOSURES, none of which regeneration fixes:**

1. **Mixed normalization inside Z's own sum.** `C_stat`/`C_ML` use unbiased `1/(N−1)`; every
   systematic term uses biased `1/N`. Effect: `+0.50%` on √Tr(`C_stat`), `+2.15%` on √Tr(`C_ML`).
   This is `OI-137`'s surviving gap, and Joseph already ruled it **2026-08-22: disclose, do not
   correct**. Switching to `1/N` would break bit-identity with G's footing constant.
2. **`C_stat` has support flicker and `C_ML` does not** — 18,979 entries exactly zero inside the
   reported mask, every one of the 100 replicas carrying at least one. **Not previously recorded
   for the scalar-5D object.** Same class as `VL132`'s PET finding, different artifact.
3. **`C_stat`'s ensemble spans two epochs** (seeds 1–2 on 07-11, the rest 07-13). Immaterial:
   leave-2-out moves √Tr by `+0.271%`, and the two sit at z = `−0.053` and `−1.012`.

**Provenance is thin and that is a real cost of reuse:** no stamps inside either ROOT, **no
`RUNS.tsv` row** (0 of 346, with a positive control), and no producing receipt anywhere — only a
consumer record. The producing revision is recoverable (`677e215d`, estimator line byte-identical
to today's), but the population validator did not exist when these ran.

**If regenerated instead:** arms 1 + 2 only, ≈ **20 GPU + 9 CPU task-h at ceilings** (≈14.9 + 5.8
at actuals) — **not** §5.3's whole-campaign figure. And the sting: only one `of_inputs_5d.npz`
exists with no bkgaware variant, so a regeneration off it reproduces the same background footing
and buys nothing; one that genuinely changed the footing would need a 142 GB re-dump and would
produce components that **no longer sum to G's `4.357790406860002e-38`**.

## 7.2 `active` and `footing` — RESOLVED, values in §1a

## 7.3 `null` — the decision point, and the blocker is not the one I expected

**The hypothesis is CONFIRMED on the merits.** `x_cv` and `x_cv2` are the *same call with the same
seed*, issued twice (`unified_throw_cov.py:369` and `:514`), and `x_cv` is computed **before the
first slab is globbed**. Zero ensemble data dependency. **≤ 0.37 CPU task-h against 61–80 for arms
5+6 — a factor of ~170–220, and zero GPU either way.**

**⚠ CORRECTED — THE SENTENCE BELOW IS FALSE AND IS RETAINED ONLY SO THE ERROR IS LEGIBLE.**
A post-split slab set DOES exist: `mii/member_k000000` carries `estimator_seed=1000`,
`draw_seed=1000` and `flux_normalized=1` on all 40 uthrow and 21 block slabs, and would pass
`:477`, `:483`, `:489` and `:496`. My search covered `uq_5d/` and missed `mii/`. **So the blocker
on the cheap route was never a tooling question — it is an AUTHORIZATION question, and the
answer is that those slabs are Gate-2 restricted.** See §8.

~~**But `unified_throw_cov.py:496` refuses every archived 5D slab set on pscratch.** They carry
`seed`, not the post-split `estimator_seed`/`draw_seed`:~~ *"There is deliberately no fallback…
doing so would let a pre-split slab combine beside a post-split one whose draw seed differs, which
is a silent mixed-estimator covariance."* So "re-run arm 7 with `--null`" is **not available at
HEAD**, for reasons that have nothing to do with the null.

| branch | what it is | cost | the catch |
|---|---|---|---|
| **A** | patch the producer, regenerate arms 5+6, re-run arm 7 | **61–80 CPU task-h** | arm 5 carries a measured ±59% swing |
| **B** | patch the producer **+ a re-stamp migration** on the existing slabs, then one arm-7 invocation | **≤ 0.37 CPU task-h** | the re-stamp is **a ruling, not a step** — `:496` argues against a fallback *inside the driver*; whether a separate audited migration tool is a different object is Joseph's call |
| **C** | a ~20-line standalone entrypoint | **≤ 0.37 CPU task-h** | `Z_BUILD.md` requirement 3 declines it: *"copying an external CV into either slot is not a substitute"* |

**⚠ AN ORDERING CONSTRAINT THAT OUTRANKS THE CHOICE.** §3.7a's route (i) — pinning
`num_threads`/`deterministic`/`force_row_wise` — **changes `x_cv` itself**, and therefore the
support mask, `nrep`, and every downstream covariance. Operands produced today under the unpinned
envelope are **superseded the moment route (i) is adopted**. If route (i) is on the table at all,
it is decided BEFORE the operands are produced.

Two more: `z_build.py:519` requires the null mask to match the production CV's mask
**elementwise** — cardinality agreement is known, elementwise is unmeasured and only the unfold
settles it. And `persist_null_operands` records no seed, bank or run id, so a standalone slab and
a genuine in-producer one are **byte-indistinguishable after the fact**.

## 7.4 THE RECOMMENDED INPUT PLAN

| source | plan | state |
|---|---|---|
| `parent` | G, `4f168e83…` | ready |
| `central` | `630306e20e4e…` | ready |
| `support` | CS, `9f7b2f55d758…` | ready |
| `active` | S, `950f8cb1…` — **name the digest, not the path** (an Aug-9 twin exists) | ready |
| `stat` | **REUSE** `6580016fa713…` | ready, with three disclosures |
| `ml` | **REUSE** `27b2e456f80e…` | ready, with three disclosures |
| `throw` | `unified_throw_cov_5d.root`, 9 keys incl. `hJointMeanShift` | ready |
| `null` | **branch B**, after the route-(i) ruling | **BLOCKED on two rulings** |
| `footing.*` | computed, §1a | ready |
| `producing_revision` | `93021448` or later | ready since the merge |

**Nine of ten are ready. The whole plan waits on `null`, and `null` waits on two rulings rather
than on compute.**

## 7.5 THE EXACT RESOURCE AUTHORIZATION NEEDED

**If branch B is chosen — the smallest faithful route:**

> Authorize **one CPU invocation of `unified_throw_cov_5d.py --combine --null`**, `ntasks=1`,
> `shared` queue, **≤ 0.5 CPU task-hours** and **0 GPU**, against `bank_uthrow_5d` and the
> `union_20260806_full160` / `rescaled_20260806_full160` slabs, producing one null-operand `.npz`
> and no covariance product for adoption.

That is **≈ 0.1 %** of R5's CPU ceiling. It also needs, and these are **not** resource questions:

1. **The route-(i) ruling first** — pin the estimator envelope or not. Operands produced before
   this are superseded by it.
2. **A ruling on the re-stamp migration** — whether writing `estimator_seed`/`draw_seed` onto
   existing slabs via a separate audited tool is admissible, given `:496`'s deliberate refusal of
   an in-driver fallback.
3. Two Tier-2 code changes (move `[rep]` after the persist; add the persist call). Code, not compute.

**If branch A is chosen instead:** ≈ **61–80 CPU task-h**, and it should be authorized as arms 5+6
of a production round rather than as a null procedure.

**Not needed for any of this:** the four withheld boundaries, a criteria owner, or any cause
disposition. **And nothing produced under any branch can be accepted** — `null_epsilon` is
withheld, so `assess_null` returns `NOT ASSESSABLE` with reject conditions `4c` and `11` in every
case. This buys auditability, not acceptance.

---

# 8. THE THROW SOURCE — corrected 2026-09-10. **NO CANDIDATE QUALIFIES.**

A bounded read-only investigation compared the three candidate families. **The answer is uniform
and it is not about any family individually: the `null` role has no candidate at all, so item 4 —
binding the matrices and the null operands to one producing execution — fails for all three.**

**MEASURED: the null operands were never produced by any execution.** `unified_throw_cov.py`
computes `x_cv` at `:369-371` and drops it at `:586`. A `find` over the whole data root returns
2,429 `.npz` files and the only matches are PET artifacts off the publication path. This is a
**writer gap, not a lost file** — which is why no retrofit onto an existing ROOT can satisfy
`REQUIREMENTS["null"]`'s *"at throw creation"*.

| | **A** `unified_throw_cov_5d.root` | **B** `…_fluxfix_20260806_full160.root` | **C** `mii/member_k000000/…` |
|---|---|---|---|
| sha256 | `038c6132…` | `4cb02ae7…` | `b1d0ceca…` |
| producing revision | **UNKNOWN, unpinnable** | UNKNOWN (job bound) | `7ac0edec…`, dirty 0 |
| receipt binding it | 12 files — **as `pre_j28_throw`** | **25 files, incl. G's own build receipt** | **none** |
| producing job | **no log, no job record** | `56429334` COMPLETED | `57753248` COMPLETED |
| J28 stamp on slabs | **30 of 40 UNSTAMPED** | 40/40 and 36/36 | 40/40 and 21/21 |
| seed roles on slabs | legacy `seed` only | legacy `seed` only | `estimator_seed`+`draw_seed` |
| population | complete | complete | complete |
| gate | none | none | **Gate-2 restricted** |
| **null bound to same execution** | **NO** | **NO** | **NO** |

**A — DISQUALIFIED, and this packet was wrong to declare it.** Three independent confirmations
that it is the pre-J28 object: the repository's own `receipt_construction_contract_5d.json` names
its entry **`pre_j28_throw`**; `RUNBOOK-20260807-gbdt-closeout.md:36` records the J28 fix landing
on the Aug-6 object; and 30 of its 40 uthrow slabs carry no `flux_normalized` stamp. It has no
producing log, no job record and no pinnable revision, and slabs 30–39 of its input set were
**overwritten on 2026-08-06**. ⚠ **AND `adopt_unified_5d.py:76` DEFAULTS `--uthrow` TO IT**, so
the pre-J28 object is also what an omitted flag selects.

**C — the best-provenanced and nonetheless unavailable.** Only family with post-split seed stamps,
a pinned revision and an import-closure receipt — and the only one **no receipt binds**. It is
**arm 7 of the seven k=0 rehearsal jobs**, so using it as Z's `throw` is *consumption outside the
seven rehearsal jobs*, which `DECISION-20260830` forbids independently of any technical merit.

**B — the only viable base, incomplete rather than wrong.** Fully J28-corrected on both sides,
digest-bound in 25 places, bound to a completed job — and **it is the throw G itself was built
from**: G's `receipt_candidate_stamps_5d.json` names it three times and names A zero times. It
still fails 11b and carries no seed-role stamps.

**THE RECOMMENDATION IS A CONSTRUCTION, NOT A SELECTION.** Z's `throw` should be a **new product
built for Z**, on **B's footing** (`union_20260806_full160` / `rescaled_20260806_full160`), with
the writer changed to persist the null operands in the same execution. That is the only route
that makes item 4 and condition 11b satisfiable at all. B is not selected because its slabs would
pass `:496`, and C is not rejected because its stamps pass — those tests decide nothing here.

## 8a. Decisions that are Joseph's

1. **The footing is a contract change, not a source swap.** A versus B moves Z between the pre-
   and post-J28 objects, and SPEC §1.1 already rules the July artifacts *"not evidence for Z."*
2. **Can ANY pre-existing throw satisfy Z?** §1.3a says *"Z's own"*, 11b says *"in Z's own throw
   product"*, `REQUIREMENTS["null"]` says *"at throw creation."* Read strictly, all three require a
   throw produced FOR Z, which retires the three-way choice entirely. Nothing in the tree settles
   strict versus loose.
3. **May the k=0 rehearsal slabs be consumed to build Z's throw?** They are the only post-split,
   fully-J28-stamped slab set in existence. Consuming them is squarely what the Gate-2 clause
   forbids, and **no authorization removes that gate — only the rehearsal work landing does.**
4. **Route (i) still outranks all of it.** Pinning the estimator changes `x_cv`; operands produced
   before that ruling are superseded by it.

## 8b. A correction to how `OI-172` is cited

Its 36.5 h figure reproduces exactly — A's mtime and ctime are both `2026-07-13 02:15:41 −0700`,
and `07c18aee` (2026-07-14) is the oldest commit adding `fixed_seed_null_norm`. But the conclusion
*"no stamp for it can ever be produced"* does not follow, **because A's ROOT already contains
`fixed_seed_null_norm`.** What the gap actually establishes is that A was written by **uncommitted
code** — SPEC §3.3 condition 10, a stronger and differently-shaped defect than the row states.
