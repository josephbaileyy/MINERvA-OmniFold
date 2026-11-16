# COV2D-G2R amendment 1: test, mutation and coverage receipts (2026-11-12)

**From** a clean detached checkout of the code commit `62864b1641a580c52b2918babc0926e468925dad` (porcelain 0 before and
after), macOS, `/opt/homebrew/bin/python3.13` with ROOT 6.36.000 and numpy 2.4.4. No LightGBM here: main() is run
through a stub OmniFold helper (MainWithMissMap); the trained whole-driver comparison is the cluster-environment test's.

| file | what |
|---|---|
| `test_g2r.txt` | `test_g2r.py` at PYTHONHASHSEED 0, 1 and 2: 27 tests, OK each time |
| `test_re2_miss_map.txt` | `test_re2_miss_map.py`: 11 tests, OK, rc 0 |
| `test_g2r_glue.txt` | `test_g2r_glue.py`: 18 tests, OK, rc 0 (phase_tune on the committed AR23 inputs included) |
| `g2r_mutation.txt` | `g2r_mutation.py`: the three unmutated suites full (27, 11, 18, none skipped), 23 mutations all killed, sources restored byte-identical to HEAD, rc 0 |
| `coverage_sweep.txt` | the director's sweep: every executable line of g2r.py, g2r_prepare.py, g2r_readout.py and the G2R lines of re2_driver.py never executed by the three suites (6 left; the amendment's §2a says why each) |
| `coverage_tracer_usercustomize.py`, `coverage_uncovered.py` | the sweep's line tracer (loaded through usercustomize so it follows subprocesses) and its reader |

The sweep was run on the code worktree at the same content as `62864b16` (its three suites rc 0).

These supersede the receipts at `0f57c22a` (23, 7, 13) and `2f6dac56` (24, 8, 15).

**MEASURES:** the tests, mutants and line coverage on synthetic fixtures and on the committed AR23 records. **CANNOT
AUTHORIZE:** any job.
