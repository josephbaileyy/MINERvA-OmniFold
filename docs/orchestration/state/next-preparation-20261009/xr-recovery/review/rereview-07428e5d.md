# XR recovery: focused re-review (use 2 of 3)

**Verdict: ADMIT.** F-1 is repaired. F-2 is repaired except for one minor gap (N-1), and no new MATERIAL defect was found. The final independent numerical verification (use 3) is still to come, after the runs.

| | |
|---|---|
| Reviewer | fresh, read-only, independent reviewer (Claude), under Joseph's 2026-10-11 XR-recovery grant; the same reviewer as the admission review `admission-review-57b7403c.md` |
| Fixed commit | `07428e5dec9fecd2e1148d8a2bdabc139a35138f`. Manifest sha256 `07a74b91…50d6` re-hashed and it matches. `xr_admit.py` sha256 `f9fbbddf…630d`. |
| UTC | start 2026-10-11T02:32:04Z, end 2026-10-11T02:37:57Z |
| Worktree | detached at `07428e5d`. Status was 0 lines at the start, 0 after the mutants and probes, and 0 at the end. Removed. |
| Resources | **Local:** about 0.08 core-hours (suite, one probe, 5 mutants), at most 2 threads. **Cluster:** one `/usr/bin/python3` compile check fed over stdin on a login node. No jobs. |

## Prior findings

| id | status | evidence |
|---|---|---|
| F-1 (MATERIAL) | **REPAIRED** | **What the gate now requires** (`preflight_passed`, l. 375–409):<br>• everything it checked before;<br>• `aN` equal to the receipt's attempt;<br>• `exit_code==0` and `identity.strict` true;<br>• the receipt's `SLURM_JOB_ID` equal to the PF `job_id` in `submissions.jsonl` for that attempt;<br>• `scontrol-job.txt` byte-equal to the recorded line and to its recorded sha256;<br>• `check_allocation(line, preflight kind, job)` passing.<br>**My hand-run probe** (`xr_run.py --run PF --require-provenance` under the guard, outside any job, OMP 12, PF submission recorded as 59645304). Every case gives `preflight-pass`, and the gate's answer is:<br>• no record, no Slurm id: **False**;<br>• the refused `(null)` line a failed jobcheck leaves, no Slurm id: **False**;<br>• the same with a faked `SLURM_JOB_ID=59645304`: **False**;<br>• `next-attempt L0`: rc 3, "no passed preflight".<br>**Real path:**<br>• `xr_job.sbatch` runs `jobcheck --record` on `scontrol show job $SLURM_JOB_ID -o` before `xr_run.py`, which records `SLURM_JOB_ID` from the environment;<br>• `xr_submit.sh` records the numeric `job_id` and the attempt;<br>• the end-to-end PF test through `xr_job.sbatch` still passes the gate.<br>**Tests and mutants:** both refusing-direction tests pass, covering 9 refusal cases plus an edited record. The 4 gate mutants are all caught; I reran them myself. |
| F-2 (MINOR) | **PARTIAL** (remaining gap is MINOR) | **Now flagged with exit 6:**<br>• a prior or amendment job with `ElapsedRaw>0` and unreadable billing (tests plus 2 mutants);<br>• a header lacking `AllocTRES`, `ElapsedRaw` or `JobID`;<br>• an empty file.<br>**Remaining gap:** see N-1. |
| F-3 (NOTE) | open, by design | The first captured RUNNING line of this account will be the preflight's own `scontrol-job.txt`. Parse it in use 3. |
| F-4 (NOTE) | open, by design | Run receipts are not bound to a job id. In use 3, check `SLURM_JOB_ID` against `submissions.jsonl` and sacct. |

## New findings

| id | severity | location | evidence |
|---|---|---|---|
| N-1 | MINOR | `xr_admit.py` `ledger` (prior-job loop, `r["State"]`, `charge`) | **What happens:** when the header lacks `State`, the ledger crashes with `KeyError` (rc 1). When it lacks `JobName`, the columns shift and it crashes with `ValueError` (rc 1). The "lacks" flag is added but never printed.<br>**Why it is MINOR:**<br>• it still fails closed (non-zero, no ledger output);<br>• the ledger's sacct format is fixed;<br>• no launcher acts on the ledger's exit code;<br>• the cap is enforced separately, by the per-attempt ceilings checked at submission.<br>**Required change:** exit 6 on a header that lacks any required column, before reading any row. |
| N-2 | NOTE | `preflight_passed` | **Probe:** a receipt that the gate accepts can still be built by forging both the environment (`SLURM_JOB_ID` set to the submitted id) and a passing allocation line in `scontrol-job.txt`; the gate then returns True.<br>**Assessment:** this needs deliberate fabrication of scheduler output, which is outside the threat model. In use 3, confirm the PF job id and its allocation from sacct. |
| N-3 | NOTE | `tests/test_xr.py` `py()` | The caller's env now overrides `OMP_NUM_THREADS`; before, a duplicate key raised `TypeError`. Only the new hand-run test passes `OMP_NUM_THREADS`, and every other caller behaves as before. No defect. |

## Other checks

- **Scientific definitions:** unchanged against `06eae0fe`. That covers `references.json`, and in `runs.json` the comparisons, controls, criterion, inputs, environment, the five runs and the exact/lgbm kinds.
- **Executed code:** of the repair batch, only `xr_admit.py` changed. `xr_run.py`, `xr_compare.py`, the launch scripts and `record/` are byte-identical to `57b7403c`.
- **Suite:** 42 tests, OK, rc 0.
- **Mutation record** (`xr-mutation-results-repair.json`): 60 of 60 caught (53 failures, 7 errors). I reran 5: `gate-job-unbound`, `gate-record-unchecked`, `gate-allocation-unchecked`, `gate-strict-exit-unchecked`, `ledger-header-unchecked`. All were caught, and the files were restored.
- **Python 3.6:** `xr_admit.py` (`f9fbbddf…`) compiles on `/usr/bin/python3` 3.6.15. The suite's 3.6 syntax test passes.

## What I could not verify

- The gate on a real PF job's receipt and its `scontrol` line: that only exists once the preflight has run (use 3).
- `xr_submit.sh` against the real `sbatch`; it is tested only with stubs.
