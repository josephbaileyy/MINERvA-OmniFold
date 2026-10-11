# XR recovery: admission review (use 1 of 3)

**Verdict: ADMIT WITH CHANGES.** One repair is MATERIAL (F-1): the preflight release gate accepts a passing preflight receipt that was not produced inside the preflight job. The focused repair/re-review is the last review use left in the budget.

| | |
|---|---|
| Reviewer | fresh, read-only, independent reviewer (Claude), under Joseph's 2026-10-11 XR-recovery grant (`logs/grant.txt` sha256 `f9d02f65…`, re-hashed) |
| Fixed commit | `57b7403caa23c23b596044dd0ac8dd6f7099a67e` (`prep/xr-recovery-20261011`). Manifest sha256 `31a2285e…2d8e` re-hashed and it matches. |
| UTC | start 2026-10-11T01:47:07Z, end 2026-10-11T01:55:42Z |
| Worktree | detached at `57b7403c`. Status was 0 lines at the start, 0 lines after the mutants and probes, and 0 lines at the end. Removed. |
| Resources | **Local:** about 0.07 core-hours (suite 2:50 wall; 8 mutants 58 s; one probe), at most 2 threads. **Cluster:** login23 reads only (squeue, scontrol, sacct, sha256sum, `/usr/bin/python3` on stdin). The 2.14 GB CFS input was read twice: once by `sha256sum`, once by Python hashlib. No jobs; SB1 not touched. |

## Findings

| id | severity | location | evidence | required change |
|---|---|---|---|---|
| F-1 | **MATERIAL** | `xr_admit.py` `preflight_passed` (l. 375–385); `xr_run.py` `preflight()` (l. 284–286) | **Probe:** I ran `xr_run.py --run PF --require-provenance` by hand under the guard, outside any job (no `SLURM_*`, `OMP_NUM_THREADS=12`), in a hand-made `PF/a1`.<br>**Result:** `status=preflight-pass`, no `allocation_record`, `environment.slurm.SLURM_JOB_ID=None`, and `preflight_passed(...)` returned **True**, which releases L0.<br>**Cause:** the gate checks only schema, status, run, `fits==[]` and the admission digest. The allocation record is optional, and strict identity is not required (unlike `comparable`).<br>**Impact:** a PF job refused at `jobcheck` leaves `PF/a1` behind, and one hand-run on a login node turns the failure into a release. That defeats the grant's "if it fails, stop dependent execution" and the reason the preflight exists (E.3 item 3). No mutant or test covers it. | The release gate must accept only a receipt produced in the PF job. It must require all of:<br>• an `allocation_record` whose line passes `check_allocation` for the preflight kind;<br>• that line's `JobId` equal to the receipt's `SLURM_JOB_ID` and to the PF `job_id` in `submissions.jsonl`;<br>• `identity.strict` true;<br>• `exit_code` 0.<br>Add a test in the refusing direction (a passing receipt with no record, a mismatched record, or no SLURM job id does not release L0) and a mutant that removes the binding. |
| F-2 | MINOR | `xr_admit.py` `charge`/`ledger` (l. 454–457, 497–508) | **Probe:** an amendment job `xrr_X0_a1 COMPLETED ElapsedRaw=72000` with empty AllocTRES is charged 0.0, with `over=[]` and rc 0.<br>A missing AllocTRES column is caught only indirectly, through the mismatch with the recorded prior charge (rc 6).<br>The cap is still bounded by the per-attempt ceilings checked at submission, so this is not a budget breach. | The ledger must flag (exit 6) any job with `ElapsedRaw>0` and unreadable billing, and must require the `AllocTRES` and `ElapsedRaw` columns in the header. |
| F-3 | NOTE | `tests/scheduler/README.txt` | **Running lines:** none of the account's own jobs was running, so I read 3 real RUNNING lines from other accounts' jobs (59654680, 59561880, 59577585; not stored). They have the same field shape as the substituted `running_line`: `AllocTRES=cpu=…,mem=…,node=1,billing=N`, no `TRES=`, no duplicate keys among 64–68. In 2 of the 3, ReqTRES differs from AllocTRES, which supports reading AllocTRES.<br>**Completed jobs:** SB1's completed sacct rows now carry an `energy=` item. The fixtures lack it; `parse_billing` handles it. | Have the final verification parse the preflight's own recorded `scontrol-job.txt` as the first captured RUNNING line of this account. |
| F-4 | NOTE | `comparable` / `xr_compare.newest_complete` | Run receipts are not bound to a scheduler job id either. This predates the delta, and a hand-run of L0 (64 threads, about 1 h) is implausible. | None required. The final verification should check that each receipt's `SLURM_JOB_ID` matches `submissions.jsonl` and sacct. |

## What I verified, with operands

1. **Allocation parsing**
   - **Code read:** `scontrol_field` is a regex `(?:^|\s)KEY=(\S*)` that requires exactly one hit. `parse_billing` refuses on absent, `(null)`, a non-`k=v` item, a repeated billing, or a non-integer billing. `check_allocation` reads JobId, QOS, NumCPUs, TimeLimit and AllocTRES; billing comes from AllocTRES only.
   - **Real RUNNING lines:** the 3 live lines pass under kinds built from their own values, and refuse when billing, CPUs, time or QOS is one below or wrong, or the JobId is wrong. The old `TRES` dict parse returns None on all 3.
   - **SubmitLine:** for xrr jobs it holds `--qos=…`, `--job-name=…` and the positional args. None of these is a whitespace-preceded `KEY=` of a parsed field. Injected duplicates refuse (tested), so free text can only cause a refusal, never an acceptance.
   - **Fixtures:** all 5 match the cluster capture dir `xrr-capture.Fs7P` byte-for-byte (sha256 `f19e1236…`, `46c20a60…`, `f67f6495…`, `613eb804…`, `fa43b040…`). SB1's 59645304/05 have finished (sacct: COMPLETED), so a live scontrol re-read was impossible.
2. **Fixtures and the other parsers**
   - `scontrol_line`/`running_line` substitute only named fields, each asserted to occur once.
   - **Mutant `tres-field-restored`:** caught. Rerun by hand, the valid line refuses with `billing: False`, the exact B7 signature, in both the Scheduler test and the jobcheck end-to-end test.
   - **`check_prior` and `sacct_jobs` on live sacct** (`-u josephrb -X -n -P -S 2026-10-10 -E now`): they pass; 5 `xr_*` jobs and 0 `xrr_*`.
3. **Preflight**
   - **Path:** `xr_job.sbatch` runs jobcheck (with the record), then verify, sources the setup, and runs under the guard. In `xr_run.py`: helper plus both drivers loaded from verified bytes, strict identity, both inputs hashed, environment check, loky seed, fit recorder (refuses every fit), OMP check, identity recheck, input stat recheck, then the receipt. There is no `main()`, no `.root` and no `receipt.json`.
   - **Receipt:** `xr-preflight-receipt/1` in `preflight-receipt.json`. `comparable` and `newest_complete` reject anything other than `xr-receipt/2`, and reject `kind=preflight` (2 mutants).
   - **Timing:** on login23, hashing the 2.14 GB input took 9.2 s with `sha256sum` and 2.8 s with Python hashlib (warm page cache, `43f8cc16…` matches). The prior jobs reached their jobcheck refusal in 4–19 s.
   - **Estimate:** setup, ROOT and package imports (not measured) should take under 2 min. 5 min at 12 CPUs is adequate, with about 2× margin.
4. **Freeze, against `06eae0fe`**
   - Unchanged: `references.json`, and in `runs.json` the comparisons, controls, criterion (1e-8, cell identity), inputs, environment, all five run specs and the exact/lgbm kinds.
   - The only verdict-logic change in `xr_compare.py` is the added preflight-receipt refusal.
   - The `88e8dc35` and `06eae0fe` package trees are identical.
   - New outroot `/pscratch/sd/j/josephrb/xr-recovery-20261011` does not exist yet, and `draft` refuses the prior outroot.
5. **Accounting**
   - **Prior charge from live sacct:** (12·45 + 64·11)/(256·3600) = 0.0013498263888888891. This equals the recorded value exactly; computed both locally and under 3.6.
   - **Planned ceiling:** 0.00134983 + 0.00390625 + 5.625 + 0.75 = 6.38025608 ≤ 6.4.
   - **Attempt caps:** max(attempt dirs, submissions, sacct `xrr_*` since 2026-10-10). Changing the date makes `check_prior` refuse (mutant `submit-window-reset` caught).
   - **Release order and window:** PF→L0→rest and the 72 h from the first (PF) submission are enforced in `next_attempt`. Under 3.6 on login23, PF gets attempt 1 with deadline 2026-10-13T18:55:09 (local time, +72 h), and L0 is refused ("no passed preflight").
6. **Negative controls**
   - The record lists 53 mutants, all caught (46 failures, 7 errors).
   - I reran 8: `tres-field-restored`, `dict-parse-restored`, `null-allocation-accepted`, `malformed-billing-accepted`, `jobid-unchecked`, `preflight-receipt-comparable`, `comparator-preflight-accepted`, `submit-window-reset`. All were caught, and the files were restored.
   - Uncovered defects found: F-1 and F-2.
7. **Suite:** 40 tests, OK, 169 s, rc 0.
8. **Python 3.6:** `xr_admit.py` (sha256 `d8c6bb8d…`) compiles and runs on `/usr/bin/python3` 3.6.15: `check_allocation`, `seconds`, `parse_billing`, `charge`, `sacct_jobs`, `check_prior`, `next_attempt` and `ledger` (rc 0) on live scheduler output.
9. **Hygiene:** the delta contains no data-event values or counts. The UID in the fixtures already appears on main.

## What I could not verify

- An `scontrol -o` line of this account's own RUNNING job: none existed, and SB1's jobs had left `scontrol`.
- In-job time for the setup `source` and the ROOT/sklearn/lightgbm imports (estimated only).
- The cold-cache CFS read rate from a compute node.
- `xr_submit.sh` against the real `sbatch`; it is tested only with stubs.
