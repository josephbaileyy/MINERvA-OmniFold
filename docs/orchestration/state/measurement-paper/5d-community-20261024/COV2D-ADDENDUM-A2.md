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

The code commit `a2005b544e5da5f2e4add11a42dc0deb1fe677d2` on main's `a548d44c` (which carries the merged #797). Its blobs are in §9. Against M
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
- **`order()`** is unchanged. It still reads AR23's PASS record at `fd/receipts-cov2d/pseudo/AR23/pseudo_b.json`.
  The rerun's record goes there, after the director has read it. The failed run's receipt sits in
  `pseudo/AR23-attempt1/` (#799).

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

**The quota check before `$UNI`** (the director's ruling).
- Before anything is staged, step A reads NERSC's `showquota`. It requires pscratch's headroom (limit − used) to be at
  least 2 × the bytes to be staged (`cov2d.STAGE_HEADROOM`).
- Otherwise, or if the quota can't be read, it refuses before any input is read, with the reason.
- The parser is tested on RE-2's own committed `showquota` row (`partb_readout/quota_before_cleanup.txt`).
- **Assumption, not yet verified:** that `showquota` runs on a compute node. The cluster test run (§6) will run it on a
  login node. If it can't be read inside the job, the job refuses at its start, before staging, and that comes to the
  director.

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

- **Step A** (`cov2d_pseudo.py`) and **step B** (`cov2d_pseudo_write.py`) read each staged copy's atime right after
  staging and again at the step's end. Both readings go into the record as epoch ns: `atime_ns = {path: {"before",
  "after"}}`, beside `atime_moved`. Any move STOPs.
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
   `test_cov2d_pseudo_write`'s silent-on-clean and fire tests running, not skipped, in their environments. It also runs
   `cov2d.headroom_problem` on `showquota`'s live output. Its connect sha goes to the director first.
2. **AR23's pseudo-data rerun** (`cov2d_submit.sh <deploy> M AR23 pseudo`, 04:00:00), its connect sha first.
   - On PASS, its record is committed at `order()`'s path after the director reads it.
   - A guard firing on a staged copy ends (c).
3. **Then the universe jobs and the bulk,** as bound in amendment 1 and binding 2, each connect's sha first. The unfold
   jobs are unchanged, except that AR23's read `$O/pseudo/AR23-a2/b`.

**How outcomes classify.** This is my reading, for the director to confirm.
- **A guard STOP** (a record with `verdict: STOP`) is a STOP.
- **A refusal** raises before any verdict: an existing directory, a quota short of 2×, a staged hash off its pin, a
  dirty deploy. It writes no record verdict, so it is not a guard STOP. It comes to the director as the job's failure.
- **A crash, OOM, kill or time-out** is INVALID, as before.

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

## 9. Tests, mutants and blobs

At `a2005b54`, in one local environment holding PyROOT, uproot and numpy (ROOT 6.28/12, uproot 5.6.9): **170 tests, 0 skipped, all pass** (`fd/receipts-cov2d/amendment/suites_a2005b54.txt`):
- step A 19, step B 15, blocks 26, null 5, scorer 12, readouts 12, jobs 35, pilot 13, cov2d 33;
- new with A2: staging, the guard's values, the quota check (5); step A's staging, fire and quota tests (3); step B's staging and fire tests (2); the limits, `pseudo_dir`, the deletion and AR23's dry run (4).

This local run used the macOS emulation of O_NOATIME (§4). The cluster run must show both directions on Linux.

**Mutants:** `fd/receipts-cov2d/amendment/mutation_amendment.py`, 77, **all killed**, harness exit 0 (`mutation_amendment.txt`). **24 are REQUIRED.** That's binding 2's 10, plus ruling (a)/(i)'s 2, plus A2's 12:
- the guards reading or watching the shared originals (A and B);
- the guard values not recorded (A and B);
- the staging pin unchecked;
- the quota check skipped;
- the headroom at 1x;
- ROOT reading the staged copies;
- AR23 rerunning into its old directory;
- AR23's limit at 03:00:00;
- the deletion without the stat match;
- the shared atime not recorded.

Each of the 12 was also run alone first, all killed.

**Blobs at `a2005b544e5da5f2e4add11a42dc0deb1fe677d2`**, every file under `2d-unfolding/cov2d`. The 14 files that differ from M (`cb31611c`) are marked: A2's 13, plus #797's `test_cov2d_blocks.py` (ruling (i)).

| file | blob | |
|---|---|---|
| `2d-unfolding/cov2d/cov2d.py` | `9c009c352a82ee4e703155df62517d8293103f75` | changed since M |
| `2d-unfolding/cov2d/cov2d_blocks.py` | `b9e63a3827e44c31a529f8d92482b7d7969d8223` |  |
| `2d-unfolding/cov2d/cov2d_null.py` | `59d9721cefbcd1276348e7ee183007160954e49d` |  |
| `2d-unfolding/cov2d/cov2d_pilot.py` | `ae9764676876857efa66ecc5c245a6936961f469` |  |
| `2d-unfolding/cov2d/cov2d_pseudo.py` | `b1ea75f16f09d5aba39fb490d3d73d14b541eac5` | changed since M |
| `2d-unfolding/cov2d/cov2d_pseudo_write.py` | `963b9882a45e8ddb5a04ad260d3e51be965d3db3` | changed since M |
| `2d-unfolding/cov2d/cov2d_readouts.py` | `7e6407c4308500e1f622dfe870b8f8f314e1a7fc` |  |
| `2d-unfolding/cov2d/cov2d_receipt.py` | `d5718bf44c2084c20c30a8b8614e9c40e6fbeee3` |  |
| `2d-unfolding/cov2d/cov2d_score.py` | `282fd27ec07c84b4f9a0f287004eca0133858c15` |  |
| `2d-unfolding/cov2d/cov2d_writer.py` | `bb3892e5447d37ee524c720c5ab623baa7184f30` |  |
| `2d-unfolding/cov2d/jobs/cov2d_env.sh` | `2eb123666e9a56b60c8d4b762c12ac93ce258272` | changed since M |
| `2d-unfolding/cov2d/jobs/cov2d_job.sbatch` | `5585e13eef98772e0ececaba88fd2480160e7ae2` | changed since M |
| `2d-unfolding/cov2d/jobs/cov2d_jobs.py` | `a3bf6c3572f43a84218eba887c0c6c4a266a83ae` | changed since M |
| `2d-unfolding/cov2d/jobs/cov2d_pseudo.sbatch` | `a0c63e0fa94383c2e73d6e6eb66d4958b43fcd88` | changed since M |
| `2d-unfolding/cov2d/jobs/cov2d_submit.sh` | `0b07131c00353dbae713f00cb1897d6e2238ff55` | changed since M |
| `2d-unfolding/cov2d/tests/deploy_fixture.py` | `75033297ae8e2617bca6c0d7aae5ddb75c110500` |  |
| `2d-unfolding/cov2d/tests/noatime_emu.py` | `d18c85116b480ca7b05c8e411f0e56e82c8ea662` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d.py` | `2de564ad0e6fcc34db9c73e406ab491ac82a40cf` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_blocks.py` | `e3682f8d5da47cbcf39a513850c781a1a7a20cd0` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_jobs.py` | `d7c3d92607c8245e879e2c67149fdcf92de60e1a` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_null.py` | `3002455578509d6d4be06a08e4fa17105f06492d` |  |
| `2d-unfolding/cov2d/tests/test_cov2d_pilot.py` | `4f65bdf5f34a9ae72441e797ff57be04fee0c0c6` |  |
| `2d-unfolding/cov2d/tests/test_cov2d_pseudo.py` | `040e41f51a377dc520fd5b5b253ffa2641c88d4e` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_pseudo_write.py` | `0dd24a191a673ccc2409c0818c108e5ab5ef46ce` | changed since M |
| `2d-unfolding/cov2d/tests/test_cov2d_readouts.py` | `1b2be505bb839e889eb968c07e4708a9a2bcd5b9` |  |
| `2d-unfolding/cov2d/tests/test_cov2d_score.py` | `25aa147442296ef4b22ed0ac43c712f604a73ec4` |  |
| `2d-unfolding/cov2d/tests/test_cov2d_writer.py` | `c08e13844292746a113d9ea545b04f54459b54f9` |  |
| `2d-unfolding/cov2d/tests/test_null205.py` | `9b88c607ccab4a0f4afafd9335bf93c2df38734b` |  |
