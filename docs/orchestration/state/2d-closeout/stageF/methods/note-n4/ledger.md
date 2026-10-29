# Note round n4: fact ledger

**Checker:** `check_ledger.py <worktree>` (base `371cccec`). The edits are in `apply_n4.py`, by batch; the outline and the
director's rulings are in `outline.md`.

**Sentence ids** are `--list`'s: a file prefix and the sentence's index in the base file's printed text.

## Batch C: the interval-sense "calibration" sites and the main-result sentence (outline sec. 2)

Accuracy and consistency fixes, unscored (rulings 2a, 2b). The ids C1–C7 and M1–M2 are `apply_n4.C`'s.

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| C1 | the joint-test candidate's pooled interval test (pull width 1.02); N1 (sec:val-fiveaxis) calls an interval property coverage | FD54 | ACC | "a pooled test of its statistical intervals (pull width 1.02)": the record's row A2 measured pull widths, pooled coverage (0.680 / 0.942) and a Mahalanobis distance, so no single property is named | `N:sec_5d.tex::and a pooled test of its statistical intervals (pull width 1.02).` && `N:sec_5d.tex::Coverage asks whether the resulting intervals contain their specified target at the stated rate` |
| C2 | the pooled pass does not extend to every functional | FD55 | ACC | "does not establish coverage and width for every functional": the record's "a pooled pass, not per-functional calibration" (six functionals beyond 3 SE; EW41 68% coverage 0.375) | `N:sec_5d.tex::The pooled test does not establish coverage and width for every functional.` |
| C3 | EW41 covers 15 of 40; a pooled pass cannot qualify the cell | FD121 | ACC | "a pooled pass" | `N:sec_5d.tex::so a pooled pass cannot qualify this cell.` |
| C4 | repeating a calculation checks neither the intervals' coverage and width nor the physical model | VA5 | ACC | "the coverage and width of the intervals" | `N:sec_validation.tex::Repeating a numerical calculation checks neither the coverage and width of the intervals nor the adequacy of the physical model.` |
| C5 | H2S1T24 fails the PET campaign's coverage rule (C1 and C4 FAIL; DECISION_RECORD-pet-final-design.md:47, :49) | PC53 | ACC | "fails the frozen coverage rule", the record's name, parallel to "the frozen point rule" | `N:sec_pet_campaigns.tex::H2S1T24 fails the frozen coverage rule and L128S1T24 fails B2 by the frozen point rule (statistically unresolved).` |
| C6 | the measured PET interval procedure failed (the same coverage rule) | PC108 | ACC | "failed the frozen coverage rule" | `N:sec_pet_campaigns.tex::and the measured PET procedure failed the frozen coverage rule.` |
| C7 | the cited work constructs intervals for functionals; its title is "Confidence intervals for functionals in constrained inverse problems" | AB67 | ACC | "confidence intervals" | `N:app_statmethods_nd.tex::Recent work constructs confidence intervals for selected functionals in constrained inverse problems~\cite{Stanley:2025functionals}` |
| M1 | the note's principal result; it matches the note abstract (main_note.tex:72) and the paper's printed Conclusions (paper_body.tex:355) | ES1, ES2 | ACC | the paper's sentence, retargeted to \S\ref{sec:fived16}; "They hold" becomes "The results hold", the same scope | `N:sec_execsummary.tex::The principal result is the sixteen-cell cross section of \S\ref{sec:fived16}, with its covariance and generator comparison.` && `N:sec_execsummary.tex::The results hold for this implementation, one data set, and the configurations, observables and deformations tested (\S\ref{sec:intro}).` && `P::The principal result is the sixteen-cell cross section of Sec.~\ref{sec:result16}, with its covariance and generator comparison.` && `X:sec_execsummary.tex::The main results are the validation findings` |
| M2 | the same, in §12, and the scope pointer kept | SU2 | ACC | as M1 | `N:sec_summary.tex::The principal result is the sixteen-cell cross section of \S\ref{sec:fived16}, with its covariance and generator comparison.` && `N:sec_summary.tex::The results hold within the scope stated in \S\ref{sec:intro}.` && `X:sec_summary.tex::The main results are the validation findings` |
