# The recovered-fraction rewrite and the figure fixes: the PRD-referee reads and the meaning reads (2026-11-12)

Rows: `pairs.tsv` (export.py, base 32ac4b767). As in bkg-read/, the PRD-referee reads were done by an independent
subagent working from facts and the rendered sentences only, and the meaning reads by an independent read-only
subagent given the records. The reports are condensed here; each finding is kept.

## PRD-referee read 1: minor revision
- Report overshoot counts beside the opposite counts.
- Write "of magnitude above 2 %".
- "Of the E_avail shape" is wrong for two of the four truths, and "on the median but not cell by cell" is vague. Use
  "the median unfolded (E_avail, W) cell moves by 56–88 % … but individual cells range from moving opposite to it to
  overshooting it".
- State EW29's −30 % injected and +21 % unfolded directly.
- :330's "leaves a similar residual there" has no referent. Name the method, quantity and truth. "Exact" reads as
  unregularized.
- The status word "Partly followed" sounds like shrinkage.
- Make the numerator explicit.
- State that σ_f includes r₀. Split the near-boundary column into near f = 0 and near f = 1.
- Motivate the 2 % threshold.
- Qualify the abstract and introduction's "retains part of its prior" (ρ). It is not contradicted, but a referee
  would read it as benign shrinkage.
- Not taken, with reasons recorded:
  - "none of the four": not true, because some sixteen-cell grades pass;
  - moving the caption's exactness clause and trimming "points shown": the director required both in the caption;
  - the abstract qualifier: the abstract is at 244 of 250 words, so it goes to the director.

## Meaning read 1: five defects
- The counts lacked "with |i| > 2 %". Over all supported cells W2 has 5 opposite cells, so "0" was false as written.
- "16–31 %" took W2's 16 % from EW37, an unsupported cell. The supported-cell range is 9–31 %.
- "Follow on the median" read as full recovery.
- The limitation's 56–88 % referred back to "every generator-sized truth change tested".
- :330's "residual" had no referent, and S4 :340's unscoped "the estimator does not follow" contradicted supp:recovery.
- Low-priority points: the semax bound now covers GiBUU, so an assert was added. The caption had no antecedent for
  "these 60", and the legend said "GiBUU/GENIE".

## PRD-referee read 2: ACCEPT after four wording edits
- Name the sixteen-cell grades in the limitation's first sentence.
- Remove the attachments in the :330 sentence.
- "Of magnitude" in the table caption.
- "Cell by cell" in place of "fully" at S4 :340.
- The abstract qualifier is recommended, not required. The shortest wording it would accept, 5 words, is
  "…retains part of its prior, though some cells move opposite."
- Applied. One deviation: :330 says "the gradient-boosted-tree unfolding in the same comparison" rather than "the
  reported estimator", because S7 does not say that comparison used the reported configuration.

## Meaning read 2: all five defects fixed, no new defects
- "Above the nominal one" became "above the nominal truth".
- The error bars are "smaller than the markers".
- check_sec4_receipts recomputes the 9–31 % from the assess receipt and the support rule; 17 tests pass.
