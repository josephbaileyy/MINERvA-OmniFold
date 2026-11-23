# LL5D paragraph, abstract and ES clauses, and the first-test scoping: independent meaning read (codex-school gpt-6.1-sol, read-only, 2026-11-16)

Prompt: two questions per sentence against LL5D-DECLARATION.md, LL5D-AMENDMENT-A1A2.md, the paper at draft/methods-short-20261109 037431430 (rendered) and DECISION-20261116-joseph-paper-batch.md. Its four FIXes were applied (sentence 4, with "the seed block not rebuilt" for its "retained", per the declaration's seed row; sentence 7; sentence 9, in the paper's F2 wording; the ES clause). Verbatim answer:

Most claims agree with the approved paper. The repair disclosure and definition of “descriptive” preserve all the required distinctions.

D = declaration; A = amendment; P = companion paper. Sentence openings identify the full sentences.

| Sentence / clause | Q1: supported and consistent? | Q2: qualifier or meaning issue? | OK or FIX with exact replacement |
|---|---|---|---|
| Heading: “The second coverage test.” | Yes; P’s numbering. | The staged redesign remains part of the first test. | **OK** |
| 1. “A second coverage test … uses the reported estimator.” | Yes; D §1, P. | “Same two tunes” has an antecedent. | **OK** |
| 2. “Its pseudo-experiments draw …” | Yes; D §3.2. | Both lateral and normalization uncertainties are correctly identified as surrogates. | **OK** |
| 3. “The graded covariance includes the model term …” | Yes; D §3.7, P. | Correctly distinguishes inclusion in covariance from drawing the term. | **OK** |
| 4. “At each tune the covariance is rebuilt … at their means; this block stands in …” | Broadly yes; D §4. | The blanket means description loses the statistical-block exception at D:297. The per-experiment stand-in disclosure is correct. | **FIX:** “At each tune the covariance is built by the reported procedure using the tune’s pseudo-data at their means, with the statistical block bootstrapped from one Poisson realization and the seed block retained; this fixed covariance stands in for one rebuilt for each pseudo-experiment, which was not computed.” |
| 5. “The lateral block is carried … and the tunes’ overlaps … (above) apply.” | Yes; D §§3.1, 3.8. | Antecedent exists: preceding text states the shared quasielastic model, G18’s Valencia-family overlap, and non-independence. | **OK** |
| 6. “The response and run-period terms are left out …” | Yes; D §4, P. | Correctly scopes the graded covariance. | **OK** |
| 7. “The test is read in two variants … primary.” | Yes; D §1, P. | Omits correlation and explicit exclusion from both pseudo-data and covariance. No contradiction, but worth preserving these qualifications. | **FIX:** “The test has two correlated variants, without and with the GEANT4 neutron and proton bands; the primary variant omits them from both its pseudo-data and its graded covariance.” |
| 8. “Each tune and each variant is graded separately … resolution …” | Yes; D §6, P. | Both resolutions and separate grading are correct. | **OK** |
| 9. “In one variant at one tune … probability at most 0.025 …” | Yes, **under the specified null**. | Unqualified probability loses P’s fixed-covariance-null restriction. | **FIX:** “Under the test’s null, which treats the fixed covariance as exact, the probability of any false cell flag is at most 0.025 per tune and variant, and the joint false-flag probability is also at most 0.025.” |
| 10. “A cell that passes … full covariance there … 16 degrees of freedom.” | Yes; D §4, P. | “There” correctly means at that tune, not at the data. Rank qualification retained. | **OK** |
| 11. “At both tunes, an event-matching entry check stopped …” | Yes; A, P’s approved repair paragraph. | Precision mismatch and every-row-unmatched finding preserved. | **OK** |
| 12. “The repair, chosen after this stop … before any … but after other gate readings …” | Yes; A, P, decision 14. | All timing distinctions retained; does not claim the repair preceded all readings. | **OK** |
| 13. “It changed no rule, threshold, bound or reporting cell.” | Yes; A, P. | Does not claim no implementation changed. | **OK** |
| 14. “Under the rule fixed before the result … descriptive: …” | Yes; P’s repair paragraph and Table 4 definition. | Exactly the approved meaning: advance criteria applied; repair selected after an entry-check stop. Sentence 12 supplies the remaining disclosures. | **OK** |
| 15. “Without the two bands … G18 … AR23 … R07.” | Yes; P. | Both tune-specific classifications match. | **OK** |
| 16. “With the two bands, the flags are the same …” | Yes; P. | Same flags, without claiming identical numerical results. | **OK** |
| 17. “Over the four readings, 1 to 14 of 300 … 195 … 3.0 to 3.7.” | Yes; P. | Counts, threshold and mean χ²/ndf range match. | **OK** |
| 18. “The test therefore flags joint under-coverage … for a covariance without …” | Yes; P §7. | Essential covariance restriction retained; no claim about full reported intervals. | **OK** |
| 19. “Whether the joint failure persists … remains untested.” | Yes; D §4, P §7, decision 2. | Correctly prevents extrapolation to the covariance including those terms. | **OK** |
| Abstract: “The first coverage test … did not run to a result” | Yes; P and preceding note text. | “First” appropriately includes its staged redesign; advance specification does not imply successful completion. | **OK** |
| Abstract: “a second, reported as descriptive … both held-out tunes … covariance without …” | Yes; P §7. | “Held-out” is supported and does not mean independent. Restricted covariance and descriptive status retained. | **OK** |
| Executive summary: “where a second, descriptive test flags … both held-out tunes” | Supported, but less qualified than P §7. | Loses the covariance restriction next to a statement about reported intervals. | **FIX:** “where a second, descriptive test flags joint under-coverage at both held-out tunes for a covariance without the response and run-period terms” |
| Scoping fix: “A staged redesign of that first test … also ended without a coverage result.” | Yes; preceding note context. | Correctly prevents the staged redesign being mistaken for LL5D; “also” refers to the earlier unsuccessful first-test run. | **OK** |

All four D §13 requirements are present: resolution and size, overlaps, the means-block stand-in, and carried laterals. The stated size allocation is 0.025 across cell flags plus 0.025 jointly, per tune and variant.

“Stop” is lowercase throughout the **new printed note text**. The supplied companion-paper rendering still has five uppercase “STOP” occurrences; if checking that artifact too, replace each printed “STOP” with “stop” under decision 21. Uppercase occurrences in TeX comments do not print.