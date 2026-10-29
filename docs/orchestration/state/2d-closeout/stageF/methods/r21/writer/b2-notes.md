# b2 notes (Sec. IV, Uncertainties and validation): choices a reviewer should know

Revised after the reviewer's ADOPT-AFTER-FIXES verdict. The fixes are listed at the end. One fix could not be
applied as asked, because an atom forbids it.

## Order, merges and float placement

- The paragraphs follow the outline in every subsection. In IV H ¶3, the outline order F286, F287, F288 is restored
  (reviewer).
- IV A is one paragraph.
- **Float placement:**
  - Fig. 1 follows IV B ¶2.
  - Fig. 2 closes IV D.
  - Fig. 3 sits between IV E ¶1 and ¶2.
  - Table II follows IV H ¶1.
- **Float matter:**
  - Each figure has `\centering`, because the base text of F165, F215 and F235 shows it.
  - In each table, the lines between `\label` and `\begin{tabular}` are carried from the base at assembly (director).
    `\caption` and `\label` stay where the ledger has them.
- `\label{sec:repro2d-pub}` directly follows `\label{sec:repro2d}` (F152 base text). `sec:cov5d` keeps its
  mismatched name.

## Text that no atom gives (please check)

- **Comparators in the listing rule.** F269 and the Table II caption (F273) split their atoms around the
  absolute-value bars. I filled the gaps as "when a cell has $|z|>\fvval{trig-z}$" and "the cells with
  $|z|>\fvval{trig-z}$". F278's "no cell beyond" agrees, but the ledger does not show the comparator.
- **F284.** "with $|z|\leq\fvval{f1-zmax-ceil}$ in every cell ...". This is the form the paper-protections probe
  expects.
- **Table II caption opener.** "Fake-data tests on the sixteen cells: $\chi^2$ ...". The colon is mine.
- **F275.** "the listed truths are the GiBUU $\Eavail$ shape ..., the GiBUU hybrid truth ..., and the synthetic
  $q_3$ tilt ...". I did not write their count, because no atom holds it.
- **F191.** "in the combined result" is attached to "includes this inconsistency". If the reviewer meant it to
  qualify the 2.0%, move it there.
- **Openers for atoms that begin lowercase:**
  - F137 is joined to F136 with ", and".
  - F146 is joined to F145.
  - F277 opens "Thus the reported uncertainty ...".
  - F138's last atom opens "Throughout, the prior used to unfold them stays at Tune~v1." This follows reviewer fix
    L9–11 to end the previous sentence at "fixed truth.". The atom is lowercase ("the prior ..."), so "The prior"
    would not match, and "Throughout," keeps it intact. As a result, F138's `after` spans two consecutive sentences,
    and the checker names it.
- **Sentences that would start with a symbol.** F144, F145 and F147 would open with a symbol, so each has a noun in
  front: "The term $C_{\mathrm{total}}$", "The model term $C_{\mathrm{model}}$" and "The response term
  $C_{\mathrm{resp}}$".
- **F151** ("The note gives the cells, ...") has no section pointer, because no atom provides one.

## Captions reworded under rule 1

- **Fig. 1:**
  - F168 and F169 are one sentence: "The band of this analysis contains the ... blocks of the covariance,
    Sec.~\ref{sec:uq2d}, and it omits ...".
  - F170 opens "Here the two bands are correlated, ...". "Note that" is dropped (reviewer). The atom is lowercase,
    so it needs an opener.
- **Fig. 3:** in (a) and (b), "where the grey step/band is ..." replaces a semicolon. F236's own semicolon is in its
  atom and stays.
- **Fig. 2:** "Both from a deterministic LightGBM estimator." is a fragment, but it is the whole atom, so it stays.

## GATE phrases

- All eight bound phrases print exactly once in b2, and none prints in b1 or b3. That holds for a literal match and
  for an any-`\SI`-value pattern.
- After fix F207–F209, "reduces it to below \SI{0.3}{\percent}" and "leaving up to \SI{1}{\percent} in some joint
  cells" each stay contiguous.
- F230's context atom `$(\Eavail,W)$ cell` now prints three times:
  - in the F230 sentence;
  - inside "the $(\Eavail,W)$ cells unfolded with ..." (F226, reviewer fix);
  - inside the Fig. 3 caption atom (F236).

  The bound phrase itself ("it is \SIrange{16}{31}{\percent} in the most affected") prints once. The checker reports
  context atoms separately and requires only that they print.

## Atom-forced deviations from the APS conventions (atoms win)

- **No serial comma:**
  - F144 "lateral and normalization uncertainties"
  - F145 "GENIE + MEC, NuWro and GiBUU"
  - F148 "species, energy-dependence or resolution effects"
  - F149 "its fake-data tests and its comparison"
  - F151 "the per-group uncertainties and the correlation matrix"
  - F168 "training-seed and run-period blocks"
  - F234 "the exact binned comparison and the joint-test-estimator shapes"
- **Semicolons inside atoms:** F145 ("in turn; it represents ..."), F236 and F239.
- **British spellings:** "labelled" (F222) and "grey" (F171, F237, F240).
- **Numerals for small counts:** "9 pseudo-experiments" (F218), "8 leaves" (F207, F219, F237) and "W bin 6"
  (F243). Spelled-out counts: "ten there, five here" (F200) and "five seed settings" (F176).
- **R10 tension.** Several HONESTY rows sit inside a result sentence because a row's atoms must share one sentence:
  F229 ("..., although no single cause is established") and F145/F146. After the reviewer's join, the
  $C_{\mathrm{resp}}$ sentence (F147–F149) is one long sentence.
- **R7 (one pointer per subsection) is exceeded where the rows require it:**
  - IV B has two pointers.
  - IV C has one, IV F has one and IV G has none.
  - IV D has four (F204 twice, F211, F214).
  - IV E has four (F232, F234, F240 in the caption, F248).

## Reviewer fixes applied

| fix | where now |
|---|---|
| MAJOR F226 | "When the true shape is reweighted by the GiBUU-to-GENIE ratio, the $(\Eavail,W)$ cells unfolded with a development variant ... deviate from it by several percent in the largest cells and by up to \SI{74}{\percent} at high $W$, in the cell ..." |
| MAJOR F207–F209 | "... reduces it to below \SI{0.3}{\percent} in those cells and at most \SI{0.4}{\percent} elsewhere in the projection, leaving up to \SI{1}{\percent} in some joint cells." |
| MAJOR IV H order | F286 ("..., and \fvval{f1-tune-g18} and the GENIE + MEC component ... also use ..."), then F287, then F288 |
| F148, F149 | "... and other deposits, but it does not cover ..., and it enters only this result, ..." |
| F230 | "For other fixed generator shapes tested with the joint-test estimator, it is \SIrange{16}{31}{\percent} in the most affected $(\Eavail,W)$ cell and lies within the quoted total uncertainty in about half of those cells." |
| L10 | "which changes their reconstructed and true distributions together" |
| L9–11 | The sentence ends at "fixed truth.", followed by "Throughout, the prior used to unfold them stays at Tune~v1." (see Openers above) |
| F191 | "in the combined result" kept (see above) |
| F198/F199 | "... generator shape. For the published analysis, this is because it chose its ten iterations ..." |
| "respectively" | Added in F283 and F288 |
| "compared with" | Used for the integrated cross section (F154) and the median uncertainties (F177) |
| L80–81 | "... per bin and is \SI{\uqIntegral}{\percent} on the integrated cross section, ..." |
| L67–68 | "Note that" dropped; "Here" opens the lowercase atom |
| L66–67 | **Not applied.** The F168 atom is "... blocks of the covariance, Sec.~\ref{sec:uq2d}", with the comma inside the atom, so "(Sec.~\ref{sec:uq2d})" would break it. |
| L231–233 | "..., so the estimator fails a data-stability requirement ..." |
| L296 | ", and" replaces "while" |

## Checks and the smoke build

- See the report for `check_batch.py b2` after the fixes.
- A smoke compile of b1–b3 in a minimal two-column `article` driver with stub graphics exits 0. Its overfull boxes
  are all in verbatim floats: Eq. (1), Tables I–III.
