# The 620 round: the independent two-direction review, with dispositions

**The reviewer:** a fresh general-purpose subagent with no stake in the text, read-only. It was given the diff, the
decisions and the sources, not the writer's conclusions.

**What it reviewed:** `c93a73bce..d758126e1` (`paper_body.tex`, `sec_3d.tex`, `sec_fived16.tex`,
`make_values_fived16.py`), against the readouts and the built PDFs.

**The two directions:** truth (each new or changed statement against its source) and loss (no true fact dropped).

**The result:**
- Every printed number matches its pinned readout.
- Nothing true was lost from the old Table I, the W paragraph or the estimator paragraph.
- Three Medium findings, all in the 1B disclosure, are fixed.
- Of eleven Low findings, eight are fixed. Two are kept, and one is reported because it lies outside the diff.

| # | sev. | finding | disposition |
|---|---|---|---|
| 1 | Medium | "draw the systematic uncertainties" overstates 1B. C_model and C_resp are not drawn, and lateral and normalization enter as surrogates (FD-1B-DECLARATION.md §3, the draws table) | FIXED. The paper reads "draw the flux, interaction, and detector uncertainties". The note adds "(the lateral and normalization ones as surrogates, and C_model and C_resp not at all)". Verified against §3's rows |
| 2 | Medium | "because its pseudo-experiment machinery did not reproduce the covariance blocks" assigns a cause. FD-1B-STAGE2-REPORT.md lists "Not measured: why the ratios depart from 1" | FIXED. The paper now says the reproduced uncertainties "disagreed with the covariance blocks they draw, for reasons not established". The note says "why the ratios depart from one has not been established". Verified at STAGE2-REPORT "Not measured" |
| 3 | Medium | "by more than 10 % in 11 of the 16 cells" hides the size: ρ_c runs from 0.696 to 2.296 | FIXED. The note prints the window 0.9–1.1 and the range 0.70–2.30, all through new keys (`cov1b-win-*`, `cov1b-rho-*`) from gate-d.json |
| 4 | Low | the paper did not say 1B was declared for the covariance without the run-period block | FIXED: "declared in advance for the covariance without the run-period block" |
| 5 | Low | (a) the 38 bands are the drawn bands, not all systematic bands. (b) "propagated through its machinery" is only partly true, because S1's stat, normalization and lateral blocks enter E_d unchanged | FIXED. (a) "of the 38 drawn bands". (b) "reproduced through the pseudo-experiments"; the source comment records which blocks enter E_d unchanged |
| 6 | Low | "accounts for the difference" reads as an explanation; L1 is a replacement test | FIXED: "Replacing the pseudo-experiments' values by the covariance's for any three or fewer of the 38 drawn bands does not bring every cell inside that window" (FD-1B-DIAG-DECLARATION.md L1) |
| 7 | Low | the paper does not define "to first order" or "as one coherent shift"; optionally, the predictions would move too | FIXED in part. The paper now has "to first order in the unfolding, without retraining" and "the norm of the shift under the reported covariance". KEPT: the predictions' shift (ASSESSMENT §7.3's caution) is not added. The sentence speaks of the result, not of a χ², and the decision limits it to one or two sentences. Reported to the director |
| 8 | Low | register: the departure sentence sat between Eq. (1)'s gloss and "The sums run over"; "Ref. [19], Eq. 4," fell mid-clause | FIXED. The departure now follows "contribute nothing", and reads "in Eq. 4 of Ref. [19]" |
| 9 | Low, informational | the paper leads with 0.19σ, the with-block value, while the question Joseph approved quoted 0.21σ, the without-block value | KEPT. Under J2 the paper prints both, with the reported covariance first. Reported to the director for Joseph's read |
| 10 | Low, unverifiable here | the repo's sources differ on whether arXiv:2312.16631 Eq. 4 has an open "strange, or heavier quark" clause (EAVAIL_DEFINITION.md:41 against :80) | KEPT. The paper claims only that Eq. 4's charged-pion term is kinetic, which both sources support, and "the open list of Ref. [20]" does not say [19] is closed. Reported to the director, since only the paper itself settles it |
| 11 | Low | the tightened W paragraph lost "because" | FIXED: "…apart from a clamp at W² = 0, because W²_reco = …" |
| 12 | Low | ":54 and :56 both say gradient-boosted trees" | FIXED. The citation moves into the new paragraph, and :56's sentence is dropped |
| 13 | Low | sec_3d: "not assessed against configuration (a)" followed by an assessment read as a contradiction | FIXED: "On the sixteen-cell result …, from configuration (e), …" |
| 14 | Low, outside the diff | EAVAIL_DEFINITION.md:118–119 calls C_total + C_resp "the reported" covariance; the paper's reported covariance includes C_PL,5D | NOT IN THIS ROUND. That file has its own owner's review (DECISION-20261101-joseph-eavail-keep-135.md item 3). Reported to the director |

**Checks the reviewer ran that passed:**
- **Digests:** the four new readouts match their pins.
- **Values:** every printed value matches its readout, and the with-block and without-block labels are correct.
- **Definitions:** the published-definition statements match EAVAIL_DEFINITION.md §1–3 and the note's sec_3d. The
  sentence does not make the pion constant the only departure.
- **Citations:** the three keys name the right papers.
- **1B:** every 1B fact is supported (declared in advance; gate D was the second gate; no coverage toy ran; NOT
  LOCALIZED).
- **Layout:** Eq. (1) renders split under one number.
- **Loss check:** clean. Every Table I entry prints, "42" and "seed plus three" print only in the note, and nothing
  references `tab:estimators`.

**A guard this round added after the review:** a ledger row whose probe quoted a markdown table row split into more
than six cells, and `step2/check_ledger.py` skipped it without a failure. Its count of rows fell from 9 to 8. The
checker now fails on any table line that does not split into six columns. A self-test plant covers this, and no
earlier round's ledger had such a row.
