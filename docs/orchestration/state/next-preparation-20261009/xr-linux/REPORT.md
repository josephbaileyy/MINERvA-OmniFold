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
