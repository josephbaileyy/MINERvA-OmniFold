# LL5D A1a receipts: tests and mutation check

**Made at** `43b73ffa2224d1ce8e2fc9654fa94498cfbab01f` (branch `amend/ll5d-a1a-20261108`), from a clean detached
checkout of that commit (`git worktree add --detach`; porcelain 0 before and after). So every tracked file, the PR's
own included, was in scope of the seed-collision check. Each receipt's header repeats the commit and the file digests.

| receipt | what | result |
|---|---|---|
| `tests-numpy126-seed0.txt`, `-seed1.txt`, `-seed2.txt` | `test_ll5d.py -v` at PYTHONHASHSEED 0, 1, 2; Python 3.12.2, numpy 1.26.4 | 67 tests, OK |
| `tests-numpy2-seed0.txt` | the same at PYTHONHASHSEED 0; Python 3.13.7, numpy 2.4.4 | 67 tests, OK |
| `mutation.txt` | `ll5d_a1a_mutation.py`: the unmutated control, then 45 mutations of `ll5d.py` | control PASS (67 tests); 45 killed; ALL-KILLED, rc 0 |

**Superseded:** the receipts committed at `73684077` were made on base `1acdee66`, before these files were tracked. At
that head the seed-collision test failed on the PR's own files, so its unmutated control failed (coverage-5b-audit's
NO-GO C1 on #945). Those files are in git history at `73684077`.

The commit that adds these receipts changes no code or test file. `ll5d.py` is `b7674f67…` in every receipt.
