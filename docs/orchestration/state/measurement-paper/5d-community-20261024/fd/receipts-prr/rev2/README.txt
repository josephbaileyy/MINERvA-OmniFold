FD-PRR rev 2 receipts (FD-PRR-DECLARATION.md section 8.2). Local, on the lane's machine, at 0 node-h, with no cluster
contact.

tests-serial.txt   the test suite at this commit, one serial process, every BLAS/OpenMP thread cap 1: 102 collected,
                   the 8 JobScript tests held (selected out by the loader; no test edited), 94 run, OK, rc 0. The
                   log's header carries the sha256 of the six FD-PRR files it ran.

HELD, at the director's request of 2026-11-08 (the shared machine's load during Codex2's #848 verification):
- the JobScript class (sbatch_prr.sh starts 8 gate processes at once by design);
- the mutation run (prr_mutation.py, 60 mutants).
Both run serially when the director clears the machine. Their receipts are added here, on the same PR, before the
audit reads it. A first mutation run at 4 mutants at once was stopped at the director's request before it reported
anything. It is not a receipt.

CITABLE FOR: that the listed tests passed on the listed files. NOT CITABLE FOR: the held tests, the mutation check,
or anything about the cluster run.
