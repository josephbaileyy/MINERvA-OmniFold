# b5d_build.py: tests, line trace and mutants (A1 and A2 package, tier3-design, 2026-11-24)

The checks are for:
- `nd-unfolding/b5d/b5d_build.py`, sha256 `69f11025c4bc0ad0288bb74641c0e76d0286fea1ba9c86531fc25cc7bb27f30d`;
- `test_b5d.py`, sha256 `2df87a4d08487c4b65eb2cc9fe74b5c906321674cae53a6674a260f5294ae857`.

**Tests:** 68 pass (`python3 -m pytest -q nd-unfolding/b5d/test_b5d.py`).

<!-- absence-ok: a coverage statement about two named lines of the code, not the absence of a result -->
**Line trace** (`line-trace.txt`, coverage.py 7.15.4): 99%. Two lines are not run:
- the `__main__` guard;
- the Linux `renameat2` branch of `rename_noreplace`. The build runs on macOS, which takes the `renamex_np` branch,
  and that branch is tested.

**Mutants** (`mutants.py`, output `mutants.txt`, one clean run): 73 of 73 killed.
- 18 are on the rev 1 method.
- The rest are on the A1 and A2 delta and the delta-recheck fixes:
  - the tie rule: COVFIX's relative null test, two passes, the span check, the sign;
  - per-ensemble f̂;
  - L on C_e's kept modes;
  - C-PSD (including C_e) and C-FIN;
  - C-LEAK as a dimensional check: the scaling of each absolute input (all of g), exact k² on the exempt matrices,
    and the shape, key, type and value comparisons;
  - the mean error's frame;
  - the cal arrays left unread;
  - the atomic no-replace writer, with a best-effort parent sync;
  - strict JSON and the matrix sha256;
  - main's STOP mapping and its verdict's band states;
  - the band traces;
  - A2's band states and stop rule;
  - the rank-0 null.
- One equivalent mutant is left out: narrowing B-SEL's `g` to Tune v1 alone before scaling. Only Tune v1's prediction
  reaches the record, so no test can see it. `scaled_predictions` itself is tested on every entry.
- Run it on a copy of `nd-unfolding/b5d/` in a scratch tree: `python3 mutants.py <tree>`.
