FD-PRR addendum A3 receipts for the union with A2 (FD-PRR-ADDENDUM-A3.md sections 5 and 7). A2 merged first. This PR
merged main into its branch, and under the director's ruling the second PR to merge reruns its suite and mutants at its
new head. Run locally on the lane's machine, at 0 node-h, with no cluster contact.

MADE AT: commit 08848a768b684164ebde74a7cd24fac4369cf8e9, the merge of main at cf76aec7 (M_A2) into A3. Its parents are
a310064a (A3's receipts commit) and cf76aec7. The runs were made in a clean clone of it, which showed 0 porcelain lines
before and after every run. The commit that adds this README changes only:
- this directory's files;
- FD-PRR-ADDENDUM-A3.md (sections 5, 6 and 7 record the union);
- the CATALOG row;
- MANIFEST.tsv.
Nothing under nd-unfolding changes, so the six FD-PRR files are the same at both commits. Every run is one serial
process, under nice -n 19, with every BLAS/OpenMP thread cap at 1. Each log's header carries the clone's HEAD and the
six files' sha256. These are the union's digests in section 6:
- sbatch_prr.sh 4493aad5…, as at 9de365e7;
- prr_read.py d7c7c2c0…, A2's;
- test_prr.py c600e4b1…;
- prr_mutation.py dfa99466….

tests-serial.txt     every test class but JobScript (selected by the test loader): 110 collected, 95 run, OK, rc 0. A2's
                     REQUIRED test_the_table_carries_each_truths_departure_d is among them.
tests-jobscript.txt  the JobScript class alone, run after the first had ended: 15 run, OK, rc 0, with A3's two REQUIRED
                     tests among them.
tests-at-MA1.txt     the same JobScript class with PRR_SBATCH set to M_A1's sbatch_prr.sh. That file was copied out of a
                     clean clone at 6727020a7c58b00dd00806151c627c8a24f72402; its sha256, 10290087…, is in the command
                     line. The header's sha256 list is the union clone's six files; only sbatch_prr.sh was swapped.
                     Result: 15 run, FAILED (failures=5), rc 1. The five failures are exactly A3's five tests, and the
                     ten others pass.
mutation.txt         2026-11-09 15:52-16:44Z. The unmutated suite passed with 110 tests in the mirrored tree. Then 71 of
                     71 mutants were killed, each by its named test, MUTATION CHECK :: PASS, rc 0. Among them:
                     - A2's REQUIRED "d over the truth, not the prior";
                     - A3's REQUIRED "two fields read as H:M" and "a parse error reported as exceeds".

CITABLE FOR: that the listed tests passed, and the listed mutants were killed, on the listed files at the merge commit
named above; that A3's five tests fail against M_A1's sbatch_prr.sh there. NOT CITABLE FOR: the cluster's squeue output
on a real job, which attempt 2 meets first; anything about LightGBM, the real inputs, route 2 or the PRR read.
