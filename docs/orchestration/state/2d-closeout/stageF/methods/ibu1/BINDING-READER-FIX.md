# IBU-1 binding addendum: the reader fix, ruled before any result (2026-10-23)

**By** the paper-tighten lane, as director, under [`DECLARATION.md`](DECLARATION.md), [`BINDING.md`](BINDING.md) and
[`BINDING-C.md`](BINDING-C.md).

**Facts reported by the validation lane** (to be restated, with evidence, in the IBU-1 report):
- Job C (60140287) COMPLETED 0:0 in 2,362 s (0.6561 CPU node-h). The charge so far is 1.0652 CPU node-h.
- There are 2,934 products, and the meta check passes 2,934/2,934. All 1,049 experiment comparator gates pass, plus 3 bootstrap base gates (the lane first reported 1,013; it corrected the count from `metacheck.json`). SHA256SUMS
  `0e45d41c…`.
- The frozen reader `ibu1_read.py` (`2214d487…`) raises `ValueError` at `:76` in `load_unit`. The IA-12 loop
  (`IBU_OWN`, `:293`) loads all 400 seeds of N_gibuu and N_w1–w3, and only 60 or 20 of those carry `f_of`, so
  `np.array` receives a mix of arrays and `None`.
- The crash came before any output. No result has been seen and no output file was written.
- IA-12 never reads `"of"`. Every use of `u["of"]` (`:234`, `:237`, `:273`) is in the paired comparisons, which load
  only the gated paired seeds.
- The tests missed it because the end-to-end fixture gave every unit's seed range a comparator, which the real
  config does not.

## Ruling: the fix is accepted as a post-binding amendment, with conditions

1. **The fix.** `ibu1_read.py:76` returns `"of": None` when any row lacks `f_of`, as proposed.
2. **Fail explicitly, not by accident.** The paired-comparison path must assert that `u["of"]` is not `None`, at each
   use (`:234`, `:237`, `:273` or their equivalents), with a message that names the unit. A `TypeError` deep in
   `relO` is not an acceptable failure mode for a missing comparator.
3. **Tests in both directions.**
   - The fixture straddles the paired range, as the lane proposed.
   - The frozen reader fails on it with the real run's `ValueError`.
   - The fixed reader passes it.
   - A new test checks that a paired load with a missing `f_of` raises the explicit assertion.
4. **Record.** The report gives the old and new reader sha256, the full diff, the test output, and the statement that
   no rule, threshold, unit, seed or comparator changed. The fix and the report go in the same PR. The read is rerun
   from the pinned products (SHA256SUMS `0e45d41c…`).
5. **No other change** to the reader or the rule. Any further reader defect stops the read and comes back to the
   director before any output is looked at.

## Incident noted

The lane's test ran `git stash pop` after a no-op `git stash push`, which applied the repository-wide `stash@{0}`
(`r5-receipt-temp`, 2026-09-08, someone else's) into the lane's detached read worktree, with a conflict. The lane
restored that file to HEAD in its worktree. The director checked (2026-10-23):
- `git stash list` still holds `stash@{0}` `805a0e6a…` and `stash@{1}` `6db38398…`, unchanged;
- the shared checkout's `git status` matches its state at the start of this session.

Stashes are shared by all worktrees of the repository, so lanes must not use `git stash` in tests. They should use a
throwaway clone or a temporary branch instead.
