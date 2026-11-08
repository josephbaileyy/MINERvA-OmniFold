# LL5D A1a receipts: tests and mutation check

**Made at** `6a9558ff8f58768c812c1b246ebe4452dcab0e1a` (branch `amend/ll5d-a1a-20261108`), from a clean detached
checkout of that commit (`git worktree add --detach`; porcelain 0 before and after). So every tracked file, the PR's
own included, was in scope of the seed-collision check. Each receipt's header repeats the commit and the file digests.

| receipt | what | result |
|---|---|---|
| `tests-numpy126-seed0.txt`, `-seed1.txt`, `-seed2.txt` | `test_ll5d.py -v` at PYTHONHASHSEED 0, 1, 2; Python 3.12.2, numpy 1.26.4 | 69 tests, OK |
| `tests-numpy2-seed0.txt` | the same at PYTHONHASHSEED 0; Python 3.13.7, numpy 2.4.4 | 69 tests, OK |
| `mutation.txt` | `ll5d_a1a_mutation.py`: the unmutated control, then 47 mutations of `ll5d.py` | control PASS (69 tests); 47 killed; ALL-KILLED, rc 0 |

**Superseded, both in git history:**
- the receipts committed at `6da967b0`, made at `43b73ffa`, before the gate wrote section 5.3's sealed clip-prep
  products;
- those at `73684077`, made on base `1acdee66` before these files were tracked. At that head the seed-collision test
  failed on the PR's own files, so its unmutated control failed (coverage-5b-audit's NO-GO C1 on #945).

The commit that adds these receipts changes no code or test file. `ll5d.py` is `9dbf9cf4…` in every receipt.
