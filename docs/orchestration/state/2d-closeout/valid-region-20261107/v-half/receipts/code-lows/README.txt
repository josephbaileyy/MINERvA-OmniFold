V-HALF follow-up receipts (DECLARATION.md section 8.2): coverage-5b-audit's four lows on #992, closed before the
binding. Run locally on the lane's machine, at 0 node-h, with no cluster contact and no input read: the tests use
synthetic fixtures, and the read refuses before it opens H1 or H2.

MADE AT: commit b4e6d11881822b9ae1d72df5531064ec873c7e12 (the follow-up's code commit), in a clean clone of it. The
clone showed 0 porcelain lines before and after every run. The commit that adds this README changes only this
directory's files and MANIFEST.tsv. Every run is one serial process, under nice -n 19, with every BLAS/OpenMP thread cap
at 1. Each log's header carries the clone's HEAD and the sha256 of v_half.py (8a1cdbe7...), test_v_half.py
(d2d28b9f...), mutate_v_half.py (09a10bc7...), INPUTS.sha256 and mutants.txt, which are section 8.2's digests.

tests.txt               python3 -B -m unittest -v test_v_half: 37 run, OK, rc 0. Among them are the four new tests
                        and the REQUIRED test_the_two_forms_agree.
mutation.txt            python3 -B mutate_v_half.py, its output written outside the clone. The baseline was 37 run,
                        OK. All 41 mutants were killed ("survivors []"), the target's sha256 was restored to
                        8a1cdbe7... after the run, and rc was 0. The output is byte-identical to the committed
                        mutants.txt.
refusal.txt             v_half.py read on the clone, which has no PRR-READOUT.sha256: "REFUSED: no pin file ...",
                        rc 4, and the output directory was not created.
tests-at-ce07a6f0.txt   this commit's test_v_half.py against v_half.py at main cd8e16fe (sha256 ce07a6f0..., the code
                        #992 merged), in a separate directory: 37 run, FAILED (failures=2), rc 1. The two failures are
                        exactly the (b) and (d) tests, test_the_licence_is_section_10_in_full and
                        test_c_prr_refuses_an_h2_entry_not_sixteen_long. The (a) and (c) tests pass there, because
                        their code was already right.

CITABLE FOR: that the listed tests passed, the listed mutants were killed, and the read refused, on the listed files at
the commit named above; that only the (b) and (d) tests fail against ce07a6f0. NOT CITABLE FOR: any V-HALF d, b, margin
or class; FD-PRR's readout, which does not exist yet; anything about H1's values.
