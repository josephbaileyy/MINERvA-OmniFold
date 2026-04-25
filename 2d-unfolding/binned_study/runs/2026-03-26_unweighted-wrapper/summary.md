# Binned debug run: unweighted-wrapper

## Run label
- `2026-03-26_unweighted-wrapper`

## Command
```bash
python3 Documents/binned_study/scripts/unfold_ptmu_omnifold_binned.py \
  --omnifile Documents/runEventLoopOmniFold.root \
  --datafile Documents/runEventLoopData.root \
  --datahist pTmu_data \
  --iters 5 \
  --engine wrapper \
  --response-weight-mode truth \
  --hunfold-mode counts \
  --verbose \
  --out Documents/binned_study/runs/2026-03-26_unweighted-wrapper/outputs/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5
- Engine: wrapper (RooUnfoldOmnifold)
- `--use-weights`: **no** (this is the key difference from nominal)
- Response weight mode: truth
- Hunfold mode: counts
- Response POT scale: data/MC = 0.220501

## Key normalization checks
- `hDataReco` in-range: 496683
- `hBkgReco` in-range: 47659.4
- `hMeasSub` in-range: 449024
- `hTruthSel` in-range: 520508
- unfolded in-range: 37410.2
- `response.Htruth()` in-range: 520508
- `response.Hmeasured()` in-range: 478901
- `data-bkg / response.Hmeasured`: **0.937613**
- `data-bkg / unfolded`: **12.0027**
- `measSub / truthSel`: 0.862664

## Response fill summary
- sum_w_fill: 478897
- sum_w_miss: 41611.2
- sum_w_fake: 3.74852

## Outputs
- ROOT file: `outputs/omnifold_ptmu_unfold.root`

## Verdict
- **reproduced old failure** (worse than weighted nominal)

## Notes
- Disabling weights makes the failure *worse* (12.0x vs 5.2x under-normalization).
- Without MC event weights, the response.Hmeasured (478901) is actually *closer* to data-bkg (449024), ratio=0.94, so the input mismatch is smaller.
- But the unfolded output (37410) is even more compressed — the OmniFold iterations are collapsing the normalization more aggressively without weights.
- hTruthSel is larger without weights (520508 vs 433804), which changes the measSub/truthSel ratio from 1.035 to 0.863.
- This confirms the problem is not caused by event weights themselves — it's structural to the binned OmniFold path.
