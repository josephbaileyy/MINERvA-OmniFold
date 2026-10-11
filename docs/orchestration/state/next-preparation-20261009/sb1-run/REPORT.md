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
  launch spec or manifest changes. The admission review (§5) still covers `b7c951b3..d4335d3b`.
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

- **Execution.** All six jobs ran once, in the declared order, and ended `COMPLETED` with exit `0:0`.
  There were no retries, requeues, cancellations, extra submissions or GPU allocations. The only
  operator actions after submission were read-only (`identify` and `status`, §4).
- **Fresh accounting** ([`evidence/scheduler/sacct-final.psv`](evidence/scheduler/sacct-final.psv)).
  This sacct was taken at 2026-10-11T01:41:18Z, after H1 ended. Times below are UTC; sacct prints
  PDT, which is UTC−7.

  | job | node | eligible → start (queue) | start → end | elapsed s | billing | charged node-h |
  |---|---|---|---|---|---|---|
  | H0 | nid004111 | 20:31:30 → 20:37:35 (365 s) | 20:37:35 → 20:53:04 | 929 | 2 | 0.002016 |
  | UL | nid004471 | 20:53:17 → 21:47:10 (3,233 s) | 21:47:10 → 22:30:34 | 2,604 | 256 | 0.723333 |
  | SL | nid007102 | 22:30:58 → 22:43:42 (764 s) | 22:43:42 → 22:58:30 | 888 | 256 | 0.246667 |
  | J1 | nid004101 | 22:58:43 → 23:53:01 (3,258 s) | 23:53:01 → 00:22:54 | 1,793 | 64 | 0.124514 |
  | C | nid004105 | 00:23:25 → 01:08:05 (2,680 s) | 01:08:05 → 01:23:53 | 948 | 64 | 0.065833 |
  | H1 | nid004140 | 01:23:58 → 01:31:35 (457 s) | 01:31:35 → 01:34:35 | 180 | 2 | 0.000391 |
  | **total** | | **10,757 s queue (2.99 h)** | | **7,342 s** | | **1.162754** |

  - Charged time is billing/256 × ElapsedRaw. Queue time is never charged.
  - First submit (20:31:30Z) to last end (01:34:35Z) is 18,185 s (5.05 h).
  - Each Eligible time is sacct's own dependency release, so a queue starts 5–31 s
    after its predecessor ends.
  - The total is 1.162754 node-h of the 2.0 cap, leaving 0.837246.
  - [`checks/owner_ledger.py`](checks/owner_ledger.py) recomputes everything above from the psv;
    its output is [`checks/owner-ledger.txt`](checks/owner-ledger.txt).
- **Verifier's in-job charge.** `H1/verdict.json` reports `charged_node_h` = 1.1627344. H1 wrote its
  `sacct.psv` while H1 itself was running (171 s elapsed at that moment), so that figure undercounts
  H1 by 9 s × 2/256, which is 0.0000195 node-h. This is a property of the frozen design. The fresh
  figure above is the one of record.
- **iris.** m3246's user charge went from 2035.0 (20:00Z, admission) to 2036.1 (01:41Z). iris rounds
  to 0.1, so the change lies between 1.0 and 1.2, which covers 1.16 plus the 0.0013 of non-SB1 jobs
  below ([`evidence/scheduler/iris-post-run.txt`](evidence/scheduler/iris-post-run.txt)).
- **Jobs outside SB1 in the window** ([`sacct-user-window.psv`](evidence/scheduler/sacct-user-window.psv),
  [`sacct-non-sb1-xr.psv`](evidence/scheduler/sacct-non-sb1-xr.psv)).
  - Five `xr_*_a1` jobs (59648608, 59648610, 59648611, 59648616, 59648617) were submitted under the
    same Unix user at 22:34:53–22:35:08Z, after admission. They came from another lane: WorkDir
    `/global/u2/j/josephrb`, output under `/pscratch/sd/j/josephrb/xr-two-d-followup-20261010/`.
  - All five FAILED with exit 3 after 4–19 s, charging about 0.00135 node-h in total. That charge is
    not SB1's and is not counted against SB1's cap.
  - SB1 did not touch them. `identify` never matched them, because neither the WorkDir nor the
    output is under the outroot, and nothing was cancelled.
  - Only X0 and X0p (22:45:15–22:45:34Z) overlapped an SB1 job (SL), and they ran on another node
    (nid004092). L1 ran on J1's node (nid004101) at 00:23:52Z, after J1 ended at 00:22:54Z.
  - Every input's stat is checked at each SB1 job's start and end against H0, and H1 = H0 (§7.5).
    The top-level env setup's digest is checked once, at each job's start, against the digest
    recorded at submission; its two sourced sub-setups are not covered (finding 3 of §8). So the xr
    jobs changed none of SB1's inputs or its top-level setup.
  - The 20:00Z admission snapshot showed an empty queue; these jobs were submitted at 22:34Z.
- **Condition C1.** After the final `status`, `squeue --me -t all` listed H1 (`COMPLETED`) at
  01:35:18Z and 01:40:50Z. It listed no row at all at 01:42:09Z
  ([`evidence/scheduler/c1-squeue-final.txt`](evidence/scheduler/c1-squeue-final.txt)). No job of
  this attempt remains, in any state.
- **One operator slip, with no effect.** At 01:40:50Z the first post-run `status` call used the login
  node's default `python3` (3.6), whose argparse rejects `add_subparsers(required=True)`. It exited
  before `identify` ran, with no scheduler call and no write. Rerun under `/usr/bin/python3.11` (the
  interpreter the submission used) at 01:41:09Z, it matched the same six ids, with 0 ambiguous and
  every job `COMPLETED`.
- **Evidence.** Every file of the outroot and of the operator record is tracked under
  [`evidence/`](evidence/): 61 files, sha256-equal to the cluster copies, listed in
  [`evidence/SHA256-MAP.txt`](evidence/SHA256-MAP.txt). JSON files carry a `.txt` suffix with their
  bytes unchanged (§11).

## 7. Results under the frozen rules

**Frozen verdict: PASS.** P, S1, NC, S2, S3 and S4 all pass. S5 and S6 are reported separately and
by rule enter no overall verdict:

- S5 = **PASS-AT-TOLERANCE**;
- S6 = **FAIL**.

The verdict is from H1's `sb1_verify.py verdict`
([`evidence/outroot/H1/verdict.json.txt`](evidence/outroot/H1/verdict.json.txt), verifier exit 0).
The owner rechecked it from the fresh sacct and the receipts; §8 has the independent verification.
Criteria are as frozen in sb1-prep REPORT §6 and `sb1_verify.py:13-30`. Nothing was relaxed or
reinterpreted after the results.

| criterion | rule (frozen) | measured | verdict |
|---|---|---|---|
| P | every receipt strict and guarded at `2b35ba52` with the admitted module digests; inputs' stat equal to H0 at each job's start and end; H1 = H0; one env-setup digest; every guard inventory on the admitted checkout alone | `problems: {}`; all 15 receipts (13 complete, 2 refused controls) pass; all 15 guard inventories satisfy P's rule (installed on the admitted checkout alone, `allow` empty, 0 origins outside, the manifest's shim, `violation` null). UL's and SL's inventories also record one **refused child launch** each (`lscpu --parse=core`), which P's rule does not test (§7.6); one env digest `ea3c6998…` | **PASS** |
| S1 | byte-identical loader digests and equal settings in the lateral, vertical and CV patterns; selective verified before first read; all arm entered fully active | lateral, vertical, cv and cv-unfold-vs-loaders difference lists all empty; arm checks empty | **PASS** |
| NC | both J1 activation controls refused with exit 5 before any loader returned | omit: exit 5 (`SetBranchAddress on inactive branch 'w_reco_Flux_0'`); extra: exit 5 (`active … != derived`, extra `w_truth`); `loaders == []` for both | **PASS** |
| S2 | SL MaxDiskRead ≤ 10 GB and ≤ 0.1 × UL | 2.3578 GB vs 171.2978 GB, ratio 0.01376 | **PASS** |
| S3 | SL MaxRSS ≤ 30 GB and ≤ 0.5 × UL | 17.1652 GB vs 69.4598 GB, ratio 0.24712 | **PASS** |
| S4 | SL elapsed ≤ 0.5 × UL | 888 s vs 2,604 s, ratio 0.34101 | **PASS** |
| S5 (separate) | UL vs SL outputs: byte-identical PASS; hXSec2D within 1e-8 relative PASS-AT-TOLERANCE; else INCONCLUSIVE | 16 histograms in each, none in only one; not byte-identical; max relative difference 6.40e-13, in hXSec2D and over all histograms | **PASS-AT-TOLERANCE** |
| S6 (separate) | C's hooked phases cover ≥ 90 % of the wrapper wall | 542.66 of 624.24 s = 0.8693 | **FAIL** |

GB here is 10⁹ bytes of sacct's KiB values, as in the verifier.

### 7.1 Input preservation in detail (S1)

- **Lateral (UL vs SL, `Muon_Energy_MINOS:0`, seed 42, five iterations, lgbm).** The four trees are:

  | tree | entries | UL active | SL active |
  |---|---|---|---|
  | data | 4,119,797 | 6/6 | 3 branches |
  | mc_background | 658,227 | 240/240 | 4 branches |
  | mc_signal_reco | 32,849,103 | 470/470 | 7 branches |
  | mc_truth_denom | 32,849,103 | 236/236 | 3 branches |

  Every digest of every loader output is equal, and the settings are equal. The selective arm was
  verified before its first read on all four trees.
- **Vertical (J1, `Flux:0`, loaders only).** The same four trees in eight guarded runs: four `all`
  and four `selective`. Digests and settings are equal for all four.
- **CV (C).** The CV file has only the branches the loaders read (3/4/7/3), so its selective arm
  deactivates nothing. Its equality holds, but trivially. It also shows that the unfold run's loaders
  equal the loaders-only run.
- **Measured vertical loader times (J1, not a criterion; 64-CPU shared allocation, one thread).** The
  load phase and the bytes it read (`/proc/self/io` `read_bytes`), all → selective. **Not a matched
  pair:** the four `all` runs ran concurrently (all started at 23:53:19Z, as the launch spec says),
  while the four `selective` runs ran one after another (00:16:14Z → 00:21:51Z). So the `all` times
  include four-way contention for the node and the filesystem, and may overstate a single job's
  saving:

  | tree | load phase | bytes read |
  |---|---|---|
  | mc_signal_reco | 1,331.7 → 133.4 s | 112.3 → 1.41 GB |
  | mc_truth_denom | 607.3 → 62.4 s | 57.8 → 0.77 GB |
  | mc_background | 13.4 → 1.6 s | 1.18 → 0.016 GB |
  | data | 4.9 → 4.4 s | 0.158 → 0.112 GB |

### 7.2 Output equivalence (S5), reported separately

- UL and SL wrote 16 histograms each. They are not byte-identical. The largest relative difference in
  any bin of any histogram is 6.40 × 10⁻¹³, in `hXSec2D`, below the frozen 10⁻⁸ tolerance. S5 is
  therefore PASS-AT-TOLERANCE and is not unresolved.
  - The verifier's note stands: the 128-thread rerun envelope of the driver itself is unmeasured.
    ("128-thread" is the frozen wording. UL and SL very probably trained with 64 LightGBM threads,
    §7.6.)
  - So this run does not show *why* two runs with byte-identical inputs differ at 10⁻¹³. It shows
    only that they differ by less than the tolerance.
  - Output sha256: UL `5745e2d5…`, SL `99b11bd1…`.
- **Unmatched comparisons** (in the verdict file but entering no criterion, because the driver
  revisions differ):

  | comparison | max relative difference in hXSec2D |
  |---|---|
  | UL vs the July `purity_newomni` product | 7.88 × 10⁻¹² |
  | SL vs the same product | 7.74 × 10⁻¹² |
  | C vs KI-84 replica 59410433_1 | 8.31 × 10⁻¹³ |

  None is byte-identical.

### 7.3 Phase coverage (S6), reported separately

- C's hooked phases cover 86.93 % of the wrapper wall: 542.66 of 624.24 s. The uncovered 81.57 s is:
  - 34.00 s before `driver:main` starts (interpreter, guard and imports);
  - 2.66 s between `driver:main` and the first load;
  - 0.07 s between the last digest and `build_measured_training_2d`;
  - 1.55 s between `build_measured_training_2d` and `omnifold`;
  - **29.93 s** between the end of `omnifold` and the start of `compute_efficiency_2d`, inside the
    driver and unhooked;
  - 13.36 s after the last hooked phase.
- UL and SL show the same shape: 35.55/28.57 s of startup, and 26.89/26.35 s unhooked after
  `omnifold`.
- S6 FAIL means the profile is not fine-grained enough to attribute about 13 % of C's wall. It says
  nothing about input preservation or about S2–S4.

### 7.4 Where the time goes (measured; UL and SL wrapper receipts)

| phase | UL s | SL s |
|---|---|---|
| startup before `driver:main` | 35.6 | 28.6 |
| four loads + digests | 1,865.0 | 182.8 |
| `build_measured_training_2d` | 5.2 | 4.9 |
| `omnifold` | 592.0 | 563.7 |
| unhooked after `omnifold` | 26.9 | 26.4 |
| other unhooked (gaps and tail) | 10.4 | 9.2 |
| `compute_efficiency_2d` + `compute_omnifold_completeness_2d` | 42.8 | 42.0 |
| wrapper wall | 2,577.8 | 857.5 |

- After selective reading, `omnifold` is 66 % of SL's wall and loading is 21 %.
- UL's and SL's `omnifold` phases (592.0 and 563.7 s) very probably ran LightGBM with 64 threads,
  not the spec's 128 (§7.6). They are matched with each other, but they are not the unguarded
  production configuration's training time.
- The 1,682 s saved is entirely in the loads, mostly `collect_signal_arrays_2d`
  (1,265.2 → 120.7 s) and `collect_truth_denom_arrays` (581.5 → 54.6 s).
- **Memory: an observation, not a criterion change.**
  - The process's own peak RSS (`ru_maxrss`) is 14.17 GB in UL and 14.10 GB in SL.
  - sacct's MaxRSS for the batch step is 69.46 GB and 17.17 GB.
  - S3 is decided on sacct's MaxRSS, as frozen. What makes up the 4× sacct difference, when the
    process peak is equal, was not measured here; file-backed memory is a candidate, not a finding.
    The S3 margin should therefore not be read as a 4× reduction in the driver's heap.

### 7.5 Input identity H0 = H1

H0 (20:37–20:53Z) and H1 (01:31–01:34Z) recorded the same sha256, size, mtime_ns and inode for all
three inputs:

| input | size (bytes) | sha256 |
|---|---|---|
| universes file | 171,117,087,867 | `220c479e…` |
| CV file | 2,144,008,221 | `43f8cc16…` |
| MC file | 5,143 | `d40aea69…` |

The CV and MC digests equal the 2026-10-09 records.

H1 hashed the universes file in 149.7 s against H0's 902.4 s. The cause, for example caching, was not
investigated, and the digests agree.

### 7.6 Guard refusal in UL and SL and the inferred LightGBM thread count (reviewer's finding 1)

- **What is recorded.** In both timed jobs the OI-136 guard refused one child launch:
  - `outcome: refused:launch-unmodelled-launch-grammar`, `verdict: REFUSED launch`;
  - `offending_argv: ["lscpu", "--parse=core"]`;
  - see `evidence/outroot/UL/inventory.jsonl` and `SL/inventory.jsonl`, and the banner in
    `sb1_UL_59645300.err:11-15` and `sb1_SL_59645301.err:11-15`.

  The run continued, and both jobs completed. C's and J1's inventories show no refusal.
- **Where the call comes from** (the reviewer's source reading, cluster environment):
  - The helper builds the LightGBM estimators without `n_jobs`, so LightGBM 4.6.0 asks joblib/loky
    for the number of physical cores.
  - With affinity 256 (= `os.cpu_count()` in the UL and SL receipts), loky runs
    `lscpu --parse=core`. On failure it falls back to counting distinct `core id` lines in
    `/proc/cpuinfo`.
  - In C the affinity was 64, so loky returned 64 without calling `lscpu`.
- **The inferred effect.** On a two-socket node the fallback counts one socket's core ids. On login23
  (2 × 64-core EPYC), distinct `core id` = 64 while `lscpu --parse=core` = 128. The owner re-measured
  this; the reviewer measured it first.
  - So UL and SL **very probably** trained with 64 LightGBM threads despite `OMP_NUM_THREADS=128`.
  - This is an inference. The receipts do not record the trainer's thread count
    (`environment.packages` is null), and the compute nodes' `/proc/cpuinfo` was not read.
- **Consequences.**
  - **None for the verdict.** P's frozen rule tests the guard's installation and origins, which all
    hold, and refusing is the guard working. UL and SL ran under the identical refusal and fallback,
    so S4 compares matched runs. S1, S2 and S3 do not depend on training threads.
  - **The `omnifold` timings are not the production configuration's.** Unguarded, `lscpu` would
    succeed and LightGBM would use 128 threads. The load savings, the subject of SB1, do not depend
    on this. The share figures in §7.4 and §10 describe the guarded runs.

## 8. Review and verification

- **Reviewer.** The same fresh, read-only reviewer as the admission review (§5), on its second and
  last authorized task. It verified commit `4cab15aa` from its own detached worktree, 01:52–01:57Z
  for the checks, using its own cluster reads: sha256 of the originals, its own `sacct`, `squeue`
  and `iris`, and read-only source reads. It did not run sbatch, srun, salloc or scancel, and wrote
  nothing on the cluster. Its worktree status was 0 lines with `--ignored` at start and end.
- **The verification is preserved byte-identical** at
  [`review/final-verification.md`](review/final-verification.md).
- **Verdicts.**
  - **RESULT VERIFIED: PASS.** This is the reviewer's independent reading of the frozen terminal.
    - It recomputed charges, queue times and S2–S4 from its own fresh sacct; its 18 rows equal
      `sacct-final.psv` field by field.
    - It recomputed S1, NC and S6 from the receipts with its own code.
    - It read S5 from the output ROOT files: 12 of 16 histograms are byte-identical; `hUnfold2D`,
      `hXSec2D`, `hXSec_pt` and `hXSec_pz` differ, by at most 6.395e-13 in content and 6.55e-13 in
      errors.
    - It checked `verdict()` against the frozen rule.
    - It re-ran C1 at 01:52:37Z: no row.
  - **RECORD: REPAIR NEEDED (disclosure only).** Three findings, each repaired in this commit
    without changing any criterion, number in a criterion or verdict:

    | # | severity | finding | repair |
    |---|---|---|---|
    | 1 | MATERIAL | the guard refused `lscpu --parse=core` in UL and SL; the record called all inventories "clean"; LightGBM very probably trained with 64 threads, not 128 | §7 P row reworded; new §7.6; qualifiers in §7.2, §7.4 and §10; §11 item 6 |
    | 2 | MINOR | J1's `all` loaders ran concurrently and its `selective` loaders sequentially, so the vertical timings and the 1,755.5 s forecast basis are not matched | disclosed in §7.1 and §10 |
    | 3 | MINOR | §6 said the env digest is checked at every job's start and end; it is checked once, at the start, against the submission-time digest, and the sub-setups are not covered | §6 corrected |

  - **Notes, recorded without repair.**
    - The xr jobs are correctly handled (note 4).
    - The python3.6 slip is consistent with the operator log, which holds exactly four events
      (note 5).
    - The jobs' own imports left two ignored `__pycache__` directories in the frozen checkout
      (`2d-unfolding/uq/coverage_fixed_truth/n2/`, `nd-unfolding/`). HEAD is still `2b35ba52`, and
      no tracked file differs (note 6).
    - The receipts' `environment.packages` is null, so the library versions come only from §2's
      login-node record (note 7).
- **Focused re-review.** The one authorized re-review covers only these repairs; its verdict is in
  §8.1.

### 8.1 Focused re-review of the repairs

RE-REVIEW_PENDING

## 9. Resources

| resource | cap | used |
|---|---|---|
| cluster CPU, charged | 2.0 node-h on m3246 | **1.162754 node-h** (fresh sacct, §6); 0.837246 below the cap |
| GPU | 0 | 0 |
| jobs | the fixed six | six, each once; no retry, requeue or extra submission |
| queue (not charged) | — | 10,757 s after eligibility; 18,185 s from first submit to last end |
| 24-hour stop | 2026-10-11T20:31:26Z | not reached; the last job ended at 01:34:35Z |
| local compute | 3 core-h, two threads, 8 GiB | small parsing scripts and the operator's unit tests only, well under 0.1 core-h (estimate); no local ROOT or training run by the owner in this phase. The reviewer's local runs are reported in §8 |
| local scratch | 2 GiB | under 2 MiB: the fetched evidence (0.7 MiB) and small text files |
| tracked evidence | ≤ 20 MiB | the `evidence/` tree is 0.69 MiB (69 staged files, including `checks/`) |
| bulk data | no local copy of the 171-GB file | none; only receipts, logs and the three 61-KB output ROOT files were copied |
| active hours | 6, including review and delivery | grant at 19:58:20Z. At this record's pre-verification commit the wall time is about 5.8 h, of which 5.05 h was scheduler queue and run time spent in passive 120-s polls. The final verification and delivery follow, and §8 records their times |

The owner's harness process reported 15 min 56 s of CPU for the whole session, phases 1 and 2. That
is the agent runtime, not compute.

## 10. Disposition

- **Terminal (frozen rules): PASS.** P, S1, NC, S2, S3 and S4 pass. S5 is PASS-AT-TOLERANCE and S6 is
  FAIL; both are reported separately (§7).
- **Verification verdict.** §8.
- **What this establishes, and only this.** For one lateral universe (`Muon_Energy_MINOS:0`) on one
  regular node, prototype 1's selective branch reading:
  - preserved every loader input byte for byte in the lateral, vertical (`Flux:0`) and CV patterns;
  - cut MaxDiskRead from 171.30 to 2.36 GB, sacct MaxRSS from 69.46 to 17.17 GB, and elapsed time
    from 2,604 to 888 s;
  - produced outputs within 6.4 × 10⁻¹³ relative of the all-branch run.
- **What it does not establish.**
  - Not a whole-sweep, production or exact-backend speedup: one lateral timing pair is not a sweep.
  - No reduction in the driver's own heap (§7.4).
  - No measured rerun envelope (S5 note).
  - No authority for deployment, a production-driver edit, N2, a KI-85 lift, covariance production,
    adoption or publication.
- **Recommended next implementation action, one only, subject to its own authorization.** Port
  prototype 1's derived-branch selection into the production driver's four loaders. Make it an
  opt-in path that refuses on any mismatch between active and derived branches (the S1/NC guard as
  shipped here), and test it with the J1 controls as regression tests.
  - **Justification from the profile.** After selective reading, loads are 21 % of SL's wall and
    `omnifold` is 66 %. Before it, loads were 72 % of UL's wall. Selective reading removes the
    largest measured phase, and nothing else measured here comes close.
  - **Measured.** For one lateral universe job on a regular node: elapsed 2,604 → 888 s (−66 %),
    disk read 171.3 → 2.36 GB, sacct MaxRSS 69.5 → 17.2 GB, charge 0.7233 → 0.2467 node-h. For the
    vertical `Flux:0` loaders alone (J1, one thread): `collect_signal_arrays_2d` 1,331.7 → 133.4 s
    and `collect_truth_denom_arrays` 607.3 → 62.4 s. These J1 pairs are not matched: the `all` runs
    were concurrent and the `selective` runs sequential (§7.1). Both timed unfold runs very probably
    trained with 64 LightGBM threads (§7.6), so the `omnifold` share is that of the guarded runs.
  - **Forecast, not measured.**
    - A vertical-universe unfold job would save roughly the J1 load difference summed over the four
      trees (1,755.5 s) of its wall. This assumes its other phases match UL's; no vertical unfold timing pair exists.
      The basis compares concurrent `all` runs with sequential `selective` runs (§7.1), so it may
      overstate the saving.
    - A whole sweep's saving scales with how many jobs read the universes file and how much of each
      job is load. Neither has been measured for the sweep.
    - The lower sacct MaxRSS might allow a smaller allocation. This is unmeasured, because the
      process peak is 14.1 GB in both arms and `omnifold`'s thread scaling on a smaller allocation
      is unknown.
  - **Precondition.** S5 is PASS-AT-TOLERANCE, not unresolved, so the grant's S5 precondition for a
    deployment proposal is met at the frozen tolerance. The proposal should still state that byte
    identity was not achieved, and that the 128-thread rerun envelope is unmeasured.
- **Not done and not to follow automatically.** No transfer study, sweep, alternate universe, extra
  timing pair, production implementation, Rust rewrite or estimator change.

## 11. Proposals for other owners (not applied here)

1. **Receipt hash-binding gate (integration owner).** Tracking this run's JSON evidence as `.json`
   would add two resolvable bindings, so the inventory would move from 144 to 146. Both bind
   correctly:
   - `outroot/admission.json` → `docs/orchestration/AUTHORIZATION-20261010-sb1.md` (`3beec1da…`);
   - 15 receipts → `setup_salloc_env.sh` (`ea3c6998…`).

   Measured with the gate's own `collect`/`localize` on the staged tree: all `OK`, none `MISMATCH`.
   The gate's constants (`RECEIPT_BINDING_COUNT` and its digest) live in a shared file outside this
   lane. So the JSON is tracked with a `.txt` suffix, bytes unchanged (map:
   `evidence/SHA256-MAP.txt`), and the gate reports `ALL BINDINGS INTACT` at 144. If integration
   wants these as live bindings:
   - rename the files back to `.json`;
   - raise the constants to 146, with the observed digest, using the gate's own inventory delta and
     the review the gate's message asks for.
2. **ROOT 6.28 portability of `P/tests/test_branch_select.py:128` (sb1-prep owner).** See §3: under
   the cluster's ROOT 6.28, `AsNumpy` returns a `UChar_t` column as a `str` object array. Casting
   the column explicitly is a candidate fix; it has not been tested here. Nothing on the run path uses
   `AsNumpy`.
3. **Operator wrapper under the login node's default interpreter (this lane's own tool, for reuse).**
   `sb1_operate.py` needs Python ≥ 3.7 (`add_subparsers(required=True)`). The login node's default
   `python3` is 3.6. A shebang or a usage line naming `/usr/bin/python3.11` would avoid the §6 slip.
   The pinned copy stays unchanged.
4. **Phase hooks (driver owner, only if S6-grade profiles are wanted again).** About 30 s inside the
   driver between `omnifold` and `compute_efficiency_2d`, plus about 34 s of startup, are unhooked
   (§7.3). Profiling them would require a production-driver change, which is not authorized here.
5. **`docs/orchestration/MANIFEST.tsv` (integration owner).** The manifest has been out of date on
   this branch since the first sb1-run record commit (`f7135d31`). Main at `016265cc` checks `OK`.
   - `generate_manifest.py --at-sha 4cab15aa` differs from the committed table by:
     - 77 added rows, every one under `Q/sb1-run/`;
     - 46 changed rows outside it, in derived columns only: `inbound_count` in all 46, plus
       `consumer` for `P/launch/sb1_submit.sh` and `P/sb1_verify.py`, and MANIFEST's own
       `lines`/`bytes`.
   - All of them follow from the new sb1-run files citing existing paths. Nothing is removed or
     reclassified.
   - Regenerating a shared generated file is outside this lane's files, so integration should
     regenerate it when merging.
6. **The guard's refusal of `lscpu` (OI-136 guard owner) and thread pinning (driver/helper owner).**
   Under the guard, LightGBM's physical-core probe falls back to a count that is very probably half
   of a two-socket node's cores (§7.6). Two candidate remedies, neither tested here:
   - model `lscpu` as a leaf tool in the guard's launch grammar;
   - pass an explicit `n_jobs` (= `OMP_NUM_THREADS`) to the helper's LightGBM estimators.

   Either way, a future timed run should record the trainer's effective thread count in its
   receipt.
