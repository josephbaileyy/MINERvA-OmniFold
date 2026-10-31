readout sha256 6d34d7f8034ea956cf22c092fb31d608f330daabdd721285302868806d50692c
5B readout sha256 a5b17895b1189543d773e94717e14cd9b1409535e366c96788f94bf6f40759db
controls_passed ['S', 'A0', 'A1', 'A2', 'A3']; assertions_passed ['A4', 'A5']

stop_condition (verbatim):

```json
{
 "O": false,
 "N": false,
 "R": false,
 "stop": false,
 "which": [],
 "O_decided_by": [],
 "N_statistic": 0.02404774449024729,
 "R_statistic": 0.990217402786203,
 "thresholds": {
  "O_E": 0.5,
  "O_abs_a": 2.0,
  "N_s_med": 0.5,
  "R_median": 0.5
 }
}
```

## T1 OV per group (on P, and on P's pattern part)

| group | OV(P) | b_1, b_2 along P's modes | OV(pattern) | b_1, b_2 along the pattern's modes |
|---|---:|---|---:|---|
| flux | 0.967 | 1.736e-02, 1.085e-04 | 0.105 | 3.148e-05, 1.353e-04 |
| detector | 0.569 | 4.148e-03, 4.963e-04 | 0.238 | 1.384e-05, 4.399e-04 |
| lateral | 0.029 | 8.154e-05, 1.462e-04 | 1.000 | 2.249e-03, 3.916e-04 |
| C_resp | 0.106 | 4.717e-04, 2.817e-03 | 1.000 | 3.614e-03, 1.852e-03 |
| DR | 0.639 | 4.701e-03, 3.460e-03 | 1.000 | 5.876e-03, 2.684e-03 |
| interaction | 0.216 | 1.340e-03, 2.513e-03 | 0.387 | 2.494e-04, 2.372e-03 |
| normalization | 0.333 | 2.633e-03, 9.679e-06 | 0.000 | -2.032e-20, -5.333e-21 |
| C_model | 0.081 | 2.703e-04, 6.530e-04 | 0.862 | 5.315e-03, 1.450e-04 |
| all | 1.000 | 2.632e-02, 6.755e-03 | 1.000 | 1.148e-02, 5.347e-03 |

P's λ: 7.572e-03, 3.739e-04; the pattern part's λ: 1.223e-03, 3.641e-04
normalization's OV(pattern) as written: -1.616e-17 (a numerical zero)

## T2 identification: the best three per group by min(E_PB, E_PC), then named rows

N_cand 51; uniform, excluded: ['normalization#1']; fired_by []; χ²_res(1): PA 157.6, PB 226.7, PC 470.8; χ²₁₄ 95% 23.685

| group | candidate | E_PB (a_PB) | E_PC (a_PC) | E_PA (a_PA) | χ²_res PB, PC | fires O |
|---|---|---|---|---|---|---|
| C_model | `C_model:gibuu#1` | 0.046 (+0.05) | 0.102 (-0.15) | 0.035 (+0.02) | 216.2, 422.8 | False |
| C_model | `C_model:nuwro#1` | 0.007 (+0.07) | 0.007 (-0.10) | 0.002 (-0.02) | 225.1, 467.6 | False |
| C_model | `C_model:genie_mec#1` | 0.003 (+0.13) | 0.059 (-0.93) | 0.016 (+0.16) | 226.0, 443.2 | False |
| C_resp | `C_resp:proton#1` | 0.085 (+0.35) | 0.451 (-1.29) | 0.021 (+0.08) | 207.3, 258.3 | False |
| C_resp | `C_resp:other#1` | 0.035 (-0.36) | 0.340 (-1.90) | 0.505 (+0.66) | 218.7, 310.8 | False |
| C_resp | `C_resp:em#1` | 0.020 (-0.25) | 0.365 (-1.84) | 0.445 (+0.56) | 222.1, 299.0 | False |
| detector | `band:GEANT_Pion#1` | 0.314 (-0.80) | 0.081 (-0.81) | 0.850 (+0.65) | 155.5, 432.7 | False |
| detector | `band:GEANT_Proton#1` | 0.069 (-3.58) | 0.021 (-2.88) | 0.041 (+1.34) | 211.2, 461.1 | False |
| detector | `band:GEANT_Neutron#1` | 0.015 (+1.10) | 0.356 (-7.59) | 0.103 (+1.33) | 223.2, 303.1 | False |
| flux | `band:Flux#2` | 0.186 (-1.41) | 0.006 (+0.39) | 0.275 (+0.79) | 184.5, 468.0 | False |
| flux | `band:Flux#1` | 0.220 (+3.10) | 0.000 (+0.03) | 0.313 (-1.62) | 176.8, 470.8 | False |
| interaction | `band:2p2h#2` | 0.158 (+5.72) | 0.361 (-13.31) | 0.012 (+0.77) | 190.8, 300.8 | False |
| interaction | `band:MaCCQE#1` | 0.131 (-0.90) | 0.190 (+2.10) | 0.015 (+0.14) | 197.0, 381.4 | False |
| interaction | `band:FrAbs_pi#1` | 0.134 (-0.94) | 0.079 (+1.37) | 0.082 (+0.32) | 196.4, 433.8 | False |
| lateral | `lat:Muon_Energy_MINOS#1` | 0.135 (+0.19) | 0.091 (-0.30) | 0.005 (-0.02) | 196.2, 428.1 | False |
| lateral | `lat:Muon_Energy_MINERvA#1` | 0.089 (+0.14) | 0.076 (-0.26) | 0.000 (+0.00) | 206.5, 434.9 | False |
| lateral | `lat:BeamAngleY#1` | 0.031 (+1.65) | 0.086 (+4.45) | 0.108 (-1.50) | 219.7, 430.3 | False |
| (named: E ≥ 0.5 in PB or PC) | | | | | | |
| C_resp | `C_resp:meson#1` | 0.002 (+0.03) | 0.556 (+0.86) | 0.437 (-0.22) | 226.3, 209.0 | False |

largest min(E_PB, E_PC) over all candidates: 0.158 (`band:2p2h#2`)

best pair in DR (no stop role): ['band:GEANT_Pion#1', 'C_resp:meson#1'], score 0.560; PA E 0.853, a (+0.62, -0.02), χ²_res 23.2; PB E 0.560, a (-1.51, -0.49), χ²_res 99.9; PC E 0.617, a (+0.91, +1.10), χ²_res 180.4

look-elsewhere: Beta tail 0.0022; if PB and PC identical 0.1116; if independent 2.44e-04

floor σ / C_stat σ: median 1.011, range 0.704–1.479; expected √(2k) 1.157; tr(floor)/tr(P) 0.0135

## T3 stability

s_med 0.0240 (threshold 0.5); replica median σ: 2.400%, 2.413%, 2.294%, 2.401%, 2.403%, 2.287%, 2.381%, 2.323%, 2.344%, 2.262%
replica trace share of M + P^(k): 0.0617, 0.0606, 0.0577, 0.0639, 0.0660, 0.0596, 0.0601, 0.0596, 0.0607, 0.0609
noise E[χ²_M], all ten (jackknife SE): dr_PB/PA 1.298 (0.124); dr_PC/PA 1.204 (0.200); dr_PC/PB 1.669 (0.236)
split half 1-5: dr_PB/PA 1.545; dr_PC/PA 1.418; dr_PC/PB 1.972
split half 6-10: dr_PB/PA 1.051; dr_PC/PA 0.991; dr_PC/PB 1.365
noise-dominated cells ['R00', 'R08']; debiased rank 2
ν_eff 1.8244; 68% interval on σ_true/σ̂ [0.7339, 2.5643]

| cell | replica σ, mean (SD) | √diag(mean P^(k)) / σ(P) − 1 | σ(floor)/σ(P) | σ(P)/σ(floor), jackknife SE | debiased σ / σ(P) | σ(floor)/σ(C_stat) |
|---|---|---:|---:|---:|---:|---:|
| R00 | 0.413% (0.118%) | +0.069 | 0.557 | 0.273 | 1.0005 | 1.102 |
| R01 | 2.675% (0.128%) | -0.010 | 0.075 | 3.325 | 1.0006 | 0.886 |
| R02 | 0.990% (0.196%) | -0.113 | 0.261 | 0.540 | 0.9971 | 0.907 |
| R03 | 1.499% (0.135%) | +0.002 | 0.158 | 2.623 | 0.9996 | 0.730 |
| R04 | 2.353% (0.118%) | +0.019 | 0.063 | 2.531 | 1.0003 | 1.047 |
| R05 | 3.070% (0.238%) | -0.027 | 0.117 | 0.977 | 0.9969 | 1.002 |
| R06 | 2.869% (0.212%) | -0.003 | 0.111 | 1.250 | 0.9989 | 0.965 |
| R07 | 2.679% (0.223%) | -0.038 | 0.132 | 1.169 | 0.9984 | 1.234 |
| R08 | 0.361% (0.202%) | +0.464 | 1.139 | 0.296 | 0.9999 | 1.479 |
| R09 | 2.845% (0.116%) | +0.026 | 0.074 | 2.400 | 1.0002 | 1.109 |
| R10 | 1.407% (0.211%) | +0.100 | 0.216 | 2.219 | 0.9938 | 1.120 |
| R11 | 2.435% (0.220%) | +0.035 | 0.134 | 2.788 | 0.9963 | 1.021 |
| R12 | 2.217% (0.129%) | +0.017 | 0.091 | 1.189 | 1.0013 | 1.092 |
| R13 | 2.584% (0.107%) | -0.023 | 0.075 | 2.121 | 0.9996 | 0.704 |
| R14 | 2.167% (0.094%) | +0.018 | 0.059 | 2.610 | 1.0017 | 0.766 |
| R15 | 2.444% (0.129%) | +0.033 | 0.069 | 3.834 | 0.9998 | 0.759 |

## T4 5A against 5B

uniform share: 5B 0.8002, 5A 0.9351; trace: 5B 7.9460e-03, 5A 7.0099e-03; trace with the uniform part removed: 5B 1.5873e-03, 5A 4.5499e-04

| period | mean offset 5B | mean offset 5A | pattern correlation | \|Δ\|/σ_comb median (min–max) | Σ (Δ/σ_comb)² over 16 cells |
|---|---:|---:|---:|---|---:|
| PA | -0.003% | -0.060% | 0.572 | 1.101 (0.292–3.137) | 44.5 |
| PB | -2.724% | -2.699% | 0.586 | 1.411 (0.115–4.377) | 81.6 |
| PC | +4.671% | +4.806% | 0.612 | 1.870 (0.011–8.330) | 192.8 |

E_avail contrast (POST HOC), Δ = g_5B − g_5A, low minus high E_avail, ± its combined-noise σ:

| period | p_∥ low half: low {R00, R08} − high {R02, R03, R10, R11} | p_∥ high half: low {R04, R12} − high {R06, R07, R15} |
|---|---|---|
| PA | -0.622% ± 0.266% (-2.34σ) | +0.031% ± 0.211% (+0.15σ) |
| PB | +2.137% ± 0.453% (+4.72σ) | +0.558% ± 0.332% (+1.68σ) |
| PC | -1.729% ± 0.508% (-3.41σ) | -1.052% ± 0.458% (-2.30σ) |

principal angles span(P_5A) vs span(P_5B): 18.30°, 55.16°
share of g_5A,X outside 5B's plane: PA 0.658, PB 0.114, PC 0.101
share of g_5B,X outside 5A's plane: PA 0.674, PB 0.112, PC 0.117

per cell |Δ|/σ_comb:

| cell | PA | PB | PC |
|---|---:|---:|---:|
| R00 | 0.993 | 4.233 | 5.014 |
| R01 | 0.292 | 3.922 | 8.330 |
| R02 | 0.481 | 0.605 | 1.194 |
| R03 | 3.124 | 2.787 | 1.946 |
| R04 | 0.814 | 0.892 | 2.415 |
| R05 | 3.137 | 0.299 | 4.411 |
| R06 | 1.316 | 0.162 | 1.795 |
| R07 | 1.700 | 1.986 | 0.011 |
| R08 | 0.856 | 4.377 | 5.816 |
| R09 | 1.130 | 1.597 | 3.650 |
| R10 | 1.072 | 1.226 | 3.600 |
| R11 | 0.326 | 0.117 | 0.734 |
| R12 | 1.635 | 0.673 | 1.575 |
| R13 | 1.829 | 2.627 | 0.096 |
| R14 | 0.952 | 0.115 | 0.962 |
| R15 | 2.853 | 2.170 | 0.714 |

## T5 rank two

rank 2; whitened eigenvalues λ̃ 2.6511, 0.3411; largest χ² fall fraction 0.7261
reference bound: PB 0.6711 (first order 0.6833); PC 0.3504 (first order 0.3402)
plane retention median 0.9902 (threshold 0.5); R_k: 0.9855, 0.9901, 0.9960, 0.9916, 0.9727, 0.9908, 0.9902, 0.9927, 0.9902, 0.9838
principal angles span(P) vs span(P^(k)), degrees: 5.5, 17.1; 2.8, 22.9; 2.1, 14.2; 4.8, 9.5; 5.5, 30.4; 2.5, 22.6; 3.8, 14.8; 2.8, 18.7; 4.4, 15.9; 4.4, 26.5
