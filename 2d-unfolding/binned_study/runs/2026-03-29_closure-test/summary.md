# Binned debug run: closure-test

## Run label
- `2026-03-29_closure-test`

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
  --closure-test \
  --iter-scan-max 8 \
  --verbose \
  --out Documents/binned_study/runs/2026-03-29_closure-test/outputs/omnifold_ptmu_unfold.root
```

## Configuration
- Iterations: 5 (main run), with `--iter-scan-max 8` scanning iterations 1–8
- Engine: wrapper (RooUnfoldOmnifold)
- `--use-weights`: yes
- `--closure-test`: **yes** — replaces hMeasSub (data-bkg) with response.Hmeasured()
- Response weight mode: truth
- Hunfold mode: counts
- Response POT scale: data/MC = 0.220501

## Closure test setup
- `hMeasSub` was replaced with `response.Hmeasured()` after building the response
- This makes the measured input **perfectly self-consistent** with the response matrix
- `data-bkg / response.Hmeasured = 1.0` (exactly)
- `measSub / truthSel = 0.919181` (natural — efficiency < 1, some truth events are misses)

## Key normalization checks (main 5-iter run)
- hMeasSub (closure) in-range: 398,745
- hTruthSel in-range: 433,804
- unfolded in-range: **0.433791**
- `data-bkg / response.Hmeasured`: **1.0** (exact, by construction)
- `data-bkg / unfolded`: **919,209x** (catastrophic)

## Iteration scan results

| Iter | Unfolded integral | Ratio to prev | target/unfolded |
|------|------------------|---------------|-----------------|
| 1 | 38,370 | — | 10.4x |
| 2 | 6,226 | 0.162 | 64.1x |
| 3 | 107 | 0.017 | 3,726x |
| 4 | 1,140,590 | 10,659 | 0.35x |
| 5 | 0.43 | 3.8e-7 | 919,209x |
| 6 | 1,552 | 3,577 | 257x |
| 7 | 0.43 | 2.8e-4 | 919,209x |
| 8 | 1,140,620 | 2,629,000 | 0.35x |

Target: response.Hmeasured = **398,745 events**.

## Verdict
- **Closure test FAILS: divergent oscillation persists even with perfectly self-consistent inputs.**

## Notes

### The instability is in the algorithm, not the inputs

With the data-bkg / response.Hmeasured ratio at exactly 1.0, there is zero
input-side normalization mismatch. Despite this, the iteration diverges in the
same oscillatory pattern as the real-data run.

This definitively rules out the hypothesis that the data/response mismatch
(~11% in the real-data case) is amplified by iteration to cause the failure.
The algorithm itself cannot preserve normalization through its iterative
reweighting even in the ideal case.

### Comparison to real-data iteration scan

| Iter | Real data | Closure test |
|------|----------|--------------|
| 1 | 43,251 | 38,370 |
| 2 | 7,656 | 6,226 |
| 3 | 218 | 107 |
| 4 | 1,140,760 | 1,140,590 |
| 5 | 58,043 | 0.43 |
| 6 | 0.43 | 1,552 |
| 7 | 1,141,300 | 0.43 |
| 8 | 0.43 | 1,140,620 |

Both show the same divergent oscillation with similar amplitudes. The closure
test is slightly phase-shifted (reaching 0.43 at iter 5 instead of iter 6) but
the instability pattern is identical.

### Implications
1. The binned OmniFold iterative reweighting is **fundamentally unstable**.
2. The root cause is not in the physics inputs, POT scaling, background subtraction, or weight handling.
3. The fix must be in the algorithm itself: either ratio clipping, damping, or a fundamentally different binned iteration scheme.
4. Next step: instrument the internal reweighting to identify which bins produce extreme ratios.
