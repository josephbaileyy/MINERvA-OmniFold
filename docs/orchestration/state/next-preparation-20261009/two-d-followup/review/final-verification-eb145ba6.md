# XR final numerical verification: `two-d-followup` at eb145ba6 (review use 3 of 3)

| field | value |
|---|---|
| Reviewer | the same fresh read-only independent reviewer (Claude Opus 5.5, `claude-opus-5-5`); this is the last of the three allowed uses |
| Fixed commit | `eb145ba6e5fade81c1183ee5f634e98616d32177`. Nothing under `xr/` changed since `06eae0fe` (checked with `git diff --quiet`). |
| UTC start / end | 2026-10-11T00:33:37Z / 2026-10-11T00:35:47Z (as printed by the local `date` at worktree creation and removal) |
| Worktree | detached at `…/fu/verify-wt`. `git status --porcelain --untracked-files=all`: 0 lines at start, 0 at end. Removed with `git worktree remove`. |
| Resources | under 0.01 local core-hours, one process. About 8 read-only ssh sessions to login23. The only cluster-side output was the frozen comparator writing to `/dev/stdout`; no files were written. No jobs, submissions or cancellations. |

## Verdicts

- **(i) Task A method: PASS.** A-5 is addressed: §E.2 states the narrowest change that would reopen the objective, and §B6–§E exist. With A-1 to A-4 and A-6 to A-8 already repaired, no Task A finding remains open.
- **(ii) XR admission review outcome as recorded: CONFIRMED.** B6 and D accurately record my re-review's ADMIT at `06eae0fe`. That admission missed a MATERIAL defect (F-1).
- **(iii) XR deployment: FAIL CONFIRMED.** All five admitted jobs were refused at the in-job allocation check because of a package defect. No fit ran.
- **(iv) Comparisons** (re-derived independently by rerunning the frozen comparator on the cluster):

| comparison | outcome |
|---|---|
| X0_vs_E_C | INCONCLUSIVE |
| X0p_vs_E_C | INCONCLUSIVE |
| X1_vs_X0 | INCONCLUSIVE |
| L0_vs_CV42 | INCONCLUSIVE |
| L0_vs_PN_CV | INCONCLUSIVE |
| L1_vs_SEED1 | INCONCLUSIVE |
| NC_X0_vs_CV42 (negative control) | INCONCLUSIVE, not exercised |

- **(v) Numerical verification overall: CONFIRMED WITH DISCREPANCIES.** Every outcome number reproduces. The discrepancies are documentary: F-2 to F-5.

## Checks

| # | check | evidence | result |
|---|---|---|---|
| 1 | sacct for the five jobs | `sacct -X -j 59648608,…617`: all `FAILED`, ExitCode `3:0`, ElapsedRaw 19/19/7/7/4. AllocTRES billing 12/12/12/64/64 (cpu = billing; mem 22860M / 121920M). QOS `shared`, partition `shared_milan_ss11`, limits 1-06:00:00 / 01:00:00. | identical to `results/xr/sacct.psv` |
| 2 | Job logs | All 10 `.out`/`.err` sha256 under the outroot equal the digests in `joblogs.txt`. The `.err` contents show `billing: False` and `TRES=None`. | match |
| 3 | Nothing beyond the logs | `find` over the outroot shows only `admission.json`, `submissions.jsonl`, and one `.out` and one `.err` per `<run>/a1/`. No `receipt.json`, no `inventory.jsonl`, no output ROOT file. | confirmed: no receipt, no fit |
| 4 | Queue | `squeue --me` shows only `sb1_C` and `sb1_H1` PENDING. sacct since 2026-10-10 lists exactly the five `xr_*` jobs, all FAILED. | none queued or running |
| 5 | `submissions.jsonl` | cluster sha256 `4d673e7c…` = committed file | match |
| 6 | Admission | cluster sha256 `ef8b49b3…`, 7,029 B | = README.txt |
| 7 | Deployed worktree | `MINERvA-OmniFold-xr-b838fc02` is at HEAD `b838fc02` with 0 status lines, and its `xr/` is identical to `06eae0fe`. The canonical checkout is still at `32e403b8`. | confirmed |
| 8 | scontrol field names | On my visible job 59645304 (`sb1_C`): `QOS=`, `TimeLimit=`, `NumCPUs=`, `ReqTRES=cpu=64,mem=121920M,node=1,billing=64`, `AllocTRES=(null)` (pending), and no `TRES=` key. | root cause confirmed |
| 9 | Code path and fixture | `xr_admit.py:241–243` reads `f.get("TRES","")`, so billing is None and the clause is False. `tests/test_xr.py:543` makes the fake scontrol print `TRES={tres}`. | confirmed |
| 10 | Order inside the job | `xr_job.sbatch`: `field` reads of the admission (system python, json only), an `echo`, then `jobcheck`, which fails and exits 3. `verify`, `source`, the guard and `xr_run.py` come after it. | nothing else ran |
| 11 | Ledger sum | Σ billing/256 × ElapsedRaw/3600 = [12·(19+19+7) + 64·(7+4)] / 921,600 = 1,244 / 921,600 = **0.0013498** node-h | = ledger.txt |
| 12 | Attempts used | exact 3 of 4 (X0, X0p, X1), LightGBM 2 of 3 (L0, L1). Remaining: 1 and 1. | confirmed |
| 13 | 72-h stop | First submission 2026-10-10T22:34:53Z, so the stop is 2026-10-13T22:34:53Z = 15:34:53 PDT. That matches the scheduler deadlines; X0's 15:34:49 is earlier, which is conservative. The last job ended 17:23:56 PDT = 00:23:56Z, which is **1.8175 h** after the first submission. | never bound |
| 14 | §E.3 "≤ 4.72 node-h" | 3 × 30 × 12/256 = 4.21875 plus 2 × 1 × 64/256 = 0.5 gives **4.71875** | correct for one attempt per run (see F-3) |
| 15 | Comparator | Frozen `xr_compare.py` from the deployed worktree, root_6_28 Python, writing to `/dev/stdout`: all seven INCONCLUSIVE ("no complete attempt") | = comparisons.json |
| 16 | Allocation | iris m3246 charged 16,979.8 of 20,000, consistent with a negligible XR charge | consistent |
| 17 | §C local accounting | Items: 0.403 + ≤ 0.22 + ≈ 0.41 + 0.518 + 0.020 + ≈ 0.32 + 0.35 + ≤ 0.1 = **≈ 2.34**, against "≈ 2.4", so the total is fine. But the items marked "measured" add to 0.941, not the stated 1.25. | see F-4 |
| 18 | §C "reduction directory (5 small text files)" | The cluster directory holds 5 files, including `sacct-nextattempt.psv`. `xr-deploy.txt` says "4" because it was written before that read. | C is right; the log is stale |
| 19 | Other in-job steps: could they fail the same way? | **`verify` in a job:** real git and file hashing, and the same calls held on the login node. Low risk, but never run in an allocation. **`check_environment`:** its frozen values were measured from the real cluster environment, not a fixture. Low risk. **Loky seed:** its Linux branch never ran in any test (the fixture host is darwin). I ran its `/proc/cpuinfo` logic on login23 (EPYC 7713): 128 cores, equal to `lscpu --parse=core` (128). `physical_cores_cache` is the global that `_count_physical_cores` uses in joblib 1.5.3. Low risk. **xr_run's `SLURM_*` and `sched_getaffinity`:** recorded only, never compared. No refusal risk. **The guard under the cluster `PYTHONPATH`, with `source` under `set -e` in a job:** not fixture-derived, but never executed in an allocation (fail-closed if wrong). | only `jobcheck`'s `TRES` read was fixture-derived; the in-allocation preflight in §E.3 item 3 is warranted |
| 20 | Data hygiene of the delta | `git diff 06eae0fe eb145ba6 -- docs`: no data-event values or counts. The additions are scheduler records, digests, job logs (refusal messages) and REPORT text. | clean |

## Findings

| id | sev | location | finding | evidence |
|---|---|---|---|---|
| F-1 | MATERIAL (recorded, not repaired) | `xr_admit.py:243`; `tests/test_xr.py:543`; reviews 1 and 2 | The admitted package's in-job billing check reads a field Perlmutter does not print, so the check fails on every correct allocation. **This reviewer missed it in both reviews.** It was detectable read-only: one `scontrol show job <visible id> -o` on the login node shows `ReqTRES=`/`AllocTRES=` and no `TRES=`. I ran exactly that read now. | checks 8–9 |
| F-2 | MINOR | REPORT B7 ("Why no control saw it … Neither the 29 mutants nor either review could detect this") | This overstates the case. The mutants could not detect it, but the reviews could have (F-1). The sentence should read "did not detect", not "could not". | F-1 |
| F-3 | MINOR | REPORT §E.3 item 6 | "≤ 4.72 charged node-h" is the ceiling for one attempt per run. With the proposed caps of 4 exact and 3 LightGBM it is 6.375, plus the preflight (12/256 × ≤ 5 min ≈ 0.004). Both fit within the 6.4 that remains available. State which ceiling is meant. | check 14 |
| F-4 | MINOR | REPORT §C local table | "1.25 h was measured" does not reconcile with the items marked measured (0.403 + 0.518 + 0.020 = 0.941). The 19-mutant pass was also measured (`xr-mutation.txt` at `8378ec23`: user+sys 1,347 s = 0.374 h) but is listed as "≈". The total of ≈ 2.34–2.4 stands. | check 17 |
| F-5 | MINOR | REPORT B7 ("`next-attempt` … offers each run attempt 2"); §C | No committed log records this `next-attempt` run. Its input exists only on the cluster (`xr-reduce.4fPw/sacct-nextattempt.psv`), and `xr-deploy.txt`'s "4 small text files" predates it. The claim is plausible but not evidenced in the commit. | check 18 |
| F-6 | NOTE | REPORT B7 ("measured on 59648617") | Consistent with my read on another job (ReqTRES carries billing; AllocTRES is `(null)` while pending and set once running). §E.3 item 1's choice of `AllocTRES` inside a running job is right. `ReqTRES` would also carry billing. | check 8 |
| F-7 | NOTE | §E.3 item 3 (preflight) | To cover what never ran, the preflight should go through `xr_job.sbatch` itself: `source` of the setup in the job, the guard, the 2 GB CFS input hash in the job, then `check_environment` and the loky seed, stopping before the first fit. A stop-before-fit mode is new code and belongs to item 4's new package. It must use its own outroot or attempt namespace so it does not consume run attempts. | check 19 |
| F-8 | NOTE | `xr_admit.py:242` | `dict(t.split("=",1) for t in text.split())` splits values that contain spaces. Harmless for the fields used, but the repair should parse the named key explicitly. | code read |

## REPORT B7, B8, C, D, E.3, E.4: verdict words

- **D, "Task A — method: PASS WITH CHANGES … applied here":** with A-5 now applied, my final word is PASS.
- **D, "XR — admission review: PASS (ADMIT)" and "The admission did not catch a MATERIAL defect":** both correct.
- **D, "deployment: FAIL":** correct.
- **The seven INCONCLUSIVE outcomes:** correct, and the control is correctly marked "not exercised".
- **"No scientific status changes":** correct.
- **B7, "The parts that ran outside a job … did hold":**
  - Supported by `xr-deploy.txt` for `manifest --check`, `check`, `draft`, `verify` and `ledger`; the ledger parsed AllocTRES correctly (billing 12/64).
  - `next-attempt` is unevidenced (F-5).
  - The sentence is scoped "outside a job", so it does not overclaim.
- **§E.3 requirements:** AllocTRES as the field, a cluster-recorded fixture with a test in each direction and a TRES mutant, an in-allocation preflight, a new package, outroot, authorization and admission review, and caps over a new grant. These are complete and correct, with F-3 and F-7 added.
- **§E.2:** the narrowest reopening change is present and consistent with A5.
- **§E.4:** it is proposals only, and the content matches A4 and B1.

## What I could not verify

- The `jobcheck` repair working inside a running allocation (by design no job ran), and whether `AllocTRES` is populated at the moment the batch script starts. It is populated once a job is RUNNING; I saw it only as `(null)` on a pending job.
- Any in-allocation behaviour of `verify`, `check_environment`, the guard or the loky seed (§E.3 item 3).
- The authorization text against the grant: I did not compare `AUTHORIZATION-20261010-xr.md` (sha `4c469151…` quoted) with Joseph's original wording.
- The local core-hour items other than my own and the logged mutation and timing files.
