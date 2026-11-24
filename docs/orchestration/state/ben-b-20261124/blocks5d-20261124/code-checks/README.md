# b5d_build.py: tests, line trace and mutants (A1 package, tier3-design, 2026-11-24)

The checks are for `nd-unfolding/b5d/b5d_build.py` sha256 `24621550f23feb0930e8b53e3ab2efaf0dd910c122be53eaf8a5e8abc692bfe4` and `test_b5d.py` sha256
`2483fe3a73153bc2e5211fcdaa061e5659771177df6caed5b0b0dde1205b6d6f`.

- **Tests:** 50 pass (`python3 -m pytest -q nd-unfolding/b5d/test_b5d.py`).
- **Line trace** (`line-trace.txt`, coverage.py 7.15.4): 99%. The only line not run is the `__main__` guard.
- **Mutants** (`mutants.py`, output `mutants.txt`): 36 of 36 killed.
  - 18 are on the rev 1 method.
  - 18 are on this delta: the tie rule, per-ensemble f̂, L on C_e's kept modes, C-PSD, C-FIN, the mean error's frame,
    C-LEAK, the matrix sha256, strict JSON, main's STOP mapping, and the rank-0 null.
  - It runs on a copy of `nd-unfolding/b5d/` in a scratch tree: `python3 mutants.py <tree>`.
