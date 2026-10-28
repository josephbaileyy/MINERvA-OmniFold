r19 b3: agy on the new non-number wording. Q1: the result table's lead and caption, against the note's table caption and the data product's labels.units. Q2-Q4: T4, K8 and the Limitations paragraph's K9 sentences, against the base. LaTeX source, at 367231da.

- agy-control.txt (plants "can use these uncertainties alone" in Q1 and "which has been shown" in Q4): both CAUGHT.
- agy-real.txt:
  - Q1 DIFFERS: "a box that reaches it holds every signal event above its lower edge on that axis" is overbroad, because the box is bounded on the other axes. Fixed (apply_b3_fixes_b4.py S5/Q1): the outer edge of the analysis grid, "which contains every signal event", with the note pointer \nsec{sec:method-binning} ("the truth grids are exhaustive") and guard G28.
  - Q2 DIFFERS: "the comparisons below" broadened the base's singular. Fixed: "the comparison that follows".
  - Q3 and Q4 SAME.
