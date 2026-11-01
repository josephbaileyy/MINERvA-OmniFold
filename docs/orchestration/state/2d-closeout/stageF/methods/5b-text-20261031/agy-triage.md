# The 5B text round: agy's agreement read, triaged

`agy-paper/` and `agy-note/` are agy's (gemini) reads of the round's changed passages, each as a BEFORE/AFTER pair
against the base `ac8fb9ae3`, with a planted control. They were built by `r22/tools/make_agy_pairs.py` (`--paper` for
`paper_body.tex`) and run by `r22/tools/agy_runs.sh`.

## The control is weak, so this read does not certify the text on its own

**What the control found:** agy named the planted negation in **2 of 6** planted pairs: paper Q8 ("do not show" made
"do show") and note Q6 ("not evidence" made "evidence").

**Where it missed:** in the other four (paper Q2 and Q3, note Q4 and Q5), it described only the large real change in
the same pair, the new run-period paragraph or the new fake-data lists, and did not mention the negation.

**Why:** every pair of this round is a changed passage, most of them long, so there are no identity fillers. A planted
negation then competes with a real change of the same pair for agy's one-line detail.

**What it means:** a DIFFERS here is not evidence that agy read each sentence. The read is kept as one input. The
independent two-direction review (`review.md`) and the ledger (`check_ledger.py`) are the checks this round relies on.

## The real pairs: every flag is a declared change

| pair | flag | disposition |
|---|---|---|
| paper Q1, Q4, Q7; note Q2, Q6, Q9, Q10 | the reported covariance now includes C_PL,5D | DECISION-20261030 item 2 (ledger R1) |
| paper Q2 | the run-period paragraph and the declaration (v) paragraph added; the median re-keyed | R3, R4, R5 |
| paper Q3; note Q5, Q8 | the GiBUU E_avail shape is listed only without C_PL,5D | J1(a) (R6); the lists are the readouts' (`make_values_fived16.py` LISTED_CLAIMS checks them against both arms) |
| paper Q5, Q6; note Q1, Q3 | the reported sigma and the medians re-keyed; the cells table gains C_PL,5D and the reported column | R2, R4 |
| paper Q8; note Q7 | Table IV and Table 16 restructured; the "with its number of degrees of freedom" clause and the ndf columns replaced by ndf once per block heading | J2(a) (R8): "ndf given once per block" |
| note Q4 | the new sec:fived16-pl and the declaration (v) paragraph | R3, R5 |

No flag names a change the ledger does not declare.
