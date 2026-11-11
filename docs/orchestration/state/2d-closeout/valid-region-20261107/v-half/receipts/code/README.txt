V-HALF code receipts (DECLARATION.md section 8.1). Run locally on the lane's machine, at 0 node-h, with no cluster
contact and no input read: the tests use synthetic fixtures, and the read refuses before it opens H1 or H2.

MADE AT: commit 10f33bcc48dee4b692c9af7e733c3463296d6168 (the V-HALF declaration and code commit), in a clean clone of
it. The clone showed 0 porcelain lines before and after every run. The commit that adds this README changes only this
directory's files and MANIFEST.tsv. Every run is one serial process, under nice -n 19, with every BLAS/OpenMP thread
cap at 1. Each log's header carries the clone's HEAD and the sha256 of v_half.py, test_v_half.py, mutate_v_half.py,
INPUTS.sha256 and mutants.txt, which are section 8.1's digests.

tests.txt     python3 -B -m unittest -v test_v_half: 33 run, OK, rc 0. Among them is the REQUIRED
              test_the_two_forms_agree.
mutation.txt  python3 -B mutate_v_half.py, its output written outside the clone. The baseline was 33 run, OK. All 36
              mutants were killed, with "survivors []" and the target's sha256 restored to ce07a6f0... after the run,
              rc 0. The output is byte-identical to the committed mutants.txt.
refusal.txt   v_half.py read on the clone, which has no PRR-READOUT.sha256: "REFUSED: no pin file ...", rc 4, and the
              output directory was not created.

CITABLE FOR: that the listed tests passed, the listed mutants were killed, and the read refused, on the listed files at
the commit named above. NOT CITABLE FOR: any V-HALF d, b, margin or class; FD-PRR's readout, which does not exist yet;
anything about H1's values.
