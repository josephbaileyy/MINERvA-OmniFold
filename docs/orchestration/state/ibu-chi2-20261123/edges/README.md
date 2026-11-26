# Edges: MINERvA's pT bin edges are 0.075 / 0.325 / 0.475, not 0.07 / 0.33 / 0.47 (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). It is part of the chain in [`../README.md`](../README.md).
It runs locally, apart from one read-only histogram step on login02 (0 node-h), with Joseph's go.

**Declared reading: EDGES-CONFIRMED.** The published 2D result's pT edges appear to be

  0, 0.075, 0.15, 0.25, 0.325, 0.40, 0.475, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50

where our analysis uses 0.07, 0.33 and 0.47 at three of them (`MINERvA101/MINERvA-101-Cross-Section/util/Binning.h:6`,
and about 65 files in the repo). This affects every bin-by-bin comparison with the published cross section in pT rows
0, 1, 3, 4, 5 and 6. Nothing has been changed in shared code. What to do about it is Joseph's and the director's call.

## Evidence

0. **The release's own histogram, which settles it.** The published result's `pt_pl_cross_section` in
   `cov_ptpl_minerva_inclusive_6GeV.root` (sha256 `6c6dce72…`, the release file the repo uses throughout) stores the
   pT axis as 0, 0.075, 0.15, 0.25, 0.325, 0.4, 0.475, 0.55, … ([`root_axis.py`](root_axis.py) →
   [`root_axis.out`](root_axis.out)). Codex-personal pointed to it, and the output here is my own read. Two repo
   scripts dismiss that axis on purpose: `2d-unfolding/compare_to_paper_interior.py:38` ("authoritative — NOT the
   TH2D axis labels") and `2d-unfolding/normalize_xsec_shape.py:51` ("not the cosmetic TH2D labels"). Both treat
   `bin_mapping.txt`, which is printed to two decimals, as the authority over the exact axis.
1. **The paper's own figures.** The blind vector extraction of Figs. 4 and 5 ([`../resp/extract/`](../resp/extract/))
   measures the drawn pT edges at 0.0760 / 0.0747, 0.3255 / 0.3241 and 0.4757 / 0.4764.
2. **The release's bin file.** `bin_mapping.txt` prints the edges to two decimals as 0.07, 0.33 and 0.47. Printing the
   binary doubles 0.075, 0.325 and 0.475 with `%.2f` gives exactly those strings ([`pct2f.py`](pct2f.py) →
   [`pct2f.out`](pct2f.out)): 0.075 is 0.07499999999999999722,
   0.325 is 0.32500000000000001110 and 0.475 is 0.47499999999999997780. The file cannot tell 0.07 from 0.075.
3. **The lead author's tutorial.** `MINERvA101/MINERvA-101-Cross-Section/runEventLoop.cpp:407` defines
   `dansPTBins = {0, 0.075, 0.15, 0.25, 0.325, 0.4, 0.475, 0.55, 0.7, 0.85, 1, 1.25, 1.5, 2.5, 4.5}`.
   `../../2d-closeout/stageA/REPORT.md:168-172` noticed these edges in the flux file, but took `bin_mapping.txt`'s
   0.07 / 0.33 / 0.47 as the paper's edges.
4. **The data.** This declared test ([`DECLARATION.txt`](DECLARATION.txt), sha256 `fa4ab40b8c0ec302813a8760d2dc0a99b26ec4cbbfcfcf6a7d56d4087e6ff441`) rebins our selected data with
   both edge sets ([`hists_remote.py`](hists_remote.py) → [`hists.json`](hists.json)). It compares each with the Fig. 2
   extraction ([`../fig2/`](../fig2/README.md)), with their counts recomputed using the matching cell areas
   ([`edgetest.py`](edgetest.py) → [`run.log`](run.log)). Control C-REP passes: with our edges, the rebinned counts equal
   BASE_N exactly.

| pT row | 0 | 1 | 2 | 3 | 4 | 5 | 6 | misfit X |
|---|---|---|---|---|---|---|---|---|
| our edges, ours/theirs | 0.915 | 0.971 | 0.999 | 1.012 | 1.008 | 0.997 | 1.001 | 104.9 |
| 0.075/0.325/0.475 | 0.986 | 0.999 | 0.999 | 1.001 | 1.001 | 1.002 | 1.002 | 19.4 |

The rows whose edges change move to within 1.5 % of 1, as declared. Row 2 (0.15–0.25), whose edges are the same in
both sets, does not move. A distribution roughly flat in pT² predicts our edges' row 0 and row 1 at −6.7 % and −2.2 %,
close to the −8.5 % and −2.9 % seen.

**Impact.** [`IMPACT-INVENTORY.md`](IMPACT-INVENTORY.md) lists every place in the repo that reads the published
products or compares with them, classified. Note that our grid is hard-coded in `2d-unfolding/driver_p1.py:32` and three
other drivers. `util/Binning.h` is included nowhere.

## What it explains in this chain

- **The low-pT "deficit" against Fig. 2** (fig2: our data and MC both about 7 % low, with equal data/MC) is this edge
  difference. It is not physics, and it is not a beam-axis convention ([`../axis/`](../axis/README.md)).
- **The fold test's low-pT row** (`../foldtest`, ROW −5.4 %) compares published densities over the 0–0.075 bin with our
  0–0.07 bin. It should be re-read once the edges are corrected.
- **The IBU-vs-published χ²/205 = 1.03**, and every comparison of ours with the published cross section in those rows,
  compares different bins. Its value with the corrected edges is not known yet.
