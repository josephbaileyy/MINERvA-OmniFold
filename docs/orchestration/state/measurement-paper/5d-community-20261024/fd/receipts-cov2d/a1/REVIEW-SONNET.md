# A1: a fresh review of the writer diff (Sonnet, read-only), 2026-11-03

**Who and how:** a fresh Claude Sonnet subagent, routed through the claude-school account (`CLAUDE_CONFIG_DIR`
checked). Its prompt gave it the problem and the diff, not the author's conclusions. It was read-only on the
worktree, could run local Python, and wrote scratch files only under the scratchpad.
- **Its script** `k2.py` is copied here as `review_k2.py`. Its ROOT outputs were deleted after the review (182 MB).
- **What it reviewed** is the diff before one change. On its item 2, the author then moved the at-Write assertion after
  the key and content checks; see `A1-REPORT.md`.

Verbatim report:

---

Findings, most severe first. I found no correctness defect. Everything below is minor or a caveat.

**1. Does the fix give exactly one cycle of `data`? Yes for AutoSave, the cause on this input.**
- **Reproduced by running** (`a1/review/k2.py`, 3 branches D/D/B, 4,119,797 rows, ROOT 6.28/12):
  - Default settings give `[('data',3),('data',2)]`. Before the write, `autosave=1971554` and `autoflush=1971554`.
  - `SetAutoSave(0)` gives `[('data',1)]`. The 12,000,000-row run with `SetAutoSave(0)` also gives only `data;1`, at 201 MB uncompressed.
- **Mechanism (the run shows it; the rule itself is from memory).** The default is `-300000000` bytes. At the first AutoFlush (1.97M entries) ROOT converts it to an entry count. That fires autosaves at about 1.97M and 3.94M rows, then the final `Write` makes the third cycle.
- **File-size change-of-file (`fgMaxTreeSize`, 100 GB): from memory only.** It opens a new file and does not add keys to the same file. It is far above any size reachable here, and I did not run it.
- **AutoFlush: from memory, plus the 12M-row run.** It flushes baskets and writes no key. The 12M run had AutoFlush active and produced no extra key.
- **Not run:** I did not run the real writer at 4.1M rows (only a standalone equivalent), and I did not test beyond 12M rows.

**2. Do the tests force the failure and fail on the old code? Yes, with one asymmetry (`test_cov2d_writer.py:152`).**
- **Setup:** my scratch copy needs `PYTHONPATH` set to the `control1` directory. Without it, every control test fails with `ModuleNotFoundError`.
- **Old code (the single `SetAutoSave(0)` line deleted), run:** 2 failed, 10 passed.
  - `test_control_passes_when_autosave_would_fire` fails with `3 != 0 : tree data: entries CV=2345 UNI=2345 branches CV=3 UNI=3 shared=3`. This is a real keys failure at 2,345 rows.
  - `test_one_cycle_when_autosave_would_fire` fails with `Lists differ: [200] != [0]`. That is the guard assertion, which comes before the key assertion, so this test never reaches the key check on old code.
- **Fixed code:** 12 passed.
- **Vacuity:** neither test can pass vacuously. `built == [200]` fails if the factory was not used. For example, a switch to `from ROOT import TTree` would fail loudly. `at_write == [0]` fails if the writer did not turn AutoSave off.
- **Weakness, by reading:** `at_write` reads `GetAutoSave()` at `Write` time. A writer that calls `SetAutoSave(0)` only after the Fill loop would pass the guard. The key check would still catch that, because the factory's 200 entries fire during the loop.

**3. Is `ROOT.TTree` restored on every path? Yes, by reading.**
- **Restore:** the `finally` restores `ROOT.TTree = real`, and `real` is captured before the patch. If an exception occurs inside the `with`, the `finally` still runs.
- **Leak:** the test fixtures that build trees (`write_cv`) run in `setUp`, outside the patch. Nothing nests the context manager.
- **Residual:** setting `ROOT.TTree = real` turns the facade's lazy attribute into a plain stored attribute. It is the same class, so this is harmless.
- I did not run a test that raises inside the context.

**4. Do the two mutants each match once, and are they killed for the right reason? Yes, with one caveat.**
- **Matching:** I counted `"t.SetAutoSave(0)  # no intermediate cycles"` in the fixed writer. It occurs once. The harness also enforces `src.count(a) == 1` and prints NOMATCH otherwise.
- **"autosave left on" (line deleted), run:** killed by the two new tests. They fail on the keys and the guard respectively, as in item 2.
- **"autosave at ROOT's default" (`-300000000`), run:** 1 failed, 11 passed. Only the guard kills it, with `[-300000000] != [0]`.
  - **Why only the guard:** at 2,345 rows the default never autosaves, so the key checks pass. The test comment says this.
  - **Consequence:** this mutant is killed by the stated threshold and not by observed behaviour. That is a real limit of any small-fixture test, not a defect.
- **Harness:** it runs pytest with `-x`, so it reports only the return code, never which test killed the mutant.
- I did not run the harness itself, only the equivalent substitutions in a scratch copy.

**5. Anything else?**
- `cov2d_writer.py:9` and the test comment cite "control (2a) (addendum A1)". A grep of `2d-unfolding/cov2d` and `receipts-cov2d` for "addendum" and "(2a)" found no addendum A1 document. It may live elsewhere or in a later commit; I can't tell.
- The docstring is accurate, but it says AutoSave "left `data;2` and `data;3`". At least as reproduced, the cause is AutoSave firing after ROOT converts the default byte threshold to an entry count at the first AutoFlush, not something specific to this tree.
- The import of `contextlib` is already present in the test file (line 7), and `mock` is still used elsewhere. The style matches the surrounding code.
