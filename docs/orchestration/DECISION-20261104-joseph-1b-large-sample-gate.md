# DECISION 2026-11-04 — Joseph: 1B's variance gate is evaluated on a large separate sample of the clipped law

**Recorded by** the paper-tighten lane, as director.

**Amends** `DECISION-20261103-joseph-1b-variance-gate.md` (#724).

## What led to it

**The gate as approved** (#724) has three checks per truth, on 16 cells:
- (i) at most 2 cells with |r − 1| > 0.20;
- (ii) |mean log r| ≤ 0.07;
- (iii) max |r − 1| ≤ 0.35.

Joseph was shown a noise-only STOP of "about 0.5% over three truths". That figure assumed independent cells.

**The calibration** of G18 and AR23 ran as job 60771025: COMPLETED, 0:0, about 0.36 node-h, with both controls
holding. It used 10⁴ null replicates per truth from a separate seed. Its records are in A2.1's `calib-run/`:
`calibration.json` (`4b6a18b6…`) and `tradeoff.json` (`415a6f72…`).
- **(ii)'s statistic has a common-mode null SD of 0.042** (G18) and **0.043** (AR23), because the cells share the
  same 300 draws. The SD assumed was 0.020.
- **At the approved numbers,** the two-truth noise-only STOP is **18.9% ± 0.4%**. Three truths can only be higher.
- **At 300 draws** no threshold on (ii) gives both a low noise rate and power against a realistic broad deflation:
  - at the 1% three-truth point, about 3.16 SD, the per-truth power against an 8% deflation is about 11%;
  - at 0.07, power over two truths is 84%, at 18.9% noise.
- The 8% size is cov2d's C2 measurement: a clipped variance-ratio median of 0.922 at AR23.

**The independent consult (Sonnet)** is verbatim in `fd/consult-1b-gate16-20261104/`. It recommended evaluating the
gate on a large separate sample of the same clipped law, with conditions. coverage-5b-audit checked the calibration's
internal consistency.

## Joseph's answer, verbatim

Asked how the gate should be fixed before any 5D draw, given that 1B's pooled variance check stops on noise about
19–27% of the time as approved:

> Large-sample gate (Recommended)

sha256 of the text plus a final newline begins `38c703adf04f21df`.

The option as put to him:
- evaluate the gate on about 3,000 extra draws of the same clipped rule, at expected counts, under 1 node-h;
- recalibrate the thresholds to a 1% false-stop budget over three truths;
- build it to catch an 8% broad shrinkage;
- verify the large-N unclipped null first;
- keep a loose check on the actual 300 draws as a backstop.

## What is decided

1. **The gate reads the law, not the realization.**
   - Per truth, the clipped-composition variance ratios r_c are evaluated on a separate sample of N draws from the same
     generating code, configuration and clip rule as the 300 declared draws.
   - The 300 declared draws are the sample's first 300, so the match can be checked bit for bit.
   - N is about 3,000, fixed in the amendment by the power requirement in item 3.
2. **The thresholds are recalibrated by null simulation at N,** before any 5D draw is examined.
   - (ii)'s and (iii)'s thresholds are set so the measured joint noise-only STOP of (i)–(iii) over three truths is at
     most 1%.
   - It is measured on the correlated null, including the reference variance's noise, not by scaling the 300-draw
     numbers.
   - (i) stays at ±0.20 with k = 2 unless the null at N shows that it alone exceeds the budget. In that case it comes
     back to Joseph.
3. **Materiality.** The gate must catch a uniform 8% variance deflation with at least 80% power per truth at the
   recalibrated thresholds. If N = 3,000 does not reach that, the amendment raises N and states the price. Power is
   also reported against a deflation concentrated in a few cells.
4. **First, the large-N unclipped null.** At N, under the unclipped first-order law, the per-cell mean ratio must be
   1 within its measured SE. This is the existing law control (z = 4) and the linearisation tolerance (0.02) at N. If
   it fails, nothing proceeds, and it comes to the director.
5. **The backstop.** On the actual 300 declared draws, (iii) at 4.3 SD per cell, by rule (α), and (i) at k = 2 are
   applied as a loose check. A config hash shared by the gate sample and the coverage draws is logged.
6. **The plug-in truth** is calibrated after B4 and the P1 capture, under the same rules, before the receipt and
   before any 5D draw. The 1% budget is over all three truths.
7. **Cost.** One more read of the inputs plus the replicates, under 1 node-h by the option's estimate. The amendment
   states the measured price. Every other part of #724 and `DECISION-20261103-joseph-coverage-clip-rule.md` is
   unchanged, and the hard stop stays.

Nothing is submitted, deposited or tagged.
