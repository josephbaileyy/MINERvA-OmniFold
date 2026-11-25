# b5d_build.py: tests, line trace and mutants (A1 and A2 package, tier3-design, 2026-11-24)

The checks are for:
- `nd-unfolding/b5d/b5d_build.py`, sha256 `dd786b523f4af3c287436b68c92509f3f82a62e05d0558ca1095de71912d2f8a`;
- `test_b5d.py`, sha256 `0c137cf0558cb839598f34aaf4aaf82332cc3ea21dc33ed4bfed02bb5ddb3c81`.

**Tests:** 64 pass (`python3 -m pytest -q nd-unfolding/b5d/test_b5d.py`).

<!-- absence-ok: a coverage statement about two named lines of the code, not the absence of a result -->
**Line trace** (`line-trace.txt`, coverage.py 7.15.4): 99%. Two lines are not run:
- the `__main__` guard;
- the Linux `renameat2` branch of `rename_noreplace`. The build runs on macOS, which takes the `renamex_np` branch,
  and that branch is tested.

**Mutants** (`mutants.py`, output `mutants.txt`, one clean run): 62 of 62 killed.
- 18 are on the rev 1 method.
- The rest are on the A1 and A2 delta and the delta-recheck fixes:
  - the tie rule: COVFIX's relative null test, two passes, the span check, the sign;
  - per-ensemble f̂;
  - L on C_e's kept modes;
  - C-PSD and C-FIN;
  - C-LEAK as a dimensional check: the scaling of each absolute input, exact k² on the exempt matrices, and the shape,
    key and value comparisons;
  - the mean error's frame;
  - the cal arrays left unread;
  - the atomic no-replace writer;
  - strict JSON and the matrix sha256;
  - main's STOP mapping;
  - the band traces;
  - A2's band states and stop rule;
  - the rank-0 null.
- Run it on a copy of `nd-unfolding/b5d/` in a scratch tree: `python3 mutants.py <tree>`.
