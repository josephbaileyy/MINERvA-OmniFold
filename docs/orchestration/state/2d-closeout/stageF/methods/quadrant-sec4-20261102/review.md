# The quadrant-sentence and Section IV paper round: the independent two-direction review, with dispositions

**The reviewer:** a fresh general-purpose subagent, read-only. It was given:
- the diff `7bac3c634..6fd6361eb`, with both builds;
- the director's work order, verbatim;
- the authorities: DECISION-20261102 (#690); the X report, declaration, `k.json` and `fd_xcov.py`; the amendment E
  report §3.2 and `overlap_refined.json`; the GENCMP declaration's rule and §10; OUTCOME-20261005; the note's sources;
  Gemini's Section IV answer; the round's records.

It was not given the writer's conclusions. It re-derived every number with its own code from the JSON readouts.

**The two directions:**
- truth: each changed sentence, caption, cell and value against its source;
- loss: no fact dropped from paper plus note, and no sentence elsewhere left false.

**The result:** nothing false in the printed numbers or in the note's descriptions of C-R's and X's rules, covariances
and bounded blocks.
- The decided sentence prints word for word.
- C-R's d/S₂D, ρ*, z at ρ = 0 and readings match. X's V_d(0), rebuilt from `k.json`'s own and 42 paired blocks, gives
  χ² = 1.16962; every p equals the χ² survival function for 4 degrees of freedom; the largest |z| is 0.985 (QC, r = 1).
  The counts (34 of 38 bands, 5 laterals, 99 controls, four bounded bands) and the correlations match.
- The code's mathematics holds: each diagonal entry of V_d(r) is linear in r, so each |z| is monotone; χ² is convex
  wherever V(r) is positive definite, which holds at both ends and so on all of [0, 1]. "p ≥ 0.87" and "no quadrant
  beyond one standard deviation" therefore hold over the whole family.
- The marginal's 0.141044 % and QA's 0.141053 % are different quantities, as the text says.
- `--self-test` on a `git archive` copy passes; all seven quadrant plants are refused by their intended guard.
- The Limitations statement is accurate and complete against the work order; IV A–C are neutral, with nothing
  repeated; IV B is faithful to Gemini §3 and to the base.

| # | sev. | finding | disposition |
|---|---|---|---|
| 1 | Medium | the commit paraphrased the A7 sentence "We make no coverage claim …" (held byte-exact, G1b:paper-g-20); the restoring edit was not yet committed while the review ran | FIXED in `eb0de39db`: the sentence moves to Limitations verbatim (ledger Q-8). `check_held.py` no longer flags it |
| 2 | Medium | the Limitations opening ("the limitations … are stated with the results they qualify, in Secs. III–V") became untrue for item 1, whose statements now print only there | FIXED: "Apart from the validation of the uncertainties and the low stability of four of the sixteen cells (below), …" (ledger Q-11; G1b:paper-s-20 is held for its facts, which stay) |
| 3 | Medium | the decided text says "a family of valid covariances", without "one-parameter"; the X declaration (A4, `:247`, `:389`) says the paper text would state "within a one-parameter family" | NOT CHANGED: the text is Joseph's, word for word. The note states "a one-parameter family … not every admissible correlation". To the director, for Joseph |
| 4 | Low | "χ² = 1.17–1.24" is the two ends; convexity bounds only the maximum, so χ² inside [0, 1] may fall below 1.17. `k.json` lacks the bounded M blocks, so it cannot be computed from the records | NOT CHANGED (decided text). The note and the source comment state it. To the director, for Joseph, with "p ≥ 0.87", which holds over the family |
| 5 | Low | Table 13's caption said "no reading is taken from it", yet prints a reading | FIXED: "it is printed only, and no outcome is read from it" (the readout's own label) |
| 6 | Low | "it differs above that" could read as "above ρ*" | FIXED: "it differs if \|d\| exceeds 2(σ₁₆² + σ₂D²)^½, beyond two standard deviations at every non-negative ρ" |
| 7 | Low | Limitations item 1's "(Secs. IV A and IV C)" points to sections that no longer state those facts | FIXED: it points to the note's Secs. 10.3, 10.4 and 4.5 |
| 8 | Low | stale `% Search:` comments after paragraphs that no longer state their claim | FIXED: re-pointed to sec:limitations |
| 9 | Low | facts now in the note only: "a comparison across the two estimators", C_PL,5D's audit sentence; nothing lost from paper plus note | NO CHANGE: the clause names "the joint-test estimator's other results", and the paper's Sec. III says the 2D result is the other estimator's; the note states both (`sec_3d.tex:85`, `sec_fived16.tex:175`) |
| 10 | Low | the paper is 13 pages (base 12); page 13 holds only references [25] and [26] | REPORTED: the decided sentence and the Limitations statement add about six lines. Cutting a fact to save two references was not done |

**After the fixes:** rebuilding moved the acknowledgments across the page 11/12 break, and `make_rater_copy.sh` stopped
at its data-availability check. Two shortenings restored the layout with no fact changed: IV B ("rather than" → ", not";
"both the LightGBM and the exact-split" → "the LightGBM and exact-split"), and the Limitations opening above. The rater
copy then exits 0, and holddiff's multiset check passes.
<!-- absence-ok: dispositions of a review; the readout's lack of interior chi2 values is a fact about k.json (fd_xcov.route_a returns r0, r1 and outcomes only) -->
