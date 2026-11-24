# COVFIX rev 12: the u = 2 amplitude calibration (cov2d)

The calibration of [a_lo, a_hi] that COVFIX-DECLARATION.md §4.2 (rev 12 DRAFT) declares, computed before any draw,
sealed or unsealed.

| file | what |
|---|---|
| `calibration-rule2.json` | **the deciding record (rule 2)**: per truth D, the debiased D', noise scale and zero counts; the c scan; both rules' targets and a_lo, a_hi; the branch; check 2's threshold; the map's own noise |
| `calibration.json` | rule 1's record, superseded and kept: raw D_g, a_lo and a_hi, and the 20-resampling noise diagnostic that led to rule 2 |
| `mutants-rule2.txt` | the hand-mutant run on rule 2's code: 22/22 killed |
| `fetch-receipt.txt` | the read-only fetch of the four pinned 5D predictions (director's go, 2026-11-24): shas, sizes, atimes before and after, host, times |
| `connect/connect.sh`, `connect/reader.py` | the fetch as run |

Reproduce, on a copy of the four files (`2d-unfolding/covfix/`):

```
python3 -B covfix_u2_calibrate.py --inputs <dir with the four npz> --out <new file>
python3 -B -m unittest test_covfix_u2_calibrate
```

The code refuses any input whose sha256 differs from its pin, and refuses to overwrite its output.

**CITABLE FOR:** the calibration constants of §4.2. **NOT CITABLE FOR:** any validation reading, or a measurement of
generator differences: D and D' are within-cell index correlations on finite-sample predictions.
