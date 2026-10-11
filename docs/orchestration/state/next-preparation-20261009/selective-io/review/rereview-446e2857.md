# Focused re-review: repair batch 1 (`446e2857`, parent `6486867f`)

Read-only. Reruns used my own detached worktree at `446e2857`, removed afterwards. Mutants ran on a scratch copy outside every checkout.

## Verdict

**PASS.** The repairs are accepted and the implementation is ready for integration. F1–F6 are resolved as REPORT §12 dispositions them. F7 needed no change. The repair introduced no new defect. One NOTE is below; it requires no change.

## Checks

**(3) The preserved review is byte-identical.** `cmp scratchpad/selio/review-6486867f.md S/review/review-6486867f.md` reports no difference.

**Scope.**
- `git diff --name-only 3892e769 446e2857` lists the driver, `tests/test_selective_io.py`, `2D_OMNIFOLD_REFERENCE.md` and files under S/. Nothing else.
- `git diff --quiet 6486867f 446e2857 -- 2d-unfolding/unfold_2d_omnifold_unbinned.py` holds: no driver byte changed in this batch.

| finding | repair at `446e2857` | verified |
|---|---|---|
| F1 | `test_selective_io.py:596–600`: `output_objects()` now also records Y-axis low edges and `repr(GetEntries())`. REPORT §6 now names exactly those operands | Diff read. New suite rerun: **Ran 27, OK**, 0 skipped (42.6 s). So both settings also agree on Y edges and entries in all six modes |
| F2 | REPORT §8 has a new row for the other importers, all unaffected | The substance holds (see the NOTE on the count) |
| F3 | REPORT §1 bullets 2–3 and the reference subsection (`2D_OMNIFOLD_REFERENCE.md:203–204`) now say the outputs come from a stub helper with nothing trained | Diff read |
| F4 | §3 now cites `:2061` (with the literal at `:2059`). The reference doc says loky's `lscpu` probe, reached through LightGBM. The mutation run has been redone with complete lists | My tally of `S/logs/mutation-run-2.txt`'s FAIL/ERROR lines gives **4 / 17 / 26 / 17 / 1 / 3**; M4 is "failures=16, errors=1", and each block has its `Ran 19` line. This matches §6 |
| F5 | The reuse test (`test_selective_io.py:353–358`) asserts null addresses on the derived branches after each derived call. New mutant `M6-no-address-restore` added to `checks/mutants.py` | I applied `mutants.py … M6-no-address-restore` to a scratch copy and ran `Loaders`+`Refusals`: **FAILED (failures=3)**, `AssertionError: True is not false` for the three reused trees. There was **no segfault**, so detection is now by assertion |
| F6 | `frozen_package_checks.sh:28–31` adds `git cat-file -e "$commit^{commit}"`, which refuses with exit 2 and its own message. `:50` runs XR's `manifest --check` under `"$py"` | The new check is read-only (`cat-file`) and runs before any worktree is created. A copy with the sb1 commit set to 40 zeros printed "commit 0000… is not in this repository; fetch it first", **rc 2**, worktree count unchanged (38→38). Bad usage gives rc 2. The XR rerun under the chosen interpreter is recorded in `S/logs/frozen-routing-xr-2.txt` (manifest current, 42 OK, rc 0). I did not rerun it, because the edit cannot affect the SB1 branch or the worktree handling |
| F7 | no change, by design | — |

REPORT §12 summarises my initial review accurately: PASS WITH CHANGES, 0 MATERIAL / 3 MINOR / 4 NOTE, and the reproductions and probes are listed correctly.

## Finding

**N1 — NOTE — the importer count of 49 cannot be re-run from the stated method.**
- The new row at REPORT §8 gives the method only as "`git grep -l` for an import of the module, at `6486867f`".
- My strict count, of files containing an `import unfold_2d_omnifold_unbinned` or `from unfold_2d_omnifold_unbinned import` statement (excluding `docs/orchestration/state` and prose hits), is **44**: 35 in `nd-unfolding/`, 6 in `pet/`, and one each in `2d-unfolding/`, `3d-unfolding/` and `docs/analysis-note/`.
- An unanchored grep that also counts prose gives 52.
- The row's breakdown adds five files to my 44: one in `nd-unfolding/`, three in `nd-unfolding/tests/` and one in `2d-unfolding/uq/`. They match files that load, inspect or stub the module by name or path, such as `fixed_truth_toy.py`, `eavail_scale_study.py`, and `test_fullevent_extract.py`/`test_k0_5ab_separated_roots.py`, which use `sys.modules`. That reading is inferred.
- Either way, the conclusion holds: no importer is affected.
- Optional disposition: record the exact grep pattern next to the count, or say "44 importing files, plus 5 that load or stub it by name or path".

## Resources

- Window: 2026-10-11T06:32:06Z – 06:35Z.
- Local CPU: about 0.02 core-h (suite 43 s user+sys, M6 run about 12 s, greps).
- Worktree `scratchpad/rr-wt` at `446e2857`: `git status --porcelain | wc -l` = **0 at start, 0 at end**; removed with `git worktree remove --force`.
- No `git config`, no cluster contact, one test process at a time, `OMP_NUM_THREADS=1`, `TMPDIR` under `scratchpad/review-tmp`.
