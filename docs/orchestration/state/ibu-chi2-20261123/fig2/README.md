# Fig. 2 test: our selected data and MC against MINERvA's (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). It is part of the chain in [`../README.md`](../README.md).
Joseph asked for it after the event-loop diagnostic ([`../evloop/results/`](../evloop/results/README.md)). It runs
locally on public inputs, with no cluster job.

**Declared reading: UNRESOLVED in both regions.** Controls pass. Below the readings are descriptive numbers that the
declaration does not read. They say where to look next, but they are not a finding.

## What it compares

[`DECLARATION.txt`](DECLARATION.txt) (sha256 `ac429f1ec6bba77391369e5cd9725a61e12142a5c48f1183a0a201417fea13f2`, written and hashed before any number was computed).

The question: at reco p‖ 40–60 GeV/c (COL) and reco pT 0–0.07 GeV/c (ROW), do our selected data match MINERvA's? If they
do, does our total selected MC?

- **Theirs:** Fig. 2 of arXiv 2106.16210v4 (PDF sha256 `39b6b8f1e6a59007ce31f4da4ab1af50dd07b491f537a3bbd898d57e2271ef69`,
  not committed), page 4: data points and the Tune v1 total MC line, as counts per cell.
- **Ours:** BASE `N` and `M.sum(1) + B` from
  [`../evloop/results/ibuchi_products.npz`](../evloop/results/ibuchi_products.npz).

**Extraction.** A Claude subagent extracted the figure from its vector paths without access to our numbers
([`extract.py`](extract.py), [`fig2_points.csv`](fig2_points.csv), [`fig2_cells.csv`](fig2_cells.csv),
[`summary.json`](summary.json)). The overlays [`overlay_top.png`](overlay_top.png) and
[`overlay_bot.png`](overlay_bot.png) draw the extracted values on a raster of the page. I checked the bottom block by eye,
including the 40–60 panel. Every y coordinate in the PDF sits on a 0.224 pt grid, so a point's precision in counts
depends on its panel's scale factor; `quantum_count` in `fig2_points.csv` gives it per point.

## Controls

| control | value | limit |
|---|---|---|
| C-DUP data, median \|top/bottom − 1\| over 194 cells with D > 100 | 0.68 % | ≤ 1 % |
| C-DUP MC, same cells | 0.89 % | ≤ 1 % |
| C-ERR, median N from error bar / N from point (59 bars ≥ 2 steps) | 0.985 | within 2 % |
| C-TOT, sum of D (finer copy per cell) | 4,105,662 | within 1 % of the quoted 4,105,696 |

The top block sums to 4,141,417 and the bottom to 4,111,184. Both are within 1 %.

## Reading

[`score_fig2.py`](score_fig2.py) → [`score.out`](score.out).

**One choice was fixed after the extraction and before the comparison**, because the declaration left it open. Each cell
uses whichever of its two copies has the finer grid step. Top-only and bottom-only results are reported as well.

The declared delta takes the top/bottom disagreement of the region sums:
- COL: delta = 11 %. In the top block the 40–60 cells are only a few grid steps tall.
- ROW: delta = 1.6 %, so 3·delta = 4.9 % ≥ τ = 3.2 %.

Both regions therefore read **UNRESOLVED**. In hindsight, that delta is dominated by the coarser copy. A per-panel error
bound from the grid step, the axis calibration and the printed scale factor would be the better measure. It is not
applied here, because it was not declared.

## Descriptive numbers (not read by any rule)

Finer copy per cell. ρ is the region ratio ours/theirs, normalized to all 205 cells.

| region | ρ data | ρ MC | data/MC ours | data/MC theirs |
|---|---|---|---|---|
| COL (40–60) | +0.2 % | −11.4 % | 1.532 | 1.342 |
| ROW (0–0.07) | −7.2 % | −6.9 % | 0.874 | 0.868 |

Their data/MC in COL is 1.344 from the top block and 1.342 from the bottom, so the ratio is stable even where the
absolute counts are not. Across the whole grid, N/D = 0.997 and P/Q = 0.987.

**What they suggest, and what they do not.**
- **COL.** Our selected data agree with theirs. Their total selected MC is about 14 % above ours there. Folding the shipped
  Tune v1 truth through our response, with our background, and scaling by the ratio of the two selected-data totals,
  gives 14,953 events against their 15,189 (1.6 % low). So that one
  spectrum is consistent with a common response. It does not show the responses are equal. One truth spectrum tests one
  weighted sum of the response columns, and folding the published result through our response gives a fold-to-Tune-v1
  ratio of 1.240 against their data/MC of 1.342. Whether MINERvA's own result folds back onto their data is therefore
  open.
- **COL, our side.** Our own K=10 result, folded through our response, closes to +0.66 % in COL and −0.37 % in ROW. The
  published result through the same response gives +10.9 % and −5.4 % ([`../foldtest/run.log`](../foldtest/run.log),
  `own_fold_refined_ur10` vs `primary_refined`).
- **ROW.** Our data and our MC are both about 7 % low against theirs, with equal data/MC. That suggests a difference
  common to data and MC, in the reco pT definition or acceptance. The data-only angle scan in `../evloop` could not have
  seen it. The next row up, 0.07–0.15, is also about 3 % low, so a simple transfer across the 0.07 edge does not fit.
