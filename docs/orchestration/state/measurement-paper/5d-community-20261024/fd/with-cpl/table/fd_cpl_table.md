# The 5B block's addition: every matrix-dependent number, without and with C_PL5D

Without: C_total + C_resp (the committed readouts). With: C_total + C_resp + C_PL5D. added under DECISION-20261030 item 2 after the audit's stop condition did not fire (FD-CT-5B-AUDIT-REPORT.md); the decision followed the data; published with and without.

## sigma/f per cell

| cell | without | C_PL5D | with | with / without |
|---|---:|---:|---:|---:|
| R00 | 7.097% | 0.400% | 7.108% | 1.0016 |
| R01 | 7.095% | 2.706% | 7.594% | 1.0702 |
| R02 | 14.004% | 1.137% | 14.050% | 1.0033 |
| R03 | 12.637% | 1.502% | 12.726% | 1.0070 |
| R04 | 4.203% | 2.313% | 4.797% | 1.1414 |
| R05 | 7.475% | 3.165% | 8.117% | 1.0860 |
| R06 | 5.891% | 2.885% | 6.559% | 1.1135 |
| R07 | 7.977% | 2.793% | 8.452% | 1.0595 |
| R08 | 6.255% | 0.279% | 6.261% | 1.0010 |
| R09 | 6.265% | 2.774% | 6.851% | 1.0936 |
| R10 | 8.592% | 1.291% | 8.688% | 1.0112 |
| R11 | 13.686% | 2.361% | 13.888% | 1.0148 |
| R12 | 6.632% | 2.183% | 6.982% | 1.0528 |
| R13 | 11.071% | 2.648% | 11.383% | 1.0282 |
| R14 | 5.265% | 2.131% | 5.680% | 1.0788 |
| R15 | 7.941% | 2.369% | 8.287% | 1.0435 |

## Stage G

| prediction | kind | ndf | chi2 without | p without | chi2 with | p with |
|---|---|---:|---:|---:|---:|---:|
| genie_cv | total | 16 | 109.354 | 5.95e-16 | 105.417 | 3.31e-15 |
| genie_cv | shape_only | 15 | 108.508 | 3.12e-16 | 100.574 | 1.02e-14 |
| genie_mec | total | 16 | 272.121 | 1.47e-48 | 223.552 | 1.32e-38 |
| genie_mec | shape_only | 15 | 258.073 | 2.69e-46 | 223.463 | 3.49e-39 |
| nuwro | total | 16 | 188.029 | 2.06e-31 | 130.681 | 4.73e-20 |
| nuwro | shape_only | 15 | 187.997 | 5.77e-32 | 113.728 | 3.09e-17 |
| gibuu | total | 8 | 58.463 | 9.32e-10 | 45.255 | 3.29e-07 |
| gibuu | shape_only | 7 | 27.690 | 0.00025 | 24.753 | 0.000839 |
| mnvtune_v1 | total | 16 | 329.716 | 1.73e-60 | 262.060 | 1.73e-46 |
| mnvtune_v1 | shape_only | 15 | 311.190 | 2.63e-57 | 261.875 | 4.42e-47 |

## F0B: each graded truth

| truth | chi2 without | p without | cells abs(z) > 2 | chi2 with | p with | cells abs(z) > 2 |
|---|---:|---:|---:|---:|---:|---:|
| nominal | 0.002081 | 1 | 0 | 0.001665 | 1 | 0 |
| W1 | 5.013 | 0.996 | 0 | 4.819 | 0.997 | 0 |
| W2 | 0.5676 | 1 | 0 | 0.4975 | 1 | 0 |
| W3 | 30.83 | 0.0141 | 0 | 27.41 | 0.0372 | 0 |
| q3 | 53.42 | 6.44e-06 | 0 | 52.48 | 9.15e-06 | 0 |
| stage0c_gibuu | 25.46 | 0.0621 | 1 | 24.57 | 0.0777 | 0 |
| closure_nuwro | 11.6 | 0.771 | 0 | 10.66 | 0.83 | 0 |
| A7_mnvtune | 0.005458 | 1 | 0 | 0.003143 | 1 | 0 |
| A7_genie_cv | 16.14 | 0.443 | 0 | 15.58 | 0.482 | 0 |
| A7_genie_mec | 14.54 | 0.558 | 0 | 13.65 | 0.625 | 0 |
| A7_nuwro | 24.92 | 0.0713 | 0 | 23.86 | 0.0925 | 0 |
| A7_gibuu | 175.1 | 7.96e-29 | 3 | 171 | 5.3e-28 | 2 |

## F1: each graded truth

| truth | chi2 without | p without | cells abs(z) > 2 | chi2 with | p with | cells abs(z) > 2 |
|---|---:|---:|---:|---:|---:|---:|
| nominal | 0.002081 | 1 | 0 | 0.001665 | 1 | 0 |
| W1 | 5.013 | 0.996 | 0 | 4.819 | 0.997 | 0 |
| W2 | 0.5676 | 1 | 0 | 0.4975 | 1 | 0 |
| W3 | 30.83 | 0.0141 | 0 | 27.41 | 0.0372 | 0 |
| q3 | 53.42 | 6.44e-06 | 0 | 52.48 | 9.15e-06 | 0 |
| stage0c_gibuu | 25.46 | 0.0621 | 1 | 24.57 | 0.0777 | 0 |
| closure_nuwro | 11.6 | 0.771 | 0 | 10.66 | 0.83 | 0 |
| A7_mnvtune | 0.005458 | 1 | 0 | 0.003143 | 1 | 0 |
| A7_genie_cv | 16.14 | 0.443 | 0 | 15.58 | 0.482 | 0 |
| A7_genie_mec | 14.54 | 0.558 | 0 | 13.65 | 0.625 | 0 |
| A7_nuwro | 24.92 | 0.0713 | 0 | 23.86 | 0.0925 | 0 |
| A7_gibuu | 175.1 | 7.96e-29 | 3 | 171 | 5.3e-28 | 2 |
| F1_genie_v3_g18 | 11.84 | 0.755 | 0 | 9.263 | 0.902 | 0 |
| F1_closure_genie_v3_g18 | 11.44 | 0.782 | 0 | 9.142 | 0.907 | 0 |
| F1_genie_v3_ar23 | 16.86 | 0.395 | 0 | 14.06 | 0.594 | 0 |
| F1_closure_genie_v3_ar23 | 16.05 | 0.449 | 0 | 13.43 | 0.641 | 0 |

## The flux bootstrap: each total chi2's replicate percentiles 16 / 50 / 84

| variant | prediction | without | with |
|---|---|---|---|
| correlation | genie_cv | 105.97 / 109.60 / 112.45 | 102.21 / 105.67 / 108.23 |
| correlation | genie_mec | 262.37 / 273.34 / 282.71 | 216.80 / 223.85 / 229.43 |
| correlation | nuwro | 185.47 / 188.78 / 190.93 | 128.51 / 130.90 / 132.69 |
| correlation | gibuu | 57.33 / 58.62 / 59.47 | 44.63 / 45.33 / 45.79 |
| correlation | mnvtune_v1 | 314.90 / 332.84 / 350.00 | 252.65 / 263.06 / 271.80 |
| block | genie_cv | 107.59 / 110.34 / 112.83 | 103.54 / 106.37 / 109.08 |
| block | genie_mec | 267.00 / 274.21 / 281.72 | 219.71 / 224.79 / 229.39 |
| block | nuwro | 187.15 / 188.97 / 190.62 | 129.16 / 131.50 / 134.23 |
| block | gibuu | 55.89 / 59.24 / 62.93 | 43.80 / 45.69 / 47.76 |
| block | mnvtune_v1 | 322.30 / 333.80 / 347.09 | 257.97 / 264.38 / 271.29 |

## Every other number

`fd_cpl_table.json` `leaves` pairs every numeric leaf of each readout:

- f0b: 2203 paired leaves
- f1: 2626 paired leaves
- g: 861 paired leaves
- g_diag: 6006 paired leaves
- g_followup: 3052 paired leaves
- g_sens2: 3464 paired leaves
- flux_boot: 624 paired leaves

NOT CITABLE FOR: a validated size for C_PL,5D: a block built from the observed differences contains them by construction; the cause of a period difference, or which period is right; a coverage or calibration statement.
