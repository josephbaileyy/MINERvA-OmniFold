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
