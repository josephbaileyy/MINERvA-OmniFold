FD-PRR rev 2 receipts (FD-PRR-DECLARATION.md section 8.2). Local, on the lane's machine, at 0 node-h, with no cluster
contact. Every run is one serial process with every BLAS/OpenMP thread cap at 1. Each log's header carries the sha256
of the six FD-PRR files it ran.

tests-serial.txt     every class but JobScript (selected by the test loader; no test edited): 103 collected, 94 run, OK,
                     rc 0.
tests-jobscript.txt  the JobScript class alone, run after the first had ended: 9 run, OK, rc 0. Its script starts 8
                     gate processes at once by design. The director held it while Codex2's #848 verification loaded
                     the machine, then cleared it on 2026-11-08.

HELD, at the director's request: the mutation run (prr_mutation.py, 62 mutants), until Codex2's #848 run has finished.
Its receipt is added here, on the same PR. A first mutation run at 4 mutants at once was stopped at the director's
request before it reported anything. It is not a receipt.

CITABLE FOR: that the listed tests passed on the listed files. NOT CITABLE FOR: the mutation check, or anything about
the cluster run.
