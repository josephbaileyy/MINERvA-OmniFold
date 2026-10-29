# REPORT: the cheap tier's readers 3a and 4C, with 5A stopped (2026-10-29)

**By** the measurement session (`coverage`), for the director.

**Under** [`FD-CT-READERS-BINDING.md`](FD-CT-READERS-BINDING.md) (PR #482). That binding binds
[`FD-CT-READERS-DECLARATION.md`](FD-CT-READERS-DECLARATION.md) (sha256 `0571c973…`) at deploy pin `28ea789e`.

**MEASURES:** the declaration's §2 steps, as bound, with their receipts; every control's outcome; the 3a and 4C
readouts' numbers, copied from the committed readouts by `make_report_tables.py`; the 5A refusal and the diagnostic the
director then authorized.

**CANNOT AUTHORIZE, and draws no conclusion on:** a covariance component or any change to the reported matrix
C_total + C_resp, a cell, a readout or κ; a coverage, calibration or χ²-distribution statement, a p value or a tail
fraction; any claim, reading or printed wording. Each readout is printed beside the reported matrix, never in it.

**CITABLE FOR:** what 3a and 4C computed on the declared inputs, as bound, and that every refusing control passed;
that 5A stopped at the leak guard, and why.

**NOT CITABLE FOR:** any reading of these numbers. In particular: 3a is not a bias under response mismatch, not a
closure and not a validation of C_resp; 4C is not a calibration of any χ²; 5A has no result.

**Receipts:** [`fd/receipts-ct/run/`](fd/receipts-ct/run/): the step scripts `s1_deploy.sh` (`3754d6e0…`) and
`s2_runs.sh` (`618fd935…`), whose argv lines equal the declaration's §2.2 block; the cluster logs under `cluster/`;
the 5A diagnostic under `diag/`. The readouts are [`fd/readout/fd_ct_recoil.json`](fd/readout/fd_ct_recoil.json)
(`c8458dd0…`) and [`fd/readout/fd_ct_chi2.json`](fd/readout/fd_ct_chi2.json) (`27f37040…`), each equal to the
sha256 its run printed.

## 0. Summary

- **Cost:** 0 node-h. Every step ran on login37, with no Slurm job. Nothing went to CFS.
- **Deploy and tests (binding §3 condition 1):** all held (§1).
- **3a, `recoil`:** exit 0 in about 1 s. Controls S, R0 and R1 passed (§2).
- **4C, `chi2`:** exit 0 in 52 s. Controls S, C0, C1, C2 and C3 passed, and the C4 assertion held (§3).
- **5A, `period`: STOP,** exit 3 at the leak guard, with nothing written (§4). Every refusing control before it
  passed. The director's ruling of 2026-10-29 authorized one diagnostic, which found the mechanism; the repair is
  amendment 1, which runs nothing until it is re-bound. 5A gets its own report after that run.

## 1. Deploy and tests (declaration §2.1; binding §3 condition 1)

A clean clone at `28ea789edd8e0211ac95d57957ba01b06380c862` into `$B/deploy/28ea789e`, `B=/pscratch/sd/j/josephrb/fd-ct-readers-20261028`,
on login37 at 2026-10-29T06:17:41Z (`cluster/deploy.log`). `$B` did not exist beforehand. Every bound condition held:
<!-- absence-ok: `test -e $B` printed B-absent on 2026-10-29 before the deploy, and s1_deploy.sh exits 9 if $B exists; it reached its clone step (cluster/deploy.log) -->
- HEAD is the pin;
- `git status --porcelain --ignored` printed 0 lines before the tests and 0 after;
- the seven §8 digests: `fd_ct_readers.py` `cccc47aa…`, `test_fd_ct_readers.py` `c68d412a…`, `fd_f0_regrade.py`
  `0dfa722c…`, `s1_assemble.py` `b157250a…`, `s5p_stage1_inspect.py` `26569afc…`, `h2_definition.json` `b6790761…`,
  and the declaration `0571c973…`;
- `tests rc=0`, with "Ran 150 tests in 393.604s, OK" (`cluster/deploy-tests.log`).

## 2. 3a, `recoil`

**Run:** 06:24:40–06:24:41Z, against a projection of 60 s and a timeout of 75 s; exit 0 (`cluster/recoil.out`,
`walls.txt`). Every control passed: S (U, f, C_total, C_resp's species sum, C_total_resp), R0 (the three W2b products'
digests and their own dumps), R1 (positive integrals).

**Its label, as written in the readout:** "data-side sensitivity at a second construction: W2b's whole simulated-recoil scale s = 0.96 and 1.04 (the test-beam agreement level, an exploratory size, not an uncertainty prescription), relative to its own delta = 0 chain, which is not bitwise the production product; not a mismatch closure and not a bias; beside C_resp, which it neither replaces nor validates"

**The reference is W2b's own δ = 0 chain, `rrzero`, not f** (binding ruling 1). s₋ = X_rr0/X_rrzero − 1 and
s₊ = X_rr1/X_rrzero − 1 at s = 0.96 and 1.04, and d = (X_rr1 − X_rr0)/(2 X_rrzero). σ/f uses S1's f, so |d|/σ divides
a shift relative to `rrzero` by a σ relative to f.

| cell | s₋ | s₊ | d | σ/f C_resp | σ/f C_total + C_resp | \|d\|/σ C_resp | \|d\|/σ C_total + C_resp |
|---|---:|---:|---:|---:|---:|---:|---:|
| R00 | -0.0350 | +0.0374 | +0.0362 | 0.0207 | 0.0710 | 1.746 | 0.510 |
| R01 | +0.0407 | -0.0391 | -0.0399 | 0.0235 | 0.0710 | 1.696 | 0.563 |
| R02 | -0.0229 | +0.0229 | +0.0229 | 0.0295 | 0.1400 | 0.777 | 0.164 |
| R03 | -0.0224 | +0.0233 | +0.0229 | 0.0185 | 0.1264 | 1.234 | 0.181 |
| R04 | -0.0136 | +0.0110 | +0.0123 | 0.0070 | 0.0420 | 1.754 | 0.292 |
| R05 | +0.0537 | -0.0570 | -0.0553 | 0.0371 | 0.0747 | 1.490 | 0.740 |
| R06 | +0.0262 | -0.0160 | -0.0211 | 0.0181 | 0.0589 | 1.166 | 0.359 |
| R07 | +0.0168 | -0.0130 | -0.0149 | 0.0155 | 0.0798 | 0.961 | 0.187 |
| R08 | -0.0699 | +0.0573 | +0.0636 | 0.0358 | 0.0625 | 1.773 | 1.016 |
| R09 | +0.0368 | -0.0384 | -0.0376 | 0.0226 | 0.0626 | 1.666 | 0.600 |
| R10 | -0.0470 | +0.0258 | +0.0364 | 0.0269 | 0.0859 | 1.355 | 0.424 |
| R11 | -0.0324 | +0.0337 | +0.0330 | 0.0285 | 0.1369 | 1.161 | 0.241 |
| R12 | -0.0393 | +0.0476 | +0.0435 | 0.0220 | 0.0663 | 1.973 | 0.656 |
| R13 | -0.0289 | +0.0268 | +0.0279 | 0.0208 | 0.1107 | 1.338 | 0.252 |
| R14 | +0.0337 | -0.0368 | -0.0352 | 0.0182 | 0.0527 | 1.937 | 0.669 |
| R15 | -0.0169 | +0.0146 | +0.0157 | 0.0164 | 0.0794 | 0.961 | 0.198 |

- **\|d\|, median (min–max):** 0.0341 (0.0123–0.0636).
- **\|d\|/σ for C_resp:** median 1.422 (0.777–1.973); **for C_total + C_resp:** median 0.391 (0.164–1.016).
- **The half-span's quadratic form dᵀ M⁻¹ d:** 4.968 for M = C_total + C_resp; 64.383 for M = C_total. Label: "d^T M^-1 d of the half-span: a length in sigma units, descriptive, not a test".
- **The fraction of d in C_resp's range:** 0.9876, beside rank/16 = 0.25 (rank 4). Label: "||P d||^2 / ||d||^2 in relative units (d and C_resp divided by f), P the projector onto C_resp's range; 1 means the scale moves the cells only in C_resp's directions, and a direction drawn at random gives rank/16 in expectation; the value depends on the units".
- **The curvature ratio:** 0.0576. Label: "build_cresp's G3 form on the cell integrals, ||X(+) + X(-) - 2 X(0)|| / ||X(+) - X(-)||; descriptive".

## 3. 4C, `chi2`

**Run:** 06:24:41–06:25:33Z, 52 s, against a projection of 300 s and a timeout of 375 s; exit 0 (`cluster/chi2.out`).
Every control passed:
- C0: 7,176 calibration products match the s5p archive sums;
- C1: every product is an A7 calibration experiment at its declared truth, in the declared count; the definition's
  p_∥ < 4.5 cells are F0's eight GiBUU cells;
- C2: each truth's B_eff equals F0b's: 272.695961, 243.857824, 245.975265, 320.819408 and 262.800962;
- C3: every truth integral is positive;
- C4 (an assertion): the mean-χ² decomposition holds for every truth, matrix and cell set.

**Its label, as written in the readout:** "descriptive only, not a calibration: F0's offset control 7 failed (chi2_16 = 245.74); A7's draws are not S1's (one flux universe drawn uniformly, model bands move the response only, laterals not applied); the truths are hybrids on the J cells; the products unfold with half of the MC; C_model is not drawn, so the reported matrix is expected to over-cover the toys' scatter"

**Descriptive only. The four disqualifiers stand beside every number below** (declaration §0):
1. **F0's offset control 7 failed,** χ²₁₆ = 245.74 (`FD-F0-REPORT.md:39-41`);
2. **A7's draws are not S1's:** one flux universe of 100 drawn uniformly, model bands that move only the response, and
   laterals not applied;
3. **the truths are hybrids on the J cells,** and the products unfold with half of the MC;
4. **C_model is not drawn,** so the reported matrix is expected to over-cover the toys' scatter.

**Read as:** "about the truth" is r_iᵀ M⁻¹ r_i, and "about b̃" is (r_i − b̃)ᵀ M⁻¹ (r_i − b̃), with b̃ the ν-e + IMD
weighted mean. The matrices are C_total + C_resp without V_g, and C_e, both relative to f (binding ruling 3). The
weighted values are primary (ruling 2). Both percentile sets use the inverted ECDF. χ²_ndf's own mean and percentiles
are beside them. The width ratio is the weighted sd of r over √diag M, per cell, descriptive (ruling 5). No p value
and no tail fraction is computed or written (ruling 4).

**A7_mnvtune** (`MnvTune_v1`): 1365 experiments, B_eff 272.7.

| matrix | cells | χ² | weighted mean | weighted 5 / 16 / 50 / 84 / 95 % | unweighted mean | unweighted 5 / 16 / 50 / 84 / 95 % |
|---|---|---|---:|---|---:|---|
| C_total_resp | all16 | about the truth | 42.69 | 5.93 / 10.45 / 27.55 / 83.90 / 122.27 | 68.79 | 10.33 / 19.45 / 52.04 / 118.67 / 191.55 |
| C_total_resp | all16 | about b̃ | 40.47 | 5.04 / 9.90 / 30.12 / 72.71 / 113.41 | 61.99 | 9.66 / 18.69 / 46.71 / 107.31 / 169.37 |
| C_total_resp | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_total_resp | all16 | b̃'s own χ²; width ratio | 2.22 | width ratio median 0.868 (0.480–1.716) | | |
| C_e | all16 | about the truth | 101.88 | 10.61 / 20.44 / 66.61 / 176.60 / 323.91 | 138.22 | 19.42 / 36.84 / 102.60 / 237.33 / 389.36 |
| C_e | all16 | about b̃ | 99.64 | 9.98 / 20.85 / 64.41 / 177.34 / 316.99 | 131.40 | 19.75 / 35.85 / 96.57 / 223.11 / 376.99 |
| C_e | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_e | all16 | b̃'s own χ²; width ratio | 2.24 | width ratio median 1.008 (0.603–2.209) | | |

**A7_genie_cv** (`GENIE_2_12_10_CV`): 1366 experiments, B_eff 243.9.

| matrix | cells | χ² | weighted mean | weighted 5 / 16 / 50 / 84 / 95 % | unweighted mean | unweighted 5 / 16 / 50 / 84 / 95 % |
|---|---|---|---:|---|---:|---|
| C_total_resp | all16 | about the truth | 55.98 | 15.02 / 21.04 / 42.32 / 90.51 / 155.66 | 81.84 | 21.21 / 32.68 / 65.56 / 135.89 / 195.13 |
| C_total_resp | all16 | about b̃ | 38.99 | 5.45 / 10.89 / 27.38 / 70.17 / 112.22 | 58.81 | 10.40 / 19.04 / 44.90 / 102.57 / 144.79 |
| C_total_resp | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_total_resp | all16 | b̃'s own χ²; width ratio | 16.99 | width ratio median 0.868 (0.533–1.646) | | |
| C_e | all16 | about the truth | 110.97 | 26.17 / 36.64 / 83.16 / 183.30 / 312.43 | 148.97 | 34.73 / 54.04 / 113.50 / 247.34 / 374.86 |
| C_e | all16 | about b̃ | 89.71 | 11.88 / 22.60 / 61.37 / 164.68 / 281.51 | 123.34 | 19.25 / 35.10 / 88.87 / 216.80 / 341.45 |
| C_e | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_e | all16 | b̃'s own χ²; width ratio | 21.25 | width ratio median 1.068 (0.664–2.119) | | |

**A7_genie_mec** (`GENIE_2_12_10_MEC`): 1343 experiments, B_eff 246.0.

| matrix | cells | χ² | weighted mean | weighted 5 / 16 / 50 / 84 / 95 % | unweighted mean | unweighted 5 / 16 / 50 / 84 / 95 % |
|---|---|---|---:|---|---:|---|
| C_total_resp | all16 | about the truth | 47.32 | 9.53 / 13.98 / 34.15 / 79.49 / 133.18 | 71.52 | 15.06 / 25.81 / 56.77 / 117.99 / 179.82 |
| C_total_resp | all16 | about b̃ | 36.39 | 5.72 / 9.84 / 26.82 / 65.09 / 99.42 | 58.43 | 9.92 / 18.59 / 45.51 / 101.78 / 151.17 |
| C_total_resp | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_total_resp | all16 | b̃'s own χ²; width ratio | 10.93 | width ratio median 0.810 (0.471–1.562) | | |
| C_e | all16 | about the truth | 104.72 | 27.94 / 39.71 / 77.15 / 183.42 / 299.83 | 143.78 | 36.01 / 52.50 / 112.96 / 238.47 / 358.11 |
| C_e | all16 | about b̃ | 88.94 | 11.70 / 22.43 / 58.23 / 165.38 / 262.18 | 125.72 | 19.87 / 36.31 / 92.91 / 219.95 / 343.05 |
| C_e | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_e | all16 | b̃'s own χ²; width ratio | 15.78 | width ratio median 0.996 (0.635–2.011) | | |

**A7_nuwro** (`NuWro_21_09`): 1751 experiments, B_eff 320.8.

| matrix | cells | χ² | weighted mean | weighted 5 / 16 / 50 / 84 / 95 % | unweighted mean | unweighted 5 / 16 / 50 / 84 / 95 % |
|---|---|---|---:|---|---:|---|
| C_total_resp | all16 | about the truth | 57.96 | 23.09 / 29.69 / 47.67 / 86.78 / 124.30 | 85.15 | 28.85 / 41.02 / 72.40 / 128.99 / 188.37 |
| C_total_resp | all16 | about b̃ | 35.72 | 5.77 / 10.83 / 28.37 / 59.44 / 93.39 | 59.63 | 10.78 / 19.68 / 46.98 / 98.30 / 154.26 |
| C_total_resp | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_total_resp | all16 | b̃'s own χ²; width ratio | 22.24 | width ratio median 0.895 (0.461–1.528) | | |
| C_e | all16 | about the truth | 156.71 | 56.23 / 70.78 / 122.85 / 232.59 / 390.03 | 207.12 | 70.45 / 93.34 / 159.95 / 310.51 / 530.60 |
| C_e | all16 | about b̃ | 81.07 | 13.01 / 21.95 / 60.74 / 131.42 / 241.70 | 125.18 | 20.57 / 38.33 / 93.10 / 209.53 / 346.21 |
| C_e | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_e | all16 | b̃'s own χ²; width ratio | 75.64 | width ratio median 1.099 (0.616–1.967) | | |

**A7_gibuu** (`GiBUU_2019`): 1351 experiments, B_eff 262.8.

| matrix | cells | χ² | weighted mean | weighted 5 / 16 / 50 / 84 / 95 % | unweighted mean | unweighted 5 / 16 / 50 / 84 / 95 % |
|---|---|---|---:|---|---:|---|
| C_total_resp | all16 | about the truth | 178.35 | 116.64 / 130.31 / 167.44 / 228.47 / 273.63 | 201.77 | 121.18 / 142.45 / 190.65 / 263.17 / 323.16 |
| C_total_resp | all16 | about b̃ | 38.00 | 6.97 / 11.12 / 25.83 / 66.40 / 108.47 | 53.92 | 9.67 / 17.85 / 41.17 / 92.33 / 138.40 |
| C_total_resp | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_total_resp | all16 | b̃'s own χ²; width ratio | 140.36 | width ratio median 0.797 (0.468–1.359) | | |
| C_total_resp | gibuu8 | about the truth | 93.16 | 62.56 / 70.92 / 90.66 / 114.09 / 132.77 | 105.04 | 65.55 / 79.30 / 101.83 / 131.07 / 152.58 |
| C_total_resp | gibuu8 | about b̃ | 6.85 | 1.53 / 2.47 / 5.42 / 11.76 / 16.90 | 10.74 | 1.87 / 3.53 / 8.40 / 17.89 / 29.12 |
| C_total_resp | gibuu8 | χ²_8 | 8.00 | 2.73 / 4.19 / 7.34 / 11.81 / 15.51 | | |
| C_total_resp | gibuu8 | b̃'s own χ²; width ratio | 86.31 | width ratio median 0.708 (0.486–1.359) | | |
| C_e | all16 | about the truth | 513.47 | 351.05 / 393.90 / 485.72 / 635.00 / 780.45 | 604.27 | 387.07 / 452.93 / 565.56 / 757.10 / 956.11 |
| C_e | all16 | about b̃ | 97.98 | 17.23 / 26.08 / 74.47 / 178.49 / 250.15 | 134.30 | 21.80 / 40.22 / 101.47 / 227.21 / 358.78 |
| C_e | all16 | χ²_16 | 16.00 | 7.96 / 10.49 / 15.34 / 21.50 / 26.30 | | |
| C_e | all16 | b̃'s own χ²; width ratio | 415.49 | width ratio median 1.013 (0.532–1.749) | | |
| C_e | gibuu8 | about the truth | 250.09 | 174.64 / 196.36 / 244.63 / 307.30 / 352.91 | 280.40 | 179.20 / 212.22 / 272.15 / 348.75 / 406.66 |
| C_e | gibuu8 | about b̃ | 30.19 | 4.52 / 8.04 / 22.11 / 54.77 / 81.67 | 40.01 | 5.74 / 10.63 / 28.62 / 69.52 / 110.45 |
| C_e | gibuu8 | χ²_8 | 8.00 | 2.73 / 4.19 / 7.34 / 11.81 / 15.51 | | |
| C_e | gibuu8 | b̃'s own χ²; width ratio | 219.90 | width ratio median 1.116 (0.698–1.749) | | |

## 4. 5A, `period`: STOP

**Run:** 06:25:33Z, under 1 s; **exit 3** (`cluster/period.out`, `period.err`). Every refusing control passed first:
S, P0 (eight checks), P1, P2 and P3, and the P4 assertion held.

**The refusal, verbatim** (`cluster/period.err`):

> REFUSED leak guard: readout carries 22 number(s) equal to f, an absolute cell value or f - g (ruling 6); nothing more was written

No `fd_ct_period.json` exists. As binding §3 condition 3 requires, nothing was rerun or repaired.

**The diagnostic,** authorized once by the director's ruling of 2026-10-29 (option (a)), ran on login37 at
06:29:57Z (`diag/`):
- `diag_period.py` (`e02e96a4…`) imported the deployed tool in-process, `cccc47aa…`, with no edit or copy.
  `diag_run.sh` (`00cfa0d6…`) gave it §2.2's period argv, except an `--out-json` under `$B/diag/` that it never wrote.
  The clone still had 0 porcelain lines afterwards.
- It prints key paths and matched roles only, and no value. Before the real run it reproduced a planted near-f cell on
  the synthetic fixture (`diag_localtest.py`).
- **It found:** 22 offending numbers, equal to the tool's own count. All are number tokens inside strings (the
  schema, the period labels, the cells list, the sha256 strings, the argv). Each matched only "f/central X_sup" or
  "central X_sup/f" for cell R09. No numeric field offended.
- **R09 is the one cell whose central partial integral over the 2D term's support, X_sup, is f to within
  LEAK_REL = 10⁻¹³ but not exactly.** The tool dropped a central X_sup only where the outside share was exactly 0, as
  it is in the other fifteen cells. So R09's f/X_sup ≈ 1 entered the guard's table, and every "1" in a string matched
  it. This is a false refusal: no written number carried f or an absolute value.
- **Disclosure:** the diagnostic also printed the cells masked because their central X_sup equals f exactly (outside
  share 0): R00–R08 and R10–R15. That is the |X_sup/f − 1| = 0 case of the condition the ruling named, but it is one
  list more than the ruling enumerated. The director accepted it as the zero case of the authorized condition.

**The repair** is amendment 1 (`FD-CT-READERS-AMENDMENT-1.md`, its own PR). It drops a central X_sup wherever
|X_sup/f − 1| < LEAK_REL, with tests in both directions and a mutation round. It runs nothing until the director
re-binds it.

**5A's weighting, for its own report** (binding ruling 6): the primary weighting is the (e) central value. That departs
from the addendum's "the cell's prior weight" (`LIMITATION-PLAN-ADDENDUM-20261028.md` §5.2). The reason: the projection
averages the 2D offsets over the pooled result's content in each footprint, and 2D's own construction used x = E_U,
the data. The choice was made before any 5A quantity existed. MnvTune v1's prior is the declared sensitivity.

## 5. Ledger, walls and storage

| step | host | start (UTC) | end (UTC) | wall | projection | rc |
|---|---|---|---|---:|---:|---|
| deploy and tests | login37 | 06:17:41 | 06:24:20 | 399 s | — | tests 0 |
| 3a `recoil` | login37 | 06:24:40 | 06:24:41 | ~1 s | 60 s | 0 |
| 4C `chi2` | login37 | 06:24:41 | 06:25:33 | 52 s | 300 s | 0 |
| 5A `period` | login37 | 06:25:33 | 06:25:33 | <1 s | 60 s | 3 (STOP) |
| 5A diagnostic (ruling (a)) | login37 | — | 06:29:57 | seconds | — | 0 (the diagnostic's own exit) |

All 0 node-h, no Slurm job. The rows are in `fd/LEDGER.tsv`. **Retention:** `$P/fd-ct-readers-20261028/` (deploy
clone, logs, the two readouts, `diag/`) joins the pscratch list.

## 6. Not changed

Every covariance, cell, readout and κ, and the reported matrix C_total + C_resp; `docs/analysis-note/**`. Claims, KI-85
and publication are Joseph's. Nothing is submitted, deposited or tagged.
