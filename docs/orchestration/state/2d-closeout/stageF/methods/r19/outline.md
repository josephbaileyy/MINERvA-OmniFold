# Register round r19, a structural round: outline in two variants (2026-10-27)

**Status:** an outline for the director's approval. Nothing in the paper or the note has been written.

**Base:**
- #413 at `00428d10`. `paper_body.tex` sha256 begins `b79837aa`, and `analysis-note/` is unchanged since `a55e2686`.
- Line numbers below are `paper_body.tex` at that base.

**Under:**
- `DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` (#431), item 3. Round 3 of at most 4 for the
  paper. Restructuring and reordering are in scope.
- `DECISION-20261025-joseph-register-rounds-paper-rewrite.md`: method, adoption and stop rules unchanged.
- R1–R10 and the KEEP list of `register-prd-study/REPORT.md`.
- The guardrail, protected text, and "no fact leaves both documents".

**Inputs:**
- the second scope review (`secondary-results/astra-consult-2-20261027/`, #432, main `6c21cafa`);
- the director's P1 re-score on the corrected rater copy: sol2 3, 3, 3 at 10,381 words. This is r19's P1 baseline.

## 0. What the variants decide, and what they do not

**MOVE versus SHORTEN.** Every **MOVE** in the scope review is Joseph's decision and has not been taken. A **SHORTEN**
moves detail to the note only where the note already prints it. That is a presentation change inside
DECISION-20261025, checked fact by fact by the ledger's MOVE→note rows.

**The variants:**
- **Variant A (joint tests stay, shortened):** the hybrid-null tests become one self-contained section, VI, after the
  result.
- **Variant B (joint tests move):** variant A without Sec. VI, plus the finite list of knock-on edits K1–K10 (§4).

  B is not a second design. Joseph's choice deletes one section and applies a fixed list, so it triggers no redesign.
  Both variants share §§1–3.
- **The review's other MOVE rows** are listed as O1–O6 (§5). Each is an independent keep-or-move item for Joseph.
  Each sits in a fixed slot of the shared outline, with the default "stays, shortened". None depends on A or B.

**Left unchanged in both variants:**
- the title and both abstracts (Joseph's);
- `\pubhold`, the acknowledgments, the AI statement, Data Availability and the release text;
- the four protected `values*.tex` / `app_*.tex` files;
- every number, claim, scope and figure meaning.

**The (c) sentences.** The 1A/3D limitation sentences print in Sec. I's limitations paragraph and in sec:gen16. r19
keeps them byte-identical, so (c) can land before or after r19 without a merge conflict in wording.

## 1. The shared order (both variants)

The corpus order is intro → experiment/data → simulation → selection → extraction → systematics → results →
comparisons → conclusions. The review's order differs only by putting validation with the uncertainties. Variant A has
7 sections and B has 6, both inside the corpus's 5–8.

**No existing label is removed in variant A.** Every `\ref` and the Data Availability's `Sec.~\ref{sec:central}` keep
resolving, so the protected source stays byte-identical. The printed numbers change.

**New labels:** `sec:cov16` (§1, IV A) and `tab:result16` (§2). See Q2.

| new | title (draft) | content, from today's location | treatment |
|---|---|---|---|
| I | Introduction | I ¶1 motivation (:14); ¶2 the contribution, sixteen-cell result first (:17); ¶3 the coverage/calibration distinction (:20), in A only (K1); the three-limitation ¶ (:23, the (c) sentences byte-identical); the scope ¶ in positive form (R1, :47); the roadmap (:50) | **Table I leaves Sec. I** (§3). Roadmap rewritten to the new order. |
| II | Data, simulation, and observables (`sec:data`) | II ¶1–5 (:55–76) | SHORTEN the convention checks (:67 the 135 MeV sensitivity, O6; :70 W redundancy anatomy; :73 nucleon-mass and axis checks), keeping the definitions, "simultaneous but not independent", and one carbon-versus-CH illustration. The coarse-grid ¶ (:76) stays in both variants, because Figs. 2b and 4 and the precision study use the coarse joint cells; in B it loses its test-domain clauses (K2). |
| III | Cross-section extraction (`sec:method`) | III ¶1–5 and Table II (:81–111); the precision study (:240–242, `sec:uncertainty-status`), shortened, as the reason for the reporting cells; the sixteen-cell definition (V F ¶1's first half, :266, up to "every reported cell passes the support rule") | The extraction ends with the cells the result is reported in. The validation-design ¶ (:114) moves to the head of IV. SHORTEN: the iteration choice (:95, the review's row "five versus 10, 15 or 20"). |
| IV | Uncertainties and validation (`sec:validation`) | **A** the reported covariance (V F ¶1's second half, :266, $C_{\mathrm{total}}+C_{\mathrm{resp}}$, $C_{\mathrm{model}}$, $C_{\mathrm{resp}}$'s scope; new `sec:cov16`); **B** the two-dimensional benchmark (IV A and IV B, :123–153, becomes one subsection with `sec:repro2d`, `sec:repro2d-pub` and `sec:uq2d` kept); **C** closure and background subtraction (`sec:closure`, Fig. 2); **D** generator-sized truth changes (`sec:departure`, Fig. 3), with the binned diagnostic (VI ¶2–3, Table III; O1) as its diagnosis; **E** coverage (`sec:coverage`, Fig. 4; O2, O4); **F** estimator stability (`sec:cov5d`, target T3); **G** the fake-data study on the sixteen cells (V F ¶2–3, Table IV, `tab:fd16`, target T2) | Validation of the measured product comes last, next to the result. SHORTEN per the review rows: the 2D benchmark's anatomy, the exact-split cross-check, the 2D budget, the superseded bands (O5), the 3D normalization, the two-dimensional closure, the deformation and coverage detail. **KEEP:** the run-period inconsistency and the rounding instability (review rows). SEC4-bound phrases stay byte-identical wherever their paragraph lands. |
| V | The sixteen-cell cross section (`sec:result16`, now a section) | **A** the result: a new compact table (§2) and the median-uncertainty sentence; **B** comparison with generator predictions (`sec:gen16`, Fig. 5, Table V, the flux-sensitivity ¶, byte-identical for (c)); **C** the three- and four-observable central values (`sec:central`, :326–329), shortened to the descriptive sentence and the note pointers | The result and its comparisons become adjacent. Today they are V F and VII B. |
| VI (A only) | Simulation-calibrated tests of generator predictions (`sec:joint`) | VII's lead ¶ (:320); VII C `sec:hypotheses`; VII D `sec:calibration` (target T1); VII E `sec:conditions`; VII F `sec:joint-results`, Table VI | Its own section, after the comparisons, as a separate inference product. Shortened in place under R4–R7. |
| VII (A) / VI (B) | Discussion and conclusions (`sec:conclusions`) | VI ¶1 (:304, the three results pointing to the prior), shortened; VI ¶4, the checklist (:314), as one sentence (review row "general checklist"); VIII (:454–464) with `sec:limitations` kept as one paragraph | `sec:limits` (today's Sec. VI title) is absorbed. Its label moves to the Discussion paragraph that carries the synthesis, so its refs resolve. |

## 2. The new result table (presentation only)

- **`tab:result16`:** cell, the five box edges, the cell integral $f$ in $10^{-40}$ cm²/nucleon, and the relative σ (%)
  under $C_{\mathrm{total}}+C_{\mathrm{resp}}$. The note's `tab:fived16-cells` has the same columns, plus the
  $C_{\mathrm{total}}$ and $C_{\mathrm{resp}}$ columns (see Q5).
- **Every entry is an existing `\fvval` key** (`box-Rxx-*`, `f-Rxx`, `f-unit`, `sig-C_total_resp-Rxx`).
  `make_values_fived16.py` already pins `fd_data_product.json` by sha256 `b79556f0` and asserts its cells, boxes and
  $f$ against S1 (`make_values_fived16.py:36`, `:88–92`). The table adds no key and no number that is not already
  printed in the note.
- **The covariance and correlation matrix** stay in the note, with a pointer. Whether the vector and covariance ship as
  supplemental data is **Q8, Joseph's**. The table does not presuppose it.

## 3. Table I

**My recommendation is to fold it into the text, not to keep a table.**
- No corpus paper has a findings table.
- R2 forbids a third statement of the same limitation, and a "validation and limitations" table beside the result
  would be one: the table, the sentence and the conclusions.
- **What folding means:**
  - Table I and its caption go.
  - Each of its nine rows already prints in its section, and the ledger probes each row's fact there.
  - The Introduction's contribution paragraph (:17) names the sixteen-cell result first. The three-limitation paragraph
    (:23) carries its fake-data assessment and its flux-correlation sensitivity, so **the sixteen-cell result's "row"
    is the Introduction's own lead**. This is the content the review says Table I lacks.
  - The roadmap (:50) and the conclusions (:454) stop citing `tab:findings`.
  - The fourth Sec. I paragraph's "Table~\ref{tab:findings} lists each finding with its test" goes.
- **The alternative (Q1):** a compact table at the end of IV, "Validation of the sixteen-cell result", with the
  sixteen-cell row first (median 7.29%; fake-data: listed at three of twelve graded truths; flux sensitivity 24–48%),
  then the benchmark, closure, truth-change, coverage, stability and precision rows. It has no limitations column, and
  every entry is a `\fvval` or an existing value. In B, the hybrid-null row goes.
- **Checks:** no gate reads Table I's text: none of SEC4's ten `paper_body.tex` patterns, and neither registry alias row (:92, :106). `fived16/scope-sites.tsv` rows 147–151 cite Table I rows; they are this
  lane's audit inventory, and I will update them.

## 4. Variant B: the knock-on list

These are the only edits B makes beyond deleting Sec. VI.

| # | site (today) | edit in B |
|---|---|---|
| K1 | I ¶3, the calibration sentences (:20, from "Two properties must be distinguished") | drop the calibration half and keep the coverage definition. Both print in the note. P02 (:20 first sentences) is rewritten with I in either variant; r19's agy pass then covers ruling 3's read. |
| K2 | II ¶5 (:76) | keep the fine and coarse grids and the support rule; the GiBUU test domain sentence goes with VI |
| K3 | II ¶4 (:73) "which the tests of Sec.~\ref{sec:joint} do not correct" | becomes "which these comparisons do not correct" |
| K4 | I scope ¶ (:47), the hybrid-null sentences | replaced by the review's neutral pointer: "The companion note presents a separate simulation-calibrated testing application and its assumptions." |
| K5 | III ¶5 and Table II's "Used for" cell (:92, :107) | "and the joint tests" and "generator tests" become a pointer to the note. The registry alias rows cite :92 and :106, so they are re-cited with `--cite`. |
| K6 | the precision study's ¶2 (:242) "motivates the different route to inference of Sec.~\ref{sec:joint}" | points to the note's joint-test section |
| K7 | IV G, the fake-data truths (:269) "the five hybrid truths of the generator tests of Sec.~\ref{sec:joint}" | "five hybrid truths, each a prediction on the fine grid" (definition kept, with a note pointer) |
| K8 | VI ¶1's third result (:304, the null displacement) | moves with VI. The synthesis keeps two results plus the miscoverage sentence. |
| K9 | the conclusions (:454) and the Limitations ¶ (:464), last three sentences | the hybrid-null limitations go with VI; a one-clause pointer remains |
| K10 | the Fig. 2(b), Fig. 4 and Table III captions, "coarse joint cells" | unchanged; the grid stays defined in II |

**Facts that leave the paper in B** (about 2,000 source words: VII's lead, C–F and Table VI) must each print in the note.
- **The check:** before any B writing, a scripted ledger pass gives each moved fact an `N:` probe into `sec_joint*.tex`
  or the appendices.
- **A paper-only fact** (one candidate is :320's "We have not compared their power with that of a reconstruction-level
  test") is listed and comes back to you as a proposed note addition. I do not edit the note silently.

**Protected text that B makes stale.** It can't be edited in r19 and goes to Joseph in (d):
- the abstract's last sentence ("simulation-calibrated tests … all reject"). The review recommends removing it.
- Data Availability's "every p value, decision … of the joint tests".
- the title's "Performance and limitations" (T0–T3 are already in the packet).

## 5. The review's other MOVE rows: O1–O6, each independent, default "stays, shortened"

| # | review row | slot in the shared outline | if Joseph moves it |
|---|---|---|---|
| O1 | the exact binned diagnostic (VI ¶2–3, Table III) | IV D, as the residual's diagnosis | IV D keeps one sentence and a note pointer; Table III goes |
| O2 | the Gaussian bias-and-spread diagnosis (:185) | IV E, one sentence | the sentence goes; the result sentence stays |
| O3 | the iteration and capacity diagnosis (:177, "We interpret the residual … without reducing it") | IV D | **Constraint:** SEC4 binds the next sentence (":177 it is \SIrange … in the most affected"), not this one, so the move is mechanical. |
| O4 | Fig. 4 and the coverage counts | IV E | the warning sentence stays (KEEP, R4 form); the figure goes |
| O5 | the superseded 2D bands (:146, last sentence) | IV B | already one pointer sentence; MOVE leaves it as is |
| O6 | the 135 MeV sensitivity (:67, "Replacing it … 1.05%") | II | the definition stays; the sensitivity sentence goes |

The pion-FSI/Valencia/published low-recoil comparisons and the earlier purity-subtracted map are already
pointer-only (:326, :329). The review's MOVE there endorses what prints, so they are not items.

## 6. Targets: the passages the P1 raters quote

| # | passage | runs | plan |
|---|---|---|---|
| T1 | VII D (:389): design, budget extension, lost pseudo-experiments | 3 of 3, twice | **A:** two or three sentences, in R4 form, keeping facts [1]–[4] as in r18 S2 (budget extended after p values were visible; error control holds for any stopping rule; \jtLostCal/\jtLostPow lost, decisions use the completed ones; A2's independence of loss not shown), plus the recomputation; the mechanics already print in the note (`sec:joint5d-frozen`, `sec:joint5d-lost`). **B:** moves. |
| T2 | V F ¶2 (:269): "A truth from a generator that contributes to $C_{\mathrm{model}}$ … \fvval{f0b-nungraded} further truths are ungraded … These are not held-out truths." | 3 of 3, twice | R9, definition before claim: define the truth set, then the grading rule (the Cov. column names each reduced-covariance entry), then the listing criterion. "Not held out" is stated once, as a property of the set (KEEP: it must stay). The 1A held-out test lands here in (c); the rewrite leaves a slot for it. |
| T3 | IV F (:234): the rounding instability | 2 of 3, twice | R4: what was varied, the criterion (0.3 median, 1.0 maximum), the outcome (2.6; the development variant 2.5), then the consequence ("inside the data-bootstrap statistical uncertainty; it limits how exactly the central values can be reproduced"). **KEEP** per the review. The review also asks whether the final uncertainty accounts for it; see Q4. |
| T4 | VII's lead (:320), "Unfolded results can be compared with any prediction at truth level …" (1 of 3; the director's note placed it in Sec. I, but it prints at the head of Sec. VII) | 1 of 3 | **A:** split under R10; its first half moves to V B's lead, where the comparison now is. **B:** the first half moves to V B and the rest goes with VI. |

## 7. Method (DECISION-20261025, unchanged)

1. **Step 0, a mechanical reorder:**
   - a script moves source blocks verbatim to the order of §1, with no wording change;
   - **check:** the printed text's word multiset is unchanged apart from headings, and the fived16 ledger and SEC4 pass;
   - built and committed alone, so every later diff is a wording diff.
2. **Writer batches**, sequential because it is one file. Each has a ledger with a planted bad probe, and MOVE→note rows
   with `N:` probes:
   - **b1:** I–III, with Table I folded;
   - **b2:** IV;
   - **b3:** V, and VI in A;
   - **b4:** Discussion.
3. **An independent two-direction review per batch,** with agy agreeing on every printed passage, P02 included.
4. **Gates:**
   - SEC4 and its self-test;
   - the registry re-cite of the alias rows at :92 and :106;
   - swallowed-text, reflow and absence-claims;
   - a full build;
   - the fived16 ledger, whose probes on rewritten sentences are re-pointed in the same commit.
5. **Measure:**
   - the rater copy from `make_rater_copy.sh` with case 4 (§6 of the fived16 handoff);
   - pairwise against the 00428d10 copy in both orders with both models;
   - P1 sol2 ×3.
   - **Adoption:** at least 3 of 4, no sol2 order flip, and P1 not below 3, 3, 3.
6. **The variant built first:** A, because B is A minus a section. If Joseph rules before b3, B is built instead and A
   is not scored. If he rules after, A is scored and B follows as a deletion with its K-list. Its own pairwise check
   against A then confirms the deletion did not lower the score.

**Estimated length** (blinded words, against 10,381):
- **A:** about 9,300–9,700;
- **B:** about 7,600–8,100. The review estimated 7,000–8,000.

These are estimates, not counts.

## 8. Outside r19

**The note's inconsistency, flagged, not fixed.**
- The note's abstract (`main_note.tex:72`): "Its principal result is a cross section in five observables".
- `sec_execsummary.tex:6`: "The main results are the validation findings."
- `sec_summary.tex:4` says the same, a second site.

I propose it goes to the **n4** note round, because r19's measure is the paper's rater copy. It goes to Joseph in (d)
as a flagged item. Both sites are named, so a fix reaches both.

## Questions for the director

1. **Q1, Table I:** fold it into the text (my recommendation), or the compact validation table at the end of IV.
2. **Q2, the binding rule** "no label, section or subsection changes" (register-method step 3). Does #431's
   "restructuring" waive its section and subsection part for r19? r19 removes no label in A and adds `sec:cov16` and
   `tab:result16`. In B, VI's seven labels (`sec:joint`, `sec:hypotheses`, `sec:calibration`, `sec:conditions`, `sec:response`,
   `sec:joint-results`, `tab:joint`) go, and their in-paper refs become `\nsec` pointers.
3. **Q3:** O1–O6 go to Joseph as independent items with the default "stays, shortened". Or bundle them with B?
4. **Q4:** the review asks whether the final uncertainty accounts for the rounding instability. I print an answer only
   if the note already prints one. Otherwise it would be a new claim, so I propose to add nothing.
5. **Q5:** the result table carries the reported σ only (my recommendation, the review's "compact"), or all three σ
   columns as in the note.
6. **Q6:** the note inconsistency to n4 (my recommendation), or into r19's scope.

## The director's rulings (2026-10-27, after 12a65d89)

**Approved.** Start with step 0, then b1. Variant A is built first. The director puts B and O1–O6 to Joseph.

1. **Q1, Table I: fold it into the text.**
   - Each of the nine rows' facts gets a ledger probe where it prints.
   - The sixteen-cell result's "row" is carried by Sec. I's lead and the limitations paragraph.
   - `fived16/scope-sites.tsv` rows 147–151 are updated in the same commit.
2. **Q2, the section and subsection part of register-method HANDOFF step 3 is superseded for r19.**
   - It is superseded by DECISION-20261025 item 1 and #431 item 3; a decision record outranks a handoff.
   - The label part stays, narrowed:
     - A removes no label and adds `sec:cov16` and `tab:result16`;
     - in B only VI's seven labels go, each in-paper `\ref` becoming an `\nsec` pointer;
     - in both, no unresolved reference, and every xr pointer into the note resolves.
   - The note's text and label numbers are unchanged.
   - **The grep** (all 28 files `main_note.tex` inputs, comments stripped):
     - `main_note.tex` has no `\externaldocument`, so the note cannot `\ref` a paper label;
     - no note `\ref` names a label defined only in the paper. Five label names exist in both documents
       (`sec:closure`, `sec:coverage`, `sec:intro`, `sec:method`, `sec:validation`), and each resolves inside its own
       document;
     - every hard-coded "Sec./Table/Fig. N" in the note cites the published measurement (Ref. MINERvA:2021owq),
       **except one: `app_release.tex:29`, "for the article's Figs.~1--3"** (protected text). In both variants,
       Figs. 1–3 stay `fig:validation`, `fig:bkg-residual` and `fig:deformation`, in that order, and each step checks
       the figure order from `main_paper.aux`.
3. **Q3:** O1–O6 go to Joseph as independent items, each defaulting to "stays, shortened". They are not bundled with B.
4. **Q4: add nothing new.**
   - T3's consequence clause prints only where each half is already printed text in the paper or the note,
     ledger-probed with its site. Otherwise that half is dropped.
   - Whether the final uncertainty accounts for the rounding instability goes to Joseph in (d) as an open item.
5. **Q5: one σ column** ($C_{\mathrm{total}}+C_{\mathrm{resp}}$), with a pointer to the note's `tab:fived16-cells` for
   the split.
6. **Q6: to n4.** The two sites, `sec_execsummary.tex:6` and `sec_summary.tex:4`, are named, with `main_note.tex:72`
   beside them, and flagged in (d).
7. **T2.** A Cov. column added to Table IV would be presentation only if every entry came from `fd_f0b_readout.json`.
   (Table IV already has a "Cov." column, at `paper_body.tex:279`, so none is added.)
8. **Step 0's commit message** gives the word-multiset result and the gate outcomes.
9. **The protected text that B makes stale** goes to Joseph in (d), unedited: the abstract's "all reject", Data
   Availability's "of the joint tests", and the title.

**Added by the lane in step 0, for the director's information:**
- one more label, `sec:fd16`, on IV G (the fake-data study). Without it, the refs that point the reader to the
  fake-data tests (`:23`, `:177`, `:335`, `:464`, today `\ref{sec:result16}`) would land on the result section V,
  once `sec:result16` labels that section. It removes nothing.
- the FIVED16 markers: `fived16/check_ledger.py` rule 7 forbids hand-typed numerals between them, so every piece of a
  FIVED16 block that moves keeps a BEGIN/END pair.
