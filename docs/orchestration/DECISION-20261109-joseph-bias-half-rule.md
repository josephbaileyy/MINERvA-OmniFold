# DECISION 2026-11-09 — Joseph: declare and compute a per-cell validity rule, |bias| ≤ ½ × the truth's departure from the prior, on the 16 cells

**Recorded by** the paper-tighten lane, as director.

## What led to it

- `OUTCOME-20261107-valid-region.md` (its read is receipt #897) classified the 16 reporting cells under V-ATLAS (the
  ATLAS User Guide's thresholds) and V-PRIOR (the lane's ρ = S_b/S_g < 0.5, an operationalization of the advisor's
  "bias spread comparable to the prior spread").
- Joseph asked the advisor where ATLAS uses a bias-spread-to-prior-spread comparison. The advisor answered, in
  private correspondence that Joseph relayed (paraphrased here, not quoted): the rules need not match ATLAS's; the
  pseudo-data already plays the role of the comparison to the priors; and a simpler rule could be that **the bias is no
  more than 50 % of the raw difference**, applied to every histogram bin, with the observable or binning modified if
  any bin fails.
- The director recommended adopting the rule, with one addition fixed before anything is computed: the ratio is
  undefined where the truth and the prior nearly agree (at the closure truths they are identical), so the rule applies
  only where they differ by at least 1 %, the floor `FD-PRR-DECLARATION.md` §4.1 already uses (|d_c| ≥ 0.01). The
  director proposed to have a lane write the rule down, at the same 12 graded truths, and compute it on the 16 cells
  from committed fake-data products, at no compute.

## Joseph's answer, verbatim

> okay yes lets do the 50% rule and can you actaully explain the denominator and unstability to me again? it seems like if we correct this fix its possible we get a passing coverage test right? and I know we are stating the instability as a limitation but isn't this a limitation that the referees said points to major revision? wouldn't the major revision step be rerunning it? or no

sha256 of the text plus a final newline begins `2c1a4baee27bebf3`. The first clause is the decision recorded here;
the rest are questions the director answers in correspondence.

## What is decided

1. **A new validity rule, V-HALF, is declared and then computed.** Per cell c of R00–R15 and per graded truth t:
   - the truth's departure from the prior, d_{c,t} = (X_{c,t} − P_c)/P_c, and the bias, b_{c,t} = (X̂_{c,t} − X_{c,t})/P_c,
     with FD-PRR §4.1's definitions;
   - the rule applies at (c, t) only where |d_{c,t}| ≥ 0.01;
   - (c, t) passes when |b_{c,t}| ≤ 0.5 |d_{c,t}|; a cell is V-HALF-valid when it passes at every truth where the rule
     applies, and a cell where it applies at no truth is reported as such, not as valid.
2. **The truths** are the 12 graded truths V-ATLAS's A3 uses, with GiBUU on all 16 cells as declared there. GiBUU's
   exclusion on the p_∥ ≥ 4.5 cells is print-only, as before.
3. **The declaration fixes, before any value is read:** X̂'s source (the committed fake-data products V-ATLAS and
   V-PRIOR read), how the estimate's own noise is treated near the threshold (a cell whose class flips within it is
   "unresolved (noise)"), and the print-only sensitivity: the threshold boundaries at which each cell changes class.
4. **The process** is V-PRIOR's: the valid-region lane drafts the declaration and code, coverage-5b-audit audits,
   the director binds, and the read is local at 0 node-h. It does not delay the FD-PRR connects.
5. **Not decided here:** the advisor's consequence (modifying the observable or binning if a cell fails). That comes
   back to Joseph with the result, because it would mean redoing the 16-cell result.

## CITABLE FOR / NOT CITABLE FOR (to be carried by the declaration)

- **Citable for:** each cell's V-HALF class, with its inputs, as declared.
- **Not citable for:** coverage; a measurement; the cause of any failure; V-HALF as ATLAS's rule, or as the advisor's
  exact formulation (the 1 % floor and the noise treatment are this record's additions); a failing cell as excluded,
  wrong or unreported; any paper or note sentence without the PRD-referee read and Joseph.

Nothing is submitted, deposited or tagged.
