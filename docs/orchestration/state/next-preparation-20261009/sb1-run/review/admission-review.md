# SB1 admission review: run/sb1-20261010 at f7135d31

**VERDICT: ADMIT WITH CONDITIONS.** There are no blockers. Two conditions apply: C1 is operational and binds at submission and cleanup; C2 is a record correction due before final delivery. Neither condition changes the pinned package or the operator wrapper.

- **C1 (operational).** After any `cleanup` or `status`, do not treat "no still_active" as proof that nothing is left. Also run `squeue --me -t all -o '%i|%j|%T|%Z'` and confirm that no job of this attempt (WorkDir = `/pscratch/sd/j/josephrb/sb1-2b35ba52`) is listed in **any** state. Any job that is listed is handled under the INCONCLUSIVE rule and named. Reason: finding 2.
- **C2 (record, before delivery).** Correct the following in `Q/sb1-run/REPORT.md` (or the final record):
  - **§1, lines 97–98.** The orphan bound is too narrow. Any orphan is one of the six sbatch calls, so it is bounded by that job's own ceiling, not by 0.0059 (the grant: "do not assume only a hash job can survive"). The total stays at most 1.69921875, because every possible job is one of the six.
  - **§2, line 104, and `checks/login-node-root628.txt:3`.** "Status 0 lines" holds only without `--ignored`. The login-node test wrote an ignored `__pycache__` into the frozen checkout. Disclose it. Reason: finding 1.
  - **§2, line 106.** Besides the inputs, the setup and the references, the run also reads from the canonical checkout the files the setup sources: `unbinned_unfolding/build/setup.sh` and `MINERvA101/opt/bin/setup.sh`. The run's environment-digest check does not cover those two files (integration F6). Reason: finding 4.

## Setup facts

- **Reviewer.** A fresh read-only reviewer, authorized for this admission review only (`reviewer-admission.md`). I did not write the package, the authorization or the run record.
- **UTC window.** Start 2026-10-10T20:13:17Z; end of checks 2026-10-10T20:29:03Z, review written just after.
- **Local worktree.** `/private/tmp/sb1run-review-a`, detached at `f7135d315536bc09254fd2137fd413c327ad446b`.
  - `git status --porcelain --ignored` at start: **0 lines**.
  - At end: **1 line**, `!! …/sb1-run/operator/__pycache__/`. My own probe created it: `python3 -I` implies `-E`, which ignores `PYTHONDONTWRITEBYTECODE`.
  - The worktree and `/private/tmp/sb1run-review-scratch` are removed after this file is written.
  - Nothing was edited, committed or pushed in the shared repository or any existing worktree.
- **CPU.** About 128 s user+sys for the test suites, plus a few seconds of git and hashing: about 0.04 core-h, under the 0.4 cap. At most one test process ran at a time.
- **Local environment.** Python 3.13.7, numpy 2.4.4, ROOT 6.36.000. No Slurm client on PATH (`command -v sbatch squeue sacct scancel srun salloc`: none).
- **Cluster commands I ran.** Login23, via `ssh -o BatchMode=yes saul.nersc.gov 'bash -s'`, with `GIT_OPTIONAL_LOCKS=0` for my own git reads.
  - Clock and timezone: `date`, `hostname`.
  - `git` read commands (rev-parse, status, log, remote, ls-files, check-ignore, worktree list) in the frozen and canonical checkouts.
  - `sha256sum`, `stat`, `ls`.
  - `python3 -I -c` hashing and stat-ing (read-only).
  - `sb1_admit.py check` (with the setup sourced in a subshell and `PYTHONDONTWRITEBYTECODE=1`).
  - `squeue` (`--me -t all`, and `-u $USER` with the operator's format).
  - `sacct` (allocations since 2026-10-09, the operator's field list, and job 59410433_1 as the billing precedent).
  - `scrontab -l` (read-only listing).
  - `iris`, `showquota`, `sacct --version`, `squeue --version`.
- **Cluster commands I did not run.** No sbatch, srun, salloc or scancel. No package test on the cluster. I created no file on the cluster: my scripts were piped through stdin, so `$SCRATCH/tmp` was not needed.

## Findings

1. **MINOR — The frozen checkout is not pristine. It holds an ignored test bytecode file.**
   - **What is there.** `git -C /pscratch/sd/j/josephrb/MINERvA-OmniFold-sb1-2b35ba52 status --porcelain --ignored` prints `!! docs/orchestration/state/next-preparation-20261009/sb1-prep/tests/__pycache__/`. It holds one file, `make_fixture_omnifile.cpython-311.pyc`, with mtime 2026-10-10 13:07:46 PDT (20:07:46Z). That falls inside the owner's login-node test window (20:06–20:12Z).
   - **What the records say.** `git status --porcelain` without `--ignored` prints 0 lines, so the claims at REPORT.md:104 and login-node-root628.txt:3 are true only for that mode.
   - **Effect on the run.** None. `sb1_admit.check` uses `--untracked-files=no`. No run-path file imports anything under `tests/`: grep over `sb1_run.py`, `sb1_verify.py` and `branch_select.py` for `tests`, `make_fixture` and `fake_slurm` returns nothing. The six manifest modules, 17 guard files and 9 launch files (32 in all) hash correctly on the cluster: 0 mismatches.
   - **Action.** Disclosure only (C2). Deleting the file is optional and is the owner's write, not mine.

2. **MINOR — The operator wrapper's `ACTIVE` set misses several non-terminal Slurm states, so `cleanup` can report clean while a job is still alive.**
   - **The gap.** `sb1_operate.py:36` sets `ACTIVE = {PENDING, RUNNING, CONFIGURING, REQUEUED, RESIZING, SUSPENDED, COMPLETING}`. `state_of` (line 123) prefers squeue's state, so a job that squeue still lists as `STOPPED`, `SIGNALING`, `STAGE_OUT`, `REQUEUE_HOLD`, `RESV_DEL_HOLD` or `SPECIAL_EXIT` is skipped:
     - not targeted (line 131);
     - not waited on (line 142);
     - and `cleanup` returns 0 (line 150).
   - **Measured.** I loaded the module and checked `state_of({'State_squeue': s}) in ACTIVE`: False for all six states, True for PENDING.
   - **Likelihood.** Low: `--no-requeue` is set, there is no burst buffer, and STOPPED or SIGNALING are transient or set by an administrator.
   - **Impact.** It cannot charge beyond the job's own wall limit, but it could misreport accounting as settled. This is the "ambiguous state treated as clean" class, so C1 closes it procedurally without changing the mode-444 wrapper.
   - **Other paths are correct.**
     - Wrong cancellation needs the same user, a submit time in the window and WorkDir equal to the unique outroot (or StdOut/StdErr under it). Only this attempt's jobs can satisfy that.
     - A garbled-reply orphan still carries the `--chdir`/`--output` binding (`sb1_submit.sh:49-50`), so `identify` finds it.
     - If `sacct` or `squeue` fails, `identify` returns None and `cleanup` refuses (rc 2): fail-closed.
     - An exit 0 that disagrees with `submission.json`, or any ambiguity, triggers cleanup and a non-zero return.
   - **Field support on the cluster.** I confirmed that Slurm 25.11.8 supports the operator's sacct fields. `StdOut` keeps the unexpanded pattern (`…/%x-%A_%a.out`), but its directory prefix still matches. `StdErr` is empty only when `--error` is not given, and SB1 gives it.
   - **Timezone.** `TZ=America/Los_Angeles` is inherited by both the wrapper and `sacct`, so times parse consistently (`parse_slurm_time` and `-S`). No DST change falls near the run.
   - **Untested paths.** The identify-failure path and these extra states have no control in `test_sb1_operate.py` (NOTE).

3. **MINOR — REPORT §1's orphan bound (REPORT.md:97–98, "orphan hash job … bounded by 0.0059") is narrower than the grant requires.**
   - **Where it is too narrow.** Integration §4.4 assumes `--kill-on-invalid-dep` removes the orphan at calls 2–5. That holds only if `on_error`'s cancellation of the predecessor makes the dependency invalid. If the predecessor had already completed, an orphan UL, SL, J1 or C would run until the operator cancels it.
   - **Why the cap still holds.** Every job that one `sb1_submit.sh` call can create is one of its six sbatch calls, each with a fixed `--time` and shape. The worst case is therefore still the sum of the six ceilings, 1.69921875 node-h, not that sum plus an orphan.
   - **Action.** Correct the wording (C2). No cap risk.

4. **NOTE — The run still depends on the canonical checkout's contents, though not on its position.**
   - **What it reads.** The canonical `setup_salloc_env.sh` (tracked; sha256 `ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48`, 1,407 B, inode 882725528459544610). That is the same value as in REPORT §1 (truncated at REPORT.md:81, in full in `admission/cluster-state-20261010T2000Z.txt`), as at `2b35ba52:setup_salloc_env.sh` and as at `32e403b8`. The setup in turn sources `${SCRIPT_DIR}/unbinned_unfolding/build/setup.sh` and `${SCRIPT_DIR}/MINERvA101/opt/bin/setup.sh` from the canonical tree.
   - **What is checked.** Each job checks only the top-level digest (integration F6, disclosed). REPORT.md:106 lists three dependencies and should name these two as well (C2).
   - **Nothing moves the canonical checkout.** The plan never moves or edits it: it stays at `32e403b8` with its two pre-existing `M` live-state files.
   - **Hardcoded path.** The driver inserts the canonical helper path at `unfold_2d_omnifold_unbinned.py:1720`. The package handles this with its reviewed helper preload and the OI-136 guard (sb1-prep §9). This is not a new issue.

5. **NOTE — The ROOT 6.28 finding (REPORT §3) is confined to the test.**
   - **Run path.** grep for `AsNumpy|RDataFrame|uproot` over `sb1_run.py`, `branch_select.py`, `sb1_verify.py`, `sb1_hash.py`, `sb1_admit.py`, the driver, `omnifold.py`, `n2/*.py` and `mnv_guarded_run.py` finds only a comment (driver:1715).
   - **ROOT calls the run does make.**
     - `branch_select.py` uses `gInterpreter.Declare` and branch addresses. These are exercised under 6.28 by the 15 byte-equality cases that passed on login23.
     - `sb1_verify.hist_values` reads bins with `GetBinContent` and `GetBinError`, which behave the same across versions.
   - **What is not exercised.** `sb1_verify.py` has not run under ROOT 6.28 or numpy 1.26 on a real output. A failure there would give a verification error inside H1, not extra charge, and final verification is independent anyway.
   - **Re-run.** I did not re-run `fixture_probe.py`; the probe's logic matches the test it replaces.

6. **NOTE — The hash throughput is assumed, not measured** (sb1-prep REPORT:478, :658). H0 and H1 each hash 173 GB within 45 min, which needs at least 64 MB/s. The universe file has no prior digest. A timeout gives INCONCLUSIVE at 0.0059 node-h. This is not an admission issue.

7. **NOTE — The authorization's provenance can be traced only to `grant.txt`.** The quoted grant matches `grant.txt` byte for byte. Its source is the owner-saved copy (mtime 13:01 PDT = 20:01Z, after the recorded receipt at 19:58:35Z). I cannot compare it with the original session prompt.

## Checks performed

### 1. Unreviewed final delta

- **Integration's repairs.** `git diff b7c951b3 d4335d3b -- Q/sb1-prep` touches four paths: REPORT.md, `checks/mutation.py` (2 mutants), `tests/test_launch_chain.py` (2 tests) and the run-5 mutation log. I read the whole diff. None of these files is executed by a job, and no script, module, launch spec or manifest changed. The new tests are correct in substance:
  - they fail sbatch at calls 1 and 6 and send a non-numeric reply;
  - they run every queued job directly after the setup changes and require exit 3 with an empty job directory.
- **Run commit `2b35ba52`.** Parent `016265cc`; exactly 4 paths: the AUTHORIZATION record (+75), CATALOG.md (+1 row), MANIFEST-overrides.tsv (+1 `LIVE open` row) and a regenerated MANIFEST.tsv. I read the CATALOG and overrides diffs. The MANIFEST.tsv changes are its own row plus regenerated referrer columns.
- **Record commit `f7135d31`.** Parent `2b35ba52`; 7 files, all under `Q/sb1-run/`.
- **The package's tree is identical everywhere.** `git rev-parse <c>:Q/sb1-prep` = `7db17678a17e…` at `d4335d3b`, `016265cc`, `2b35ba52` and `f7135d31`.
- **No executed or guard file changes.** `git diff --quiet` over `Q/sb1-prep` plus all 32 manifest paths (17 guard, 9 launch, 6 modules) returns 0 for `d4335d3b..016265cc`, `016265cc..2b35ba52`, `d4335d3b..f7135d31` and `2b35ba52..f7135d31`.
- **Manifest digest and file hashes, locally.** `expected-code.json` sha256 is `f060df81338b17069a31a0a2cc7a3430ed81c91ce64de6d6f3d54b80e08eb15a` at the worktree and at `d4335d3b`. All 32 files match it.
- **Pushed refs.** `git ls-remote origin`: `run/sb1-20261010` = `f7135d31…` and `main` = `016265cc…`.

### 2. Authorization binding

- **The quote.** I stripped `> ` / `>` from AUTHORIZATION:45–75. The result has sha256 `dec02013f3c1baf69936a32de2d97cbb7829fa422a5decd8b838deaa47294b3f`, which `cmp` finds byte-identical to `grant.txt` (same sha256, 7,007 B, newline-terminated).
- **The binding.** The record names `d4335d3b9bc2502002f93390f9555d07e134855f` and `f060df81…eb15a` in full (lines 13–14) and excludes all other compute (§2).
- **The record's digest.** Its sha256 is `3beec1da1fbd33154ffcc7da5e87adf957ebe7565372587f7da246069d0e9537` at `2b35ba52` (blob), at `f7135d31` and in the frozen checkout. That equals the admission's `authorization.sha256`.
- **Frozen checkout.**
  - HEAD = `2b35ba52…`.
  - Plain `git status --porcelain` prints 0 lines; with `--ignored`, see finding 1.
  - Manifest sha256 `f060df81…`.
  - All 32 manifest files match; 0 mismatches.
  - Its `.git` points to the canonical common dir, and `worktree list` shows it detached at `2b35ba520`.
- **Admission check, run myself on the cluster.** `sb1_admit.py check --admission /pscratch/sd/j/josephrb/sb1-admission-2b35ba52.json` under root_6_28 Python 3.11.14 printed `[sb1-admit] admission holds`, rc 0. The frozen status was unchanged afterwards.
- **Admission file.** `cc9dc814dfc53db300803deb1de6c455a0b00793be4b1bcbbf863837d645722c` on the cluster, identical to `admission/admission.json.txt`.
- **Admission fields against `launch/ADMISSION-PROPOSAL.json`.** Only these differ: authorization, checkout, `code.commit`/`package_commit`, `how_to_admit` (removed), outroot and status. Their values:

  | field | value |
  |---|---|
  | `status` | `ADMITTED` |
  | `checkout` | the frozen worktree |
  | `outroot` | `/pscratch/sd/j/josephrb/sb1-2b35ba52` |
  | `code.commit` | `2b35ba52…` |
  | `package_commit` | `d4335d3b…` (full) |
  | `modules` | equal to the manifest's modules |
  | `launch_spec_sha256` | `fb9a1947…`, equal to the spec file and the manifest |
  | `jobs` | six ceilings summing to 1.69921875 |
  | `ceiling_node_h` | 2.0 |

- **Inputs, re-stat on the cluster** (`os.stat`). Size, mtime_ns and inode are identical to `inputs_observed`:
  - universe: 171117087867 / 1783523295000000000 / 882725391507234642;
  - CV: 2144008221 / 1779094334000000000 / 882724772125893981;
  - flux MC: 5143 / 1777003503000000000 / 882724771874215681.

  Both reference products exist.
- **Outroot.** `/pscratch/sd/j/josephrb/sb1-2b35ba52` is absent (`ls -ld`: No such file). The only `sb1-*` entries are the admission file and the operator directory.
- **Environment setup digest.** Current sha256 `ea3c6998…1d48` = REPORT §1 = the cluster-state file.

### 3. Negative controls

Local runs at `f7135d31`, using `PYTHONPATH=$(root-config --libdir)`, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, a `TMPDIR` in my scratch and no Slurm on PATH:

| suite | runner result | skips |
|---|---|---|
| `test_branch_select` | Ran 16, OK | 0 |
| `test_sb1_guarded` | Ran 10, OK | 0 |
| `test_launch_chain` | Ran 29, OK | 0 |
| `test_package_consistency` | Ran 7, OK | 0 |
| `sb1-run/operator/test_sb1_operate` | Ran 5, OK | — |

These equal the integration counts at `dcae1a3a` (16/10/29/7).

- **Operator wrapper.**
  - The cluster copy `/pscratch/sd/j/josephrb/sb1-operator-2b35ba52/sb1_operate.py` is mode `-r--r--r--`, 8,924 B, sha256 `f626997f0078d9c3ac4296d41ca4afb97888c24c8355dfa67ab3ed87774cb5ce`, identical to the repository copy.
  - I reviewed its logic in full; see finding 2.
  - It invokes the package's `sb1_submit.sh` exactly once and never resubmits (`submit`, lines 153–179).
- **Submit script.** It is fail-closed on a failed or non-numeric sbatch reply (`sb1_submit.sh:58-64`) and cancels returned ids on ERR (51–55).
- **ROOT 6.28.** See finding 5.

### 4. Charge accounting

- **Ceilings recomputed.** The rule is regular → 256 × nodes, shared → cpus-per-task, ÷ 256 × wall. Wall is the submit-time `--time` (`sb1_submit.sh:65-76`), and shape and QOS come from each script's `#SBATCH` lines.

  | job | script, QOS × cpus | wall | node-h |
  |---|---|---|---|
  | H0 | hash, shared × 2 | 45 min | 0.005859375 |
  | UL | unfold, regular × 128 (full node) | 50 min | 0.833333 |
  | SL | unfold, regular | 30 min (overrides the script's 50) | 0.5 |
  | J1 | identity, shared × 64 | 45 min | 0.1875 |
  | C | cv, shared × 64 | 40 min | 0.166667 |
  | H1 | hash, shared × 2 | 45 min | 0.005859375 |
  | **total** | | | **1.69921875 ≤ 2.0** |

  - The spec, the submit-time `--time`, the `#SBATCH` lines and the admission all agree.
  - No `--mem` is requested anywhere, so shared billing equals cpus. Precedent: sacct for 59410433_1 (shared, 64 cpus) shows `billing=64` with mem 121920M.
- **H1's verification.** `sb1_verify.py verdict` runs inside `sb1_hash.sbatch` when `STAGE=H1` (lines 25–38), so it is inside H1's 45-minute ceiling.
- **Orphans and no-retry.** Every job any attempt can create is one of the six calls (finding 3). Every job has `--no-requeue`, and the wrapper never resubmits. The structural maximum is therefore 1.69921875 node-h.
- **Fresh reads (20:26Z).**
  - `iris`: m3246 charged 16,976.9 of 20,000.0; the user has charged 2,035.0 of 10,000.0.
  - `squeue --me -t all`: empty.
  - `sacct -X` since 2026-10-09: no rows.
  - `showquota`: pscratch 16.76 of 20.00 TiB (83.8%), inodes 12.9%.
  - All four match REPORT §1.
- **Nothing found that could charge outside the six jobs.**
  - `scrontab -l`: "no crontab".
  - No other user jobs exist.
  - Inside jobs, the OI-136 guard's PATH shim intercepts `sbatch`, `srun` and the other Slurm tools.
  - No run-path module calls sbatch, srun or salloc (grep).
  - The operator's and verifier's login-node commands are not charged.

### 5. Deployment

- **Canonical checkout.** It stays at `32e403b8` on `main`, with only the two pre-existing `M` live-state files plus untracked artifacts. Nothing in the plan moves it (finding 4).
- **Frozen checkout.** It is a separate detached worktree at `2b35ba520`.
- **XR and dependents.**
  - No `two-d-followup` directory exists, locally at `f7135d31` or in the canonical cluster checkout.
  - No `*xr*` or `*XR*` path exists in `$SCRATCH`.
  - The queue is empty, so no XR or dependent job is pending or running.
- **Serialization.** The chain is strictly serial, as the spec's `serial_order_reason` requires:
  - H0 → UL → SL → J1 → C, each `afterok` on its predecessor with `--kill-on-invalid-dep=yes`;
  - H1 `afterany` on all five.

  Filesystem contention from other users cannot be controlled (descriptive only).
