# Batch of 2026-11-16 (items 1-8 and B2-B4): independent meaning read (codex-school gpt-6.1-sol, read-only)

Read over every changed printed sentence from 4297bd33f to e70241f6f against the paper and Supplement at draft/methods-short-20261109, App. D and DECISION-20261114-joseph-d1-g2r-adopted.md. Its four FIXes were applied in the following commit: the App. I first-grade row names the one per-cell threshold that moved (G18 cell 29, keyed: cov2d-g18-29-kc-first); sec. 5.3 says the threshold rule, not every threshold, was fixed in advance; the truncation sentence is marked descriptive and made after the result; the pulls caption (and, by the same reasoning, the sensitivity, eigenmode and breakdown captions) says the CH correction is the secondary comparison. Verbatim answer:

| Site | Q1 | Q2 | OK or FIX with exact replacement |
|---|---|---|---|
| App. I, new first-grade row, “keeps its verdict…” | Joint thresholds agree; broader “thresholds” is ambiguous. | G18 cell 29’s per-cell threshold moved **175 → 174**. | **FIX outcome cell:** “Superseded by the regrade against the adopted covariance: the verdict, joint counts and their thresholds, and flagged cells and their in-interval counts are unchanged; G18 cell 29’s threshold changes from 175 to 174, and the mean χ²/ndf, false-flag bounds and other flagged-cell diagnostics also change.” |
| §5.3, retained “The thresholds were fixed…” | Supported for the original design; not established for every numerical threshold in the regrade. | Re-keying makes the distinction between the unchanged **rule** and changed thresholds consequential. | **FIX:** “The null-based threshold rule was fixed before any pseudo-experiment was read.” |
| §5.3, new truncation sentence | Numerical result matches paper §6.2 and Supplement S8.4. | Loses their **descriptive, after-the-result** qualification; comments do not print it. | **FIX:** “In a descriptive study made after the test’s result, truncating the joint test to its 73 or 139 largest-eigenvalue directions still finds none of the 300 pseudo-experiments in its region at either tune, so truncation to the better-determined directions does not remove the joint under-coverage.” |
| §10.7, new CH-diagnostics sentence / consequential Table 23 caption | The new sentence correctly identifies the diagnostics as CH-corrected. | Table 23 still says “for each prediction of Table 22,” whose NuWro/GiBUU predictions are now carbon. | **FIX Table 23 caption:** “Per-cell pull \((f-g)/\sigma\) against \(C_{\mathrm{total}}+C_{\mathrm{resp}}+C_{\mathrm{PL,5D}}+V_g\) and \((g-f)/f\) (%) for the secondary comparison with NuWro and GiBUU corrected to CH; the other predictions are unchanged from Table 22, and GiBUU is shown on its eight cells only.” |

The remaining changed sentences and printed entries pass as follows; grouped sites cover each changed sentence at that location.

| Site | Q1 | Q2 | Verdict |
|---|---|---|---|
| Abstract: “No reported interval…”; two-observable under-coverage sentence; separate five-dimensional futility sentence | Supported; consistent with paper §§6.2, 7.1 and the note’s five-dimensional test. | “0 of 300 … at each” correctly applies to **both** tunes. | **OK** |
| Executive summary: carbon comparison sentence and GiBUU sentence | Matches Supplement S10: range 107–229; GiBUU carbon rounds to 45 on eight cells. | No CH-primary claim remains in these sentences. | **OK** |
| Executive summary: revised \(C_Z\) interpretation sentences | Consistent with §9’s actual descriptive uses and stated restrictions. | Names configuration (a), preserves the companion-covariance distinction, and denies uncertainty-product status. | **OK** |
| Executive summary: expanded coverage-limitation sentence | Matches paper §7.1. | Preserves procedure-versus-reported-interval scope; zero count applies at each tune. | **OK** |
| Introduction: “The tests and uncertainty…” | Consistent with §9’s findings. | Removes the validation implication. | **OK** |
| Introduction: PET scope sentence | Consistent with stated batch intent. | Companion pointer resolves through App. F; no result dependence claimed. | **OK** |
| Method: “in shape as well as normalization…” | Matches Supplement S4. | Both numerical observations retained. | **OK** |
| Experiment: deletion of duplicate prior/data sentence | Supported by the retained control-distribution sentences. | Neither normalization nor shape information is lost. | **OK** |
| §9 heading and opening “This section tests…” | Consistent with the failed recovery, stability and coverage findings. | No validation claim remains. | **OK** |
| §9.6: revised seed-shift uncertainty sentence | Consistent with the surrounding configuration-(a) diagnostic. | Denominator is identified; surrounding text retains the two-companion-covariance scope. | **OK** |
| §8.4: reconstruction-only / shifted-response status sentence | Supported by App. D. | Distinguishes the unrun reconstruction-only test from completed sixteen-cell closures. | **OK** |
| §5.1: reconstruction-only / noise-free closure sentence | Supported by App. D. | No blanket “response mismatch not run” claim remains. | **OK** |
| Closure-test table: revised response-mismatch result entry | Supported by App. D. | Row’s reconstructed-\(E_{\mathrm{avail}}\) description scopes “not run”; shifted-response closures are separately named. | **OK** |
| §5.3: regraded mean χ²/ndf, false-flag bounds, and Table 8’s changed numerical entries | Match the landed values and paper. | Includes G18’s revised threshold of 174. | **OK** |
| §5.3: “These numbers are the test’s regrade…” | Supported by adoption decision items 2–3 and landed differences. | Explicitly preserves **joint** thresholds and flagged-cell in-interval counts only. | **OK** |
| §5.3 Limits: all three new covariance-noise sentences | Match paper §6.2 and Supplement S8. | Preserve exact-covariance null, finite-ensemble limitation, no correction, and unchanged grading interpretation. | **OK** |
| §10.5: “A first coverage test…” | Matches paper §6.2(c) and Supplement S8.6. | Correctly identifies the gate-stopped first test; surrounding text distinguishes its staged redesign and the second test. | **OK** |
| App. I: revised first-test and staged-redesign row labels | Same test identities as paper/Supplement. | Neither stop becomes a coverage result. | **OK** |
| §10.7: carbon-primary sentence and CH-secondary/caveat sentence | Matches Supplement’s target policy and caveat. | Primary/secondary distinction is explicit. | **OK** |
| Table 22: revised target sentences and NuWro/GiBUU rows | Carbon values and labels agree with Supplement S10. | Caption, rows and comparison regions agree. | **OK** |
| §10.8: revised opening sentence and CH-construction sentence | Supported by Supplement and the explicit mixture formula. | Separates target correction from definition changes. | **OK** |
| §10.8: “Table 26 gives…” and CH-versus-carbon numerical sentence | Consistent with displayed values. | Correct table references and target assignments. | **OK** |
| Table 26: revised opening caption sentence and four carbon/CH row labels | Supported; labels match values. | Carbon references now point correctly to Table 22; CH remains secondary. | **OK** |
| Appendix guide: PET sentence; App. F heading and three revised PET sentences | No paper/Supplement contradiction; matches stated intent. | Terminal selection status is explicit; companion citation resolves as [98]. | **OK*** |

\* The supplied material does not include the PET selection decision or companion-note contents, so its terminal selection outcome is consistent with your stated intent but not independently verified here.