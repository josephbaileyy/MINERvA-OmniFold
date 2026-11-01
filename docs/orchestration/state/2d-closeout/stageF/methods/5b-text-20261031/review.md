# The 5B text round: independent two-direction review, with dispositions

**The reviewer:** a fresh general-purpose subagent with no stake in the text, read-only.

**What it reviewed:** the diff `ac8fb9ae3..208621612` against the decisions, the referee's answer, PROVENANCE-20261031
§3–§6, the 5B, audit and addition reports, the data product's block label, `values_fived16.tex` and the rendered PDFs.

**The two directions:** truth (is each new or changed sentence supported?) and loss (does a rewritten sentence drop a
fact or qualifier?).

**Result:** 10 findings (1 High, 4 Medium, 5 Low). Every other area passed; the checks that passed are listed at the end.

| # | sev. | finding | disposition |
|---|---|---|---|
| 1 | High | note sec:fived16-pl: "These falls are larger than the change in any cell's σ". False for 4 of the 10 falls (GENIE CV total 3.6 %, GENIE CV shape-only 7.3 %, GiBUU shape-only 10.6 %, GENIE + MEC shape-only 13.4 %, against R04's 14.1 % σ rise), and it compares unlike units | FIXED. The premise is removed. The inference stays, marked as one, in the referee's form: "We infer from these falls that …; the comparison does not test this interpretation." |
| 2 | Medium | note: "not mutually consistent on the sixteen cells within the other uncertainties". 5B supports only "beyond the bootstrap noise". Against M = C_total + C_resp the double ratios give χ²_M of 10.66 to 38.0 for 16 cells, two of them within M (re-measured from FD-CT-5B-REPORT.md's table) | FIXED. The note now says only that the groups differ from one another by more than their bootstrap scatter. The paper's "accounts for an inconsistency" became "accounts for differences" |
| 3 | Medium | note: the audit description implied that no overlap was found. It also left out the 5A/5B pattern comparison and the rank-two stability (clause R) | FIXED. All four audit items are named. The text adds "Passing the audit establishes neither the block's size nor the absence of overlap", and states the descriptive pair finding (`labels.context_dr_pair`) without numbers |
| 4 | Medium | paper: the declaration-(v) list of "the others" left out C_PL,5D and V_g | FIXED. The list names the run-period block (three exposure-weighted periods) and V_g |
| 5 | Medium | abstracts: "the stated comparison thresholds" are not stated in the abstract and lose the link to the reported uncertainty. Also "and" where the decision quotes "or" | PROPOSED FOR JOSEPH (A4). Both abstracts now read "the thresholds set against the reported uncertainty at a GiBUU-like truth and at a synthetic q3 tilt". The pairs go to the director with "and" flagged; Joseph approves each whole abstract. The with-block range (105–224; 7.86 %, against 109–272 and 7.29 % without) is left to him |
| 6 | Low | paper: "one cell's uncertainty, R04's" could read as the only cell affected | FIXED: "the uncertainty of the most affected cell, R04" |
| 7 | Low | the ledger's R6 said the fake-data tables give the without-block grade; only the note's does | FIXED in the ledger. The paper's prose gives both lists, which is what its sentence claims |
| 8 | Low | paper: the block's label (the 68 % interval; undebiased) does not travel with it | FIXED. The paper prints "is not corrected for the bootstrap noise it contains" and the 0.73–2.56 interval (`\fvval{pl-sigratio-*}`). The noise-dominated cells stay in the note |
| 9 | Low | note: the base's "listed as failing" sits beside the new "meets the listing criterion" | KEPT. That base sentence defines the criterion. The two wordings name the same rule, and the guard checks every listing sentence |
| 10 | Low | hand-typed constants. The playlist ranges match the 2D text (ME has no 1H–1K) | "ten bootstrap replicas" is REMOVED ("bootstrap replicas of each period"). The other constants (16×16, 8×8, 100 f fᵀ, three periods, four shifts, 68 %) are declaration constants, agreeing with PROVENANCE §3, and are KEPT |

**Not checked by the review, and re-measured here:** "In cell R11 at G18, the bias lies below the reported uncertainty
only with C_model included" (paper, F1 paragraph). In the with-block F1 readout (`5ccc89e5`), R11's |bias| / σ is 1.029
under C_e + C_resp + C_PL,5D and 0.614 under the reported C_total + C_resp + C_PL,5D. The sentence still holds.

**Checks that passed** (the reviewer's words, abridged):
- the listing criterion and both lists, with "the other 10" and z = 2.01 against 1.76;
- the bias identical across the arms;
- the χ² falls and the medians and rises;
- the block's construction;
- declaration (v): N, normalization, n_eff, Cholesky, no truncation, no correction, and no use of the truncation argument;
- "followed the data";
- Table IV and Table 16;
- the downstream numbers recomputed with the block;
- no stale "C_total + C_resp as reported" text left.
