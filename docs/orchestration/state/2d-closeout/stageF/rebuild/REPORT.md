# Stage F rebuilds R1–R4, phase 1: report (products, numbers, χ², figures)

**Owner:** the paper-tighten lane, as director (Stage F). Run 2026-10-18 under the frozen [`SPEC.md`](SPEC.md)
(freeze `40e1265d`; step B `01f70c37`), after Joseph adopted Q = S5 total + C_PL
([`DECISION-20261017`](../../../../DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md)).

**CITABLE FOR:** the values of every 2D-covariance-dependent number and figure that SPEC §3a maps to a receipt, for
phase 2 to write into the deliverables; and KI-90's consumer patch and its "verify they ran" evidence.
**NOT CITABLE FOR:** any text in a deliverable (phase 2), a claim (J3/R5), disclosure wording (J4), KI-85 (J5), a
coverage, calibration or validation statement, or an outward act (J6).

## 1. Run

| field | value |
|---|---|
| Where | Perlmutter `login04`, root_6_28 (python 3.11.14, matplotlib 3.10.8, numpy 1.26.4), 0 node-h; `/pscratch/sd/j/josephrb/tmp-2d-rebuild-20261018/` |
| Runner | [`scripts/run_rebuild.sh`](scripts/run_rebuild.sh) `1f4d16d4…`, then [`scripts/check_rebuild.py`](scripts/check_rebuild.py) `1d994f84…` (committed with this report; both ran byte-identical) |
| Exit codes | every one of the 33 invocations rc 0 ([`outputs/RUN.txt`](outputs/RUN.txt)) |
| Step A | [`scripts/build_q_products.py`](scripts/build_q_products.py) `050c5b0d…`: **ALL 76 STOPS AND CONTROLS PASSED** ([`outputs/logs/stepA.log`](outputs/logs/stepA.log)) |
| Cross-run checks | **32/32 passed** ([`outputs/checks.json`](outputs/checks.json)) |
| Fig. 1 | local, pinned venv (matplotlib 3.11.2, numpy 2.5.4); environment control reproduced the committed VL175 figure `49766e26…` byte for byte; [`outputs/fig1/RUN-fig1.txt`](outputs/fig1/RUN-fig1.txt) |
| Durable copy | CFS `m3246/josephrb/2d-closeout-stageF-rebuild-20261018/`, 127 files, `sha256sum -c` all OK ([`outputs/SHA256SUMS.cfs`](outputs/SHA256SUMS.cfs)). `uq_adopted_covariance.root` `fdbbae5d…`, `cov2d_Q_205.npz` `771e49a5…` |
| Recompute | **REPRODUCED**, 31/31 (§5) |

**Controls that passed (step A):** VL175 `budget.json` summary fields to 1.7e-13; `group_medians.json` exactly;
`combination.json` to 1.5e-15 and its projections at 4 decimals; `s5.json` block summaries to 4.5e-16;
`\rhoFluxMuon` 0.900. A0–A5 all hold (cell sets equal; value-anchored order; storage exact; Q = S5 + C_PL exactly;
read-back exact; symmetric, PSD).

## 2. KI-90 (step B)

- **Equivalence on VL175's inputs** (unpatched archive 1 vs patched archive 2): the nine `run_repair.sh` χ² logs are
  identical after removing the added check lines; the lines added are exactly SPEC §4's (ml pass in all; one
  warning in adopted; a universe pass in control and repaired). The three fig. 6/7 runs give identical
  `summary.txt` and byte-identical PNGs.
- **Every Q run shows the identity check passing on `hReportedCells`**: the three χ² forms (one pass line each, no
  warning) and fig. 6/7 (four pass lines). This is CHECKLIST K3's "verify they ran" for KI-90's two consumers.
- Not recorded as a remedy of KI-90's producers or of any other consumer; K3 closes the row only to that extent.

## 3. The numbers (`outputs/outA/budget_Q.json.gz`; uncompressed sha256 `e7e3f24c…`, as in `outA/SHA256SUMS`)

`budget_Q.json` and `cov2d_Q_205.json` are committed gzipped, as `c04-repair/products/build.json.gz` was. The
receipt-artifact pre-commit check reads five check names in `budget_Q.json` (`A4_readback_<file>.root`) and three
cluster products named in `cov2d_Q_205.json` (`production_cov.npz`, `playlist_term.npz`, `s5_plus_playlist.npz`,
which it also cites by full CFS path) as in-repo artifacts missing from git. None is an in-repo artifact. The check
classifies a bare name as MISSING before it tries the same name cited by path (`verify_receipt_artifacts.py`
`classify_bare`). That ordering is reported to the coordination-tooling owner, not changed here.

Relative σ in percent of `E_U`; integral = width-weighted total σ.

| matrix | cell median | p84 | max | integral |
|---|---|---|---|---|
| **Q (adopted)** | **6.448** | 9.184 | 23.64 | **4.755** |
| S5 total | 6.041 | 8.953 | 23.29 | 4.328 |
| universe | 5.969 | 8.728 | 20.28 | 4.328 |
| universe + stat | 6.040 | 8.953 | 23.29 | 4.328 |
| stat | 0.684 | 1.712 | 17.98 | 0.061 |
| c08 (training seed) | 0.057 | 0.140 | 0.715 | 0.0025 |
| C_PL (run period) | 2.137 | 3.308 | 5.694 | 1.968 |
| `band_Flux` | 3.747 | | | 3.640 |

- **Against `E_C`** (exact-split denominator): Q 6.410, S5 total 6.047, universe + stat 6.046.
- **Variance shares of Q:** universe 0.871 per cell (median), 0.828 of the integral; C_PL 0.099 and 0.171; stat
  0.0094 and 0.00016; c08 6e-5 and 3e-7.
- **Ranks / conditions** (eigenvalues of (C+Cᵀ)/2 above t·λmax): universe 123 (t = 1e-10) / 137 (1e-12); universe +
  stat, S5 total and Q 197 / 205. Universe + stat cond 8.17e11 at 1e-12.
- **Against the paper:** √Tr(Q)/√Tr(TotalCovariance) = 1.071; √Tr(stat)/√Tr(StatOnly) = 0.428; per-cell median
  σ_stat/σ_StatOnly = 0.435.
- **Copied from `s5.json`:** stat centring, median |offset|/σ_mean = 4.43 (the replica mean's offset, in units of
  σ/√300: 0.26 σ); MAT agreement 3.4e-16.
- **Not computed:** the "99.6%" flux leading-mode share (no committed producer). `\rhoFluxMuon` = 0.900 does not
  depend on Q.

## 4. χ² against the published covariance, and figures

| quantity | VL175 (current text) | **Q** | receipt |
|---|---|---|---|
| χ²/ndf, paper Total + ours (`\chiCombined`) | 0.994 | **0.964** (197.59/205) | [`chi2_Q_std.txt`](outputs/chi2/chi2_Q_std.txt) |
| log-normal (`\chiCombinedLog`) | 1.014 | **0.987** (202.33/205) | [`chi2_Q_lognormal.txt`](outputs/chi2/chi2_Q_lognormal.txt) |
| paper stat subtracted (`\chiCombinedSubStat`) | 5.80 | **6.012** (1232.38/205) | [`chi2_Q_substat.txt`](outputs/chi2/chi2_Q_substat.txt) |
| combined pull mean / RMS | 0.048 / 0.406 | **0.042 / 0.398** | standard-form log |
| ours only, direct inverse: universe + stat / Q | 24.4 (universe + boot) | **23.57 / 23.23** | [`ours_only_*.txt`](outputs/chi2/) |

- The ours-only universe-alone direct inverse is numerically meaningless (rank 137/205 at 1e-12, cond 5.6e12, a
  negative χ²); it is reported only because the script prints it.
- The pull "RMS" is the standard deviation about the mean (0.398). The recompute's root-mean-square, 0.400, is the
  same data (√(0.400² − 0.042²) = 0.398).

**Figures:**
- Fig. 1 [`outputs/fig1/fig1_validation.pdf`](outputs/fig1/fig1_validation.pdf) `82665808…`. Its inset reads 6.45%
  against the published 6.85%. Its residual statistics (published σ) are unchanged by Q.
- Figs. 6/7: [`outputs/fig67/`](outputs/fig67/) (PDF and full-precision projections; legend labels "Training seed"
  and "Run period" are provisional).
- Statistical-block figures: [`outputs/stat/`](outputs/stat/). The colorbar's "std/mean" now means σ/`E_U`, a
  caption item.

## 5. Independent recompute

A fresh verifier wrote its own code without opening the producers, from the four pinned inputs. It reproduced all 31
claimed values exactly at their printed precision: the per-cell and integral σ, ranks, the three χ², and the two
direct-inverse χ² with their condition numbers. Its files are in [`outputs/recompute/`](outputs/recompute/), with
`SHA256SUMS` (`sha256sum -c` OK on the cluster).

**Finding for phase 2 and J4: the log-normal χ² depends on its definition.** 0.987 reproduces only with
δ = ln E_U − ln paper and C_ln = (Total + Q)/(pᵢpⱼ), both scaled by the paper value. Scaling Q by our own value gives
1.197; scaling both by ours, 0.958; geometric mean, 0.963; ln(1 + C/pp), 1.015. The deliverable must state the
definition next to the number.

## 6. What phase 2 receives

- Every receipt above, mapped by SPEC §3a.
- **Not recomputed, with reasons (SPEC §3a):** the VL169 coverage macros and the post-hoc rescoring (a superseded
  band; S5's stat block is untested, KI-85); the regularization scan (no producer); the seed-scan figures (C08
  replaces them); the "99.6%" flux share (no producer).
- `make_figures.sh` lines 54 and 57 still regenerate figs. 6/7 and the stat figures from VL170 inputs, and must be
  updated in phase 2.

**Same-model caveat:** the director, the implementer, the reviewers and the verifier are Claude Opus 5.5 on the
claude-school account.
