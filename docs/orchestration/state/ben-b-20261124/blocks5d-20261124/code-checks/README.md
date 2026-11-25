# b5d_build.py: tests, line trace and mutants (A1 and A2 package, tier3-design, 2026-11-24)

The checks are for:
- `nd-unfolding/b5d/b5d_build.py`, sha256 `4d21c21f8a6e4ab514a89667b3cab4a23b279a03c0c713eb010c4cc41fc7055c`;
- `test_b5d.py`, sha256 `744cc77218082147ed312969361500dd66d397bf9972594ff0b1148a576a6871`.

**Tests:** 64 pass (`python3 -m pytest -q nd-unfolding/b5d/test_b5d.py`). They include a dimensional-invariance test:
scaling every absolute input by k leaves every non-exempt number unchanged and scales C_b,abs and V_F by k².

**Line trace** (`line-trace.txt`, coverage.py 7.15.4): 99%. The only line not run is the `__main__` guard.

**Mutants** (`mutants.py`, output `mutants.txt`, one clean run): 58 of 58 killed.
- 18 are on the rev 1 method. "phi below 1 allowed" was re-anchored to A2's trigger line.
- 40 are on the A1 and A2 delta and the delta-recheck fixes:
  - the tie rule: COVFIX's relative null test, two passes, the span check, the sign;
  - per-ensemble f̂;
  - L on C_e's kept modes;
  - C-PSD and C-FIN;
  - C-LEAK, with vectors per entry and matrices by their largest entry;
  - the mean error's frame;
  - the cal arrays left unread;
  - the exclusive writer;
  - strict JSON and the matrix sha256;
  - main's STOP mapping;
  - the band traces;
  - A2's band states and stop rule;
  - the rank-0 null.
- Run it on a copy of `nd-unfolding/b5d/` in a scratch tree: `python3 mutants.py <tree>`.
