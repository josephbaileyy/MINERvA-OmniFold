FD-PRR rev 2 receipts (FD-PRR-DECLARATION.md section 8.2). Local, on the lane's machine, at 0 node-h, with no cluster
contact.

MADE AT: commit 0478e727b8f196b88e75c808487c50f8035ad047 (the code commit), in a clean clone of it, which showed 0
porcelain lines before and after every run. The commit that adds this README changes only this directory's files,
the CATALOG row and MANIFEST.tsv. Nothing under nd-unfolding changes, so the six FD-PRR files are the same at both
commits. Every run is one serial process, under nice -n 19,
with every BLAS/OpenMP thread cap at 1. Each log's header carries the clone's HEAD and the six files' sha256, which are
the declaration's section 8.1 digests.

tests-serial.txt        every test class but JobScript (selected by the test loader): 103 collected, 94 run, OK, rc 0.
tests-jobscript.txt     the JobScript class alone, run after the first had ended: 9 run, OK, rc 0. Its script starts 8
                        gate processes at once by design.
mutation.txt            run 2 (2026-11-08 19:09-19:59Z): the unmutated suite passed with 103 tests in the mirrored
                        tree, then 62 of 62 mutants were killed, each by its named test. MUTATION CHECK :: PASS, rc 0.
mutation-run1-fail.txt  run 1, at the earlier test file (test_prr.py sha256 2a990367...): 59 of 62 killed, FAIL. Its
                        three survivors were tests that did not isolate their check. Three assertions were added to
                        test_prr.py before run 2, and no checked code changed. Kept as a receipt (the director).

CITABLE FOR: that the listed tests passed, and the listed mutants were killed, on the listed files at the commit named
above. NOT CITABLE FOR: anything about the cluster run, LightGBM, the real inputs, squeue or O_NOATIME, which the dry
run meets first.
