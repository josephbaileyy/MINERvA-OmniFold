# V_F (C_e^infl) Phase 1 readings, OLD -> C_e^infl

From the Phase 1 readouts of FD-VF BINDING 1's run (#1356), read by `phase1_readings.py`. Readings go to the director first; nothing here is note wording.

## 1. Decision-rule outcome changes (first)

No flag is set and no count rises: every change below clears a flag or lowers a count.

Rule: a truth is listed if p < 0.01 or any cell has |z| > 2 against its grade matrix (F0/F0b/F1).

| readout | truth | graded | listed OLD | listed V_F | |z|>2 cells OLD | V_F | p OLD | p V_F |
|---|---|---|---|---|---|---|---:|---:|
| f0 | W3 | True | True | False | - | - | 0.00273 | 0.478 |
| f0 | q3 | True | True | False | - | - | 5.59e-07 | 0.0196 |
| f0 | stage0c_gibuu | True | True | False | R06 | - | 0.00313 | 0.389 |
| f0 | A7_gibuu | True | True | True | R02 R06 R07 | R02 R06 | 0 | 9.34e-16 |
| f0 | P2g | False | False | False | R07 | - | 0.000959 | 0.299 |
| with/f0b | q3 | True | True | False | - | - | 9.15e-06 | 0.129 |
| with/f0b | P2g | False | False | False | R07 | - | 0.00251 | 0.358 |
| with/f1 | q3 | True | True | False | - | - | 9.15e-06 | 0.129 |
| with/f1 | P2g | False | False | False | R07 | - | 0.00251 | 0.358 |
| nopl/f0b | q3 | True | True | False | - | - | 6.44e-06 | 0.12 |
| nopl/f0b | stage0c_gibuu | True | True | False | R06 | - | 0.0621 | 0.681 |
| nopl/f0b | A7_gibuu | True | True | True | R02 R06 R07 | R02 R06 | 7.96e-29 | 7.09e-13 |
| nopl/f0b | P2g | False | False | False | R07 | - | 0.00153 | 0.332 |
| nopl/f1 | q3 | True | True | False | - | - | 6.44e-06 | 0.12 |
| nopl/f1 | stage0c_gibuu | True | True | False | R06 | - | 0.0621 | 0.681 |
| nopl/f1 | A7_gibuu | True | True | True | R02 R06 R07 | R02 R06 | 7.96e-29 | 7.09e-13 |
| nopl/f1 | P2g | False | False | False | R07 | - | 0.00153 | 0.332 |

Trigger counts by group (cells with |z| > 2; truths with p < 0.01), OLD -> V_F:

| readout | group | cells OLD | cells V_F | truths OLD | truths V_F |
|---|---|---:|---:|---:|---:|
| f0 | prior | 0 | 0 | 0 | 0 |
| f0 | vertex-family | 4 | 2 | 3 | 1 |
| f0 | non-vertex | 0 | 0 | 1 | 0 |
| with/f0b | prior | 0 | 0 | 0 | 0 |
| with/f0b | vertex-family | 2 | 2 | 1 | 1 |
| with/f0b | non-vertex | 0 | 0 | 1 | 0 |
| with/f1 | prior | 0 | 0 | 0 | 0 |
| with/f1 | vertex-family | 2 | 2 | 1 | 1 |
| with/f1 | non-vertex | 0 | 0 | 1 | 0 |
| with/f1 | held-out | 0 | 0 | 0 | 0 |
| nopl/f0b | prior | 0 | 0 | 0 | 0 |
| nopl/f0b | vertex-family | 4 | 2 | 1 | 1 |
| nopl/f0b | non-vertex | 0 | 0 | 1 | 0 |
| nopl/f1 | prior | 0 | 0 | 0 | 0 |
| nopl/f1 | vertex-family | 4 | 2 | 1 | 1 |
| nopl/f1 | non-vertex | 0 | 0 | 1 | 0 |
| nopl/f1 | held-out | 0 | 0 | 0 | 0 |

**Not yet read (Phase 2):** PRR/RSN listings, V-ATLAS A3 and its validity list, C-R's and gover's labels, X's agreement, E2's seed-variation rule, the gdefs seed flags.

**Bias regrades:** REGRADE (rg16, rg2d) and LL5D grade under truth-specific C_T and do not move (declaration section 4.3). Phase 2's recomputes run locally with the producers' own functions.

## 2. Stage G, all four chains

Rows whose p crosses 0.01: 0

| chain | prediction | part | ndf | chi2 OLD | p OLD | chi2 V_F | p V_F |
|---|---|---|---:|---:|---:|---:|---:|
| S with/g | genie_cv | total | 16 | 105.417 | 3.31e-15 | 62.881 | 1.7e-07 |
| S with/g | genie_cv | shape_only | 15 | 100.574 | 1.02e-14 | 58.337 | 4.86e-07 |
| S with/g | genie_mec | total | 16 | 223.552 | 1.32e-38 | 137.542 | 2.18e-21 |
| S with/g | genie_mec | shape_only | 15 | 223.463 | 3.49e-39 | 137.538 | 7.04e-22 |
| S with/g | nuwro | total | 16 | 130.681 | 4.73e-20 | 92.612 | 8.24e-13 |
| S with/g | nuwro | shape_only | 15 | 113.728 | 3.09e-17 | 80.029 | 6.9e-11 |
| S with/g | gibuu | total | 8 | 45.255 | 3.29e-07 | 39.580 | 3.84e-06 |
| S with/g | gibuu | shape_only | 7 | 24.753 | 0.000839 | 21.349 | 0.00329 |
| S with/g | mnvtune_v1 | total | 16 | 262.060 | 1.73e-46 | 155.790 | 5.61e-25 |
| S with/g | mnvtune_v1 | shape_only | 15 | 261.875 | 4.42e-47 | 155.394 | 2.04e-25 |
| E with/g | genie_cv | total | 16 | 107.183 | 1.54e-15 | 64.012 | 1.09e-07 |
| E with/g | genie_cv | shape_only | 15 | 102.115 | 5.18e-15 | 59.298 | 3.33e-07 |
| E with/g | genie_mec | total | 16 | 229.094 | 9.78e-40 | 140.340 | 6.18e-22 |
| E with/g | genie_mec | shape_only | 15 | 228.999 | 2.56e-40 | 140.335 | 1.98e-22 |
| E with/g | nuwro | total | 16 | 127.692 | 1.8e-19 | 91.320 | 1.43e-12 |
| E with/g | nuwro | shape_only | 15 | 107.524 | 4.81e-16 | 75.580 | 4.45e-10 |
| E with/g | gibuu | total | 8 | 47.779 | 1.09e-07 | 41.803 | 1.47e-06 |
| E with/g | gibuu | shape_only | 7 | 22.192 | 0.00235 | 18.921 | 0.00844 |
| E with/g | mnvtune_v1 | total | 16 | 262.060 | 1.73e-46 | 155.790 | 5.61e-25 |
| E with/g | mnvtune_v1 | shape_only | 15 | 261.875 | 4.42e-47 | 155.394 | 2.04e-25 |
| S nopl/g | genie_cv | total | 16 | 109.354 | 5.95e-16 | 64.126 | 1.04e-07 |
| S nopl/g | genie_cv | shape_only | 15 | 108.508 | 3.12e-16 | 62.057 | 1.11e-07 |
| S nopl/g | genie_mec | total | 16 | 272.121 | 1.47e-48 | 161.465 | 4.21e-26 |
| S nopl/g | genie_mec | shape_only | 15 | 258.073 | 2.69e-46 | 156.004 | 1.54e-25 |
| S nopl/g | nuwro | total | 16 | 188.029 | 2.06e-31 | 120.087 | 5.28e-18 |
| S nopl/g | nuwro | shape_only | 15 | 187.997 | 5.77e-32 | 119.592 | 2.27e-18 |
| S nopl/g | gibuu | total | 8 | 58.463 | 9.32e-10 | 49.736 | 4.59e-08 |
| S nopl/g | gibuu | shape_only | 7 | 27.690 | 0.00025 | 23.536 | 0.00137 |
| S nopl/g | mnvtune_v1 | total | 16 | 329.716 | 1.73e-60 | 188.440 | 1.7e-31 |
| S nopl/g | mnvtune_v1 | shape_only | 15 | 311.190 | 2.63e-57 | 184.064 | 3.6e-31 |
| E nopl/g | genie_cv | total | 16 | 111.218 | 2.63e-16 | 65.256 | 6.66e-08 |
| E nopl/g | genie_cv | shape_only | 15 | 110.320 | 1.4e-16 | 63.116 | 7.29e-08 |
| E nopl/g | genie_mec | total | 16 | 277.939 | 9.26e-50 | 164.380 | 1.11e-26 |
| E nopl/g | genie_mec | shape_only | 15 | 263.745 | 1.82e-47 | 158.844 | 4.18e-26 |
| E nopl/g | nuwro | total | 16 | 180.616 | 6.34e-30 | 115.842 | 3.45e-17 |
| E nopl/g | nuwro | shape_only | 15 | 180.525 | 1.86e-30 | 114.360 | 2.34e-17 |
| E nopl/g | gibuu | total | 8 | 61.406 | 2.47e-10 | 52.225 | 1.52e-08 |
| E nopl/g | gibuu | shape_only | 7 | 24.660 | 0.000872 | 20.710 | 0.00422 |
| E nopl/g | mnvtune_v1 | total | 16 | 329.716 | 1.73e-60 | 188.440 | 1.7e-31 |
| E nopl/g | mnvtune_v1 | shape_only | 15 | 311.190 | 2.63e-57 | 184.064 | 3.6e-31 |

## 3. Per-cell relative sigma (percent), OLD and C_e^infl

The C_e and C_e^infl columns are A2's per-cell table's pair; the six source columns are unchanged. The S1/C_resp rows are given both ways (C_e form, as printed now; C_e^infl form), for Joseph's open question (declaration section 4.3).

| cell | C_e | C_e^infl | C_total (S1) | C_total^infl | C_total_resp (cresp) | C_total_resp^infl | C_rep OLD | C_rep V_F |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R00 | 6.77 | 7.10 | 6.79 | 7.11 | 7.10 | 7.40 | 7.11 | 7.42 |
| R01 | 6.66 | 6.97 | 6.69 | 7.00 | 7.10 | 7.39 | 7.59 | 7.87 |
| R02 | 7.65 | 8.33 | 13.69 | 14.09 | 14.00 | 14.39 | 14.05 | 14.44 |
| R03 | 8.27 | 9.37 | 12.50 | 13.25 | 12.64 | 13.38 | 12.73 | 13.47 |
| R04 | 4.05 | 4.24 | 4.14 | 4.33 | 4.20 | 4.38 | 4.80 | 4.96 |
| R05 | 5.48 | 6.08 | 6.49 | 7.00 | 7.47 | 7.92 | 8.12 | 8.53 |
| R06 | 4.61 | 5.67 | 5.60 | 6.51 | 5.89 | 6.76 | 6.56 | 7.35 |
| R07 | 7.02 | 8.15 | 7.82 | 8.85 | 7.98 | 8.98 | 8.45 | 9.41 |
| R08 | 4.86 | 5.24 | 5.13 | 5.48 | 6.25 | 6.55 | 6.26 | 6.56 |
| R09 | 4.87 | 5.10 | 5.84 | 6.04 | 6.26 | 6.45 | 6.85 | 7.02 |
| R10 | 7.10 | 7.62 | 8.16 | 8.62 | 8.59 | 9.03 | 8.69 | 9.12 |
| R11 | 7.42 | 8.10 | 13.39 | 13.78 | 13.69 | 14.07 | 13.89 | 14.26 |
| R12 | 6.23 | 6.57 | 6.25 | 6.59 | 6.63 | 6.95 | 6.98 | 7.28 |
| R13 | 8.47 | 9.12 | 10.87 | 11.38 | 11.07 | 11.57 | 11.38 | 11.87 |
| R14 | 4.87 | 5.10 | 4.94 | 5.17 | 5.27 | 5.48 | 5.68 | 5.88 |
| R15 | 6.13 | 6.64 | 7.77 | 8.18 | 7.94 | 8.34 | 8.29 | 8.67 |
| median | 6.45 | 6.80 | 6.74 | 7.05 | 7.29 | 7.66 | 7.86 | 8.20 |

## 4. Follow-ups for other lanes (after Phase 2 and the director's review)

- `make_values_fived16.py`: `READOUTS`, `NOPL_READOUTS`, `ARMS`, `MATRIX_KEYS`; also its literal `"C_total_plus_C_resp"` (:678, :689) and the C_PL5D label it parses from the product (:700-702); Table IV through gdefs (:282-312) and gencmp_values' 2 x 2 (:314-404) need Phase 2's gdefs copy.
- `make_supplemental.py`, `fived16_headline`, `fived16_genresidual`, the EA2 redraw, `valid_region.py`'s `COV_KEY` for a bound rerun.

NOT CITABLE FOR: a validated size for C_e^infl; a coverage or calibration statement; any note wording.
