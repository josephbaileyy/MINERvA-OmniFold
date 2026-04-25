# Binned debug run: helper-truth-axis-fix-nominal

## Run label
- `2026-03-29_helper-truth-axis-fix-nominal`

## Command
```bash
python3 Documents/binned_study/scripts/unfold_ptmu_omnifold_binned.py \
  --omnifile Documents/runEventLoopOmniFold.root \
  --datafile Documents/runEventLoopData.root \
  --datahist pTmu_data \
  --iters 5 \
  --use-weights \
  --engine helper \
  --response-weight-mode truth \
  --hunfold-mode counts \
  --verbose \
  --out Documents/binned_study/runs/2026-03-29_helper-truth-axis-fix-nominal/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5
- Engine: helper (`binned_omnifold`)
- `--use-weights`: yes
- Response weight mode: truth
- Hunfold mode: counts
- Response-axis repair: enabled
- Helper truth-axis repair: enabled

## Key normalization checks
- `hMeasSub` in-range: 449024
- `hTruthSel` in-range: 433804
- unfolded in-range: 694343
- `response.Hmeasured()` in-range: 398745
- `data-bkg / response.Hmeasured`: **1.12609**
- `data-bkg / unfolded`: **0.646688**

## Verdict
- **Truth-axis output bug fixed. The helper result now lands on the correct variable-width truth bins, but the normalization overshoot is larger than previously estimated.**

## Notes
- The previous post-response-fix nominal helper output used equal-width truth bins and therefore applied `Vefficiency()` to the wrong truth-bin grouping.
- This rerun is the first helper output with both the response-axis fix and the truth-axis output fix in place.
