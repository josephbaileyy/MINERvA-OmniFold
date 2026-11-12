# L-rows G1–G5: the fresh referee round's cheap lookups (2026-11-12)

**By** the valid-region lane (director-helper-2), at the director's request of 2026-11-12, for director-helper-3 to
place in #977.

**Source:** the fresh referee round on #977 at `283f3044` (5/10). The report is in the director's scratchpad
(`referee6/gpt.txt`), and its run header records the round.

**What these are:** numbers and readouts only, with no paper text. Each was computed locally from committed records:
no job, no cluster read. Every script runs from the repository root as `python3 -I <script>` and writes the `.json`
beside it.

**CANNOT AUTHORIZE:**
- any paper or Supplement sentence. helper-3 places the numbers, and the wording rules are #977's;
- printing G2 at all. That is Joseph's decision.

| file | sha256 |
|---|---|
| `cp_intervals.py` / `.json` | `203e98d2` / `73e25db3` |
| `geant_share.py` / `.json` | `4afc0c8a` / `4d93b3c9` |
| `rounding_decomp.py` / `.json` | `098f5b35` / `46c6f8f3` |
| `reconcile.py` / `.json` | `a686195c` / `ecdb66a2` |

## G1, major 3: Clopper–Pearson 95 % intervals on the observed coverage fractions

**Inputs:**
- `fd/receipts-cov2d/readout/{AR23,G18}/score_*.json` (`fe5263e9`, `84976694`) [`grade/counts`, `grade/joint_count`];
- the nulls `null_*.json` (`80274e52`, `6bd5259d`) [`null/p_cell`, `null/q_joint`].

**What is counted** (nd-unfolding/fd_1b_mc.py:666, :680 @ `25192993`):
- a cell's count is #{toys with |e_c| ≤ σ_c} of 300;
- the joint count is #{toys with χ² ≤ the null's `chi2_cut`}.

Each interval is two-sided and covers one fraction. It is not simultaneous, and it is not the test's flag rule (one-sided, Bonferroni,
at the null content minus 3 MC standard errors, `fd_1b_null.thresholds`).

| | joint | CP 95 % | null content | flagged cells |
|---|---|---|---|---|
| AR23 | 0 / 300 | [0, 0.0122] | 0.6918 | cell 29: 164/300 = 0.547 [0.488, 0.604], null 0.685; cell 56: 148/300 = 0.493 [0.435, 0.551], null 0.684 |
| G18 | 0 / 300 | [0, 0.0122] | 0.6972 | cell 29: 148/300 = 0.493 [0.435, 0.551], null 0.687 |

**Over the 205 cells,** the null content lies:
- above the cell's CP 95 % upper limit in 5 (AR23) and 4 (G18);
- below its lower limit in 137 (AR23) and 103 (G18) (over-coverage);
- inside in 63 (AR23) and 98 (G18).

`cp_intervals.json` [`tunes/<T>/cells/per_cell`] gives every cell.

**LL5D's form:** 300 toys per truth and reading, with the same two counts on 16 cells
(`LL5D-DECLARATION.md:471-472`). The interval will be cp95(k, 300) on its readout's k. Two reference points:
- at k = 205 (the 1σ content 0.683): [0.627, 0.736], half-width 0.054;
- at k = 0: [0, 0.0122].

`ll5d_form/at_k` lists further k.

- **CITABLE FOR:** the intervals as computed on the committed counts.
- **NOT CITABLE FOR:** a revised verdict. The test's verdicts stand as graded.

## G2, the GEANT middle option: GEANT_Neutron and GEANT_Proton in the reported covariance

**Readout only.** Joseph decides whether it prints. The GEANT channel split (#1081) stays NOT CITABLE and is not used
here.

**Inputs:**
- S1's committed universe unfolds `s1/readout/s1_assembly/S1_GEANT_{Neutron,Proton}_{0,1}.npz`, through the float64 U
  of the committed H2 definition;
- the reported covariance C_total + C_resp + C_PL5D and its parts (`fd/with-cpl/data-product/fd_data_product_cpl.json`,
  `d6752d2c`);
- C_model's vertex shifts (`nd-unfolding/pv-ladder/readouts/cmodel_5d.json`, `3cfdc6a5`);
- F0b's graded truths (`fd/with-cpl/readout/fd_f0b_readout.json`, `5f542830`).

**Controls:**
- The four detector bands, rebuilt this way, reproduce S1's committed detector relative σ to 2.5e-14.
- C_model_abs is rebuilt from the shifts to 7e-16.

**Diagonal share of the reported covariance, both bands together:**
- median 0.02 %, and at most 0.21 % (R08: neutron 0.10 %, proton 0.11 %);
- removing both would lower the reported σ by a median 0.01 % and at most 0.11 %;
- their share of the fractional trace is 0.045 %.

`geant_share.json` [`diag_share_of_reported`] gives the per-cell values and each band alone.

**The bias tests' χ²** (F0b, the fake-data grades: χ² = bᵀ(C^(T) + C_x + N_T)⁻¹b, fd_f0_regrade.py:14-15, :31
@ `25192993`):
- Dropping the two bands raises χ² by at most +0.57 (q3, 52.27 → 52.84). Relative to χ², the largest rise is +1.8 %
  (A7_genie_mec).
- No graded truth's |z| > 2 cell list changes. A7_gibuu keeps R02 and R06.
- At N_T = 0 the changes agree to within 0.01 on every graded truth.

**Caveat on the χ² readout:**
- Only N_T's diagonal is committed (`noise_sigma`; the full N_T is the covariance of each truth's mean,
  fd_f0_regrade.py:217, :792). So the committed χ² is reproduced approximately: within 0.76 % for the 12 graded truths,
  and 21–75 % off for the six ungraded P-truths, whose N_T off-diagonals matter.
- The Δχ² values are computed consistently within that approximation. An exact value would need the regrade's
  per-experiment products, a 0 node-h login read.

- **CITABLE FOR:** nothing until Joseph rules. These are values for the readout.
- **NOT CITABLE FOR:** the GEANT departure's cause, coverage, or any validation of the bands' treatment.

## G3, major 7: the rounding jitter inside the statistical bootstrap

**Inputs:**
- RS1's R0 readout `fd/rounding-stability-20261106/receipts/full-a1/read/rs1_r0.json` (`724f0c3a`): σ_J/f from I0's
  20 data jitters; S1's bootstrap σ_stat/f; R0a = their ratio;
- `fd_data_product_cpl.json` for the scale.

**Assumption:** R0b's, that the jitter and the remaining sampling variances add per cell
(`rs1_r0.json` [`assumption`]).

**Results:**
- **Jitter share of each cell's bootstrap variance (R0a²):** median 26.2 %, range 14.9–67.0 % (max R10).
- **The bootstrap σ without the jitter** is lower by a median 14.1 %, and by 7.7–42.6 % across cells.
- **Against the reported σ (C_total + C_resp + C_PL5D),** removing the jitter lowers it by a median 0.009 %, and by
  at most 0.048 % (R05).

**What the committed products cannot give:** the off-diagonals, because I0 recorded per-cell spreads only. So the
change in the statistical covariance's correlations is not computed. Two ways to get it: <!-- absence-ok: a scoping statement: this readout computes the diagonal only, because I0's committed record (i0.json) holds per-cell spreads; it does not claim the off-diagonals are unknowable -->
- **the exact jitter covariance:** from the 20 data-jitter unfolds I0 graded, if they survive on pscratch. That is a
  login read at 0 node-h, with the script's sha256 to the director first;
- **a bootstrap without the jitter:** S1's 50 statistical replicas (`s1_assembly.json` [`meta/stat_replicas`]) rerun
  without it. That is 50 unfolds, about 1.4–1.5 node-h at 0.027–0.029 node-h per item
  (`FD-1B-PRECHECK-FD-DECLARATION.md:229-230`).

- **CITABLE FOR:** the diagonal decomposition, under R0b's additivity assumption.
- **NOT CITABLE FOR:** correlations, or any statement that the jitter-free bootstrap was run.

## G4, major 8: a run-period figure of reconstructed and unfolded double ratios

**Whether the products exist: yes, all committed, so the figure is local work at 0 node-h.**

| content | where | sha256 |
|---|---|---|
| unfolded double ratios by p_∥ for the period groups (P_A = 1A–1F, P_B = 1G–1M, P_C) against each other and the pool, with the step and its 10-pair bootstrap noise (`dr_*`), the raw ratios (`raw_*`) and the closure terms (`bias_*`, `mc_*`) | `2d-closeout/period-unfold-20261014/outputs/analysis.json` [`comparisons/<pair>/pz_marginal_shift_pct`, `…/step`] | `05edff61` |
| the same after RE-2's refined background (the reported 2D configuration) | `stageF/methods/re2/run/partc_r2/partc-r2/periods/analysis.json` | `2ce5d5da` |
| reconstruction-level reference 1G–1M vs 1A–1E by p_∥, with its step (+6.1 %) | `period-unfold-20261014/outputs/analysis.json` [`reco_reference_1G-1M_vs_1A-1E`] | `05edff61` |
| per-playlist reco templates on the 14×16 analysis grid (data D; signal S, S2; background B, B2), for reco double ratios on the same P_A/P_B/P_C groups | #977 branch, `methods-short-20261109/pscr-20261112/members/work_proxy.npz` @ `60d14439` | `42ce788b` |
| the 5D per-playlist offsets on R00–R15 | `fd/receipts-rpd/run/readout/fd_rpd.json` | `c0b06cfd` |

**Price:** 0 node-h. A local producer would draw two panels, reco and unfolded by p_∥, for P_B/P_A and P_C/P_A, with
the bootstrap noise band. It needs about 2–3 hours, including a check that its unfolded steps equal the committed
`step` values. Not made, as asked. The figures lane would own the producer.

## G5, minor 6: two reconciliations

**The period steps are two evaluations of the same quantity:** the p_∥ step of the double ratio 1G–1M (P_B) against
1A–1F (P_A) after per-period unfolding, with σ from ten paired bootstrap draws.

| printed | where printed | configuration | source |
|---|---|---|---|
| +(6.94 ± 0.41) % | the paper, `paper_body.tex:233` @ `60d14439` | the original 2D unfolding, purity background | `period-unfold-20261014/outputs/analysis.json:2165-2166` [`comparisons/dr_PB/PA/step`]: 0.069427, noise 0.004135 (`05edff61`) |
| (+6.89 ± 0.46) % | the Supplement, `supplemental_body.tex:500` @ `60d14439`, copied from the note, `sec_systematics.tex:165` @ `25192993` | the RE-2 refined 2D unfolding (negweight-refined background), the adopted 2D result (DECISION-20261024-joseph-adopt-re2-2d-refined) | `re2/run/partc_r2/partc-r2/periods/analysis.json:2165-2166`: 0.068881, noise 0.004594 (`2ce5d5da`); RE-2 part C's `values_table.tsv:162-163` (`d0a8f47b`) lists the purity → refined pair, applied to the note in `5b2d0618b` |

So the paper prints the pre-RE-2 value, and the Supplement prints the refined one. This is a fact for helper-3, not a
correction made here.

**The lower endpoints are two populations of cells** over the same three shape changes (W1, W2, W3):

| printed | key | population | W1 / W2 / W3 |
|---|---|---|---|
| 16 % to 31 % (Supplement Table S10 row 2, `supplemental_body.tex:649` @ `60d14439`) | `s5e-shapes-ewmax-lo/-hi` (make_values_fived16.py:1677) | every (E_avail, W) cell | 31.32 % at EW29 / **16.38 % at EW37** / 23.67 % at EW29; `docs/orchestration/state/s5e/cand/assess_receipt.json` [`points/<W>/ew_max_abs_pct`] (`84266e30`) |
| 9 % to 31 % (the paper, `paper_body.tex:175` @ `60d14439`) | `rec-w-supmax-lo/-hi` (make_values_fived16.py:2020-2022) | supported cells only | 31.32 % at EW29 / **8.78 % at EW9** / 23.67 % at EW29; `secondary-results/referee-figure-deformation-20261112/check-a/a_recovery.json` [`shapes/<W>/max_abs_residual_supported`] (`75db95a1`, #977 branch) |

**Why they differ:** only W2's largest residual changes, because it lies in EW37, an unsupported cell. The producer's
comment already records this (make_values_fived16.py:2020 @ `60d14439`).

- **CITABLE FOR:** the provenance of each printed number.
- **NOT CITABLE FOR:** which number the paper should print. That is helper-3's and the director's call.
