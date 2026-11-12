# COV2D-G2R amendment 1: test and mutation receipts (2026-11-11)

**From** a clean detached checkout of the code commit `2f6dac56a2382f9decf098eb309ed6683af0caed` (porcelain 0 before and
after), macOS, `/opt/homebrew/bin/python3.13` with ROOT 6.36.000 and numpy 2.4.4. No LightGBM here: the whole-driver
comparisons run in the cluster-environment test of the job addendum.

| file | what |
|---|---|
| `test_g2r.txt` | `test_g2r.py` at PYTHONHASHSEED 0, 1 and 2: 24 tests, OK each time |
| `test_re2_miss_map.txt` | `test_re2_miss_map.py`: 8 tests, OK, rc 0 |
| `g2r_mutation.txt` | `g2r_mutation.py`: both unmutated suites full (24, 8, none skipped), 15 mutations all killed, sources restored byte-identical to HEAD, rc 0 |

**MEASURES:** the tests and mutants on synthetic fixtures. **CANNOT AUTHORIZE:** any job.

These supersede the first receipts, made at `0f57c22a` (23, 7, 13), before the director's two conditions on §2.
