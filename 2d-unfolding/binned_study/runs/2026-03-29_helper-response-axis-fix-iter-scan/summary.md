# Binned debug run: helper-response-axis-fix-iter-scan

## Run label
- `2026-03-29_helper-response-axis-fix-iter-scan`

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
  --out Documents/binned_study/runs/2026-03-29_helper-response-axis-fix-iter-scan/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5 (main run), with `--iter-scan-max 8`
- Engine: helper (`binned_omnifold`)
- `--use-weights`: yes
- Response weight mode: truth
- Hunfold mode: counts
- Response POT scale: data/MC = 0.220501
- Response-axis repair: enabled in helper path

## Iteration scan results

| Iter | Unfolded integral | Ratio to prev | data-bkg / unfolded |
|------|------------------|---------------|---------------------|
| 1 | 589,836 | — | 0.761 |
| 2 | 592,399 | 1.00435 | 0.758 |
| 3 | 593,682 | 1.00217 | 0.756 |
| 4 | 594,149 | 1.00079 | 0.756 |
| 5 | 594,164 | 1.00003 | 0.756 |
| 6 | 594,018 | 0.999755 | 0.756 |
| 7 | 593,747 | 0.999543 | 0.756 |
| 8 | 593,358 | 0.999345 | 0.757 |

Target: `hMeasSub = 449024` events.

## Verdict
- **Stable convergence to a high-yield plateau; the divergence is gone.**

## Notes
- The repaired helper path reaches an apparent fixed point by iteration 4-5.
- The remaining problem is not oscillation but a converged normalization that is too high by about `32%`.
