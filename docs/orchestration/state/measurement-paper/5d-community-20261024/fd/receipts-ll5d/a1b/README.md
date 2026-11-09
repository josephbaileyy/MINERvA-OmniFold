# LL5D A1b receipts: tests and mutation check

**Made at** `cfe67afb280ef162f412a0747dd9b0eaaa2731f0` (branch `amend/ll5d-a1b-20261108`), from a clean detached checkout of that commit (porcelain 0
before and after), so every tracked file was in scope. Each receipt's header repeats the commit and the file digests.

| receipt | what | result |
|---|---|---|
| `tests-b-numpy126-seed0.txt`, `-seed1.txt`, `-seed2.txt` | `test_ll5d_b.py -v` at PYTHONHASHSEED 0, 1, 2; Python 3.12.2, numpy 1.26.4 | 28 tests, OK |
| `tests-b-numpy2-seed0.txt` | the same at PYTHONHASHSEED 0; Python 3.13.7, numpy 2.4.4 | 28 tests, OK |
| `tests-a1a-with-a1b.txt` | A1a's `test_ll5d.py` with A1b's files tracked (its seed-collision test included) | 69 tests, OK |
| `mutation-b.txt` | `ll5d_a1b_mutation.py`: the unmutated control, then 26 mutations of `ll5d_b.py` | control PASS (28 tests, none skipped); 26 killed; ALL-KILLED, rc 0 |

The commit that adds these receipts changes no code or test file. `ll5d_b.py` is `24312ca8…` and `ll5d.py`
`9dbf9cf4…` in every receipt.
