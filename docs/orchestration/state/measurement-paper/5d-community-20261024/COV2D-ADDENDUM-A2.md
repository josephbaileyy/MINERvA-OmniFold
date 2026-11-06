# COV2D addendum A2: staged private inputs, guards that record their values, and AR23's rerun

**By** the `cov2d` session, 2026-11-05, for the director to audit and bind. It is written under:
- [`COV2D-DECLARATION.md`](COV2D-DECLARATION.md);
- [`COV2D-BINDING-1.md`](COV2D-BINDING-1.md) and [`COV2D-BINDING-1-A1.md`](COV2D-BINDING-1-A1.md);
- [`COV2D-AMENDMENT-1.md`](COV2D-AMENDMENT-1.md), bound by [`COV2D-BINDING-2.md`](COV2D-BINDING-2.md);
- Joseph's ruling, [`DECISION-20261105-joseph-ar23-stop-external-and-765-phrases.md`](../../../DECISION-20261105-joseph-ar23-stop-external-and-765-phrases.md)
  §1, and the director's rulings of 2026-11-05 restated below.

**MEASURES:** nothing; it states code and rules. **CANNOT AUTHORIZE:** any job before the director binds it. After that,
first a cluster-environment test run, then AR23's pseudo-data rerun, each connect's sha256 sent to the director first.

**The STOP count is two:**
- **#1:** CONTROL-2A, 2026-11-03.
- **#2:** AR23's step A atime guard, ruled externally caused by Joseph, 2026-11-05, for that event only.

**A third STOP of any kind, or any guard firing on a private (staged) file, ends (c),** with no further
reclassification.

## 1. What A2 binds

The code commit `94544e0b7a29f31d82ddd7c3c92485e703518117`, the unfreeze after stage 1's first attempt (§9), on main's `77d76cfc`. It carries A2 as bound at `cf533377` (code `038f28e8`, on `928204b0` and `a2005b54`, on main's `a548d44c` with the merged #797), plus exactly the two unfrozen changes and the TMPDIR reset. Its blobs are in §10. Against M
(`cb31611c`), it changes:
- `cov2d.py`;
- `cov2d_pseudo.py` (step A);
- `cov2d_pseudo_write.py` (step B);
- `jobs/cov2d_env.sh`, `jobs/cov2d_job.sbatch`, `jobs/cov2d_pseudo.sbatch`, `jobs/cov2d_submit.sh` and
  `jobs/cov2d_jobs.py`;
- their tests, and a new test helper, `tests/noatime_emu.py`.

It also carries #797's `tests/test_cov2d_blocks.py` (blob `e3682f8d`, ruling (i)). The deploy is a fresh clean checkout
at the commit binding A2 names.

## 2. Item 1: AR23 reruns into a new directory, at 04:00:00

- **One map, used by both job scripts:** `pseudo_dir` in `cov2d_env.sh` sends AR23 to `$O/pseudo/AR23-a2` and every
  other truth to `$O/pseudo/<truth>`.
  - `cov2d_pseudo.sbatch` writes `P=$(pseudo_dir "$TRUTH")`.
  - `cov2d_job.sbatch` reads `D=$(pseudo_dir "${DATA_TRUTH:-$TRUTH}")/b`.
  - The first run's outputs stay in `$O/pseudo/AR23/a`.
  - The sbatch still refuses an existing output directory ("a pseudo-data rerun is a new connect").
  - G18's directory is unchanged.
- **The limit:** `cov2d_jobs.PSEUDO_LIMITS = {"G18": "03:00:00", "AR23": "04:00:00"}` (the director's ruling). It is
  the one source for the submit script's `--time`, the job's own `scontrol` TimeLimit check and the gate's limits.
  - The gate holds 4.0 node-h at submission.
  - The charge so far is 4.36 node-h: G18 2.41, pilot 0.75, AR23's first run 1.20.
  - Expected: about 2.7 node-h. That is G18's 2.41 plus `$UNI`'s staging. The figure is mine, not a measurement.
- **`order()`** still reads AR23's PASS record at `fd/receipts-cov2d/pseudo/AR23/pseudo_b.json`. The rerun's record
  goes there, after the director has read it. The failed run's receipt sits in `pseudo/AR23-attempt1/` (#799).
- **`order()` now requires `pins_checked: true` in each pseudo-data PASS record** (the audit's L1, ruled in). A record
  written in tests' unpinned mode opens nothing. The pilot readout's record is exempt from this field, for two reasons:
  - `cov2d_pilot` has no unpinned mode, since it always copies part B's references at their pins;
  - its committed record (`b59ffa2d…`) predates the field, and a committed record is never hand-edited.

  `test_the_writers_record_is_what_order_admits` now runs the real writer with its pins checked, against the fixture's
  own digests: `order()` admits the record, and refuses it with `pins_checked: false`. A record without the field is
  refused too.
- **A pinned step B refuses an unpinned step A** (the audit's re-check, L1's gap, ruled in). Otherwise B's record could
  say `pins_checked: true` over an unpinned A. The refusal comes before B's work.
- **Binding 2's records are admitted at A2's deploy by a declared table** (the audit's N1, the director's rule R1).
  - `cov2d_jobs.PRIOR_RECORDS` holds exactly two entries, both from binding 2: G18's pseudo-data record (`cb31611c`,
    `230f6918…`) and the pilot record (`cb31611c`, `b59ffa2d…`).
  - `order()` admits a record whose M is the deploy's M. Otherwise it admits a record only if its path, its M and the
    sha256 of its exact bytes on origin/main all match that path's entry. The order CLI hashes what `git show` returns.
  - Everything else is refused, including AR23 at `cb31611c`: its rerun's record must carry A2's M.
  - **Without this,** no single M passed the sequence: A2's deploy refused binding 2's records, and a deploy at
    `cb31611c` ran the code without staging.

## 3. Item 2: every shared input the guards watch is staged first

**What is staged.** Each step stages its shared inputs into its own `stage/` with `cov2d.stage_copy`, before its guard's
first reading:
- step A into `$P/a/stage`;
- step B into `$P/b/stage`.

| step | input | shared original | pin |
|---|---|---|---|
| A | `$UNI` (171 GB) | `$A/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root` | `220c479e…` (part B's `preflight/inputs.stat:2`) |
| A | the CV | the CFS original (`cov2d_writer.CV`) | `43f8cc16…` (RE2-DECLARATION.md:145) |
| A | the truth's ratio | F1's prep (`cov2d_receipt.PREP`/`bridged/…`) | F1's committed digest (`fd_1b_toys.committed_ratio_sha256`) |
| A | the flux constraint | `MINERvA101/…/sorted_NuEConstraint_FHC_RHC_IMD.txt` | `e38ad7d2…` (`cov2d.CONSTRAINT_SHA256`) |
| B | E_R | part B's `out/ER/xsec.root` | `a5c13fc3…` |
| B | the MC file | `$A/…/baseline_flux/runEventLoopMC_MEFHC.root` | `d40aea69…` |
| B | the flux-universe file | `$A/…/baseline_flux/flux_integral_universes_MEFHC.root` | `5eecae84…` |

**How `stage_copy` works.**
- It reads the original once, through O_NOATIME, hashing as it writes the copy.
- It refuses, deleting the copy, unless the hash is the pin.
- It makes the copy read-only.
- It records the copy's size, mtime and inode, and the original's atime before and after the copy.
- Each step's record carries all of this under `staged`, with `shared_atime_moved` listing any original whose atime
  moved.

**The shared-atime check is a record, not a stop** (the director's ruling on design point 2). The reasoning:
- Our read is O_NOATIME, and `os.open` raises (EPERM) rather than drop the flag, so a refused flag fails loudly.
- Lazy propagation of another process's earlier read, the mechanism inferred for STOP #2, could move a shared atime
  during staging with no read of ours. Under the third-STOP rule, a guard there would end (c) on someone else's read.
- It is printed (`SHARED-ATIME (a record, not a stop) …`) and reported.

**The quota check, at submission** (the director's option (c), after stage 1's first attempt).
- **Where it runs:** `cov2d_submit.sh`'s gate (`cov2d_jobs.py gate`), on the login node, just before a pseudo-data
  job's `sbatch`.
- **What it checks:** it stats the seven shared inputs of §3 (`cov2d_jobs.staged_inputs`). It does not read them, so no
  atime moves. It then requires pscratch's headroom (limit − used, from NERSC's `showquota`) to be at least
  2 × their bytes (`cov2d.STAGE_HEADROOM`).
- **On failure:** if the headroom is short, or the quota can't be read, the gate refuses. Its JSON records
  `staged_bytes` and `quota_problem`, the connect stops, and the refusal is reported to the director.
- An unfold job's gate does not read the quota.
- **Why not in the job:** stage 1, attempt 1 measured `showquota` failing on a compute node. It calls GPFS's
  `mmlsquota`, which compute nodes lack (`fd/receipts-cov2d/a2/cluster_tests-attempt1/`). So step A no longer reads the
  quota at all, and it has no refusal path for it.
- The parser is tested on RE-2's own committed `showquota` row (`partb_readout/quota_before_cleanup.txt`).

**What reads what.**
- The jobs read only the copies, always through O_NOATIME.
- ROOT opens files plainly, so step B gives it a second, working copy in `$TMPDIR`, made from the staged copy through
  O_NOATIME. **No staged copy is ever opened plainly.** Without this, step B's guard would fire on every correct run.

**Deletion** (the director's ruling).
- After step B's PASS, `cov2d_jobs.py delete-staged` deletes each copy listed in `pseudo_a.json` and `pseudo_b.json`.
- It first checks each copy's size, mtime and inode against what staging recorded.
- It writes a B9-form row to `$P/deletions.tsv`, in RE-2's `deletions.tsv` columns: utc, path, sha256, size, mtime,
  inode, stat_match and condition.
- A copy whose stat differs is kept and ledgered "no".
- `$UNI`'s copy is deleted too, since no later job under A2 reads it. The universe jobs read the shared `$UNI`, as bound.
- If step A or B does not pass, the copies are kept for the director.

## 4. Item 3: both guards watch only the copies, and record both values

- **Step A** (`cov2d_pseudo.py`) and **step B** (`cov2d_pseudo_write.py`) read each staged copy's atime once it has
  settled (below), and again at the step's end. Both readings go into the record as epoch ns: `atime_ns = {path:
  {"before", "after"}}`, beside `atime_moved`. Any move STOPs.
- **Settling before the guard** (the audit's D2, ruled in). A private-file firing ends (c), and the evidence points to
  lazy atime on this Lustre. So:
  - `stage_copy` fsyncs each copy, then its directory, before any reading.
  - The guard's "before" is taken only when two readings of every copy's atime, `cov2d.SETTLE_WAIT` = 5 s apart, agree
    (`cov2d.settle_atime`, at most `SETTLE_TRIES` = 6 pairs, so about 30 s).
  - Every reading is recorded (`settle_atime_ns`).
  - If they never agree, the step writes its record with `verdict: REFUSED`, the reason and the readings, before any of
    its work, and exits 2. That is a refusal, not a STOP, since nothing has been graded.
  - **Tested** with a stand-in that moves the staged copies' atime between every pair of readings: both steps refuse,
    with SETTLE_TRIES + 1 readings recorded and no product. `settle_atime` itself is tested settling on its second pair,
    and never settling.
- **Tested in both directions,** in `test_cov2d_pseudo` and `test_cov2d_pseudo_write`:
  - **Silent on a clean run:** every staged copy has `before == after`, `atime_moved == []` and PASS.
  - **Fires on a plain read of a private copy:** a test reads one staged copy with plain `open()` mid-step, after the
    first reading. The verdict is STOP, `atime_moved` is exactly that copy, and its `after > before`.
- **Where each direction is shown.**
  - The fire direction is deterministic on both test filesystems: a fresh copy's first plain read moves atime (relatime),
    which I checked locally.
  - Silence on a clean run needs real O_NOATIME. On macOS, `tests/noatime_emu.py` emulates the flag for COV2D's four
    read helpers only, restoring the atime they leave. Plain reads are not emulated, so the fire test is unchanged.
  - On Linux nothing is emulated. **The cluster test run (§6) must show both directions running there, not skipped**
    (the director's ruling).

## 5. Item 4: the fence (the director routes it)

- No REF-G1 run before REF-G1's addendum A1 is bound.
- While a COV2D job runs, no lane runs code that plain-reads a COV2D-guarded input. With A2, the guards watch only
  private copies under `$O`. The shared originals of §3 still matter, though: they are what staging reads and records.

## 6. The order after A2 binds

1. **A cluster-environment test run at the A2 commit,** as binding 2's ruling 5. It must show `test_cov2d_pseudo`'s and
   `test_cov2d_pseudo_write`'s silent-on-clean and fire tests running, not skipped, in their environments.
   - It runs `cov2d.headroom_problem` on live `showquota` output on the login node, where the submission's check now
     runs. The audit's L2 compute-node check ran in attempt 1 and measured `showquota` failing there, which is why the
     check moved to submission.
   - Its connect sha goes to the director first.
2. **AR23's pseudo-data rerun** (`cov2d_submit.sh <deploy> M AR23 pseudo`, 04:00:00), its connect sha first.
   - On PASS, its record is committed at `order()`'s path after the director reads it.
   - A guard firing on a staged copy ends (c).
3. **Then the universe jobs and the bulk,** as bound in amendment 1 and binding 2, each connect's sha first. The unfold
   jobs are unchanged, except that AR23's read `$O/pseudo/AR23-a2/b`.

Each step proceeds only on the previous step's PASS record, and stops and reports on anything else (the director's
fixed conditional sequence).

**How outcomes classify** (the director's ruling on this section, 2026-11-05). It is binding because the declaration's
§6 (iii) makes the amendment's definitions binding, with a third STOP ending (c).
- **Refusals before any read or product are not STOPs:** an existing output directory, a quota short of 2× at
  submission (a refused gate, so no job is submitted), a dirty deploy. So is the settle refusal (§4), which comes before any of the step's work. Each is reported
  to the director.
- **A staged copy whose hash differs from its pin IS a STOP:** the declared input is not the pinned one.
  - `cov2d.stage_copy` raises `PinMismatch` and deletes the copy.
  - `cov2d.stage_all` turns that into the step's STOP, written into `pseudo_a.json` or `pseudo_b.json` before any
    product. The record's `verdict` is `STOP`, and its `off_pin` names the step, the input, its path and both digests
    (`sha256` and `pinned`). The stop text is "<step>: staged input <key> (<path>) is off its pin: sha256 … != pinned
    …".
  - The step exits 3, and the sbatch exits 5 or 6.
  - Tested in both steps with pins checked against a fixture that is not the pinned file, and in `stage_all`.
- **A guard verdict STOP on a private copy is a STOP.**
- **A crash, OOM, kill or time-out is INVALID** under §9.13. It isn't a STOP, but it comes to the director unrepaired,
  and any rerun needs the director's go.

## 7. Item 5: Lustre's atime settings

Receipts are in `fd/receipts-cov2d/a2/lustre/` (#799), from two probes on login02.
- `/pscratch`'s mount options carry no noatime, relatime, strictatime or lazytime option.
- The client (lctl 2.15.7.1) exposes no atime parameter in `llite` or `mdc`.
- The server-side policy, for example the MDT's `atime_diff`, cannot be read from a client.

So lazy propagation is consistent with what can be measured, but it was not measured.
<!-- absence-ok: states what a client-side probe can read, as the decision requires; not a claim that a result is absent -->

## 8. Item 6: the failed run's receipt

`fd/receipts-cov2d/pseudo/AR23-attempt1/` (#799) holds:
- `pseudo_a.json` (`9e581949…`), the job log, sacct and the connect, committed as is;
- a README stating STOP #2, the ruling and its scope, the guard and what it did not record, the inferred cause with its
  stat-only evidence, and what would falsify it.

## 9. The audit (coverage-5b-audit on #803, at 1b1ed6b5 and at 9575dd1d) and what changed

The auditor's report, its re-check and the director's rulings are copied verbatim in `fd/receipts-cov2d/a2/AUDIT-A2.md`.

| finding | change | tests | mutants (all REQUIRED) |
|---|---|---|---|
| D1: §6 as the ruling; a hash off its pin is a STOP, written mechanically | §6; `PinMismatch` and `stage_all`; both steps write the STOP record with `off_pin` | `test_a_staged_input_off_its_pin_is_a_stop` (steps A and B); `test_stage_all_stops_at_the_first_copy_off_its_pin` | "A2 a staged pin mismatch is a refusal, not a STOP"; "A2 step A off-pin STOP skipped"; "A2 step B off-pin STOP skipped"; "A2 D1 the off-pin STOP without its digests" |
| D2: settle before guarding | fsync of each copy and its directory; `settle_atime` (5 s, 6 pairs); `REFUSED` with the readings | `test_a_copy_whose_atime_will_not_settle_is_refused_before_the_work` (steps A and B); `test_settling` | "A2 D2 step A settle skipped"; "A2 D2 step B settle skipped"; "A2 D2 settle wait under 5 s"; "A2 D2 an unsettled reading accepted" |
| L1: `order()` requires `pins_checked: true` | pseudo-data records; the pilot record is exempt (§2) | `test_a_pseudo_record_without_its_pins_checked_opens_nothing`; the writer test with pins checked | "A2 L1 order ignores pins_checked" |
| L2: showquota on a compute node | the cluster test run's 1-minute allocation (§6), run in stage 1's attempt 1: `showquota` fails on a compute node, so the check moved to submission (below) | — | — |
| N1 (re-check, blocking): no single M passes the sequence | `PRIOR_RECORDS` (rule R1, §2); the order CLI hashes the committed bytes | `PriorRecords` (the sequence at A2's deploy on the real committed files; a record off its bytes or without digests; AR23 at binding 2's M; another record's bytes under AR23's path; the CLI on a real origin); the writer test's real sequence (binding 2's records plus this writer's record open the universes) | "N1 the prior records ignored"; "N1 a prior record admitted on its M alone"; "N1 a prior record admitted under any path"; "N1 the order CLI hashes nothing" |
| L1's gap (re-check): an unpinned A under a pinned B | step B refuses unless A's record says `pins_checked: true` | `test_a_pinned_step_b_refuses_an_unpinned_step_a` | "L1 step B ignores step A's pins" |

The fsync itself is not mutated, because no test can observe it.

**Stage 1, attempt 1 (FAILED, not a STOP; `fd/receipts-cov2d/a2/cluster_tests-attempt1/`), and the director's
unfreezing of exactly two things:**

| failure | change | tests | mutants (REQUIRED) |
|---|---|---|---|
| step A's fire test on Linux: the plain read fell in the copy's creation tick (inferred) | both fire tests sleep 0.25 s before the plain read; tests only, and the 5 s settle is unchanged | the two fire tests | — |
| `showquota` fails on a compute node | option (c): the quota check moves to the submission's gate on the login node; step A's call and its refusal are removed | `test_a_pseudo_submission_needs_twice_the_headroom`; `test_an_unfold_submission_reads_no_quota`; `test_staged_inputs_are_the_seven_shared_files` | "A2 the submission's quota check skipped"; "A2 the submission's quota verdict ignored" (replacing "A2 quota check skipped") |
| the a2quota job inherited a removed TMPDIR | both job scripts reset `TMPDIR` under `$O/tmp` right after sourcing the environment | — | — |

## 10. Tests, mutants and blobs

At `94544e0b`, in one local environment holding PyROOT, uproot and numpy (ROOT 6.28/12, uproot 5.6.9): **184 tests, 0 skipped, all pass** (`fd/receipts-cov2d/amendment/suites_94544e0b.txt`):
- step A 20, step B 17, blocks 26, null 5, scorer 12, readouts 12, jobs 44, pilot 13, cov2d 35.
- This local run used the macOS emulation of O_NOATIME (§4). The cluster run must show both directions on Linux.

**Mutants:** `fd/receipts-cov2d/amendment/mutation_amendment.py`, 92, **all killed**, harness exit 0 (`mutation_amendment.txt`). **39 are REQUIRED:**
- binding 2's 10;
- rulings (a) and (i)'s 2;
- A2's first 12, with "A2 quota check skipped" replaced by the submission's two quota mutants;
- the §6 ruling's 3, the first audit's 6, and the re-check's 5 (§9).

Each new mutant was also run alone first, all killed.

**Blobs at `94544e0b7a29f31d82ddd7c3c92485e703518117`**, every file under `2d-unfolding/cov2d`. The 14 files that differ from M (`cb31611c`) are marked: A2's 13, plus #797's `test_cov2d_blocks.py` (ruling (i)).

| file | blob | |
|---|---|---|
| `2d-unfolding/cov2d/cov2d.py` | `9e510e89e1b731ab5899fb1e4e85089b7442f303` | changed since M |
| `2d-unfolding/cov2d/cov2d_blocks.py` | `b9e63a3827e44c31a529f8d92482b7d7969d8223` |  |
| `2d-unfolding/cov2d/cov2d_null.py` | `59d9721cefbcd1276348e7ee183007160954e49d` |  |
| `2d-unfolding/cov2d/cov2d_pilot.py` | `ae9764676876857efa66ecc5c245a6936961f469` |  |
| `2d-unfolding/cov2d/cov2d_pseudo.py` | `4b23971e0f79f4a20e75b9ecb2ee013fdf638c68` | changed since M |
| `2d-unfolding/cov2d/cov2d_pseudo_write.py` | `5234deb290dc00449203b9c1070e2a6a6a9afdcc` | changed since M |
| `2d-unfolding/cov2d/cov2d_readouts.py` | `7e6407c4308500e1f622dfe870b8f8f314e1a7fc` |  |
| `2d-unfolding/cov2d/cov2d_receipt.py` | `d5718bf44c2084c20c30a8b8614e9c40e6fbeee3` |  |
| `2d-unfolding/cov2d/cov2d_score.py` | `282fd27ec07c84b4f9a0f287004eca0133858c15` |  |
| `2d-unfolding/cov2d/cov2d_writer.py` | `bb3892e5447d37ee524c720c5ab623baa7184f30` |  |
| `2d-unfolding/cov2d/jobs/cov2d_env.sh` | `2eb123666e9a56b60c8d4b762c12ac93ce258272` | changed since M |
| `2d-unfolding/cov2d/jobs/cov2d_job.sbatch` | `ddfee60929cd6b06a2eefe66b3f1c95513468649` | changed since M |
| `2d-unfolding/cov2d/jobs/cov2d_jobs.py` | `a74d6b0069e58a7b90480fcff4fe0ee4070e7f05` | changed since M |
| `2d-unfolding/cov2d/jobs/cov2d_pseudo.sbatch` | `a4746da9cf9cda568c18b5d65cbd8cbe004c1345` | changed since M |
| `2d-unfolding/cov2d/jobs/cov2d_submit.sh` | `0b07131c00353dbae713f00cb1897d6e2238ff55` | changed since M |
| `2d-unfolding/cov2d/tests/deploy_fixture.py` | `75033297ae8e2617bca6c0d7aae5ddb75c110500` |  |
| `2d-unfolding/cov2d/tests/noatime_emu.py` | `d18c85116b480ca7b05c8e411f0e56e82c8ea662` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d.py` | `3914524b9ccd17ab809711ac11f0d2d3f61ad215` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_blocks.py` | `e3682f8d5da47cbcf39a513850c781a1a7a20cd0` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_jobs.py` | `b60283e8111dfe7a0ceaabf1b625506958bf1238` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_null.py` | `3002455578509d6d4be06a08e4fa17105f06492d` |  |
| `2d-unfolding/cov2d/tests/test_cov2d_pilot.py` | `4f65bdf5f34a9ae72441e797ff57be04fee0c0c6` |  |
| `2d-unfolding/cov2d/tests/test_cov2d_pseudo.py` | `c415afc06d994608e97334f1ceedcb5d572c3ee6` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_pseudo_write.py` | `d37930c5094699c8b597db26ad34a08bd831aada` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_readouts.py` | `1b2be505bb839e889eb968c07e4708a9a2bcd5b9` |  |
| `2d-unfolding/cov2d/tests/test_cov2d_score.py` | `25aa147442296ef4b22ed0ac43c712f604a73ec4` |  |
| `2d-unfolding/cov2d/tests/test_cov2d_writer.py` | `c08e13844292746a113d9ea545b04f54459b54f9` |  |
| `2d-unfolding/cov2d/tests/test_null205.py` | `9b88c607ccab4a0f4afafd9335bf93c2df38734b` |  |
