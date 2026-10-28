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
pass 4 (pairs4*.txt; after the review of 589f0780: N2 "the same quasielastic cross-section model", with AR23's
z-expansion form factor in the note; N3 "the tune's shape ratio to GENIE CV"):
  control: 4 of 4 caught; Q3 SAME.
  real: Q1-Q4 SAME. Q5 DIFFERS on "with a z-expansion form factor" and "defined as in Table 15". BEFORE lacked the
  declaration's model facts (FD-F1-DECLARATION.md:296-298), and the table is the note's own cross-reference. Fixed in
  BEFORE (make_pairs.py quotes the declaration; the prompt note says a cross-reference is not judged), not in the text.
pass 5 (pairs5*.txt; the final text, the fuller BEFORE):
  control: 4 of 4 caught; Q3 SAME.
  real: all five SAME.
p02/ (director ruling 3, after 0a87881c): P02 as printed against its pre-round-3 text (r4/input.txt's OLD), with round
  3's agy prompt. The control drops "a coverage test": caught. Real: DIFFERS. "show how far the result can be trusted"
  becomes "assess the result", and "the background subtraction" becomes "background-subtraction tests". These are the
  register changes that PRD reads r4 and r5 accepted 3 of 3 each. Neither strengthens anything, so they go to Joseph in (d)
  as reading notes, not edits.
pairs2*.txt-pairs4*.txt are kept as run. prd-read/r5/applied.txt now regenerates pass 5's input (make_r5.py reads the
worktree; run it with base 22314565).
