# SB1 execution: the matched selective-read benchmark on Perlmutter

**CITABLE FOR:** the admission, deployment, submission, scheduler accounting, receipts and frozen
verdict of the SB1 benchmark executed under
[`AUTHORIZATION-20261010-sb1.md`](../../../AUTHORIZATION-20261010-sb1.md).
**NOT CITABLE FOR:** production equivalence, a production or whole-sweep speedup, an exact-backend
price, any estimator, uncertainty, coverage or adoption claim, or authority for further compute.

| field | content |
|---|---|
| `Lane` | SB1 execution owner (`sb1-run`) |
| `Decision` | *On the real file, does selective branch reading preserve the required inputs and materially reduce I/O, memory and elapsed time for the declared matched lateral comparison?* |
| `Branch` / `Base` | `run/sb1-20261010` / integrated main `016265cceadbd0f38de31e7f4956377f3d3c5e82` (PR #72) |
| `Run commit` | `2b35ba520e1dd98a162f82ac6a9e4f8cd63a86ac` (the authorization record and its registration; nothing else) |
| `Package` | `Q/sb1-prep/` at package commit `d4335d3b9bc2502002f93390f9555d07e134855f`, manifest sha256 `f060df81338b17069a31a0a2cc7a3430ed81c91ce64de6d6f3d54b80e08eb15a`; immutable input, byte-identical at the run commit |
| `Owned files` | `Q/sb1-run/`; the authorization record and its scoped registration (one `MANIFEST-overrides.tsv` row, one `CATALOG.md` row, regenerated `MANIFEST.tsv`) |
| `Resources` | §9 |
| `Review` | §8 |
| `Model / effort` | owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | §10 |

`Q` = `docs/orchestration/state/next-preparation-20261009`; `P` = `Q/sb1-prep`.

## 0. Setup

- **Roles.** One owner and one fresh read-only reviewer. The reviewer does the admission review, then
  the final result verification, with at most one focused repair and re-review across the task. No
  other agent and no peer messages.
- **Terminal.** PASS, FAIL or INCONCLUSIVE under `P`'s frozen rules (sb1-prep REPORT §6), plus a
  separate verification verdict.
  - A refusal of admission, access, deployment or resources ends the task without submission.
  - No retry or extra submission is authorized.
- **Budget.** 6 active hours; 3 local core-hours; two threads; 8 GiB; 2 GiB scratch; ≤ 20 MiB tracked;
  cluster ≤ 2.0 charged CPU node-h on m3246; zero GPU.

## 1. Pins and inputs (verified 2026-10-10T19:58–20:12Z)

- **Main.** `git fetch origin`: `origin/main` = `016265cc`, the integrated pin.
  - `git diff --quiet d4335d3b 016265cc -- P` holds.
  - `P/manifest/expected-code.json` hashes to `f060df81…`.
  - Nothing under `P`, the six executed modules or the 17 guard files changes between `d4335d3b` and
    the run commit (`git diff --name-only` over those paths: empty).
- **Integration's check of the post-review changes.** Integration-followup REPORT §4.1–§4.3 checked
  all three post-re-review changes of the SB1 lane:
  - the failed-`sbatch` cancellation (N1);
  - the environment check in every job (N5);
  - the exact authorization binding (N2).

  It added the two missing controls (`62e55530`; mutation run 5, 29 of 29). It disclosed the
  orphan-job case and the stale route lines (§4.4); the orphan procedure is implemented in §4 here.
  The delta from the lane head `b7c951b3` to `d4335d3b` changes only `P/REPORT.md`,
  `P/checks/mutation.py`, `P/tests/test_launch_chain.py` and a mutation log. No script, module,
  launch spec or manifest changes. The admission review (§8) still covers `b7c951b3..d4335d3b`.
- **Authorization.** [`AUTHORIZATION-20261010-sb1.md`](../../../AUTHORIZATION-20261010-sb1.md) (sha256
  `3beec1da1fbd3315…`) quotes the grant verbatim. The quoted text's sha256 is `dec02013…`, equal to
  the received text. It names `d4335d3b…` and `f060df81…` in full.
  - It is registered by one scoped commit, `2b35ba52`, touching four paths: the record, one
    `MANIFEST-overrides.tsv` row (`LIVE open`), one `CATALOG.md` routing row (the LIVE-index gate
    requires it) and the regenerated `MANIFEST.tsv`.
  - No competing writer: every other ref with manifest edits ahead of main is a stale branch from
    2026-08-30 to 2026-10-05, and there are no open PRs.
- **Cluster state** (`admission/cluster-state-20261010T2000Z.txt`, login23, 20:00:42Z):
  - **Queue.** `squeue --me` is empty. `sacct` of the user since 2026-10-09 shows no allocations.
    No XR or other dependent job exists or is pending (there is no `two-d-followup` record or
    directory).
  - **Allocation.** iris m3246: charged 16,976.9 of 20,000.0 node-h, so 3,023.1 node-h remain for all
    users. The user has charged 2,035.0 of 10,000.0.
  - **Filesystem.** pscratch: 16.76 of 20.00 TiB, leaving 3.24 TiB of headroom; the Lustre
    filesystem is 69 % used.
  - **Inputs.** All three inputs have exactly the admitted size, mtime_ns and inode:

    | input | size | mtime_ns | inode |
    |---|---|---|---|
    | universe omnifile | 171,117,087,867 | 1783523295000000000 | 882725391507234642 |
    | CV omnifile | 2,144,008,221 | 1779094334000000000 | 882724772125893981 |
    | flux MC | 5,143 | 1777003503000000000 | 882724771874215681 |

  - **Prior digests.** Two inputs have digests recorded independently on 2026-10-09
    (`state/uncertainty-preparation-20261008/b/remote-reads-20261009.txt` §3): CV omnifile
    `43f8cc16…`, flux MC `d40aea69…`. H0 must reproduce them. The universe file has no prior digest.
  - **Environment setup.** `setup_salloc_env.sh` has sha256 `ea3c6998d33f45c8…` (1,407 B);
    `sb1_submit.sh` binds it in `run.env`.
  - **References.** Both unmatched reference products exist.
- **Charging.** Billing is unchanged from the package's operand, `billing / 256 × elapsed`. The
  ceilings, from `admission.json` and recomputed from the launch spec, are:

  | job | ceiling (node-h) |
  |---|---|
  | H0 | 0.005859375 |
  | UL | 0.833333 |
  | SL | 0.5 |
  | J1 | 0.1875 |
  | C | 0.166667 |
  | H1 | 0.005859375 |
  | **total** | **1.69921875 ≤ 2.0** |

  The final verification runs inside H1's ceiling. An orphan from a failed submission can be any of
  the six jobs, not only a hash job. Every job a single `sb1_submit.sh` call can create is one of its
  six `sbatch` calls, each with a fixed shape and time limit, so the worst case stays the sum of the
  six ceilings, 1.69921875 ≤ 2.0 (admission review finding 3; the earlier "≤ 0.0059" wording was too
  narrow).

## 2. Deployment (frozen before submission)

- **Isolated checkout.** `/pscratch/sd/j/josephrb/MINERvA-OmniFold-sb1-2b35ba52` was created by
  `git -C <canonical> fetch github run/sb1-20261010` and `git worktree add --detach … 2b35ba52`.
  Its manifest hashes to `f060df81…`. `git status --porcelain` printed 0 lines. With `--ignored` it
  showed one `tests/__pycache__/` file that my login-node test wrote (admission review finding 1).
  I removed it at 20:31Z, after which `--ignored` also printed 0 lines. The run never imports
  `tests/`.
- **The canonical checkout is not moved.** It stays at `32e403b8`, with its two pre-existing
  modifications to live-state files untouched. The run reads these from it:
  - the inputs and the two reference products;
  - the environment setup `setup_salloc_env.sh`;
  - the two files that setup itself sources, `unbinned_unfolding/build/setup.sh` and
    `MINERvA101/opt/bin/setup.sh`.

  Each job checks only the top-level setup's digest (integration F6, admission review finding 4). No XR or other dependent job is
  pending or running.
- **Helper preload.** `sb1_run.py` loads the frozen checkout's verified helper as
  `sys.modules["omnifold"]` before the driver's `sys.path` insert (sb1-prep §9). The OI-136 guard
  refuses any import from the canonical checkout.
- **Admission.** `sb1_admit.py draft` (package commit `d4335d3b…`) wrote
  `$SCRATCH/sb1-admission-2b35ba52.json` (sha256 `cc9dc814…`). `check` reported "admission holds".
  - The byte-identical copy is [`admission/admission.json.txt`](admission/admission.json.txt).
  - It is stored with `.txt` so that `verify_hash_bindings.py`, which harvests `{path, sha256}`
    pairs from `docs/**/*.json`, does not count it as a new live receipt binding: its
    `authorization` pair would move `RECEIPT_BINDING_COUNT` from 144 to 145.
  - Changing that shared gate is outside this lane; §11 proposes the patch.
  - The binding it carries is checked by `sb1_admit.py` at submission and by the reviewer.
  - Status `ADMITTED`; checkout the frozen worktree; commit `2b35ba52`.
  - Outroot `/pscratch/sd/j/josephrb/sb1-2b35ba52`, absent before submission.
  - `outroot`, every job directory, every receipt and every output are created exclusively, so
    nothing can overwrite earlier evidence.
- **Environment.** `root_6_28`: Python 3.11.14, numpy 1.26.4, LightGBM 4.6.0, scikit-learn 1.8.0,
  ROOT 6.28/12.

## 3. Pre-submission finding: one fixture-sanity test is not portable to ROOT 6.28

The package's `tests/test_branch_select.py` was run on the login node under the target ROOT 6.28
(`checks/login-node-root628.txt`). Result: **15 of 16 OK, 1 error.**

- **Passed:** every byte-equality case (15 loader × pattern cases), every negative control, and the
  reuse/restore and discovery tests.
- **Errored:** `TheFixture.test_boundaries_present` (`test_branch_select.py:128`). ROOT 6.28's
  `AsNumpy` returns the `UChar_t` column as an object array of Python `str`, which `.view(np.uint8)`
  rejects. ROOT 6.36 returns a numeric array.
- **The run path is unaffected.** No run-path file uses `AsNumpy` or `RDataFrame`: not `sb1_run.py`,
  `branch_select.py`, `sb1_verify.py` or the driver.
- **The fixture's coverage was checked separately.** The error stopped that test before its other
  assertions. `checks/fixture_probe.py` therefore re-checks every property the test asserts on a
  fixture written by ROOT 6.28 with the suite's parameters, reading the pass flag per row as the
  pinned loader does. All are present:
  - pass flags 0, 1 and 2 (62 rows with 2);
  - 116 rows within 1e-14 rad of the 20° cut;
  - both weights at 1e4 and one ulp below, non-finite and negative;
  - `-0.0`;
  - the background's 1e6 edges;
  - 15 data rows with `|x| > 1e3`.
- **Disposition.** This is a test-portability defect, disclosed here and not repaired: `P` is
  immutable, and the defect does not touch what SB1 runs.

## 4. Operator procedure for submission and orphan jobs

[`operator/sb1_operate.py`](operator/sb1_operate.py) implements integration-followup §4.4 and the
grant's step 4 outside the pinned package. It runs on the login node with the system Python and
uses only the standard library.

- **`submit`.** It refuses an existing outroot, then records the UTC window around one call of
  `P/launch/sb1_submit.sh`, its exit status, stdout and stderr, and identifies the attempt's jobs.
  A non-zero exit, or an exit 0 whose jobs disagree with `submission.json`, triggers `cleanup`. It
  never resubmits.
- **`identify`.** It finds this attempt's jobs **without trusting returned ids**: every job of the
  user in `sacct` and `squeue` whose submit time lies in the window (padded by 120 s) **and** whose
  WorkDir is the unique outroot or whose StdOut/StdErr lie under it. `sb1_submit.sh` sets `--chdir`,
  `--output` and `--error` to the outroot. A job that matches only one key is AMBIGUOUS: it is never
  acted on, and it stops the task as INCONCLUSIVE.
- **`cleanup`.** It cancels identified active jobs one verified id at a time, never by name, polls
  until none is active, and records the final states. Charges are counted from `sacct` whether or
  not `submission.json` exists.
- **Controls.** `operator/test_sb1_operate.py` uses fake `sacct`, `squeue` and `scancel`: 5 OK.
  - A failed submission cancels exactly this attempt's two jobs, including one whose id was never
    returned. A same-named job from another day and an unrelated job are left alone.
  - A same-named job from another directory inside the window is reported AMBIGUOUS and not
    cancelled.
  - A clean submission is left alone.
  - An exit 0 with a job missing from `submission.json` is treated as ambiguous, and all three
    attempt jobs are cancelled.
  - An existing outroot is refused before the submit script runs.
- **24-hour rule.** If the attempt is unfinished 24 h after the window opens, `cleanup` is run with
  reason `24h`, and partial evidence is preserved.

## 5. Admission review

- **Reviewer.** One fresh, read-only reviewer, explicitly authorized. It is a Claude subagent of the
  owner's model family, so the review is not cross-provider independent.
- **Scope and setup.** It reviewed the fixed commit `f7135d31` (run commit `2b35ba52`), 20:13Z →
  20:29Z, ≈ 0.04 core-h.
  - Its own detached worktree was clean at start. At the end it held only an ignored
    `__pycache__` that its own probe wrote; the worktree was then removed.
  - On the cluster it made read-only queries only: no `sbatch`, `srun`, `salloc` or `scancel`, and it
    created no file there.
  - Preserved verbatim: [`review/admission-review.md`](review/admission-review.md), sha256
    `73425af791503eab…`.
- **Verdict: ADMIT WITH CONDITIONS**, no blocker.
- **What it re-did itself:**
  - the unreviewed delta `b7c951b3..d4335d3b` (tests, mutants and record only; nothing executed);
  - the four-path run commit;
  - byte identity of `P` (tree `7db17678…` at all four commits) and of all 32 manifest files;
  - the grant quote (`cmp`-identical, sha256 `dec02013…`);
  - the binding of the record's digest to the admission;
  - `sb1_admit.py check` on the cluster (holds);
  - the admission's fields, a re-stat of the inputs and the outroot's absence;
  - the suites at `f7135d31`: 16 / 10 / 29 / 7 OK and the operator's 5 OK, 0 skipped;
  - the operator wrapper's bytes on the cluster (`f626997f…`, mode 444) and its logic;
  - the ceilings and the charge accounting;
  - the ROOT 6.28 finding, confirmed confined to a test.

| # | severity | finding | disposition |
|---|---|---|---|
| 1 | MINOR | the frozen checkout held an ignored `tests/__pycache__` file from the owner's login-node test; "status 0 lines" held only without `--ignored` | **fixed**: file removed before submission (20:31Z; `--ignored` 0 lines, admission re-checked); §2 corrected |
| 2 | MINOR | the operator's `ACTIVE` set omits `STOPPED`, `SIGNALING`, `STAGE_OUT`, `REQUEUE_HOLD`, `RESV_DEL_HOLD` and `SPECIAL_EXIT`, so `cleanup` could report clean while such a job lived | **condition C1, applied**: after any `status` or `cleanup`, `squeue --me -t all` must list no job whose WorkDir is the outroot, in any state; anything listed is named and handled under the INCONCLUSIVE rule. The mode-444 wrapper is not changed |
| 3 | MINOR | §1's orphan bound (≤ 0.0059) was narrower than the grant | **fixed** (§1): any orphan is one of the six calls, so the total stays ≤ 1.69921875 |
| 4 | NOTE | the setup sources two more canonical files, which the digest check does not cover | **fixed** (§2 lists them) |
| 5 | NOTE | ROOT 6.28 finding confined to the test; `sb1_verify.py` is unexercised on 6.28 | recorded; the final verification is independent |
| 6 | NOTE | hash throughput is assumed (≥ 64 MB/s needed) | recorded |
| 7 | NOTE | the grant's provenance traces to the owner's saved copy | recorded |

## 6. Submission and scheduler record

- **Submission.** One call through the operator wrapper, `submit` at 2026-10-10T20:31:26Z →
  20:31:43Z UTC. `sb1_submit.sh` exited 0, and its `check` reported "admission holds".
  `identify` at 20:31:48Z matched six jobs by user, window and WorkDir = outroot, with 0 ambiguous,
  agreeing with `submission.json`:

  | job | id | dependency |
  |---|---|---|
  | H0 | `59645299` | none |
  | UL | `59645300` | afterok H0 |
  | SL | `59645301` | afterok UL |
  | J1 | `59645302` | afterok SL |
  | C | `59645304` | afterok J1 |
  | H1 | `59645305` | afterany on all five |

- **Outroot.** `/pscratch/sd/j/josephrb/sb1-2b35ba52`; the operator record is
  `/pscratch/sd/j/josephrb/sb1-operator-2b35ba52/record/`.
- **24-hour stop.** The stop deadline is 2026-10-11T20:31:26Z.

SUBMISSION_PLACEHOLDER

## 7. Results under the frozen rules

RESULTS_PLACEHOLDER

## 8. Review and verification

VERIFICATION_PLACEHOLDER

## 9. Resources

RESOURCES_PLACEHOLDER

## 10. Disposition

DISPOSITION_PLACEHOLDER
