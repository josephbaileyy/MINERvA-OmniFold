# Axis test: a common beam-axis rotation against Fig. 2's low-pT rows (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). It is part of the chain in [`../README.md`](../README.md).
It runs locally with Joseph's go, on existing products only.

**Declared reading: EDGE: AXIS-NO.** [`DECLARATION.txt`](DECLARATION.txt) (sha256 `cd415f1e37d28a1172223d100b616a2a5f21c93ff0d66290b768c7f6057331bf`),
[`axistest.py`](axistest.py) → [`run.log`](run.log).

The test takes our selected data, rotated by (dx, dy) in ±3 mrad (the evloop `scanA`), and compares the within-slice pT
fractions of rows 0–4 with the Fig. 2 bottom block.
- The best point is on the scan edge, at (+3.0, −0.75) mrad.
- The misfit improves only from 100.6 to 91.0, and row 0 stays at 0.925 of theirs.
- The row-0 deficit is largest at low p‖ (0.87–0.93 at 1.5–4 GeV) and smallest at high p‖. A rotation predicts the
  opposite.

**Why:** the low-pT deficit is the pT edge difference recorded in [`../edges/`](../edges/README.md). Fig. 2's lowest bin
is 0–0.075 and ours is 0–0.07. The axis test compared fractions over different bins, so it could not have closed the
gap.
