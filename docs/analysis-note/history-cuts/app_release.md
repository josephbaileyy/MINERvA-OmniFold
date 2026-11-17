# History restructure, App. G (app_release.tex): cut log

**Authority:** DECISION-20261113-joseph-note-n4-n5-role.md, addendum adopting the history rule and structure
(`ead7e3c22`); the release appendix is the referee's section diagnosis and item 10. Scope is App. G only.

**Rule:** history stays in the note only if removing it would change a reader's understanding of the reported
object, its reproducibility, its evidential independence or its limitations. Other history goes to the ledger,
with a pointer. Each timing statement names its object; method uses of "declared" become "specified".

**Base:** `6b9b5be5c678428f5c15403c1ff84a91a5ae3674:docs/analysis-note/app_release.tex`.
All line numbers below refer to that base. Owner: the Appendix G editor; meaning review: a fresh, read-only
codex-school2 exec using the committed two-question prompt. Terminal condition: one documented edit with no
lost reproduction limit, provenance gap or after-results disclosure, a passing meaning read and the note build
and build tests. Review budget: one read, with at most one repair/read if it finds a material problem; no new
scientific computation. The standalone mirror is outside this edit's scope.

## Changes

| id | base file:line | old text | new text or cut | class and ledger home |
|---|---|---|---|---|
| G1 | `app_release.tex:52` | "An earlier version of the package, RC1, was replayed from an empty directory by a separate AI agent session (Opus~5.5) that had no access to the repository and used only the package and its README; its verifier passed." | cut; the rest of the paragraph is unchanged | LEDGER: this exact base sentence at `6b9b5be5c678428f5c15403c1ff84a91a5ae3674:docs/analysis-note/app_release.tex:52`, and `docs/publication/release/RC1-REPLAY-RECEIPT-20261006.md:11-25`. The receipt records REPLAY PASS WITH DEFECTS and distinguishes the tested package from the README-only successor. Neither is RC7. RC7's own verifier and its limits remain at :9 and :37. The source comment at :51, solely supporting the removed sentence, is also cut; the source-only pointer at :13 changes from "below" to this cut log. |
| G2 | `app_release.tex:68` | "the declared centering variant" | "the specified centering variant" | NEEDED method identity, kept: base :68; `app_release_records.tex:14-24` names the cv variant and non-interchangeable mean-centered sibling. No timing claim is added. |
| G3 | `app_release.tex:69` | "bins where the inflation denominator vanished and $g$ was declared $1$" | "bins where the inflation denominator vanished and $g$ was specified as $1$" | NEEDED pinned-mask definition, kept: base :69; `app_release_records.tex:61` states the pinned-bin convention. No number or timing claim changes. |
| G4 | `app_release.tex:102` | "without a declared regularization" | "without a specified regularization" | NEEDED inverse limitation, kept: base :100-102; `app_release_records.tex:65` describes the cutoff dependence. The regularization requirement and every following qualification are unchanged. |
| G5 | `app_release.tex:105` | heading "Undeclared acceptance field." | heading "Unspecified acceptance field." | NEEDED provenance gap, kept: base :105. The literal metadata `acceptance_question: UNDECLARED`, the undecided acceptance correction at build time, and the requirement to carry the field all stay verbatim. The metadata value is not editorial prose and is not renamed. |

## Material retained

- RC7's version, local/not-deposited status, verified replay capabilities, tolerances, figure-production check and
  the unrecomputed rounding-jitter statistic remain unchanged. No RC7 independent replay is asserted. The note
  still distinguishes RC7's exact-split curve from the refined LightGBM validation figure.
- Every exclusion at base :52 stays: archived-product extraction, event-level unfolding, closure/bias
  measurements, covariance-status measurements, 2D uncertainty/coverage, low-recoil comparisons,
  recoil-response sensitivity and proxy convergence rate. The multiplier scan remains outside RC7's own
  verification, and the event-processing input requirements stay.
- The input inventory and its checksum-versus-preservation distinction, the missing simulation preservation
  copies, lack of a public deposit, and missing producing-code/job metadata remain unchanged.
- The AUD-N4 planned-package paragraph (:44), AUD-N5 preservation paragraph (:57), and all of ISSUES.md
  (including OPEN AUD-N5a) remain byte-identical to the base. This pass does not supply the missing citable
  preservation record, authorize a deposit or change the release schema.
- `app_release_records.tex` is a separately built internal records document, not App. G's posted text. It is
  unchanged; its verbatim-move integrity contract is preserved. Its excerpts support method identities here,
  but no record is promoted into a new result or provenance claim.

## Disclosure and value checks

No disclosure of a choice made after results were seen is removed. The removed RC1 sentence describes only
an earlier candidate's replay; its independence is not transferred to RC7. The meaning reader is also asked
to check this explicitly.

An exact edit check requires the new file to equal the base after removing G1 and its source-only comment,
retargeting the source-only RC1 pointer to this log, and making only G2-G5's replacements. All scientific numeric literals, reference targets, value macros and
`fvval` keys remain unchanged. The only numeric text removed with G1 identifies the superseded candidate
(RC1) and its historical reader (Opus 5.5); these identities remain above and in the original receipt.

Meaning-read artifacts: `history-cuts/reads/app_release-prompt.txt` (verbatim common prompt),
`app_release-records.txt` (attached record excerpts), and `app_release-pass1.txt` (fresh reader's answer).
Old and new sections were supplied as separate files; the old section remains recoverable at the base commit.

**Meaning read:** fresh codex-school2 exec, gpt-6.1-sol, high reasoning, read-only; session
`01a1d9dd-d160-7a93-91e2-985714f888a6`. G1-G5 PASS; G1 LEDGER, G2-G5 NEEDED and retained;
no needed item or after-results disclosure lost. OVERALL PASS, no failures. After the read, only the
unprinted RC1 source-pointer comment was retargeted from "below" to this cut log; the reviewed printed text
is unchanged. No App. I row is proposed.

## Proposed Development-history appendix rows (for the section owner)

None. G1 is superseded package-testing history that the adopted referee rule sends to the ledger, not a
configuration or test whose change affects a released result. G2-G5 retain method identities and limitations
in App. G. `app_devhistory.tex` is not edited.
