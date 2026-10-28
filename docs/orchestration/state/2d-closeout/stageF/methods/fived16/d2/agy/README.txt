d2's agy pass (gemini-3.8-flash-high via run_x.sh; prd-read/r3/agy's prompt: BEFORE accepted as correct, AFTER judged
against it). make_pairs_d2.py builds the pairs from the tree, nothing retyped:
  Q1 the paper abstract (PB) against the abstract before d2 (13af4709);
  Q2 the note abstract (NA) against the note abstract before d2;
  Q3 O3's qualified sentence against the paper's sentence before d2 and the note's statements on the residual;
  Q4 IV H's R11 sentence against the review's measured |b|/sigma values at that cell;
  Q5 the title (T1) against the paper's opening sentence.
For Q1 and Q2, the pairs say that AFTER is BEFORE with whole sentences removed by design, so a removal is not to be
flagged as such.

control (pairs-control.txt, one strengthening planted per pair): 5 of 5 caught.
real:
  Q1 SAME.
  Q2 DIFFERS: "We report a simultaneous measurement" frames the note as a measurement where "This note documents an
     unfolding ... and its validation" did. Against the note's own removed sentence 1 ("Its principal result is a
     cross section in five observables") this is not a strengthening, so the candidate stands. It bears on n4
     item 1, though: the note's executive summary and summary call the validation findings the main results. It goes
     to Joseph in d2. The dropped covariance-term list is a removal by design (ledger D2-A1 probes it in the body).
  Q3 DIFFERS: on limitations that BEFORE's note context carries and the paper's sentence never did ("no uncertainty
     quoted includes this residual bias"; "a finite scan"). The qualified sentence adds the note's "no single cause
     is established" and states nothing beyond BEFORE. Declined, as an artifact of how BEFORE was built.
  Q4 DIFFERS: on "G18_10a_02_11b", where BEFORE has the abbreviation "G18" (the same tune, FD-F1-REPORT.md §1.3), and
     on the sentence leaving out the numbers and "GiBUU vertex". "only with C_model included" is true: |b|/sigma is
     1.07 with C_e + C_resp alone. Declined; the fuller form, naming the GiBUU vertex, goes to Joseph.
  Q5 DIFFERS: on "on hydrocarbon", which is not in BEFORE (the opening sentence), and on the dropped "medium-energy".
     T1 is Joseph's choice (DECISION-20261028 item 1). The paper body places the vertex in the tracker fiducial volume
     and compares predictions per nucleon for CH, but no body sentence names the target material. It goes to Joseph
     in d2, with a DRAFT phrase for the fiducial-volume sentence.
