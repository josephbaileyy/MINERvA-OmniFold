# XR recovery: final independent numerical verification (use 3 of 3)

**Overall: CONFIRMED WITH DISCREPANCIES.** Every number and outcome I checked is confirmed. The discrepancies are three wording or completeness problems in the REPORT (V-1 to V-3), all MINOR. The preflight failed for the stated reason, and nothing else was launched.

| | |
|---|---|
| Reviewer | fresh, read-only, independent reviewer (Claude), under Joseph's 2026-10-11 XR-recovery grant; the same reviewer as uses 1 and 2 |
| Fixed commit | `204805d8a13f63cd71c37e857700ed15e4bf8cfc`. The package is byte-unchanged since `07428e5d`. |
| UTC | start 2026-10-11T03:19:40Z, end 2026-10-11T03:23:50Z |
| Worktree | detached at `204805d8`. Status was 0 lines at the start and 0 at the end. Removed. |
| Resources | **Local:** under 0.01 core-hours. **Cluster, login23 only:** sacct, squeue, cat and sha256sum reads; `/usr/bin/python3` running `next-attempt` and `ledger`; one run of the frozen comparator with the setup sourced (output went to a `/tmp` dir that was then removed); two Popen-spy traces of a few seconds each. No jobs. The outroot re-hashed unchanged afterwards. SB1 not touched. |

## Verdicts

- **(i) Admission, as recorded: CONFIRMED.**
  - `admission.json` (sha256 `4563871f…`) is ADMITTED, with head `9ec77fa1`, package `07428e5d`, manifest `07a74b91…` and the outroot.
  - The authorization at `9ec77fa1` (sha256 `25deb61b…`) names both the package commit and the manifest in full.
  - The cluster worktree is at `9ec77fa1` with 0 status lines.
- **(ii) Preflight: FAIL confirmed, and the stated defect is the cause.**
  - **Scheduler:** sacct for 59655414 gives `FAILED 1:0`, ElapsedRaw 74, `billing=12,cpu=12,energy=39366,mem=22860M,node=1`. Times: submitted 02:40:04Z, started 03:11:21Z, ended 03:12:35Z.
  - **Receipt:** status `preflight-fail`, exit 1, error `SystemExit: 3`, `fits: []`.
  - **Guard log:** the guard refused `['/sbin/ldconfig', '-p']`.
  - **Reproduced on login23:** the spy recorded exactly one launch, from `threadpool_info()`. The chain is `_load_libraries` → `_find_libraries_with_dl_iterate_phdr` → `_get_libc` → `find_library` → `_findSoname_ldconfig`. Nothing else launched across the imports, the loky seed or the fit-recorder imports.
- **(iii) Execution: INCONCLUSIVE (not launched), confirmed.**
  - The only `xrr_*` job in sacct is 59655414, and nothing is queued.
  - The outroot holds 10 entries: no `receipt.json`, no `.root` file, and no run directory other than `PF/a1`.
- **(iv) Comparisons:** X0_vs_E_C, X0p_vs_E_C, X1_vs_X0, L0_vs_CV42, L0_vs_PN_CV, L1_vs_SEED1 and NC_X0_vs_CV42 are each **INCONCLUSIVE** ("no complete attempt"). There is no histogram to reproduce.
- **(v) Numerical verification overall: CONFIRMED WITH DISCREPANCIES** (V-1 to V-3, all MINOR wording or completeness).

## Checks

| check | operands | result |
|---|---|---|
| PF/a1 digests | cluster sha256 of `preflight-receipt.json`, `scontrol-job.txt`, `inventory.jsonl`, both slurm logs, `admission.json`, `submissions.jsonl` | `55ed2b9e`, `539a9d78`, `65535693`, `80f8f1b4`, `94d0e08f`, `4563871f`, `12d08849`. All equal `results/preflight-summary.txt` and `joblogs.txt`. |
| F-3 (first own RUNNING line) | the cluster `scontrol-job.txt` against `results/scontrol-job-59655414.txt` | Byte-equal. `check_allocation` for the preflight kind gives billing 12, and it refuses another job id. JobState RUNNING, no duplicate keys. |
| F-4 / N-2 (job ids agree) | receipt `SLURM_JOB_ID`, the line's JobId, `submissions.jsonl` `job_id`, sacct | All four are 59655414. The receipt also carries the allocation record's sha256 `539a9d78`. |
| Defect is in the run path | `xr_run.py` l. 153 (`threadpool_info`), l. 408 (`check_environment`), l. 412 (`driver.main()`) | `check_environment` runs unconditionally before `main` in every run. A SystemExit there gives `driver-exit` before any fit. "All five would have failed the same way" holds. |
| Versions passed (inference) | code order: a version mismatch raises BackendRefusal (exit 6) before l. 153 | The receipt has no `environment_checked`, so "versions passed" is inferred from the exit path. The inference is valid. |
| Fit-path probe (indicative) | login23, no guard: GBC, GBR, LGBMClassifier and LGBMRegressor `fit` plus `predict`/`predict_proba` on tiny data; spies on Popen and on `os.fork`, `os.posix_spawn`, `os.system`, `os.exec*` | 0 launches. The driver and helper sources contain no subprocess, ctypes or threadpool calls. |
| Gates | live sacct; `next-attempt` for L0, X0, X0p, X1, L1, PF | All rc 3. The five runs: "no passed preflight". PF: "1 of 1 used". |
| Charges | sacct ElapsedRaw × billing | prior (12·45 + 64·11)/921600 = 0.0013498263888888891; PF 12·74/921600 = 0.0009635416666666667; sum **0.0023133680555555555**. The live ledger agrees (rc 0, `over` empty). |
| Window | first submission 02:40:04Z | Stop 2026-10-14T02:40:04Z; the Deadline of 19:40:00 PDT is 4 s earlier, which is conservative. PF ended 0.54 h after submission; nothing queued. |
| Comparator | frozen `xr_compare.py` on the live outroot | 7 of 7 INCONCLUSIVE. The JSON equals `results/comparisons-post.json`. |
| REPORT arithmetic | §9.4, §10 | Remaining 6.3976866; second-preflight ceiling 6.3812196 ≤ 6.4; local total ≈ 1.40 h. All correct. |
| Hygiene, `9ec77fa1..204805d8` | the added lines (64 KiB) | No data-event values or counts. The only sizes are input file bytes, already in `runs.json`. |

## Findings

| id | severity | location | evidence |
|---|---|---|---|
| V-1 | MINOR | REPORT §6 "Consequence" | "the exact runs after up to 30 h of queue and allocation" is an overclaim. The failure comes about 1 min into the allocation (PF: 47 s of wall time in `xr_run.py`). 30 h is the time limit, not when a run would fail. The charge at risk was minutes per run. |
| V-2 | MINOR | REPORT §9 item 2 | Incomplete. The steps after `check_environment` also never ran in an allocation or under the guard on Linux: the loky seed, `rec.install()`, the OMP check, `gx.recheck` and the input stat recheck. The requirement should be to run the whole PF code path, and the package's own end-to-end fixture tests (all five runs, with fits, under the guard), on Linux in the frozen environment before admission. That covers both this class of defect and item 3's fit path. |
| V-3 | MINOR | REPORT §9 item 1 | Removing `threadpool_info()` also removes the receipt's thread-pool record. The requirement should say what child-free evidence of the BLAS/OpenMP pools replaces it, if any comparison or thread check relies on it (§7 mentions a pre-registered thread-count check). |
| V-4 | NOTE | REPORT §9 item 3 | My unguarded login-node probe found no child launches in the fits or predictions of the four classes. That lowers the fit-path risk but does not remove it: it skipped the driver's own code (`refine_stay_positive`, ROOT I/O, pickling), used no guard, and used tiny data. The item stands. |
| V-5 | NOTE | REPORT §6 "The guard behaved correctly" | Correct against the guard's specification: it refuses any child it cannot prove is a leaf, and `/sbin/ldconfig` is not on its leaf list. `ldconfig -p` cannot launch Python, so this refusal is a false positive with respect to the guard's purpose, but it is the fail-closed design working as intended. §11's "a property of the environment, not a guard defect" is accurate. |
| V-6 | NOTE | REPORT §1, §6 | Start and end times are quoted from the job log (03:11:26–03:12:32Z). sacct says 03:11:21–03:12:35Z. They are consistent; the charge uses sacct's 74 s. |

## What I could not verify

- The guard's refusal path itself: I reproduced the trace without the guard, and the in-allocation refusal is evidenced only by the job's stderr and receipt.
- Whether any later step of the run path, or the real driver's fit on production input, would launch a child under the guard on a compute node.
- What a full scientific run would have produced: no histogram exists.
