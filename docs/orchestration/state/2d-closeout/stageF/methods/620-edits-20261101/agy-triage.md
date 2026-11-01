# The 620 round: agy's targeted read, triaged

**Setup:**
- **Pairs:** `agy-paper/` and `agy-note/` hold agy's (gemini) reads of the round's replaced passages, as BEFORE/AFTER
  pairs against the base `c93a73bce`. `r22/tools/make_agy_pairs.py` built them (`--paper` for `paper_body.tex`), and
  `r22/tools/agy_runs.sh` ran them.
- **Prompt:** Step 4's targeted one (`r22/step4/agy2/prompt.txt`, with "paper" for the paper batch), which asks for
  every difference in meaning.
- **Control:** a copy with three planted negation removals per batch (`KEY.txt`). It includes identity fillers, which
  must read NONE in the real read.
- **Text read:**
  - The paper batch reads the final paper text (`3863016d4`).
  - The note batch reads `6c6c20f11`, whose `sec_3d.tex` and `sec_fived16.tex` are byte-identical to the final ones.
  - Two earlier reads were superseded by later edits and are not kept.

**What the tool pairs.** It pairs only replaced passages. The added sentences are the departure after Eq. (1) and the
two 1B disclosures. Those rest on the ledger (E5, E7, E8) and on the two-direction review (`review.md`).

## Control

**The control caught all six planted changes, 3 of 3 in each batch.**

| batch | planted | listed |
|---|---|---|
| paper | Q2 "do not provide" → "do provide"; Q5 "did not reduce" → "did reduce"; Q6 "with no reference period" → "with reference period" | 3 of 3 |
| note | Q1 "changes no … bin" → "changes such bin"; Q2 "does not make a bin irrelevant" → "does make"; Q3 "no error bars" → "error bars" | 3 of 3 |

The identity fillers (paper Q5 and Q6; note Q2 and Q3) read NONE in the real read, so the silent direction holds.

## The real read

| pair | change | differences listed | verdict |
|---|---|---|---|
| paper Q1 | E1, Eq. (1) split | NONE: layout only | pass |
| paper Q2 | E2, the W paragraph | NONE: every fact kept | pass |
| paper Q3 | E3 and E4, the estimator paragraph | the table reference dropped; the shared settings stated for both; "seed~42" → "a fixed seed"; the 2D estimator's outputs, with the covariance and Sec. IV B | pass, all declared. The shared refinement was in Table I's rows for both estimators, so it is not a new attribution |
| paper Q4 | E4, Table I | the table dropped, and with it each caption and row fact | pass. Each fact prints in the new paragraph (Q3; ledger E4's probes), apart from "seed plus three", which moves to the note by decision (E3; it prints at `sec_method.tex` (f)) |
| note Q1 | E6, the 135 MeV paragraph | the new share and largest change, and their sample; "materiality is not established" dropped; the sixteen-cell size added | pass, all declared |

**The result:** no undeclared difference in meaning.
