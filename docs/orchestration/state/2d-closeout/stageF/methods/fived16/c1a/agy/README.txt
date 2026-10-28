Step (c), 1A half: agy (gemini-3.8-flash-high via run_x.sh) checking the 1A sentences against the F1 study's facts.
BEFORE (make_pairs.py) is generated from fd_f1_readout.json and quoted from FD-F1-REPORT.md, with a NOT CITABLE FOR
list: coverage or width validated; a test of the detector response; the two truths as independent tests. It excuses
nothing (the b2 lesson). Q1 = Sec. I (L1), Q2 = paper abstract (A1), Q3 = note abstract (A2), Q4 = IV H (H1),
Q5 = note sec:fived16-fd (H2). Each pass has a control copy that plants four strengthenings: L1 "confirms the width";
A1 drops "GENIE v3"; H1 "two independent tests"; H2 "1 of 4 records with p<0.01". Q3 is left unplanted, as a check.

pass 1 (pairs*.txt; prd-read/r5/input.txt, the first drafts):
  control: 4 of 4 caught; Q3 SAME.
  real: Q1, Q4, Q5 SAME. Q2 and Q3 DIFFERS: without "cannot test the width" the abstracts could read as validating the
  intervals. Fixed: both abstracts add L1's "but does not test interval widths". Q3's second point ("the result's
  intervals") is the base wording, and it is right: the coverage not validated is the result's. Declined.
pass 2 (pairs2*.txt; prd-read/r5/applied.txt as it stood after the round-5 forms, before pass 1's fix):
  control: 4 of 4 caught; Q3 SAME.
  real: Q1, Q2, Q5 SAME. Q3 DIFFERS on "the result's intervals" again (declined, as above). Q4 DIFFERS: H1's "using
  the C_model procedure and the simulation's detector response" can read as the response being used or probed. Fixed:
  "...using the C_model procedure; the detector response is the simulation's and is not probed."
pass 3 (pairs3*.txt; prd-read/r5/applied.txt as committed, the final text):
  control: 4 of 4 caught; Q3 SAME.
  real: all five SAME.
pairs2*.txt are kept as run. applied.txt now regenerates pass 3's input, since make_r5.py reads the worktree.
