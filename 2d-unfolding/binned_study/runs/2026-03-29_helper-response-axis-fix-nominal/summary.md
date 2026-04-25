# Binned debug run: helper-response-axis-fix-nominal

## Run label
- `2026-03-29_helper-response-axis-fix-nominal`

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
  --out Documents/binned_study/runs/2026-03-29_helper-response-axis-fix-nominal/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5
- Engine: helper (`binned_omnifold`)
- `--use-weights`: yes
- Response weight mode: truth
- Hunfold mode: counts
- Response POT scale: data/MC = 0.220501
- Response-axis repair: enabled in helper path

## Key normalization checks
- `hMeasSub` in-range: 449024
- `hTruthSel` in-range: 433804
- unfolded in-range: 594238
- `response.Hmeasured()` in-range: 398745
- `data-bkg / response.Hmeasured`: **1.12609**
- `data-bkg / unfolded`: **0.755629**

## Verdict
- **Axis mismatch fixed, divergence removed, but normalization now overshoots by ~32%.**

## Notes
- The rebuilt response TH2 preserves the original matrix contents but changes the axes from internal `[0,1]` to physical `[0,4.5]` GeV.
- This run shows that the old catastrophic under-normalization was caused by the response-coordinate bug.
- The remaining issue is now a stable normalization bias, not an unstable iteration.
