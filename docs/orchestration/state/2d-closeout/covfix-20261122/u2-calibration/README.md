# COVFIX rev 12: the u = 2 amplitude calibration (cov2d)

The calibration of [a_lo, a_hi] that COVFIX-DECLARATION.md §4.2 (rev 12 DRAFT) declares, computed before any draw,
sealed or unsealed.

| file | what |
|---|---|
| `calibration.json` | the record: input shas, D_g per build truth, the c scan, a_lo and a_hi, and the reported-only noise diagnostic |
| `fetch-receipt.txt` | the read-only fetch of the four pinned 5D predictions (director's go, 2026-11-24): shas, sizes, atimes before and after, host, times |
| `connect/connect.sh`, `connect/reader.py` | the fetch as run |

Reproduce, on a copy of the four files (`2d-unfolding/covfix/`):

```
python3 -B covfix_u2_calibrate.py --inputs <dir with the four npz> --out <new file>
python3 -B -m unittest test_covfix_u2_calibrate
```

The code refuses any input whose sha256 differs from its pin, and refuses to overwrite its output.

**CITABLE FOR:** the calibration constants of §4.2. **NOT CITABLE FOR:** any validation reading, or a measurement of
generator differences: D_g is a within-cell index correlation on finite-sample predictions, and the noise diagnostic
shows D_genie_mec at the metric's noise scale.
