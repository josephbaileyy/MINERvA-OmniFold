# Response test: our p‖ migration and efficiency against MINERvA's Figs. 3–5 (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). It is part of the chain in [`../README.md`](../README.md).
It runs locally with Joseph's go. One descriptive read-only step on login02 is marked below.

**Declared reading: EFF-DIFF.** Our migrations match Fig. 3 within the declared 0.03. Our efficiency at true p‖ 40–60
is 13 % below Fig. 5's.

## Extraction

A Claude subagent extracted Figs. 3, 4 and 5 without seeing our numbers. It read the PDF content streams directly
([`extract/extract.py`](extract/extract.py), [`extract/pdfops.py`](extract/pdfops.py)), and the cell values are in
[`extract/fig3.csv`](extract/fig3.csv), [`extract/fig4.csv`](extract/fig4.csv) and
[`extract/fig5.csv`](extract/fig5.csv), with overlays.
- **Precision.** All 657 drawn cells match a palette box exactly: 200 steps, σ = 0.0025. Cells in the bottom box may
  be anywhere in [0, 0.005).
- **Row sums.** Fig. 3's rows sum to 0.979–1.010 over the drawn bins. The true 40–60 row is the lowest, at about 0.95
  once its bottom-box cells are treated as near 0. That fits normalization over bins that include reco overflow.
- **pT edges.** The extraction also found the pT edges recorded in [`../edges/`](../edges/README.md).

## Result

[`DECLARATION.txt`](DECLARATION.txt) (sha256 `fc57cb88fe5a42a070242f8918b97f96bebe7f9ce570f0a88f29f02cd06d3928`), [`resptest.py`](resptest.py) → [`run.log`](run.log).

| quantity | ours | theirs |
|---|---|---|
| P(reco 40–60 \| true 40–60) | 0.576 | 0.548 |
| P(reco 20–40 \| true 40–60) | 0.408 | 0.398 |
| P(reco 40–60 \| true 20–40) | 0.027 | 0.033 |
| efficiency at true 40–60, weighted by our T | 0.747 | 0.861 |

Per pT row at true 40–60, our efficiency is 0.60–0.88 and theirs is 0.81–0.98: ours is lower in every row. At true
20–40 the gap is 2–3 % at low pT and grows to 23 % at the highest pT.

## Descriptive follow-up (not declared)

[`overflow_remote.py`](overflow_remote.py) → [`overflow.out`](overflow.out). This was run read-only on login02, on this
lane's merged event-loop output. It measures where our selected signal events with truth in the grid reconstruct:

| true p‖ | reco in grid | reco p‖ ≥ 60 | reco pT ≥ 4.5 |
|---|---|---|---|
| 40–60 | 94.0 % | 4.1 % | 2.8 % |
| 20–40 | 98.0 % | 0.8 % | 1.8 % |
| 10–15 | 99.3 % | 0.3 % | 0.7 % |

Counting reco-anywhere raises our 40–60 efficiency from 0.747 to 0.794, still 8 % below Fig. 5. If Fig. 5's efficiency
counts reco-anywhere events but the unfolding used in-grid data, the published result would run low by these
fractions. The predicted fold residual is then +6.0 / +2.0 / +0.7 % at 40–60 / 20–40 / 10–15, against +10.1 / +1.6 /
+0.6 % observed net of the baseline. **This is a hypothesis, not a finding.** It is in tension with fig2 and flux:
after the flux swap, our selected MC and our truth at 40–60 both match theirs to 2–3 %, which suggests our full
response is close to theirs. It should be re-tested with the corrected pT edges.
