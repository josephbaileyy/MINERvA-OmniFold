# Cross-document audit items D3 and the ratio direction (2026-11-15)

The director passed on two items from the codex-school cross-document audit of draft 3027c9596
(`crossdoc-numbers-3027c959…-6c38249b….md`).

- **D3, the prior-retention threshold boundary.** The record's rule is inclusive. FD-PRR-DECLARATION.md:288-291 gives
  *reduces* if some ρ_L ≤ ρ_B0 − δ_F, *increases* in reverse, and *no effect* if every |ρ_L − ρ_B0| < δ_F.
  prr_read.py:303-311 has the same rule for the factor classes and for IBU's own class. Index row 4's criterion
  already said "at least". The following said "more than" and now say "at least":
  - the Supplement's thresholds paragraph and its classes paragraph;
  - row 4's Reading;
  - the paper's three study sentences (rule, increases results, IBU result).

  The paper's "no change above the threshold" is now "no change as large as the threshold" (strict <).
- **The ratio's direction (Supplement S8.6, the interaction group).** It is F_prior = √(B/A) (FD-1B-INV-DECLARATION.md:262),
  with A the full universe and B the response alone (:227-228). The sentence now names it as the note does: the
  response block's spread over the full-universe block's, per cell.

`meaning-read.txt`: the codex-school meaning read (gpt-6.1-sol, high effort, read-only) of `diff-as-read.txt` against
`meaning-read-records.txt` (prompt `meaning-read-prompt.txt`): PASS.
