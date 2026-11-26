# Tests A and B: results against the declared readings

**A contradicts a single recoil function: the E_avail rise steepens with p∥. B is inconclusive. A constant curvature offset ε is nonzero and fits far better than a rate tilt, but it fails the held-out data and accounts for about a third of the excess at 50–80.** Both directions agree: training to held-out and the swap.

The choices, metrics and readings were committed in `DECLARATION.md` (e9d6300bf) and pushed before any A or B model was fitted or scored. The scripts were run once afterward, with no code change. `scan.py` was added after the run. It only reprints the ε scans stored in `test-b.json` and changes no reading. Everything is local and uses 0 node-hours. `bash run.sh` regenerates every output from the saved event tables through `../test1/events.py`, with the versions in `versions.txt`.

## A. One recoil function for all p∥ bands → contradicts

Source: `test_a.py` → `test-a.txt`, `test-a.json`. Good negative tracks, 5 p∥ bands × 9 E_avail bins. Held-out cells with fold ≥ 5 are scored: 36 primary, 38 swap.

| | Primary | Swap |
|---|---|---|
| A1 separable a_i·b_j, held-out χ² (2% floor) | 149.0/36, p = 1.1×10⁻¹⁵ | 167.1/38, p = 4.1×10⁻¹⁸ |
| Interaction γ on training | +0.217 ± 0.018 (+12.2σ) | +0.252 ± 0.019 (+13.3σ) |
| Held-out χ² with γ fixed from training | 71.3/36, p = 4.2×10⁻⁴ (Δχ² = +77.7) | 68.8/38, p = 1.6×10⁻³ (Δχ² = +98.3) |
| A2 common E_avail scale s, held-out χ² | s = 1.15: 315.8/38, p = 1.8×10⁻⁴⁵ | s = 1.16: 284.2/40, p = 1.5×10⁻³⁸ |
| A2 per-band s_i, 20–40 … ≥80 | 1.14, 1.20, 1.19, 1.10, 1.09 | 1.14, 1.20, 1.18, 1.19, 1.10 |

**Reading.** H_A is contradicted in both directions, because p < 0.001 and γ ≥ 3σ with held-out Δχ² ≥ 9. γ is positive. Under the declaration this is reported as a recoil slope that steepens with p∥, which is the high-y/Eν reading in `../test1/NEXT.md`. The held-out residuals against the separable model show the same thing. At 40–50, Data/prediction runs from 0.88 at E_avail < 1 GeV to 1.24–1.49 above 7.5 GeV. At 20–40, which dominates b(E_avail), it stays within 0.94–1.04. Even with γ, the primary fit fails p < 0.001, so one interaction term is not a complete description. A single recoil scale also fails. Its per-band optima reach the 1.20 grid edge at 40–60, which would mean a 20% MC recoil deficit.

## B. Constant curvature offset against a rate tilt → inconclusive

Source: `test_b.py` → `test-b.txt`, `test-b.json`; `scan.py` → `scan.txt`.

| | Primary | Swap |
|---|---|---|
| ε fitted on training (GeV/c)⁻¹ | +0.0009 | +0.0004 |
| Significance, declared 7-point parabola | 6.0σ | 3.2σ |
| Significance, √Δdeviance at ε = 0 | 4.6σ | 3.2σ |
| Held-out χ² over 16 terms, ε model | 136.3, p = 3.7×10⁻²¹ | 240.3, p = 4.9×10⁻⁴² |
| Held-out χ² over 16 terms, rate model | 412.6, p = 8.5×10⁻⁷⁸ | 341.1, p = 7.5×10⁻⁶³ |
| Contributions S1 / S2 / S3 / S4, ε model | 29.2 / 62.5 / 3.5 / 41.2 | 44.2 / 137.8 / 8.7 / 49.6 |

**Reading.** H_B is inconclusive in both directions. ε is at least 3σ from zero, and the ε model beats the rate model by at least 9. Its own held-out p is below 0.01, so the "supports" clause fails, and neither "contradicts" clause holds.

- **How much it explains.** All negatives in the primary held-out playlists, against data and fold:
  - At 50–60, ε predicts 2,146 against 2,617 data and 1,939.2 fold, about 31% of the excess.
  - At 60–80, it predicts 838.4 against 1,181 and 688.8, about 30%.
  - At ≥80, it predicts 183.2 against 192 and 162.9.
- **Where it overshoots.** It overpredicts low-recoil 40–50: 1,852 against 1,608.
- **Curvature precision.** It moves the 60–80 good-curvature fraction to 0.791. The rate model gives 0.726 and the data 0.865.
- **Size.** ε = +0.0009 raises a 60 GeV/c negative track by about 6%.

**Caveats that do not change the reading.**
- The deviance scan is jagged at the grid step, because MC tracks cross bin edges (`scan.txt`). The declared 7-point parabola therefore understates σ_ε in the primary direction. √Δdeviance gives 4.6σ. Every reading falls in the same category either way.
- The primary and swap values of ε differ by 0.0005, so ε is not stable across the playlist halves.
- The rate alternative fits a tilt consistent with zero: c = −0.005 ± 0.039 primary and −0.021 ± 0.041 swap. The Δχ² therefore mostly compares ε against a renormalized nominal fold.
- Positives (S3) do not discriminate. Both models describe them after the 20–40 normalization (χ² 3.5 and 0.8 primary).

## What follows

Neither a muon-independent recoil function (A) nor a constant curvature offset (B) describes the pattern. A finds the recoil slope rising with p∥, the direction a high-y/Eν rate change would give. B finds that a curvature offset can carry about a third of the 50–80 excess but not its shape. Under `../test1/NEXT.md`, test C, the truth-Eν reweight, was to be run only if B did not support H_B. B did not, so C is now the candidate. It needs its own binding, Joseph's NERSC certificate and a cluster authorization. Nothing here is a cause determination, and no note sentence follows from it.
