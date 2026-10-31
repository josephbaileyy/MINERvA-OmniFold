# r22 paper pass 3: two-direction review (read-only)

Reviewer: an independent Claude session, 2026-10-31. Tree: the worktree at HEAD `078056564`. Base: `4121f185d60d`.
I diffed `docs/analysis-note/paper_body.tex` only. `sec_5d.tex` is unchanged since the base, so each note home below
already printed at the base. I read STEP2-PAPER.md §5–§6, `pass3/ledger.md`, REVIEW.md rows paper-g-02, -03 and -06,
`DECISION-20261031-joseph-chi2-table-option-b.md`, `sec_5d.tex` §9.4 (`sec:gbdt-model-dependence`, from
`main_note.aux:453`), and `values_fived16.tex`. I did not read the untracked `pass3/agy/` directory.

## Findings

### R3-1 (most serious). Line 271: "The second is the envelope of Sec.~\ref{sec:uncertainty-status}, which tracks the same bias and alone exceeds the precision target in two of the three tested reporting definitions."
- **Direction:** MOVED-AWAY. The sentence itself is unchanged, but its support was moved out from under it.
- **Base:** Sec. `uncertainty-status` stated the target ("Our precision target is a \SI{10}{\percent} median
  half-width for the total 68\% interval"), named the three definitions (the \jtNcells{} joint cells, the 39
  $(\Eavail,W)$ cells and the 27-cell partition), and said the envelope alone exceeds the target for two of them.
- **New:** Sec. `uncertainty-status` no longer defines a precision target, names no definitions, and gives no count
  ("three"). Line 271 still sends the reader there for "the precision target" and "two of the three".
- **Why:** The paper now uses "the precision target" without ever defining it. The cross-reference points to a section
  that no longer supports the claim. The ledger has no row for this sentence: it is r21 F337 (ORDINARY), so it may be
  reworded. The fact is true in the note: RD1 and RD3 exceed the target on the model component alone (`sec_5d.tex`
  §9.4).
- **Fix (reword):** point the claim at its note home, for example "…which tracks the same bias and, on its own, exceeds
  the study's precision target in two of the three reporting definitions it tested
  (\nsec{sec:gbdt-model-dependence})". Then add a ledger row with a `P::` probe of the new wording and the `N:` probe
  already used for P3-3. The other option is to restore the single definition sentence in Sec. `uncertainty-status`.
  That keeps the precision-target discussion in the paper, which the narrowed form allows but does not ask for.

### R3-2. Line 65 heading: "\subsection{Reporting definitions and the precision target}"
- **Direction:** AMBIGUOUS. This is the same root cause as R3-1.
- **Base and new:** the heading is unchanged. In the base, the body discussed the target. In the new text, the body
  only points to "its precision targets" in the note.
- **Why:** The heading promises content the subsection no longer contains. It also says "target" (singular) while the
  new pointer says "targets". Together with R3-1, a reader looking for the target finds nothing.
- **Fix (reword):** retitle the subsection to match what it now holds, for example "Reporting definitions and model
  dependence". The label `sec:uncertainty-status` is unchanged, so no reference breaks. If you take R3-1's restore
  option instead, the heading can stay.

### R3-3. Line 52: "The joint-test estimator keeps five iterations because the larger counts tested did not reduce its model dependence, measured as the largest residual proxy over the truth changes used in its development; the counts tested and their values are given in \nsec{sec:gbdt-model-dependence}."
- **Direction:** AMBIGUOUS, tending to overstate. It is within the narrowed form's wording ("larger tested counts").
- **Base:** "…because 10, 15, or 20 iterations did not reduce its model dependence, … The comparison and its values
  are given in …".
- **New:** "the larger counts tested" / "the counts tested and their values".
- **Why:**
  - The note's comparison is specific. Its rule compared only 10, 15 and 20 against 5, on J or H2: "it is 0.314 at
    five iterations and at least 0.384 at 10, 15 or 20".
  - The note also tested larger counts that the maximum-proxy measure is not reported for. D1 and W1 run to 40
    iterations, $q_3$ to 30 and W3 to 200, and "D1 and W1 improve slowly".
  - The paper's line 136 says the residual "persists over the tested iteration numbers". A reader can take "the larger
    counts tested" to mean that same wider set, which would extend "did not reduce its model dependence" to counts up
    to 200. The note does not state that.
  - "Their values" also attaches a value to each count. The note gives one lower bound (≥0.384, H2 only) and no J
    value. The base's "The comparison and its values" made no such claim.
  - F109's substance (the reason, the residual-proxy measure and the development-sample scope) is otherwise kept, and
    the counts print in the note (`sec_5d.tex` §9.4: "10, 15 or 20").
- **Fix (reword):** tie the counts to the comparison, for example "…because the larger counts in its iteration
  comparison did not reduce its model dependence, measured as …; the comparison, its counts and its values are given
  in \nsec{sec:gbdt-model-dependence}." This adds no number.

### R3-4. Line 68: "Over the reporting definitions of a five-observable measurement tested in the study, the envelope has a median of about 10--13\% per cell, …"
- **Direction:** AMBIGUOUS (an attachment is lost). Low severity.
- **Base:** "With the joint-test estimator, the envelope alone exceeds …; … the same estimator's envelope …; Over these
  definitions, the envelope has a median of about 10--13\% per cell …".
- **New:** the sentences that named the estimator are cut, so the 10–13% figure is no longer attached to the
  joint-test estimator. The paper uses two estimators (Table I).
- **Why:** The wording is accurate. The note's §9.4 heading is "Reporting definitions for a five-dimensional
  measurement", RD1–RD3, with medians of 12.0, 9.6 and 13.4%, "about 10--13\%". It also supports "The study and its
  precision targets are described in" (the total-width, model-component and recovery targets). The only loss is which
  estimator the size describes.
- **Fix (reword, optional):** "…tested in the study, the joint-test estimator's envelope has a median of about 10--13\%
  per cell…".

### R3-5. Lines 17: "… are reported for the sixteen-cell result in Secs.~\ref{sec:fd16} and~\ref{sec:gen16}. Interval coverage has not been validated. The findings are …"
- **Direction:** AMBIGUOUS (scope). Low severity.
- **Base:** "Interval coverage has not been validated." opened its own paragraph, ahead of the sixteen-cell sentence.
- **New:** it is the fourth of five sentences, directly after the sentence about the sixteen-cell result.
- **Why:**
  - The FROZEN sentence is verbatim, prints once, and keeps its unhedged strength.
  - The explanation of what the tests establish is kept verbatim ("They examine whether the unfolding gives reliable
    multidimensional cross sections …").
  - Placed after "reported for the sixteen-cell result", it can be read as limited to the sixteen-cell result. That
    would leave open whether "a coverage test" in the first sentence validated anything else. The base's position read
    as general.
  - The Limitations list (line 280) still states the lack of coverage for 2D, 3D/4D and the sixteen cells, so the
    paper as a whole loses nothing.
  - STEP2-PAPER.md §6 does not require this order.
- **Fix (reword, optional):** keep the paragraphs joined and put the FROZEN sentence directly after "…by
  generator-sized amounts." and before "The bias tests…". The sentence then follows the list that includes "a coverage
  test", keeps its general scope, and still sits in the integrated paragraph.
<!-- absence-ok: quotes the printed FROZEN sentence; not a claim that something has not been run -->

## Checked and clean

- **Table IV, rows:** each cell uses the base row's macro, unchanged (`g-<gen>-total-chi2int`, `-total-ndf`,
  `-shape_only-chi2int`, `-shape_only-ndf`, `label-<gen>`), split from "a/b" into two columns. The four "All 16 cells"
  rows have total ndf 16 and shape-only ndf 15. GiBUU has 8 and 7, which matches its "8-cell subset" label.
  `h2-mid-pz` is 4.5, which matches Joseph's "p∥ < 4.5 GeV/c". MINERvA Tune v1 moving above GiBUU follows the
  decision's grouping. No χ²/ndf ratio is printed.
- **Table IV, caption:** word for word Joseph's text, with the math typeset as in the base caption. The base's "against
  the sixteen-cell result" and the spelled-out "number of degrees of freedom" are replaced by Joseph's text. "ndf" is
  now never spelled out in the paper. This is within the decision, so it is no finding; Joseph may want to know.
- **Fig. 3 acceptance-failure qualification:** "an earlier purity-subtracted five-observable covariance that fails its
  specified acceptance criteria (\nsec{sec:eavailw-adopted})" (line 136) is byte-identical to the base.
- **Cut precision-target facts:** each prints in `sec_5d.tex` §9.4:
  - the target ("a median 68\% half-width of at most \SI{10}{\percent}");
  - none of the definitions meets it ("None of the three reporting definitions can meet these precision targets");
  - the model component alone exceeds it in RD1 (109 J) and RD3 (39 EW);
  - RD2 (27 H2, "not nested within J", median 9.6%) exceeds it once the flat 1.4% normalization is added.
- **The envelope's meaning:** "sensitivity diagnostic … not an interval" is kept verbatim.
- **Side note (rule doc, not the paper):** STEP2-PAPER.md §6 gives the note home of the failed target as Sec. 9.4
  "none of its reporting definitions (RD1-RD3) met a precision target". That quote prints in no note `.tex` source.
  The ledger's `N:` probes (P3-3) quote the current §9.4 text and do print. The section number 9.4 is right.

## Per change

1. Table IV (Option B): OK.
2. paper-g-03 (FROZEN): OK. Optional: R3-5, move the FROZEN sentence to just before "The bias tests…".
3. paper-g-02 (five iterations): fix R3-3. Tie "the larger counts tested" to the iteration comparison and make "their
   values" "the comparison, its counts and its values".
4. paper-g-06 (precision target): fix R3-1, the line-271 dangling "precision target" and "two of the three" reference.
   Add R3-2 (retitle the subsection) and, optionally, R3-4 (name the estimator).
