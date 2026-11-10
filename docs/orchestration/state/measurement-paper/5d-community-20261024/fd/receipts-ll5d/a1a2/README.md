# LL5D A1a.2 receipts: both suites, both mutation checks, and the REQUIRED test against a95cc39f

**Made at** `9d906bf40994e9814ee63a2386e7fd7e14da5b4e` (branch `amend/ll5d-a1a2-20261110`, the amendment's code commit), from a clean detached checkout of
that commit, porcelain 0 before and after. Each receipt's header repeats the commit, the interpreter and numpy, and the
file digests.

| receipt | result |
|---|---|
| `test_ll5d-numpy126-seed0.txt` | Ran 82 tests in 61.755s; OK; # rc=0 |
| `test_ll5d-numpy126-seed1.txt` | Ran 82 tests in 53.976s; OK; # rc=0 |
| `test_ll5d-numpy126-seed2.txt` | Ran 82 tests in 51.220s; OK; # rc=0 |
| `test_ll5d-numpy2-seed0.txt` | Ran 82 tests in 43.689s; OK; # rc=0 |
| `test_ll5d_b-numpy126-seed0.txt` | Ran 29 tests in 20.076s; OK; # rc=0 |
| `test_ll5d_b-numpy126-seed1.txt` | Ran 29 tests in 23.785s; OK; # rc=0 |
| `test_ll5d_b-numpy126-seed2.txt` | Ran 29 tests in 22.323s; OK; # rc=0 |
| `test_ll5d_b-numpy2-seed0.txt` | Ran 29 tests in 20.004s; OK; # rc=0 |
| `ll5d_a1a_mutation.txt` | UNMUTATED PASS tests=82 expected=82 rc=0; ALL-KILLED; # rc=0; 58 mutants, all killed (8 of them A1a.2's) |
| `ll5d_a1b_mutation.txt` | UNMUTATED PASS tests=29 expected=29 skipped=False rc=0; ALL-KILLED; # rc=0; 27 mutants, all killed |
| `required-test-at-a95cc39f.txt` | `MatchedRows.test_vi_finds_every_matched_row_and_the_read_is_not_forced`, with a95cc39f's `ll5d.py` (sha256 `b49f5d5f…`) first on `sys.path`: Ran 1 test in 4.752s; FAILED (failures=1); # rc=1, `AssertionError: Tuples differ: (2980, 2980) != (0, 0)`. **This failure is expected:** it is the test failing on the code that ran the gates. |

- **numpy 1.26** is miniconda's Python 3.12.2 with numpy 1.26.4. **numpy 2** is Homebrew's Python 3.13.7 with numpy 2.4.4.
- **The scripts:**
  - `mk-suites.sh` made the eight suite receipts, running each test file directly from `tests/`.
  - `mk-mutation-and-required.sh` made the two mutation receipts and the a95cc39f run.
- **Disclosure: a first attempt was discarded.** `mk-mutation-and-required.sh` also first ran the suites with
  `python -m unittest tests.<module>`. Under the miniconda interpreter that form did not import the module
  (`ModuleNotFoundError: No module named 'tests.test_ll5d'`), so no test ran. Those six numpy 1.26 outputs were
  discarded, not committed, and the suites were remade with `mk-suites.sh` from the same checkout.
- **The mutation checks run the full suite under numpy 1.26 as their control,** by `runpy`, which imports correctly.
- **This commit changes no code or test file.**
