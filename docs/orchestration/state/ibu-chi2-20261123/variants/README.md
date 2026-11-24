# Variant test: shipped generator models against our MC truth (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). It is part of the chain in [`../README.md`](../README.md).
It runs locally on public inputs, with no cluster job.

**Declared reading: UPSTREAM in both regions, against our *tuned* truth.** See the limitation below before using it.

## What it compares

[`DECLARATION.txt`](DECLARATION.txt) (sha256 `1771df4af53d231bc5d7048dc7ef962190c5f9054e8512abfa32629a5d82e549`, written and hashed before any number was computed).

The truth test ([`../truthtest/`](../truthtest/)) found shipped Tune v1 above our CV MC truth by 16–20 % at truth
p‖ 40–60 and by 6–9 % at pT 0–0.07. This test asks whether that difference is already present against bare GENIE
2.12.6, before Tune v1's reweights.

Inputs:
- `m`, `mask` and `area` from [`../truthtest/vectors.npz`](../truthtest/vectors.npz).
- The published TotalCovariance.
- Seven model tables from the arXiv 2106.16210v4 ancillary files. They were fetched to the laptop and are not committed;
  their sha256 values are in [`arxiv-fetch.sha256`](arxiv-fetch.sha256).

Script [`varianttest.py`](varianttest.py) → [`run.log`](run.log).

## Results

Controls pass: the arXiv Tune v1 table equals the one truthtest used, and every table has the 205 reported cells.

| model | χ²(model − ours)/205 | shape at COL40 | shape at ROW0 |
|---|---|---|---|
| GENIE 2.12.6 | 3.80 | +12.0 % | +7.2 % |
| + QE RPA | 5.96 | +15.9 % | +8.9 % |
| + non-resonant pion tune | 6.92 | +15.0 % | +13.7 % |
| + low-recoil enhancement | 9.60 | +13.8 % | +12.0 % |
| MINERvA Tune v1 | 1.57 | +14.7 % | +7.2 % |
| Tune v1 + low-Q² pion (MINOS) | 20.5 | +16.2 % | −29.3 % |
| MINERvA Tune v2 | 35.7 | +17.9 % | −29.9 % |

Shape is the region ratio model/ours, normalized to all 205 cells. Each single modification moves COL40 by −2.6 to −4.1 %
absolute, against −4.1 to −7.3 % on the total.

The declared rules read UPSTREAM at COL40 (+12.0 % against +14.7 %) and at ROW0 (+7.2 % against +7.2 %).

## Limitation

Every shipped model, bare GENIE included, is compared here with our **tuned** CV truth. A gap against bare GENIE
therefore cannot separate:
- a difference that exists before any reweight (flux, target, truth definition, sample); from
- our tune reweights pulling our truth away from theirs.

Settling it needs our own bare-GENIE truth, from the same events with the tune weights off. That is an event-loop run and
has not been done. Until then, the reading means only this: shipped bare GENIE is already about 12 % above our tuned
truth at 40–60.

This test is about the truth-level model difference. On its own it does not explain the reco-level column excess. In
`../wstest`, reweighting the column's truth to the shipped model moved the reco residual only from 10.0 % to 8.8 %.
