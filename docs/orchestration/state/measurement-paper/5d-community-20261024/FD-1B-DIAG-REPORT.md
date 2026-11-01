# REPORT 1B gate-D diagnosis: NOT LOCALIZED, so 1B stops (2026-11-01)

**By** the measurement session `coverage-5b`, for the director.

**Under:**
- [`FD-1B-DIAG-DECLARATION.md`](FD-1B-DIAG-DECLARATION.md) (#626, M3 `ea297761`), bound by
  [`FD-1B-DIAG-BINDING.md`](FD-1B-DIAG-BINDING.md) (#633, merged 2026-11-01T03:33:35Z);
- `DECISION-20261031-joseph-three-covariance-files-and-1b-diagnosis.md`, item 2.

**The verdict: NOT LOCALIZED.** L1 (named bands) FAIL and L2 (the carry) FAIL.
- **The branch (declaration §4, bound):** 1B stops, with this report.
- **No repair is named.** What 1B tested stays the matrix without the run-period block, C_total + C_resp of
  `fd_data_product.json` (`b79556f0…`).
- **Disclosure:** the paper and the note disclose the stopped attempt in every outcome (the decision). That text is
  the paper lane's.

**MEASURES:** the declared readouts, all labelled DERIVATION. **CANNOT SUPPORT:** any claim about the coverage of the
reported intervals, in either direction. No coverage toy ran. The statement that the coverage of the reported
intervals has not been validated stands.
<!-- absence-ok: restates the decision record's own statement (DECISION-20261031-joseph-three-covariance-files-and-1b-diagnosis.md item 3); this report adds no search claim -->

## 1. The run

| item | value |
|---|---|
| node | login37, `nice -n 19`, 0 node-h; no job |
| deploy | `$B/deploy/diag`, a fresh clone detached at M3 `ea2977613cd051dc3c2b321c7fad44f7a6d3ef2c`, empty porcelain |
| code | `fd_1b_diag.py` `96d72445…`, `fd_1b_score.py` `c6c9a45f…`, recorded in the readout |
| inputs | the 176 derivation products in `$B/runs/derivation`; S1's assembly (`db000707…`); gate D's committed readout (`e1838c0a…`, pinned in code) |
| run | 2026-11-01T06:32Z, one run, rc 0, 3 s wall; no rerun |
| consistency control | its ρ equals gate D's committed ρ bit for bit (it refuses otherwise) |
| readout | `$B/score/diag.json`, 69,691 bytes, sha256 `6fd6669efdae5e8dd0934962b4547537a92d37371df6ad481c7df7dd2dfb2a4f` |
| time | from the binding's merge (03:33:35Z) to this report: under 4 h, inside the 24 h time-box |

It wrote only to `$B/deploy/diag`, `$B/score/diag.json` and `$B/logs/diag.log`. The receipts are in
[`fd/receipts-1b/diag/`](fd/receipts-1b/diag/): the readout, its log, and the connect's script and transcript.

## 2. L1, named bands: FAIL

**No set of at most K_MAX = 3 of the 38 bands puts every cell in [0.9, 1.1].** The readout reads `size: null`,
`n_sets: 0`, and the union and intersection are both empty. Since no minimal set exists, no band is named.

**Why, as arithmetic.** S1's stat, normalization and lateral blocks enter both sides. So, exactly,

    ρ_c² − 1 = Σ_b (E_b,cc − M_b,cc) / M_d,cc,

and each band's term is its "excess" (`share_toys · ρ_c² − share_s1`, from the readout; the terms sum to ρ_c² − 1 to
1e-9). Substituting S1's block for band b removes its term. A cell is in the window when ρ_c² ∈ [0.81, 1.21].

Two cells cannot be brought into the window by any set of at most 3 bands, **even on their own**:
- **R08** (ρ² − 1 = +4.271) needs its excess cut by 4.06. Its three largest positive terms, MaRES +2.098, MaCCQE
  +1.224 and MvRES +0.602, sum to 3.924.
- **R07** (ρ² − 1 = −0.516) needs 0.326 recovered. Its deficit is spread across bands, and no three of them recover
  it.

So L1 fails whatever happens in the other cells. The other failing cells close with one band (R00, R02, R05, R09,
R13), two (R10, R12, R15) or three (R11) on their own, but no single set of at most three closes them all.

## 3. L2, the carry: FAIL

ρ_raw, every band's block uncarried, is in the window in **4 of 16 cells**. g = f / x_T runs from 0.909 to 1.254.

| cell | ρ_c | ρ_raw,c | g_c |
|---|---:|---:|---:|
| R00 | 1.157 | 1.118 | 1.064 |
| R01 | 1.032 | 0.972 | 1.151 |
| R02 | 1.149 | 1.177 | 0.964 |
| R03 | 0.938 | 0.855 | 1.180 |
| R04 | 1.020 | 0.998 | 1.026 |
| R05 | 0.838 | 0.727 | 1.226 |
| R06 | 1.015 | 1.105 | 0.909 |
| R07 | 0.696 | 0.622 | 1.159 |
| R08 | 2.296 | 1.842 | 1.254 |
| R09 | 1.113 | 0.999 | 1.132 |
| R10 | 1.780 | 1.488 | 1.200 |
| R11 | 1.827 | 1.520 | 1.218 |
| R12 | 1.251 | 1.128 | 1.178 |
| R13 | 1.314 | 1.119 | 1.214 |
| R14 | 1.091 | 0.911 | 1.240 |
| R15 | 1.418 | 1.257 | 1.159 |

ρ_raw is inside [0.9, 1.1] at R01, R04, R09 and R14 (0.972, 0.998, 0.999, 0.911); every other cell is outside.
Removing the carry lowers ρ where g > 1 and raises it where g < 1, and it closes neither R08 (1.842) nor R07
(0.622). As bound, L2 tests only the uncarried alternative for all bands at once.

## 4. The per-band readout

The per-band carried and raw σ ratios and the S1 and toy shares, for all 38 bands and 16 cells, are in `diag.json`
(`per_band`). The table gives each band's term (E_b,cc − M_b,cc) / M_d,cc for the eight largest by Σ_c |term|, with
the other thirty summed. The rows add to ρ_c² − 1.

| band | group | R00 | R01 | R02 | R03 | R04 | R05 | R06 | R07 | R08 | R09 | R10 | R11 | R12 | R13 | R14 | R15 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MaRES | interaction | +0.130 | −0.007 | +0.212 | +0.019 | +0.056 | −0.016 | +0.115 | −0.028 | +2.098 | −0.025 | +1.611 | +1.662 | +0.235 | +0.596 | −0.028 | +0.796 |
| MvRES | interaction | +0.030 | −0.001 | −0.001 | −0.017 | +0.008 | −0.034 | +0.007 | −0.080 | +0.602 | −0.034 | +0.379 | +0.351 | +0.072 | +0.048 | −0.018 | +0.219 |
| MaCCQE | interaction | +0.017 | −0.002 | −0.020 | −0.000 | +0.006 | −0.000 | −0.081 | +0.001 | +1.224 | −0.001 | +0.032 | +0.013 | +0.281 | +0.020 | −0.000 | +0.022 |
| Flux | flux | +0.139 | +0.005 | +0.096 | +0.087 | −0.042 | −0.171 | −0.019 | −0.072 | +0.219 | −0.017 | +0.103 | +0.034 | −0.022 | −0.040 | +0.138 | −0.012 |
| Rvn2pi | interaction | +0.001 | +0.002 | +0.023 | −0.152 | −0.000 | −0.020 | +0.032 | −0.163 | +0.010 | +0.076 | +0.055 | +0.160 | −0.002 | +0.059 | +0.013 | +0.031 |
| Rvp2pi | interaction | +0.005 | −0.004 | +0.063 | −0.052 | +0.001 | −0.011 | +0.040 | −0.052 | +0.026 | +0.025 | +0.100 | +0.082 | −0.004 | +0.035 | +0.002 | +0.056 |
| MFP_pi | interaction | +0.005 | +0.059 | +0.002 | −0.003 | +0.001 | +0.019 | −0.002 | −0.010 | +0.012 | +0.076 | +0.003 | +0.009 | −0.001 | +0.004 | +0.044 | −0.001 |
| MinosEfficiency | detector | +0.009 | +0.000 | +0.002 | +0.022 | +0.007 | −0.024 | +0.024 | +0.012 | −0.022 | +0.020 | −0.013 | +0.004 | −0.011 | −0.003 | +0.012 | −0.010 |
| the other 30 | | +0.004 | +0.012 | −0.057 | −0.025 | +0.003 | −0.042 | −0.086 | −0.123 | +0.103 | +0.119 | −0.100 | +0.022 | +0.016 | +0.009 | +0.029 | −0.089 |
| **ρ² − 1** | | +0.338 | +0.065 | +0.321 | −0.120 | +0.041 | −0.298 | +0.030 | −0.516 | +4.271 | +0.240 | +2.170 | +2.337 | +0.564 | +0.728 | +0.191 | +1.012 |

- **The largest terms.** MaRES's are the largest: +2.098 at R08, and +1.6 to +1.7 at R10 and R11. MaCCQE's
  +1.224 at R08 and MvRES's +0.602 there come next.
- **Ratios against small blocks.** Per-band σ ratios reach far beyond 1 where S1's block is small; MaRES's run from
  0.160 to 184.4 across cells. The term above weighs each ratio by S1's share, which is why it, not the ratio,
  decides the rule.
- **NormDISCC** reads null in every cell: its block is zero in S1 and in the toys alike. No ratio reads "inf".

These are DERIVATION numbers. No mechanism is asserted, and none is tested here.

## 5. Not changed

The protocol, gate D's window, the tested matrix, the reported covariance, κ, every claim and number. Nothing was
submitted, and nothing went to CFS or HPSS.
