# Binned debug run: iteration-scan

## Run label
- `2026-03-26_iteration-scan`

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
  --iter-scan-max 8 \
  --verbose \
  --out Documents/binned_study/runs/2026-03-26_iteration-scan/outputs/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5 (main run), with `--iter-scan-max 8` scanning iterations 1–8
- Engine: wrapper (RooUnfoldOmnifold)
- `--use-weights`: yes
- Response weight mode: truth
- Hunfold mode: counts
- Response POT scale: data/MC = 0.220501

## Key normalization checks (main 5-iter run)
- `hDataReco` in-range: 496683
- `hBkgReco` in-range: 47659.4
- `hMeasSub` in-range: 449024
- `hTruthSel` in-range: 433804
- unfolded in-range: 66276.5
- `response.Htruth()` in-range: 433804
- `response.Hmeasured()` in-range: 398745
- `data-bkg / response.Hmeasured`: **1.12609**
- `data-bkg / unfolded`: **6.775**
- `measSub / truthSel`: 1.03508

## Iteration scan results

| Iter | Unfolded integral | Ratio to prev | data-bkg / unfolded |
|------|------------------|---------------|---------------------|
| 1 | 43,251 | — | 10.4x |
| 2 | 7,656 | 0.177 | 58.6x |
| 3 | 218 | 0.028 | 2,059x |
| 4 | 1,140,760 | 5,229 | 0.39x |
| 5 | 58,043 | 0.051 | 7.7x |
| 6 | 0.43 | 7.5e-6 | ~1,000,000x |
| 7 | 1,141,300 | 2,631,000 | 0.39x |
| 8 | 0.43 | 3.8e-7 | ~1,000,000x |

Target: data-bkg = 449,024 events.

## Response fill summary
- sum_w_fill: 398741
- sum_w_miss: 35063.3
- sum_w_fake: 3.82167

## Outputs
- ROOT file: `outputs/omnifold_ptmu_unfold.root`

## Verdict
- **Violent oscillation, not monotonic collapse**

## Notes

### The normalization does NOT monotonically shrink — it oscillates wildly

The iteration scan reveals that the binned OmniFold is **divergently oscillating**, not converging:

- **Odd iterations (1, 3, 5)**: normalization collapses progressively (43k → 218 → 58k → 0.4).
- **Even iterations (4, 6, 8)** and **(7)**: normalization either overshoots massively (1.14M, well above the 449k target) or collapses to near-zero.
- The oscillation amplifies with each cycle: the ratio-to-previous swings from 0.18 → 0.03 → 5229 → 0.05 → 7.5e-6 → 2.6M → 3.8e-7.

This is the signature of an **unstable iterative reweighting scheme**. The per-bin histogram ratios used in binned OmniFold are compounding multiplicatively across iterations, and because the ratio in some bins can be >> 1 or << 1, the product diverges rather than converging.

### Comparison to previous nominal run

The previous nominal 5-iter run gave unfolded=85,786 (data-bkg/unfolded=5.23), while this run's 5-iter result is 66,277 (ratio=6.78). The discrepancy arises because the scan runs OmniFold from scratch for each iteration count (independent calls), while the main run is a single 5-iter call. The qualitative conclusion is the same: severe under-normalization at 5 iterations.

### Why the unbinned path doesn't have this problem

Unbinned OmniFold uses ML classifiers (neural networks) that learn smooth, bounded reweighting functions. The classifier outputs are constrained to [0,1] by the sigmoid, so the per-event weight updates are naturally bounded. The binned path replaces this with raw histogram ratios that have no such constraint — bins with small denominators produce extreme ratios that destabilize the iteration.

### Implications

1. The binned OmniFold failure is a **divergence**, not a convergence to the wrong fixed point.
2. Any fix must stabilize the per-bin reweighting — e.g., ratio clipping, smoothing, or damping.
3. Increasing iterations will never fix this; it makes it worse.
4. The original 5-iteration result (5.23x under-normalization) was a coincidental snapshot of a diverging sequence.
