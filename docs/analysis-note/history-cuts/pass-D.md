# Stale references and process words (item D of the director's plan, 2026-11-15): cut log

**Under** the director's approval of the style-recheck plan, item D. The recheck is
`note-style-recheck-6c38249bcf5c.md` §3 ("Coherence and surviving references") and §4 ("Remaining process
vocabulary"). B.1's title "declarations" stays (the director's ruling), so the noun forms on pp. 8, 22, 105, 112, 119
and 120 are not changed.

**Base:** each file at `bb8e03b20f47cfc09f9bb23904d79cb4381f684b`, line numbers the base's. Line counts are
unchanged in every file. Each removed text stays at the base sha and line, its ledger home.

| id | site | old | new | support |
|---|---|---|---|---|
| Q1 | sec_validation.tex:128, §5.1 "Deformation" | "(\S\ref{sec:coverage-5d}, response-information diagnostic)" | "(\S\ref{sec:val-departure}, comparison with exact binned unfolding)" | The pointer was written at f63cec226 (2026-10-12), when sec_5d.tex held "A scoped response-information diagnostic" (f63cec226:sec_5d.tex:353–362: binned exact-response inversions, "Of the 144, 121 … weakly constrained"). That study now prints as "Comparison with exact binned unfolding" at sec_5d.tex:84–90 (sec:val-departure), with the same 144 and 121. |
| Q2 | app_guide.tex:10 | "and the two universe sweeps (\S\ref{sec:uq-2d-construction})" | "and the universe sweeps of the quoted universe block (\S\ref{sec:uq-universes}) and of the earlier 2D budget (\S\ref{sec:uq-2d-scope})" | sec_systematics.tex:12 (the July sweep, sec:uq-universes) and :282 (the earlier budget's sweep, sec:uq-2d-scope). The earlier sweep's label "the May sweep" left the note in S6 (history-cuts/sec_systematics.md). |
| Q3 | app_guide.tex:14 | "; the earlier MAT check without the normalization band (\S\ref{sec:minerva}) used the option \texttt{-{}-add-norm 0}" | cut | The recheck's item 8: the check's account left §A.2.6. Search: `grep -n -i 'without the normali[sz]ation\|add-norm\|norm band\|MAT check' app_statmethods*.tex sec_*.tex` (comments excluded) finds nothing @ bb8e03b20. |
| Q4 | app_statmethods.tex:5, :625, :639 | "\S\ref{sec:val-other}" (three pointers to the same-ensemble pull diagnostic) | "\S\ref{sec:pull-diagnostic}" | The diagnostic moved verbatim to app_statmethods.tex:646 (sec:pull-diagnostic) in the history restructure (history-cuts/sec_validation.md V2); sec_validation.tex:230 holds only a pointer to it. Not changed: app_provenance.tex:34 (the records document's index, `coverage-toys` "& \S\ref{sec:val-other}"), which check_note_records.py holds to its moved text; left for the director. |
| Q5 | sec_5d.tex:237, §9.5 | "It failed its futility criterion," | "The end-to-end test failed its futility criterion," | the paragraph's subject, "An end-to-end independent-truth test", :237 |
| Q6a | main_note.tex:83 (p. 1) | "The declared coverage test of the sixteen-cell result did not run to a result" | "The coverage test of the sixteen-cell result, specified before it ran, did not run to a result" | the same object and words as sec_5d.tex:237, read with records as F3 (history-cuts/sec_5d.md, pass 3) |
| Q6b | selection_features.tex:13 (Table 3) | "as declared for each cross-check" | "as specified for each cross-check" | a method use: no timing |
| Q6c | selection_features.tex:17 (Table 3) | "Declared sample population" | "Specified sample population" | a method use: no timing |
| Q6d | sec_results.tex:136 (§6.4) | "A benchmark declared before it ran" | "A benchmark specified before it ran" | the timing object is unchanged |
| Q7 | main_note.tex:81 (p. 1) | "beyond a stability requirement fixed in advance." | "beyond the criterion of a data-stability test, set before the test was run." | sec_5d.tex:96–99: configuration (e) "fails the data-stability test, whose criterion was set before it was run" (at most 2.6, \lrval{stab-max}) |
| Q8 | sec_fived16.tex:244 (p. 80) | "The other control checks (numbers \fvval{f0b-controls-passed}) passed." | "The other eight control checks passed." Source as a trailing comment on the line: fv@f0b-controls-passed = "0, 1, 2, 3, 4, 5, 6, 8" (values_fived16.tex:1574), eight entries. | the failed offset check and its consequence for the six power alternatives are unchanged |
| Q9 | sec_fived16.tex:283 (p. 81) | "…ended without a coverage result: its first stage stopped under a fail-closed rule fixed before that stage ran. That rule stops the stage if any specified draw makes a cell of the drawn natures' composite denominator non-positive. In a cell, that denominator is the first drawn universe's denominator plus each later universe's departure from the central-value denominator, and a cell that is positive at the central value and non-positive in the sum is the failure. N of the M specified draws failed, with at most K such cells in a draw. … The stop concerns the specified composition of the natures, not the estimator's coverage, …" | "…ended without a coverage result. Each of its pseudo-experiments is drawn from a simulated world built from randomly drawn systematic universes; in each cell, that world's denominator is the first drawn universe's denominator plus each later universe's departure from the central-value denominator. A rule fixed before the first stage ran stops that stage if any draw gives a non-positive denominator in a cell that is positive at the central value. N of the M draws did so, with at most K such cells in a draw, and the first stage stopped. … The stop concerns how the drawn universes were combined, not the estimator's coverage, …" | FD-1B-STAGED-DECLARATION.md §4.2 ("One toy is one nature, drawn …", the groups table :184–193); FD-1B-STAGED-AMENDMENT-1.md:195 (the denominator composes per cell); FD-1B-STAGED-AMENDMENT-2.md @ b3f27fab §1 (:40–43: "a_D = a_{u₁} + Σ_{j≥2} (a_{u_j} − a_CV) … for the denominator per cell"; "a cell with d_CV > 0 and d_D ≤ 0 refuses … as a STOP in the receipt (§2b)") and :222 (the STOP); OUTCOME-20261106-1b-stage1-receipt-stop.md :27–31 (892 of 900, max_cells 62) and :70–74 |

**Not in the plan, left:** sec_fived16.tex:182 (p. 76, "fixed in advance" for the inverted dimension), and the
recheck's p. 135 and p. 137 items (App. G, for Joseph, and E's UNDECLARED note).

**Numbers and keys:** numdiff on each base and new file, comments stripped:
- Removed: app_guide's "0" (Q3's `--add-norm 0`); the macro `\fvval{f0b-controls-passed}` (Q8).
- Added: app_guide's "2" (Q2's "2D").
- Nothing else in any file.

## Meaning read (codex-school gpt-6.1-sol, high, read-only; the body passages and records attached)

- **Pass 1:** OVERALL FAIL on Q6b, Q6c and Q9. All other rows passed, and every removed item was LEDGER or NEEDED and retained.
  - Q6b and Q6c: under the general definition "declared = specified before the run", the table cells lose a timing.
  - Q9: the denominator formula and the "positive at the central value" condition were not in the attached records (both were carried over from the base wording). reads/pass-D-pass1.txt.
- **Pass 2:** OVERALL PASS, with no FAILs. reads/pass-D-pass2.txt.
  - Q9 was read with FD-1B-STAGED-AMENDMENT-2.md @ b3f27fab §1 and :222, the amendment in force, which states both.
  - Q6b and Q6c were read under the director's classification as method uses (item D: "Table 3 (×2) … → 'specified'"). The reader: "the old word's before-run implication disappears, but no reader-needed timing loss is established here". That residual is reported to the director.

## F: layout (the recheck's "Visible presentation problems")

| id | site | change | check |
|---|---|---|---|
| F1 | sec_joint.tex:69–90, Table 29's flowchart (`picture`) | Box heights raised to fit their `\scriptsize` lines (source box 30→38, unfold 24→30, added-terms 24→38, Holm 23→26 pt), coordinates recomputed, picture 176→207 pt tall. The feedback line's ends moved with the boxes. Same text, same lines. | Rendered p. 92 at 140 dpi: every label lies inside its box, and no arrow crosses text. |
| F2 | app_statmethods.tex:605, :628, "Sources of the 2D comparison numbers" | `tabular{@{}lll@{}}` → `tabularx{\textwidth}` with a wrapped first column (0.27 text width) and a wrapped `X` procedure column. | main_note.log: the 229.2 pt overfull box (lines 605–629) is gone; the widest left is 26.9 pt (lines 110–125, not in this item). Rendered p. 118: the table fits the text width. |
| F3 | Table 38 (App. I) | Done in the App. I pass (history-cuts/app_devhistory.md, Layout). | — |

## The director's rulings on D's leftovers, 2026-11-15 (rows Q10–Q13)

Base: each file at `c23305268498c325a0115de91c0f0714d3f5cdef`, before the merge of main a06eeb85c (which touches none
of these files).

| id | site | old | new | support |
|---|---|---|---|---|
| Q10 | app_provenance.tex:34 (records document, App. G index) | "`coverage-toys` & \S\ref{sec:val-other}" | "… & \S\ref{sec:pull-diagnostic}" | as Q4. P5 holds the table paragraph by digest, so the change is recorded as R-EDIT-2 in records-move-ledger.md (old 8f74f07a…, new 06002545…), the checker's own mechanism for a pointer-only edit; check_note_records.py itself is unchanged. `probe records-inventory-base.json .` gives the same 14 failures with and without this edit (all present at HEAD, none from it; reported to the director). |
| Q11 | sec_fived16.tex:182 (p. 76) | "the inverted dimension $p$ equals the number of cells and is fixed in advance" | unchanged | Ruling (A): a property of the construction. Every χ² inverts the full covariance by Cholesky without truncation, so p is the cell count and no data-dependent choice sets it. No timing object is claimed. |
| Q12 | sec_pet_campaigns.tex:27, :38 | "its declared ten-iteration operating point"; "at the declared packing" | "its specified ten-iteration operating point"; "at the specified packing" | the director: method uses |
| Q13 (E) | app_release.tex:104 | "…carries \texttt{acceptance\_question: UNDECLARED}: when the projection was built, it had not been decided whether an acceptance correction is needed at the destination binning. The package must carry this field with its value until that is decided, so that no default in the data format makes that scientific choice." | "…carries \texttt{acceptance\_question: UNDECLARED}. The field is stored metadata of the product, written when the projection was built. At that time it had not been decided whether an acceptance correction is needed at the destination binning. The note applies none: \S\ref{sec:eavailw-adopted} states that no separate acceptance weight at the destination binning was specified and that none is applied to Fig.~\ref{fig:eavailWexcess}. Whether one is needed remains the open question the field records. The package must carry the field with its stored value until that is decided, so that no default in the data format answers that question." (pass 1 of the read failed a first wording that added "and no later record decides it", beyond a one-snapshot search, and "The package carries", which weakened the requirement; both are corrected) | the director's approval of E. docs/orchestration/state/PROJ-20260920-m1-publication-receipt.json `acceptance_question: UNDECLARED`; sec_5d.tex:340. Search for a deciding record: `git grep -l -i 'acceptance_question\|acceptance question' -- 'docs/orchestration/DECISION-*' 'docs/orchestration/AUTHORIZATION-*' 'docs/orchestration/**/DECISION-*'` finds nothing @ c23305268. Open item: PLAN-scalar5d-reportable-uncertainties-and-inference.md:664. §9.6's double-correction reason is deliberately not carried, so the field does not read as answered. |

numdiff on each of the four files: none removed, none added. Line counts unchanged.

**Meaning read of Q10–Q13 (codex-school gpt-6.1-sol, high, read-only):** pass 1 FAIL on Q13 only (an absence claim beyond its search, and a weakened retention requirement); pass 2, Q13 corrected, OVERALL PASS with no FAILs and no NEEDED item lost. reads/pass-D-rulings-pass1.txt, -pass2.txt.
