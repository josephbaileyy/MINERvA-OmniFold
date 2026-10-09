# Session 6 — PET saved-output diagnosis and interval feasibility

| field | content |
|---|---|
| `Lane` | Session 6, `pet` |
| `Decision` | Can the uncertainty of the declared PET point estimator be diagnosed from existing outputs, and what smallest new experiment would distinguish viable repairs from an unaffordable or inadequate procedure? |
| `Branch` / `Base` / `Head` | `prep/next-pet-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269`, the merged common baseline that supersedes the dispatch commit / the commit that adds this revision. The reviewed commits are named in §11. |
| `Owned files` | Only `docs/orchestration/state/next-preparation-20261009/pet/`: `REPORT.md`, `reduce_saved.py`, `check_independent.py`, `design_cost.py`, `test_pet_q.py`, `results/saved_reductions.json`, `results/design_cost.json` and `results/operands.tsv`. No other path was written. |
| `Pinned inputs` | Read at `5ac9706a`. The operands are 956 committed score files plus 2 completeness records, each listed with its sha256 in `results/operands.tsv`; the digest of that list is `bb809717…1324e7`. The governing records are: `nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md`; `PROTOCOL-20260925.md` (§§2, 3, 4, 6.4, 8, 9, 11; Amendments 2c, 5, 5b, 6); `freeze/COMPLETENESS-s5c_a5_H2S1T24.tsv` (sha256 `6d2a25a7…`); `freeze/COMPLETENESS-look1.tsv`; `nd-unfolding/pet/generator_diagnosis/REPORT-20261006.md`; `nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md`; the Gate-6 receipt `docs/orchestration/state/gate6-member-trajectories-result-56847059.json` (sha256 `8f40541f…b6a5`); and `closeout/REPORT.md` §11. |
| `Resources` | See §12. Local CPU: < 0.05 core-hours for the author, plus about 1 core-minute for the reviewer, all single-threaded, with peak RSS ≤ 100 MB. New scratch/data: 0 bytes from the author (nothing was copied) and < 1 MB from the reviewer. Tracked bytes added: ≈ 0.40 MB. Cluster/GPU: **0**. Training: **0**. |
| `Review` | One fresh read-only reviewer: cycle 1 at `a1de6d14`, with 8 MATERIAL and 7 MINOR findings, all repaired in one batch (§11); the focused re-review is recorded in §11. |
| `Model / effort` | Author: Claude Opus 5.5 (`claude-opus-5-5`), as the session context states. Reviewer: a fresh Claude subagent of the same model family; this is not cross-provider independence. Effort: not observable. |
| `Disposition` | **(1) Saved-output diagnosis.** **PASS** for the components identified at study scale on the development tilt, aggregate and by region (§4.2–4.4): internal member variance, between-experiment variance of the estimate and of its error, bias, coverage and asymmetry. **INCONCLUSIVE** for: the P×T interaction; σ_T² in the Poisson-weighted regime (two instruments 2× apart); member-mean bias and coverage outside the development tilt; and every data-scale term (§4.5). **(2) Interval question and discriminating experiment: PASS, conditional on a prior scope decision.** The 192-unfold pilot is not the smallest experiment for the binding question. E1 is designed, calibrated and priced (§§6–7). Its result changes a later spend only if Joseph first accepts a conditional-on-DEV validation scope or funds new simulation, because (3) holds otherwise. **(3) Complete procedure: FAIL** at the declared full-domain endpoint with independent inputs. Independent events would need ≈ 100–130× the inventory under per-decision sizing, or ≈ 225× under joint sizing (PROTOCOL §2: no further same-model simulation exists). The GPU cost is 63–67 % of the last recorded allocation at a 2 M-row prior under per-decision sizing, and 1.06–1.09× under joint sizing (§8). The publication-ready objective is **not** achieved. |
| `Next action` | **First, Joseph's scope decision:** whether a PET coverage claim conditional on the inspected DEV bank (held-out cases, not held-out events) would be acceptable, or whether new simulation would be funded. If neither, no further PET interval experiment is justified, PET stays diagnostic, and the reopening conditions of §9 apply. **If yes, the next request is E1 look 1** (§7). That is 60 data-scale unfoldings of H2S1T24 K5, ≈ 575 A100-h including the 20 % reserve (forecast band 291–1,150), against P0's 165 A100-h, which cannot test interval coverage. |

## 1. Answer in brief

1. **The six-member spread mostly measures PET's own randomness — in the aggregate.**
   - Model-free observation: one Poisson member's variance within an experiment (W) exceeds a single nominal fit's total variance across independent experiments (V1). V1/W is 0.47–0.71 in the aggregate E_avail bins.
   - Under the additive components model (§4.2), between-experiment event-sample variance is **≈ 17 %** of the six-member mean's variance in the aggregate (median over bins 1–5). By region it is **≈ 30 %** in low acceptance, **≈ 43 %** in moderate and **≈ 15 %** in good.
   - So the §9 interval, which charges the full member variance W(1 + 1/B), is over-wide in aggregate, because most of W averages away in the member mean.
2. **Fixing the width does not fix the procedure; bias then dominates.**
   - Take an interval sized to the variance the model predicts for the member mean's error, W_r/6 plus the error's event-sample term, both fitted in-sample. It covers **0.554 at 68 % and 0.896 at 95 %** in aggregate, and **0.082 / 0.312** in the low-acceptance region.
   - On the development tilt itself, |bias|/sd of the six-member mean is 2.24 in bin 0 and 0.57–0.85 in bins 4–6 (aggregate). In the low-acceptance region it is 1.0–4.2 in every bin.
   - The proposed lower bounds tolerate at most **0.46 sd** (68 %) and **0.51 sd** (95 %) of bias.
3. **The interval's estimator is not the one the point rules certified.**
   - §§6.1–6.3 were decided on single unbootstrapped fits: E0 is 0.895, which reproduces exactly.
   - §9 reports the mean of six Poisson-bootstrap members. That is a different estimator: E0 0.943 on its own draws.
   - Its expected histogram differs from the single fit's by **2.7–4.3 SE** in 6 of 7 aggregate bins, and the sign of the bias advantage reverses by region.
   - The bootstrap bias correction 2 × single − mean(members) increases |bias| relative to the single fit in 25 of 28 region bins.
4. **The 192-unfold pilot does not answer the binding question.**
   - Its seed-repeat arm would identify the Poisson-regime σ_T² and the P×T term, which the saved design cannot.
   - But neither term is needed for interval validity: the member mean's error variance requires only W and the error's sampling term, and both are identified.
   - It also cannot measure the failure that binds, which is bias in low acceptance and in generator cases.
   - At data scale it costs ≈ 1,840 A100-h (§6).
5. **E1 replaces the question.** It is a data-scale futility gate on low-acceptance coverage for the development tilt and D5 NuWro. It is **not** a component experiment (§7).
   - A fired no-go excludes every interval centred on the six-member mean that is no wider than §9, which covers all variance-only repairs.
   - It does not exclude a wider bias-allowance interval, another centre, or a new estimator.
   - The critical count is calibrated at the 0.63 boundary. Per-case power at the study-scale behaviour is 0.66 at E = 4 and 0.94 at E = 8.
6. **The complete procedure is infeasible as declared** (§8).
   - Multiplicity-adjusted validation at the 0.63/0.92 tolerances needs 428–539 replicates per case per decision, or 710–955 for a joint 0.9.
   - The never-drawn rows hold **0.35** of one data-size experiment, and DEV holds **3** disjoint ones.

## 2. Inputs, ownership and conditions

- **Baseline.** `origin/main` was fetched at 13:00 PDT and equals `5ac9706a` (0 commits after the pin). The worktree `MINERvA-OmniFold-next-pet-20261009` was created from the pin. No other `prep/next-*` lane branch had been pushed by the last check.
- **Writes.** I wrote only `Q/pet/`. I did not touch `CATALOG.md`, `MANIFEST-overrides.tsv`, `MANIFEST.tsv`, the shared registers, publication sources or other lanes' files.
- **Operands.** Every operand is a committed per-run score JSON that was already unblinded, scored and inspected. No final-bank or reserve row was read, and no sealed data was opened. Nothing was refitted. The D4c coverage members that were stopped before completion stay unscored and unused.
- **Gate 6.** The Gate-6 family is untouched. The receipt's exact `prohibitions_applied` keys are `do_not_select_passing_subset`, `do_not_construct_C_ML`, `do_not_move_central`, `do_not_start_leg_2` and `do_not_retry_unchanged`. Nothing here selects a subset, constructs `C_ML`, moves a central value, starts leg 2 or retries.
- **Terminal campaigns.** `NO_ELIGIBLE_DESIGN` (VL167) and VL168 stand. This lane does not resume the final-design study, its §11 repair, Gate 6 or P0.
- **Setup** (campaign review §1). One owner and one fresh read-only reviewer, with one review and one focused re-review. The decision is Goal 6's. The terminal outcomes are the dispositions in the header.

## 3. The declared estimator and interval, reconstructed from code

Sources: `PROTOCOL-20260925.md` §9 with Amendment 2c; `runner/design_inputs.py:926-971` (`bootstrap_counts`, `member_seed`, `bootstrap_config`, `apply_bootstrap`); `analysis/score_design.py:241-266, 360-378`; `analysis/coverage.py`; `freeze/make_coverage_stage.sh`; the configs in `configs/S5/`, `S4F/` and `S3P/`.

**Fixed estimator E\*.** H2S1T24 at K = 5, using iteration file `iter04.npz`.

- **Step 1** is a PET hybrid: K = 3, local attention, 2 heads, 2 transformers, projection 32. It trains for 8 epochs per iteration with Adam at 4e-4 and batch 512.
- **Step 2** uses the same network and trains for 24 epochs.
- **Training details:** warm start across iterations; a 20 % row validation split, fixed across iterations; `restore: last`; efficiency-corrected miss rule; feature arm `reco_summaries_pdg_onehot`.
- **Sample:** 600,130 prior and 600,111 pseudodata rows of signal-only simulation, with the inventory's response.
- **Config identity:** the S5, S4F and S3P configs differ only in the four estimator seeds, the name and the note.

**Member b of replicate r** (b = 1–6):

- **Poisson weights.** Each pseudodata and prior event gets a Poisson(1) weight, obtained by inverting a uniform hash of `(STUDY_SALT/bootstrap, seed_r, b, side, event identity)`.
  - The pseudodata and prior streams use different salts.
  - `seed_r` is the replicate's `--bootstrap-seed` from the released manifest. Its six members share it, and it is distinct across the 120 replicates (checked).
- **Estimator seeds.** All four estimator seeds are replaced by `sha256(MEMBER_SEED_SALT/field/seed/b) mod (2^31−1) + 1`.
  - Each member therefore has its own training seeds and its own validation split.
  - The base seeds are distinct across replicates, so no seed is shared within or across replicates.
- **Events.** All six members use the same prior and pseudodata rows (the loaders refuse otherwise).
- **Unfolded histogram.** It is the prior's `w_truth × Poisson count × push` over truth-passing rows. It is unit-normalized per histogram: the aggregate seven E_avail bins, and each historical acceptance region separately.
- **Score target.** The target is the replicate's own unweighted pseudodata truth, without the pseudodata Poisson weight. It is identical across members (checked to 1e-12). The FB population truth is reported beside it.

**Reported estimate and interval.**

- The estimate is the per-bin member mean.
- The interval is mean ± t₅ × sd × √(1 + 1/6), with sd the member sd (ddof 1), t₅ = 1.1037 (68 %) and 2.5706 (95 %), and √(7/6) = 1.0801.
- The interval is per-bin marginal. The inference is conditional on the frozen DEV/FB banks.
- **What it covers.** It represents pseudodata statistics, prior-MC statistics and training randomness. It does **not** represent detector response, flux, backgrounds or physics models.
- **Why the √(1 + 1/B) factor misleads.** The factor treats the member sd as the sampling sd of one fit and adds the averaging variance. §4.2 shows most of the member variance averages away.
- **Why dividing by √6 is not justified either.** The event-sample term is common to all six members, bias does not average, and the members share events. §4.3 shows that the correctly averaged variance still under-covers.

## 4. Saved-output diagnosis

### 4.1 Operands and controls

| object | content | binding |
|---|---|---|
| S5 coverage | 120 replicates × 6 members, development tilt D1 +0.35, k = 5 (720 files) | each `receipt_sha256` equals `COMPLETENESS-s5c_a5_H2S1T24.tsv`; one row set and one bootstrap seed per replicate |
| S4F FINAL | 60 single unbootstrapped fits of the same estimator, one seed per replicate (60 files) | each receipt equals `COMPLETENESS-look1.tsv` (`check_s4f_receipts`, negative-tested); seeds distinct; the reviewer found no rows shared with S5 |
| S-N2 | 2 DEV draws × 4 seeds at fixed events and nominal weights (8 files) | row digests equal within each draw |
| S4S library | all 21 cases × FB draws 0–7, single fits (168 files) | committed score files |

**Reproductions.**

- **Pooled §9 coverage** (68 % / 95 %): aggregate **0.896 / 0.990**; low-acceptance **0.257 / 0.789**; moderate **0.701 / 0.964**; good **0.929 / 0.998**. These are exactly the decision record's values.
- **S4F E0** recomputes to **0.895**, with max |ΔR| = 0.0 against `recovery_raw`.
- **Generator-diagnosis T1b.** The D5 single-fit biases for S4S FB0–7 reproduce H2S1T24's rows in T1b. Examples: NuWro bin 6 +34.3 and GiBUU bin 4 +11.4 × 10⁻³.
- **T1b's development-tilt row** equals the S4F FB0–7 mean. That differs from the library's own D1 +0.35 draws, which use another seed set: −14.7 against −6.9 × 10⁻³ in bin 6.

### 4.2 Variance components (× 10⁻⁶ unless a ratio)

**Model.** member_rb = μ + D_r + P_rb + T_rb and single_r = μ₁ + D_r + T_r, where:

- **D** is the replicate's event-sample effect;
- **P** is the Poisson-reweighting effect;
- **T** is training randomness at nominal weights.

**Estimators.**

- W = E[within-replicate member variance] = σ_P² + σ_T².
- V = Var(member mean) = σ_D² + W/6.
- V1 = Var(single fit) = σ_D² + σ_T².

**Assumptions.** The model assumes the same σ_T² in Poisson-weighted members and in nominal single fits, the same σ_D² for both, and no P × T term. Bounds are replicate-cluster bootstrap percentiles, with S5 and S4F resampled independently over 2,000 draws.

**Aggregate E_avail:**

| bin | 0 | 1 | 2 | 3 | 4 | 5 | 6 (3–100 GeV) |
|---|---|---|---|---|---|---|---|
| W | 3.62 | 2.65 | 8.60 | 17.16 | 16.44 | 20.33 | 267.0 |
| V | 0.51 | 0.51 | 1.72 | 3.46 | 3.31 | 4.71 | 52.0 |
| V1 | 1.92 | 1.58 | 6.12 | 10.77 | 8.51 | 9.45 | 145.3 |
| σ_D² = V − W/6 | −0.10 | 0.07 | 0.29 | 0.60 | 0.57 | 1.32 | 7.5 |
| g = σ_D² / (W/6) | −0.16 | 0.16 | 0.20 | 0.21 | 0.21 | 0.39 | 0.17 |
| g, 95 % bounds | ≤ 0.04 | −0.21, 0.61 | −0.18, 0.65 | −0.16, 0.64 | −0.12, 0.59 | 0.01, 0.81 | −0.18, 0.58 |
| V1/W | 0.53 | 0.60 | 0.71 | 0.63 | 0.52 | 0.47 | 0.54 |
| V1/W, 97.5 % bound | 0.80 | 0.91 | 1.01 | 0.87 | 0.73 | 0.62 | 0.78 |
| σ_T²/W, S4F-derived | 0.56 | 0.57 | 0.68 | 0.59 | 0.48 | 0.40 | 0.52 |
| σ_T²/W, S-N2 on DEV (6 dof) | 0.33 | 0.37 | 0.33 | 0.24 | 0.25 | 0.13 | 0.22 |

**g by region, bins 0–6:**

| region | g | event-sample share g/(1+g), median bins 1–5 |
|---|---|---|
| low-acceptance | 0.25, 1.20, 1.06, 0.37, 0.16, 0.42, 0.29 | 0.30 |
| moderate | 0.35, 1.12, 0.57, 0.42, 0.85, 0.75, 0.30 | 0.43 |
| good | −0.04, 0.18, 0.09, 0.08, 0.21, 0.34, −0.01 | 0.15 |

**What this establishes** (study scale, conditional on the banks):

- **W > V1, model-free.**
  - It holds at the 97.5 % bound in 6 of 7 aggregate bins and 25 of 28 region bins. These are per-bin, unadjusted and correlated; the reviewer's resample gives 7/7 and 27/28, with the borderline bins near 1.0.
  - So one Poisson member varies more within one experiment than a single fit's total variation across independent experiments. The member spread is therefore not a bootstrap estimate of a single fit's sampling variance.
  - Within the components model this is σ_P² > σ_D². One further caveat applies: V is conditional on the bank (the pseudodata finite-population factor is 0.773), whereas the Poisson bootstrap targets unconditional sampling.
- **Internal randomness dominates the member mean's variance in aggregate and in the good region, but not uniformly.**
  - The event-sample share is ≈ 0.17 in aggregate.
  - In low acceptance and moderate it is 0.30–0.43, and g's 2.5 % bound is above 0 in several bins.
- **σ_T²/W is 0.13–0.68, depending on the instrument.**
  - The two instruments are S4F-derived (by difference, 59 dof) and S-N2 (direct, 6 dof).
  - With the S-N2 value, the model implies a single-fit σ_D² about 10× the member σ_D² (bin 3: ≈ 0.39 W against 0.035 W).
  - So the 2× gap is a model-consistency question, not a confirmed error. It is not significant at 6 dof.
- **Mechanism of C1/C4.**
  - The §9 variance is W(1 + 1/6), while the member mean's error variance is ≈ W/6 + σ_De² + bias².
  - Ignoring bias, the width ratio is √(7/(1 + g)) ≈ 2.4 in aggregate.
  - The measured member sd / RMS error is 1.66–2.17 in bins 1–6, lower than 2.4 because bias is nonzero. The C4 ratio is 1.65–2.15× a calibrated width.

### 4.3 Bias, asymmetry, finite-sample truth and regions (six-member mean against its own truth)

| region | \|bias\|/sd per bin (0…6) | §9 68 % / 95 % | 68 % misses, estimate above / below | error-variance interval, in-sample, 68 % / 95 % |
|---|---|---|---|---|
| aggregate | 2.24, 0.39, 0.19, 0.31, 0.85, 0.57, 0.62 | 0.896 / 0.990 | 0.087 / 0.017 | 0.554 / 0.896 |
| low-acceptance | 4.17, 3.02, 3.23, 4.04, 3.39, 1.04, 2.97 | 0.257 / 0.789 | 0.640 / 0.102 | 0.082 / 0.312 |
| moderate | 3.23, 1.06, 1.16, 1.30, 0.50, 1.06, 0.67 | 0.701 / 0.964 | 0.256 / 0.043 | 0.429 / 0.813 |
| good | 0.47, 0.72, 0.81, 0.90, 0.83, 0.36, 0.71 | 0.929 / 0.998 | 0.025 / 0.046 | 0.564 / 0.935 |

The error-variance interval is mean ± t₅ √(W_r/6 + σ̂_De²), with σ̂_De² = Var(estimate − own truth) − W/6 fitted on these same replicates and no bias term. It is a diagnostic, not a validated interval.

- **The over-width was masking bias.** At the variance-correct width the interval under-covers in every region, and the misses stay one-sided.
- **Low-acceptance under-coverage is bias, not width.**
  - The bias share of the MSE is 0.899–0.946 in 6 of 7 bins.
  - The mean pulls are +1.75 to +2.35 in bins 0–4.
- **The finite-sample truth does not drive the miscalibration.**
  - sd(t − t_pop) is 0.20–0.67 × 10⁻³, against an aggregate RMS error of 0.80–8.46 × 10⁻³.
  - Coverage is the same against the population target (aggregate 0.896; low-acceptance 0.250).
  - The tracking slope is −0.17 to 0.65.
- **Asymmetry.**
  - The error skewness is −0.53 to +0.47 in aggregate, −0.95 to +0.78 in low acceptance, −0.20 to +1.00 in moderate and −0.28 to +0.40 in good.
  - The misses are one-sided mainly because of bias.

### 4.4 Reconciling the point-rule outcomes

- **The point rules and the interval apply to different estimators.**
  - §§6.1–6.3 were decided on S4F single fits. H2S1T24 K5 passes every one (R_E0 0.895, LB 0.876).
  - B2 is point-decided and statistically unresolved: 0.0097, with interval 0.0025–0.0169.
  - B1's per-unit bound is not established under within-draw dependence.
  - The six-member mean was never scored against those rules or the library. Its development-tilt E0 is 0.943 (sd 0.033, 120 replicates).
- **The two estimators' expected histograms differ.**
  - E[mean] − E[single] is −0.11, −0.48, −1.14, −1.85, −1.79, −1.19 and +6.54 × 10⁻³ in aggregate bins 0–6, with z = −0.5 to −4.3 in bins 0–5 and +3.9 in bin 6.
  - **The member mean is less biased in 6 of 7 aggregate bins, 6/7 low-acceptance and 5/7 moderate, but in only 1 of 7 good-region bins** (z of the difference −3.1 to −5.6 there).
  - The bootstrap bias correction 2 × single − mean(members) **increases** |bias| relative to the single fit in 7/7 aggregate, 6/7 low-acceptance, 5/7 moderate and 7/7 good bins. In aggregate bin 6 the bias goes to −17.6 × 10⁻³.
- **The generator-diagnosis deficits are measured on single fits.**
  - The detector step under-fits the generator-reweighted pseudodata: detector-level R is 0.78–0.84 for PET against 0.93–0.94 for the GBDT.
  - The extrapolation to non-reconstructed events degrades with iteration.
- **Library bias.** Below is the largest single-fit bias over the seven aggregate E_avail bins (not each case's natural histogram), in units of the development-tilt §9 68 % half-width of the member mean. All 21 cases, over FB0–7:

  | ≤ 1 | > 1 |
  |---|---|
  | null 0.18, D1 +0.175 0.32, D4b 0.44, R2 0.68, D1 +0.35 0.71, R1 ×1.05 0.79, D4a 0.95 | D4d down 1.14, D1×D4c 1.24, D4c up 1.36, D4c down 1.74, D4d up 1.81, R1 ×0.95 2.85, D5p NuWro′ 2.93, D3 +0.35 3.17, D5 GiBUU 3.72, D5 NuWro 4.14, D1 −0.70 4.25, D3 −0.35 4.97, D2 bump c=1.0 5.76, D2 bump c=0.3 5.88 |

  - In 14 of 21 cases, the single-fit bias exceeds a half-width that is itself 1.65–2.15× too wide in bins 1–6.
  - **The member-mean bias on these cases is not measured.** If it resembles the single fit's, as it does on the tilt within a factor of about 2–4 (the single fit is the more biased there), no variance-only interval for E\* can cover them.
  - A model-dependence term would be needed, and it could not be calibrated on the tilt alone. The bias pattern changes sign: bin 6 is −4.5 × 10⁻³ on the tilt for the member mean, against +34 × 10⁻³ on NuWro for the single fit.

### 4.5 What the saved design can and cannot tell us

| question | saved design | status |
|---|---|---|
| Between-experiment variance of the estimate (σ_D²) and of its error (σ_De²), study scale | V − W/6 and Var(e) − W/6 over 120 independent replicates (given the banks) | **measured**; small in aggregate and good, 30–43 % of the member-mean variance in low and moderate |
| Internal member randomness W | 600 within-replicate degrees of freedom | **measured** |
| Its nominal-seed part σ_T² | By difference with S4F; directly from S-N2 on DEV | **two values about 2× apart; INCONCLUSIVE** |
| σ_P² and the P × T interaction | Only W within an experiment; σ_P² by difference under the model | **INCONCLUSIVE**: no seed × weight crossing |
| Member-mean bias, development tilt, by region | SE 0.03–0.7 × 10⁻³ | **measured**; material |
| Bias in other cases | Single fits only, 8 draws | single-fit bias **measured**; member-mean bias and intervals **INCONCLUSIVE** |
| Coverage outside the development tilt | D4c stopped incomplete | **not measured** |
| Anything at data scale | — | **not measured** |
| Detector, flux, background or model uncertainty; real data | Signal-only, inventory response | **out of scope** |
| Untouched validation | FB inspected; RB sealed | **none** at study scale without opening RB |

## 5. Interval strategies for the fixed estimator E\* (at most two)

### S-I — bootstrap the whole reported estimator (benchmark)

**Construction.** For each outer replicate o = 1…O:

1. Draw outer Poisson(1) weights on the pseudodata and prior.
2. Run the full six-member procedure on them, with each member multiplying its inner Poisson weights by the outer weights and using its own seeds.
3. Record the member mean θ\*_o.

The interval is the percentile or BCa interval, or ± t × sd(θ\*_o).

- **What it targets.** It targets the variance of the reported estimator, including the averaging that §9 ignores.
- **Assumptions.**
  - The smooth part of the outer response must equal between-experiment sampling.
  - Given the W > V1 finding, the Poisson-induced part must be non-smooth enough to average by 1/6.
  - It inherits E\*'s bias.
  - Its width relative to §9 is unknown.
- **Cost.** 6 (1 + O) unfoldings per experiment: 306 at O = 50 and 1,206 at O = 200. Validating it on 120 experiments takes 36,720 unfoldings, ≈ 352 k A100-h at 2 M.
- **Role.** Benchmark on 2–4 experiments only. It is priced in §8.

### S-II — components interval with independently calibrated terms (proposal)

**Construction.** θ̂ ± t × √(W_r/6 + σ̂²_De,cal + Δ²_bias,cal), where:

- W_r is observed within the experiment.
- σ̂²_De,cal = Var(θ̂ − t) − W/6 is taken from an **independent calibration ensemble** at the target scale. It is defined on the error, not on the estimate; the two differ by up to 1.7× per bin here.
- Δ_bias,cal is a bias allowance over predeclared physical cases.
- Calibration uncertainty is carried through one-sided 84 % upper bounds on both calibrated terms.

**Requirements and evidence.**

- It must be compared with S-I.
- In-sample with Δ_bias = 0, it under-covers in every region (§4.3), so Δ_bias is mandatory.
- Δ_bias cannot be transferred from the tilt to the generator cases (§4.4).
- An asymmetric allowance or a bias correction needs a declared model of how bias depends on the true spectrum, validated on held-out physical cases.
- The bias-correction precedent (arXiv:1505.04768) motivates an iterated, coverage-checked correction. It is not evidence for PET, and §4.4 shows that the naive bootstrap correction goes the wrong way here.

## 6. The suggested 192-unfold crossed pilot, assessed

- **Design read.** The pilot is 24 six-member experiments (144 unfoldings) plus 8 repeated ensembles (48).
  - A repeat informs σ_T only if it uses **the same events and Poisson weights with new seeds**. Then the member differences give 2σ_T² over 48 pairs, in the Poisson-weighted regime. That crossing is exactly what §4.5 lists as missing, and it would resolve the P × T term and the 2× σ_T² gap.
  - A repeat with new Poisson weights only re-measures W/6.
- **Precision** (Gaussian components model with σ_T²/W = 0.57 and g = 0.21, no P × T term, 4,000 repetitions; `pilot_precision`). The simulation assumes away the very interaction the repeats would test, so the comparison is fair only for the terms that model contains.

  | design | σ_T²/W, 16–84 % | g, 2.5–97.5 % | bias SE / error sd |
  |---|---|---|---|
  | saved: 120 × 6 + 60 single | 0.46–0.69 | −0.10 to 0.58 | 0.09 |
  | 192 pilot: 24 × 6 + 8 repeats | 0.45–0.70 | −0.42 to 1.12 | 0.20 |

- **Verdict.**
  - **What the pilot adds is real but not decision-relevant.** It adds the Poisson-regime σ_T² and the P × T term. Neither is needed to size the member mean's error: that needs W and σ_De², both identified. Neither changes the §9 diagnosis.
  - The split of W matters for efficiency, for instance in choosing B or a training change, not for interval validity.
  - The pilot cannot address bias in low acceptance or in the generator cases. With 24 experiments of one case it could estimate a bias, but at a 0.2 sd standard error only.
  - At data scale it costs **1,840 A100-h** (932–3,679 at 2 M; 7,308 at 10 M) and needs 24 data-size experiments, 278 M rows, 6.2× DEV.
  - **Not recommended as the next experiment.**
- **Cheap optional alternative for the model question only.** A study-scale partner-only crossing of 8 DEV experiments × 6 members, refit with the same events and Poisson weights and new seeds, would take **48 unfoldings ≈ 111 A100-h** with the reserve at the measured u = 1.768. It would resolve P × T and the σ_T gap at study scale. It is optional and does not replace E1.

## 7. Proposed experiment E1: data-scale futility gate on low-acceptance coverage (not launched)

**Question.** At data scale, does the low-acceptance under-coverage of every same-centre interval no wider than §9 persist for E\*, on the development tilt and on D5 NuWro?

- This is a **replacement question**, not a variance-component experiment. E1's look-1 g is uninformative (2.5–97.5 %: −0.91 to 3.80).
- It is a **signal-only simulation milestone**, not a data measurement.
- **It matters for the endpoint only if Joseph has first accepted conditional-on-DEV validation scope or funded new simulation**, because §8 otherwise blocks S5.

**Fixed settings.**

- E\* is exactly as in §3: B = 6, the §9 member construction, the frozen scorer `analysis/score_design.py` and the frozen interval `analysis/coverage.py`. Nothing is tuned.
- The data-scale settings are declared at admission: about 9.6 M DEV truth rows of pseudodata (≈ 4.0 M reco-passing), and a disjoint 2 M-row DEV prior, or a separately justified 10 M.

**Populations and identity.**

- Draws come from DEV, disjoint within an experiment, with identity hashes salted by stage and experiment.
- DEV holds only **3** disjoint data-size experiments. With 8 experiments the pseudodata sampling fraction is 0.213, so the experiments overlap. Inference is **conditional on DEV**, with the finite-population factor 0.787 recorded. The simulated operating characteristics ignore this overlap.
- Both cases share the same draws. The Bonferroni split over cases is valid under any correlation.
- FB and RB are not used.
- Identities and overlap counts are written per experiment. Missing identities or within-experiment overlap refuse the run.

**Cases.** D1 +0.35 and D5 NuWro. Both were already inspected, so E1 is development evidence.

**Looks.**

| look | content | unfoldings | A100-h with reserve, data 2 M (band) / 10 M |
|---|---|---|---|
| 1 | 4 experiments × 2 cases × 6 members, plus 2 development-tilt experiments with 6 seed partners each | 60 | **575** (291–1,150) / 2,284 |
| 2 (only if look 1 does not stop) | +4 experiments × 2 cases × 6 | 108 cumulative | **1,035** (524–2,070) / 4,111 |

Pricing is units × 1.05 (assumed failures) × u, divided by 0.8. u = 7.3 A100-h is a **forecast** (3.7–14.6) from gbdt_comparison §7.2, not a measurement.

**Primary rule (futility).**

- **Statistic.** For each case, the total 68 % hits of the frozen §9 interval in the low-acceptance region (7 bins × E experiments).
- **No-go** if the hits are ≤ k_crit in either case.
- **Critical count.** k_crit is calibrated by beta-binomial simulation (measured deff 2.23) **at the boundary p = 0.63**, to a one-sided size of ≤ 0.0125 per case and look (2 cases × 2 looks, Bonferroni ≤ 0.05).
- **Values:**

  | E per case | k_crit | size at p = 0.63 | P(no-go) at p = 0.26 (study-scale) | p = 0.45 | p = 0.55 | p = 0.68 |
  |---|---|---|---|---|---|---|
  | 2 | 2 | 0.012 | 0.37 | 0.09 | 0.03 | 0.006 |
  | 3 | 5 | 0.012 | 0.54 | 0.13 | 0.04 | 0.006 |
  | **4 (look 1)** | 8 | 0.011 | **0.66** | 0.15 | 0.04 | 0.004 |
  | **8 (look 2)** | 22 | 0.011 | **0.94** | 0.32 | 0.07 | 0.002 |

  - These powers are per case.
  - The Wilson-bound version in the first draft was anti-conservative at the boundary (0.021 at E = 4 against 0.0125) and is superseded.
  - **Why E = 4 per case at look 1, not fewer.** Power is 0.66 at E = 4, against 0.54 at E = 3 and 0.37 at E = 2. The marginal 12 unfoldings per case buy about 0.12–0.29 power.
- **Scope of a fired no-go.**
  - For a fixed centre, coverage is monotone in half-width, so the no-go excludes **every interval centred on the six-member mean that is no wider than §9 in each low-acceptance bin**. That is all variance-only repairs, including S-II with Δ_bias = 0.
  - It does **not** exclude S-II with a bias allowance, S-I if it is wider than §9, a different centre (single fit, model-based correction) or a new estimator.
  - It therefore closes E\* for the full-domain endpoint **for variance repairs**. The bias-allowance route goes to the S-II terminal below.

**Secondary measurements** (reported only):

- u at data scale and whether two runs fit per GPU;
- W, σ_T²/W from the partners, and g;
- member-mean bias by bin and region for both cases;
- the **minimum Δ_bias** (the 84 % upper bound of |bias| per low-acceptance bin) and the resulting 68 % half-width √(W_r/6 + σ̂²_De + Δ²);
- truth-weight tails, with P0's stops (a) re-cost and (b) weights adopted unchanged.

**What E1 cannot do.** E1 cannot certify bias adequacy. With 7 bins × 4 regions × 2 cases, P(declare |bias| < 0.46 sd) is ≤ 0.08 even at E = 48 and zero bias. So a pass means only "not excluded".

**Outcomes.**

- **Futility no-go** → variance repairs of E\* are closed for the full domain. A fiducial endpoint that excludes low acceptance is a different endpoint, needs Joseph's explicit scope approval, and is **not** a success of E\*.
- **S-II bias-allowance terminal.** The bias-allowance route is no-go if the 68 % half-width it needs exceeds a precision target Joseph declares. If no target is declared, it is INCONCLUSIVE.
- **Not excluded** → admit S2 (§9) with the measured u, W, g, bias pattern and Δ.

**Missing results.** A failed member is listed as missing. An experiment with fewer than 6 members is excluded from the statistic but reported, and the rule is computed with and without it. More than one incomplete experiment per look makes the look INCONCLUSIVE, never PASS.

**Admission requirements.**

1. Joseph's scope decision (header).
2. Joseph authorizes E1 with its cap.
3. The data-scale input builder, the identity sidecar and the overlap report pass a synthetic test.
4. Runs go through `nd-unfolding/mnv_guarded_run.py`, with the `OI-136` probe and the `OI-123` checkout condition re-measured on the executing checkout.
5. Bit-exact resume is tested if a 10 M prior is used.
6. The scorer and coverage code are pinned by digest.

**Terminal.** The cap is the look-2 price, 1,035 A100-h at the forecast. If the first unfolding exceeds 1.5× the forecast u, stop and re-cost.

**Against P0** (gbdt_comparison §8; ≤ 165 A100-h; deferred by Joseph on 2026-10-06).

- P0 runs single fits of both finalists, 2 draws per case, plus real-data nominals and a 10 M timing run.
- It measures u and point-estimator R against the GBDT, but it builds no six-member intervals, so it **cannot** evaluate coverage or E1's rule.
- E1 look 1 costs ≈ 3.5× P0 and answers the interval question. P0 answers cost and point accuracy.
- If only cost is wanted, P0's first unfolding and stop (a) suffice. E1's request is justified only by the interval question, and only after the scope decision.

## 8. Later stages priced, and full-procedure feasibility

Figures are in `results/design_cost.json`, `costs`. They include 5 % failures, and every total is subtotal / 0.8. The 2 M figures use the forecast u = 7.3. "Days" is GPU-days at the study's *observed* concurrency of ≈ 288 A100-h/day (about 12 A100s), not a capacity limit.

| stage | unfoldings | 2 M: A100-h (band) | GPU node-h | days at observed concurrency | 10 M |
|---|---|---|---|---|---|
| E1 through look 2 | 108 | 1,035 (524–2,070) | 259 | 3.6 | 4,111 |
| S2 calibration: 60 experiments × 6 × 3 cases | 1,080 | 10,348 (5,245–20,695) | 2,587 | 36 | 41,108 |
| S-I benchmark, 2–4 experiments × 306 | 612–1,224 | 5,864–11,727 | 1,466–2,932 | 20–41 | 23,294–46,588 |
| S5 validation, per-decision sizing: 4 cases × 539 × 6 | 12,936 | 123,943 (62,820–247,886) | 30,986 | 430 | 492,376 |
| S5 validation, joint sizing: 4 cases × 955 × 6 | 22,920 | 219,602 | 54,900 | 762 | 872,393 |
| S3 physical systematics (R3 unit counts) | 121–308 | 1,159–2,951 | 290–738 | 4–10 | 4,606–11,723 |
| **Full procedure, per-decision sizing** | **14,857–15,656** | **142,349–150,004** (72,149–300,008) | 35,587–37,501 | 494–521 | 565,495–595,906 |
| **Full procedure, joint sizing** | **24,841–25,640** | **238,008–245,663** (120,634–491,326) | 59,502–61,416 | 826–853 | 945,511–975,922 |

**Validation sizing** (`validation_sizing`).

- **Per-decision rule.** P(Wilson LB ≥ tolerance) ≥ 0.9 for a procedure with exactly nominal coverage, pooled over 7 bins with deff 2.30, one-sided α = 0.05/m.
- **Joint rule.** All m decisions pass with probability ≥ 0.9, assuming independent decisions (per-decision 0.9^(1/m)).
- **Replicates per case** at the proposed tolerances (0.63 at 68 % / 0.92 at 95 %):

  | family | per-decision | P(all pass) at that N | joint |
  |---|---|---|---|
  | m = 2 (one case, aggregate) | 314 / 241 | 0.81 | 384 / 288 |
  | m = 8 (one case, four regions) | 428 / 335 | 0.43 | 662 / 494 |
  | m = 32 (four cases × four regions × two levels) | 539 / 427 | 0.035 | 955 / 710 |

- At the study's C1 form (0.60/0.90) the per-decision counts are 125/99, 171/140 and 215/179, and the joint counts 153/118, 263/201 and 379/288.
- **Bias tolerance implied by the proposed bounds**, for a normal interval with exactly calibrated variance: |bias| ≤ 0.463 sd at 68 % and ≤ 0.508 sd at 95 %. At 1 sd of bias the coverage is 0.475 / 0.830.

**Feasibility.**

- **Events bind, and no speed-up changes them.**
  - Independent validation needs 428–539 (per-decision) to 955 (joint) data-size experiments per case, at 11.6 M rows each with the cases sharing draws. That is 5.0–6.3 B rows (**101–127×** the 49.15 M-row inventory) to 11.1 B rows (**225×**).
  - The never-drawn rows hold 0.35 of one experiment, and DEV holds 3 disjoint ones.
  - PROTOCOL §2 records that no further same-model simulation exists. Genuinely independent data-scale validation therefore requires **new detector-simulated production of ≈ 5–11 × 10⁹ rows**, which is not available.
  - The alternative is validation conditional on the inspected DEV bank, with held-out cases but not held-out events. That is a narrower claim, and accepting it is Joseph's decision.
- **GPU.**
  - At 2 M, the full procedure takes **63–67 %** of the `m3246_g` balance recorded on 2026-10-05 (56,132 node-h, not re-measured) under per-decision sizing, and **1.06–1.09×** under joint sizing.
  - At 10 M it takes 2.5–2.7× and 4.2–4.4× respectively.
  - Elapsed time is ≈ 494–853 days at the study's observed concurrency. That figure scales inversely with the concurrency obtained, so it is not a feasibility verdict on its own.
  - **Hypothetical speed-ups** (no Session-4 result was pushed). With Amdahl's law at training share f = 0.981, the 2 M per-decision procedure falls to 72.5 k / 30.7 k / 16.7 k / 4.1 k A100-h at 2/5/10/100× (`speedup_sensitivity`). The event requirement is unchanged.
- **Physical systematics, backgrounds and normalization** remain unvalidated for PET.
  - These need the 564,591 negative-weight background rows, a flux normalization, and a universe treatment. No per-event universe weights are known for the PET inventory; check this via `EVENT_IDENTITY_JOIN_CONTRACT.md`.
  - A total PET uncertainty also needs the joint correlation construction and `C_ML` (gbdt_comparison R3). The Gate-6 receipt's `do_not_construct_C_ML` applies to that family, so a new PET covariance would be a new, separately authorized family.

**Conclusion.** The complete procedure at the declared full-domain endpoint with genuinely independent inputs is **infeasible with the existing simulation**: the events bind. Under joint sizing it also exceeds the recorded allocation at either prior size. This is the FAIL of disposition (3). It does not show that a conditional-scope or fiducial PET result is impossible; those are different endpoints.

## 9. Staged route to the declared endpoint: admission and terminal no-go per stage

The endpoint is a publication-ready PET measurement: a reproducible central estimator, a matched uncertainty construction, and validation supporting the actual claims. PET remains diagnostic by Joseph's 2026-08-20 ruling. Nothing below changes that.

| stage | content | admission requirement | terminal no-go |
|---|---|---|---|
| S0 | saved-output diagnosis (this lane) | done | — |
| Scope | conditional-on-DEV validation, or new simulation | Joseph's decision | neither: no further PET interval experiment toward this endpoint |
| S1 point-estimator / interval adequacy | E1 (§7). P0 optional, for cost and point accuracy | scope decision; Joseph authorizes E1 with its cap; the §7 preconditions | futility fires: variance repairs of E\* fail the full domain. The bias-allowance route fails if its needed half-width exceeds Joseph's precision target, and is INCONCLUSIVE without one. A new estimator (generator-diagnosis levers: step-1 budget or optimization, truth-step E_avail/q3 globals, a carried miss rule) is development work needing new DEV training and a new authorization |
| S2 interval construction | S-II calibration (1,080 units) and an S-I benchmark on 2–4 experiments | S1 not excluded; a calibration bank disjoint from the validation bank, declared before any draw; the Δ_bias model declared | calibrated 84 % bounds inflate the median half-width > 1.25× over the variance-only width; or S-II and S-I disagree beyond their joint calibration uncertainty; or a Δ_bias covering the calibration cases exceeds Joseph's precision target |
| S3 backgrounds, normalization, physical systematics | background rows; flux; detector/flux/GENIE universes; model dependence | per-event universe weights joinable to the PET inventory; a new authorization for any PET covariance family (not Gate 6) | universes cannot be applied, or the model-dependence band makes the measurement not useful against the scalar result |
| S4 production-scale independent inputs | ≈ 5–11 B independent simulated rows, or explicit conditional scope | new production delivered, **or** Joseph accepts the conditional-on-DEV claim | neither: no full-domain validated-coverage claim |
| S5 final validation | coverage of intervals reconstructed per experiment by the frozen procedure, on ≥ 3 held-out physical/response cases plus the development tilt; m-adjusted, sized per §8 (the joint figure if every decision must pass) | S2 and S3 frozen; held-out cases never inspected for PET. Candidates are GENIE MEC and MnvTune (used by s5p for the scalar estimator, never for PET) and MAT detector-universe responses, if S3 makes them applicable. If none exists, S5 is not untouched validation and must say so | any decision fails its LB rule. **A low-acceptance failure fails the full-domain candidate**; a fiducial restriction is a different endpoint requiring explicit scope approval |
| S6 verification and supported reproduction | independent reimplementation; guarded provenance; a frozen environment and reproduction path (cf. `reproduction/s5p/`); note, primer and paper builds | prior stages closed with committed evidence; Joseph's publication-scope decision | any unreproduced number or unresolved publication blocker |

## 10. Verification

```
cd docs/orchestration/state/next-preparation-20261009/pet
python3 reduce_saved.py --out results/saved_reductions.json      # 958 operand files, digest bb809717...
python3 design_cost.py --reductions results/saved_reductions.json --out results/design_cost.json
python3 check_independent.py results/saved_reductions.json results/design_cost.json   # exit 0
python3 -m pytest test_pet_q.py -q -p no:cacheprovider            # 14 passed
```

**Independent check.** `check_independent.py` uses the standard library only, finds files by its own glob, and has its own t quantile (Simpson integration plus bisection) and normal CDF (`erf`).

- For the aggregate and low-acceptance histograms, it recomputes the following per bin and agrees with the reduction:
  - W, V, V1, σ_D², σ_T², the S-N2 variance and the member-mean bias, to a relative 1e-9 (σ_D² and σ_T² to 1e-7);
  - the pooled §9 coverage, exactly;
  - the single-fit E0.
- It re-derives:
  - the bias tolerances;
  - the prices (T/0.8, not 1.2T);
  - the events arithmetic;
  - the per-decision and joint full-procedure totals.
- It confirms that every per-decision N and joint N is the minimum.

**Separately, the reviewer reimplemented** every consequential reduction from the raw JSON files. All values matched (§11).

**Negative controls** (each shown to fire):

- the checker exits 1 on a 0.1 % change in one W entry and on a 1 % change in one price;
- the loader refuses a mismatched S5 receipt digest, a missing member and an incomplete completeness row;
- `check_s4f_receipts` refuses a mismatched S4F digest;
- the futility critical count holds size ≤ 0.0125 at the 0.63 boundary on fresh simulation, and the superseded Wilson rule is shown to exceed it.

**Synthetic positive control.** Members dominated by internal randomness over-cover, while the components variance is nominal within 0.03. A bias of 1 error-sd drives that interval below 0.55, with one-sided misses.

**Monotonicity test.** `test_coverage_function_is_monotone_in_half_width` checks only the coverage function. The futility rule's scope (§7) is a statement of scope; the test does not prove it.

**Engineering checks against scientific claims.** The tests prove code paths. The scientific claims rest on reductions of committed operands that were reproduced independently twice.

## 11. Independent review

**Reviewer.** One fresh read-only Claude subagent (same model family as the author), given a fixed commit in the clean detached worktree `MINERvA-OmniFold-next-pet-review-20261009`.

- **Cycle 1 at `a1de6d14`:** 8 MATERIAL and 7 MINOR findings.
- **Numbers.** It independently rebuilt every saved-output number listed in §4. All matched. Rerunning the author's scripts reproduced the JSON files byte-identically.
- **Hygiene.** Its review worktree's `git status --porcelain` was empty afterwards. It used about 1 core-minute.

| # | finding (severity) | disposition in this repair batch |
|---|---|---|
| 1 | futility no-go wider than its monotonicity logic (MATERIAL) | §7 scope restated: same-centre intervals no wider than §9 only. S-II with Δ_bias, other centres and S-I not excluded. S-II terminal added (§7, §9) |
| 2 | validation sizing per-decision, not joint (MATERIAL) | joint sizing added (`replicates_per_case_joint`; 955/710 at m = 32). Bracket carried into §8, §9 and the header; checker verifies minimality |
| 3 | "unaffordable in elapsed time at any prior size" not shown (MATERIAL) | removed. Days labelled as observed concurrency; FAIL rests on events, plus allocation under joint sizing |
| 4 | "pilot adds nothing" contradicted §4.5 (MATERIAL) | §6 rewritten: the pilot adds the Poisson-regime σ_T² and P × T, which are not decision-relevant for validity. E1 relabelled a replacement question. Study-scale partner-only option priced (48 units, ≈ 111 A100-h) |
| 5 | "≈ 83 % internal" aggregate-only (MATERIAL) | regional g added (§4.2); §1 and the status patch qualified (low acceptance 30 %, moderate 43 % sampling) |
| 6 | Next action missing its conditionality and the P0 comparison (MATERIAL) | scope decision placed first. E1 vs P0 compared (§7). Power vs E table added (E = 2/3/4/8) |
| 7 | full procedure omitted the S-I benchmark (MATERIAL) | added (612–1,224 units); totals updated |
| 8 | disposition (1) PASS outran §4.5 (MATERIAL) | split into PASS for the identified terms and INCONCLUSIVE for the listed ones |
| 9 | "≥ 118×" not a bound of the lane's own sizing (MINOR) | now "101–127× per-decision, 225× joint" |
| 10 | Wilson futility rule anti-conservative; test too loose (MINOR) | replaced by a critical count simulation-calibrated at p = 0.63. The test asserts the boundary size, and a second test documents the Wilson excess. Overlap between experiments stated as ignored |
| 11 | library claim transferred single-fit bias to E\*; 9 of 21 cases; max not stated (MINOR) | all 21 cases; "maximum over bins, aggregate histogram, single fit" stated; the member-mean claim made conditional |
| 12 | V1/W ⇔ σ_P² > σ_D² is assumption-laden (MINOR) | the model-free W > V1 statement made the headline; assumptions and the bank-conditionality caveat listed |
| 13 | regional bias reversal and asymmetry hidden (MINOR) | good-region reversal stated; bootstrap-correction counts given per region; regional skewness given |
| 14 | S-II sampling term defined on the estimate, not the error (MINOR) | redefined as Var(θ̂ − t) − W/6. The diagnostic interval was recomputed with it (aggregate 0.554/0.896; low acceptance 0.082/0.312) |
| 15 | monotone test tautological; S4F check untested; file count (MINOR) | test renamed and its limit stated; `check_s4f_receipts` factored out and negative-tested; counts corrected (956 + 2) |

**Focused re-review.** Recorded below once completed.

## 12. Resources and limitations

**Time.**

- **Wall clock.** The worktree was created at 13:00:09 PDT. The review completed at about 13:45, and the repair batch began at 16:22 after an idle wait for usage-limit reset.
- **Active effort.** About 1 h 50 min to the end of the repair batch, including the review. The idle wait is excluded and stated, not hidden.

**Limitations.**

- **Scope of the measurements.** Every measured statement is at study scale (600 k pseudodata), signal-only, with the inventory's response, on the development tilt, and conditional on the banks.
- **Model.** The components model is additive and moment-level, and P × T is unidentified.
- **σ_T².** Its two estimates are about 2× apart.
- **Bounds.** The bins are correlated, and the per-bin bounds are unadjusted.
- **Diagnostics.** The in-sample interval variants are diagnostics.
- **Simulations.**
  - The futility and pilot simulations assume a beta-binomial or Gaussian model.
  - They ignore overlap between experiments.
- **Costs.** Data-scale costs are forecasts within a 0.5–2× band, and the allocation balance was not re-measured.
- **Dispatch inputs.**
  - The 192-pilot design was read from Goal 6 alone.
  - The 0.63/0.92 bounds are proposed tolerances, not existing rules.

## 13. Delivery and integration

- **Delivery hooks.** `pre-commit: 13 checks passed` on every commit of this branch. `live_doc_indexed.py --unrowed` finds 0 unrowed docs.
- **Manifest, for the integration owner.**
  - `generate_manifest.py --check --at-sha 5ac9706a` is **OK** (exit 0).
  - At this branch's commits it is **OUT OF DATE** (exit 1), solely because of this lane's new files. Those add new `MACHINE state-artifact` rows, plus `consumer`/`inbound_count` changes that the generator infers from path strings in the lane's scripts. No integrity constant is involved.
  - **Requirement:** after merge, the integration owner regenerates `docs/orchestration/MANIFEST.tsv` from source with `python3 docs/orchestration/generate_manifest.py`.
  - This lane does not edit `MANIFEST.tsv`, `MANIFEST-overrides.tsv` or `CATALOG.md`. `REPORT.md` is pre-registered as `MACHINE open` and already routed.
- **Proposed status patch for a shared-register owner** (proposal, not applied), for example for `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`:

  > *Session 6 (2026-10-09, `Q/pet/REPORT.md`): from the saved coverage members and FINAL single fits (study scale, development tilt), one H2S1T24 K5 Poisson member varies more within an experiment than a single fit varies across experiments. In aggregate E_avail the six-member mean's variance is ≈ 83 % internal randomness, ≈ 57–70 % in the low-acceptance and moderate regions. A variance-correct interval under-covers because of bias (in-sample 68 %: aggregate 0.554, low acceptance 0.082). The complete independently validated PET procedure is infeasible with the existing simulation. Diagnostic; nothing adopted.*
