# DECISION 2026-11-03 — Joseph: 1B's pre-bulk variance gate allows 2 of 16 cells, with two pooled checks

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The gate.** `DECISION-20261103-joseph-coverage-clip-rule.md` item 2 has 1B apply C2's fixed reading
(`fd/receipts-cov2d/clip/c2_reading.txt`, sha256 b5b4fc4b…) before its bulk, as a hard stop. Part of that reading is
the clipped-composition variance gate: |ratio − 1| ≤ 0.20 in at least 95% of cells. For cov2d's 205 cells, C2 chose
95% because an every-cell rule "would fail about 2–3 cells by chance alone".

**At 1B's 16 cells,** 95% is 15.2, so every cell must pass. coverage-5b priced the noise-only STOP probability in
A2.1's mapping record. It assumes 300 draws per truth, SE √(2/299) = 0.0818, and independent cells:
- 0.0146 per cell;
- 0.21 per truth;
- 0.51 over three truths (G18, AR23 and the plug-in).

**The independent consult (Sonnet).** `state/measurement-paper/5d-community-20261024/fd/consult-1b-gate16-20261103/`
holds PROMPT and ANSWER verbatim, with SHA256SUMS. What carries over from the 2D rule is its false-alarm rate, not its
5% fraction. The 2D rule allows up to 10 of 205 cells to fail, with a noise-only STOP of about 3e-4.

| failing cells allowed per truth | noise-only STOP over three truths |
|---|---|
| 0 | 0.51 |
| 1 | 0.066 |
| 2 | 0.0046 |

It recommended allowing 2, plus a pooled mean-log-ratio bound and a max-deviation bound to recover power against
broad or single-cell distortions, all calibrated on separate null natures and fixed before any 5D draw is seen.

## Joseph's answer, verbatim

Asked which rule 1B's pre-bulk variance check at 16 cells should fix before any 5D draw is seen:

> Allow 2, plus pooled checks (Recommended)

sha256 of the text plus a final newline begins `4c71ccba80ae332f`.

The option as put to him: up to 2 of 16 cells may miss ±20%; the mean log ratio must also lie within ±0.07, and no
cell beyond 0.35. Noise-only stop about 0.5% over three truths; thresholds calibrated on separate null simulations and
committed first.

## What is decided

1. **1B's variance gate, per truth.** The clipped-composition variance ratio (C2's definition, through cov2d's code)
   passes if all three hold:
   - **(i)** at most 2 of the 16 cells have |ratio − 1| > 0.20;
   - **(ii)** |mean over cells of log ratio| ≤ 0.07;
   - **(iii)** max over cells |ratio − 1| ≤ 0.35.

   It is read at each of the three truths: G18, AR23 and the plug-in.
2. **Calibration first.** Before any 5D draw is examined:
   - the noise-only rates of (i)–(iii) are measured on null (unclipped, first-order) natures from a separate seed;
   - the measured standard errors replace the analytic √(2/299) where they differ;
   - the result and the rule are committed.
   - **The director's ruling, not Joseph's:** if the calibrated combined noise-only STOP over three truths exceeds
     about 1%, it comes back to Joseph before any 5D draw. The lane does not re-tune the thresholds.
3. **Unchanged:** the rest of C2's reading (the R_c rules and the row-match bound), the 0.9 "weakened" rule, and the
   hard stop. A failed gate means nothing launches, and 1B returns to Joseph.
4. **Only 1B's 16-cell mapping changes.** cov2d's 205-cell gate is unchanged.

Nothing is submitted, deposited or tagged.
