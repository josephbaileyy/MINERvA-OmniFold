# XR on the Linux runtime: the repaired package, its admission, the preflight and the five XR runs

**CITABLE FOR:**
- the xr-linux XR launch package, its tests and its Linux probe;
- its admission evidence, the in-allocation preflight and its fixture stage;
- the scheduler record and the cumulative charge;
- the five runs' comparisons against the frozen 1e-8 criterion, where they ran;
- the independent numerical verification.

**NOT CITABLE FOR:**
- any cross section, uncertainty, coverage or calibration result;
- a re-quote, an adoption, a narrowed claim or a changed gate;
- seed invariance in general, or a resolution of the 2D pairing issue;
- an uncertainty transfer, covariance production, N2 or a KI-85 lift;
- compute authority beyond `AUTHORIZATION-20261011-xr-linux.md`.

| field | content |
|---|---|
| `Lane` | `xr-linux` (XR owner; registered by the XR/SB1 integration, its REPORT §8) |
| `Decision` | Can the original five XR runs, with unchanged inputs, estimator settings, references and comparison rules, answer the central-reproduction and one-seed questions? |
| `Branch` / `Base` | `run/xr-linux-20261010` / `3892e769043cddebfd58ec19e1ab1a567eb01784` (`origin/main`, PR #77; refreshed at the start, no later commit) |
| `Owned files` | `Q/xr-linux/` (this record, the package `xr/`, `logs/`, `results/`, `review/`); `docs/orchestration/AUTHORIZATION-20261011-xr-linux.md` and its two registration rows (one `MANIFEST-overrides.tsv` row, one `CATALOG.md` routing row) |
| `Owner / reviewer` | One owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code. One fresh read-only reviewer: Claude Opus 5.5, a general-purpose subagent of this session. Same provider and model as the owner: **not** a cross-provider review. The campaign review's suggested Astra High reviewer is not available in this session |
| `Review budget` | admission review; at most two focused repair/re-review cycles in total; final independent numerical verification |
| `Terminal outcomes` | admission, preflight, execution and each comparison are each PASS, FAIL or INCONCLUSIVE. A failed preflight stops dependent execution; the window is 72 h from the first preflight submission |

`Q` = `docs/orchestration/state/next-preparation-20261009`; `P` = `Q/xr-linux/xr` (the package).

## 1. Answer

**Yes. The five runs, with unchanged inputs, estimator settings, references and comparison rules,
answer both questions.** Admission PASS; preflight PASS; execution PASS (all five runs complete on
their first attempt). Each comparison, under the frozen 1e-8 criterion on the 205 reported cells and
their area-weighted integral:

| comparison | question | verdict | max \|new/ref − 1\| | median | integral |
|---|---|---|---|---|---|
| `X0_vs_E_C` | today's driver regenerates the quoted exact central | **PASS** | 3.9e-15 | 5.6e-16 | 2.2e-16 |
| `X0p_vs_E_C` | the `d1bc8813` driver (today's helper) regenerates it | **PASS** | 7.1e-15 | 4.4e-16 | 0 |
| `X1_vs_X0` | one-seed P09b: `random_state` 1/2/3 against `None` | **FAIL** | 1.6e-2 (GlobalID 111) | 1.8e-3 | 4.0e-6 |
| `L0_vs_CV42` | a CV-file seed-42 run reproduces the adopted sweep's CV | **PASS** | 1.4e-11 | 5.9e-12 | 7.0e-13 |
| `L0_vs_PN_CV` | the same against the July background-aware sweep's CV | **PASS** | 9.8e-13 | 2.2e-14 | 1.4e-14 |
| `L1_vs_SEED1` | a seed-1 run reproduces the seedscan seed-1 central | **PASS** | 2.4e-12 | 6.3e-14 | 4.2e-14 |
| `NC_X0_vs_CV42` | negative control: different estimators must FAIL | **FAIL = control met** | 1.4e-1 | 9.9e-3 | 9.4e-5 |

- **Central reproduction: PASS.** The quoted exact central `E_C` is regenerated, by today's driver and
  by the `d1bc8813` driver, to rounding (29–32 of 205 cells bitwise equal; the rest differ in the last
  bits). Both LightGBM centrals and the seed-1 central are regenerated to ≤ 1.4e-11, under 64
  LightGBM threads, inside the 5.8e-9 thread prior, so the pre-registered L-arm thread-cause check
  was never triggered.
- **One-seed question: FAIL — terminal.** Seeding the exact backend (`random_state` 1/2/3, X1) moves
  every one of the 205 cells relative to the unseeded run (X0): median 0.18 %, max 1.6 %, integral
  4.0e-6. The exact central is therefore **not** invariant to the estimator seed at the frozen
  criterion. Per the frozen rules, this is an outcome, not a reason to retry. Its mechanism was not
  examined: the run path sets no global numpy seed, the estimator settings are sklearn's defaults
  (no subsampling, all features), and why the unseeded run reproduces `E_C` while seeded runs move is
  an open question for the 2D estimator owner. It is not a measurement of seed spread (one seed
  triple), and it changes no gate.
- Cumulative charge **3.0911 of 6.4** CPU node-h on m3246 (every XR job since 2026-10-10), from sacct.
- Independently reproduced by the owner (`checks/reproduce_comparisons.py`) and by the final
  numerical verification (§8).

## 2. Baseline, reading and preservation

- **Baseline.** `git fetch` at the start: `origin/main` = `3892e769` (PR #77), the integration commit
  the dispatch names; no later commit to reconcile. Isolated worktree
  `MINERvA-OmniFold-xr-linux-20261010` on the new branch `run/xr-linux-20261010`. The canonical local
  checkout and its untracked files were not touched.
- **Read:** `AGENTS.md`, `CAMPAIGN-REVIEW-20260929.md`, `docs/CURRENT_WORK.md` (no XR row; XR is
  routed by `CATALOG.md`'s 2026-10-11 table), `Q/two-d-followup/REPORT.md` (B1–B8, E.3) and its
  reviews, `Q/xr-recovery/REPORT.md` and its three reviews, `Q/sb1-run/REPORT.md` (§7.6, §11),
  `Q/xr-sb1-integration/REPORT.md` (§8).
- **Preserved, unchanged:** `Q/two-d-followup/` (including its package `xr/`, whose `d1bc8813` record
  copy X0p executes in place, by digest), `Q/xr-recovery/`, `Q/sb1-prep/` (whose fixture writer the
  preflight executes in place, by digest), `Q/sb1-run/`, both earlier authorizations, both earlier
  outroots on `/pscratch` and both earlier cluster worktrees. No production driver, helper, guard or
  shared register was edited.
- **The driver pin (integration §8).** X0, X1, L0 and L1 execute `2d-unfolding/unfold_2d_omnifold_unbinned.py`
  at sha256 `3cc5adc7306b3043c2fd147602d866b90162644523b64060462aa4d934766933`, measured on the
  baseline tree; its last change is `355174fe64309811ca6a0d79ced46f2a71f653a9` (2026-10-09, "REPAIR 1:
  hash the driver at main() start and the helper at import"). It is pinned from the integrated
  baseline, as in `07428e5d`: `runs.json` carries the digest, `xr_run.py` refuses any other bytes,
  `xr_admit.py check` refuses a HEAD whose driver differs from the package commit's, and the cluster
  worktree is detached at this branch's authorization commit, which contains no selective-I/O change.
  A selective-I/O merge on `main` therefore cannot reach these runs; it would only make this package's
  at-HEAD `manifest --check` report OUT OF DATE on a later `main` (integration §8 item 3).

## 3. The package (`P`, package commit `60bd68c0`, manifest `5d2f5955…`)

A new package, built from `07428e5d`'s and changed only where the grant's six repair items require.
Each item, with what was done:

1. **The environment inspection that launched `ldconfig` is gone, and the guard is unchanged.**
   `check_environment` keeps the frozen version check and the module origins. It no longer calls
   `threadpoolctl.threadpool_info()`, whose `ctypes.util.find_library("c")` runs `/sbin/ldconfig -p`
   on Linux. In its place, `runtime_record()` lists the loaded OpenMP, BLAS and LightGBM libraries from
   `/proc/self/maps` and calls each library's own thread getter through `ctypes.CDLL(<absolute path>,
   RTLD_NOLOAD)` — no `find_library`, no child. That record is labelled supporting evidence only. A
   unit test fails if `threadpool_info` or a write to loky's private cache reappears in `xr_run.py`, or
   if `find_library` appears outside the deliberate launch control.
2. **Effective threading, established before any fit and checked at every fit and prediction; no
   estimator setting changed.**
   - `thread_plan(kind)`: `OMP_NUM_THREADS` equals the kind's; on Linux `LOKY_MAX_CPU_COUNT` is unset
     (the job script unsets it), the CPU affinity equals the kind's CPUs and is below the node's count,
     and `joblib.cpu_count(only_physical_cores=True)` — what LightGBM's default `n_jobs` resolves to —
     equals the kind's CPUs. Below the node's count joblib returns the affinity count without querying
     physical cores, so the guard-refused `lscpu` (and its undercounting `/proc/cpuinfo` fallback, SB1
     §7.6) is never reached. A full-node allocation is refused rather than seeded.
   - The loky cache seed of the earlier packages is removed: nothing writes joblib's private state.
   - `FitRecorder`: before each LightGBM fit, the count LightGBM resolves (`_process_n_jobs`) must equal
     the plan; after it, the booster's `num_threads` must equal that count (an alias override is
     caught); every `LGBMModel.predict` is recorded and checked the same way. The exact sklearn
     backend has no thread parameter and builds trees serially; the receipt records 1 thread, from
     the source.
   - On the frozen configuration this is the pre-registered one: L0/L1 on shared-64 train with 64
     LightGBM threads (the references used 128; two-d-followup B1's thread-cause check stands), the
     exact arms serially.
3. **A launch window.** From the environment check to the end of the fit path, `LaunchSpy` replaces
   `subprocess.Popen` and the `os` launch primitives; any attempt is refused and recorded, and
   `require_no_launch` fails the run even when a library caught the refusal (loky does). It only
   narrows what may run; the OI-136 guard and its leaf table are untouched.
4. **The preflight exercises the whole Linux path in the allocation, including fits.** Through the
   real `xr_job.sbatch`: allocation parsing (`jobcheck` on the real `scontrol` line), admission
   `verify`, the setup sourced, then two job controls (this allocation checked against the lgbm kind
   must be refused; a guarded child calling `threadpool_info` must be refused by the guard), then
   `xr_run.py --run PF` under the guard: helper and all drivers from verified bytes, strict identity,
   both production inputs hashed, the environment check, the thread plan, the identity and input
   rechecks — no fit on production inputs — and then the **fixture stage**: SB1's frozen fixture
   writer (executed by digest) writes a 3,000-row synthetic omnifile in the attempt directory, and the
   five configurations run end to end in-process with their own drivers, argv templates, backends and
   seeds (fits and predictions; 10 classifier and 5 regressor fits each), plus an L0 repeat (frozen
   1e-8 criterion), the comparator both ways (repeat PASS, X0 vs L0 FAIL), refusal controls (wrong
   seed, wrong backend, wrong LightGBM thread count — each before training) and the launch-window
   controls (`find_library("c")` and loky's physical-core query must be refused). The fixture
   products are synthetic, live only in `PF/a<N>/fixture/`, and no comparison can read them.
5. **Scheduler formats and the ledger header.** Real Perlmutter captures: the preflight's own RUNNING
   `scontrol` line, the current `sacct -X -n -P` and ledger-format output, and seven historical rows
   chosen by state (`CANCELLED by <uid>`, TIMEOUT, array ids, PREEMPTED, gres items). Every parser is
   tested on them. The ledger now refuses (exit 6, printed reason) a header lacking any required
   column before reading a row — recovery review N-1.
6. **Frozen anew.** Package `60bd68c0`, manifest `5d2f5955…`, outroot
   `/pscratch/sd/j/josephrb/xr-linux-20261011`, job names `xrl_<RUN>_a<N>`. The five runs, their argv,
   backends and seeds, the inputs, the frozen environment, `references.json` (byte-identical), the
   comparator (byte-identical), the comparisons, the negative control, the 1e-8 criterion, cell
   identity and missing-result rules are those of `07428e5d` (admission review B-1).

**Accounting and release** (`xr_admit.py`). Both earlier grants' six jobs are prior and must appear in
sacct exactly; their charge, 2132/921600 = 0.002313368055555556 node-h, is recomputed by every ledger
and enters every planned ceiling. Caps: 2 preflight, 4 exact, 3 LightGBM attempts in total; a run's
second attempt needs a stated `--diagnosis`, recorded in `submissions.jsonl`. The release gate
requires the PF job's own bound receipt with the fixture verdict PASS, every check and control met,
no launch recorded, and a clean guard inventory; then L0 alone; then the rest once L0 has a complete,
comparable receipt. The 72-h stop is passed to Slurm as `--deadline`.

## Pre-registered before the first preflight submission (2026-10-11)

- **A fixture L0-repeat FAIL** (the in-allocation L0 fixture run repeated in the same process does not
  meet the frozen 1e-8 criterion; admission note E-3) is recorded as a **preflight FAIL** whose cause is
  LightGBM run-to-run instability at the preflight's thread count, **not** an infrastructure defect. It
  does not qualify for the diagnosed-infrastructure repair and second preflight; dependent execution
  stops, every comparison is INCONCLUSIVE, and the next decision goes to Joseph. The count of
  bitwise-equal cells is recorded either way.
- **Any other preflight FAIL** is diagnosed from the receipt, the job logs and sacct before anything
  else is submitted. Only a diagnosed infrastructure cause admits a repair, which is reviewed
  (focused re-review, carrying admission finding E-1) before the second and last preflight.
- **After a passing preflight:** L0 alone; X0, X0p, X1 and L1 only when the release gate finds L0's
  complete, comparable receipt. A comparison FAIL is a terminal outcome, never a reason to retry.
- **L-arm FAIL:** first examined for a thread-count cause against the ≤ 5.8e-9 prior (the
  64-versus-128-thread difference pre-registered in the two-d-followup REPORT B1); the criterion does
  not change.

## 4. Admission: PASS

- **Review** (`review/admission-review-60bd68c0.md`, verbatim): **ADMIT** at package `60bd68c0`,
  manifest `5d2f5955…` re-hashed by the reviewer. One MINOR finding (E-1: a *repaired* package's
  accounting would not import this package's `xrl` attempts). It applies only to a repair after a
  failed first preflight. None happened, so E-1 never became live. Notes E-2 to E-4, A-1 to A-4,
  B-1, C-1 and D-1 confirm the time budget, the thread plan on a correct allocation, both job
  controls on Linux, the scientific definitions unchanged against `07428e5d`, the driver pin and
  the accounting. E-3 led to the pre-registration above. Reviewer window 05:49:49Z–06:10Z.
- **Authorization.** `docs/orchestration/AUTHORIZATION-20261011-xr-linux.md` quotes the dispatch and
  binds package `60bd68c05ad89116ac5a4bca5f925f8da1240e4e` and manifest `5d2f5955…`. It has one
  `MANIFEST-overrides.tsv` row and one `CATALOG.md` routing row.
- **Admission record.** `/pscratch/sd/j/josephrb/xr-linux-20261011/admission.json`, sha256
  `6b7660f4…`, drafted with `xr_admit.py draft` on the cluster worktree
  `MINERvA-OmniFold-xrl-92386d3f`. That worktree is detached at `92386d3f` (this branch, after the
  amendment commit), with `git status --porcelain` empty at the start and before every submission.
  The canonical cluster checkout (`32e403b8`) was not moved.
  It is held off the tracked tree (results/README.txt): tracking it adds one live receipt
  binding, and the verifier constants belong to integration (§9).
- **Ledger before the first submission.** The six prior jobs (both earlier grants) were matched
  in sacct. Prior charge 2132/921600 = 0.002313368055555556 node-h; `over: []`.

## 5. Preflight: PASS (one of two allowed attempts used)

Job **59659845** `xrl_PF_a1`, submitted 2026-10-11T06:13:23Z. That submission starts the 72-h window,
which ends **2026-10-14T06:13:23Z** and is passed to Slurm as `--deadline`. The job ran on
`nid004085` from 06:41:05 to 06:43:32Z: ElapsedRaw 147 s of the 300-s limit, billing 12,
COMPLETED 0:0. The receipt is `results/outroot/PF/a1/preflight-receipt.json` (sha256 `50907f29…`,
schema `xr-preflight-receipt/2`, `status: preflight-pass`, `launches: []`). It shows:

- **Allocation and admission.** `jobcheck` passed on the real RUNNING `scontrol` line
  (`scontrol-job.txt`; QOS shared, 12 CPUs, AllocTRES `billing=12`, 00:05:00), and
  `verify` passed.
- **Job controls, both met.**
  - `jobcheck --run L0` against this allocation: rc 3, "allocation outside the frozen caps"
    (NumCPUs 12 ≠ 64).
  - The guarded `xr_guard_control.py`: rc 3. The guard refused `/sbin/ldconfig -p`, and the
    control's inventory verdict is `REFUSED launch` (`results/controls-PF-a1.txt`).
- **Thread plan.** affinity 12, `os.cpu_count()` 256, joblib physical and logical counts 12,
  `LOKY_MAX_CPU_COUNT` unset, `OMP_NUM_THREADS` 12.
- **Environment.** Python 3.11.14, ROOT 6.28/12, joblib 1.5.3, lightgbm 4.6.0, numpy 1.26.4,
  scipy 1.16.3, sklearn 1.8.0, threadpoolctl 3.6.0, all equal to the frozen environment. The
  child-free runtime record lists libgomp at 12 threads and OpenBLAS at 1.
  - The separate `environment.packages` provenance field reads `null` for every package. It comes
    from the shared `n2` execution record, which looks up distributions by another route; the
    frozen check, `environment_checked`, is the one that gates.
- **Production inputs.** Both inputs hashed to their frozen digests (omnifile `43f8cc16…`,
  2,144,008,221 bytes on CFS; mcfile `d40aea69…`). The guard inventory verdict is
  `REPOSITORY-ORIGINS-INSPECTED`.
- **Fixture stage: PASS**, all six checks true.
  - The five configurations and the L0 repeat ran end to end on SB1's 3,000-row fixture, each
    with its frozen classes and seeds.
  - LightGBM used 12 threads at every fit and every predict.
  - The L0 repeat was bitwise equal in 176 of 176 cells: comparator PASS, max 0.
  - The comparator FAILs X0 against L0 (max 0.725), as the control requires.
  - All four refusal and launch controls were met.
- **Wall time.** `xr_run` took 104 s inside the 147-s job.

Under the release rule, this receipt was the gate for L0.

## 6. Execution

| run | job | submitted (UTC) | ran (UTC) | ElapsedRaw | billing | state | receipt |
|---|---|---|---|---|---|---|---|
| PF | 59659845 | 10-11 06:13:23 | 06:41:05–06:43:32 | 147 | 12 | COMPLETED 0:0 | preflight-pass |
| L0 | 59660487 | 10-11 06:44:07 | 08:24:41–08:38:37 | 836 | 64 | COMPLETED 0:0 | complete |
| X0 | 59664200 | 10-11 08:41:25 | 08:58:03–10-12 05:52:59 | 75296 | 12 | COMPLETED 0:0 | complete |
| X0p | 59664201 | 10-11 08:41:28 | 08:58:03–10-12 06:12:33 | 76470 | 12 | COMPLETED 0:0 | complete |
| X1 | 59664202 | 10-11 08:41:31 | 09:03:02–10-12 06:09:41 | 75999 | 12 | COMPLETED 0:0 | complete |
| L1 | 59664203 | 10-11 08:41:34 | 11:03:21–11:18:30 | 909 | 64 | COMPLETED 0:0 | complete |

**L0 first, and the release.** L0 (`results/outroot/L0/a1/receipt.json`) ran on `nid004128`. Its
receipt shows:

- `status: complete`, `launches: []`;
- 10 classifier and 5 regressor fits, with frozen classes and `random_state` 42/43/44;
- 64 LightGBM threads at all 15 fits and all 15 predict calls (affinity 64 of 256, joblib 64);
- identity rechecked;
- both inputs re-hashed against their frozen digests at the end. The digests are checked; the
  end record keeps stat fields only;
- output `XR-L0.root`, sha256 `75138024…`, 205 reported cells, and the 7 normalization parameters.

The guard inventory verdict is `REPOSITORY-ORIGINS-INSPECTED`. The release gate in `xr_submit.sh`
accepted this receipt, and X0, X0p, X1 and L1 were submitted together at 08:41Z, with no diagnosis
(first attempts).

**L1** (`results/outroot/L1/a1/receipt.json`, `nid004084`) has the same shape as L0:

- `status: complete`, `launches: []`;
- 10 classifier and 5 regressor fits, with seeds 1/2/3;
- 64 LightGBM threads at all 15 fits and all 15 predict calls;
- output sha256 `e472fa62…`;
- guard inventory verdict `REPOSITORY-ORIGINS-INSPECTED`.

**The exact runs** (`results/outroot/{X0,X0p,X1}/a1/receipt.json`) each completed in 20.9–21.2 h
of the 30-h limit, against about 19.3 h expected (`Q/speed` REPORT §3). sstat MaxRSS was 16.7–16.8 GB
of 22.86 GB. Each receipt shows:

- `status: complete`, `launches: []`, 10 classifier and 5 regressor fits, 205 reported cells;
- the frozen classes and seeds: `GradientBoosting*` with `random_state=None` for X0 and X0p, and
  1/2/3 for X1; 1 estimator thread from the source;
- X0 and X1 executed the pinned driver `3cc5adc7…` (logged `driverSha256`); X0p executed the
  `d1bc8813` record copy in place, by digest;
- outputs X0 `68a0de2d…`, X0p `3449de34…`, X1 `11ff7744…`;
- guard inventory verdict `REPOSITORY-ORIGINS-INSPECTED` for each.

No job failed, so no spare attempt and no diagnosis was used. At the end no `xrl` job was queued
(`squeue` empty), so nothing was left to cancel at the window's expiry.

## 7. Comparisons

The frozen comparator (`xr/xr_compare.py`, byte-identical to `07428e5d`) was run once on the
complete outroot on a Perlmutter login node: `results/final/comparisons-final.json` (sha256
`e43bf8f1…`). It enforces the receipt schema, the admission binding, the output digests, the
reference digests from `references.json`, the axes and the frozen 205-cell set. The table in §1 is
taken from it. For every comparison: axes equal, both cell sets equal the frozen 205.

The owner's independent reproduction (`checks/reproduce_comparisons.py`, sha256 `d9d96515…`,
written apart from the comparator, correctly rounded sums) gives `results/final/reproduction-final.json`
(sha256 `50dc9561…`). It agrees with the comparator on every maximum and median exactly and on every
integral difference to ≤ 1e-15 absolute (summation order). It also stores the 205 values (repr) of
each of the nine products read, so the comparisons can be re-derived from tracked evidence.

The interim files in `logs/` are the same comparator and reproduction run as each run finished.

**The X1 FAIL in detail.** All 205 cells exceed 1e-8; the ten largest are GlobalIDs 111 (1.62 %),
127, 5, 17, 18, 15, 1, 223, 4 and 6 (0.93 %). Every exceeding cell is listed in
`comparisons-final.json`. For scale, the negative control (exact against LightGBM) has median 0.99 %.

## 8. Independent numerical verification

_Pending: the final verification by the same fresh reviewer (review use 2)._

## 9. Resources

**Cluster** (m3246; charged node-h = ElapsedRaw/3600 × billing/256; `results/final/sacct-final-ledger.psv`,
captured 2026-10-12T06:13:19Z, and `ledger-final.json`, `over: []`):

| | jobs | CPU-seconds (ElapsedRaw × billing) | node-h |
|---|---|---|---|
| prior XR grants (5 `xr_*`, 1 `xrr_*`) | 6 | 2,132 | 0.0023134 |
| this grant: PF | 1 | 147 × 12 = 1,764 | 0.0019141 |
| this grant: L0, L1 | 2 | (836 + 909) × 64 = 111,680 | 0.1211806 |
| this grant: X0, X0p, X1 | 3 | (75,296 + 76,470 + 75,999) × 12 = 2,733,180 | 2.9656901 |
| **cumulative** | 12 | 2,848,756 | **3.0910981 of 6.4** |

The ledger's figure (`xr_admit.py ledger`) and the independent arithmetic above agree to every digit.
Attempts used: preflight 1 of 2, exact 3 of 4, LightGBM 2 of 3. No GPU, no full node, no resource
change. The sacct capture also lists six SB1 jobs of the same user, which the ledger does not read.

**Local:** about 1.1 CPU core-hours in total (the suite and mutation pass before admission; the rest
is ssh and file copies), two threads at most, well under 8 GiB and 3 GiB of scratch. Active time,
excluding scheduler waits, about 5 h of 10.

**Durable copies.** Receipts, guard inventories, `scontrol` records and digested Slurm logs are tracked
under `results/`. The five ROOT outputs (ignored by `.gitignore`) were copied read-only to
`/global/cfs/cdirs/m3246/josephrb/xr-linux-20261011/outputs/<RUN>/a1/`, with sha256 re-measured equal
to their receipts; their reported-cell values are in `reproduction-final.json`.

## 10. Proposed changes for integration (exact; not applied here)

The dispatch reserves shared-register and binding-inventory changes for integration.

1. **Enroll the admission record.** Recover `/pscratch/sd/j/josephrb/xr-linux-20261011/admission.json`
   read-only at sha256 `6b7660f44632bad13304209d17d3929bc7d5c7bed535176f70d80a27259f118d`, track it as
   `Q/xr-linux/results/outroot/admission.json`, and move `docs/orchestration/verify_hash_bindings.py`'s
   constants from `RECEIPT_BINDING_COUNT = 148` / `1b610bb3…` to **149** /
   `6a3787ea17b042e371908a70bc83f720300557fc9f1464ba9ddace9850215b13`. Measured on this branch's final
   tree with the copy in place; without it the gate reports 148 / `1b610bb3…`, ALL BINDINGS INTACT.
   No other file in `Q/xr-linux/` adds a binding.
2. **`CATALOG.md` outcome row**, under the 2026-10-11 XR rows:
   `| XR owner (xr-linux). Delivered 2026-10-12: admission PASS; preflight PASS; all five runs complete;
   central reproduction PASS (X0 and X0′ regenerate E_C to ≤ 7.1e-15; L0 regenerates CV42 and PN_CV
   and L1 regenerates SEED1 to ≤ 1.4e-11); one-seed P09b FAIL (X1 against X0: median 0.18 %, max
   1.6 %); negative control met; 3.09 of 6.4 node-h cumulative | `state/next-preparation-20261009/xr-linux/REPORT.md` |`
3. **`docs/orchestration/MANIFEST.tsv`**: regenerate with `generate_manifest.py` for the new
   `Q/xr-linux/` files (none of them has a row yet; the gates pass without one).
4. **`docs/CURRENT_WORK.md`**: an `xr-linux` row with the line in item 2; no follow-on work is
   authorized by this grant.
5. **For the OI-136 owner** (observation only): on Linux, `threadpoolctl.threadpool_info()` and
   joblib's physical-core query reach `/sbin/ldconfig` and `lscpu`, which the guard refuses. This
   package avoided both without changing the guard: it read `/proc/self/maps` with `RTLD_NOLOAD`, and
   used an affinity below the node's CPU count. Any guarded LightGBM run on a full node would still
   reach `lscpu`.
6. **For the 2D estimator owner** (observation only): unseeded exact runs regenerate `E_C` to
   rounding, twice, with two driver revisions, while one seeded run moves every cell (median 0.18 %).
   The mechanism is unexamined. This is one seed triple: it is not a seed-spread estimate, and no
   claim, gate or re-quote changes.

## 11. Limitations and what this record does not do

- One owner and one reviewer, both Claude Opus 5.5: no cross-provider independence.
- X1_vs_X0 is one seeded run against one unseeded run. It answers the frozen one-seed question
  (FAIL) and nothing about the distribution of seed effects.
- The exact backend's single thread is read from sklearn's source (admission note B-1), not measured.
- `environment.packages` in every receipt reads `null` (§5); the gating version check is in
  `environment_checked`.
- No uncertainty transfer, covariance, N2, KI-85 lift, re-quote or publication change was made or is
  supported by this record.
