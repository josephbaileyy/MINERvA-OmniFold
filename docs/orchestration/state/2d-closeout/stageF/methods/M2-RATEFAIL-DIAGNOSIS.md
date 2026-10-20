# The ~10% rate-change coverage failure: diagnosis from existing outputs (record)

**Run by** a Claude agent for the director, 2026-10-20, from local committed receipts and code only (0 node-h). Scripts and output are in [`ratefail/`](ratefail/). The agent could not write this file; the director saved its report verbatim below.

**Question (outside referee X7, comment 2).** Why do statistical intervals miscover (down to 0.06) under what is in effect a ~10% signal-rate reduction (KI 98)?

**Finding:**
- **The rate change is recovered.** The total is −9.58% recovered against −9.56% injected.
- **The intervals are not too narrow.** Setting the spread equal to the half-width leaves coverage at 0.06–0.22.
- **The referee's purity mechanism is excluded.** The subtraction removes the absolute nominal background expectation, which is unchanged.
- **The cause is residual bias that the nominal-truth bias correction does not remove.** The rate change adds a positive bias that grows with W: about +0.2% (W 1.4–2.2), +0.4% (W 2.2–3) and +0.7–1.1% (W ≥ 3). That is 1.3–2.6σ against intervals of 0.16–0.43%.
- **Not established:** whether that term comes from the background fraction rising by 0.111·f_bkg (its size and ordering match) or from the estimator alone.
- **Measured vs inferred:** the per-functional means and spreads are **inferred**, by a Gaussian fit to each functional's 68%/95% coverage pair. They are cross-checked against EW17 (+1.04% fitted against +1.05% recorded). The per-experiment products are on the cluster only.

**Confirming test (cluster, not run; about 0.1–0.2 node-h):** tilt pseudo-experiments on the same seeds (a) as run, (b) with no background, and (c) with the background scaled by 0.9.

**CITABLE FOR:** the decomposition above, with its inferred status.
**NOT CITABLE FOR:** the source of the W-graded term.

---

I could answer every part of the question from local material except the per-experiment means and SDs. The tilt point's failure is not a normalization failure: OmniFold recovers the ~10% rate drop in the total. What fails is a positive residual that remains after the bias correction and grows with W. It is present even where the nominal bias β ≈ 0, so it is bias, not narrow intervals. The referee's specific purity mechanism (nominal purity applied to rate-shifted data) is not what the code does. The source and sign of the W-graded residual are not established.

**What is measured vs inferred.** The receipt (`interim_400.json`) records only hit counts, confidence bounds, σ and half-width/σ. It has no per-experiment means or SDs, and the 400 products exist only on the cluster. So item 2's means and item 3's empirical SDs are inferred: I fitted a Gaussian with shift d and spread s to each functional's observed 68% and 95% coverage pair. The SE comes from a parametric bootstrap with n=400. The sign of the shift comes from the one local tilt experiment, `p3_tilt20_s2`. One cross-check passes: the fit gives EW17 +1.04% (+2.60σ), and the OUTCOME doc quotes +1.05% and 2.6σ (`OUTCOME-20260925-s5c-tier-s-futility-fail.md:47`).

Worktree `wt-m3` at `89e395d0`. Scripts and output are in `scratchpad/methods-ratefail/` (`diag.py`, `group.py`, `wcount.py`, `se.py`, `diag_out.json`).

### 1–4. Per-functional numbers (tilt point unless marked)

| functional | injected | β (nominal) ± se | corrected mean residual | implied raw bias at tilt | mean recovered change | SD/σ | half-width/σ | cov68 nom → tilt |
|---|---|---|---|---|---|---|---|---|
| total_integrated | −9.56% | +0.30 ± 0.02% | not invertible; p3 +0.16% (1.7σ) | — | p3: −9.58% | — | 1.03 | 0.590 → **0.743** |
| EW_all_ones | −9.95% | +0.09 ± 0.03% | +0.09% (0.63 ± 0.12σ) | +0.18% | −9.86% | 0.67 | 1.02 | 0.708 → 0.715 |
| EW7 (typical) | −9.97% | +0.06 ± 0.03% | +0.10% (0.54 ± 0.13σ) | +0.15% | −9.88% | 0.62 | 1.02 | 0.765 → 0.770 |
| EW0 (typical) | −9.99% | +0.14 ± 0.08% | −0.16% (0.62 ± 0.10σ) | −0.02% | −10.14% | 0.66 | 1.04 | 0.660 → 0.735 |
| EW9 (W 1.8–2.2) | −9.97% | +0.22 ± 0.04% | +0.19% (1.31 ± 0.07σ) | +0.41% | −9.80% | 0.98 | 1.03 | 0.690 → 0.380 |
| EW10 (W 2.2–3) | −9.97% | +0.54 ± 0.05% | +0.40% (1.82 ± 0.05σ) | +0.94% | −9.61% | 0.80 | 1.03 | 0.705 → 0.160 |
| EW16 (W 2.2–3) | −9.94% | +0.54 ± 0.05% | +0.38% (1.96 ± 0.05σ) | +0.91% | −9.60% | 0.78 | 1.04 | 0.705 → 0.117 |
| J116 | −9.97% | +0.04 ± 0.04% | +0.37% (2.05 ± 0.06σ) | +0.42% | −9.63% | 0.95 | 1.03 | 0.720 → 0.140 |
| **J224** | −9.97% | −1.00 ± 0.08% | +0.66% (2.54 ± 0.09σ) | −0.35% | −9.38% | 0.96 | 1.05 | 0.660 → **0.060** |
| J233 | −9.80% | −1.78 ± 0.07% | +0.52% (2.21 ± 0.06σ) | −1.27% | −9.34% | 0.84 | 1.05 | 0.657 → 0.083 |
| **EW17** (W ≥ 3) | −9.94% | −3.96 ± 0.09% | +1.04% (2.60 ± 0.10σ) | −2.96% | −9.00% | 1.05 | 1.02 | 0.627 → **0.068** |
| EW11 / EW23 / EW29 | −9.97 / −9.88 / −9.77% | −4.06 / −4.02 / −4.11% | +1.13 / +1.00 / +0.79% | ≈ −3.0 to −3.35% | ≈ −9.0% | 1.14–1.18 | 1.03–1.04 | 0.63 → 0.13 / 0.085 / 0.18 |

How each column was obtained:
- **Injected change** is computed exactly. Both p3 products share split key 20260924, so the ratio of their stored truths, f_true(tilt)/f_true(nominal) − 1, isolates the reweight. Across all 153 functionals it runs from −7.90% (EW41, the overflow corner) through a median of −9.86% to −10.00%.
- **β ± se** are from `d1/bias_correction.json`.
- **SD/σ and half-width/σ**: half-width/σ is from the receipt; SD/σ is inferred (fit described above).

**Interval construction (item 3).** The estimate is f̂/(1+β) and the half-width is z·√(σ² + (se·f)²) (`s5c_coverage.py:94-97`, amendment 4). σ is an absolute value from one nominal bootstrap (`:65-73`, `:129-131`), and the same σ is used at every grid point (`:158`). With 10% fewer events the true absolute SD should be about √0.9 ≈ 0.95σ, so at the tilt point the intervals are, if anything, slightly too wide.

**Where the failures sit (item 4).** The pattern depends on W, not on E_avail:

| truth-W band | futile at tilt (68%) | median cov68 at tilt |
|---|---|---|
| W < 1.4 | 3 / 46 | 0.740 |
| W 1.4–2.2 | 22 / 66 | 0.659 |
| EW cells, W 2.2–3 | 6 / 7 | 0.287 |
| EW cells, W ≥ 3 | 6 / 7 | 0.180 |
| J cells, W ≥ 2.2 | 14 / 25 | 0.568 |
| total_integrated, EW_all_ones | 0 / 2 | 0.73 |

At the nominal point the same bands have 0 futile functionals. In the single p3 experiment, the mean corrected residual over the EW cells rises with W: −0.04σ, 1.07σ, 0.85σ, 0.89σ, 1.79σ, 3.61σ for W bins 0 to 5.

**Decomposition (item 4).** I recomputed each failing cell's coverage under the fitted model in two ways:
- **Keep the bias, set SD equal to the half-width:** coverage stays at 0.06–0.22.
- **Remove the bias, keep the fitted SD:** coverage becomes 0.62–0.82 at 68% and 0.92–0.99 at 95%.

So the miscoverage is almost entirely residual bias. Interval width contributes only the M2 effect (the bootstrap does not redraw background): SD/σ is about 1.15 in the W ≥ 3 column, which alone would land near 0.62.

The bias is better described as β failing to transfer than as β being rescaled. The tilt adds a positive amount wherever W is high, whatever β's sign:
- At W ≥ 3, β ≈ −4% and the raw bias shrinks to about −3%.
- At W 2.2–3, β ≈ +0.54% and the raw bias grows to about +0.92%.
- In J116, β ≈ 0 and the raw bias is +0.42%.

A multiplicative rescaling of β would move the W ≥ 3 and W 2.2–3 cells in opposite directions; both actually move up.

### 5. Backgrounds and purity

Backgrounds are included:
- **Background is drawn fresh and not reweighted.** Background rows are drawn as Poisson(bkg_w) in every experiment (`s5c_pseudo.py:130`), and the reweight r multiplies only the signal (`:128`).
- **The purity is not the simulation's S/(S+B).** The weight is max(0, d − b)/d per 5D reco bin (`:107-111`). Here d is the pseudo-data histogram (`:101`) and b is the nominal background expectation in absolute counts (`:136-137`).
- **The subtraction is unbiased per bin.** Because the background is unchanged, E[d] − b equals the tilted signal exactly, apart from the max(0, ·) clipping.

The referee's mechanism would apply the nominal purity S/(S+B). That would give a relative excess of f_bkg·(1/0.9 − 1) = 0.111·f_bkg per bin. Summed over the sample this predicts about +11.5k events (+0.36%). The measured excess is −60 events out of 3.197M (p3 tilt meta: `measured_weight_sum` 3,196,994 vs 3,197,054 pseudo-signal events). That equals realized minus expected background (119,078 − 119,132 = −54). The referee's mechanism is therefore excluded at the reco-bin level.

There is a coincidence worth stating, as inference only. The purity-bias OUTCOME gives B/S as 1.3–4.0% below W = 3 GeV and 13% in W ∈ [3, 100) (`OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md:40-41`). Then 0.111·f_bkg ≈ 0.14–0.43% for W < 3 and ≈ +1.3% for W ≥ 3, close in size and ordering to the observed residuals. My assignment of B/S values to individual W bins is a guess within the quoted range. The linear within-bin-leakage reading of the D1 bias predicts the opposite sign at W ≥ 3: about −4.8% raw, against −3% observed.

### 6. Normalization in OmniFold

The normalization is not fixed by construction:
- **No class balancing for LightGBM.** `balance = (kind == "nn")` (`omnifold_nn_core.py:225`), so for `lgbm` the multiplier stays 1.0 and the raw weights are used (`:230-231`).
- **The density ratio is unnormalized.** The weight is p/(1−p) with only a clip (`:152-155`). Step 1 trains MC (w_push·w_reco) against data weights that sum to about 0.9 of the MC (`:253-255`).
- **No renormalization downstream.** The unfolded counts are the histogram of wpush·w_truth (`s5c_unfold.py:138`). The cross-section extraction divides by completeness·flux·N·POT·volume (`xsec_nd.py:79-82`) and does not normalize to the MC total.

A global rate change is therefore learnable as the classifier's prior odds; that LightGBM's starting score is the log prior odds is my inference from library defaults, not repo code. The measurements agree: the total covers at 0.743/0.960, EW_all_ones at 0.715/0.980, and the p3 total change is recovered at −9.58% against −9.56% injected. The rate change does not appear as a global residual bias.

### Conclusion

- **Most likely mechanism:** the nominal-truth correction β does not transfer, because the rate change adds a W-graded positive bias of about +0.2% (W 1.4–2.2), +0.4% (W 2.2–3) and +0.7–1.1% (W ≥ 3). Measured against σ/f of only 0.16–0.43%, that is a 1.3–2.6σ shift, which explains coverage of 0.06–0.4.
- **Ruled out:** a global normalization failure, the referee's literal purity mechanism, and intervals that are too narrow (only the minor M2 effect).
- **Not established:** whether the W-graded term comes from how the unfold responds to purity-weighted background events at higher B/S (its size matches 0.111·f_bkg) or from the estimator alone.

**Cheap confirming test (cluster, not run):** on the same seeds, with no other code change, run tilt pseudo-experiments three ways:
- (a) as now;
- (b) with `--no-background` (`s5c_pseudo.py:131-132`, a single-experiment development diagnostic);
- (c) with the background scaled by 0.9 as well.

Use about 4–9 seeds per arm at roughly 0.015 node-h each (`FEASIBILITY-20260925-s5c-scalar5d-measurement-and-inference.md:21`). If the W-graded residual disappears in (b) or (c), the cause is the change in B/S; if it persists, it belongs to the estimator. Separately, the per-functional means and SDs of the 400 existing tilt products would replace my inferred table directly; they need only cluster reads.

Housekeeping: importing `s5c_coverage` created `nd-unfolding/__pycache__` in `wt-m3`. When I removed it I also deleted two older .pyc files from a previous session; they are gitignored and regenerate automatically. Nothing else in any checkout was touched.