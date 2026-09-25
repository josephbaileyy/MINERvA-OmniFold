# N-D OmniFold run log

The complete pre-compaction chronology is frozen at
`evidence/prepublication-2026-08-20-0b329e8a` under this exact path:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:nd-unfolding/ND_OMNIFOLD_RUN_LOG.md
```

Read `ND_OMNIFOLD_STATUS.md` for current scalar/PET/FPS state,
`PET_UQ_REMEDIATION_STATUS.md` for the live PET DAG, and `VALIDATION_LEDGER.md` for verified
numbers. The tag is historical evidence, not scientific adoption.

## Post-freeze chronology

Append only committed post-2026-08-20 events here; keep current state in the owning STATUS file.

### 2026-09-14 — prospective Z precursor campaign `z_precursor_20260914` COMPLETE (construction evidence only)

Authorized by Joseph 2026-09-14 as a 62-task measurement-only campaign, max additional admitted
exposure 393.5 CPU task-hours, no GPU, no ceiling extension. **Successful execution adopts nothing.**

- **Deployment** `/pscratch/sd/j/josephrb/zdeploy-e09513d8` at `e09513d842ad3acc1964c1af740696f02eaed7d9`
  (immutable, `dr-xr-x---`; A-2(f) listing `b25953573962d94650c40bee6190a8d27b08fa059e0668b3bd6c67556a777b7b`
  over 886 tracked files).
- **Campaign manifest digest** `e6426e25ec06798739730d4a2e7f9c31cbbd04f1a61b8a9f2b8e62646d0ff993`,
  namespace established by an exclusive create.
- **Jobs** `58302605` (block, 21 tasks `0-20%10`), `58302608` (run, 40 tasks `0-39%40`),
  `58302610` (combine, `afterok` on both). All tasks `COMPLETED 0:0`.
  `Requeue=0` asserted per job (status-, identity- and value-aware) AND verified after the fact:
  `sacct --duplicates` returned 62 rows with no JobID appearing twice, so no requeue occurred.
- **Population** 62/62 by identity — 21 `block5d_*.npz`, 40 `uthrow5d_slab_*.npz`, 1
  `unified_throw_cov_5d.root`. 62 claims, 62 receipts, every receipt `attempt: 1`;
  `_campaign/evidence/` and `_campaign/recovery/` both empty, so no recovery ran.
  `z_precursor.require_campaign_complete` passes for all three declared arms.
- **Receipt-last** verified independently of the producer's own log line, by mtime: the combine's
  product is `1789426386` and its receipt `1789426395` (+9 s); no receipt on any arm predates the
  product it names; exact bijection with the products on disk (0 undeclared, 0 missing).
- **Product** `unified_throw_cov_5d.root`, 2,668,265,910 B, sha256
  `09a029ed2a7de0ffd144b1ad0ad8d3e0bf8e8b9788797b0af58693c753795560`. Opens with
  `Recovered: False`; `C_unified` is 10694×10694.
- **Seeds** draw 1000, estimator 1000, `MNV_EST_SEED_OFFSET` unset (`est_seed_offset 0`,
  `est_seed_offset_declared 0`) — recorded in the product and identically in all 40 run slabs.
- **Support** reported bins **10694 of 65856** under `x_cv > 0`; 55162 genuinely zero, **0 negative**
  (10694 + 55162 = 65856). Bank: 12 knob bands, 100 flux universes, 32,849,103 events,
  edges `[14, 16, 7, 7, 6]`. 160 throws from 40 slabs; 124 band donors.
- **THE NULL'S PERSISTENCE OBLIGATION IS NOW DISCHARGED BY THE PRODUCER.** `Z_BUILD.md`
  requirement 3 asks for "both same-run internal fixed-seed CV vectors and the predicate in the
  throw producer", and the combine persisted `hCvExecution0`, `hCvExecution1` and
  `hCvSupportMask` with `cv_support_predicate = "x_cv > 0"`, bound by `cv_code_revision`,
  `cv_producer_file` and `cv_producer_sha256`
  (`dbf423052e23854d61e8c420ad33a4ec33eae36edc215f8779119456d1cee884`).
  `n_cv_executions = 2`; the two vectors are **NOT bitwise identical** (max abs difference
  2.584e-51, relative L2 over the support 4.452e-14), which is what distinguishes two executions
  from one result written twice. The mask equals `x_cv > 0` recomputed from the persisted CV
  elementwise, and its sum is 10694 = `n_cv_support`. `fixed_seed_null_norm = 1.430183e-50`
  against the producer's 1e-12 tolerance.
  **`B`, `S`, `B <= S` and `epsilon` in `[B, S]` remain UNAPPROVED — the persistence half is
  discharged, the approval half is not, and no tolerance was invented here.**
- **Invalid-ratio handling, preserved and unchanged** (tallied over exactly this campaign's 61
  producer logs, 61-of-61 positive control): 897 `[ratio][WARN]` lines across 45 of 61 tasks, in
  two distinct policies. (A) non-finite or `<= 0` ratios replaced with **neutral ratio 1** on 9
  physical operands — `LowQ2:+1` 576/437/437, `HighQ2:+1` 117/94/94, `MFP_N:-1` 1/1/1 — worst
  576/32,849,103. (B) clipping to `(0.01, 100.0)` on flux universes 9/41/57/73 and the same three
  knobs, worst 387/32,849,103. **Rarity is not validation**; the neutral-1 substitution is a
  policy choice whose scientific justification is a separate decision and was not taken here.
- **Measured construction scalars** (the producer's own, non-quotable): `sqrt_tr_unified`
  4.443674e-38, `sqrt_tr_block` 3.750055e-38, ratio 1.185; per-bin sigma ratio unified/block
  median 0.919; `joint_mean_shift_norm` 1.878697e-38.
- **Accounting** (`r5_meter measure`, 2026-09-14T23:00:43Z): CPU 95.7617 / 500, GPU 0.1439 / 500,
  no stop fired. This campaign drew ~77.0 CPU task-hours of the 393.5 authorized — block 30.321 h
  (21 tasks), run 45.871 h (40 tasks), combine 0.818 h.

**Nothing here is quotable, nothing is promoted, no covariance is adopted, and no significance is
authorized.** The campaign establishes that the operands EXIST and are BOUND; the scientific
criteria in `Z_BUILD.md`'s remaining requirements are untouched by it.

### 2026-09-14 — Stage-1 assembly/spectrum pilot implementation (code and tests only)

Authorized by Joseph as implementation, synthetic tests and independent review; **no cluster
allocation, retry, grading, adoption or publication use.** Four added files, no existing module
changed:

- `nd-unfolding/z_null_bridge.py` — transcribes the producer's ROOT null operands into the
  versioned NPZ slab `z_build` requires, reusing `z_build.Source` (digest-bound read),
  `z_receipt.persist_null_operands` (write), `z_statistics.support_mask` (predicate recomputation)
  and `z_build_path.preservation_guard` (overwrite refusal). It transcribes and never repairs: the
  mask's values must be exactly `{0, 1}` BEFORE any bool cast, the predicate is recomputed and must
  agree, the producer's four recorded counts are checked against the arrays, and the slab carries
  the **PRODUCER's** code identity rather than the assembling revision.
- `nd-unfolding/z_pilot.py` — digest-bound manifest builder, spectrum persistence, and an
  exit-aware runner. Exit 2 means "construction complete, science NON-PASSING" and is **preserved,
  never converted to 0**; it is also not accepted as proof of anything until both products, both
  receipts and the null slab exist and each receipt's recorded product digest matches the file
  beside it, matched **by path** rather than by position.
- `nd-unfolding/z_pilot_manifest_cli.py` — the manifest entry point, separate so declaring inputs
  and consuming them are not one invocation.
- `nd-unfolding/sbatch_z_pilot_5d.sh` — guarded launcher: explicit `--time`/`--mem`/
  `--cpus-per-task`, `#SBATCH --no-requeue` (safe here because this launcher is new and unshared,
  unlike the four precursor launchers), the existing env preflight/pathcheck/source-manifest/
  env-provenance closure, a fresh-output directory that **refuses rather than cleans**, and a
  receipt-last check performed against the filesystem after the exit code.
- `nd-unfolding/tests/test_z_pilot.py` — 40 controls passing under the repository default
  interpreter plus 4 PyROOT-gated ROOT round-trip controls. **Quote the interpreter with the
  count**: the 4 gated controls SKIP without PyROOT and were run separately under
  ROOT 6.28/12 / Python 3.11.14 on Perlmutter (23 of 23 OK in that class selection).
  Three mutants were introduced and each was killed by its intended control: deleting the
  `{0, 1}` mask-value check, converting exit 2 to 0, and matching a receipt digest by first-found
  instead of by path.

The spectrum is **reported, never clipped, floored or regularized**, and it is a deliberate second
independent `eigvalsh` on the closed artifact rather than a harvest of the PSD gate's internal
decomposition — the cost is priced in the execution request, per `Z_BUILD.md` requirement 8.
`z_assembly.gate_symmetry_psd` keeps sole ownership of the PSD verdict.

**INDEPENDENT REVIEW, 2026-09-14: three blockers, five should-fixes, all landed.** The reviewer
verified the "no pre-existing module modified" claim independently (`git diff --numstat`: 9 files,
all 4 deletions in `Z_BUILD.md`) and killed 11 of 14 mutants. The three that SURVIVED were all
launcher-side and all real:

1. **The job exited 0 for a NON-PASSING construction.** The script's last statement was an `echo`,
   so `sacct` would record `COMPLETED 0:0`. `z_pilot.py` takes care to preserve 2 and the launcher
   discarded it at the last hop — worse than never preserving it, because the inner discipline made
   the outer artifact look trustworthy. Fixed with `exit "$PILOT_RC"`. The guard test asserted
   `"exit 0" not in text`, a SPELLING check blind to falling off the end; it is replaced by one
   that executes the launcher's own `case` block, which also kills a `PILOT_RC=0`-inside-the-arm
   mutant that survived the first repair.
2. **`--no-requeue` was satisfied by its own prose comment**, so deleting the real `#SBATCH`
   directive passed. Now anchored on the directive line, with a negative control proving the
   comment alone does not satisfy it.
3. **The fresh-output guard asserted its MESSAGE, not its predicate**, so replacing the predicate
   with `[ -e /nonexistent-sentinel ]` passed. Now executed as a fragment against five cases:
   empty, non-empty, a regular file, an unlistable directory, and a dangling symlink.

Should-fixes landed: exact `TNamed` class check; 40-hex producer revision (it had a weaker standard
than the assembling revision); `OMP_NUM_THREADS` cap (measured 0.480 s vs 4.248 s at n=2800, ~9×);
`ls` status read directly instead of `2>/dev/null`; the guard's CANNOT-LOOK exit 2 distinguished
from the pilot's completion 2 by requiring the receipt; `json.loads` on a receipt wrapped so a torn
file raises `ZContractError` rather than escaping; the bridge record written atomically behind the
preservation guard; and scope item 7 enforced in code for the first time.

**THE LAUNCHER-COUNT RATCHET FIRED, AND MY FIRST READING OF IT WAS WRONG.** I reported that the
count was "still 217 before and after, so the new launcher does not enter that population" — I had
compared the wrong assertion. Measured properly: at `e09513d8` `SubstitutionFenceS1` fails
`217 != 216` (the standing total); at the first pilot commit it failed `199 != 198`, a DIFFERENT
assertion, because `sbatch_z_pilot_5d.sh` landed in the unclassified remainder. The ratchet exists
for exactly that event, and leaving it would have **masked** the standing finding behind a new one.
Classified rather than incremented: the pilot is not `hooked` (that set is closed at the seven
driver legs plus declared consumers), and not `fenced` (nine frozen substitution hazards; the pilot
writes only into a refusing fresh namespace and never a canonical product), so `neither` at 199 is
the honest bucket, pinned with a positive membership assertion so a count that moved for the wrong
reason cannot pass. **The total pin is deliberately left at 216**: it is a standing finding, not
this change's to close, and the arithmetic is recorded instead — 216 pinned + 1 pre-existing and
unexplained + 1 this pilot = 218.

Suites after the fixes: `test_z_pilot.py` 50 passed / 4 skipped (default `python3`); 29 of 29 OK
under ROOT 6.28/12 / Python 3.11.14 on Perlmutter; all Z suites 276 passed / 7 skipped;
`test_uq_remediation` 3 failed / 232 passed — the same three test IDs as at `e09513d8`.

### 2026-09-17 — the Z assembly/spectrum pilot RAN. Job `58454524`: construction COMPLETE, science NON-PASSING, adoption WITHHELD

**CLOSED as completed construction. Not a validation, not a grade, not an adoption.** Authorized by
Joseph as one fourth pilot attempt at ≤1.5 CPU task-hours on the reviewed `fb9ec356` deployment; the
authorization is **consumed** and **no replacement submission is authorized or sought.**

**Judge this by the artifact and receipt contract, not by `sacct`.** `sacct` labels any nonzero exit
`FAILED`, and **2 is this CLI's completion code** — `z_build.py` returns 1 for failed, 2 for
"completed, non-passing", and 0 only for `--help`. The guard's CANNOT-LOOK exit is also 2, which is
why the pilot's own validator additionally **requires the receipt** before reading 2 as completion.

```
58454524 | z_pilot5d | ExitCode 2:0 | ElapsedRaw 1037 s | AllocCPUS 36 | nid004093
         | 2026-09-17T00:21:56 -> 00:39:13 | build_seconds 760.767
```

**Evidence route (all preserved):** `/pscratch/sd/j/josephrb/zpilot-20260916/outcome-58454524/` —
both logs, `submission-a5.txt` with the exact command and exported settings, `scontrol-a5.txt`,
`source-manifest-a5.json`, `env-provenance-a5.json`, all four guard inventory records under
`inv-a5/`, every receipt, `product-digests.txt`, `r5-receipt-20260917.json`, and
`sacct-all-nine.txt`. Products remain in place at
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/`.

#### The contract, re-checked 2026-09-17 against the files

- **Products, digests re-measured on the cluster today and identical to the receipts:** `z-cv.npz`
  **890,500,272 B** `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`; `z-mean.npz`
  **890,383,062 B** `61b7a4939bd40459452e232d4a5cec3c0b19ad7a21715452f7bb3bc9e0c72dd2`; `z-null.npz`
  **190,817 B** `cb82fc3285c981b91625530d48c14ff5554db5154db298a3144a57520633d77e`.
- **The pilot receipt names 5 artifacts and every recorded digest re-measures — 5 of 5 MATCH.** It
  names five and not six because **a receipt cannot digest itself**. The two build-receipt digests
  (`9f8f91d9be69d767…`, `5bdc9a1830dc183a…`) were re-computed again from the preserved copies during
  this close-out: **2 of 2 MATCH**.
- **The output directory holds ten files, not six** — the six the contract covers plus
  `bridge.json`, `z-manifest.json`, `z-provenance.json` and `z-null-source.npz` (189,794 B,
  `2ac9d087…`, written by the **bridge**, distinct from the build's `z-null.npz`). Stated because
  "six artifacts" is the contract's population, not the directory's.
- **Each build receipt describes the file beside it**: two matching path entries per product,
  digests agree, matched **by path** and not by position.
- **RECEIPT-LAST holds**, visible in the mtimes: `z-cv` 463 → `z-mean` 492 → `z-null` 585 → both
  build receipts 681 → pilot receipt 749 (seconds into the job).
- `construction_status` **CHECKED**; `scientific_acceptance` **NON-PASSING**; `adoptable` **false**;
  `build_returncode` **2**; `notes.input_kind` **real**; `revisions_distinct` **true** with producer
  `e09513d842ad3acc1964c1af740696f02eaed7d9` and assembling
  `fb9ec3560fd6d62295dffc81b5694c9e26667d5b` — the two roles did not collapse.
- **Deployment parity** at `zdeploy-fb9ec356`: 895 tracked files, listing sha256
  `f2333fb32876363d12c2c5aebfe50e2a986504845affd5721f4c04fedee23e61`, `dirty 0`, **15 of 15
  CURRENT**; `code_identity.worktree_files_differing_from_revision` empty; 15 import-closure digests.

#### Both harness repairs are confirmed on real inputs at production scale

**The `git show --no-ext-diff` repair.** Attempt 3 (`58358282`) died with the depth-1 `z_build`
guard record reading `refused:launch-unmodelled-launch-grammar`, `offending_flag: git show without
--no-ext-diff`. That same record is now clean. All four guarded processes:

```
depth=0  z_pilot_manifest_cli.py   REPOSITORY-ORIGINS-INSPECTED  launch_refusal None  checked=219
depth=0  z_null_bridge.py          REPOSITORY-ORIGINS-INSPECTED  launch_refusal None  checked=219
depth=1  z_build.py                REPOSITORY-ORIGINS-INSPECTED  launch_refusal None  checked=234
depth=0  z_pilot.py                REPOSITORY-ORIGINS-INSPECTED  launch_refusal None  checked=138
```

Every record: `expect_root /pscratch/sd/j/josephrb/zdeploy-fb9ec356`,
**`repo_origins_outside_expect_root` empty (0)**, `violation None`, `guard_installed true`,
`shell restricted`. **OI-136 containment held on all four**, and `z_pilot.py`'s `outcome` is
`child-systemexit:2` — the guard observed and propagated the completion code rather than masking it.
(Read the containment from these records, **not** from the `15 of 15 CURRENT` parity line: parity
can be true and blind when an earlier import owns `sys.path[0]`. The guard's `expect_root` check is
the evidence.)

**The stderr-preservation repair, and it earned its place.** The child's stderr is preserved intact:
`chars 2424`, `abridged false`, `sha256 9c780d4101c4c3cea5f12cbe589b4ddfcd1873b2575788242c49841bb879519c`
(the 4000-char cap did not engage). It carries nine ROOT `TInterpreter::ReadRootmapFile` warnings —
the in-situ evidence that the **real** PyROOT environment was the one used — **and the depth-1
`z_build` guard's own `[oi136] inventory: checked=234 repo_origin_count=12 outside_expect_root=0`
line, which appears nowhere else.** Without this repair that line would have been discarded with the
child's stderr, and the depth-1 containment evidence would have had to be taken from the JSONL
alone.

#### Measurements — RECORDED, NOT GRADED

**PSD gate, `fb9ec356:nd-unfolding/z_assembly.py:512-561`.** Fail-closed and it returns no boolean:
`require()` raises `ZContractError`, so a populated `G4_symmetry_psd` block **is** the pass. The
criterion is scale-free by deliberate design (the clamp was deleted): `asym <= rtol` and
`lam_min >= -rtol * lam_max`, via `eigvalsh` on `0.5*(C+Cᵀ)`. `rtol = IDENTITY_RTOL = 1e-9`
(`fb9ec356:nd-unfolding/z_contract.py:125`) and it is **arithmetic, not scientific** —
`z_assembly.py:49-51`: *"NO ACCEPTANCE BOUNDARY APPEARS IN THIS MODULE."*

| object | `lambda_min` | `lambda_max` | `neg_fraction_of_max` | `rel_asymmetry` | `rtol` |
|---|---|---|---|---|---|
| cv (inflated) | `-1.2750516323643892e-90` | `2.229223998752954e-75` | `5.719710684424999e-16` | `2.1641333629718972e-16` | `1e-09` |
| mean (inflated) | `-5.146659106575015e-91` | `1.9272637183054823e-75` | `2.670448811800462e-16` | `1.0927533323421377e-16` | `1e-09` |
| block-sum reference | `-4.6860865778129674e-91` | `1.205970554862754e-75` | `3.885738800933054e-16` | `0.0` | `1e-09` |

The cv object's negative excursion is **`5.72e-16` of `lambda_max` — `1.75e6`× inside the
tolerance.** **No clipping, flooring, regularization or replacement threshold was applied, and none
is proposed here.**

**Spectra, persisted separately by the pilot** as a deliberate *second independent* `eigvalsh` on
the closed artifact, each bound to its product's digest, `verdict: None` in both because
`gate_symmetry_psd` keeps sole ownership of the PSD decision: cv `n_negative` **5214**, 33.503 s;
mean `n_negative` **5215**, 16.516 s. **A count is not the gate's criterion** — the gate is on the
extremal eigenvalue relative to `lambda_max` — and nothing grades these counts.

**Other gates:** `G1_closure_identity` `max_rel_residual` **0.0**; `G3_g_reconstruction`
`max_rel_diff` **0.0**; `active_total_eq_sum5` **0.0**; `G2_g_domain` `g_min 1.0`, `g_median
1.0473565738188244`, `g_max 17.653141714565614`, `n_gt_one 6528`, `n_pinned 0`;
`G3R_raw_operand_reconstruction` **`discriminating: true`** (`n_separated 6527`,
`n_saturated_v_uni_below_v_blk 4166`, `n_shift_below_tolerance 1`, `max_separation
0.6270761129833259`), `n_clipped_blocksum 0`, `n_clipped_unified 0`; `G5_band_partition` exhaustive,
`5 + 13 + 27 = 45`. Inflation: `sqrt_tr_before 4.3576468306957044e-38` →
`sqrt_tr_after 5.674200780785609e-38`, ratio **1.302125**.

**Null, as the build reconstructed it:** `r_null 4.4520002137582904e-14`,
`num_norm 1.4301832847122437e-50`, `cv_norm 3.2124510692799616e-37`, `n_rep 10694` — **identical to
the precursor's own record at § 2026-09-14 to every digit**, which is the expected result, not an
independent confirmation: `z-null.npz` transcribes that campaign's two persisted CV vectors. New
here is the **per-bin** statistic `max_i |Δ_i/x_i|` = **`1.7552716191735518e-12`** at
`argmax_grid_index 31499`, flagged `grades_nothing: true` by its own writer. `null.assessment`
records `verdict` **NOT ASSESSABLE**, `reject_conditions ["4c", "11"]`; the receipt's `outcome` is
`assessable: false`, `reject_conditions ["4c"]`, reason *"Scientific criteria and real-input
evidence remain unresolved."*

**Two named non-checks inside an otherwise-closed gate set, recorded and not repaired:**
`G3R.stored_cv_cross_checked` **false** (`stored_cv_deviation`, `stored_cv_discriminating` both
`null`), and `null.declared_cv_crosscheck.external_crosscheck_status` **UNPERFORMED**, `verdict
UNRESOLVED` — its own stated reason being that the compared object is this build's declared
`central` source, not an external production ROOT. Neither is the precursor persistence question.

**A digest that differs for a good reason, stated so it is not read as a disagreement:** the ROOT
object `hCvSupportMask` digests `ea0059ed…` while the persisted `sha256_support_mask` is
`eed021e9…`. The bridge **recomputes** the predicate and stores its own array; agreement is
established by the four counts matching exactly (`n_cv_bins_total 65856`, `n_cv_support 10694`,
`n_cv_genuine_zero 55162`, `n_cv_negative 0`, `recorded == measured`), not by digest equality of two
different representations.

#### Why NON-PASSING, and what the fourteen-key list does and does not mean

`notes.remaining_requirements` is a **fixed fourteen-key list** emitted unconditionally, so
"fourteen remain" is not a measurement. The reconciliation — completed subrequirements, unresolved
scientific criteria, independent verification, and work needing new compute, plus `authorization`
which belongs to none of them — is at
**`docs/orchestration/DECISION-SUPPORT-20260916-z-to-adopted-5d-covariance.md` §10**, with the
recommended next action at **§11**. In one line: `withheld_boundaries` carries four entries, all
`status: WITHHELD`, `value: null` — `null_epsilon`, `cause3_agg`, `cause3_med`, `cause3_corr` — and
the `null` requirement's own text is *"Persist both internal same-run fixed-seed CVs and predicate
at throw creation; approve B, S, B <= S and epsilon in [B, S] before production."* **The
persistence half was already discharged; the approval half is untouched by construction**, and
`cause5` says it outright: *"construction alone does not dispose of this cause."*

#### Resource sizing — one figure was wrong and it is the one that mattered

```
58454524.batch   MaxRSS 52146232K = 49.73 GiB   ReqMem 64G   ->  77.7% of the request
                 ElapsedRaw 1037 s of a 5400 s wall          ->  19.2% of the wall
                 TotalCPU 02:17:02 across AllocCPUS 36
```

The decision-support record's §4 predicted *"peak memory a few GB … 64G have large margin"*. The
**wall** had large margin; the **memory had 22.3% headroom**, against a prediction low by more than
an order of magnitude. Runtime went the other way: `eigvalsh` at n=10694 was predicted ~59 s per
variant and measured **33.503 s** and **16.516 s**. Any future sizing starts from **49.73 GiB
measured**. `MaxRSS` is a **step-level** field: `sacct -X`, or any JobName filter that drops the
`.batch` row, returns it empty and reads as "not recorded".

#### The nine-job census for this campaign, preserved (`sacct-all-nine.txt`)

| JobID | name | State | Exit | Elapsed | stage reached |
|---|---|---|---|---|---|
| 58347943 | z_pilot5d | FAILED | 1:0 | 4 s | operand guards voided by an apostrophe inside a `${VAR:?…}` message |
| 58354056 | z_pilot5d | FAILED | 3:0 | 13 s | input declaration |
| 58356573 | z_pilot5d | FAILED | 12:0 | 160 s | input declaration |
| 58358282 | z_pilot5d | FAILED | 1:0 | 162 s | **`z_build` refused at launch** — `git show` without `--no-ext-diff` |
| 58398465 | z_e2e_validate | FAILED | 28:0 | 79 s | small-fixture validation; `copy2` preserved `r--r-----`, 7 of 9 controls passed |
| 58403382 | z_e2e_validate | COMPLETED | 0:0 | 95 s | **small-fixture validation PASSED**, all controls |
| 58403491 | z_pilot5d | FAILED | 0:53 | 6 s | **before the script started** — relative `--output` against a read-only CWD, `.batch` CANCELLED |
| 58403564 | z_pilot5d | FAILED | 3:0 | 8 s | `mnv_env_pathcheck` refused five `$HOME` PATH entries |
| **58454524** | z_pilot5d | FAILED | **2:0** | **1037 s** | **completed construction, NON-PASSING science** |

`58403491` is recorded as a **consumed attempt**: Joseph ruled that *"the script never started"* is
not an automatic exception to the no-retry condition. Five submission-side and harness defects were
found and fixed between `58403564` and `58454524` — an IFS-contaminated allowlist loop, an allowlist
that deferred to the environment, an `errexit` enabled after the `sbatch` call that would have lost
the record of a consumed authorization, and two assemble-versus-record ordering faults.

#### Accounting, measured 2026-09-17T07:41:55Z

```
cpu_task_hours  96.196111 / 500    headroom 403.803889
gpu_task_hours  10.210833 / 500    fired: none      58454524 in metered_task_ids
```

The pilot drew **1037 s = 0.288** of its authorized **1.5** CPU task-hours. `stop_date_utc`
**2026-09-30T00:00:00Z — 13 days.** Storage, per-user and not the filesystem's:
**pscratch 16.02 / 20.00 TiB = 80.1%** (`showquota`), inodes 380.67 K / 10.00 M; the 1.7 GB of
products sit inside that. **An earlier report of "pscratch 67%" was `df` on the shared Lustre mount
— the wrong denominator, and it understated the constraint.**

#### No `VALIDATION_LEDGER.md` row is created, deliberately

Nothing here is a verified-for-quotation number: `scientific_acceptance` is NON-PASSING,
`outcome.assessable` is false, and every boundary that would grade any of it is WITHHELD. This
entry and the receipts are the route; a ledger row would read as validation. **Nothing here is
quotable, promoted, adopted or projected. `B`, `S` and `ε` remain open. Successful construction
authorizes no grading, adoption or publication use.**

### 2026-09-25 — s5c campaign (OI-190): pilots, F1 screen, frozen contract, construction and Tier-S launch

Authority `docs/orchestration/AUTHORIZATION-20260924-scalar5d-campaign-activation.md`; index
`docs/orchestration/CAMPAIGN-s5c-20260924-index.md`; all jobs admitted and priced by
`nd-unfolding/s5c_meter.py` (ledger `/pscratch/sd/j/josephrb/s5c-20260924/ledger/admissions.jsonl`).

- `58855902` (xfer): D3 HPSS backup of the nine sole-copy objects, restore SHA-256 9/9 —
  `docs/orchestration/RECEIPT-20260925-d3-hpss-backup-of-nine-sole-copy-objects.md`.
- `58856439` (interactive, 0.789 CPU node-h): pilots P1 (18 unfolds), P2 (background dump, exact
  reproduction of the npz purity weights), P3/P4 (three end-to-end pseudo-experiments), the
  projection reproduction and the development-MC partition scans. `58856170`, `58856255`,
  `58856256` were batch submissions cancelled while pending (queue depth), zero spend.
- F1 two-member screen and P1: `VALIDATION_LEDGER.md` `VL146`–`VL148`.
- Contract frozen at `c29dde25`; feasibility receipt
  `docs/orchestration/FEASIBILITY-20260925-s5c-scalar5d-measurement-and-inference.md`.
- `58857016` (interactive): Tier-S σ bootstrap, 200 replicas. `58857523` (interactive): F2
  construction, real-data bootstrap and first 40 vertical universes. `58857600` (cancelled 15 min
  in: detector arm without `--closure-slack 5000`), `58857791` (interactive GPU node): F2 detector
  weight-only bands and matched CV.

### 2026-09-25 (later) — s5c campaign (OI-190): Tier-S futility FAIL, final disposition

- Reviews: round 2 (`4bdfa75e`) confirmed the purity-background bias and found amendment 3's
  allowance inflating every interval → amendment 4 (bias correction, `95d0e87c`, frozen with 22
  unread validation products on disk). Round 3 (`f511dcd6`): the evaluator is correct, but a pass
  would cover only the corrected construction and development data predict failure →
  `docs/orchestration/state/s5c/review-3-disposition.json`; construction beyond running
  allocations HELD, all slots to validation lines 0-119.
- Unattended lanes: `nd-unfolding/s5c_queue.sh`, `s5c_launch.sh`, `s5c_valid_next.sh` (claims),
  `s5c_futility_watch.sh`; queues under `docs/orchestration/state/s5c/queues/`. Two defects found
  and fixed in flight: GPU-node steps inherited all 4 GPUs (serialized, `3683a4af`); the claim
  lock was inherited by the launched steps runner (CPU lane blocked 46 min, `83b16c16`).
- Validation allocations: `58861566`, `58862360`, `58863216`, `58865811`, then `58868867`,
  `58870274`, `58872289` (cancelled by the futility watcher at 17:40:55Z). Construction:
  `58857523` (bootstrap 100/100, sweep lines 0-39), `58857791` (detector lines 0-4).
- **Futility look 17:40:55Z: FAIL** — `VALIDATION_LEDGER.md` `VL150`,
  `docs/orchestration/OUTCOME-20260925-s5c-tier-s-futility-fail.md`; independently reproduced
  (review round 4, `83b16c16`), which also found the q3-truth sentinel defect (fixed in
  `s5c_pseudo.py`, `KNOWN_ISSUES.md` 76).
- Spend (meter, 17:49Z): 20.09 CPU + 9.79 GPU node-h (39.2 A100-h) of the 500/500 envelope;
  `docs/orchestration/state/s5c/tier_s/meter-measure-20260925T1749Z.json`. No s5c job remains.

