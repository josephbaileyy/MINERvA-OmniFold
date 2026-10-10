# Focused re-review of the integration repair batch (`2a394cd1..51e0d98b`)

- **Reviewer:** Claude Opus 5.5 (`claude-opus-5-5`), the same fresh read-only Claude Code subagent that did the initial review. This is its one focused re-review. It is not cross-provider independent.
- **Fixed commit:** `51e0d98beff994faafcbe6a9336eb97bbe484d55`. Delta reviewed: `c829c1ea` (code) and `51e0d98b` (records).
- **Time:** 2026-10-10T04:01:35Z to 04:05:11Z (UTC). The background tests started at the beginning of that window.
- **CPU:** about 0.07 core-h, 1 thread per command, at most 2 concurrent.
- **Worktree** (`scratchpad/review-wt2`, detached at `51e0d98b`):
  - At the start, `git status --porcelain --untracked-files=all` was empty.
  - At the end, the same command was still empty, and HEAD was unchanged. `--ignored` showed four `__pycache__/` directories only.
  - I deleted the scratch clone `mut2` (restored, 0 changes), then removed the worktree with `git worktree remove --force`. `worktree list` no longer shows it.
- **Boundaries kept:** no cluster or GPU, and no other worktree touched.

## Verdict: **PASS**

All seven findings are resolved as their dispositions say. The R2 tightening is correct, refuses the two F4 cases, and still admits every legitimate form of a canonical repository-relative path that I tried. Suites, mutants, manifest and lint are green. The delta stays inside the owner's scope. One new NOTE (N1) is cosmetic and does not need a repair round.

## Per-finding status

| id | status | evidence |
|---|---|---|
| F1 | **RESOLVED** | §10 now says "≈ 170 kB, net, against `dd73de73`". I re-measured at `51e0d98b`: new files 122,883 B plus net growth of modified files 50,080 B = **172,963 B** (≈ 169 KiB). Itemized: `MANIFEST.tsv` +39,966, REPORT +30,477, preserved review +16,671, new test +8,995. The "10 MiB" cap matches the dispatch convention (DISPATCH.md:90; guard REPORT:453). See N1 for one stale sub-figure. |
| F2 | **RESOLVED** | KNOWN_ISSUES rows 89 and 90 now say "delivered on `integrate/next-preparation-20261009` … for merge to `main`". The diff touches only those two rows; row 88 and every other row are unchanged. |
| F3 | **RESOLVED** | **§7 sb1-prep** now carries speed §15's condition: SB1 matters only if option (b) or (c) is to be priced, "neither of which the 2026-10-09 ruling authorizes". **two-d-path** now reads: transfer, N2, re-quote, KI-85 lift, changed gates and reopened terminal campaigns are "**not authorized**", and a changed central estimator is "reserved to Joseph". **d-id** adds "0 Slurm, one owner and one fresh reviewer", the §10.3 scope question, and the simulation-only/conditional caveat. Each CATALOG row has a short pointer: "the ruling's prohibitions stand", "SB1 itself needs Joseph's authorization", "not admitted; its branch-B route is unreviewed". No text grants authority. |
| F4 | **RESOLVED** | Analysis of the R2 tightening and my probes are below. |
| F5 | **RESOLVED** | The §3 gbdt cell now reads "branch-B downstream route (N1, #8) and the cost repair (#7)", and distinction 1 says the same. The PET source is now cited as "`results/design_cost.json` (`events.inventory_multiples_for_independent_validation`)". |
| F6 | **RESOLVED** | §4.2 now says "must contain the R1 code commit `21c97390`; `b19b5e91` adds only the test". |
| F7 | **RESOLVED** (recorded, no change) | §8 records the mode difference as pre-existing and out of scope. That matches the NOTE severity. |

## R2 tightening (`c829c1ea`)

**The change.** `norm` is now built in three steps:
1. `os.path.normpath(rel)`, applied to a relative `rel` only; an absolute `rel` gives `""`.
2. Refuse when the result is `""`, `.` or `..`, or starts with `../`.
3. Refuse when `(top / norm).resolve() != top / norm`, so any symlink component is refused.

The prefix and name rules, the digest check and the HEAD check then all apply to `top / norm`, so the stated path is the checked path. For a missing file, `resolve()` is non-strict, so it passes this step and is then refused by `is_file()` with the "absent" message.

**Probes.** I subclassed the suite's `Harness` fixture in a scratch clone at `51e0d98b`. Each case states the target file's true digest.

| path tried | result |
|---|---|
| canonical `docs/orchestration/AUTHORIZATION-…` | rc 0, "admission holds" |
| `docs/orchestration/./AUTH…` | rc 0 |
| `./docs/orchestration/AUTH…` | rc 0 |
| `docs//orchestration/AUTH…` | rc 0 |
| trailing slash `…/AUTH….md/` | rc 0 (normpath strips it; harmless) |
| `docs/orchestration/sub/../AUTH…` (lexical) | rc 0 |
| `DECISION-` record in `docs/orchestration/state/x/` | rc 0 |
| absolute in-checkout path | rc 3 |
| `docs/orchestration/../../elsewhere/AUTHORIZATION-…` | rc 3 |
| `""` | rc 3 |
| backslash separators | rc 3 |
| committed symlink (the suite's new case) | rc 3 |

No legitimate committed record is wrongly refused. A real record could only be refused if a symlinked directory sat in its path inside the checkout. `git ls-files -s` shows **0** tracked symlinks under `docs/`. `top` is itself resolved, so a symlinked checkout root does not cause a refusal.

**Mutation.** `logs/mutation-results.json` is at `c829c1ea`: `all_controls_pass: true`, caught 7/7. `R2-revert` fails 3 subtests and `R2-first-version` fails 2. I reproduced `R2-first-version` myself by restoring the `resolve().relative_to(top)` block. The R2 test went **red**, FAILED (failures=2), on exactly "the canonical record, as an absolute path" and "a symlink to the canonical record". After restoring, the test was OK and the clone had 0 changes. The run-1 log is preserved byte-identical as `logs/mutation-results-run1-b19b5e91.json` (same blob as the old `mutation-results.json`).

**Suites at `51e0d98b`.** 0 skips in each.

| suite | result |
|---|---|
| harness (`python3 -m unittest discover -s 2d-unfolding/uq/coverage_fixed_truth/n2 -p 'test_n2*.py'`) | Ran 22, OK |
| both OI-136 ratchets | Ran 17, OK |
| `verify_hash_bindings.py` | ALL BINDINGS INTACT |

## Other checks

- **Preserved review:** `integration/review/review.md` and my original `review-scratch/review.md` both have sha256 `f67d51cc82b81e323067cc77ab87aae51fb381ba4745ef54a605cad03aa1897e`, and `cmp` says they are identical. Its MANIFEST row is `MACHINE generated` (immutable), as for the other lanes' preserved reviews.
- **Manifest and lint:**
  - `generate_manifest.py --check --at-sha HEAD`: OK at `51e0d98b`.
  - `live_doc_indexed.py --unrowed`: 0.
  - `control_plane_lint.py`: CONTROL-PLANE PASS (1,952 tracked files).
- **Scope:** the delta touches 10 paths:
  - `n2/harness.py` and `n2/test_n2_harness.py`, for R2/F4 only;
  - `KNOWN_ISSUES.md`, rows 89 and 90 only;
  - CATALOG's next-session rows;
  - regenerated `MANIFEST.tsv`;
  - the `Q/integration/` subtree (REPORT, `checks/mutation.py`, two mutation logs, `review/review.md`).

  There are no changes to the guard core, `execution.py`, the driver, `omnifold.py`, `OPEN_ITEMS.md`, lane files or receipts. No new number, figure or readiness claim appears. §8 and §11 still say PASS only "if the review finds no material defect", and the publication-ready disposition stays NOT ACHIEVED.

## New findings

| id | severity | file | finding | suggested repair |
|---|---|---|---|---|
| N1 | NOTE | `Q/integration/REPORT.md` §10, tracked-bytes row | "this report ≈ 27 kB" is stale within the same commit. The report is now 30,477 B larger than at `dd73de73`, where it did not exist. The ≈ 170 kB total is still right (measured 172,963 B). | Optional: write "≈ 30 kB", or leave as is. |
