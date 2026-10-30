# REPORT: the audit of the 5B run-period block C_PL,5D (2026-10-30)

**By** the measurement session `coverage-5b-audit`, for the director.

**Under** [`FD-CT-5B-AUDIT-BINDING.md`](FD-CT-5B-AUDIT-BINDING.md) (PR #552), which binds
[`FD-CT-5B-AUDIT-DECLARATION.md`](FD-CT-5B-AUDIT-DECLARATION.md) (`65213f15a68010e5…`) at deploy pin `6dd41539`, under
[`DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md`](../../../DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md)
item 2.

**MEASURES:**
- the bound deploy and tests (§10.1) and the single run of the reader (§10.2), with their receipts;
- every control's outcome;
- the stop condition's verdict, as the reader wrote it;
- the audit's descriptive numbers, copied from the committed readout by `make_audit_report_tables.py`.

**CANNOT AUTHORIZE:**
- the addition of C_PL,5D. That is its own declared step (declaration §8, binding "CANNOT AUTHORIZE");
- any change to the reported matrix C_total + C_resp, to a claim or to printed wording;
- a cause of the period differences, or which period is right.

**CITABLE FOR:**
- that the audit ran once as bound, with every control passed;
- `stop` = false: none of O, N and R fired, at the thresholds frozen before the run;
- the descriptive numbers, as labelled in the readout.

**NOT CITABLE FOR** (the readout's `labels.not_citable_for`): the cause of a period difference, or which period is right; a validated size: a block built from the observed differences contains them by construction; a coverage or calibration statement; the addition, which is its own declared step.

**Receipts:** [`fd/receipts-ct/5b/audit/run/`](fd/receipts-ct/5b/audit/run/):
- the step scripts `s1_deploy.sh` and `s2_run.sh`. The run's argv is the declaration's §10.2 block, verbatim;
- `deploy.log`, `deploy-tests.log`, `audit.out`, `audit.err` (empty) and `run.log`, copied from `$BA/logs/`;
- `make_audit_report_tables.py`, and its output `report-tables.md`, from which every table below is copied.

**The readout:** [`fd/readout/fd_ct_5b_audit.json`](fd/readout/fd_ct_5b_audit.json)
(`6d34d7f8034ea956cf22c092fb31d608f330daabdd721285302868806d50692c`). It equals the sha256 the reader printed.

## 0. Summary

- **Deploy and tests** (binding condition 1): all held. HEAD was the pin, with 0/0 porcelain lines, the declaration's
  sha256 `65213f15…`, 19 of 19 §14 digests, and "Ran 210 tests, OK" with **no skip** (§1).
- **The run** (condition 2): once, exit 0, in 8 s on login37 at 0 node-h. Controls S and A0–A3 passed, and the A4 and
  A5 assertions held (§2).
- **THE STOP CONDITION: `stop` = false.** O, N and R all stayed silent (§3):

| clause | statistic | threshold | fires | decided by |
|---|---|---|---|---|
| **O** (§3.3) | the largest min(E_PB, E_PC) over 51 candidates is 0.158, at \|a\| of 5.7 and 13.3; no candidate has E ≥ 0.5 in both periods | E_PB, E_PC ≥ 0.5 and \|a_PB\|, \|a_PC\| ≤ 2 | false | none (`O_decided_by` []) |
| **N** (§4.1) | s_med = 0.0240 | > 0.5 | false | the ten replica blocks |
| **R** (§6.3) | median_k R_k = 0.9902 | < 0.5 | false | the ten replica blocks |

- **The next step** is §8's addition, as its own declaration (§8 below).
- **Clause N, in words** (binding §2 item 2): N fires only when the replica blocks' size is itself unstable. Its
  silence shows that P's size is stable under the data's resampling. It does not show that the data noise is small
  next to the offsets (declaration §13 item 5).

## 1. Deploy and tests

- `s1_deploy.sh` on login37, 2026-10-30T21:11:04Z–21:13:45Z (161 s; `deploy.log` and its mtime).
- `BA=/pscratch/sd/j/josephrb/fd-ct-5b-audit-20261030` and `D=$BA/deploy/6dd41539`.
<!-- absence-ok: s1_deploy.sh exits 2 with "STOP: $BA exists" when $BA exists, and it reached its clone step (deploy.log); an `ls -d` on login37 just before also returned "No such file or directory" -->
- `$BA` did not exist beforehand.
- A clean clone, detached at `6dd415391da44d3d996bed7ab39a0654a2a5345e`: HEAD equals the pin, with 0 porcelain
  (`--ignored`) lines before the tests and 0 after.
- The declaration's sha256 is `65213f15a68010e5c4fdedcd77cb8585489e25964a54c589f8b5246b3caacd44`, and all 19 §14
  digests match (`pins 19 mismatches 0`).
- The tests ran with root_6_28 activated by prefix (Python 3.11.14): `tests rc=0`, **"Ran 210 tests in 146.818s, OK"**,
  and `skipped_lines 0`. So `RootLoader` and the 5B ROOT tests ran.

## 2. The run

- `s2_run.sh` on login37: started at about 21:13:53Z (`audit.err`'s mtime) and ended at 21:14:01Z (`run.log`). The
  command is §10.2's, run once under its 1,200 s timeout. `rc=0`, and `audit.err` is empty.
- **Controls passed:** S, A0, A1, A2 and A3, each on its own PASS line in `audit.out`. They include:
  - P, the floor, σ_M, e, g_X and its noise σ, rebuilt from the 5B unfolds, equal the committed ones (A1);
  - the blocks sum to M (A2);
  - 2D's committed bootstrap noise share is reproduced, and 5A's reprojected g equals the committed g (A3).
- **Assertions held:** A4, P's column space is span(g), and A5, P − floor has at most two positive eigenvalues.
- **The leak guard** did not refuse.
- **After the run,** the deploy's porcelain is still 0 lines, and `$BA/tmp` is empty. `$BA` is 1.1 GB, almost all of
  it the clone.

## 3. The stop condition, verbatim

`stop_condition` from the readout:

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

## 4. Item 1: overlap with the existing blocks

**The identity (§3.1)** was tested, not measured. A period-common factor cancels exactly, so a source can be counted
twice only through its period-dependent part.

**Clause O (§3.3):** silent. No single component explains half of both PB's and PC's noise-weighted patterns. The
largest min(E_PB, E_PC) is 0.158, from `band:2p2h#2`, whose amplitudes of +5.7σ and −13.3σ are far outside the 2σ
bound. N_cand is 51, against about 55 declared. The look-elsewhere bound is 0.112 if PB's and PC's patterns were
identical, and 2.4 × 10⁻⁴ if they were independent. Only `normalization#1` is uniform, and it was excluded.

**Descriptive, with no stop role:**
- **The flux and detector rows asked for:**
  - flux: OV(P) = 0.967, but OV on P's pattern part is 0.105. The best flux mode explains 0.220 of PB's pattern, at
    a = +3.10, and 0.000 of PC's;
  - detector: OV(P) = 0.569 and OV(pattern) = 0.238. `GEANT_Pion#1` explains 0.850 of PA's pattern, within χ²₁₄'s
    95 % quantile, but 0.314 of PB's and 0.081 of PC's;
  - **DR** (detector ∪ lateral ∪ C_resp): OV(P) = 0.639 and OV(pattern) = 1.000.
- **Why OV(P) is large for flux:** P is 80 % uniform (§6, (3a)). Flux's variance along P's first mode is 2.3 times
  that mode's λ, so OV saturates on geometry that cannot produce a period difference. This is declaration §3.2's
  caveat (arithmetic: 1.736 × 10⁻² / 7.572 × 10⁻³).
- **Why OV(pattern) = 1.000 for lateral, C_resp, DR and "all":** the pattern part is small, with λ of 1.22 × 10⁻³
  and 3.64 × 10⁻⁴. Each of those groups has more variance than that along both pattern modes (b ≥ λ), so the bound
  saturates. It says nothing about cause.
- **One species, `C_resp:meson#1`,** explains 0.556 of PC's pattern at a = +0.86, but 0.002 of PB's.
- **The best DR pair, `GEANT_Pion#1` with `C_resp:meson#1`,** explains 0.853, 0.560 and 0.617 of PA's, PB's and PC's
  patterns, with every |a| ≤ 1.51. Its residual χ² is 23.2, 99.9 and 180.4, against χ²₁₄'s 95 % quantile of 23.685,
  so it reproduces PA's pattern to within noise and PB's and PC's not.
  - Pairs have no stop role (§3.3): they multiply the candidates about 1,500-fold.
  - It is the descriptive answer to how much of the pattern the pion and meson response can carry at their own size.
    It is not an identification.
- **Noise against stat (§3.4):** the floor's σ over C_stat's σ has a median of 1.011, range 0.704–1.479, against
  1.157 expected under the Poisson model. The floor is 1.35 % of tr P.

**T1. OV per group (on P, and on P's pattern part)** (`report-tables.md`)

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

**T2. identification: the best three per group by min(E_PB, E_PC), then named rows** (`report-tables.md`)

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

## 5. Item 2: noise and the stability of P's size

- **N is silent at s_med = 0.0240.** The ten replica blocks' median σ runs from 2.262 % to 2.413 %, beside 5B's
  2.337 % (`FD-CT-5B-REPORT.md`, the C_PL,5D line).
- **Trace share:** the replica blocks' share of tr(M + P^(k)) runs from 0.0577 to 0.0660, with a mean of 0.0611
  (arithmetic), beside 5B's 0.0609.
- **The noise E[χ²_M] from all ten replicas** is 1.298, 1.204 and 1.669 for dr_PB/PA, dr_PC/PA and dr_PC/PB, equal
  to 5B's reported references, with jackknife SEs of 0.124, 0.200 and 0.236. The split halves give 1.545 / 1.051,
  1.418 / 0.991 and 1.972 / 1.365.
- **The noise-dominated cells** are R00 and R08, as 5B reported: σ(floor)/σ(P) is 0.557 and 1.139, the inverses of
  5B's 1.796 and 0.878. Their jackknife SEs on σ(P)/σ(floor) are 0.273 and 0.296.
- **The double-noise bias:** √diag(E_k P^(k)) exceeds σ(P) by 46.4 % in R08 and 6.9 % in R00. In the other 14 cells it
  is within −11.3 % to +10.0 %.
- **The debiased block (§4.3), a sensitivity:** its σ over P's σ runs from 0.9938 to 1.0017, R08 included.
  - The floor is full rank, while P − floor keeps only its two positive eigenvalues. Those lie in P's plane, where the
    floor is 1.35 % of tr P. So the debiasing as declared moves P by under 1 %, even in the cell where the floor's
    full-rank σ exceeds P's.
  - The block that would be added is P, undebiased (§8.1).
- **Three periods (§4.4), disclosed and not a clause:** ν_eff = 1.8244. The 68 % interval on σ_true/σ̂ is
  [0.7339, 2.5643], as declared. The ten replicas do not test this term.

**T3. stability** (`report-tables.md`)

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

## 6. Item 3: why 5B's cell pattern differs from 5A's, while their sizes agree

No clause rides on item 3 (§5.4). The numbers, by hypothesis:

- **H-a, a common per-period mean offset dominates both sizes, while the patterns differ:**
  - **supported in part:** P_5B is 0.800 uniform and P_5A is 0.935;
  - the cell-mean offsets agree, PB −2.724 % against −2.699 % and PC +4.671 % against +4.806 %;
  - the traces are 7.95 × 10⁻³ and 7.01 × 10⁻³;
  - the patterns about the mean correlate at 0.57–0.61;
  - 5B's pattern part has 3.49 times 5A's trace (arithmetic: 1.587 × 10⁻³ / 4.550 × 10⁻⁴). So the agreement in size is
    carried by the uniform part.
- **H-c, the difference is within the combined noise:**
  - with 5A's noise now included, the median |Δ|/σ_comb is 1.101, 1.411 and 1.870 for PA, PB and PC. 5B's own-noise
    medians were 1.575, 1.752 and 2.094 (`FD-CT-5B-REPORT.md`, the g_X table);
  - Σ(Δ/σ_comb)² over the 16 cells is 44.5, 81.6 and 192.8. Sixteen independent unit-variance cells would give 16
    (arithmetic). Cell correlations are not modelled (declaration §2);
  - so noise alone, as modelled, does not reach the PB and PC differences.
- **H-b, the offset depends on the hadronic variables inside a 2D bin (POST HOC, (3c)):**
  - in the low-p_∥ half, Δ = g_5B − g_5A at low E_avail minus at high is +2.137 % ± 0.453 % for PB (+4.7σ) and
    −1.729 % ± 0.508 % for PC (−3.4σ);
  - in each case the sign is opposite to the period's mean offset. So, relative to the high-E_avail cells, 5B's
    offsets at low E_avail (R00, R08) sit closer to zero than 5A's projection does;
  - in the high-p_∥ half, the same contrasts are +1.7σ and −2.3σ;
  - this was chosen after the 5B table was seen.
  <!-- absence-ok: scoped to this audit's measurements; declaration §5.3 declares H-d unmeasured, and §11 item 2 names the test -->
  - It is what H-b predicts, but **H-d,** a 5D shrinkage toward each period's prior, is not measured, and R00 and
    R08 are the two noise-dominated cells. So H-b and H-d cannot be told apart here, and both stay open.
- **The planes (3d):** the principal angles between span(P_5A) and span(P_5B) are 18.30° and 55.16°. PB's and PC's
  offsets lie 88–90 % inside the other construction's plane. PA's offset, whose mean is near zero, lies 66–67 % outside
  it.

**T4. 5A against 5B** (`report-tables.md`)

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

## 7. Item 4: what the rank-two construction can and cannot represent

- **The algebra (§6.1)** was tested, not measured. Rank 2 holds (A4).
- **What it cannot represent** (§6.1, items 1–5):
  - an offset outside the plane;
  - uncertainty in the shapes;
  - period-common effects;
  - structure finer than the three flux-file groups;
  - independent cell-to-cell scatter.
- **The plane is stable (clause R silent):**
  - R_k runs from 0.9727 to 0.9960, with a median of 0.9902;
  - the replica planes' first principal angle to P's is 2.1–5.5°, and their second is 9.5–30.4°;
  - the second mode is 4.71 % of tr P (arithmetic, λ₂/tr P), and is the less stable one.
- **The largest χ² change (§6.2):**
  - the whitened eigenvalues are λ̃ = 2.6511 and 0.3411;
  - so adding P can lower any comparison's χ² by at most **72.61 %**, and only along P's plane;
  - no prediction was read. This is the bound the addition's Stage G recomputation runs under.
- **The reference bound (DESIGN §4), recomputed on the 16 cells:**
  - PB 0.6711, against a first-order bound of 0.6833;
  - PC 0.3504, against 0.3402. The value exceeds its first-order bound by 3 % (arithmetic).

**T5. rank two** (`report-tables.md`)

rank 2; whitened eigenvalues λ̃ 2.6511, 0.3411; largest χ² fall fraction 0.7261
reference bound: PB 0.6711 (first order 0.6833); PC 0.3504 (first order 0.3402)
plane retention median 0.9902 (threshold 0.5); R_k: 0.9855, 0.9901, 0.9960, 0.9916, 0.9727, 0.9908, 0.9902, 0.9927, 0.9902, 0.9838
principal angles span(P) vs span(P^(k)), degrees: 5.5, 17.1; 2.8, 22.9; 2.1, 14.2; 4.8, 9.5; 5.5, 30.4; 2.5, 22.6; 3.8, 14.8; 2.8, 18.7; 4.4, 15.9; 4.4, 26.5

## 8. The next step: §8's addition, as its own declaration

`stop` is false, so the decision's item 2 continues to "then added".
- **The matrix** is declaration §8.1's C_rep,PL = C_e + C_model_abs + C_resp + C_PL,5D,abs, with P byte-pinned from
  `fd_ct_5b_periods.json` (`a5b17895…`) and undebiased.
- **Its label** is §8.2's: "audited (FD-CT-5B-AUDIT-REPORT.md); added after the data were seen; published with and
  without"; the three-period interval [0.73, 2.56]; and the noise-dominated cells R00 and R08.
- **The products** are §8.3's groups (A)–(D). The readouts in (B) stay in M unless the director rules otherwise
  (§11 item 6).

That declaration is the next step and is not drafted here. Two numbers from this audit bear on it:
- the 72.61 % ceiling on any χ² fall, along the plane only;
- the pattern part's possible partial overlap with the pion and meson response (§4, the DR pair). It is descriptive and
  not an identification.

## 9. Deviations and notes

- **None from the bound steps.** Every command is the declaration's §10.1 or §10.2, run once.
- **The deploy script is 5B's `s1_deploy.sh`, retargeted:**
  - to this record's §14 section, found by its header up to the next `## `. §12 follows §14 in the declaration, so a
    slice up to "## 15." would not have worked;
  - to the three declared test modules;
  - 5B's table regeneration is dropped, since this record declares no tables.
- **`s2_run.sh` adds two refusals** before the §10.2 command: one if the readout exists, and one if `audit.out`
  exists. It also adds a `run.log` with the time, host, rc and the readout's sha256.
- **The declaration's §9 says "46 mutants".** The committed receipt has 54 (pass 2, 54 of 54 killed), which is the
  count the director checked. §9's text was not updated after §13's second pass. It is noted here, not repaired, since
  the declaration is bound.
- **The section order 13, 14, 12** in the declaration is as committed.
- **The 2D per-period draws** were still on pscratch: 37 directories, as declared. (3b)'s control passed.

## 10. Ledger, storage and not changed

- **Ledger:** two rows in `fd/LEDGER.tsv`: the deploy and tests, and the run.
- **Storage:** `$BA`, 1.1 GB, joins the pscratch retention list, as §10 declares. Nothing went to CFS. There was no
  Slurm job and no GPU.
- **Not changed:**
  - the reported covariance C_total + C_resp, `s1_assembly.npz`, `cresp.npz`, and every committed readout except this
    new one;
  - every claim and printed wording;
  - `docs/analysis-note/**` by hand.
- Nothing is submitted, deposited or tagged.
