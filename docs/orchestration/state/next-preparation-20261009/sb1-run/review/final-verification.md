# SB1 final result verification: run/sb1-20261010 at 4cab15aa

**RESULT VERIFIED: PASS**

**RECORD: REPAIR NEEDED**

The repair needed is disclosure only. It changes no criterion, no number in a criterion and no verdict, and it needs no rerun. It is finding 1 (MATERIAL), plus findings 2 and 3 (MINOR).

## Setup facts

- **Reviewer.** The same read-only reviewer who did the admission review, on task 2 of 2.
- **UTC window.** Start 2026-10-11T01:52:06Z; end of checks 2026-10-11T01:57:27Z, review written just after.
- **Worktree.** `/private/tmp/sb1run-review-b`, detached at `4cab15aaccd33095f52fd3b1aa76381e19bebf00`.
  - `git status --porcelain --ignored` printed **0 lines** at start and **0 lines** at end.
  - The worktree and `/private/tmp/sb1run-review-scratch-b` are removed after this file is written.
  - Nothing was edited, committed or pushed in the repository or any existing worktree.
- **CPU.** Well under 0.05 core-h. I ran no test suites: only JSON parsing, a ROOT read of three 61-KB files, and the hash-binding gate. One process at a time.
- **Local environment.** ROOT 6.36.000 with Python 3.13.7 for S5. System Python 3.12.2 for the gate.
- **Cluster commands I ran.** All on login23, via `ssh -o BatchMode=yes saul.nersc.gov`, read-only:
  - `date`, `hostname`;
  - `find` plus `sha256sum` over the outroot and the operator directory, and `sha256sum` of the admission file;
  - `ls -la`;
  - `git rev-parse` and `git status --porcelain --ignored` in the frozen checkout, with `GIT_OPTIONAL_LOCKS=0`;
  - `sacct -e`;
  - `sacct -P --units=K --duplicates` for the six ids;
  - `sacct -u $USER -X -P --duplicates` from 2026-10-10T12:00 PDT;
  - `squeue --me -t all`;
  - `iris`;
  - `grep`/`sed` reads of LightGBM, joblib and loky source in the root_6_28 environment;
  - on the login node: `grep` of `/proc/cpuinfo`, `lscpu --parse=core` and `nproc`.
- **Cluster commands I did not run.** No sbatch, srun, salloc or scancel. Nothing was written on the cluster: scripts went through stdin, and no `$SCRATCH/tmp` files were created. The env setup was not sourced on the cluster, because S5 was read locally from hash-verified copies.

## Recomputed table, from my own fresh sacct

`sacct -P --units=K --duplicates`, read at 2026-10-11T01:52Z. Charge is billing / 256 × ElapsedRaw of the allocation row. Queue is Start − Eligible. MaxRSS and MaxDiskRead come from the batch step, in GB = 10⁹ B.

| job | id | state, exit | QOS | billing | ElapsedRaw s | node-h | ceiling | queue s | Restarts | GPU | MaxRSS GB | MaxDiskRead GB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 59645299 | COMPLETED 0:0 | shared | 2 | 929 | 0.002016 | 0.005859 | 365 | 0 | none | 3.9645 | 169.6165 |
| UL | 59645300 | COMPLETED 0:0 | regular_1 | 256 | 2604 | 0.723333 | 0.833333 | 3233 | 0 | none | 69.4598 | 171.2978 |
| SL | 59645301 | COMPLETED 0:0 | regular_1 | 256 | 888 | 0.246667 | 0.500000 | 764 | 0 | none | 17.1652 | 2.3578 |
| J1 | 59645302 | COMPLETED 0:0 | shared | 64 | 1793 | 0.124514 | 0.187500 | 3258 | 0 | none | 20.8179 | 173.8740 |
| C | 59645304 | COMPLETED 0:0 | shared | 64 | 948 | 0.065833 | 0.166667 | 2680 | 0 | none | 16.3714 | 6.5649 |
| H1 | 59645305 | COMPLETED 0:0 | shared | 2 | 180 | 0.000391 | 0.005859 | 457 | 0 | none | 1.8276 | 165.0070 |
| **total** | | | | | **7342** | **1.162754** | 1.699219 | **10757 (2.99 h)** | | | | |

- **Against the cap.** 1.162754 of 2.0 node-h, leaving 0.837246. Every job stayed under its own ceiling.
- **Wall span.** First submit to last end is 18,185 s.
- **No retries or duplicates.** Each id has exactly one allocation row under `--duplicates`, and Restarts = 0. There is no `gres/gpu` in any AllocTRES.
- **Ratios.**

  | criterion | SL | UL | ratio | verdict |
  |---|---|---|---|---|
  | S2, MaxDiskRead | 2.3578 GB (≤ 10) | 171.2978 GB | 0.01376 (≤ 0.1) | PASS |
  | S3, MaxRSS | 17.1652 GB (≤ 30) | 69.4598 GB | 0.24712 (≤ 0.5) | PASS |
  | S4, elapsed | 888 s | 2604 s | 0.34101 (≤ 0.5) | PASS |

- **Agreement with the tracked psv.** Every column of my 18 rows equals `evidence/scheduler/sacct-final.psv`: a field-by-field diff found 0 differences.

## Findings

1. **MATERIAL (record) — The OI-136 guard refused a child launch in both timed unfold jobs. The record calls all 15 inventories "clean" and never discloses it. The refusal very probably set LightGBM's thread count in UL and SL to 64, not 128.**
   - **What the inventories say.** `evidence/outroot/UL/inventory.jsonl` and `SL/inventory.jsonl` carry:
     - `outcome: "refused:launch-unmodelled-launch-grammar"` and `verdict: "REFUSED launch"`;
     - `offending_argv: ["lscpu","--parse=core"]`;
     - `refusal_site: "launch-python-startup-flags"`.

     The banner is in `sb1_UL_59645300.err:11-15` and `sb1_SL_59645301.err` (3 `lscpu` lines each). The other 13 inventories end `child-systemexit:0` or `:5`.
   - **Where the call comes from** (cluster source, read-only):
     - The helper builds `LGBMClassifier`/`LGBMRegressor` without `n_jobs` (`unbinned_unfolding/python/omnifold.py:209-220`).
     - LightGBM 4.6.0 then calls `_LGBMCpuCount(only_physical_cores=True)` (`lightgbm/sklearn.py:901-902`), which resolves to joblib's loky `cpu_count`.
     - In loky's `context.py`, the affinity check (lines ~120-121) applies only when the affinity is narrower than the node. In UL and SL the receipts show affinity = `os.cpu_count` = 256, so loky calls `_count_physical_cores_linux()`.
     - That function runs `lscpu --parse=core` (lines 267-276). On the guard's refusal, a bare `except` falls back to `cat /proc/cpuinfo` and counts the distinct `core id` lines.
   - **What that count gives.** On a dual-socket host it undercounts. I measured it on login23 (2 × EPYC 7713): distinct `core id` = **64**, but `lscpu --parse=core` gives **128**. Perlmutter CPU compute nodes are also dual-socket 64-core Milan, so UL and SL trained with LightGBM `num_threads` = 64, overriding `OMP_NUM_THREADS=128`. That is an inference: the receipts do not record the trainer's thread count, and `environment.packages` is null in every receipt.
   - **Effect on C.** None. Its affinity of 64 is below 256, so loky returns 64 without calling `lscpu`, and C's inventories show no refusal.
   - **Effect on the verdict.** None. P's frozen rule (sb1-prep REPORT §6.1) requires the guard installed on the admitted checkout alone with the manifest's shim. All 15 records satisfy it (`violation: null`, `allow` empty, 0 origins outside, `shim_sha256` = the manifest's), and refusing is the guard working. S4 compares UL and SL under the identical refusal and fallback, so the comparison is still matched.
   - **Effect on the record.** Three places need disclosure:
     - **REPORT.md:324** (P row): "all 15 guard inventories clean" is inaccurate as written.
     - **Lines 368 and 497:** the "128-thread rerun envelope" wording and the timing narrative (§7.4, §10 "Measured") present UL and SL as the spec's "full 128-thread LightGBM" configuration (launch-spec UL `does`). The trainer very probably ran 64 threads. So UL's and SL's `omnifold` phases (592.0 and 563.7 s) are not the unguarded production configuration's. The recommendation's direction is unaffected: loads are 72 % of UL's wall either way.
     - **Repair.** Disclose the refusal, the loky fallback, the inferred thread count and its unrecorded status in §7 (P row and §7.4), §7.2 and §10. Do not change any verdict.

2. **MINOR (record) — The J1 vertical loader times are not a matched comparison.** The all-arm and selective-arm runs did not run under the same conditions:
   - From J1's receipts, the four `--arm all` loaders started together at 23:53:19.71Z and ran concurrently, as `launch-spec.json` J1 says.
   - The four selective runs ran one after another (00:16:14Z → 00:21:51Z).
   - REPORT.md:353 calls them "64-CPU shared allocation, one thread" without this. §10 (line 489) sums the differences into the 1,755.5 s forecast basis.
   - I confirmed the numbers themselves (1,331.7 → 133.4, 607.3 → 62.4, 13.4 → 1.6 and 4.9 → 4.4 s; read bytes as stated; sum 1,755.5 s).
   - **Repair.** State that the all-arm times include four-way contention, and therefore may overstate the per-job saving. The figure is already labelled a forecast.

3. **MINOR (record) — REPORT.md:291 overstates what P checks.** It says the env setup's digest is checked "at every SB1 job's start and end". In fact:
   - `sb1_check_env` runs once, at each job's start (`run.env`);
   - the receipts carry the submission-time digest from `run.env`, not a fresh hash (integration F6);
   - the two sourced sub-setups are not covered.

   The input stats are checked at each job's start and end, and I re-verified that against H0 for all 13 complete receipts. The conclusion that the xr jobs changed nothing SB1 read still holds for the inputs and the top-level setup.

4. **NOTE — The xr_\* jobs are handled correctly.** They are not SB1's, and SB1 did not touch them.
   - **Whose they are.** All five (59648608/10/11/16/17) have WorkDir `/global/u2/j/josephrb` and StdOut under `/pscratch/sd/j/josephrb/xr-two-d-followup-20261010/`. Neither key matches the outroot, so `identify` correctly never matched them. The operator log shows only `identify` events and no `scancel`.
   - **What they charged.** All FAILED, exit 3. Their charge, recomputed: 12·19 + 12·19 + 12·7 + 64·7 + 64·4 = 1,244 CPU-s, /256/3600 = 0.00135 node-h. That is outside SB1's cap.
   - **Overlap with SB1.**
     - X0 and X0p (22:45:15–22:45:34Z, nid004092) overlapped SL on nid007102, a different node, sharing only Lustre, for 19 s.
     - X1 (23:06Z) and L0 (23:35Z) fell between SL's end and J1's start.
     - L1 ran on J1's node at 00:23:52Z, after J1 ended (00:22:54Z) and before C started (01:08:05Z).
   - **Could they have affected SB1?** H0 = H1 for all inputs, and every complete receipt's input stats equal H0. There is no plausible effect beyond negligible filesystem load.

5. **NOTE — The operator's python3.6 slip cannot be checked against the operator record, and nothing contradicts it.** The failed call exited in argparse, before `identify`, so by construction it wrote nothing. The log has exactly 4 events: submit-start, submit-end, identify at 20:31:48Z, and identify at 01:41:09Z. That fits the record's account. `attempt-jobs.json` has mtime 18:41 PDT = 01:41Z.

6. **NOTE — The frozen checkout now holds two ignored `__pycache__` directories** (`2d-unfolding/uq/coverage_fixed_truth/n2/` and `nd-unfolding/`). The jobs' own imports wrote them. HEAD is still `2b35ba52`, and no tracked file differs. The record does not mention them. They are harmless.

7. **NOTE — The receipts do not capture package versions.** `environment.packages` (lightgbm, numpy, scikit-learn, scipy) is null in every receipt. The versions come only from the login-node record (§2). The receipts do record `root_version` 6.28/12 and Python 3.11.14.

## Checks performed

### 1. Raw receipts and hashes

- **Cluster originals against the tracked copies.** I hashed 62 cluster files (61 in the outroot and operator record, plus `sb1_operate.py`). All 61 rows of `SHA256-MAP.txt` give cluster = map = local sha256, all `MATCH`. No cluster file is missing from the map, and no tracked evidence file outside `scheduler/` is unmapped.
- **Untracked items, checked separately.**
  - The admission file is `cc9dc814…`, equal to `outroot/admission.json`.
  - `sb1_operate.py` is still `f626997f…`, mode 444.
- **H0 = H1** for all three inputs, on sha256, size, mtime_ns and inode, with H0 also equal to the admission's stat:

  | input | sha256 |
  |---|---|
  | universes | `220c479e…` |
  | CV | `43f8cc16…` |
  | MC | `d40aea69…` |

- **Receipts.** My own checker covered all 15 (13 `complete`, 2 `selection-refused` with exit 5). For each:
  - commit `2b35ba52…`, git `status: ok`, `mismatched: []`;
  - the executed module set equal to the admission's six digests exactly, with nothing extra or missing;
  - guard `installed`, `expect_root` and `allowed` equal to the frozen checkout alone;
  - `strict: true`;
  - one env digest, `ea3c6998…1d48`, which equals `run.env`'s `SB1_ENV_SETUP_SHA256`;
  - `inputs_start` and `inputs_end` equal to H0 on stat and stated sha256, for all complete receipts.
- **Guard inventories.** All 15 show guard installed, `expect_root` and `script_checkout_root` = the frozen checkout, `allow` empty, 0 origins outside it, shim `b7f78a72…` = the manifest's, and `violation` null. Their repo origins are only the frozen `n2/__init__.py` and `n2/execution.py`. For the UL and SL outcome, see finding 1.
- **Output provenance.** The output files' `driverFile` and `omnifoldHelperFile` both point into the frozen checkout, with the manifest's sha256s (`3cc5adc7…` and `e9623412…`), in UL, SL and C. So the helper preload worked.

### 2. Fresh accounting

- **Table.** Above. It matches REPORT §6's table, in UTC (PDT + 7 h), row for row: nodes, eligible, start and end times, elapsed, billing, node-h, the queue total of 10,757 s and the 18,185 s span.
- **Queue starts.** Each job's Eligible time follows its predecessor's end by 13, 24, 13, 31 and 5 s, matching "5–31 s".
- **H1's in-job sacct.** It differs from mine only in H1's own rows: RUNNING at ElapsedRaw 171 against 180, and empty batch MaxRSS and MaxDiskRead. The verifier's 1.1627344 is 9 × 2/256/3600 = 0.0000195 below 1.162754, as REPORT §6 says.
- **iris.** User charge on m3246 is 2036.1 now, against 2035.0 at admission, a delta of 1.1 ± 0.1. That covers SB1's 1.1628 plus the xr jobs' 0.0014.
- **Other jobs of this attempt.** None. The user-window sacct from 12:00 PDT has exactly the six SB1 allocations (WorkDir = outroot) plus the five xr jobs (finding 4).
- **C1, re-run myself.** `squeue --me -t all` at 01:52:37Z returned a header only, rc 0. No job with WorkDir = outroot exists, in any state.

### 3. Criteria from operands

| criterion | what I recomputed | result |
|---|---|---|
| **S2–S4** | from my own sacct (table above) | all PASS |
| **S1** | my own code compared each tree's `digests`, `settings`, `entries`, `sizes` and `loader` in lateral (UL vs SL), vertical (four J1 pairs), CV (C_all vs C_sel) and CV-unfold vs loaders (C vs C_all) | 0 differences |
| S1 arm checks | all-arm `n_active_on_entry == n_branches_in_tree` (6, 240, 470, 236; CV file 3, 4, 7, 3); selective `verified_before_first_read: true` on every tree; `mode` equals the arm | 0 problems |
| S1 matching | UL and SL `comparison_key` and argv without `--out` equal; SL `compare_digests` = UL's receipt | holds — **PASS** |
| **NC** | omit: exit 5, `selection-refused`, `loaders: []`, `SelectionError: SetBranchAddress on inactive branch 'w_reco_Flux_0'`; extra: exit 5, `loaders: []`, active ≠ derived with an extra `w_truth` | **PASS** |
| **S6** | sum and union of C's leaf phases = 542.66 s of wall 624.24 s = 0.8693 (no overlap); gaps 34.00 / 2.66 / 0.07 / 1.55 / 29.94 / 13.36 s, as §7.3 states | **FAIL** (UL 0.9717, SL 0.9252, not criteria) |
| **S5** | read locally with ROOT 6.36 on the tracked UL and SL outputs (sha256 equal to the cluster originals and to each receipt's `output.sha256`): 16 TH1/TH2 in each, none in only one. 12 histograms byte-identical; `hUnfold2D`, `hXSec2D`, `hXSec_pt` and `hXSec_pz` differ. Max relative difference: content 6.395e-13 (`hXSec2D`), errors 6.55e-13; no non-finite bins | ≤ 1e-8 — **PASS-AT-TOLERANCE** |

### 4. Verdict logic

- **The code against the frozen rule.** `sb1_verify.py` `verdict()` at `2b35ba52` (byte-identical at `4cab15aa`):
  - the overall verdict is FAIL if S1 or NC fails;
  - PASS if all of P, S1, NC, S2, S3 and S4 pass;
  - FAIL if P and S1 pass and any of S2–S4 fails;
  - otherwise INCONCLUSIVE.

  That matches the docstring (lines 13-30) and sb1-prep REPORT §6.1.
- **S5 and S6 never feed the overall verdict.** The `core` list excludes them. My independent reading of P, S1, NC and S2–S4 (all PASS) gives **PASS**.
- **Nothing relaxed after the results.** Both P and the package are byte-identical to `016265cc`. The thresholds (10 GB, 30 GB, 0.1, 0.5, 0.5, 1e-8, 0.9) are unchanged, and `verdict.json` (exit 0) is the frozen code's output.
- **Gaps in the verifier's own checks, now covered.** The verifier does not compare the single env digest with `run.env`'s, and it ignores inventory `outcome`. I checked both myself: the digest matches, and the outcome is finding 1, with no P consequence.

### 5. Record accuracy

- **Confirmed.**
  - §6: submission window 20:31:26–20:31:43Z, `identify` agreement, the job table, the H1 undercount, iris, the xr facts and C1. Exception: line 291 (finding 3).
  - §7 tables. Exceptions: the "clean" wording at line 324 and the J1 parallelism (findings 1 and 2).
  - The §7.4 phase table (UL/SL startup 35.55/28.57 s, loads 1,865.0/182.8 s, `omnifold` 592.0/563.7 s, unhooked after `omnifold` 26.89/26.35 s; load share 72.3 % → 21.3 %, `omnifold` 65.7 % of SL), and the process peak RSS of 14.17 and 14.10 GB.
  - §7.5: H0 = H1, and hash times of 902.4 and 149.7 s.
  - §9: tracked evidence is 704 KiB in 67 files, plus 2 `checks/` files.
- **§10.**
  - Measured gains (2,604 → 888 s, 171.3 → 2.36 GB, 69.5 → 17.2 GB, 0.7233 → 0.2467 node-h) are kept apart from labelled forecasts.
  - No whole-sweep, production or exact-backend speedup is claimed.
  - The one recommendation follows from the profile (loads are 72 % of UL's wall).
  - The S5 precondition statement is correct: PASS-AT-TOLERANCE is not "unresolved", and the record still discloses that byte identity was not reached.
- **Failures reported.** The python3.6 slip, S6 FAIL and the xr jobs are all reported. The guard refusal in UL and SL is not (finding 1).
- **Byte identity of the package.** `git rev-parse 4cab15aa:Q/sb1-prep` = `016265cc:Q/sb1-prep` = `7db17678…`, and `git diff --quiet 016265cc 4cab15aa -- Q/sb1-prep` holds.
- **Commit scope.** `git diff --name-only f7135d31 4cab15aa` touches only `Q/sb1-run/`, across `e074c781` and `4cab15aa`. The 72 files of `4cab15aa` are all under `Q/sb1-run/`.
- **Hash-binding gate.** `python3 docs/orchestration/verify_hash_bindings.py` at `4cab15aa`: rc 0, "ALL BINDINGS INTACT, 144 of them from receipt bindings (inventory 144 tracked, sha256 f9dab8dd…)".
- **Admission review.** The preserved copy `review/admission-review.md` is `73425af7…`, byte-identical to my original.
