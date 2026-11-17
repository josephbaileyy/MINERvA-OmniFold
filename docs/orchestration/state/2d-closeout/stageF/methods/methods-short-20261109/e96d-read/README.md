# E96D's data sentence in §6.1: the meaning read and the PRD read (2026-11-12)

Joseph decided to print E96D's data result (RESPONSE.md section J3). Two independent general-purpose subagents read
the first draft (`diff-as-read.txt`) read-only:
- `MEANING.txt`, against E96D-DECLARATION.md's Licence: MINOR, no defect. The S4 pointer just before now says "The
  pseudo-data values and their accounting", since S4 holds no data numbers. e96d_values() now also asserts that the
  record's σ is C_e's relative σ.
- `PRD.txt`: accept with one edit, applied. The maxima are scoped to "the sixteen reported cells", the two maxima are
  separate (R05 for the percentage, R06 for the σ figure), and the float64 clause says why it belongs here: the
  ensemble's fits perturb a float64 copy. Its tie to RS1's pseudo-experiment ("as float32 and float64 inputs did") was
  not applied, because RS1's finding is bitwise and this record's is equality to double precision.
