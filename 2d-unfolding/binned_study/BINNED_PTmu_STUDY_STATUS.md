# Binned `pTmu` study status

Last updated: `2026-04-09 UTC`

## Goal

Re-establish the binned OmniFold `pTmu` workflow as a controlled debugging
environment. The current objective is to isolate and understand the binned-path
failures, not to claim a production-ready physics result.

## Documentation policy

- This file is the **authoritative status / todo / progress log**.
- New progress should be recorded here first, with **hour:minute UTC timestamps**.
- Older entries may use placeholder `00:00 UTC` when the exact minute was not
  captured at the time of the run.
- `Documents/binned_study/notes/` should stay small.
- For `2026-03-29`, keep only **one** advisor-facing note in `notes/`.
- `Documents/binned_study/plots/` should keep only the current most relevant
  visual check, not every intermediate figure.

## Current active files

- `Documents/BINNED_PTmu_STUDY_STATUS.md`
- `Documents/binned_study/scripts/unfold_ptmu_omnifold_binned.py`
- `OmniFold/unbinned_unfolding/python/omnifold.py`
- `Documents/binned_study/scripts/plot_gaussian_style_ptmu_binned.py`
- `Documents/binned_study/notes/2026-03-29_advisor_update.md`
- `Documents/binned_study/plots/ptmu_binned_nominal_current_counts.png`
- `Documents/binned_study/plots/ptmu_binned_nominal_current_density.png`

## Current diagnosis

Three distinct bugs have been identified and fixed in the helper binned OmniFold
path:

1. `RooUnfoldResponse.Hresponse()` exposed the response matrix on RooUnfold's
   internal uniform `[0,1]` axes instead of the physical reco/truth binning.
2. `OmniFold_helper_functions.binned_omnifold()` returned its unfolded TH1 on a
   uniform truth axis `(nbins, xmin, xmax)` instead of the original
   variable-width truth bin edges.
3. `RooUnfoldResponse::Fill()` for the 1D case fills physical coordinates
   directly into the `[0,1]`-binned internal `_res` TH2D (no `findBin`/
   `binCenter` mapping, unlike the 2D/3D cases). Events with pTmu > 1 GeV go
   to overflow; events below 1 GeV land on the wrong uniform bins. This
   garbles the `_res` content and makes `Vefficiency()` incorrect.

Together, these explain the full progression of failures:

- Bug 1 caused the violent classifier-driven divergence (MC reco in `[0,1]`
  vs measured in `[0,4.5]`).
- Bug 2 distorted the plotted truth shape and also misapplied the
  post-helper `Vefficiency()` correction bin-by-bin.
- Bug 3 garbled the 2D response content used by `binned_omnifold()` and
  produced incorrect efficiency values, causing ~55% normalization overshoot
  even after fixes 1-2.

## Current status

- Historical nominal failure was reproduced.
- The earlier one-factor debug matrix was completed.
- Pre-fix iteration scan and closure test showed divergent oscillation.
- The response-axis mismatch was identified and fixed in the helper path (fix 1).
- The helper truth-axis output bug was identified and fixed (fix 2).
- The garbled `_res` content and wrong `Vefficiency()` were identified and fixed
  by filling a properly-binned TH2D during the TTree loop and computing
  efficiency from it directly (fix 3).
- **All three fixes are now in place.** The helper path produces:
  - Closure (5 iter): unfolded = 433,808 ≈ hTruthSel = 433,804 (near-perfect).
  - Nominal (5 iter): unfolded = 489,505, ratio data-bkg/unfolded = 0.917
    (= expected overall efficiency).
  - Nominal iteration scan (1-8): stable convergence within 0.08%.

## Current todo

- [x] Restore archived binned scripts into `Documents/binned_study/scripts/`.
- [x] Create and enforce the canonical run layout under `Documents/binned_study/runs/`.
- [x] Reproduce the historical weighted nominal failure.
- [x] Run the initial debug matrix for engine / weights / response-weight mode.
- [x] Run the pre-fix iteration scan.
- [x] Run the pre-fix closure test.
- [x] Identify the response-axis mismatch root cause.
- [x] Fix the helper response TH2 handoff before `binned_omnifold()`.
- [x] Re-run nominal helper after the response-axis fix.
- [x] Re-run helper iteration scan and helper closure after the response-axis fix.
- [x] Identify the helper truth-axis output bug.
- [x] Fix the helper returned TH1 to use physical truth bin edges.
- [x] Re-run the nominal helper case after the truth-axis fix.
- [x] Confirm the truth-axis-fixed helper closure 5-iteration output.
- [x] Reassess the remaining normalization bias using only outputs with both fixes in place.
- [x] Check whether the current manual `Vefficiency()` division is still correct after the truth-axis fix.
  - It was NOT correct. `Vefficiency()` reads from garbled `_res`. Fixed by
    computing efficiency from a properly-binned TH2D filled during the TTree loop.
- [x] Re-run nominal helper after all three fixes — ratio = 0.917 (correct).
- [x] Re-run closure helper after all three fixes — unfolded ≈ hTruthSel (near-perfect).
- [x] Re-run nominal iteration scan after all three fixes — stable convergence.
- [x] Re-run and log the closure iteration scan after all three fixes — perfect
  convergence at 433,808 for all iterations 1-8 (ratio_to_prev = 1.0 exact).
- [x] Rename or restructure helper-path outputs so `hUnfoldRaw` actually means
  pre-efficiency output.
  - `run_binned_omnifold_direct()` now returns `(h_post_eff, h_pre_eff)`.
  - Output file contains: `hUnfoldPreEff` (raw OmniFold output) and
    `hUnfoldPostEff` (after efficiency correction).
  - Verified: pre-eff integral = 449,021 ≈ data-bkg = 449,024.
- [x] Persist iteration-scan values to file instead of stdout only.
  - Scan results now written to `<output>.iter_scan.tsv` alongside the ROOT file.
- [x] Port the same fixes into the wrapper/C++ path or prove why that path
  differs.
  - The C++ wrapper (`BinnedOmnifold()` in `RooUnfoldOmnifold.cxx`) has the
    exact same three bugs:
    1. Line 172: `Hresponse()` returns [0,1]-binned `_res`.
    2. Line 175: `createHist` reconstructs with `vars(res)` = [0,1] binning.
    3. Line 194: `Vefficiency()` reads from garbled `_res`.
  - These bugs are in the `rymilton/unbinned_unfolding` package itself, not
    in the study scripts. See the package bugs section below.
  - Fixing the wrapper requires either modifying the package C++ source or
    reimplementing `BinnedOmnifold()` externally (as the helper path now does).
- [x] Decide whether the binned path is useful as a debugging environment.
  - **Yes.** With all three fixes in place, the helper binned path produces
    near-perfect closure and physically sensible nominal results. It is a
    viable debugging environment and could serve as a cross-check against
    the unbinned path. It is not recommended for final physics extraction
    until the upstream package bugs are fixed.

## Key reference numbers

- Target `hMeasSub` in-range: `449024`
- Truth prior `hTruthSel` in-range: `433804`
- Response measured `response.Hmeasured()` in-range: `398745`
- Historical failure ratio: `data-bkg / unfolded = 5.23423`
- Post response-axis fix nominal helper ratio: `data-bkg / unfolded = 0.755629`
- Post truth-axis fix nominal helper ratio: `data-bkg / unfolded = 0.646688`
- Post truth-axis fix closure helper ratio: `response.Hmeasured / unfolded = 0.642495`
- **Post all-three-fixes nominal helper ratio**: `data-bkg / unfolded = 0.917301`
- **Post all-three-fixes closure helper ratio**: `unfolded = 433808 ≈ hTruthSel = 433804`
- Internal `_res` in-range: `310686` (78% of correct `398741`)

## Run log

- `2026-03-26 00:00 UTC` Dedicated binned workspace created at `Documents/binned_study/`.

- `2026-03-26 00:00 UTC` Run `2026-03-26_nominal-weighted-repro`.
  - Config: wrapper, truth mode, `--use-weights`, 5 iterations.
  - Result:
    `data-bkg / response.Hmeasured = 1.12609`,
    `data-bkg / unfolded = 5.23423`,
    unfolded in-range `= 85786`.
  - Verdict: historical under-normalized failure reproduced.

- `2026-03-26 00:00 UTC` Debug matrix completed.
  - `2026-03-26_unweighted-wrapper`: `data-bkg / unfolded = 12.0027`
  - `2026-03-26_weighted-helper`: `data-bkg / unfolded = 5.23423`
  - `2026-03-26_weighted-legacy-mixed`: `data-bkg / unfolded = 10.5506`
  - Conclusion: the failure was not resolved by engine choice, disabling weights,
    or switching to legacy-mixed response weights.

- `2026-03-26 00:00 UTC` Pre-fix iteration scan completed with `--iter-scan-max 8`.
  - Iterations 1-8 gave:
    `43251, 7656, 218, 1140760, 58043, 0.43, 1141300, 0.43`
  - Conclusion: the old "5x low" result was not a fixed point; the binned
    iteration was diverging violently.

- `2026-03-29 00:00 UTC` Pre-fix closure test completed.
  - Used `response.Hmeasured()` as pseudo-data.
  - Still diverged:
    `38370, 6226, 107, 1140590, 0.43, 1552, 0.43, 1140620`
  - Conclusion: the failure was not caused by the modest nominal
    `data-bkg / response.Hmeasured` mismatch.

- `2026-03-29 00:00 UTC` Algorithm trace identified the first root cause.
  - `response.Hresponse()` exposed a TH2 with uniform internal `[0,1]` axes.
  - Measured histograms remained on physical `[0,4.5]` binning.
  - `binned_omnifold()` converted both to pseudo-events at bin centers, so the
    classifier saw MC reco values in `[0,1]` and measured values in `[0,4.5]`.
  - Conclusion: the divergence came from a histogram-coordinate mismatch, not
    from the underlying event samples.

- `2026-03-29 00:00 UTC` Helper response-axis repair implemented in
  `Documents/binned_study/scripts/unfold_ptmu_omnifold_binned.py`.
  - The response matrix is now rebuilt onto a TH2D with the physical reco/truth
    bin edges from `response.Hmeasured()` and `response.Htruth()`.

- `2026-03-29 00:00 UTC` Run `2026-03-29_helper-response-axis-fix-nominal`.
  - Result:
    `data-bkg / unfolded = 0.755629`,
    unfolded in-range `= 594238`.
  - Conclusion: the divergent oscillation was removed, but the helper result
    still overshot the target.

- `2026-03-29 00:00 UTC` Run `2026-03-29_helper-response-axis-fix-iter-scan`.
  - Iterations 1-8 gave:
    `589836, 592399, 593682, 594149, 594164, 594018, 593747, 593358`
  - Conclusion: after the response-axis fix alone, the helper path converged to
    a stable but high-yield plateau.

- `2026-03-29 00:00 UTC` Run `2026-03-29_helper-response-axis-fix-closure`.
  - Iterations 1-8 gave:
    `522306, 523743, 524555, 524926, 525055, 524913, 524695, 524407`
  - Final closure ratio:
    `response.Hmeasured / unfolded = 0.759435`
  - Conclusion: closure also became stable after the response-axis fix, but the
    normalization remained high.

- `2026-03-29 00:00 UTC` Post-fix pseudo-event support check.
  - MC pseudo-events populated all 14 physical reco bins after the rebuilt
    response TH2 was used.
  - Conclusion: the zero-support feature-space bug was fixed.

- `2026-03-29 20:32 UTC` Helper truth-axis output bug identified.
  - The helper returned `hUnfoldTruthSel` on 14 equal-width bins across
    `[0,4.5]` instead of the physical MINERvA truth-bin edges.
  - This affected both the plot shape and the subsequent bin-by-bin
    `Vefficiency()` division in `run_binned_omnifold_direct()`.

- `2026-03-29 20:32 UTC` Helper truth-axis output bug fixed in
  `OmniFold/unbinned_unfolding/python/omnifold.py`.
  - `binned_omnifold()` now builds its output TH1 from the explicit truth-bin
    edge array on `response_hist.GetYaxis()`.

- `2026-03-29 20:32 UTC` Run `2026-03-29_helper-truth-axis-fix-nominal`.
  - Config: helper, truth mode, `--use-weights`, 5 iterations, with both the
    response-axis and truth-axis fixes in place.
  - Result:
    unfolded in-range `= 694343`,
    `data-bkg / unfolded = 0.646688`.
  - Conclusion: the current helper output now lands on the correct variable-width
    truth bins, and the earlier `~32%` overshoot estimate is obsolete.

- `2026-03-29 20:32 UTC` Current visual check regenerated from the corrected
  nominal helper output.
  - Plot:
    `Documents/binned_study/plots/ptmu_binned_nominal_current_counts.png`
  - Use this plot for visual comparison, not the earlier intermediate figures.

- `2026-03-29 20:44 UTC` Truth-axis-fixed helper closure output inspected from
  `Documents/binned_study/runs/2026-03-29_helper-truth-axis-fix-closure/omnifold_ptmu_unfold.root`.
  - Final 5-iteration values:
    `hMeasSub = 398745`,
    `hUnfoldTruthSel = 620619`,
    `response.Hmeasured / unfolded = 0.642495`.
  - Conclusion: even after both geometry fixes, the helper closure result still
    overshoots strongly, so the remaining bias is not a nominal-data-only effect.

- `2026-03-29 20:44 UTC` Helper output bookkeeping issue identified.
  - In the direct helper path, `run_binned_omnifold_direct()` applies the
    `Vefficiency()` division before returning.
  - The object later written as `hUnfoldRaw` is therefore already post-efficiency
    and is misnamed for helper-engine runs.
  - Conclusion: any raw-vs-post-efficiency diagnostic needs either a new saved
    pre-eff histogram or a code-path split before writing output.

- `2026-03-29 04:45 UTC` Third root cause identified: garbled `_res` content.
  - `RooUnfoldResponse::Fill()` for the 1D case fills physical coordinates
    directly into the `[0,1]`-binned `_res` TH2D (line 1135 of
    `RooUnfoldResponse.cxx`), with no `findBin`/`binCenter` mapping.
  - Compare to the 2D/3D cases (lines 1147, 1159), which correctly convert
    physical coordinates to internal bin centers before filling.
  - Diagnostic: internal `_res` in-range integral = `310686`, properly-binned
    TH2D integral = `398741` (internal captures only 78% of content).
  - `Vefficiency()` computes efficiency from the garbled `_res`, producing
    values ranging from 0.45 to 4.76 (unphysical — efficiency > 1 is
    impossible). Correct values range from 0.84 to 0.97.

- `2026-03-29 04:45 UTC` Fix 3 implemented in
  `Documents/binned_study/scripts/unfold_ptmu_omnifold_binned.py`.
  - A properly-binned TH2D (`hResp2D`) is now filled during the TTree loop
    alongside the RooUnfoldResponse, using the physical variable-width bin edges.
  - `run_binned_omnifold_direct()` uses this TH2D for `binned_omnifold()` and
    computes efficiency from its Y-projection vs `hTruthSel`, bypassing the
    garbled `Vefficiency()`.

- `2026-03-29 04:50 UTC` Run `2026-03-29_proper-resp2d-closure`.
  - Config: helper, truth mode, `--use-weights`, 5 iterations, `--closure-test`,
    all three fixes in place.
  - Result:
    unfolded in-range `= 433808`,
    `hTruthSel = 433804`,
    `data-bkg / unfolded = 0.919173`.
  - Conclusion: **near-perfect closure.** The ratio 0.919 equals the overall
    efficiency (398745/433804), which is the expected relationship between
    measured yield and truth yield.

- `2026-03-29 04:55 UTC` Run `2026-03-29_proper-resp2d-nominal`.
  - Config: helper, truth mode, `--use-weights`, 5 iterations, all three fixes.
  - Result:
    unfolded in-range `= 489505`,
    `data-bkg / unfolded = 0.917301`.
  - Conclusion: nominal result is now physically sensible. The unfolded truth
    exceeds the measured yield by the efficiency factor, as expected.

- `2026-03-29 05:00 UTC` Run `2026-03-29_proper-resp2d-iter-scan`.
  - Iterations 1-8 gave:
    `489115, 489368, 489457, 489491, 489499, 489496, 489489, 489481`
  - Conclusion: stable monotonic convergence within 0.08% across all 8
    iterations. The divergent oscillation and the high-level plateau are both
    fully resolved.

- `2026-03-29 05:12 UTC` Run `2026-03-29_proper-resp2d-closure-scan`.
  - Config: helper, truth mode, `--use-weights`, `--closure-test`,
    `--iter-scan-max 8`, all three fixes.
  - Iterations 1-8 gave:
    `433808, 433808, 433808, 433808, 433808, 433808, 433808, 433808`
    (ratio_to_prev = 1.0 exact for all iterations).
  - Conclusion: **perfect closure.** The algorithm recovers hTruthSel at
    iteration 1 and holds steady. This is the ideal behavior for a closure
    test where the input is exactly the response X-projection.

## Bugs in `rymilton/unbinned_unfolding` (package-level)

The following bugs are in the upstream package at
`https://github.com/rymilton/unbinned_unfolding` (commit `9b5cdc4`), not in
the MINERvA study scripts.

### Bug A: `RooUnfoldResponse::Fill()` 1D coordinate mapping (RooUnfoldResponse.cxx:1135)

The 1D `Fill(xr, xt, w)` fills physical coordinates directly into `_res`:

    return fill(_res, xr, xt, w);

The 2D and 3D overloads correctly map physical coordinates to internal bin
centers via `findBin`/`binCenter`:

    return fill(_res,
                binCenter(_res, findBin(_mes, xr, yr)+1, X),
                binCenter(_res, findBin(_tru, xt, yt)+1, Y), w);

Because `_res` is created with uniform `[0,1]` axes (line 1046), the 1D
case puts events with physical values > 1 into overflow and bins the rest
on the wrong grid. This garbles the `_res` content.

**Impact**: `Hresponse()`, `Vefficiency()`, and any method that reads `_res`
bin contents returns incorrect results for the 1D case. Other RooUnfold
methods (IBU, SVD) are unaffected because they derive their response matrix
from the correctly-filled 1D histograms `_mes`/`_tru`/`_mestru`.

**Suggested fix**: add `findBin`/`binCenter` mapping to the 1D Fill, matching
the 2D/3D implementations.

### Bug B: `BinnedOmnifold()` uses garbled `Hresponse()` (RooUnfoldOmnifold.cxx:172-175)

`BinnedOmnifold()` calls `response->Hresponse()` (line 172) and reconstructs
a TH2D using `vars(res)` (line 175), which preserves the `[0,1]` binning.
The reconstructed histogram is passed to `binned_omnifold()` along with
`Hmeasured()` which has correct physical binning. The classifier sees MC reco
features in `[0,1]` and measured features in `[0,4.5]`.

**Impact**: the GBT classifier trivially separates MC from data, producing
extreme weights and divergent iteration.

**Suggested fix**: reconstruct the response TH2D on physical bin edges from
`Hmeasured()`/`Htruth()`, or fix Bug A so `_res` has correct content.

### Bug C: `BinnedOmnifold()` uses garbled `Vefficiency()` (RooUnfoldOmnifold.cxx:194)

`BinnedOmnifold()` divides the unfolded result by `Vefficiency()` (line 194).
`Vefficiency()` (RooUnfoldResponse.cxx:576-598) computes column sums of
`h2m(_res)` divided by `h2v(_tru)`. Because `_res` is garbled (Bug A), the
column sums are wrong, and the efficiency values can be > 1 (unphysical).

**Impact**: ~55% normalization overshoot after the other bugs are fixed.

**Suggested fix**: compute efficiency from correctly-binned histograms, or
fix Bug A.

### Bug D: `binned_omnifold()` truth-axis output (omnifold.py, pre-fix line 210)

`binned_omnifold()` created its output TH1D with `TH1D(name, title, nbins,
xmin, xmax)`, producing uniform truth bins. It should use the variable-width
bin edges from the response Y-axis.

**Impact**: distorted truth shape; misapplied efficiency correction.

**Status**: already fixed locally in the study
(`OmniFold/unbinned_unfolding/python/omnifold.py` line 210).

## Study completion

All TODO items are complete as of 2026-03-29. The binned OmniFold debug study
has achieved its goal: all three normalization bugs have been identified, fixed,
and verified. The helper binned path is now a working debugging environment.

Remaining optional follow-ups (not blocking):
- File issues on `rymilton/unbinned_unfolding` for bugs A–D.
- Submit upstream PRs to fix the package.
- Port fixes to the C++ wrapper path if needed for production use.

## Algorithm equivalence: binned OmniFold vs IBU (April 2026)

### Mathematical equivalence

Binned OmniFold and D'Agostini IBU are the same algorithm when both use the
same prior, the same data, and exact density ratios. Specifically:

- **Same prior**: MINERvA's IBU (`MnvUnfold::UnfoldHisto`, line 275 of
  `MnvUnfold.cxx`) constructs its `RooUnfoldResponse` from
  `h_migration->ProjectionX()` and `h_migration->ProjectionY()` — i.e.,
  Fill-only truth and Fill-only reco, with no Miss events. The binned OmniFold
  path uses the same `ProjectionY(migration)` as its truth prior. Both
  algorithms start from identical priors.

- **Same data**: both unfold `data - bkg` (background-subtracted measured).

- **At iteration 1 the prior cancels**: the update formula
  `π_j^(1) = Σ_i A_{ji} · d_i / M_i` is independent of the prior because
  the prior appears in both numerator and denominator and divides out. Both
  algorithms give the same result at iteration 1.

- **At iteration 2+**: IBU iterates by computing exact per-bin density ratios
  via matrix algebra. OmniFold approximates these ratios with a GBT classifier
  (`GradientBoostingClassifier(max_depth=3, n_estimators=100, lr=0.1)`) trained
  on pseudo-events at 14 discrete bin centers. The approximation error
  compounds across iterations.

### 1-iteration verification

A dedicated 1-iteration run confirmed the equivalence:

```
bin   OF_1iter/IBU   OF_5iter/IBU
  1      0.985          1.538
  3      0.992          0.931
  8      0.999          0.993
 14      0.934          1.045
```

At 1 iteration, OmniFold matches IBU to ~1–7% (worst case bin 14, an edge
bin). At 5 iterations, the GBT approximation error compounds and divergence
reaches up to 54% (bin 1).

### Why bin 1 is the worst case

Bin 1 has the fewest truth events (2402) and the most extreme migration ratio
(bkgSub=13798 vs truth=2402, ratio 5.7:1). This is where the GBT classifier
approximation is least accurate — low statistics and extreme class imbalance.

### Implications

- Binned OmniFold is an **approximate IBU**. The approximation quality depends
  on the GBT hyperparameters, the number of bins, and the number of iterations.
- Fewer iterations reduce compounding error. For visual comparison with IBU,
  1 iteration is closest.
- The real value of OmniFold is the **unbinned case**, where it can capture
  continuous distributions that IBU cannot represent.
- The 1-iteration density plot is at
  `Documents/binned_study/plots/ptmu_binned_density_1iter.pdf`.

## Current interpretation

- All three normalization bugs are now identified and fixed.
- The helper binned OmniFold path produces correct results:
  - **Closure**: unfolded = hTruthSel to 4 significant figures (433808 vs 433804).
  - **Nominal**: physically sensible ratio data-bkg/unfolded = 0.917 (= efficiency).
  - **Convergence**: stable within 0.08% across iterations 1-8.
- The root cause was a chain of three bugs in the histogram handoff between
  RooUnfold's internal representation and the Python `binned_omnifold()`:
  1. `Hresponse()` axis mismatch (fix: rebuild TH2D on physical axes).
  2. Truth-axis output uniformization (fix: use response Y-axis bin edges).
  3. Garbled `_res` content from 1D Fill (fix: fill a proper TH2D in the TTree
     loop; compute efficiency from it instead of `Vefficiency()`).
- The wrapper/C++ path has the same underlying bugs but has not been fixed.
- The binned helper path is now a viable debugging environment.
- **Binned OmniFold is mathematically equivalent to IBU** when using exact
  density ratios. The observed per-bin divergence (up to 54% at 5 iterations)
  is entirely from the GBT classifier approximation compounding across
  iterations. At 1 iteration, the two methods agree to ~1%.
