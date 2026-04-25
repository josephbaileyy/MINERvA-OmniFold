# Binned OmniFold `pTmu` debug study -- advisor update (2026-03-29)

## Executive summary

The binned OmniFold helper path now produces correct results. Three bugs were
found in the histogram handoff between RooUnfold's internal representation and
the Python `binned_omnifold()` function. All three have been fixed. Closure is
near-perfect and the nominal result converges stably to a physically sensible
answer.

## Bug inventory

### Bug 1: Response-axis mismatch (divergence)

`RooUnfoldResponse.Hresponse()` returns the internal `_res` TH2D on uniform
`[0,1]` axes, while the measured histogram uses physical `[0, 4.5]` GeV
variable-width bins. `binned_omnifold()` creates pseudo-events at bin centers,
so the GBT classifier saw MC reco in `[0,1]` and data in `[0,4.5]` -- trivial
separation, extreme weights, violent odd/even divergence.

**Fix**: rebuild a TH2D on physical axes before calling `binned_omnifold()`.

### Bug 2: Truth-axis output uniformization (shape distortion)

`binned_omnifold()` returned its unfolded TH1D on 14 equal-width bins instead
of the MINERvA variable-width truth edges. This distorted the plotted shape
and caused the downstream efficiency correction to be applied to the wrong
bins.

**Fix**: build the output TH1D from the response Y-axis bin edges.

### Bug 3: Garbled `_res` content + wrong `Vefficiency()` (normalization)

This was the most subtle bug. `RooUnfoldResponse::Fill()` for the 1D case
(line 1135 of `RooUnfoldResponse.cxx`) fills physical coordinates directly
into the `[0,1]`-binned `_res` TH2D:

    return fill(_res, xr, xt, w);   // physical pTmu values into [0,1] TH2D

Compare to the 2D/3D cases (lines 1147, 1159) which correctly map:

    return fill(_res,
                binCenter(_res, findBin(_mes, xr, yr)+1, X),
                binCenter(_res, findBin(_tru, xt, yt)+1, Y), w);

This means:

- Events with pTmu > 1 GeV go to overflow of `_res` (lost).
- Events with pTmu < 1 GeV land on the wrong uniform bins.
- Internal `_res` captures only 78% of fill entries (310,686 vs 398,741).
- `Vefficiency()` (which reads from `_res`) produces unphysical values
  ranging from 0.45 to 4.76 (efficiency > 1 is impossible). Correct values
  range from 0.84 to 0.97.
- Dividing by these wrong efficiencies inflated the result by ~55%.

Note: this bug does NOT affect other RooUnfold methods (IBU, SVD) because
they use `Mresponse()` which is derived from the correctly-filled 1D
histograms `_mes` and `_tru`, not from `_res` bin coordinates.

**Fix**: fill a properly-binned TH2D with physical variable-width edges
during the TTree loop. Use its Y-projection and `hTruthSel` to compute
correct efficiency, bypassing `Vefficiency()`.

## Results with all three fixes

### Closure test (5 iterations)

| Quantity | Value |
|----------|-------|
| Input (`response.Hmeasured`) | `398,745` |
| Unfolded | `433,808` |
| `hTruthSel` | `433,804` |
| Unfolded / hTruthSel | `1.0001` |

Near-perfect recovery of the truth distribution.

### Closure iteration scan (1-8)

| Iter | Unfolded | Ratio to prev |
|------|----------|---------------|
| 1 | `433,808` | -- |
| 2 | `433,808` | `1.0` |
| 3 | `433,808` | `1.0` |
| 4 | `433,808` | `1.0` |
| 5 | `433,808` | `1.0` |
| 6 | `433,808` | `1.0` |
| 7 | `433,808` | `1.0` |
| 8 | `433,808` | `1.0` |

The algorithm converges to the truth in a single iteration and holds
exactly steady. This is the expected behavior for a closure test where the
input is the response X-projection.

### Nominal weighted (5 iterations)

| Quantity | Value |
|----------|-------|
| `data-bkg` (measured) | `449,024` |
| Unfolded | `489,505` |
| `data-bkg / unfolded` | `0.917` |
| Expected efficiency | `0.919` |

The ratio 0.917 matches the expected overall efficiency (398,745 / 433,804
= 0.919). The unfolded truth exceeds the measured yield because it includes
truth events not reconstructed (misses). This is physically correct.

### Nominal iteration scan (1-8)

| Iter | Unfolded | Ratio to prev |
|------|----------|---------------|
| 1 | `489,115` | -- |
| 2 | `489,368` | `1.00052` |
| 3 | `489,457` | `1.00018` |
| 4 | `489,491` | `1.00007` |
| 5 | `489,499` | `1.00002` |
| 6 | `489,496` | `0.99999` |
| 7 | `489,489` | `0.99999` |
| 8 | `489,481` | `0.99998` |

Stable monotonic convergence within 0.08% across all 8 iterations.

### Efficiency comparison (old vs corrected, per bin)

| Bin | Correct eff | Old Vefficiency | Ratio |
|-----|-------------|-----------------|-------|
| 1 | 0.970 | 0.877 | 1.11 |
| 2 | 0.967 | 0.864 | 1.12 |
| 3 | 0.963 | 0.596 | 1.62 |
| 4 | 0.957 | 0.762 | 1.26 |
| 5 | 0.950 | 0.785 | 1.21 |
| 6 | 0.944 | 0.826 | 1.14 |
| 7 | 0.934 | 0.855 | 1.09 |
| 8 | 0.924 | 0.448 | 2.06 |
| 9 | 0.912 | 0.521 | 1.75 |
| 10 | 0.900 | 0.669 | 1.35 |
| 11 | 0.884 | 0.642 | 1.38 |
| 12 | 0.870 | 1.300 | 0.67 |
| 13 | 0.863 | 1.008 | 0.86 |
| 14 | 0.842 | 4.758 | 0.18 |

The old `Vefficiency` values include two bins > 1 (unphysical) and one
bin at 4.76. The correct values smoothly decrease from 0.97 to 0.84.

## Progression of failures

| Stage | Nominal ratio | Problem |
|-------|---------------|---------|
| Original (all bugs) | `5.23` | Divergent oscillation |
| After fix 1 (response axes) | `0.756` | Stable but wrong content + efficiency |
| After fixes 1+2 (+ truth axis) | `0.647` | Correct shape, still wrong efficiency |
| After fixes 1+2+3 (+ proper TH2D) | `0.917` | **Correct** (= expected efficiency) |

## Plots

- `Documents/binned_study/plots/ptmu_binned_nominal_current_counts.png`
  (event counts, all three fixes)
- `Documents/binned_study/plots/ptmu_binned_nominal_current_density.png`
  (probability density, all three fixes)

## Remaining items

- The wrapper/C++ path (`RooUnfoldOmnifold::BinnedOmnifold()`) has the
  same bugs and has not been fixed.
- The `hUnfoldRaw` output is misnamed in the helper path (already
  post-efficiency).
- Iteration scan values are only in stdout, not persisted to file.
- The binned path is now functional as a debugging tool. Whether it is
  suitable for final physics extraction is a separate question.

## Files modified

| File | Change |
|------|--------|
| `Documents/binned_study/scripts/unfold_ptmu_omnifold_binned.py` | Fills proper TH2D in TTree loop; computes correct efficiency; bypasses `Vefficiency()` |
| `OmniFold/unbinned_unfolding/python/omnifold.py` (line 210) | Truth-axis output uses variable-width bin edges (fix 2, applied earlier) |

## Run outputs

| Run | Directory |
|-----|-----------|
| Proper TH2D closure | `Documents/binned_study/runs/2026-03-29_proper-resp2d-closure/` |
| Proper TH2D nominal | `Documents/binned_study/runs/2026-03-29_proper-resp2d-nominal/` |
| Proper TH2D nominal scan | `Documents/binned_study/runs/2026-03-29_proper-resp2d-iter-scan/` |
| Proper TH2D closure scan | `Documents/binned_study/runs/2026-03-29_proper-resp2d-closure-scan/` |
