# Session 6 — PET saved-output diagnosis and interval feasibility

| field | content |
|---|---|
| `Lane` | Session 6, `pet` |
| `Decision` | Can the uncertainty of the declared PET point estimator be diagnosed from existing outputs, and what smallest new experiment would distinguish viable repairs from an unaffordable or inadequate procedure? |
| `Branch` / `Base` / `Head` | `prep/next-pet-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (the merged common baseline that supersedes the dispatch commit) / the commit that adds this file. The review section names the fixed commit the reviewer saw. |
| `Owned files` | Only `docs/orchestration/state/next-preparation-20261009/pet/`: `REPORT.md`, `reduce_saved.py`, `check_independent.py`, `design_cost.py`, `test_pet_q.py`, `results/saved_reductions.json`, `results/design_cost.json` and `results/operands.tsv`. No other path was written. |
| `Pinned inputs` | All are read at `5ac9706a`. 862 committed score files, each listed with its sha256 in `results/operands.tsv`; the digest of that list is `12b4e3dc…a12ffb`. The governing records are `nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md`, `PROTOCOL-20260925.md` (§§3, 4, 6.4, 8, 9, 11; Amendments 2c, 5, 5b, 6), `freeze/COMPLETENESS-s5c_a5_H2S1T24.tsv` (sha256 `6d2a25a7…`), `freeze/COMPLETENESS-look1.tsv`, `nd-unfolding/pet/generator_diagnosis/REPORT-20261006.md`, `nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md`, the Gate-6 receipt `docs/orchestration/state/gate6-member-trajectories-result-56847059.json` (sha256 `8f40541f…b6a5`) and `closeout/REPORT.md` §11. |
| `Resources` | Elapsed time is in §12. Local CPU was below 0.05 core-hours: every reduction takes under 4 s, and the tests and independent check take under 5 s. All of it ran single-threaded, with peak RSS ≤ 95 MB. New scratch/data is 0 bytes, because nothing was copied: the operands are already in the repository. About 0.35 MB of tracked files were added. Cluster/GPU: **0**. Training: **0**. |
| `Review` | See §11. |
| `Model / effort` | The model is Claude Opus 5.5 (`claude-opus-5-5`), as the session's system context states. Effort: not observable. |
| `Disposition` | **(1) Saved-output diagnosis: PASS** at study scale, conditional on the frozen banks, on the development tilt and with signal-only simulation (§4). **(2) Interval question and discriminating experiment: PASS.** The 192-unfold crossed pilot is rejected as not the smallest informative experiment. A named alternative, E1, is designed and priced and is ready for a separate decision (§§6–7). **(3) Complete procedure: FAIL** at the declared full-domain endpoint with independent inputs. It needs ≥ 118× the simulated inventory in independent events and ≈ 61 % of the last recorded GPU allocation at a 2 M-row prior, or 2.4× that allocation at 10 M (§8). The publication-ready objective is **not** achieved. |
| `Next action` | Joseph decides whether to authorize E1 look 1 (§7). It is 60 data-scale unfoldings of H2S1T24 K5 and costs ≈ 575 A100-h including the 20 % reserve (forecast band 291–1,150). It decides one thing: whether the frozen estimator's low-acceptance failure persists at data scale. If not authorized, PET stays diagnostic and the reopening conditions of §9 apply. |

## 1. Answer in brief

1. **The member spread mostly measures PET's own randomness, not sampling.**
   - The data are the 120 × 6 saved coverage members plus the 60 FINAL single fits.
   - Between-experiment event-sample variance is only **≈ 17 %** of the six-member mean's variance (median over bins 1–5). The remaining ≈ 83 % is internal randomness divided by 6.
   - A single nominal fit varies less across independent experiments than a Poisson member varies within one experiment: V1/W = 0.47–0.71. So the Poisson members do not reproduce between-experiment sampling.
   - This explains the over-wide §9 interval quantitatively. The interval charges the full member variance W(1 + 1/B), but the member mean carries only ≈ W/B of it plus a small sampling term.
2. **Fixing the width does not fix the procedure: bias then dominates.**
   - An interval sized to the variance the components model predicts (W_r/6 plus the sampling term, fitted in-sample) covers **0.545 at 68 % and 0.893 at 95 %** in aggregate, and **0.08 / 0.29** in the low-acceptance region.
   - On the development tilt itself, |bias|/sd of the six-member mean is 2.24 in bin 0 and 0.57–0.85 in bins 4–6. In the low-acceptance region it is 1.0–4.2 in every bin.
   - The proposed lower bounds tolerate at most **0.46 sd** (68 %) and **0.51 sd** (95 %) of bias.
   - On the generator reweightings (single fits, 8 draws), the bias reaches **2.9–4.1×** the §9 68 % half-width, and that half-width is itself 1.65–2.15× wider than a calibrated one in bins 1–6 (C4: 1.32–1.72 × its 1.25× limit).
3. **The interval's estimator is not the one the point rules certified.**
   - §§6.1–6.3 were decided on single unbootstrapped fits: E0 is 0.895, which reproduces exactly.
   - §9 reports the mean of six Poisson-bootstrap members. That is a different estimator: E0 0.943 on its own draws, and its expected histogram differs from the single fit's by **2.7–4.3 SE** in 6 of 7 bins.
   - A bootstrap bias correction would push the bias in the wrong direction.
4. **The 192-unfold pilot is not the smallest informative experiment.**
   - At study scale, the saved design already estimates every variance term it would, more precisely, and it would add nothing (§6).
   - At data scale it would cost ≈ 1,840 A100-h with the reserve (932–3,679).
   - Its component estimates do not answer the binding question, which is bias in the low-acceptance region and on the generator cases.
5. **The smallest discriminating experiment is E1** (§7). It uses data-scale six-member ensembles on the development tilt and on D5 NuWro, with a predeclared futility rule.
   - The rule relies on coverage being monotone in half-width: if even the wide §9 interval under-covers the low-acceptance region at data scale, no narrower repair of this estimator can pass.
   - If the study-scale behaviour persists, look 1 returns that no-go with probability 0.76. A calibrated procedure would be wrongly stopped with probability 0.007.
6. **The full procedure is not feasible as declared** (§8).
   - Multiplicity-adjusted validation at the 0.63/0.92 tolerances needs ≈ 430–540 independent replicates per case.
   - The never-drawn rows hold **0.35** of one data-size experiment. DEV holds **3** disjoint ones.

## 2. Inputs, ownership and conditions

- **Baseline.** `origin/main` was fetched at 13:00 PDT. It equals `5ac9706a`, with 0 commits after the pin, so there is no upstream delta to reconcile.
- **Worktree.** The worktree `MINERvA-OmniFold-next-pet-20261009` was created from the pin. No other `prep/next-*` branch had been pushed at the start, and none was pushed by the time of the last check.
- **Ownership.** I wrote only `Q/pet/`. `CATALOG.md`, `MANIFEST-overrides.tsv`, `MANIFEST.tsv`, the shared registers, publication sources and every other lane's files were not touched.
- **Data access.** Every operand is a committed per-run score JSON: already unblinded, already scored, already inspected.
  - No final-bank or reserve row was read, and no sealed data was opened.
  - Nothing was refitted. The D4c coverage members that were stopped incomplete stay unscored and unused.
- **Gate 6.** The Gate-6 family is not touched. Its receipt's exact `prohibitions_applied` keys are `do_not_select_passing_subset`, `do_not_construct_C_ML`, `do_not_move_central`, `do_not_start_leg_2` and `do_not_retry_unchanged`. Nothing here selects a subset, constructs `C_ML`, moves a central value, starts leg 2 or retries.
- **Terminal campaigns stay terminal.** `NO_ELIGIBLE_DESIGN` (VL167) and the PET-vs-GBDT results (VL168) stand. This lane does not resume the final-design study, its §11 repair, Gate 6 or P0.
- **Owner and review setup** (campaign review §1). The owner is this session. There is one fresh read-only reviewer with one review and one focused re-review. The decision answered is the Goal-6 sentence above. The terminal outcomes are the three dispositions in the header. A failed or inconclusive result completes the stage.

## 3. The declared estimator and interval, reconstructed from code

Sources: `PROTOCOL-20260925.md` §9 as amended by Amendment 2c; `runner/design_inputs.py:926-971` (`bootstrap_counts`, `member_seed`, `bootstrap_config`, `apply_bootstrap`); `analysis/score_design.py:241-266, 360-378`; `analysis/coverage.py`; the configs `configs/S5/`, `configs/S4F/` and `configs/S3P/`.

**Fixed estimator E\*.** H2S1T24 at K = 5, reported at iteration file `iter04.npz`.

- Step 1 is a PET hybrid with K = 3, local attention, 2 heads, 2 transformers and projection 32. It trains for 8 epochs per iteration with Adam at 4e-4 and batch size 512.
- Step 2 has the same network trained for 24 epochs (the "T24" N2 repair).
- Warm start across iterations; a 20 % row validation split, fixed across iterations; `restore: last`.
- The miss rule is efficiency-corrected. The feature arm is `reco_summaries_pdg_onehot`.
- Study scale is 600,130 prior and 600,111 pseudodata rows of signal-only simulation, with the inventory's response.
- A diff of the S5, S4F and S3P configs differs only in the four estimator seeds, the name and the note.

**Member b of replicate r** (b = 1–6):

- **Poisson weights.** Each pseudodata and prior event gets Poisson(1) weights, computed by inverting a uniform hash of `(STUDY_SALT/bootstrap, seed_r, b, side, event identity)`.
  - The pseudodata and prior streams use different salts, so they are independent.
  - `seed_r` is the replicate's bootstrap seed from the released manifest. It is shared by its six members and distinct across the 120 replicates; the latter is checked.
- **Estimator seeds.** All four seeds (`step1.seed`, `step1.validation.seed`, `step2.seed`, `step2.validation.seed`) are replaced by `sha256(MEMBER_SEED_SALT/field/seed/b) mod (2^31−1) + 1`. So each member has its own training seeds and its own validation split. No member shares a seed with another.
- **Events are shared.** All six members use the same prior and pseudodata rows. The loaders refuse otherwise.
- **The member's unfolded histogram** is the prior's `w_truth × Poisson count × push` over truth-passing rows. It is unit-normalized per histogram: the aggregate seven E_avail bins, and each historical acceptance region separately within that region.
- **The score target** is the replicate's own unweighted pseudodata truth. It never includes the pseudodata Poisson weight, and it is identical across members (checked to 1e-12). The FB population truth is reported beside it.

**Reported estimate and interval.**

- The estimate is the member mean of the six unit-normalized histograms, per bin.
- The interval is the mean ± t₅ × sd × √(1 + 1/6), with sd the member sd (ddof 1). The t₅ factor is 1.1037 at 68 % and 2.5706 at 95 %, and √(7/6) = 1.0801.
- The interval is per-bin marginal, and the inference is conditional on the frozen DEV/FB banks.
- **What it represents.** §9 says the interval represents pseudodata statistics, prior-MC statistics and training randomness. It does **not** represent detector-response, flux, background or physics-model uncertainty.
- **Why the √(1 + 1/B) factor.** It treats the member sd as an estimate of the sampling sd of one fit and adds the Monte-Carlo variance of averaging B members. §4.2 shows that the premise fails: most of the member variance averages away.
- **Dividing widths by √6 is not justified either.** The event-sample term D is common to all six members and does not average, the bias does not average, and the members share events. §4.3 shows that even the correctly averaged variance under-covers.

## 4. Saved-output diagnosis

### 4.1 Operands and controls

| object | content | binding |
|---|---|---|
| S5 coverage | 120 replicates × 6 members, development tilt D1 +0.35, k = 5 (720 files) | every member's `receipt_sha256` equals `COMPLETENESS-s5c_a5_H2S1T24.tsv`; the six members of a replicate share rows and differ in bootstrap member |
| S4F FINAL | 60 single unbootstrapped fits, the same estimator, one seed per replicate, development tilt (60 files) | every receipt digest equals `COMPLETENESS-look1.tsv`; seeds distinct |
| S-N2 | 2 DEV draws × 4 seeds at fixed events and nominal weights (8 files, `results/s3n/`) | the four seed runs of a draw share their row digests |
| S4S library | 8 FB draws × 9 cases (72 files) | committed score files |

**Reproductions.** These checks show that the operands and formulas are the ones the record used.

- **Coverage.** The pooled §9 coverage reproduces the decision record exactly: 68 % **0.896** and 95 % **0.990**. By region: low-acceptance **0.257 / 0.789**, moderate **0.701 / 0.964**, good **0.929 / 0.998**.
- **Single-fit E0.** The S4F E0 recomputes to **0.895**, with max |ΔR| = 0.0 against the committed `recovery_raw`.
- **Generator bias.** The D5 single-fit biases (S4S, FB0–7) reproduce generator-diagnosis T1b for H2S1T24 to its printed precision, for example NuWro bin 6 +34.3 × 10⁻³ and GiBUU bin 4 +11.4 × 10⁻³. T1b's development-tilt row equals the S4F FB0–7 mean, which differs from the library's own D1 +0.35 draws (another seed set): −14.7 against −6.9 × 10⁻³ in bin 6.

### 4.2 Variance components (aggregate E_avail; per bin; × 10⁻⁶ unless a ratio)

The model is member_rb = μ + D_r + P_rb + T_rb, with single_r = μ₁ + D_r + T_r:

- D is the replicate's event-sample effect, from its pseudodata and prior draw;
- P is the effect of the Poisson reweighting;
- T is the training and validation-split randomness at nominal weights.

The moment estimators are W = E[within-replicate member variance] = σ_P² + σ_T², V = Var(member mean) = σ_D² + W/6 and V1 = Var(single fit) = σ_D² + σ_T². Ratios carry 95 % replicate-cluster bootstrap bounds, resampling S5 and S4F independently, 2,000 draws.

| bin | 0 | 1 | 2 | 3 | 4 | 5 | 6 (3–100 GeV) |
|---|---|---|---|---|---|---|---|
| W (member variance) | 3.62 | 2.65 | 8.60 | 17.16 | 16.44 | 20.33 | 267.0 |
| V (member-mean variance) | 0.51 | 0.51 | 1.72 | 3.46 | 3.31 | 4.71 | 52.0 |
| V1 (single-fit variance) | 1.92 | 1.58 | 6.12 | 10.77 | 8.51 | 9.45 | 145.3 |
| σ_D² = V − W/6 | −0.10 | 0.07 | 0.29 | 0.60 | 0.57 | 1.32 | 7.5 |
| g = σ_D² / (W/6) | −0.16 | 0.16 | 0.20 | 0.21 | 0.21 | 0.39 | 0.17 |
| g, 95 % bounds | ≤ 0.04 | −0.21, 0.61 | −0.18, 0.65 | −0.16, 0.64 | −0.12, 0.59 | 0.01, 0.81 | −0.18, 0.58 |
| V1/W (< 1 ⇔ σ_P² > σ_D²) | 0.53 | 0.60 | 0.71 | 0.63 | 0.52 | 0.47 | 0.54 |
| V1/W, 97.5 % bound | 0.80 | 0.91 | 1.01 | 0.87 | 0.73 | 0.62 | 0.78 |
| σ_T²/W, S4F-derived | 0.56 | 0.57 | 0.68 | 0.59 | 0.48 | 0.40 | 0.52 |
| σ_T²/W, S-N2 on DEV (6 dof) | 0.33 | 0.37 | 0.33 | 0.24 | 0.25 | 0.13 | 0.22 |

**What this establishes.** These statements hold at study scale and are conditional on the banks.

- **The six-member mean's error variance is mostly internal randomness.**
  - The event-sample share of the member mean's variance is g/(1 + g), about 0.17 in the median interior bin.
  - g is below 0.81 at 95 % in every bin.
- **The Poisson members over-represent sampling variance.**
  - V1 < W, that is σ_P² > σ_D², at the 97.5 % bound in 6 of 7 aggregate bins and in 25 of 28 region bins (per bin, unadjusted, with correlated bins).
  - The Poisson perturbation changes the trained networks far more than an independent redraw of 600 k events changes the answer. So the member spread is not a bootstrap estimate of the sampling variance.
- **The nominal-seed share of the member variance (σ_T²/W) lies between 0.13 and 0.68**, depending on the instrument.
  - The S4F-derived value (between-experiment, 59 dof, by difference) sits about 2× above the direct S-N2 value (within-draw on DEV, 6 dof).
  - Their intervals overlap. I treat the gap as unresolved, not as an error.
  - The remainder is Poisson-induced (P), which is not separable from a P × T interaction in this design.
- **The quantitative mechanism of C1/C4.** The §9 variance is W(1 + 1/6), while the member mean's error variance is about W/6 + σ_D² + bias². Ignoring bias, the ratio of widths is √(7/(1 + g)), about 2.4. The measured member sd / RMS error is 1.66–2.17 in bins 1–6, because bias is not zero.

### 4.3 Bias, asymmetry, finite-sample truth and regions (six-member mean against its own truth)

| region | \|bias\|/sd per bin (0…6) | §9 68 % / 95 % coverage | misses at 68 %, estimate above / below | variance-model interval, in-sample, 68 % / 95 % |
|---|---|---|---|---|
| aggregate | 2.24, 0.39, 0.19, 0.31, 0.85, 0.57, 0.62 | 0.896 / 0.990 | 0.087 / 0.017 | 0.545 / 0.893 |
| low-acceptance | 4.17, 3.02, 3.23, 4.04, 3.39, 1.04, 2.97 | 0.257 / 0.789 | 0.640 / 0.102 | 0.080 / 0.292 |
| moderate | 3.23, 1.06, 1.16, 1.30, 0.50, 1.06, 0.67 | 0.701 / 0.964 | 0.256 / 0.043 | 0.405 / 0.765 |
| good | 0.47, 0.72, 0.81, 0.90, 0.83, 0.36, 0.71 | 0.929 / 0.998 | 0.025 / 0.046 | 0.554 / 0.929 |

The variance-model interval is mean ± t₅ √(W_r/6 + σ̂_D²), with σ̂_D² fitted on these same replicates. It is a diagnostic of what a variance-correct width would do, not a validated interval.

- **The over-width was masking bias.** Give the interval the width that matches the estimator's variance and it under-covers everywhere, while the misses stay one-sided.
- **Low-acceptance under-coverage is bias, not width.** The bias share of the MSE there is 0.899–0.946 in 6 of 7 bins, and the mean pulls are +1.75 to +2.35 in bins 0–4.
- **Own truth versus population truth.** The replicate's own-truth fluctuation, sd(t − t_pop), is 0.20–0.67 × 10⁻³. Against it:
  - the member-mean RMS error is 0.80–8.46 × 10⁻³;
  - coverage is the same against either target (0.896 / 0.896);
  - the estimate tracks its own truth only partly, with slope −0.17 to 0.65.

  So the finite-sample truth is not what drives the miscalibration.
- **Asymmetry is mild in the error distribution itself.** The skewness of the member-mean error is between −0.53 and +0.47, and the within-replicate member skewness is about ±0.15. The one-sidedness of the misses comes from bias.

### 4.4 Reconciling the point-rule outcomes

- **The point rules and the interval apply to different estimators.**
  - §§6.1–6.3 were decided on S4F single fits. H2S1T24 K5 passes every one: R_E0 0.895, LB 0.876.
  - B2 is point-decided and statistically unresolved: 0.0097, with interval 0.0025–0.0169.
  - B1's per-unit bound is not established under within-draw dependence.
  - The six-member mean was never scored against §§6.1–6.3 or the robustness library. Its own development-tilt E0 is 0.943, with sd 0.033 over its 120 replicates.
  - Its expected histogram differs from the single fit's in 6 of 7 bins by 2.7–4.3 SE: E[mean] − E[single] is −1.85, −1.79 and −1.19 × 10⁻³ in bins 3–5, and +6.54 × 10⁻³ in bin 6.
  - The member mean is the less biased of the two in 6 of 7 bins (not bin 1: −0.29 against +0.19 × 10⁻³). A bootstrap bias correction, 2 × single − mean(members), would therefore *increase* the bias, to about −17.6 × 10⁻³ in bin 6.
- **The generator-diagnosis deficits carry over.**
  - The detector step under-fits the generator-reweighted pseudodata: detector-level R is 0.78–0.84 for PET against 0.93–0.94 for the GBDT.
  - The extrapolation to non-reconstructed events degrades with iteration.
  - In the library, the bias of the single fit in units of the development-tilt §9 68 % half-width is:

    | case | null | D1 +0.175 | D1 +0.35 | D5p NuWro′ | D5 GiBUU | D5 NuWro | D1 −0.70 | D2 bump c=1.0 | D2 bump c=0.3 |
    |---|---|---|---|---|---|---|---|---|---|
    | bias / §9 68 % half-width | 0.18 | 0.32 | 0.71 | 2.93 | 3.72 | 4.14 | 4.25 | 5.76 | 5.88 |

  - That half-width is already 1.65–2.15× a calibrated one in bins 1–6. **No variance-only interval for E\* can cover these cases.** A model-dependence term is required, and it cannot be calibrated on the development tilt: the bias pattern changes sign between cases, for example bin 6 is −4.5 × 10⁻³ on the tilt against +34 × 10⁻³ on NuWro.

### 4.5 What the saved design can and cannot tell us

| question | saved design | status |
|---|---|---|
| Between-experiment event-sample variance σ_D², study scale | Identified by V − W/6 over 120 independent replicates (given the banks) | **measured**; small |
| Internal member randomness W | Identified over 600 within-replicate degrees of freedom | **measured** |
| Its nominal-seed part σ_T² | By difference with S4F, or directly from S-N2 on DEV | **measured; the two disagree about 2×; unresolved** |
| Poisson-induced part σ_P², and its interaction with seeds | Only σ_P² + σ_T² = W within experiment; σ_P² by difference | partly identified; interaction **not separable** (no seed × weight crossing) |
| Bias of the member mean, development tilt, by region | SE 0.03–0.7 × 10⁻³ | **measured**; material |
| Bias in generator, response or hadron-content cases | Single fits, 8 draws, no member ensembles | single-fit bias **measured**; member-mean bias and intervals **not measured** |
| Coverage outside the development tilt | D4c members stopped incomplete; nothing else constructed | **not measured** |
| Any of the above at data scale (≈ 16× pseudodata, 2–10 M prior) | — | **not measured**; σ_D² should shrink, while W and bias may not |
| Detector, flux, background or physics-model uncertainty; real data | Signal-only study, inventory response | **out of scope** of the saved design |
| Untouched validation | FB has been inspected; RB stays sealed | **none available** at study scale without opening RB |

## 5. Interval strategies for the fixed estimator E\* (at most two)

**S-I — bootstrap the whole reported estimator (benchmark).**

- **Construction.** For each outer replicate o = 1…O:
  1. draw outer Poisson(1) weights on the pseudodata and the prior;
  2. run the complete six-member procedure on that resample, each member multiplying its own inner Poisson weights by the outer ones and using its own seeds;
  3. record the six-member mean θ\*_o.

  The interval is the percentile (or BCa) interval of θ\*_o, or ± t × sd(θ\*_o).
- **Why it is the reference.** It targets the variance of the estimator actually reported, including the averaging that §9 ignores. The smooth data dependence is common to the six inner members, and the Poisson-induced and seed noise average by 1/6.
- **Assumptions.**
  - The smooth part of the outer response must equal the between-experiment sampling response.
  - It inherits the bias of E\* and does not correct it.
- **Cost.** 6 (1 + O) unfoldings per experiment: 306 at O = 50 and 1,206 at O = 200. Validating it on 120 experiments needs 36,720 unfoldings, ≈ 352 k A100-h at a 2 M-row prior.
- **Use.** Only as a benchmark on two to four experiments, to compare with S-II. It is not a production procedure.

**S-II — components interval with independently calibrated terms (proposal).**

- **Construction.** θ̂ ± t × √(W_r/6 + σ̂²_D,cal + Δ²_bias,cal).
  - W_r is observed within the experiment.
  - σ̂²_D,cal comes from an **independent calibration ensemble** at the target scale, as V − W/6.
  - Δ_bias,cal is a bias allowance calibrated over predeclared physical cases.
  - Calibration uncertainty is carried by using one-sided 84 % upper bounds of both calibrated terms.
- **It must be compared with S-I** on the same benchmark experiments.
- **What saved data show.** Even in-sample, with Δ_bias = 0, it under-covers (§4.3). So Δ_bias is mandatory.
  - The allowance cannot be transferred from the development tilt to generator cases (§4.4).
  - Any asymmetric allowance, or any bias correction, needs a declared model of how bias depends on the true spectrum. It must then be validated on held-out physical cases.
- **On the bias-correction precedent** (arXiv:1505.04768): it motivates an iterated, coverage-checked bias correction. It is not evidence for PET, and §4.4 shows that the naive bootstrap correction would go the wrong way here.

## 6. The suggested 192-unfold crossed pilot, assessed

- **Design read.** The pilot is 24 six-member experiments (144 unfoldings) plus 8 repeated ensembles (48).
  - A repeat is informative about σ_T only if it re-uses the **same events and Poisson weights with new seeds**. Then a member difference measures 2σ_T² directly, over 48 pairs.
  - A repeat with new Poisson weights only re-measures W/6.
- **Precision.** The simulation used the measured study-scale ratios, σ_T²/W = 0.57 and g = 0.21, over 4,000 synthetic repetitions (`results/design_cost.json`, `pilot_precision`).

| design | σ_T²/W, 16–84 % | g, 2.5–97.5 % | bias SE / error sd |
|---|---|---|---|
| saved, 120 × 6 + 60 single | 0.46–0.69 | −0.10 to 0.58 | 0.09 |
| 192 pilot, 24 × 6 + 8 repeats | 0.45–0.70 | −0.42 to 1.12 | 0.20 |

- **Verdict.**
  - At study scale the pilot is **dominated by the existing outputs**: the same σ_T precision, a 2.3× wider interval on g, and twice the bias SE. It would add nothing.
  - At data scale it would cost **1,840 A100-h with the reserve** (932–3,679 at a 2 M-row prior; 7,308 at 10 M). It needs 24 data-size experiments, about 278 M rows, or 6.2× DEV, so each row would be reused about 6 times. And its decision-relevant output, g, would not change the next decision, because §4.3 shows the binding failure is bias.
  - It is therefore **not recommended as the next experiment**. The relevant question at data scale is first whether the bias failure persists. A pilot that estimates variance shares cannot answer that cheaply.

## 7. Proposed experiment E1: data-scale bias-and-variance gate (not launched)

**Question.** At data scale, does the frozen estimator E\*'s full-domain failure persist? The failure is its low-acceptance under-coverage on the development tilt and its generator-case bias. If it persists, the full-domain PET candidate is a no-go for any interval repair, and only a new estimator could proceed.

**This is a signal-only simulation milestone, not a data measurement.**

**Fixed settings.**

- E\* exactly as in §3: H2S1T24, K = 5, B = 6, the §9 member construction, the frozen scorer (`analysis/score_design.py`) and the frozen interval (`analysis/coverage.py`). There is no tuning, and K, epochs, seeds, rules and the scorer are unchanged.
- The data-scale settings are not frozen today. They must be declared at admission:
  - pseudodata of about 9.6 M DEV truth rows, about 4.0 M reco-passing, matching the data's 4.0 M signed signal events;
  - a disjoint 2 M-row DEV prior;
  - a separately justified prior size, if 10 M is chosen.

**Populations and identity.**

- Each experiment draws its pseudodata and prior from DEV, disjoint within the experiment, with identity hashes salted by stage and experiment, as in PROTOCOL §3.
- DEV holds only **3** disjoint data-size experiments. With 8 experiments the pseudodata sampling fraction is 0.213, so pairs of experiments overlap. Inference is therefore **conditional on DEV**, with a finite-population variance factor of 0.787 recorded.
- The two cases share the same event draws, paired as in the study.
- FB and RB are not used.
- Event identities and overlap counts are written per experiment. The run refuses to start if it finds a missing identity or overlap within an experiment.

**Cases.** D1 +0.35 (the development tilt, anchoring to the study scale) and D5 NuWro (the weakest generator case). Both are already-inspected cases. E1 is development evidence, not untouched validation.

**Looks and content.**

| look | content | unfoldings | A100-h with reserve: study-scale u / data 2 M (band) / 10 M |
|---|---|---|---|
| 1 | 4 experiments × 2 cases × 6 members, plus 2 development-tilt experiments with 6 seed partners each (same events and Poisson weights, new seeds) | 60 | — / **575** (291–1,150) / 2,284 |
| 2 (only if look 1 does not stop) | +4 experiments × 2 cases × 6 | 108 cumulative | — / **1,035** (524–2,070) / 4,111 |
| optional bias-estimation extension | to 24 experiments per case | 312 cumulative | — / 2,989 (1,515–5,979) / 11,876 |

**Pricing.** Units × 1.05 for failed members (assumed) × u, then divided by 0.8 for the 20 % reserve. u = 7.3 A100-h is a **forecast**: 3.7–14.6, scaled from the study (gbdt_comparison §7.2), and not measured.

**Primary rule: futility, the no-go.**

- **Statistic.** For each case, the pooled 68 % coverage of the **frozen §9 interval** in the low-acceptance region.
- **Rule.** No-go if its Wilson upper bound, at one-sided 0.05/4 (two cases × two looks) on n_eff = 7E/deff with the measured deff 2.23, is below 0.63 in either case.
- **Logic.** For a fixed centre, coverage is monotone in half-width. The §9 interval is the widest member-based construction in play, so no narrower repair of E\* can cover more. A failure therefore disqualifies every variance repair of E\*, not only §9. This is tested in `test_coverage_is_monotone_in_half_width`.
- **Operating characteristics** (simulated, beta-binomial with the measured deff):

  | true low-acceptance coverage | P(no-go), look 1 (E = 4) | P(no-go), look 2 (E = 8) |
  |---|---|---|
  | 0.26 (the study-scale value) | 0.76 | 0.96 |
  | 0.45 | 0.23 | 0.39 |
  | 0.68 (calibrated) | 0.007 | 0.004 |

**Secondary measurements** (reported only; they decide nothing in E1):

- A100-h per data-scale unfolding and whether two fit per GPU;
- W, σ_T²/W from the seed partners, and g from the experiments, all at data scale;
- member-mean bias by bin and region for both cases, against the bias tolerance of §8;
- truth-weight tails, with P0's stops (a), re-cost, and (b), weights, adopted unchanged.

**What E1 cannot do.** E1 cannot certify bias adequacy.

- With the multiplicity of 7 bins × 4 regions × 2 cases, declaring |bias| < 0.46 sd needs well over 48 experiments per case: P(adequate) is ≤ 0.08 at E = 48, even with zero bias.
- So a pass of the futility rule means only "not excluded".

**Outcomes.**

- **No-go.** E\* is closed for the full-domain endpoint. A fiducial endpoint excluding low acceptance would be a different endpoint and needs Joseph's explicit scope approval. It is **not** a success of E\*.
- **Not excluded.** Admit S2 (§9) with the measured u, W, g and bias pattern.

**Missing results.** A failed or missing member counts as missing for its experiment, and every missing member is listed. An experiment with fewer than 6 members is excluded from the statistic but reported, and the rule is computed both with and without it. If more than one experiment per look is incomplete, the look is INCONCLUSIVE, never PASS.

**Admission requirements.**

1. Joseph authorizes E1 as a named experiment, with its cap.
2. The data-scale input builder, the identity sidecar and the overlap report pass a synthetic test.
3. Runs go through `nd-unfolding/mnv_guarded_run.py`. Before any run, the `OI-136` probe and the `OI-123` per-leg checkout condition are re-measured on the executing checkout.
4. A bit-exact resume is tested, if the 10 M-row prior is chosen.
5. The scorer and coverage code are pinned by digest.

**Terminal.** The cap is the look-2 price, 1,035 A100-h at the forecast. If the first unfolding exceeds 1.5× the forecast u, stop and re-cost, as in P0 stop (a).

## 8. Later stages priced, and full-procedure feasibility

The figures are in `results/design_cost.json`, `costs`. They are A100-h including 5 % failures, and every total is the subtotal divided by 0.8. The 2 M figure uses the forecast u = 7.3; ×4 for a 10 M-row prior.

| stage | unfoldings | 2 M prior: A100-h (band) | GPU node-h | GPU-days at 288 A100-h/day | 10 M prior |
|---|---|---|---|---|---|
| E1 through look 2 | 108 | 1,035 (524–2,070) | 259 | 3.6 | 4,111 |
| S2 calibration: 60 experiments × 6 × 3 cases (development tilt, one generator, one response) | 1,080 | 10,348 (5,245–20,695) | 2,587 | 36 | 41,108 |
| S-I benchmark, one experiment at O = 50 | 306 | 2,932 | 733 | 10 | 11,647 |
| S5 final validation: 4 held-out cases × 539 experiments × 6 | 12,936 | 123,943 (62,820–247,886) | 30,986 | 430 | 492,376 |
| S3 physical systematics, R3 unit counts | 121–308 | 1,159–2,951 | 290–738 | 4–10 | 4,606–11,723 |
| **Full procedure, S-II route** | **14,245–14,432** | **136,485–138,277** (69,177–276,553) | **34,121–34,569** | **474–480** | **542,200–549,318** |

**Validation sizing.** The multiplicity-adjusted assurance rule is in `results/design_cost.json`, `validation_sizing`.

- The rule: per decision, P(Wilson LB ≥ tolerance) ≥ 0.9 for a procedure whose true coverage is exactly nominal, pooled over 7 bins with deff 2.30, one-sided α = 0.05/m.
- At the proposed tolerances (0.63 at 68 %, 0.92 at 95 %), the replicates needed per case are:
  - **314 / 241** for one case, aggregate only (m = 2);
  - **428 / 335** for one case, aggregate plus the three regions (m = 8);
  - **539 / 427** for 4 cases × 4 regions × 2 levels (m = 32).
- At the study's looser C1 form (0.60/0.90), the numbers are 125/99, 171/140 and 215/179.
- **The bias tolerance implied by the proposed bounds**, for a normal interval with exactly calibrated variance, is |bias| ≤ 0.463 sd at 68 % and ≤ 0.508 sd at 95 %. At 1 sd of bias the coverage is 0.475 / 0.830.

**Feasibility.**

- **Events are the binding constraint, and a speed-up cannot change them.**
  - Independent validation at 539 data-size experiments per case needs about 6.3 B simulated rows (539 × 11.6 M, with the cases sharing draws). That is 127× the 49.15 M-row inventory; 500 experiments would be 118×.
  - The never-drawn rows hold 0.35 of one experiment, and DEV holds 3 disjoint ones.
  - **Genuinely independent data-scale validation requires new detector-simulated production of ≈ 6 × 10⁹ rows**, which is not available.
  - The only alternative is a validation conditional on the inspected DEV bank, which holds out cases but not events. That is a narrower claim, and accepting it is Joseph's scope decision.
- **GPU.**
  - At 2 M the full procedure takes about 61 % of the `m3246_g` balance last recorded on 2026-10-05 (56,132 node-h, not re-measured), and about 480 GPU-days at the study's throughput.
  - At 10 M it is **2.4×** that balance.
  - **Speed-up sensitivity.** These are hypothetical; Session 4 had pushed no result. They apply Amdahl's law with the measured training share f = 0.981. At 2/5/10/100× training speed-up the 2 M full procedure falls to 69.6 k / 29.4 k / 16.0 k / 4.0 k A100-h. Even at 100× the event requirement is unchanged.
- **Physical systematics, backgrounds and normalization** remain unvalidated for PET.
  - A data-target PET needs the 564,591 negative-weight background rows and a flux normalization.
  - It also needs a detector/flux/GENIE universe treatment. No per-event universe weights are known to exist for the PET inventory; this needs to be checked through `EVENT_IDENTITY_JOIN_CONTRACT.md`.
  - The gbdt_comparison R3 note says a total PET uncertainty also needs the joint correlation construction and `C_ML`. The Gate-6 receipt's `do_not_construct_C_ML` applies to that family, so a new PET covariance would be a new, separately authorized family.

**Conclusion.** The complete procedure at the declared full-domain endpoint with genuinely independent inputs is **infeasible** with the existing simulation, and **unaffordable** in elapsed GPU time at any prior size. This is the FAIL of disposition (3). It does not show that a conditional-scope or fiducial PET result is impossible; those are different endpoints.

## 9. Staged route to the declared endpoint: admission and terminal no-go per stage

The endpoint is a publication-ready PET measurement with a reproducible central estimator, a matched uncertainty construction and validation that supports the actual claims. Scope remains Joseph's ruling: PET is diagnostic (2026-08-20). Nothing below changes it.

| stage | content | admission requirement | terminal no-go |
|---|---|---|---|
| S0 | saved-output diagnosis (this lane) | done | — |
| S1 point-estimator adequacy | E1 (§7); P0's data-real nominal is optional and diagnostic only | Joseph authorizes E1 with its cap; the guard, identity and resume preconditions of §7 | the E1 futility rule fires: E\* fails the full domain. A new estimator (the generator-diagnosis levers: step-1 budget or optimization, truth-step E_avail/q3 globals, a carried miss rule) is development work needing new DEV training under a new authorization |
| S2 interval construction | S-II calibration, 1,080 units, plus an S-I benchmark on 2–4 experiments | S1 not excluded; a calibration bank disjoint from the validation bank and declared before any draw; Δ_bias model declared | the calibrated 84 % upper bounds inflate the median half-width more than 1.25× over the variance-only width; or S-II and S-I disagree by more than their joint calibration uncertainty; or a Δ_bias that covers the calibration cases makes the interval not useful (median 68 % half-width above a precision target Joseph declares) |
| S3 backgrounds, normalization, physical systematics | background rows; flux normalization; detector/flux/GENIE universes; model dependence | per-event universe weights joinable to the PET inventory (verifiable from the identity contract); a new authorization for any PET covariance family (not Gate 6) | universes cannot be applied to the PET inventory, or the model-dependence band exceeds the statistical band so far that the measurement is not useful against the scalar result |
| S4 production-scale independent inputs | about 6.3 B independent simulated rows for the S5 sizing, or explicit conditional scope | new production authorized and delivered, **or** Joseph accepts conditional-on-DEV validation with held-out cases as the stated claim | neither: then no full-domain validated-coverage claim exists |
| S5 final validation | coverage of intervals reconstructed by the frozen procedure in each experiment, on ≥ 3 held-out physical/response cases plus the development tilt; m-adjusted, sized as in §8 | S2 and S3 frozen; held-out cases never inspected for PET — candidates are the GENIE MEC and MnvTune predictions (used by s5p for the scalar estimator, never for PET) and MAT detector-universe responses, if S3 makes them applicable. If none exists, S5 cannot be untouched validation and must say so | any decision fails its LB rule; **low-acceptance failure fails the full-domain candidate**, and a fiducial restriction is a different endpoint requiring explicit scope approval |
| S6 verification and supported reproduction | independent reimplementation of reductions; guarded provenance; a frozen environment and reproduction path (cf. `reproduction/s5p/`); note, primer and paper builds | all prior stages closed with committed evidence; a publication-scope decision by Joseph | any unreproduced number, or an unresolved publication blocker |

## 10. Verification

```
cd docs/orchestration/state/next-preparation-20261009/pet
python3 reduce_saved.py --out results/saved_reductions.json                  # 862 operand files, digest 12b4e3dc...
python3 design_cost.py --reductions results/saved_reductions.json --out results/design_cost.json
python3 check_independent.py results/saved_reductions.json results/design_cost.json   # exit 0
python3 -m pytest test_pet_q.py -q -p no:cacheprovider                        # 12 passed
```

**Independent numerical check.** `check_independent.py` uses only the standard library and finds its files by its own directory glob, not through the completeness records.

- It has its own Student-t quantile, from Simpson integration and bisection, and its own normal CDF, using `erf`.
- For the aggregate and low-acceptance histograms it recomputes per bin W, V, V1, σ_D², σ_T², the S-N2 seed variance, the member-mean bias, the pooled §9 coverage at both levels, and the single-fit E0. The moments agree to a relative 1e-9 (σ_D² and σ_T² to 1e-7) and the coverage counts agree exactly.
- It re-derives the bias tolerances, the prices (confirming T/0.8, not 1.2T), the event arithmetic and the full-procedure total.
- It confirms each validation N is the smallest that reaches 0.9 assurance.

**Negative controls.** Each was shown to fire.

- The checker exits 1 on a 0.1 % change of one W entry and on a 1 % change of one price.
- The loader refuses a receipt digest that differs from the completeness record, a missing member, and an incomplete completeness row.
- A synthetic positive control reproduces the diagnosed mechanism: internal-randomness-dominated members over-cover at 68 %, while the components variance is nominal within 0.03. A bias of 1 error-sd drives that interval below 0.55, with one-sided misses.
- Coverage is monotone in half-width.
- The futility rule's false no-go rate is below 0.03 at E = 4, and its power is above 0.9 at E = 8 for coverage 0.26.

**Engineering checks against scientific claims.** The tests prove the code paths. The scientific claims rest on the reductions of committed operands, reproduced independently. No delivery hook was bypassed; their results are in §13.

## 11. Independent review

Pending. Exactly one fresh read-only reviewer will receive a fixed commit in a clean, isolated worktree, followed by one focused re-review after one repair batch. The findings and their dispositions will be recorded here.

## 12. Resources and limitations

- **Elapsed.** The worktree was created at 13:00:09 PDT. The report was drafted at 13:20 PDT.
- **Limitations.**
  - Every measured statement is at study scale (600 k pseudodata), signal-only, with the inventory's response, on the development tilt, and conditional on the frozen banks. It is not a data-scale or real-data statement.
  - The components model is additive and Gaussian at the moment level.
  - The P × T interaction is unidentified.
  - σ_T² has two estimates about 2× apart.
  - The bins are correlated, and the per-bin bounds are unadjusted.
  - The in-sample interval variants are diagnostics, not validated constructions.
  - All costs at data scale are forecasts with a 0.5–2× band. The allocation balance was not re-measured.
  - The 192-pilot design was read as described in Goal 6; no other record of it exists in the repository.
  - The 0.63/0.92 bounds are the dispatch's proposed tolerances, not existing rules.

## 13. Delivery and integration

- **Delivery hooks.** `pre-commit: 13 checks passed` on the scripts/results commit `1d40c0b4`, and again on the report commit. `live_doc_indexed.py --unrowed` reports 0 unrowed docs.
- **Manifest, for the integration owner.**
  - `generate_manifest.py --check --at-sha 5ac9706a` is **OK** (exit 0).
  - `--at-sha 1d40c0b4` is **OUT OF DATE** (exit 1). The cause is solely this lane's new files: new `MACHINE state-artifact` rows, plus `consumer` and `inbound_count` changes the generator infers from path strings inside `reduce_saved.py` and `design_cost.py`. No integrity constant is involved.
  - **Requirement:** after merging this branch, the integration owner regenerates `docs/orchestration/MANIFEST.tsv` from source with `python3 docs/orchestration/generate_manifest.py`.
  - This lane does not edit `MANIFEST.tsv`, `MANIFEST-overrides.tsv` or `CATALOG.md`. `REPORT.md` is pre-registered `MACHINE open`. No `CATALOG.md` route change is needed, because the report path is already routed.
- **Status patch for a shared-register owner** (proposal, not applied). For `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md` or a ledger owner, the suggested text is:

  > *Session 6 (2026-10-09, `Q/pet/REPORT.md`): from the saved coverage members and FINAL single fits, the H2S1T24 K5 six-member spread is ≈ 83 % internal randomness; a variance-correct interval under-covers because of bias (aggregate 68 % 0.545; low-acceptance 0.08, in-sample); the complete independently-validated PET procedure is infeasible with the existing simulation. Diagnostic; nothing adopted.*
