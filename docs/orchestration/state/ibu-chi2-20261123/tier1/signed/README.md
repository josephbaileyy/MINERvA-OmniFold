# Signed-target IBU on the paper's pT edges (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). It follows [`../README.md`](../README.md) (Tier 1).
Joseph asked for it, and the director gave GO. It is `2d-unfolding/ibukt/signed_data.py`
(`OUTCOME-20261119-ibu-signed-data.md`), rerun on the paper's pT edges.
- **Where:** login02, outside Slurm, nice 19, 0 node-h.
- **Declaration:** [`SD-DECLARATION.txt`](SD-DECLARATION.txt), sha256 `e3fe7fa42a587fe9f1a7a1aee561d32977e6beb75ccf57ccce58b202f2c7942f`.

**Result: PASS.** On the paper's edges the signed-target IBU's χ²/205 against the published result is **0.474 at
K = 10**. That is a little below the refined (Stay Positive) target's 0.538, as it was on our edges.

| IBU χ²/205 vs published | K = 5 | K = 10 |
|---|---|---|
| signed, our edges (OUTCOME-20261119) | 0.816 | 0.961 |
| refined, our edges | 0.830 | 1.027 |
| **signed, paper's edges** | **0.380** | **0.474** |
| refined, paper's edges (Tier 1, reproduced here) | 0.395 | 0.538 |

E_R's distance on the paper's edges is reproduced at 434.894 / 205 = 2.1214.
The refined target is the adopted analysis path; the signed target is the descriptive sensitivity check.

## Controls, and what they test

The script's own checks all pass ([`readout.json`](readout.json)):
- the replayed truth prior and the refined K = 5 and K = 10 cross sections equal the archived inputs exactly (max
  differences 0.0);
- RooUnfold and NumPy agree to 2.3e-15 and 2.7e-15;
- E_R's distance and the refined distances match the asserted values.

**The asserted values (434.894… and the rounded 0.39 / 0.54) are Tier 1's own outputs**, and the "archived" inputs are
Tier 1's paper-edge `er.root` and `c2_central.npz`. So these checks test that this run *reproduces Tier 1*. They are
not an independent physics control. The physics control for the paper-edge build is Tier 1's OLD-edge reproduction of
E_R (8e-12) and of the committed distances.

## How it ran

- **Code:** a fresh clone of main `f00ed54b` (`tier1/impl_e`). [`impl_e.diff`](impl_e.diff) (21abe6e1…) changes 8 lines
  in 2 files:
  - signed_data.py's REFERENCE_DRIVER (the patched Tier-1 driver 677ac75f…), its asserted E_R χ², and its asserted
    refined distances;
  - ibukt/config.json's `pt_edges` and its `er` / `c2` input pins.
  
  The reference deploy is Tier 1's `deploy_e`. Prepared by [`sd_prepare.sh`](sd_prepare.sh) →
  [`sd_prepare.out`](sd_prepare.out).
- **Before running** ([`sd_presubmit.txt`](sd_presubmit.txt), 22:24:22Z): impl_e's signed_data.py was 34749511… and
  config.json 49efcdff…. The six stage copies equalled their pins: cv 43f8cc16, flux d40aea69, er 5171c7b8,
  c2 b6cb6142, paper 6c6dce72, libRooUnfold 0b34e1e3.
- **Run log:** [`sd_run.log`](sd_run.log), rc 0. The outputs (readout.json, signed_data.npz and historical_identity.root,
  the last not committed) have the shas in [`sd_out.sha256`](sd_out.sha256).
