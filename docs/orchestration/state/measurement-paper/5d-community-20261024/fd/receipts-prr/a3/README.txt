FD-PRR addendum A3 receipts (FD-PRR-ADDENDUM-A3.md section 7). Run locally on the lane's machine, at 0 node-h, with
no cluster contact.

MADE AT: commit 9de365e7022969b61607723b1136c666fe73dabe (the A3 code commit), in a clean clone of it, which showed
0 porcelain lines before and after every run. The commit that adds this README changes only this directory's files,
the CATALOG row and MANIFEST.tsv. Nothing under nd-unfolding changes, so the six FD-PRR files are the same at both
commits. Every run is one serial process, under nice -n 19, with every BLAS/OpenMP thread cap at 1. Each log's header
carries the clone's HEAD and the six files' sha256, which are the addendum's section 6 digests.

tests-serial.txt     every test class but JobScript (selected by the test loader): 109 collected, 94 run, OK, rc 0.
tests-jobscript.txt  the JobScript class alone, run after the first had ended: 15 run, OK, rc 0. Among them are the
                     REQUIRED test_a_sub_hour_limit_in_squeues_m_ss_form_is_read and
                     test_an_unreadable_limit_is_refused_as_unreadable_not_as_exceeding.
tests-at-MA1.txt     the same JobScript class with PRR_SBATCH set to M_A1's sbatch_prr.sh. That file was copied out of
                     a clean clone at 6727020a7c58b00dd00806151c627c8a24f72402 (0 porcelain lines), and its sha256,
                     10290087cdd57d972a4df5289f1910161373e8def3f44c15ba0682f9d14a0b85, is in the command line. The
                     header's sha256 list is the A3 clone's six files; only sbatch_prr.sh was swapped, through
                     PRR_SBATCH. Result: 15 run, FAILED (failures=5), rc 1. The five failures are exactly the five new
                     tests, and the ten existing JobScript tests pass. So the new tests fail at M_A1 and pass at A3.
mutation.txt         2026-11-09 14:22-15:18Z. The unmutated suite passed with 109 tests in the mirrored tree. Then 70 of
                     70 mutants were killed, each by its named test, MUTATION CHECK :: PASS, rc 0. Among them:
                     - "two fields read as H:M" (REQUIRED), killed by the sub-hour test;
                     - "a parse error reported as exceeds" (REQUIRED), killed by the unreadable test;
                     - the five other new mutants and the re-anchored "TimeLimit unchecked".

CITABLE FOR: that the listed tests passed, and the listed mutants were killed, on the listed files at the commit named
above; that the five new tests fail against M_A1's sbatch_prr.sh. NOT CITABLE FOR: the cluster's squeue output on a
real job, which attempt 2 meets first; anything about LightGBM, the real inputs or route 2; the A2 union (110 tests,
71 mutants), which is rerun at whichever PR merges second.
