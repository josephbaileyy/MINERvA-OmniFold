# Binned debug run: nominal-weighted-repro

## Run label
- `2026-03-26_nominal-weighted-repro`

## Command
```bash
python3 Documents/binned_study/scripts/unfold_ptmu_omnifold_binned.py \
  --omnifile Documents/runEventLoopOmniFold.root \
  --datafile Documents/runEventLoopData.root \
  --datahist pTmu_data \
  --iters 5 \
  --use-weights \
  --engine wrapper \
  --response-weight-mode truth \
  --hunfold-mode counts \
  --verbose \
  --out Documents/binned_study/runs/2026-03-26_nominal-weighted-repro/outputs/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5
- Engine: wrapper (RooUnfoldOmnifold)
- `--use-weights`: yes
- Response weight mode: truth
- Hunfold mode: counts
- Response POT scale: data/MC = 0.220501
- Other toggles: none (all defaults)

## Input stats
- tData entries: 498457 (pass-skipped=0, guard-skipped=26)
- tBkg entries: 260386 (pass-skipped=0, guard-skipped=3, weight-skipped=0, has_w_bkg=True)
- tSig entries: 2368292 (Fill=2171858, Miss=188712, Fake=17, skipped=7705, bad-weight=0)

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

## Width-integral checks
- unfolded (width): 10558
- data-bkg (width): 84259.1
- response.Hmeasured (width): 71199.1
- response.Htruth (width): 80561

## Response fill summary
- sum_w_fill: 398741
- sum_w_miss: 35063.3
- sum_w_fake: 3.82167

## Outputs
- ROOT file: `outputs/omnifold_ptmu_unfold.root`
- Plots: none (reproduction run only)

## Verdict
- **reproduced old failure**

## Notes
- Both key ratios match the historical failure state exactly (1.126, 5.23).
- The unfolded integral (85786) is roughly 5x lower than the measured-subtracted target (449024).
- The response.Hmeasured (398745) is already ~11% lower than data-bkg (449024), indicating the response does not fully represent the measured-side normalization even before unfolding.
- No weight clipping occurred (bad-weight=0, weight-skipped=0).
- No negative bins in hMeasSub (minimum bin = 5093.57).
- No floored bins in training histogram.
- The mismatch is present in both standard and width integrals, confirming this is not a density convention issue.
