FD-PRR addendum A2 receipts (FD-PRR-ADDENDUM-A2.md section 5). Made locally, on the lane's machine, at 0 node-h,
with no cluster contact.

MADE AT: commit db0e801f1fc4a928deaa3331d438758dac29837c, the A2 code commit, in a clean clone of it. The clone showed 0
porcelain lines (--ignored) before and after every run. The fixture comparison also used a clean clone at M_A1,
6727020a7c58b00dd00806151c627c8a24f72402, which showed 0 lines before and after.

The commit that adds this README changes only three things: this directory's receipt files, the CATALOG row and
MANIFEST.tsv. Nothing under nd-unfolding changes, so the six FD-PRR files are the same at both commits.

Every run is one serial process, under nice -n 19, with every BLAS/OpenMP thread cap at 1. Each log's header carries
the clone's HEAD and the six files' sha256, which are the addendum's section 4 digests.

tests-serial.txt
  every test class but JobScript, selected by the test loader: 105 collected, 95 run, OK, rc 0.
  Among them is the REQUIRED test_the_table_carries_each_truths_departure_d.

tests-jobscript.txt
  the JobScript class alone, run after the first had ended: 10 run, OK, rc 0.

fixture-comparison.txt
  prr_read.main on test_planted_classes' fixture, at M_A1 and at A2, with PYTHONHASHSEED=0, via fixture_read.py.
  Then compare.py:
  - readout.txt: 32,707 bytes, identical;
  - M_A1's readout.json: no "d" key;
  - A2's readout.json: 181 table entries, each with a 16-value d, and no "d" key anywhere else;
  - A2's readout.json with each table entry's "d" deleted: 252,119 bytes, byte-identical to M_A1's.
  A2 FIXTURE COMPARISON :: PASS, rc 0.

mutation.txt
  2026-11-09T07:27:27Z to 2026-11-09T08:01:37Z: the unmutated suite passed with 105 tests in the mirrored tree, then 64 of
  64 mutants were killed, each by its named test, among them the REQUIRED "d over the truth, not the prior".
  MUTATION CHECK :: PASS, rc 0.

CITABLE FOR: that the listed tests passed, the listed mutants were killed and the fixture outputs compare as stated,
on the listed files at the commits named above.
NOT CITABLE FOR: anything about the cluster products, any d on real inputs, or any V-HALF class.
