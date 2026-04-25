# Binned debug run: helper-response-axis-fix-closure

## Run label
- `2026-03-29_helper-response-axis-fix-closure`

## Command
```bash
python3 Documents/binned_study/scripts/unfold_ptmu_omnifold_binned.py \
  --omnifile Documents/runEventLoopOmniFold.root \
  --datafile Documents/runEventLoopData.root \
  --datahist pTmu_data \
  --iters 5 \
  --iter-scan-max 8 \
  --use-weights \
  --engine helper \
  --response-weight-mode truth \
  --hunfold-mode counts \
  --closure-test \
  --out Documents/binned_study/runs/2026-03-29_helper-response-axis-fix-closure/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5 (main run), with `--iter-scan-max 8`
- Engine: helper (`binned_omnifold`)
- `--use-weights`: yes
- `--closure-test`: yes
- Response weight mode: truth
- Hunfold mode: counts
- Response POT scale: data/MC = 0.220501
- Response-axis repair: enabled in helper path

## Closure setup
- `hMeasSub` replaced with `response.Hmeasured()`
- `data-bkg / response.Hmeasured = 1.0` exactly

## Iteration scan results

| Iter | Unfolded integral | Ratio to prev |
|------|------------------|---------------|
| 1 | 522,306 | — |
| 2 | 523,743 | 1.00275 |
| 3 | 524,555 | 1.00155 |
| 4 | 524,926 | 1.00071 |
| 5 | 525,055 | 1.00024 |
| 6 | 524,913 | 0.99973 |
| 7 | 524,695 | 0.999584 |
| 8 | 524,407 | 0.999451 |

Target: `response.Hmeasured = 398745` events.

## Key normalization checks (main 5-iter run)
- closure target in-range: 398745
- `hTruthSel` in-range: 433804
- unfolded in-range: 525055
- `response.Hmeasured / unfolded`: **0.759435**

## Verdict
- **Closure no longer diverges, but it still converges to a normalization ~32% too high.**

## Notes
- This run isolates the remaining problem from data/response mismatch.
- The surviving bias is consistent with the nominal helper run, which points to a normalization convention or post-processing issue rather than the old feature-space bug.
