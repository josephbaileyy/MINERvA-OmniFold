# LL5D amendment A1b.1: the receipts (2026-11-10)

**By** the `cov2d` session. Every file here was made at the code commit `dd90a0d702e0016f9a45b523f88dd899eb3ec4ae`, from a clean detached checkout of
it (porcelain 0 before and after). Each file's header names the interpreter, numpy, PYTHONHASHSEED and the sha256 of
`ll5d_ctl.py`, its tests, its mutation check, and the unchanged `ll5d_b.py` and `ll5d.py`.

| file | what | result |
|---|---|---|
| `test_ll5d_ctl-numpy126-seed0.txt`, `…seed1.txt`, `…seed2.txt` | `test_ll5d_ctl.py`, python 3.12.2, numpy 1.26.4 | 16 tests, OK, rc 0 at each seed |
| `test_ll5d_ctl-numpy2-seed0.txt` | the same under python 3.13, numpy 2.4.4 | 16 tests, OK, rc 0 |
| `mutation-a1b1.txt` | `ll5d_a1b1_mutation.py` | the unmutated suite runs 16 tests, none skipped, rc 0; 12 of 12 mutations killed; `ALL-KILLED`, rc 0 |
| `test_ll5d-numpy126-seed0-with-a1b1.txt` | A1a's suite with `ll5d_ctl.py` tracked | 82 tests, OK, rc 0 |
| `test_ll5d_b-numpy126-seed0-with-a1b1.txt` | A1b's suite with `ll5d_ctl.py` tracked | 29 tests, OK, rc 0 |

These are tests on synthetic fixtures and on the committed reference files. Nothing ran on the cluster.
