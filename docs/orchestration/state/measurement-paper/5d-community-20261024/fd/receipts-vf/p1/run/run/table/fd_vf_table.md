# C_e^infl's adoption: each Phase 1 readout, OLD (C_e) and C_e^infl

DeltaC_e = C_e^infl - C_e, the covariance increment; C_e^infl = L C_e L^T is C_e with its eigenvalue ranks 1-4, 5-8 and 9-16 rescaled by the applied variance multipliers phi_j (B5D's fluctuation block, V_F in its build records: blocks5d-20261124/RECEIPT.md), adopted into the reported covariance C_rep = C_e^infl + C_model + C_resp + C_PL,5D by DECISION-20261125 section 3, with A1 section 4's caveat: the estimated band ratio r_hat_j, which sets phi_j, measures the toy spread relative to LL5D's rebuilt reference block.

## Listings (p < 0.01 or any |z| > 2)

| readout | OLD | C_e^infl | newly listed | cleared |
|---|---|---|---|---|
| F0 | A7_gibuu, W3, q3, stage0c_gibuu | A7_gibuu | - | W3, q3, stage0c_gibuu |
| S with/f0b | A7_gibuu, q3 | A7_gibuu | - | q3 |
| S with/f1 | A7_gibuu, q3 | A7_gibuu | - | q3 |
| S nopl/f0b | A7_gibuu, q3, stage0c_gibuu | A7_gibuu | - | q3, stage0c_gibuu |
| S nopl/f1 | A7_gibuu, q3, stage0c_gibuu | A7_gibuu | - | q3, stage0c_gibuu |

## Each readout's block (argv)

| readout | OLD key | C_e^infl key |
|---|---|---|
| F0 | none | DeltaC_e |
| S with/f0b | C_resp_plus_C_PL5D | C_resp_plus_C_PL5D_plus_DeltaC_e |
| S with/f1 | C_resp_plus_C_PL5D | C_resp_plus_C_PL5D_plus_DeltaC_e |
| S with/g | C_resp_plus_C_PL5D | C_resp_plus_C_PL5D_plus_DeltaC_e |
| E with/g | C_resp_plus_C_PL5D | C_resp_plus_C_PL5D_plus_DeltaC_e |
| E with/g_diag | C_resp_plus_C_PL5D | C_resp_plus_C_PL5D_plus_DeltaC_e |
| E with/g_followup | C_resp_plus_C_PL5D | C_resp_plus_C_PL5D_plus_DeltaC_e |
| E with/g_sens2 | C_resp_plus_C_PL5D | C_resp_plus_C_PL5D_plus_DeltaC_e |
| E with/flux_boot | C_resp_plus_C_PL5D | C_resp_plus_C_PL5D_plus_DeltaC_e |
| S nopl/f0b | C_resp | C_resp_plus_DeltaC_e |
| S nopl/f1 | C_resp | C_resp_plus_DeltaC_e |
| S nopl/g | C_resp | C_resp_plus_DeltaC_e |
| E nopl/g | C_resp | C_resp_plus_DeltaC_e |
| E nopl/g_diag | C_resp | C_resp_plus_DeltaC_e |
| E nopl/g_followup | C_resp | C_resp_plus_DeltaC_e |
| E nopl/g_sens2 | C_resp | C_resp_plus_DeltaC_e |
| E nopl/flux_boot | C_resp | C_resp_plus_DeltaC_e |

## Stage G, S with/g

| prediction | kind | ndf | chi2 OLD | p OLD | chi2 C_e^infl | p C_e^infl |
|---|---|---:|---:|---:|---:|---:|
| genie_cv | total | 16 | 105.417 | 3.31e-15 | 62.881 | 1.7e-07 |
| genie_cv | shape_only | 15 | 100.574 | 1.02e-14 | 58.337 | 4.86e-07 |
| genie_mec | total | 16 | 223.552 | 1.32e-38 | 137.542 | 2.18e-21 |
| genie_mec | shape_only | 15 | 223.463 | 3.49e-39 | 137.538 | 7.04e-22 |
| nuwro | total | 16 | 130.681 | 4.73e-20 | 92.612 | 8.24e-13 |
| nuwro | shape_only | 15 | 113.728 | 3.09e-17 | 80.029 | 6.9e-11 |
| gibuu | total | 8 | 45.255 | 3.29e-07 | 39.580 | 3.84e-06 |
| gibuu | shape_only | 7 | 24.753 | 0.000839 | 21.349 | 0.00329 |
| mnvtune_v1 | total | 16 | 262.060 | 1.73e-46 | 155.790 | 5.61e-25 |
| mnvtune_v1 | shape_only | 15 | 261.875 | 4.42e-47 | 155.394 | 2.04e-25 |

Matrices: OLD C_total + C_resp + C_PL5D + V_g + 100 f f^T (free normalization) / C_e^infl C_total + C_resp + C_PL5D + DeltaC_e + V_g + 100 f f^T (free normalization); OLD C_total + C_resp + C_PL5D + V_g / C_e^infl C_total + C_resp + C_PL5D + DeltaC_e + V_g

## Stage G, E with/g

| prediction | kind | ndf | chi2 OLD | p OLD | chi2 C_e^infl | p C_e^infl |
|---|---|---:|---:|---:|---:|---:|
| genie_cv | total | 16 | 107.183 | 1.54e-15 | 64.012 | 1.09e-07 |
| genie_cv | shape_only | 15 | 102.115 | 5.18e-15 | 59.298 | 3.33e-07 |
| genie_mec | total | 16 | 229.094 | 9.78e-40 | 140.340 | 6.18e-22 |
| genie_mec | shape_only | 15 | 228.999 | 2.56e-40 | 140.335 | 1.98e-22 |
| nuwro | total | 16 | 127.692 | 1.8e-19 | 91.320 | 1.43e-12 |
| nuwro | shape_only | 15 | 107.524 | 4.81e-16 | 75.580 | 4.45e-10 |
| gibuu | total | 8 | 47.779 | 1.09e-07 | 41.803 | 1.47e-06 |
| gibuu | shape_only | 7 | 22.192 | 0.00235 | 18.921 | 0.00844 |
| mnvtune_v1 | total | 16 | 262.060 | 1.73e-46 | 155.790 | 5.61e-25 |
| mnvtune_v1 | shape_only | 15 | 261.875 | 4.42e-47 | 155.394 | 2.04e-25 |

Matrices: OLD C_total + C_resp + C_PL5D + V_g + 100 f f^T (free normalization) / C_e^infl C_total + C_resp + C_PL5D + DeltaC_e + V_g + 100 f f^T (free normalization); OLD C_total + C_resp + C_PL5D + V_g / C_e^infl C_total + C_resp + C_PL5D + DeltaC_e + V_g

## Stage G, S nopl/g

| prediction | kind | ndf | chi2 OLD | p OLD | chi2 C_e^infl | p C_e^infl |
|---|---|---:|---:|---:|---:|---:|
| genie_cv | total | 16 | 109.354 | 5.95e-16 | 64.126 | 1.04e-07 |
| genie_cv | shape_only | 15 | 108.508 | 3.12e-16 | 62.057 | 1.11e-07 |
| genie_mec | total | 16 | 272.121 | 1.47e-48 | 161.465 | 4.21e-26 |
| genie_mec | shape_only | 15 | 258.073 | 2.69e-46 | 156.004 | 1.54e-25 |
| nuwro | total | 16 | 188.029 | 2.06e-31 | 120.087 | 5.28e-18 |
| nuwro | shape_only | 15 | 187.997 | 5.77e-32 | 119.592 | 2.27e-18 |
| gibuu | total | 8 | 58.463 | 9.32e-10 | 49.736 | 4.59e-08 |
| gibuu | shape_only | 7 | 27.690 | 0.00025 | 23.536 | 0.00137 |
| mnvtune_v1 | total | 16 | 329.716 | 1.73e-60 | 188.440 | 1.7e-31 |
| mnvtune_v1 | shape_only | 15 | 311.190 | 2.63e-57 | 184.064 | 3.6e-31 |

Matrices: OLD C_total + C_resp + V_g + 100 f f^T (free normalization) / C_e^infl C_total + C_resp + DeltaC_e + V_g + 100 f f^T (free normalization); OLD C_total + C_resp + V_g / C_e^infl C_total + C_resp + DeltaC_e + V_g

## Stage G, E nopl/g

| prediction | kind | ndf | chi2 OLD | p OLD | chi2 C_e^infl | p C_e^infl |
|---|---|---:|---:|---:|---:|---:|
| genie_cv | total | 16 | 111.218 | 2.63e-16 | 65.256 | 6.66e-08 |
| genie_cv | shape_only | 15 | 110.320 | 1.4e-16 | 63.116 | 7.29e-08 |
| genie_mec | total | 16 | 277.939 | 9.26e-50 | 164.380 | 1.11e-26 |
| genie_mec | shape_only | 15 | 263.745 | 1.82e-47 | 158.844 | 4.18e-26 |
| nuwro | total | 16 | 180.616 | 6.34e-30 | 115.842 | 3.45e-17 |
| nuwro | shape_only | 15 | 180.525 | 1.86e-30 | 114.360 | 2.34e-17 |
| gibuu | total | 8 | 61.406 | 2.47e-10 | 52.225 | 1.52e-08 |
| gibuu | shape_only | 7 | 24.660 | 0.000872 | 20.710 | 0.00422 |
| mnvtune_v1 | total | 16 | 329.716 | 1.73e-60 | 188.440 | 1.7e-31 |
| mnvtune_v1 | shape_only | 15 | 311.190 | 2.63e-57 | 184.064 | 3.6e-31 |

Matrices: OLD C_total + C_resp + V_g + 100 f f^T (free normalization) / C_e^infl C_total + C_resp + DeltaC_e + V_g + 100 f f^T (free normalization); OLD C_total + C_resp + V_g / C_e^infl C_total + C_resp + DeltaC_e + V_g

## F0: each truth

| truth | graded | chi2 OLD | p OLD | cells OLD | chi2 C_e^infl | p C_e^infl | cells C_e^infl |
|---|---|---:|---:|---|---:|---:|---|
| nominal | True | 0.003128 | 1 | - | 0.001709 | 1 | - |
| W1 | True | 5.689 | 0.991 | - | 2.974 | 1 | - |
| W2 | True | 0.7744 | 1 | - | 0.3466 | 1 | - |
| W3 | True | 36.19 | 0.00273 | - | 15.65 | 0.478 | - |
| q3 | True | 59.83 | 5.59e-07 | - | 29.7 | 0.0196 | - |
| stage0c_gibuu | True | 35.75 | 0.00313 | R06 | 16.94 | 0.389 | - |
| closure_nuwro | True | 13.08 | 0.667 | - | 5.744 | 0.991 | - |
| A7_mnvtune | True | 0.00549 | 1 | - | 0.003311 | 1 | - |
| A7_genie_cv | True | 17.37 | 0.362 | - | 6.382 | 0.983 | - |
| A7_genie_mec | True | 16.18 | 0.44 | - | 5.76 | 0.99 | - |
| A7_nuwro | True | 29.96 | 0.0182 | - | 13.91 | 0.606 | - |
| A7_gibuu | True | 246.8 | 0 | R02 R06 R07 | 108.3 | 9.34e-16 | R02 R06 |
| P1r | False | 50.64 | 1.81e-05 | - | 21.35 | 0.165 | - |
| P2r | False | 40.73 | 0.000609 | - | 20.77 | 0.187 | - |
| P3r | False | 2.955 | 1 | - | 1.581 | 1 | - |
| P1g | False | 85.5 | 1.67e-11 | - | 38.7 | 0.0012 | - |
| P2g | False | 39.38 | 0.000959 | R07 | 18.44 | 0.299 | - |
| P3g | False | 24.83 | 0.0728 | - | 9.176 | 0.906 | - |

Grade matrices: OLD C_total / C_e^infl C_total + DeltaC_e; OLD C_total minus genie_mec / C_e^infl C_total minus genie_mec + DeltaC_e; OLD C_total minus gibuu / C_e^infl C_total minus gibuu + DeltaC_e; OLD C_total minus nuwro / C_e^infl C_total minus nuwro + DeltaC_e

## S with/f0b: each truth

| truth | graded | chi2 OLD | p OLD | cells OLD | chi2 C_e^infl | p C_e^infl | cells C_e^infl |
|---|---|---:|---:|---|---:|---:|---|
| nominal | True | 0.001665 | 1 | - | 0.0008826 | 1 | - |
| W1 | True | 4.819 | 0.997 | - | 2.354 | 1 | - |
| W2 | True | 0.4975 | 1 | - | 0.2214 | 1 | - |
| W3 | True | 27.41 | 0.0372 | - | 14.61 | 0.553 | - |
| q3 | True | 52.48 | 9.15e-06 | - | 22.46 | 0.129 | - |
| stage0c_gibuu | True | 24.57 | 0.0777 | - | 12.69 | 0.695 | - |
| closure_nuwro | True | 10.66 | 0.83 | - | 5.415 | 0.993 | - |
| A7_mnvtune | True | 0.003143 | 1 | - | 0.002168 | 1 | - |
| A7_genie_cv | True | 15.58 | 0.482 | - | 6.087 | 0.987 | - |
| A7_genie_mec | True | 13.65 | 0.625 | - | 5.265 | 0.994 | - |
| A7_nuwro | True | 23.86 | 0.0925 | - | 12.71 | 0.694 | - |
| A7_gibuu | True | 171 | 5.3e-28 | R02 R06 | 92.14 | 1.01e-12 | R02 R06 |
| P1r | False | 38.93 | 0.00111 | - | 19.49 | 0.244 | - |
| P2r | False | 33.89 | 0.00562 | - | 17.72 | 0.341 | - |
| P3r | False | 2.093 | 1 | - | 1.193 | 1 | - |
| P1g | False | 75.53 | 1.05e-09 | - | 36 | 0.00289 | - |
| P2g | False | 36.45 | 0.00251 | R07 | 17.44 | 0.358 | - |
| P3g | False | 21.6 | 0.157 | - | 8.642 | 0.927 | - |

Grade matrices: OLD C_total + C_resp + C_PL5D / C_e^infl C_total + C_resp + C_PL5D + DeltaC_e; OLD C_total minus genie_mec + C_resp + C_PL5D / C_e^infl C_total minus genie_mec + C_resp + C_PL5D + DeltaC_e; OLD C_total minus gibuu + C_resp + C_PL5D / C_e^infl C_total minus gibuu + C_resp + C_PL5D + DeltaC_e; OLD C_total minus nuwro + C_resp + C_PL5D / C_e^infl C_total minus nuwro + C_resp + C_PL5D + DeltaC_e

## S with/f1: each truth

| truth | graded | chi2 OLD | p OLD | cells OLD | chi2 C_e^infl | p C_e^infl | cells C_e^infl |
|---|---|---:|---:|---|---:|---:|---|
| nominal | True | 0.001665 | 1 | - | 0.0008826 | 1 | - |
| W1 | True | 4.819 | 0.997 | - | 2.354 | 1 | - |
| W2 | True | 0.4975 | 1 | - | 0.2214 | 1 | - |
| W3 | True | 27.41 | 0.0372 | - | 14.61 | 0.553 | - |
| q3 | True | 52.48 | 9.15e-06 | - | 22.46 | 0.129 | - |
| stage0c_gibuu | True | 24.57 | 0.0777 | - | 12.69 | 0.695 | - |
| closure_nuwro | True | 10.66 | 0.83 | - | 5.415 | 0.993 | - |
| A7_mnvtune | True | 0.003143 | 1 | - | 0.002168 | 1 | - |
| A7_genie_cv | True | 15.58 | 0.482 | - | 6.087 | 0.987 | - |
| A7_genie_mec | True | 13.65 | 0.625 | - | 5.265 | 0.994 | - |
| A7_nuwro | True | 23.86 | 0.0925 | - | 12.71 | 0.694 | - |
| A7_gibuu | True | 171 | 5.3e-28 | R02 R06 | 92.14 | 1.01e-12 | R02 R06 |
| P1r | False | 38.93 | 0.00111 | - | 19.49 | 0.244 | - |
| P2r | False | 33.89 | 0.00562 | - | 17.72 | 0.341 | - |
| P3r | False | 2.093 | 1 | - | 1.193 | 1 | - |
| P1g | False | 75.53 | 1.05e-09 | - | 36 | 0.00289 | - |
| P2g | False | 36.45 | 0.00251 | R07 | 17.44 | 0.358 | - |
| P3g | False | 21.6 | 0.157 | - | 8.642 | 0.927 | - |
| F1_genie_v3_g18 | True | 9.263 | 0.902 | - | 4.903 | 0.996 | - |
| F1_closure_genie_v3_g18 | True | 9.142 | 0.907 | - | 4.645 | 0.997 | - |
| F1_genie_v3_ar23 | True | 14.06 | 0.594 | - | 6.61 | 0.98 | - |
| F1_closure_genie_v3_ar23 | True | 13.43 | 0.641 | - | 6.251 | 0.985 | - |

Grade matrices: OLD C_total + C_resp + C_PL5D / C_e^infl C_total + C_resp + C_PL5D + DeltaC_e; OLD C_total minus genie_mec + C_resp + C_PL5D / C_e^infl C_total minus genie_mec + C_resp + C_PL5D + DeltaC_e; OLD C_total minus gibuu + C_resp + C_PL5D / C_e^infl C_total minus gibuu + C_resp + C_PL5D + DeltaC_e; OLD C_total minus nuwro + C_resp + C_PL5D / C_e^infl C_total minus nuwro + C_resp + C_PL5D + DeltaC_e

## S nopl/f0b: each truth

| truth | graded | chi2 OLD | p OLD | cells OLD | chi2 C_e^infl | p C_e^infl | cells C_e^infl |
|---|---|---:|---:|---|---:|---:|---|
| nominal | True | 0.002081 | 1 | - | 0.001026 | 1 | - |
| W1 | True | 5.013 | 0.996 | - | 2.41 | 1 | - |
| W2 | True | 0.5676 | 1 | - | 0.2322 | 1 | - |
| W3 | True | 30.83 | 0.0141 | - | 15.49 | 0.489 | - |
| q3 | True | 53.42 | 6.44e-06 | - | 22.78 | 0.12 | - |
| stage0c_gibuu | True | 25.46 | 0.0621 | R06 | 12.88 | 0.681 | - |
| closure_nuwro | True | 11.6 | 0.771 | - | 5.608 | 0.992 | - |
| A7_mnvtune | True | 0.005458 | 1 | - | 0.003278 | 1 | - |
| A7_genie_cv | True | 16.14 | 0.443 | - | 6.202 | 0.986 | - |
| A7_genie_mec | True | 14.54 | 0.558 | - | 5.402 | 0.993 | - |
| A7_nuwro | True | 24.92 | 0.0713 | - | 12.92 | 0.679 | - |
| A7_gibuu | True | 175.1 | 7.96e-29 | R02 R06 R07 | 92.96 | 7.09e-13 | R02 R06 |
| P1r | False | 44.55 | 0.000163 | - | 20.66 | 0.192 | - |
| P2r | False | 37.04 | 0.00207 | - | 18.67 | 0.286 | - |
| P3r | False | 2.501 | 1 | - | 1.352 | 1 | - |
| P1g | False | 82.48 | 5.93e-11 | - | 38.17 | 0.00143 | - |
| P2g | False | 37.97 | 0.00153 | R07 | 17.86 | 0.332 | - |
| P3g | False | 23.25 | 0.107 | - | 8.959 | 0.915 | - |

Grade matrices: OLD C_total + C_resp / C_e^infl C_total + C_resp + DeltaC_e; OLD C_total minus genie_mec + C_resp / C_e^infl C_total minus genie_mec + C_resp + DeltaC_e; OLD C_total minus gibuu + C_resp / C_e^infl C_total minus gibuu + C_resp + DeltaC_e; OLD C_total minus nuwro + C_resp / C_e^infl C_total minus nuwro + C_resp + DeltaC_e

## S nopl/f1: each truth

| truth | graded | chi2 OLD | p OLD | cells OLD | chi2 C_e^infl | p C_e^infl | cells C_e^infl |
|---|---|---:|---:|---|---:|---:|---|
| nominal | True | 0.002081 | 1 | - | 0.001026 | 1 | - |
| W1 | True | 5.013 | 0.996 | - | 2.41 | 1 | - |
| W2 | True | 0.5676 | 1 | - | 0.2322 | 1 | - |
| W3 | True | 30.83 | 0.0141 | - | 15.49 | 0.489 | - |
| q3 | True | 53.42 | 6.44e-06 | - | 22.78 | 0.12 | - |
| stage0c_gibuu | True | 25.46 | 0.0621 | R06 | 12.88 | 0.681 | - |
| closure_nuwro | True | 11.6 | 0.771 | - | 5.608 | 0.992 | - |
| A7_mnvtune | True | 0.005458 | 1 | - | 0.003278 | 1 | - |
| A7_genie_cv | True | 16.14 | 0.443 | - | 6.202 | 0.986 | - |
| A7_genie_mec | True | 14.54 | 0.558 | - | 5.402 | 0.993 | - |
| A7_nuwro | True | 24.92 | 0.0713 | - | 12.92 | 0.679 | - |
| A7_gibuu | True | 175.1 | 7.96e-29 | R02 R06 R07 | 92.96 | 7.09e-13 | R02 R06 |
| P1r | False | 44.55 | 0.000163 | - | 20.66 | 0.192 | - |
| P2r | False | 37.04 | 0.00207 | - | 18.67 | 0.286 | - |
| P3r | False | 2.501 | 1 | - | 1.352 | 1 | - |
| P1g | False | 82.48 | 5.93e-11 | - | 38.17 | 0.00143 | - |
| P2g | False | 37.97 | 0.00153 | R07 | 17.86 | 0.332 | - |
| P3g | False | 23.25 | 0.107 | - | 8.959 | 0.915 | - |
| F1_genie_v3_g18 | True | 11.84 | 0.755 | - | 5.73 | 0.991 | - |
| F1_closure_genie_v3_g18 | True | 11.44 | 0.782 | - | 5.304 | 0.994 | - |
| F1_genie_v3_ar23 | True | 16.86 | 0.395 | - | 7.325 | 0.966 | - |
| F1_closure_genie_v3_ar23 | True | 16.05 | 0.449 | - | 6.904 | 0.975 | - |

Grade matrices: OLD C_total + C_resp / C_e^infl C_total + C_resp + DeltaC_e; OLD C_total minus genie_mec + C_resp / C_e^infl C_total minus genie_mec + C_resp + DeltaC_e; OLD C_total minus gibuu + C_resp / C_e^infl C_total minus gibuu + C_resp + DeltaC_e; OLD C_total minus nuwro + C_resp / C_e^infl C_total minus nuwro + C_resp + DeltaC_e

Every other number is in the readouts themselves (`fd/with-vf/readout/`); no number is paired here by its position alone.


NOT CITABLE FOR: a validated size for C_e^infl; a coverage or calibration statement. Readings go to the director first.
