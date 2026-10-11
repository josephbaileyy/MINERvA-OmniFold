# XR recovery: the repaired package, its admission, the preflight and the five XR runs

**CITABLE FOR:**
- the repaired XR launch package and its tests;
- its admission evidence and the in-allocation preflight;
- the scheduler record;
- the five runs' comparisons against the frozen 1e-8 criterion;
- the independent numerical verification.

**NOT CITABLE FOR:**
- any cross section, uncertainty, coverage or calibration result;
- a re-quote, an adoption, a narrowed claim or a changed gate;
- seed invariance in general, or a resolution of the 2D pairing issue;
- an uncertainty transfer;
- compute authority beyond `AUTHORIZATION-20261011-xr-recovery.md`.

| field | content |
|---|---|
| `Lane` | `xr-recovery` (owner of the XR package's scoped repair and this record) |
| `Decision` | Can the repaired, correctly admitted package answer the original central-reproduction and one-seed comparison questions? |
| `Branch` / `Base` | `prep/xr-recovery-20261011` / `88e8dc3587c7f743eefa6809dfc11bb85b907073` (the delivered `prep/two-d-followup-20261010` head, PR #74, unmerged; `origin/main` at `ced3a8db` holds neither) |
| `Owned files` | `Q/two-d-followup/xr/` (the package and its tests; repaired in place, the old package preserved at `06eae0fe`); `Q/xr-recovery/` (this record); `docs/orchestration/AUTHORIZATION-20261011-xr-recovery.md` and its scoped registration (one `MANIFEST-overrides.tsv` row, one `CATALOG.md` row) |
| `Owner / reviewer` | One owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code. One fresh read-only reviewer: Claude Opus 5.5, a general-purpose subagent. The campaign review's suggested Astra High reviewer is not available in this session |
| `Review budget` | 1 admission review, 1 final numerical verification, at most 1 focused repair/re-review |
| `Terminal outcomes` | admission, preflight, execution and each comparison are each PASS, FAIL or INCONCLUSIVE (§10). A failed preflight stops dependent execution; the window is 72 h from the preflight submission |

`Q` = `docs/orchestration/state/next-preparation-20261009`. The prior record is `Q/two-d-followup/REPORT.md` (B7, B8, E.3), with its final verification `Q/two-d-followup/review/final-verification-eb145ba6.md`.

## 1. Answer

**INCONCLUSIVE.** The repaired package was correctly admitted. Its preflight then found a second, independent infrastructure defect inside the real allocation: every one of the five runs would hit it before its first fit. As the grant requires, dependent execution stopped. No run was launched, and every scientific comparison is INCONCLUSIVE. The answer to the decision is therefore: **not yet**. This package, as admitted, cannot answer the central-reproduction or the one-seed questions. §9 lists exactly what would let it.

| object | outcome |
|---|---|
| admission | **PASS**: ADMIT WITH CHANGES at `57b7403c`, then one repair batch, then ADMIT at `07428e5d` (§4) |
| preflight (PF, job 59655414) | **FAIL**: `check_environment` → `threadpoolctl.threadpool_info()` → `find_library("c")` → `/sbin/ldconfig -p`, which the OI-136 guard refused (§6) |
| execution (L0, then X0, X0′, X1, L1) | **INCONCLUSIVE**: not launched (the grant's stop on a failed preflight); the release gate refused it as well (§6) |
| X0_vs_E_C, X0p_vs_E_C, X1_vs_X0, L0_vs_CV42, L0_vs_PN_CV, L1_vs_SEED1 | **INCONCLUSIVE** each (no run) |
| NC_X0_vs_CV42 (negative control) | **INCONCLUSIVE** (not exercised) |
| final numerical verification (use 3) | §8 |

**What the preflight did establish, in the allocation, on the real scheduler.** The parts below passed, which means the original TRES defect is repaired in situ:
- The repaired allocation check passed on this account's first captured RUNNING line (`AllocTRES=cpu=12,mem=22860M,node=1,billing=12`; no `TRES=` token).
- The admission verified.
- The setup sourced.
- The guard started.
- The helper and both drivers loaded from verified bytes, under strict provenance.
- Both inputs hashed to their frozen digests.
- Every import and the frozen-version comparison in `check_environment` passed.

What never ran in an allocation:
- the threadpool record;
- the loky core-count seed;
- the fit recorder's installation;
- the thread-count check;
- anything in the fit path.

## 2. Baseline and preservation

- **Refreshed refs:** `origin/main` `ced3a8db` (PR #73); `origin/prep/two-d-followup-20261010` `88e8dc35` (PR #74, open draft, unmerged).
  - This branch is based on `88e8dc35`, so the review diff shows only the recovery.
  - Isolated local worktree `MINERvA-OmniFold-xr-recovery-20261011`.
- **Preserved, unchanged:**
  - the old package at `06eae0fe`;
  - its authorization `AUTHORIZATION-20261010-xr.md`;
  - the failed-run records, results and reviews in `Q/two-d-followup/` at `eb145ba6`/`88e8dc35`;
  - the prior outroot `/pscratch/sd/j/josephrb/xr-two-d-followup-20261010` (12 files; admission `ef8b49b3…` and submissions `4d673e7c…` re-hashed at 02:32Z);
  - the prior cluster worktree `MINERvA-OmniFold-xr-b838fc02`.
- **Untouched:** SB1's checkout `MINERvA-OmniFold-sb1-2b35ba52`, its package, environment and outputs. Its two pending jobs finished on their own before XR deployed (`squeue --me` empty at 02:32Z and at every later read).
- **Read for this assignment:** `AGENTS.md`, `CAMPAIGN-REVIEW-20260929.md`, the committed XR authorization, and the two-d-followup REPORT B7–B8 and E.3 with its final verification.
  - `CURRENT_WORK.md` on main has no XR row; the two-d-followup row is a proposed update awaiting its owner.

## 3. The repair (package `Q/two-d-followup/xr/`, repaired in place)

Each grant item, with what was done (code at `07428e5d`):

1. **AllocTRES, parsed explicitly, fail-closed.**
   - `xr_admit.py` `scontrol_field` returns a named field and requires it exactly once.
     - `SubmitLine=` carries the sbatch argv after the scheduler's fields, so the old whole-line dict let a later token stand in for a field.
   - `parse_billing` returns None for an absent, empty, `(null)`, malformed, repeated or non-integer billing.
   - `check_allocation` reads JobId, QOS, NumCPUs, TimeLimit and AllocTRES, and refuses on any failure.
   - `jobcheck --record` writes the raw line first (exclusively), so a refused allocation is still on record.
2. **Real scheduler formats.**
   - `tests/scheduler/` holds byte-for-byte captures from 2026-10-11T00:55:14Z: two pending `scontrol -o` lines and three `sacct` formats (README there).
   - No RUNNING line of this account existed. A running form substitutes named fields only, each asserted to occur once, with the AllocTRES that `scontrol` printed for the finished 59648617.
   - The reviewer checked three live RUNNING lines of other accounts: same field shape.
   - The preflight's own line, `results/scontrol-job-59655414.txt`, is now the first captured RUNNING line of this account. It parses as the substitution assumed.
   - Tests cover: a valid allocation; excessive billing; a pending `(null)` allocation; malformed output (no billing, non-numeric, empty, repeated, absent, duplicated via `SubmitLine`, another job, `UNLIMITED`, empty output); and the old fixture's format.
   - The old parser's regression is mutant `tres-field-restored`. It is caught.
   - `sacct_jobs`, `check_prior` and the ledger's AllocTRES/ElapsedRaw are tested on the captured sacct output.
3. **Preflight `PF`** (kind `preflight`: shared, 12 CPUs, 22,860M, 5 min, one attempt).
   - It runs through the real `xr_job.sbatch`: allocation check, admission verification, setup, guard, then `xr_run.py --run PF`.
   - In order, `xr_run.py --run PF` does:
     - loads the helper and the drivers of all five runs from verified bytes, with strict identity;
     - hashes both inputs;
     - `check_environment`;
     - the loky seed;
     - installs a fit recorder that refuses every fit;
     - checks the thread count;
     - rechecks the identity and the input stats;
     - writes `preflight-receipt.json` (`xr-preflight-receipt/1`, carrying `not_a_result`).
   - It never calls a driver's `main`, and writes no histogram and no `receipt.json`.
   - The comparator and the release gate accept only `xr-receipt/2`, never a preflight receipt.
4. **Freeze.**
   - Package `07428e5dec9fecd2e1148d8a2bdabc139a35138f`, manifest `07a74b914329c8286b1434619976c246a7543e7643f3f8b2f4792a7ad0a950d6`.
   - Outroot `/pscratch/sd/j/josephrb/xr-recovery-20261011`; `draft` refuses the prior one.
   - Unchanged against `06eae0fe`, checked by the owner and by both reviews: `references.json`; and in `runs.json` the criterion (1e-8, cell identity), inputs, environment, the five run specs, the exact/LightGBM kinds, the comparisons and the control.
   - The only change to the comparator's verdict logic is the preflight-receipt refusal.
5. **Cumulative accounting.**
   - This amendment's jobs are `xrr_<RUN>_a<N>`, and its caps count only them: attempt directories, submissions, and `sacct` since `cumulative_since` 2026-10-10.
   - `sacct` must show exactly the prior five `xr_*` jobs (`check_prior`).
   - Their charge, recomputed by every ledger, must equal the recorded 0.0013498263888889. It enters every planned ceiling: prior + Σ ceilings of submitted attempts + this one ≤ 6.4 (planned maximum 6.3802560763888889).
   - Release order PF → L0 → the rest is enforced by `next-attempt`.
   - The 72-h window starts at the first submission, which is the preflight's.

## 4. Admission (review uses 1 and 2)

- **Admission review at `57b7403c`: ADMIT WITH CHANGES** (`review/admission-review-57b7403c.md`, verbatim).
  - F-1 MATERIAL: a preflight run by hand outside the job wrote a passing receipt that released L0.
  - F-2 MINOR: the ledger charged 0 for a job with unreadable billing.
  - F-3 and F-4 are notes.
  - The reviewer read live scheduler operands: three RUNNING lines, live sacct, the prior charge recomputed to 0.0013498263888888891. It reran 8 mutants and timed the input hash on login23 (9.2 s `sha256sum`, 2.8 s hashlib).
- **One repair batch, `07428e5d`.**
  - The gate now also requires exit 0, strict identity, the receipt's `SLURM_JOB_ID` equal to the PF submission's job id, and the job's recorded `scontrol-job.txt` (at the receipt's digest) passing the preflight allocation check.
  - Tests in the refusing direction: the hand-run probe, nine unbound or mismatched receipts, and an edited record.
  - The ledger flags unreadable billing and a header lacking a required column.
  - 7 new mutants.
- **Focused re-review at `07428e5d`: ADMIT** (`review/rereview-07428e5d.md`, verbatim).
  - F-1 REPAIRED.
  - F-2 PARTIAL: N-1 MINOR, not repaired, since no repair round remains. A header lacking `State` or `JobName` makes the ledger crash (rc 1, still fail-closed) instead of exiting 6.
  - N-2 NOTE: a deliberately forged environment and allocation line would pass the gate. This is outside the threat model.
- **Authorization:** `AUTHORIZATION-20261011-xr-recovery.md` quotes the grant verbatim and binds `07428e5d`/`07a74b91…`. It is committed at `9ec77fa1` with its two registration rows.

## 5. Tests and negative controls

| object | result |
|---|---|
| suite at `57b7403c` | 40 tests OK (`logs/xr-tests.txt`) |
| mutants at `57b7403c` | **53 of 53 caught**, 28:27 wall (`logs/xr-mutation-results.json`) |
| suite at `07428e5d` | 42 tests OK, 2:51 wall (`logs/xr-tests-repair.txt`) |
| mutants at `07428e5d` | **60 of 60 caught**, 28:26 wall (`logs/xr-mutation-results-repair.json`) |

- Package bytes were digest-checked before and after both mutation runs.
- Scheduler, accounting and preflight tests run in a light class (`Launch`, no training), so their 31 mutants run in seconds.
- **Limit.** The suite runs on macOS. `ctypes.util.find_library` takes no `ldconfig` path there, so no local test or mutant could see the §6 defect. Only a Linux run under the guard could, and that is what the preflight was for.

## 6. Deployment and the preflight

All of it is in `logs/xr-deploy.txt`, with values as printed.

**Deployment.**
- **Isolated pinned worktree:** `/pscratch/sd/j/josephrb/MINERvA-OmniFold-xrr-9ec77fa1` at `9ec77fa1`, 0 status lines. The canonical checkout stayed at `32e403b8` and was not moved.
- **Checks under `/usr/bin/python3` 3.6.15:** `manifest --check` current; `check` holds; `jobcheck` outside a job gives rc 3.
- **Admission:** `draft` wrote `admission.json` (sha256 `4563871f…`), and `verify` held.
- **Ledger before launch:** prior 0.0013498263888888891 recomputed from live sacct, equal to the recorded value.
- **Re-measured before launch** (02:39:47Z):
  - billing equals CPUs (`shared_milan_ss11` TRES `cpu=17920…billing=17920`; 1905 MB per CPU);
  - QOS shared MaxWall 2 days;
  - m3246 charged 16,981.9 of 20,000;
  - no queued jobs.
- **Coexistence with SB1:** SB1 had no queued job, and XR shares no mutable path with it.

**Preflight.**
- **Submitted:** `xr_submit.sh <adm> PF` at **2026-10-11T02:40:04Z**, as job **59655414** (`xrr_PF_a1`, shared, 12 CPUs, billing 12, `TimeLimit=00:05:00`, Deadline 2026-10-13T19:40:00 PDT). The window's stop is 2026-10-14T02:40:04Z.
- **Ran:** 03:11:26–03:12:32Z on nid004073, after 31 min in the queue.
- **sacct:** `FAILED`, ElapsedRaw 74, `billing=12`, exit 1.

What passed in the allocation:
- `jobcheck`, on its own RUNNING line;
- `verify`;
- the setup;
- the guard;
- strict identity over the six executed files: the helper `e9623412…`, today's driver `3cc5adc7…`, the `d1bc8813` record `447288e2…`, `n2` ×2 and `xr_run.py`;
- both inputs hashed (omnifile `43f8cc16…`, 2,144,008,221 B; mcfile `d40aea69…`);
- every import and version comparison in `check_environment`.

**The failure, exact** (traced read-only on login23 with `subprocess.Popen` spied: no guard, no job, about 10 s).
- **What happens:** `xr_run.py` `check_environment` ends with `have["threadpools"] = threadpoolctl.threadpool_info()`. In threadpoolctl 3.6.0 the chain is:
  1. `ThreadpoolController._load_libraries`;
  2. `_find_libraries_with_dl_iterate_phdr`;
  3. `_get_libc`, which calls `ctypes.CDLL(find_library("c"))`;
  4. on Linux, `ctypes/util.py` `_findSoname_ldconfig` runs `subprocess.Popen(['/sbin/ldconfig', '-p'])`.
- **The guard's refusal:** the OI-136 guard refuses that child (`/sbin/ldconfig` "is neither an interpreter, a shell, a leaf tool nor a script with a readable shebang"). It raises `SystemExit(3)`, which the preflight recorded as `preflight-fail`, `SystemExit: 3`, exit 1. No fit was attempted (`fits: []`).
- **The trace:** the spy counted 0 child launches across `import ROOT`, threadpoolctl, numpy, sklearn, lightgbm, joblib, scipy and `gROOT.GetVersion()`, and 1 launch in `threadpool_info()`.
- **Consequence:** every scientific run calls the same `check_environment` before its first fit (`xr_run.py` `main`, before `driver.main()`). All five would have failed this way about a minute into their allocation (PF: 47 s in `xr_run.py`), after their queue wait. The charge at risk was minutes per run, not their 30-h limits (V-1).
- **The guard behaved correctly.** Its own message says not to widen its leaf table. The defect is XR's call.

**After the failure** (03:16:02Z).
- `next-attempt` refuses L0 and X0 ("no passed preflight for this admission"), and refuses PF (1 of 1 preflight attempts used).
- The comparator gives all seven INCONCLUSIVE.
- No job queued, nothing to cancel. No further submission was made.

## 7. Comparisons

No run produced a histogram, so there is nothing to reproduce from output histograms. The frozen comparator's `results/comparisons-post.json` records INCONCLUSIVE ("no complete attempt") for X0_vs_E_C, X0p_vs_E_C, X1_vs_X0, L0_vs_CV42, L0_vs_PN_CV, L1_vs_SEED1 and NC_X0_vs_CV42. There are no maxima and no affected cells, and the pre-registered thread-count check did not arise.

## 8. Independent numerical verification (use 3 of 3)

Preserved verbatim in `review/final-verification-204805d8.md`. The same reviewer worked read-only at `204805d8`, 2026-10-11T03:19:40–03:23:50Z, under 0.01 local core-hours, with login23 reads only.

- **Admission, as recorded: CONFIRMED.**
- **Preflight: FAIL confirmed, and the stated defect is the cause.** The reviewer reproduced it on login23: one launch, from `threadpool_info()`, and none from the imports, the loky seed or the fit-recorder imports.
- **Execution: INCONCLUSIVE (not launched), confirmed.** The only `xrr_*` job is 59655414. The outroot holds no `receipt.json`, no `.root` file and no run directory other than `PF/a1`.
- **All seven comparisons: INCONCLUSIVE.** The frozen comparator was rerun on the live outroot.
- **Numerical verification overall: CONFIRMED WITH DISCREPANCIES** (V-1 to V-3, all MINOR wording or completeness).

What the reviewer re-derived:
- the cumulative charge from sacct, 0.0023133680555555555;
- every digest in `PF/a1`;
- F-3: the job's own RUNNING line, byte-equal to the tracked copy, parses under `check_allocation`;
- F-4/N-2: the receipt `SLURM_JOB_ID`, the line's JobId, the submission and sacct all agree (59655414);
- all six release refusals (`next-attempt` for L0, X0, X0p, X1, L1, PF: rc 3);
- the window;
- the §9–§10 arithmetic;
- the data hygiene.

**Post-verification corrections.** These are documentary only: nothing under `xr/` changed, and no review remains, so they are not re-reviewed.
- V-1: §6 now says the failure would come about a minute into each allocation, not after 30 h.
- V-2: §9 item 2 now requires the whole PF path and the end-to-end fixture tests on Linux under the guard.
- V-3: §9 item 1 now requires a child-free replacement for the thread-pool record.
- V-4 (a fit-path probe found no launch, indicative only) is added to §9 item 3.
- V-5 and V-6 are notes.

## 9. Reopening requirements (a new grant; not within this one: its single preflight is spent)

1. **Remove the child launch from `check_environment`.** Record the thread pools without starting a process: no `threadpoolctl.threadpool_info()`, and nothing else that reaches `ctypes.util.find_library` on Linux. The guard must not be widened. State what child-free evidence of the BLAS/OpenMP pools replaces the dropped record, for example the loaded libraries from `/proc/self/maps` plus the thread environment. The pre-registered L-arm thread-count check reads the receipt's thread record (V-3).
2. **Exercise the whole Linux path before admission (V-2).** Run the full PF code path under the OI-136 guard on Linux in the frozen environment. That path is `check_environment`, `seed_loky_cache`, the fit recorder's installation, the OMP check, `gx.recheck` and the input recheck. Also run the package's own end-to-end fixture tests there (all five runs, with fits, under the guard). This closes the gap the macOS suite has (§5) and covers item 3's fit path on fixtures. Add a test or mutant that fails if a child launch reappears.
3. **Audit the fit path for child launches.** The verifier's unguarded login-node probe of the four classes' `fit`/`predict` on tiny data launched no child (V-4). That lowers the risk without removing it: the probe skipped the driver's own code, ran without the guard and used tiny data. Decide whether the next preflight may include a fit, for example a tiny fixture fit under the guard in the allocation. That is the only way to see whether sklearn's exact GBT or LightGBM launch a child on Linux, as loky's `lscpu` did (which XR's seed handles). This grant's preflight forbids fits. Without that decision, the risk remains for the exact runs (up to 30 h each).
4. **One new preflight attempt and a new 72-h window.** The cumulative budget remaining is 6.4 − 0.0023134 = 6.3977 node-h. The planned ceiling with a second preflight is 0.0023134 + 0.0039063 + 5.625 + 0.75 = 6.3812 ≤ 6.4.
5. **A new package commit, manifest and outroot,** and an independent admission review of the delta with its own budget. Carry N-1 (ledger header check before reading any row).
6. **Unchanged:** the comparisons, the 1e-8 criterion, the control, the references and the release order.

## 10. Resources

**Remote (m3246), from sacct and the cumulative ledger** (`results/ledger-post.txt`, `results/sacct-post.psv`).

| item | limit | used |
|---|---|---|
| charged CPU node-hours, cumulative | 6.4 | **0.002313368055555556**: prior five 0.0013498263888888891 + PF 0.0009635416666666667 (74 s × 12/256) |
| GPU / full-node substitution | 0 / none | 0 / none |
| preflight jobs | 1, ≤ 5 min at ≤ 12/256 | **1** (FAILED at 74 s, billing 12) |
| exact jobs | 4, ≤ 30 h at ≤ 12/256 | **0** |
| LightGBM jobs | 3, ≤ 1 h at ≤ 64/256 | **0** |
| window | 72 h from 02:40:04Z | the PF ended 0.54 h after its submission; nothing cancelled |

- **Remote storage:**
  - worktree `MINERvA-OmniFold-xrr-9ec77fa1`;
  - outroot `xr-recovery-20261011` (admission, submissions, `PF/a1` with 5 files);
  - reduction and capture directories `xrr-reduce.41iU` and `xrr-capture.Fs7P`.
  - All of it is left in place as evidence.
- **Login-node work:** read-only reads, captures, the worktree, the admission tools, one comparator run, and one ~10 s spy trace. All of it took seconds.

**Local.**

| item | limit | used |
|---|---|---|
| active hours | 6 (last quarter protected) | grant 00:52:24Z; ≈ 2.5 h at 03:20Z. The value at delivery is in the commit message |
| local CPU core-hours | 3 | **≈ 1.4** before the final verification (itemized below) |
| local compute threads | 2 | ≤ 2 processes (mutation runs ~105 % CPU) |
| RAM | 8 GiB | not instrumented; the largest were the suite's small-fixture trainings |
| new local scratch | 3 GiB | ≈ 8 MiB (`scratchpad/xrr`; the test TMPDIR is emptied after each run) |
| tracked evidence | 20 MiB | `Q/xr-recovery/` 0.13 MiB, plus `tests/scheduler/` 5 KiB |

Local CPU items, all `user+sys`:
- 4 full suites: 616 s;
- 3 fast-class runs: about 90 s;
- the 53-mutant run: 1,784 s;
- the 60-mutant run: 1,813 s;
- the reviewer: about 0.07 + 0.08 h, self-reported;
- miscellaneous: ≤ 0.05 h.

## 11. Limitations, held items and proposed shared-status updates (for their owners; not applied)

- **Held untracked:** `admission.json`, `PF/a1/preflight-receipt.json` and `inventory.jsonl`. They carry path+sha256 pairs (live receipt bindings for the shared pre-commit inventory). Their digests and key fields are in `results/preflight-summary.txt` and `logs/xr-deploy.txt`.
- **N-1 and N-2 are open** (§4).
- **The fit path is unexercised in an allocation** (§9 item 3).

| owner | proposed update |
|---|---|
| `CURRENT_WORK.md` / integration owner | the `xr-recovery` row: admission PASS; preflight FAIL (threadpoolctl → ldconfig under the guard); execution and all comparisons INCONCLUSIVE; cumulative 0.0023 of 6.4 node-h; no follow-on authorized |
| OI-136 owner | `threadpoolctl.threadpool_info()` (3.6.0) launches `/sbin/ldconfig -p` on Linux through `ctypes.util.find_library`. Any guarded code that inspects thread pools will be refused. This is a property of the environment, not a guard defect |
| 2D estimator owner | none from this record; the X0/X0′/X1 questions remain open |
