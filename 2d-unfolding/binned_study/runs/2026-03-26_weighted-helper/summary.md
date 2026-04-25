# Binned debug run: weighted-helper

## Run label
- `2026-03-26_weighted-helper`

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
  --out Documents/binned_study/runs/2026-03-26_weighted-helper/outputs/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5
- Engine: **helper** (direct `binned_omnifold` + efficiency correction)
- `--use-weights`: yes
- Response weight mode: truth
- Hunfold mode: counts
- Response POT scale: data/MC = 0.220501

## Key normalization checks
- `hDataReco` in-range: 496683
- `hBkgReco` in-range: 47659.4
- `hMeasSub` in-range: 449024
- `hTruthSel` in-range: 433804
- unfolded in-range: 85786
- `response.Htruth()` in-range: 433804
- `response.Hmeasured()` in-range: 398745
- `data-bkg / response.Hmeasured`: **1.12609**
- `data-bkg / unfolded`: **5.23423**
- `measSub / truthSel`: 1.03508

## Response fill summary
- sum_w_fill: 398741
- sum_w_miss: 35063.3
- sum_w_fake: 3.82167

## Outputs
- ROOT file: `outputs/omnifold_ptmu_unfold.root`

## Verdict
- **reproduced old failure** (identical to wrapper engine)

## Notes
- The helper engine produces *exactly the same* normalization ratios as the wrapper engine (5.23423).
- This confirms the issue is not in the RooUnfoldOmnifold C++ wrapper specifically — the underlying `binned_omnifold` Python helper has the same behavior.
- The `import_binned_helper` path was fixed from `parents[1]` to `parents[3]` before this run.
- Both engines agree on the unfolded integral (85786) despite different code paths: wrapper uses `RooUnfoldOmnifold.Hunfold()`, helper uses `binned_omnifold()` + manual efficiency division.
