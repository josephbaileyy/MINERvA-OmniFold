# LL5D A1a.1 receipts: both suites and both mutation checks

**Made at** `eeed15993831f4f2b352595b98842ed05f62097c` (branch `amend/ll5d-a1a1-20261109`), from a clean detached checkout of that commit (porcelain 0
before and after). Each receipt's header repeats the commit and the file digests.

| receipt | result |
|---|---|
| `test_ll5d-numpy126-seed{0,1,2}.txt`, `test_ll5d-numpy2-seed0.txt` | 72 tests, OK, at each (numpy 1.26.4; 2.4.4) |
| `test_ll5d_b-numpy126-seed{0,1,2}.txt`, `test_ll5d_b-numpy2-seed0.txt` | 29 tests, OK, at each |
| `ll5d_a1a_mutation.txt` | control PASS (72 tests); 50 mutants, all killed; rc 0 |
| `ll5d_a1b_mutation.txt` | control PASS (29 tests, none skipped); 27 mutants, all killed; rc 0 |

No receipt carries a seed value. The commit that adds these changes no code or test file.
