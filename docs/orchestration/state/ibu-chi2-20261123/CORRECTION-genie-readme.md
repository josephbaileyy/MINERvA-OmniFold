# CORRECTION 2026-11-23: "χ²(ours vs shipped)/ndf = 1.57 (MC-stat-limited)" does not hold as an attribution

**The statement.** `3d-unfolding/genie/README.md:110-112` (Stage B) reads: "reproduces the shipped
`model_ptpl…Tune_v1.txt` to 0.01 % in normalisation (σ/data 0.9125 vs 0.9124); χ²(ours vs shipped)/ndf = 1.57
(MC-stat-limited)".

**The measurement** ([`truthtest/`](truthtest/), declared at `69efb1aa…` before computing). The comparison uses our
Tune v1 truth from the current 2D CV MC (`43f8cc16…`, read through E_R's `xsec.root` `a5c13fc3…`: `hTruth2D` ×
`hXSec2D`/`hUnfold2D`). It is made against the shipped model on the published `TotalCovariance`, over 205 cells.
- χ²/205 = **1.572**. The 1.57 reproduces.
- Null baselines, 2000 toys each:
  - three-significant-figure rounding alone: median 0.008, 99th percentile 0.011;
  - rounding plus our MC statistics: 99th percentile 0.22 for σ² and 0.43 for 2σ².
- The pull RMS in our MC-statistical units is 8.2. Only 33 of 205 cells match to three significant figures, against
  57–71 expected under MC noise.
- The declared reading is **SYSTEMATIC**.

**The correction.** The difference is systematic, not MC-statistical. Shipped/ours − 1 rises with p‖ to +16–20 % at
40–60 GeV/c, flat in pT, and is +6–9 % in the lowest pT row, flat in p‖. Elsewhere it is mostly within 1–2 %. Only the
"MC-stat-limited" attribution is corrected. The normalisation sentence was made on the older 3D omnifile, which this
measurement did not use, so it is left as written. On the current CV the 205-cell total ratio shipped/ours is 1.0048.
The README gains a dated correction under the bullet, and the original text is kept.

**Not citable for:** a cause of the difference, or which prediction is right.
