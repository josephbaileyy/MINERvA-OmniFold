# r22 Step 3: agy's agreement read on the final text, triaged

[agy2/](agy2/) is the read on the final text, after the review fixes and the director's rulings. agy sees each
BEFORE/AFTER pair alone. It cannot see the ledger home of a cut fact, or the narrowed form that allowed a change.

**Result:**
- **Control:** 3 of 3 planted negations caught (Q1, Q5, Q10 in `pairs-control.txt`).
- **Real pairs:** 18 SAME, 20 DIFFERS, out of 38.

Each DIFFERS is listed below with its disposition. None is an open defect.

The first read ([agy1/](agy1/), on the writers' text) flagged 25. Four of those were fixed:
- the B09 "bitwise equal" and "detector response fixed" wordings;
- B11's dropped "learned";
- B14-g-02, which the director reverted.

The B05-g-08 caption remark is restored.

| pair | gap | flag | disposition |
|---|---|---|---|
| Q1 | B01-g-03 | adds "the comparison is descriptive" and the covariance's three validation gaps | The narrowed form asks for exactly this. Each fact prints at `sec:uq-2d-scope` (`N:` probes, B01-1). Review F3's wording fix is applied. |
| Q2 | B01-g-02 | drops "to time limits" and "every submitted draw has been observed" | Both print in `sec:joint5d-lost` (`N:` probes, B01-2). Review B01–B05 rules this OK. |
| Q5 | B02-g-01 | drops why the seed was not fixed | The director ruled on 2026-10-30, superseding round n2: the detail moves to `pairings.tsv` P01 (`L:`). The note still says the seed was not fixed and the log was not found. The n2 source comment is updated. |
| Q6 | B02-g-10 | "\SI{0.18}{\percent}" appears | The value prints twice above, in the same subsection (review F6). The referent is now named ("the reseeded run's median"). |
| Q7 | B03-g-07 | drops "does not demonstrate a causal efficiency advantage" | ALLOW. The same limit prints at the same strength in the next paragraph and in `app_statmethods.tex` (`N:` probes, B03). |
| Q8, Q9 | B03-g-10 | values leave the prose, and a table is added | The narrowed form asks for this. All six values and labels match the base (review B01–B05 ruling). The headers are clarified (review F5). |
| Q10 | B04-g-01 | "Two bands were scored" and "for coverage" | "Rebuilt without this term" is restored (review F2). "For coverage" is accurate, because the quoted block has had the nested-half stability check (review ruling). |
| Q11 | B04-g-10 | drops "natively" | "Diagnostic only" stays, and `sec_method.tex` prints "requires no separate efficiency correction" (`N:`). "Miss treatment" is restored (review F4). |
| Q12 | B05-g-03 | drops `hXSec2D`, `hXSec_pt`, `hXSec_pz` | `L:` home `PHASE2-IMPLEMENTATION.md:35-36`, a tracked record that names them in words. |
| Q14 | B05-g-05 | "remains the leading, unconfirmed hypothesis" | This is the narrowed form's wording. "Of this analysis" restores the attribution (review F7). |
| Q15 | B07-g-03 | drops "the event-loop output files" | `L:` home `nd-unfolding/pet/P5B_LATERAL_SOURCE_DECISION.md`, whose audited branch list of the event-loop output tree names the three branches in words (the director's rule for code and record homes). "Stored" is restored (review). |
| Q17 | B09-g-11 | "Gaussian references" | The preceding sentence prints "(Gaussian reference …)". The added "descriptive" was removed. |
| Q22 | B11-g-08 | drops "hence the two color schemes" | ALLOW. Both scales are still stated in the caption, and the figure shows them. |
| Q23 | B11-g-01 | drops "(the battery of 2026-06-10)" | `R:` home `app_provenance.tex`. The date also prints in `app_negweight.tex`. |
| Q25 | B12-g-11 | guide drops "implemented but not yet run" and describes the protocol | ALLOW. The status prints in App. D's first paragraph (`N:`). The description matches App. D's equation and "OmniFold still uses the nominal response" (review B12–B15). |
| Q26 | B12-g-04 | label table rows cut | `R:`/`L:` homes, each checked by review B12–B15. The learner-backend labels (`lgbm`, `exact`, `hist`) stay as one prose sentence, because the registry cites them (review F1, re-pinned). |
| Q27 | B12-g-06 | "MAT's code supplies the per-band construction and the independent band sum, but no separate pair formula" | Review F2's fix. The next paragraph prints it: `CalcCovMx` and `GetTotalErrorMatrix`, with no N = 2 special case. |
| Q29 | B13-g-06 | ", which has not been shown (§…)" | A restatement of `sec_joint.tex:109` (review ruling). The requirement and the cross-reference wording are fixed (review F4, F5). |
| Q32 | B14-g-03 | drops the PET note's path and `\repolink` | `L:` home `README.md:8`. The repository link still prints on the title page (`N:`). |

<!-- absence-ok: quotes printed qualifiers and the raters' flags; not a claim that something has not been run -->
