# b5d_build.py: tests, line trace and mutants (A1 package, tier3-design, 2026-11-24)

The checks are for:
- `nd-unfolding/b5d/b5d_build.py`, sha256 `f6af9c024b086745e6054e27313c8750d71db15f06060889bbe65073f2127fa1`;
- `test_b5d.py`, sha256 `b0bcc62038545cd2abbdb4d20a1c2a562353fe3551963475c3126a86d679af6b`.

**Tests:** 58 pass (`python3 -m pytest -q nd-unfolding/b5d/test_b5d.py`).

**Line trace** (`line-trace.txt`, coverage.py 7.15.4): 99%. The only line not run is the `__main__` guard.

**Mutants** (`mutants.py`, output `mutants.txt`): 49 of 49 killed.
- The first 18 are on the rev 1 method.
- The other 31 are on the A1 delta and the delta-recheck fixes:
  - the tie rule, with its sign and threshold;
  - per-ensemble f̂;
  - L on C_e's kept modes;
  - C-PSD, C-FIN and C-LEAK;
  - the mean error's frame;
  - the cal arrays left unread;
  - the record formed whole, its matrix sha256 and strict JSON;
  - main's STOP mapping;
  - the band traces;
  - the rank-0 null.
- Run it on a copy of `nd-unfolding/b5d/` in a scratch tree: `python3 mutants.py <tree>`.
