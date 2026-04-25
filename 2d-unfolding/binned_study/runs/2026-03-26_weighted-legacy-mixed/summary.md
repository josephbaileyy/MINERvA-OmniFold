# Binned debug run: weighted-legacy-mixed

## Run label
- `2026-03-26_weighted-legacy-mixed`

## Command
```bash
python3 Documents/binned_study/scripts/unfold_ptmu_omnifold_binned.py \
  --omnifile Documents/runEventLoopOmniFold.root \
  --datafile Documents/runEventLoopData.root \
  --datahist pTmu_data \
  --iters 5 \
  --use-weights \
  --engine wrapper \
  --response-weight-mode legacy-mixed \
  --hunfold-mode counts \
  --verbose \
  --out Documents/binned_study/runs/2026-03-26_weighted-legacy-mixed/outputs/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5
- Engine: wrapper (RooUnfoldOmnifold)
- `--use-weights`: yes
- Response weight mode: **legacy-mixed** (Fill/Fake use w_reco, Miss uses w_truth)
- Hunfold mode: counts
- Response POT scale: data/MC = 0.220501

## Key normalization checks
- `hDataReco` in-range: 496683
- `hBkgReco` in-range: 47659.4
- `hMeasSub` in-range: 449024
- `hTruthSel` in-range: 433804
- unfolded in-range: 42559
- `response.Htruth()` in-range: 424814
- `response.Hmeasured()` in-range: 389755
- `data-bkg / response.Hmeasured`: **1.15207**
- `data-bkg / unfolded`: **10.5506**
- `measSub / truthSel`: 1.03508

## Response fill summary
- sum_w_fill: 389751
- sum_w_miss: 35063.3
- sum_w_fake: 3.68489

## Additional checks
- Response truth-vs-hTruthSel mismatch (expected in legacy-mixed): response=424814, hTruthSel=433804, rel=0.0207

## Outputs
- ROOT file: `outputs/omnifold_ptmu_unfold.root`

## Verdict
- **reproduced old failure** (worse than truth-mode)

## Notes
- Legacy-mixed mode makes the failure *worse* (10.55x vs 5.23x under-normalization).
- Using reco-side weights for Fill/Fake introduces a 2% truth mismatch in the response (424814 vs 433804), which is expected behavior for mixed-weight mode.
- The response.Hmeasured is also slightly lower (389755 vs 398745 in truth mode), increasing the input-side mismatch to 1.152.
- The unfolded integral (42559) is roughly half of the truth-mode result (85786), showing that the mixed-weight response amplifies the normalization collapse.
- This mode is clearly not helpful — the truth-mode response is more internally consistent.
