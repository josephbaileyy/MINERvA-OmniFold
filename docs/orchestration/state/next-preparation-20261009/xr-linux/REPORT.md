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

_DRAFT — results sections are filled in as the assignment proceeds._

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
