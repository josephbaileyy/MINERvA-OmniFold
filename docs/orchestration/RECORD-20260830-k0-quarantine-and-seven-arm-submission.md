# RECORD 2026-08-30 — the `aa67c426` products quarantined out of the k=0 namespace, and the seven arms submitted

**CITABLE FOR:** the disposition executed on the exact file set named in
[`DECISION-20260830-joseph-quarantine-k0-member-namespace.md`](DECISION-20260830-joseph-quarantine-k0-member-namespace.md);
the measured before/after counts and digests of that move; the five reads of the F-17(a) porcelain
operand around it; and the seven job ids, `sbatch` commands, host and UTC times of the step-4
submission for run `k0-7ac0edec-20260830T000215Z`.

**NOT CITABLE FOR** any gate movement; any Gate-2 clause or evidence; any adoption; any result about
the products of either rehearsal; any claim that the submitted arms will complete; ratification of
proposal §6's per-arm CPU ceilings (see `OI-177`); leg 6; any member `k != 0`; the M(ii) family;
`C_ML`; or a publication claim. **Gate 2 remains FAIL and no scalar-5D covariance is adopted.**

**Producer:** `claude-school`, the named rehearsal producer of
[`PROPOSAL-20260830-forward-only-rehearsal.md`](PROPOSAL-20260830-forward-only-rehearsal.md) §4 —
the same lane that withheld this submission at `d3742e93` and filed `OI-176`. **This is a PRODUCER
filing. This lane executed both actions and is therefore ineligible to grade either, and ineligible
for Gate 2.**

---

## 0. What Joseph ruled, and what it authorized

`OI-176` put two routes to him: quarantine the namespace on the 2026-08-23 pattern, or rule
resume-adoption acceptable. His words: ***"do option 1"***. The ratified scope
(`DECISION-20260830-joseph-quarantine-k0-member-namespace.md`, commit `deef0e48`) authorizes
**exactly one action** — **MOVING, never deleting**, the 517 files / 7 directories /
2 733 149 261 bytes under `nd-unfolding/mii/member_k000000` to a dated quarantine directory outside
the member namespace. It is a **per-instance** authorization naming an exact file set, not a standing
rule and not a precedent for the next one.

## 1. Preflight, re-measured rather than inherited

Submitting host `login23` (`ssh -n -o BatchMode=yes -o ConnectTimeout=30 saul.nersc.gov`),
`GIT_OPTIONAL_LOCKS=0`, `GIT_PAGER=cat`, `PAGER=cat`, `git --no-pager` throughout.

| property | required | measured `15:39:29Z`–`15:39:31Z` | result |
|---|---|---|---|
| deploy HEAD | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` | same | PASS |
| deploy detachment | detached | `symbolic-ref -q HEAD` rc=1; `branch --show-current` empty; **0** refs in `refs/heads`; **0** remotes | PASS |
| deploy porcelain | 0 | 0, and `--ignored` also **0** | PASS |
| deploy source dir modes | `dr-xr-x---` | 184 dirs, all `dr-xr-x---` | PASS |
| deploy regular file modes | no write bit | 1638 `-r--r-----` + 165 `-r-xr-x---` | PASS |
| `.git` mode | `drwxrwx---` (§11.1.1 forbids read-only) | `drwxrwx---` | PASS |
| writable paths outside `.git` | 0 | 0, independent `-writable` walk pruning `.git` | PASS |
| measurer `measure_m1_m6.py` | `ce52ff77…3ed51` | same, 14108 B | PASS |
| comparator `compare_m1_m6.py` | `28490539…65242` | same, 67440 B | PASS |
| expected differences | `13547f3f…5efc2c` | same, 11302 B | PASS |
| far-end measurer | `ad1a8b64…b84775` | same, 16358 B | PASS |
| canonical HEAD / branch | `32e403b8…`, `main` | same | PASS |
| **canonical porcelain** | **726** | **726**, 726 untracked, 0 modified, 0 staged | **PASS** |
| **canonical status digest** | `d429f0f3…8146a` | same | **PASS** |
| queue | only the waker cron | `57712764 WAKER_STATE_DI PENDING (BeginTime)`, nothing else | PASS |
| pscratch | under ~90% | **15.99 TiB / 20.00 TiB = 80.0%** (`hpssquota`; `lfs quota` agrees) | PASS |

**The digest recipe is NAMED, not assumed.** `d429f0f3…` is the sha256 of the **raw bytes of
`git status --porcelain`** — default `-unormal`, no `--branch`, no `--ignored`, trailing newline
included. Eight candidate recipes were measured and only this one reproduces it; in particular
`--untracked-files=all` gives **3473** lines and a different digest, and a sorted variant gives a
different digest at the same 726 lines. **The recipe is not interchangeable with any of them.** The
A-2 consolidated arm (five `--require-*` plus `--compare` in one invocation) returned **rc=0,
`SOURCE MANIFEST IDENTICAL (820 files, 8d036d94…)`**, and its negative control — `--compare` against
the superseded `declarations/aa67c426/source-manifest.json` — returned **rc=3
`SOURCE MANIFEST MOVED`**. The arm fires.

## 2. The move

```
source      /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/mii/member_k000000
destination /pscratch/sd/j/josephrb/quarantine/20260830-k0-aa67c426-failed-rehearsal/member_k000000
executed    2026-08-30T15:42:29Z on login23
```

Three `mv -n --` renames of the three top-level children (`boot_nd_5d`, `seedscan_split_5d`,
`uq_5d`), following the destination pattern of the 2026-08-23 disposition
(`…/quarantine/20260823-k0-a54038b2-failed-rehearsal`). **The executing script contains no `rm` and
no `cp`.**

**Why the contents and not the container.** The authorization names *the entire contents of*
`member_k000000`. Moving the three children moves exactly those contents and leaves the container in
place — the narrower action, inside the authorization under either reading. The 2026-08-23 precedent
also left empty directories behind and that was ruled harmless, because `mr_skip_if_complete` keys on
`.done` markers, not on directory existence. `mr_prefix`/`mr_dir_prefix` (`lib_member_resume.sh:140`,
`:147`) `mkdir -p` on demand, so an empty container is sufficient for the arms.

### Counts, with both byte decompositions published

| quantity | before | after (at destination) |
|---|---:|---:|
| regular files | **517** | **517** |
| regular-file bytes | **2 733 087 821** | **2 733 087 821** |
| directories | 7 | 7 (6 moved + 1 `mkdir`-created container) |
| directory-inode bytes | 61 440 | 61 440 |
| **all entries** | **2 733 149 261** | **2 733 149 261** |
| `.done` markers | 143 | 143 |
| `.root` / `.npz` / `.done` | 189 / 185 / 143 | 189 / 185 / 143 |

**The authorization's `2 733 149 261` counts ALL ENTRIES — regular files plus directory inodes — not
the sum of file sizes.** `2 733 087 821 + 61 440 = 2 733 149 261`. Both decompositions are recorded
so the arithmetic can be checked and can contradict itself; a receipt that published only the total
would have made the 61 440 B gap between the two figures invisible.

### Verification

Per-file `sha256` over all 517 files **before** the move and again **after**, plus a
`(relpath, bytes, mtime, inode)` ledger on both sides — two full reads of 2.6 GB.

- `sha256` set diff: **0 lines**. Concatenated listing digest `4c5458ff…7d0cd` on both sides.
- ledger diff: **0 lines** — sizes, mtimes and **inodes identical**.
- **Identical inodes are the stronger receipt.** Equal digests alone are consistent with
  copy-then-unlink; equal inodes are not. `st_dev` was measured equal on both sides **before** the
  move, with an abort arm on inequality, so `mv` was a rename by construction.
- **Negative control:** the after-listing was perturbed in its first byte and re-diffed — **4 diff
  lines**. A comparison only ever observed agreeing is decoration; this one fires.
- Abort arms armed and not fired: destination not absent-or-empty (exit 11); differing `st_dev`
  (13); operand drifted from 517 / 2 733 087 821 on a re-read immediately before the move (14); any
  `mv` returning nonzero (15).
- **pscratch unchanged at 80.0% after the move**, which is the falsifier for "this was secretly a
  copy".

### The 143 job ids

Read from the `"job"` field of the 143 `.done` markers themselves, **not** from a handoff or a job
list — a handoff's list is what was *submitted*. 143 markers, 143 carrying a job field, **143
distinct base ids**, 143 distinct `job:task` tokens, min `57527866`, max `57587242`, and **all 143
read `"note":"est_seed_offset=0"`** — exactly what this k=0 anchor declares, which is why
`mr_skip_if_complete` would have adopted rather than refused. Markers per directory: `boot_nd_5d`
100, `seedscan_split_5d` 24, `uq_5d/universe_sweep_bkgaware` 19. Full list in the receipt.

### The operand, and what it would have taken to break it

`nd-unfolding/mii` is untracked and not ignored inside the canonical checkout, and porcelain
collapses it to the single line `?? nd-unfolding/mii/`. **Emptying `mii/` entirely would delete that
line and move the population 726 → 725** — the staleness condition `F-17(a)` tests and the one that
blocked Gate 1 round 1. `member_k001200` (6 files, 278 647 B) and `member_k002400` (6 files,
278 656 B) keep it non-empty, and **neither was touched**: identical file counts, identical byte
totals, identical directory inodes **and identical directory mtimes** before and after. An unchanged
directory mtime is the test — a rename into or out of a directory updates it.

## 3. The operand across five reads

| # | UTC | when | porcelain | status sha256 |
|---|---|---|---:|---|
| 1 | `15:39:30Z` | preflight, before the move | **726** | `d429f0f3…8146a` |
| 2 | `15:42:59Z` | after the move | **726** | `d429f0f3…8146a` |
| 3 | `15:45:58Z` | **immediately before the first `sbatch`**, abort arm armed | **726** | `d429f0f3…8146a` |
| 4 | `15:48:02Z` | **immediately before the arm-6/7 `sbatch` calls**, abort arm armed | **726** | `d429f0f3…8146a` |
| 5 | `15:48:13Z` | after the last `sbatch` | **726** | `d429f0f3…8146a` |

Unchanged throughout, and byte-identical to the Gate-1 round-2 grader's `09:49:32Z` and `10:11:11Z`
reads. `?? nd-unfolding/mii/` present in every read.

## 4. The namespace the arms submit against

At `15:45:58Z`, immediately before the first `sbatch`: `mii/member_k000000` present and **empty** —
**0 entries, 0 files, 0 `.done` markers**. `mr_skip_if_complete` has nothing to adopt, so no task can
silently skip and no inventory can be cross-run or mixed-pin on adopted products. This is the state
§6's estimates and §8's cost model already assume.

## 5. The submission

```bash
export MNV_CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean
export MNV_DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold
export MNV_ENV_ROOT=/pscratch/sd/j/josephrb/k0env
export MNV_CONDA_PREFIX=/global/u2/j/josephrb/.conda/envs/root_6_28
export MNV_GUARD_INVENTORY_DIR=/pscratch/sd/j/josephrb/k0r2/runs/k0-7ac0edec-20260830T000215Z/inv
export MNV_SOURCE_MANIFEST=/pscratch/sd/j/josephrb/k0r2/runs/k0-7ac0edec-20260830T000215Z/source-manifest.json
export MNV_LAUNCHER_DIR=/pscratch/sd/j/josephrb/k0r2/clean/nd-unfolding
export MNV_EST_SEED_OFFSET=0
cd /pscratch/sd/j/josephrb/k0r2/runs/k0-7ac0edec-20260830T000215Z/log
C=/pscratch/sd/j/josephrb/k0r2/clean/nd-unfolding
sbatch --parsable $C/sbatch_bootstrap_5d_gpu.sh                                          # 57742557
sbatch --parsable $C/sbatch_seedscan_split_5d.sh                                         # 57742558
sbatch --parsable $C/sbatch_unfold_5d_detector_bkgaware_gpu.sh                           # 57742559
sbatch --parsable $C/sbatch_uthrow_run_5d_fast.sh                                        # 57742560
sbatch --parsable $C/sbatch_uthrow_block_5d.sh                                           # 57742561
sbatch --parsable --dependency=afterok:57742559          $C/sbatch_sweep_bank_5d_run_bkgaware_gpu.sh   # 57742633
sbatch --parsable --dependency=afterok:57742560:57742561 $C/sbatch_uthrow_combine_5d_fast.sh           # 57742635
```

All six `MNV_*` roots are **mandatory in all seven launchers** (measured: every one carries the
`${VAR:?}` form). `MNV_LAUNCHER_DIR` is set explicitly because `sbatch` runs a **spool copy**, so
`BASH_SOURCE[0]` is the spool path and `lib_member_resume.sh` is not beside it; `SLURM_SUBMIT_DIR` is
deliberately not a resolver candidate because it would silently resolve the canonical checkout's
library instead of the deployed one. `cwd` is the run's `log/` directory because the launchers'
`--output` paths are **relative** (`boot5dG_%a_%A.out`, `uq_5d/…`, `uq_4d/…`); `log/uq_5d` and
`log/uq_4d` were created first. Launchers are submitted **by absolute path under the code root**.
`env | grep -E '^(SBATCH_|SLURM_)'` was **empty** in both the submitting shell and a login shell, so
no `SBATCH_ARRAY_INX` silently redefined a population.

| arm | leg | job id | name | array | tasks | dependency | walltime | submitted UTC |
|---|---|---|---|---|---:|---|---|---|
| 1 | bootstrap | `57742557` | `boot5dG` | `1-100%32` | 100 | – | 03:00:00 | `15:46:01Z` |
| 2 | seed split | `57742558` | `ssplit5d` | `1-24%24` | 24 | – | 03:00:00 | `15:46:05Z` |
| 3 | detector | `57742559` | `det5dBKG` | `0-18%8` | 19 | – | 04:00:00 | `15:46:07Z` |
| 4 | uthrow run (5a) | `57742560` | `uthrow5d_runF` | `0-39%40` | 40 | – | 06:00:00 | `15:46:07Z` |
| 5 | uthrow block (5b) | `57742561` | `uthrow5d_block` | `0-20%10` | 21 | – | 12:00:00 | `15:46:07Z` |
| 6 | sweep | `57742633` | `sweep5dBKGrun` | `1-169%48` | 169 | `afterok:57742559` | 01:30:00 | `15:48:02Z` |
| 7 | uthrow combine (5c) | `57742635` | `uthrow5d_combF` | single | 1 | `afterok:57742560:57742561` | 03:00:00 | `15:48:04Z` |

**374 tasks total** (100+24+19+40+21+169+1), which equals the 374 guard-inventory files the
`aa67c426` run produced. Dependencies **read back from `scontrol`**:
`Dependency=afterok:57742559_*(unfulfilled)` on arm 6, and
`Dependency=afterok:57742560_*(unfulfilled),afterok:57742561_*(unfulfilled)` on arm 7 — **conjunctive
over both uthrow arrays**, as required. Arm 6 depends on the detector because both write into the
same member-scoped `uq_5d/universe_sweep_bkgaware` directory
(`sbatch_unfold_5d_detector_bkgaware_gpu.sh:285`, `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh:278`);
this reproduces the 2026-08-23 wiring and the `aa67c426` submission order rather than introducing an
unrecorded change to the submission shape.

### Populations were counted with `squeue -r`, and `sacct` would have got two of them wrong

`sacct -X` reported `57742557_[3-100%32]` and `57742558_[3-24%24]` — which would have
**under-declared both arms by two tasks each**. The `%32` and `%24` throttles had already promoted
tasks 1 and 2 to their own job records (`57742563`, `57742564`, `57742565`, `57742566`, confirmed by
`scontrol`), so the bracketed range is the **un-split pending remainder**, not the declared spec.
`squeue -r -j <id>` counted one row per task: **100 / 24 / 19 / 40 / 21 / 169 / 1**, min task
`1 / 1 / 0 / 0 / 0 / 1 / –`. The declared `#SBATCH --array` directives in the executing scripts agree
with those counts and with proposal §6 exactly, and **no `--array` override was passed**.

## 6. Budgets against ceilings — and a discrepancy that is disclosed, not buried

**The operative hard ceiling is strictly under 500 GPU-h AND strictly under 500 CPU-h per arm, and
every arm passes with two orders of magnitude of margin** — on the `aa67c426` measured actuals (max
**30.94**) and on the far more conservative walltime-request envelope (tasks × per-task `--time`; max
**253.5**).

| arm | billed column | §6 estimate | §6 per-arm ceiling | `aa67c426` **actual** | walltime envelope | < 500? |
|---|---|---:|---:|---:|---:|:--:|
| 1 bootstrap | GPU | 14.00 | 20 | **15.38** | 300.0 | ✔ |
| 2 seed split | CPU | 3.72 | 5 | **5.43** ⚠ | 72.0 | ✔ |
| 3 detector | GPU | 14.23 | 20 | **13.88** | 76.0 | ✔ |
| 4 sweep | GPU | 23.84 | 30 | **25.54** | 253.5 | ✔ |
| 5 uthrow run | CPU | 21.38 | 30 | **30.94** ⚠ | 240.0 | ✔ |
| 6 uthrow block | CPU | 22.02 | 30 | **30.01** ⚠ | 252.0 | ✔ |
| 7 combine | CPU | 3.0 (bounded) | 5 | **0.42** | 3.0 | ✔ |
| **totals** | | 52.07 GPU / 47.12+3 CPU | 70 / 70 | **54.80 GPU / 66.80 CPU** | | |

`aa67c426` **actual** = sum over all array tasks of `sacct` `Elapsed` for the corresponding arm of the
2026-08-24 run, every task `COMPLETED` at full population. **It is a different population from §6's
estimate column**, and naming both sides is the point: every §6 estimate (`3.72`, `14.23`, `23.84`,
`21.38`, `22.02`) is inherited verbatim from
[`PLAN-20260822-oneMember-mii-staged.md`](PLAN-20260822-oneMember-mii-staged.md)`:220-224`, a
2026-08-22 prior whose detector row is **24** tasks, not this arm's 19.

**⚠ Three arms' `aa67c426` actuals sit marginally above §6's per-arm CPU ceilings** — seed split by
**0.43** CPU task-h (8.6%), uthrow run by **0.94** (3.1%), uthrow block by **0.01** (0.03%);
**1.38 CPU task-h in total**. The ceilings were set "deliberately above the recorded estimates", i.e.
above the 08-22 priors, and the later run came in higher on three CPU arms. **The aggregate
envelopes still hold**: 54.80 GPU-h against 70, and 66.80 CPU-h against 70.

**Why the submission proceeded.** §6 reserves the call for Joseph at **500** in either column and
states the delegated authority may set these per-arm ceilings *precisely because* each arm is
strictly under 500. Withholding a second submission over 1.38 CPU task-hours of bookkeeping would
not have been proportionate. **This submission does not ratify those ceilings** — an amendment or
ratification against the `aa67c426`-population actuals rather than the 08-22 priors is routed as
`OI-177`, and it is not this lane's to grade.

**One walltime is stated rather than left to rest on the standing grant:** arm 5 requests
`--time=12:00:00`, which is **at** the standing 12-hour pre-authorization boundary rather than
strictly under it. Its authority is the specific per-arm delegation of §6, not the generic standing
grant; the `aa67c426` run ran this same arm at this same directive under authorization.

## 7. A defect in this lane's own submission script, and why the ids are not contiguous

The first submission block used a shell helper that both **logged to stdout and returned the job id
via command substitution**, so the captured "id" for arms 3–5 was the whole log line. Arms 6 and 7,
which take those ids as `--dependency` operands, therefore received malformed arguments and `sbatch`
refused both with `Unable to open file id=…`.

**No malformed job was created.** Verified against the full `squeue --me` **and** against
`sacct -S 2026-08-30 -u josephrb -X`, which together show exactly the five arrays, the pre-existing
waker cron, and nothing else — a queue read alone would not have caught a job that had already left
it. Arms 6 and 7 were submitted 2 minutes later in a second block that captured each id **from a
file** rather than a function's stdout, re-checked the operand with the same abort arms first, and
read the dependencies back from `scontrol`.

This is why the ids are `57742557`–`57742561`, then `57742633` and `57742635`. A reader comparing
against the `aa67c426` run's contiguous block would otherwise have an unexplained discontinuity.

## 8. What was not done

- **Nothing was deleted.** No file, directory, marker or intermediate was deleted, truncated or
  overwritten. The quarantined set is readable and digest-checkable at its destination with every
  `sha256` published. **The 41.44 GB combined intermediate was not touched** — it is not under the
  member namespace and its deletion remains gated on `MVFINAL_j` by §11g.
- **Neither sibling member was touched.** `member_k001200` and `member_k002400` are byte-identical,
  inode-identical and mtime-identical before and after.
- **Leg 6 / `fin5dBKG` was not run or submitted.** `finalize_submitted=NO`. And the prohibition is
  now **more** load-bearing, not less: §6b's *"no member is runnable"* was **two** independent
  refusals (`:167` 3 of 100 replicas; `:168` 0 of 24 splits, directory absent), and the failed
  `aa67c426` rehearsal had satisfied **both** — so `fin5dBKG`'s two documented validators *would*
  have passed against the pre-quarantine namespace. That is a consequence of a failed rehearsal, not
  a licence. After the quarantine both refusals hold again.
- **No other member and no family work.** `MNV_EST_SEED_OFFSET=0` only.
- **No gate was moved, nothing was adopted, and no Gate-2 evidence was filed.** Gate 2 remains
  **FAIL**.
- **No scheduler write other than the seven `sbatch` calls** — no `scancel`, `scontrol update`,
  `scrontab` or requeue. The waker cron `57712764` was not altered.
- **Neither protected tree was written.** The deploy tree is untouched at `7ac0edec` with porcelain
  0; the only write inside the canonical checkout was the authorized move, and its porcelain and
  status digest are unchanged across all five reads.
- **No poller, watcher or cron was armed by this lane, and none will resume it.** The jobs were not
  waited on. Anyone continuing this run must observe the scheduler directly.

## 9. Routes

- Quarantine receipt, with the 517-file digest ledger and the 143 job ids:
  [`state/RECEIPT-20260830-quarantine-k0-aa67c426-member-namespace.json`](state/RECEIPT-20260830-quarantine-k0-aa67c426-member-namespace.json)
- Submission receipt, with per-arm operands and the budget discrepancy:
  [`state/RECEIPT-20260830-k0-7ac0edec-legs-1-5-submission.json`](state/RECEIPT-20260830-k0-7ac0edec-legs-1-5-submission.json)
- The authorization: [`DECISION-20260830-joseph-quarantine-k0-member-namespace.md`](DECISION-20260830-joseph-quarantine-k0-member-namespace.md)
- Why it was needed: [`FINDING-20260830-k0-member-namespace-blocks-submission.md`](FINDING-20260830-k0-member-namespace-blocks-submission.md)
- The delegation and the sequence: [`DECISION-20260830-joseph-accept-forward-only-rehearsal.md`](DECISION-20260830-joseph-accept-forward-only-rehearsal.md), [`PROPOSAL-20260830-forward-only-rehearsal.md`](PROPOSAL-20260830-forward-only-rehearsal.md) §6, §9
- Submission procedure and abort conditions: [`RUNBOOK-20260822-b1-lift-preflight.md`](RUNBOOK-20260822-b1-lift-preflight.md) §5a, §6, §6b
- On-cluster record: `/pscratch/sd/j/josephrb/k0r2/runs/k0-7ac0edec-20260830T000215Z/SUBMISSION.txt`
  and `quarantine-20260830/` (before/after ledgers and digest listings)
