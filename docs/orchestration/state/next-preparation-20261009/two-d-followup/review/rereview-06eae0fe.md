# Focused re-review: `two-d-followup` at 06eae0fe (review use 2 of 3)

| field | value |
|---|---|
| Reviewer | the same fresh read-only independent reviewer as the admission review (Claude Opus 5.5, `claude-opus-5-5`); this is the single allowed re-review |
| Fixed commit | `06eae0fede3508419f235f8cbe61954b33de8497`. The repair batch is `8378ec23..06eae0fe`; it changes only files under `two-d-followup/`. |
| Manifest | `xr/manifest/expected-code.json` sha256 = `fbca1be80d56b09751bcd9f8fbe698ac65786ebe08e21ae04e561e5c73dd06b8`, as the coordinator stated |
| UTC start / end | 2026-10-10T22:25:07Z / 2026-10-10T22:32:12Z |
| Worktree | detached at `…/fu/rereview-wt`. `git status --porcelain --untracked-files=all`: 0 lines at start, 0 at end. Removed with `git worktree remove`. |
| Resources | about 0.15 local core-hours, at most 2 processes, `OMP_NUM_THREADS=1`, scratch TMPDIR. Mutants were run in an untracked `git archive` mirror. Read-only login-node reads only (login23): no job, no writes. The Python 3.6 check fed the module source over stdin, so nothing was copied to the cluster. |

## Verdicts

- **(i) XR admission: ADMIT.** All of B-1 to B-11 are repaired, and I found no new MATERIAL defect. Two notes remain (N-1, N-2).
- **(ii) Task A method: PASS WITH CHANGES.** A-1 to A-4 and A-6 to A-8 are repaired. A-5 is not: REPORT still cites §E.2 for "the narrowest change that would reopen" the objective, and §E is absent. No conclusion changes.

## Prior findings

| id | status | evidence |
|---|---|---|
| B-1 | **REPAIRED** | `xr_admit.py` now uses `stdout=PIPE, stderr=PIPE, universal_newlines=True` and `str.format`. I ran the module source under the cluster's `/usr/bin/python3` 3.6.15. It compiles and executes; `run(["git","--version"])` works; `parse_utc`, `timedelta`, `min(default=)` and `fromtimestamp(...).strftime` work; `seconds("1-06:00:00")` = 108000; `main()` for `next-attempt` and `jobcheck` gets past argparse and fails only at the file read I deliberately left missing. A static test `test_admission_tool_is_python36_syntax_and_api` was also added. The "cluster run … recorded in B7" that B5 claims is not in the commit; my run stands in for it. |
| B-2 / B-4 | **REPAIRED** | **Outroot:** frozen in `runs.json` as `/pscratch/sd/j/josephrb/xr-two-d-followup-20261010`. It must be absolute and free of symlinks. `draft` creates it with `mkdir(parents=False)`, so a second draft gets FileExistsError and a refusal, and `admission.json` is written with `open(…,"x")`. `--outroot-base` is gone. `verify` requires the admission to be the outroot's own `admission.json`, and `xr_run.py` refuses an admission naming another outroot. **Attempts:** counted per kind as the largest of three records: the attempt directories, `submissions.jsonl`, and `sacct -u <user> -X -n -P -S <grant_date>` `xr_<RUN>_a<N>` jobs (steps excluded). **Stop:** refused if `now > first + 72 h`, or if `now + limit > stop`. **Deadline:** the stop is printed in local time, and `sbatch --deadline` parses it on the same login node and shell, so the time zone is consistent. The login node is on PDT, and no DST change falls between 10-10 and 10-13. A Slurm DEADLINE removal still counts as an attempt (conservative). Tested at the 42 + 30 h boundary. Today: the outroot is absent and no `xr_*` jobs appear in sacct. |
| B-3 | **REPAIRED** | **Frozen values match what I measured on the cluster:** Python 3.11.14, ROOT `6.28/12`, numpy 1.26.4, sklearn 1.8.0, lightgbm 4.6.0, joblib 1.5.3, threadpoolctl 3.6.0, scipy 1.16.3. **Refusal:** `check_environment` runs inside the try, before `seed_loky_cache` and `rec.install()`, so a mismatch exits 6 before any fit. Module origins and `threadpool_info` are recorded. **Nested setup:** all five scripts are bound and form the complete sourcing chain. `unbinned_unfolding/build/setup.sh` and `MINERvA101/opt/bin/setup.sh` are sourced by the top-level script, and `setup.sh` sources `setup_MAT.sh`, `setup_MAT-MINERvA.sh` and `setup_UnfoldUtils.sh`. Prefix digests match `remote-reads.txt`: `40ff3a3d…` and `e22a5b93…`. `verify` re-hashes them in every job, before `source`. |
| B-5 | **REPAIRED** | B1 now records the 64-vs-128-thread difference, the ≤ 5.8e-9 prior and a pre-registered thread-cause check; the criterion is unchanged. |
| B-6 | **REPAIRED** | B2 records the deviation from §10's `-c 2 --mem 24G` and its reason, and cites MaxRSS sources (`53116554.batch`, `59410433`). I did not open the cited `Q/speed` files. |
| B-7 | **REPAIRED** | B2 records the MEHFC/MEFHC name and my content check. |
| B-8 | **REPAIRED** | Both CFS directories are now `drwxr-s---` (I re-read them). The copy's sha256 is still `43f8cc16…`. The group-writable parent is disclosed. |
| B-9 | **REPAIRED** | The worktree path is a sibling, `MINERvA-OmniFold-xr-<sha8>`, not nested. The TIMEOUT risk is stated (19.3 h against a 30-h limit). |
| B-10 | **REPAIRED** | `newest_complete` checks the receipt's `run`, its admission sha256 against the outroot's `admission.json`, and the resolved path. Attempt order is now numeric. `compare` returns INCONCLUSIVE on a shape or edge mismatch. Tested; the `axes-unchecked` and `receipt-admission-unchecked` mutants are caught. |
| B-11 | **REPAIRED** | `n_r != it` refuses anything other than exactly 5 regressor fits. Production has MC reco misses, so 5 is the expected count. Tested (`FitCounts`). |
| A-1 | **REPAIRED** | A2 item 4 and the status table now state the production model; the fixed-N counterexample (Cov = −Nμ², 1.508) is included. |
| A-2 | **REPAIRED** | The R/M χ² terms are "controlled"; the finite-sample term is "not tested (cancels in ln κ̂)". C5 is relabelled. |
| A-3 | **REPAIRED** | "Not established as exact" now rests on the analytic argument; the C4 rows say the toy cannot resolve it (1.62–2.01, ±0.23). |
| A-4 | **REPAIRED** | `methods/a4_pair_offsets.py` reads only the committed two-d-path operands and records their digests. My rerun matches `results/a4_pair_offsets.json` to the last float digit: 37 vertical bands, correlation 0.679 (0.640 without the two offset universes; July 0.126), EtaNCEL median 0.981 σ_ML, NormNCRES (July) median 0.758 σ_ML, EtaNCEL−MaNCEL max 2.86e-10 σ_ML. "Explains" is now scoped to the two universes examined. |
| A-5 | **NOT REPAIRED** | B5 says "§B6–§E written" and the header still routes to §B7, §C, §D, §E, but REPORT.md ends at B5 (536 lines; the last line reads "(B6–B8, C, D, E below)"). A5 cites §E.2 for "the narrowest change that would reopen" the objective; that section does not exist. B-1's "recorded in B7" is likewise absent. |
| A-6 | **REPAIRED** | The purity wording now says it is MC-derived and held at its full-bank value, and that the production bootstrap must hold it fixed the same way. |
| A-7 | **REPAIRED** | The model-bias row now names pre-registered, never-used truth warps as a partial route. |
| A-8 | **REPAIRED** | The text now says the test also detects bootstrap implementation defects. |

## New findings

| id | sev | task | location | finding |
|---|---|---|---|---|
| N-1 | NOTE | B | `xr_admit.py next_attempt` | The stop's start ("first") is read only from `submissions.jsonl`. If that file were lost or edited, the 72-h stop would restart. The attempt cap is unaffected, because sacct and the directories still count. A sacct read that returns empty with exit 0 also lowers only one of the three counts. Residual; no repair needed for admission. |
| N-2 | NOTE | B | `launch/xr_submit.sh` | A refused `next-attempt` returns through the explicit `exit 3`, which does not trigger the ERR trap. Jobs already queued in the same invocation stay queued and recorded, which is correct; the operator should know this behaviour. |
| N-3 | MINOR | A/B docs | REPORT header, B5, A5 | Dangling references to §B6–B8, §C, §D, §E and §E.2 (the same issue as A-5). |
| H-1 | — | both | delta | **Data hygiene: clean.** `a4_pair_offsets.json` holds only summary statistics of unfolded cross-section differences (no arrays). `remote-reads.txt` additions are versions, digests, permissions and the queue. No data-event values or counts. |

## What I ran

- **Suite:** `test_xr`, **32 tests OK** in 163.0 s.
- **Mutation logs:** 29 mutants, 28 caught in the full pass. The survivor, `outroot-unchecked`, is caught in the committed rerun (1/1).
- **My mutant reruns** in the untracked mirror: `stop-unchecked`, `environment-unchecked`, `nested-setup-unbound` and `receipt-admission-unchecked`, **4 of 4 caught**.
- **Cluster, read-only:**
  - `xr_admit.py` executed under Python 3.6.15;
  - the frozen environment re-measured;
  - the nested-setup chain and digests read;
  - CFS permissions and the copy's digest re-read;
  - the outroot and XR worktree are absent;
  - 4 SB1 jobs PENDING, 0 `xr_*` jobs in sacct.
- **A4 producer:** rerun, matching the committed output (above).

## What I could not verify

- `jobcheck`, `verify` and `git` on a **compute** node under `/usr/bin/python3`; I checked the login node only.
- How Slurm handles `--deadline` on a live submission (tested only against fake Slurm).
- The cited MaxRSS source files (`Q/speed/…`), which I did not open.
- An end-to-end `draft` → submit on the cluster; none has been done, by design.
- §B6–§E, which are absent at the fixed commit.
