FD-PRR addendum A1 receipts (FD-PRR-ADDENDUM-A1.md section 5). Local, on the lane's machine, at 0 node-h, with no
cluster contact.

MADE AT: commit b2cbaab89e294184ba214fb518d90aa337a161b4 (the A1 code commit), in a clean clone of it, which showed
0 porcelain lines before and after every run. The commit that adds this README changes only this directory's files,
the CATALOG row and MANIFEST.tsv. Nothing under nd-unfolding changes, so the six FD-PRR files are the same at both
commits. Every run is one serial process, under nice -n 19, with every BLAS/OpenMP thread cap at 1. Each log's header
carries the clone's HEAD and the six files' sha256, which are the addendum's section 4 digests.

tests-serial.txt     every test class but JobScript (selected by the test loader): 104 collected, 94 run, OK, rc 0.
tests-jobscript.txt  the JobScript class alone, run after the first had ended: 10 run, OK, rc 0. Among them is the
                     REQUIRED test_every_python3_call_runs_after_the_environment_is_sourced.
mutation.txt         2026-11-09 00:02-00:53Z: the unmutated suite passed with 104 tests in the mirrored tree, then 63 of
                     63 mutants were killed, each by its named test, the REQUIRED "limit above the source" among them.
                     MUTATION CHECK :: PASS, rc 0.

CITABLE FOR: that the listed tests passed, and the listed mutants were killed, on the listed files at the commit named
above. NOT CITABLE FOR: anything about the cluster run, LightGBM, the real inputs, squeue or O_NOATIME, which the dry
run meets first.
