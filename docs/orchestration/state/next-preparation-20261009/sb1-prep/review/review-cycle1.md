# SB1 preparation package: focused re-review (c1)

**VERDICT: PASS WITH CHANGES.** The four MATERIAL findings are resolved, and I re-ran my own probes
to confirm each one. Findings 5–8 and 10–12 are resolved or disclosed, with one small gap noted under 5.

Finding 9 is **NOT RESOLVED**. The ERR trap that should `scancel` a partial submission never fires.
`sb1_submit.sh` also carries on after a failed `sbatch`: it submits later jobs with an empty
`afterok:` dependency, records an empty id, and exits 0. The repair is a single line, plus a test.
With that change, and the minor and note items below, I see no remaining blocker to putting the
package before Joseph for a named resource authorization.

## Setup facts

- Target: `1ac7cec30099c7ff447cd98f85676b9bb5cfb92b`. The repair batch is `9fa3fed7`; `1ac7cec3` adds
  only mutation run 3, the suite log and §5.3.
- `git diff --name-only a16d5786 1ac7cec3` shows nothing outside P.
- Worktree: `/private/tmp/sb1-review-c1`, detached. Scratch: `/private/tmp/sb1-review-scratch-c1`.
  Both were removed at the end (`git worktree remove --force`, `rm -rf`), and `worktree list` no longer
  shows the worktree.
- Times: start 2026-10-10T06:14:06Z, end of measurement 06:19:49Z.
- `git status --porcelain --ignored`: 0 lines at start, **1 line at end**.
  - I removed the worktree before capturing that line.
  - It is almost certainly an ignored `P/__pycache__/` entry. I ran `python3 -I costs.py` and
    `make_manifest.py --check` from a shell without `PYTHONDONTWRITEBYTECODE`, and `costs.py` imports
    `branch_select`.
  - No command or tool of mine wrote a tracked file in the worktree. Mutations ran only in
    `git archive` copies under scratch.
- CPU: about 0.06 core-hours, from the runners' user+sys:
  - suites: about 87 s user;
  - three mutation runs: about 120 s;
  - probes: about 20 s.
- At most two processes ran at a time, all with `OMP_NUM_THREADS=1`.
- Cluster: one read-only `ssh saul.nersc.gov` (06:19:45Z) that ran `os.stat` on the three inputs. Size,
  mtime_ns and inode all match `input_stat_20261010.psv` and the proposal.
- Preserved c0 review: `P/review/review.md` has sha256 `41f62d7aa2df2d239177…`, identical to
  `/private/tmp/sb1-review-out-c0.md`.

## Per-finding disposition (against REPORT §11)

| # | c0 sev. | status | evidence |
|---|---|---|---|
| 1 | MATERIAL | **RESOLVED** | I re-ran my `pkgbind` probe on the new fixture (package commit A, then an authorization commit). The baseline admission holds (rc 0). I then changed `branch_select.py`, regenerated the manifest and committed. With `package_commit` = A the result is **rc 3**: "files bound to the package changed after …: [branch_select.py, ADMISSION-PROPOSAL.json, expected-code.json]". With `package_commit` = the new HEAD it is also **rc 3**: "the authorization record does not name the package commit and the manifest's sha256 in full". Code: `sb1_admit.py` `check()` runs a `git diff --name-only pkg HEAD` over P, the modules and the guard, then checks the authorization text. |
| 2 | MATERIAL | **RESOLVED** (one stale comment) | The no-retry rule reads the same everywhere: `launch-spec.json:167`, REPORT §1 (line 44), §6.2, §7.4 (lines 425-434), §10 (line 522), `costs.json` `retries`/`sl_timeout`, the proposal's `decision`, and `ledger`, which no longer has `--retry` and now prints "(no retries under an admission)". Remaining stale text: `launch/sb1_submit.sh:8-9` still says "Retries are manual: see the launch spec's retry_rule and `sb1_verify.py ledger`" (new finding N3). |
| 3 | MATERIAL | **RESOLVED** | My verdict probe gives: SL `running` with 2 trees → S1 INCONCLUSIVE, overall INCONCLUSIVE. SL `input-mismatch` with a digest difference on tree 3 and tree 4 missing → S1 FAIL, overall FAIL. Both receipts `complete` but one short → FAIL. SL `selection-refused` with 2 trees → INCONCLUSIVE (see N4). |
| 4 | MATERIAL | **RESOLVED** | §6.2 now says an SL TIMEOUT ends SB1 INCONCLUSIVE. `costs.json` `sl_timeout` agrees, and so does the verifier (the c0 probe already showed INCONCLUSIVE for this case). The reference-based 0.69 argument is gone. |
| 5 | MINOR | **RESOLVED**, with one gap | New tests cover each guard: `test_each_admission_guard_refuses` (6 subtests, each asserting its own reason), plus dirty tree, package binding, authorization text, unadmitted module, receipt input stat, and NC loaders. The recorded mutation log says 25 of 25 caught at `9fa3fed7`. My own mutants: (a) `compare_loaders` `whole = … and …` → `or` was caught (`test_a_killed_selective_arm_is_inconclusive_not_fail` FAILED); (b) `sb1_source_env` with `return 3` → `true` was caught (`test_an_environment_changed_after_submission_stops_the_chain` FAILED). **Gap:** (c) weakening the authorization-text test from `pkg not in … or manifest_sha not in …` to `and` **survived**. The only fixture authorization names neither value, so nothing pins "both" (N2). |
| 6 | MINOR | **RESOLVED** | J1 is described as four parallel plus four selective processes in REPORT §7.1, §8 and §12, `launch-spec.json:113` and `costs.py`. The forecast is 1,157 + 100 + 4×120 + 60 = 1,797.5 s, so J1 = 0.25 × 1797.5 / 3600 = 0.1248 node-h. Total expected is 1.1864 (the REPORT table says 1.186; the prose and the proposal say ≈ 1.19). I re-ran `costs.py`, and its output equals the committed `results/costs.json`. |
| 7 | MINOR | **RESOLVED** | Header line 22 now points to §15, which still reads "pending review". |
| 8 | MINOR | **RESOLVED** (one untested-on-target note) | `run.env` exports `SB1_ENV_SETUP_SHA256` and defines `sb1_source_env`, which refuses (exit 3) if the setup script's digest changed. All four batch scripts call it. Receipts record the path and digest, and P requires a single digest across all receipts. Tests and my mutant (b) confirm this. See N5 on sourcing inside a function. |
| 9 | MINOR | **NOT RESOLVED** | See N1. On macOS `/bin/bash` 3.2 I ran the unmodified `sb1_submit.sh` with a fake `sbatch` that fails on its 3rd call, a logging `scancel`, and a stubbed admission check. Result: **submit rc=0**, `scancel` never called, and `submission.json` holds `"SL": ""`. Calls 4-6 were still made, with `--dependency=afterok:` (empty) for J1 and `afterany:1001:1002::1004:1005` for H1. No test exercises the trap (`grep scancel\|SCANCEL tests/ checks/` finds nothing). |
| 10 | NOTE | **RESOLVED** | §3.2 (lines 145-146) now names `MC_<b>`/`MC_pz_<b>`. |
| 11 | NOTE | **RESOLVED** (disclosed) | §12 (line 583) covers `--array=1-400%30` contention. |
| 12 | NOTE | **RESOLVED** | §7.4 (lines 431-434) says a 128-CPU J1 rerun needs a new authorization. §7.1 line 355 cites speed §3 for the 374-task RSS range. |

## New findings

### N1. MINOR (carries over from finding 9): a failed `sbatch` does not stop the submission, and the trap never fires
- **Where:** `P/launch/sb1_submit.sh`, function `submit()` (the `local id; id="$("${S[@]}" "$@")"; echo …` line) and `trap on_error ERR`.
- **Cause:**
  - `submit` runs inside `$(…)`. Bash does not inherit `errexit` into command substitutions. That holds
    on 3.2, and on ≥ 4.4 too unless `shopt -s inherit_errexit` is set, which this script does not do.
  - So the failed inner `sbatch` is ignored, `echo ""` returns 0, the assignment succeeds, and `ERR`
    never triggers.
- **Effect:**
  - Jobs already queued stay queued: UL alone can charge 0.833 node-h.
  - Later jobs are submitted with empty dependencies. If Slurm accepted `afterok:` as no dependency,
    J1 could read the universe file at the same time as UL and contaminate S4.
  - The record shows an empty id, and the script exits 0.
- **Repair:**
  - `submit() { local id; id="$("${S[@]}" "$@")" || return 1; [[ -n "${id%%;*}" ]] || return 1; echo "${id%%;*}"; }`.
    The failing assignment in the parent then triggers `set -e` and the ERR trap.
  - Add a `fake_slurm` mode that fails the Nth `sbatch`, and assert `scancel` of the earlier ids and a
    non-zero exit.
- **Note on REPORT:** §7.2 ("If `sbatch` fails partway, the submit script cancels the jobs it already
  queued") and §11 row 9 are currently false.

### N2. MINOR: the "both values" authorization requirement has no test that pins it
- **Where:** `P/sb1_admit.py`, the line `if pkg not in auth_text or manifest_sha not in auth_text:`, and `tests/test_launch_chain.py` `test_an_authorization_that_does_not_name_the_package_is_refused`.
- **Evidence:** my mutant `or` → `and` passed both that test and `test_the_good_admission_holds`.
- **Repair:** add two subcases, one where the authorization names only the commit and one where it
  names only the manifest sha.
- **Related note:** `pkg` is taken as given. An abbreviated sha passes the substring check whenever the
  record holds the full sha. Requiring `re.fullmatch("[0-9a-f]{40}", pkg)` would make "in full" literal.

### N3. NOTE: stale retry wording in the submit script
- **Where:** `P/launch/sb1_submit.sh:8-9` ("Retries are manual: see the launch spec's retry_rule and `sb1_verify.py ledger`").
- **Repair:** change it to "No retries under an admission (launch-spec retry_rule)".

### N4. NOTE: say explicitly what an exit 5 outside a control decides
- An SL or J1 selective run refused by `SelectionError` on the real file now yields S1 INCONCLUSIVE.
  My probe confirms it, and it follows from "complete receipts only".
- §6.2 says exit 5 "fails the job" and that failures end INCONCLUSIVE "unless a frozen rule already
  decides it", naming only exit 4.
- This is defensible. But a selection refusal on the real file is direct evidence that prototype 1
  is incomplete there, which REPORT §1 contradicts.
- **Repair:** state the intended verdict in §6.2 (INCONCLUSIVE, reported as "prototype 1 refused on
  the real file"), or classify it as S1 FAIL. Then add a test either way.

### N5. NOTE: the setup script is now sourced inside a shell function, which has not been exercised on Perlmutter
- `sb1_source_env` sources `setup_salloc_env.sh` from inside a function. That script in turn runs
  `conda shell.bash hook`, `conda activate`, and two ROOT/MINERvA `setup.sh` files.
- Any top-level `local` or `declare` in those files would become function-local and vanish on return.
- KI-84's precedent sourced the script at top level, and the local tests use a one-line `env.sh`.
- I found no `declare` or `local` in `setup_salloc_env.sh` itself. I did not inspect the conda hook or
  the two `setup.sh` files on the cluster, which was outside my query scope.
- **Repair (optional):** do the digest check in the function, but `source` at top level
  (`sb1_check_env && source "${SB1_ENV_SETUP}"`). Alternatively, have H0 record `python -c 'import ROOT, lightgbm'`
  as a smoke check.

### N6. NOTE: which commit is "the package commit"
- §7.2 says the authorization must quote "the reviewed commit that last changed `P`".
- `check()` refuses any difference under P between that commit and HEAD, and REPORT §11 and §15 will
  be edited after this re-review. So the package commit has to be the commit that records this
  re-review (a REPORT-only delta from `1ac7cec3`), not `1ac7cec3` itself.
- The manifest is unaffected by that delta. Its sha256 at `1ac7cec3` is `eff903590b547a16055bc1b634b7704f69150f91cebe9bc9b708cfd4d708284e`,
  and `make_manifest.py --check` reports it current.
- **Repair:** one sentence in §7.2 and §16 that makes this explicit.

## Checks run

**Suites at `1ac7cec3`** (my runs, runner output; 0 skipped, all rc 0):

| suite | result |
|---|---|
| `test_branch_select` | Ran 16, OK |
| `test_sb1_guarded` | Ran 10, OK |
| `test_launch_chain` | Ran 25, OK |
| `test_package_consistency` | Ran 7, OK |

**Probes:**

| probe | finding | result |
|---|---|---|
| `pkgbind` | 1 | baseline rc 0; changed package with A → rc 3; with new HEAD → rc 3 |
| no-retry consistency (`grep` of retry, underspend and slack wording) | 2 | consistent except `sb1_submit.sh:8-9` |
| partial-receipt verdict, four cases | 3 | as in the table above |
| `sb1_submit.sh` with the 3rd `sbatch` failing | 9 | N1 |

**Mutants of my own** (in `git archive` copies):
- `compare_loaders` `and` → `or`: caught.
- `sb1_source_env` refusal disabled: caught.
- authorization text `or` → `and`: survived (N2).

**Number consistency:**
- Ceilings 1.6992 (unchanged).
- Expected total 1.1864, with J1 at 1,797.5 s and 0.1248 node-h.
- `costs.py` output equals `results/costs.json`.
- The manifest and proposal are current.

**Cluster:** read-only `stat` of the three inputs; they are unchanged.
