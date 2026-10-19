# Statistical audit: s5p calibrated joint tests (methods-paper referee, Q1–Q4)

**Tree:** detached worktree `scratchpad/wt-meas` at `origin/main` = `19b46af9da4c90686a379377c0fdef847fcf36f7`. All `file:line` references are at that sha. This audit was read-only: no repo edit, no ssh, no cluster access. Paths below are relative to the repo root unless they are absolute.
**Scripts and outputs** (in `scratchpad/methods-m2/`): `fwer_seq.py` → `fwer_seq_out.json`; `fwer_extra.py` → `fwer_extra_out.json`; `cont_rest.py` → `cont_rest_out.txt`; and a re-run of the director's script, `seqsize_rerun_out.txt`.

---

## Q1. The generative model

**What one calibration pseudo-experiment does (code).**

1. **Truth.** The null truth is a per-row weight `r_h`, set by the fine cell of the row's true 5D coordinates (`s5p_nullexp.py:299`; the `fine` kind is in `s5p_truths.py:21-28`). The MnvTune null uses ρ = 1 (`prod/spec.json`, `nullsJ/null-mnvtune_v1-J.json`). Each seed draws a fresh MC split, `split_key_for(seed)` (`s5c_pseudo.py:278-281`; `s5p_nullexp.py:318-321`):
   - **half B** is the pseudo-data source. Pseudo-data are Poisson with mean `2·w_reco·r_h·f_s` on the reco-passing rows of B (`s5n_pseudo.py:133-134`).
   - **half A** is the unfolding MC, at CV weights ×2. The prior is Tune v1 unreweighted, because `prior_matches_truth` is False (`s5n_pseudo.py:146-151`, `ra = 1.0` at :147).
   - **Background.** The source C is Poisson at `2·bkg_w·f_b` (:135). The template D stays at CV ×2 (:141-142). The background carries **no** `r_h`, so under every H0(G) the background is Tune v1 plus its bands.
   - **Recorded truth.** `x_true` is **half B's** truth, `2·w_truth·r_h` over B (`s5n_pseudo.py:156,170-186`), written to each product as `xtrue_flat` (`s5p_nullexp.py:352`).
2. **Nuisance draws** (one RNG keyed by the seed, `s5p_nullexp.py:316-317`; `draw` at :127-132). They act on the source rows only (B and C, :333-334); A and D stay at CV.
   - **Flux.** One PPFX universe of 100 multiplies the signal reco weights and the background weights (:206-209). There is no truth preservation, so the pseudo-data rate is σ = G under flux Φ_u while the analysis divides by Φ_CV (`x_true` uses CV flux, `s5n_pseudo.py:184`). This is a flux nuisance on the measurement; σ itself is unchanged.
   - **34 interaction-model bands.** Every band is drawn at one universe (2p2h: one of three) (:79-87, :130).
     - **Background prediction:** the product of the weight ratios multiplies the background source (:213).
     - **Signal response:** the signal reco weights get `k_wr·g_f`, where `g_f = Σw_t / Σw_t·k_wt` is taken over the source rows of the row's fine truth cell (:158-174, :215). Each fine-cell truth integral of B is therefore unchanged, and the knobs move only the within-cell composition, hence efficiency and migration (docstring :21-23).
     - Truth-failing rows and rows outside the grid get the plain factor (`g = 1`, :172).
     - **Clipping:** negative ratios are clipped to 0 per universe before the product (:103-115, :149-154). Only LowQ2_1 and HighQ2_1 carry them. The docstring bounds the effect at ≤ 4.2% of a cell's band shift (:106-109); A7 states ≤ 0.35% in whitened norm (A7 :15). These are two different metrics, and both are recorded.
     - **Combined weights are uncapped:** row factors up to 112 (signal) and 987 (background), Kish ratio 0.63–0.83 (REVIEW-20260927-…-confirmation.md:43). Per-product diagnostics are recorded (`s5p_nullexp.py:330-332`).
   - **Four detector bands** (MinosEfficiency, GEANT n/π/p), each at ±1σ with probability 1/2, on reco weights only. They change the response and background, not the truth (:216-220).
   - **Downstream on the unfolded J cells** (`s5p_joint.py:115-121`):
     - laterals, `+Σ z_b Δ_b`, with Δ taken from the real-data endpoint unfolds (:108);
     - normalization `×(1 + 0.014 z)`;
     - rounding noise `N(0, s_num²)` from 20 data jitters (:111-112);
     - the prediction's MC error, `μ_G + ε` with `ε ~ N(0, Var μ_G)` (:158-159).
3. **Unfolding.** Five iterations, deterministic LightGBM, refinement refit, on half A (`s5p_nullexp.py:341-342`).

**Data analysis.** The data use the **full** MC at weight ×1, the prior is Tune v1 CV, the full background dump is the template, and no nuisance draws are made (`s5n_pseudo.py:189-204`, via `s5p_numerics.py:6`). The observed T gets no additive draws (`s5p_joint.py:222`, `draw=False`).

**Does the truth stay at G on the reported cells?**
- **Interaction-model and detector draws:** yes. Each fine-cell integral of the source is held exactly, and J cells are unions of fine cells (`s5p_truths.py:158-162`).
- **Flux and normalization draws:** they change the event rate, not σ.
- **Not exactly G per experiment.** The J-cell truth is half B's realization. It differs from G by MC half-sampling noise that is redrawn with every seed. The full-MC null integrals equal G's to < 1e-14 (REVIEW-20260927-…-confirmation.md:19), but no record quantifies the per-experiment spread: a `grep` for `xtrue|x_true` under `docs/` finds only product-format notes.
- **Below the fine grid the null is a family, not a point.** The truth's sub-cell distribution, including the variables outside the 5D grid that drive the response, is Tune v1's reweighted by the drawn 34-band universe and renormalized per fine cell.
- **The text disagrees with the code.** A7 calls H0(G) "SIMPLE … with MnvTune v1's shape … below [the fine grid]" (A7 :9), and the paper copies this (paper_body.tex:745-748). The code makes Tune v1's sub-cell shape the CV member of a prior-drawn family.
- **The only quantified sub-fine sensitivity** is deterministic. It is the M1 step (Tune v1 → G at merged×2 versus fine), worth 0.02–0.54 null SD (`stage3/prefreeze/units.json`, `M1_mid_minus_fine`).

**VERDICT Q1.**
- **As is:** the chain description (paper_body.tex:779-792).
- **Text only:**
  - Restate H0(G) as "the true cross section equals G on every fine cell; below that grid, Tune v1's composition varied by the 34 drawn interaction-model universes, fine-cell integrals fixed; background from the Tune v1 simulation with its bands."
  - Say that the per-experiment truth is a half-MC realization of G.
- **Computation (0 CPU node-h, login node on the CFS archive):** the J-cell spread of `xtrue_flat` relative to G and to the null SD, per null.

---

## Q2. The sequential Monte Carlo decision rule

**Reconstructed procedure (code and records).**

- **Batches and looks.**
  - Seeds come in fixed order, in batches of 200, with a maximum of 1999 (`s5p_production.py:30-31`; `prod/spec.json` geometry).
  - A controller look runs before each batch and once more after the last (`prod/queues/cal-NuWro_21_09.q:2-22`).
  - That gives at most 10 non-empty looks, at B ≈ 200j, with B_10 = 1999.
  - B counts **finished** products only (`s5p_seqstop.py:50-51`; partials excluded, `s5p_joint.py:135-138`), so lost seeds give B_j < 200j.
- **Look statistic.** Each look uses the claim (k, B) of each test (`s5p_seqstop.py:64-68`). The claim is the max-p over the variants c ∈ {0, ½, 1}·D and ±2δ_M1 (`s5p_joint.py:228-258`).
- **Thresholds.** {α/j, j = 1..10} ∪ {0.01, 0.05} (`s5p_seqstop.py:66-67`).
- **Stop rule** (`s5p_inference.py:89-111`). A null stops when, for both tests:
  - the **99.5%** Clopper–Pearson interval contains no threshold (:100); and
  - the precision tier is met (:102-109): half-width ≤ 0.05 if p̂ ≥ 0.05; ≤ 0.5 p̂ if 0.01 ≤ p̂ < 0.05; below 0.01 only if the upper end < 0.005.
- **Minimum and maximum B.** MnvTune and GENIE CV need B ≥ 1200 (`s5p_seqstop.py:69-70`; `design.json` `min: 1200`). Every null stops at the maximum (:72).
- **Terminal stops.** A stop is terminal (:47-49). The last line force-stops with "batches exhausted" (`cal-*.q:22`). A meter refusal gives a terminal "budget" stop (A7 :23).
- **Decision.** Holm with determinacy (`s5p_inference.py:127-152`). Tests are taken in increasing p̂ = (k+1)/(B+1), and step i compares with α/(m−i). The step **rejects** if the **95%** CP upper end is < threshold; it stops "not rejected" if the lower end > threshold, and "undetermined" otherwise.
- **Not used in production.** `besag_clifford` (:62-74) appears only in tests (`tests/test_s5p_inference.py:35-37`).
- **Budget extensions decided with p values visible:**
  - **Revision 6:** "k = 0 at every null through batch 1" (RUNBOOK-20260930-…-rev6.md:31-32).
  - **Revision 7** (+25 CPU node-h): decided at 21 looks, all "continue", with k = 0 everywhere except NuWro shape k = 1 at B = 779 (DECISION-20261004-s5p-production-budget-extension.md:14-25, :66-67).
  - Neither revision changed the maximum of 1999, the thresholds or the rule (:9-10).
- **Outcome.** Nine tests have k = 0 at B = 1343–1751, and NuWro shape has k = 1 of 1751 (DELIVERY-20261006-…:35-41). The stops were at B = 1365, 1366, 1343, 1751 and 1351 (MnvTune, GENIE CV, GENIE MEC, NuWro, GiBUU).

**Independent derivation.**

*Model.* For one test, conditional on the data, the null draws in seed order give exceedances X_b iid Bernoulli(p), with p = P(T_null ≥ t_obs | data). Two assumptions:
- **A1 (calibration exactness):** under H0, p is super-uniform. This is the whole content of Q3 and Q4.
- **A2:** which seeds are available at a look does not depend on the X's. Losses came from slow-node timeouts (A7 :61; DELIVERY :45-49), and the available sets are nested, so A2 is plausible.

*Per test.* For any stopping time τ ≤ 1999, including the budget extensions, budget stops, irregular looks and lost seeds:

{reject at c} ⊆ E_c := ∪_{B ≤ 1999} {U(k_B, B) < c}, where U is the 97.5% one-sided CP upper end.

So P(reject) ≤ R(c) := ∫₀¹ P(E_c | p) dp. At a fixed B this is exactly (k\*+1)/(B+1) < c.

*Holm.* Let I₀ be the true nulls, with m₀ = |I₀|. The first true null rejected comes after at most m − m₀ rejections, so its threshold is ≤ α/m₀ (code :139). Hence FWER ≤ Σ_{i∈I₀} P(U_i < α/m₀) ≤ m₀ R(α/m₀). This needs no independence: total and shape share an ensemble and a stopping time.

*Claim variants.* The variants include c = 0, so k_claim ≥ k₀, and U increases in k. The bound for the unshifted test therefore covers the claim rule, including the ensemble-dependent D shift (`s5p_joint.py:200`).

*Numbers* (exact binomial DP plus quadrature; `fwer_seq.py`, `fwer_extra.py`, `cont_rest.py`). Each entry is m₀·R(α/m₀)/α:

| m₀ | threshold c | frozen rule as coded | any stop on the batch grid | any stop after any draw |
|---|---|---|---|---|
| 1 | 0.05 | 0.810 | 0.844 | **0.890** |
| 2 | 0.025 | 0.740 | 0.779 | 0.825 |
| 3 | 0.0167 | 0.690 | 0.729 | 0.775 |
| 5 | 0.01 | 0.600 | 0.656 | 0.691 |
| 10 | 0.005 | 0.405 | 0.484 | 0.514 |

- **Bound:** the maximum is at m₀ = 1, so FWER ≤ **0.81α** under the rule as coded, ≤ **0.844α** for any stopping on the look grid (this covers the extensions), and ≤ **0.89α** for any stopping at all.
- **Simulation check:** a direct Monte Carlo of the whole family (5 nulls × 2 tests sharing stops, frozen rule, global null, independent U p's, 4×10⁵ replicates) gives FWER = 0.0199 ± 0.0002, which is 0.40α.
- **Conditional on p** (the MC-decision error given the data), sup over p ≥ c of P(reject | p):
  - 0.012–0.024 under the frozen rule (the 0.995 look level does its job);
  - 0.038–0.074 for adversarial stopping on the grid;
  - up to 0.16 at p = c for stopping after every draw.

  Only the integrated size is bounded below α. Given the data, the MC-decision error is not bounded by 2.5% under arbitrary stopping.
- **At the observed counts the MC error is negligible.** For a k = 0 decision to be wrong, p ≥ 0.005 would be needed, and P(k = 0 | p = 0.005, B = 1343) = 0.0012.

**Does validity need (k+1)/(B+1) to be valid at a data-dependent B?**
- **No.** Rejections are defined only by the CP gate. p̂ only orders the Holm steps (the bound does not depend on the order) and enters the precision tier (the bound covers any stopping).
- **And p̂ is not valid in general at a data-dependent B.**
  - Under adversarial stopping on the grid, P(p̂_τ ≤ u) = 1.17u, 1.39u, 1.54u and 1.25u at u = 0.05, 0.01, 0.005 and 0.001.
  - With stopping after any draw it is 1.55–1.61u (director's script).
  - Under the frozen rule it is u to 2×10⁻⁵ at 0.05, 0.01 and 0.005, because decisions near those levels run to B = 1999. At 0.001 it is 0.83u.

**The director's calculation** (`triage-calc/seqsize.py`).
- **What it computes:** R(t) with the union over looks (every B, or the batch looks), under u ~ U(0,1) and the CP95 gate.
- **Agreement:** my independent code reproduces it to three decimals (0.890 / 0.844 at 0.05; 0.514 / 0.484 at 0.005; see `seqsize_rerun_out.txt`).
- **What it assumes:**
  1. A1 (exact calibration);
  2. iid draws in a fixed order (A2);
  3. a decision that is purely CP-gated;
  4. the Holm reduction m₀ R(α/m₀), which is implicit and unstated.
- **What it omits:** α/3, α/4 and α/6–α/8 are not evaluated. I evaluated them, and all are ≤ 0.775.
- **Verdict on it:** **"Holm FWER ≤ 0.89α" is correct** under A1 and A2, as an any-stopping bound. It is conservative relative to the rule as coded (0.81α). It says nothing about A1.

**Replacement for paper_body.tex:843-844 and sec_joint.tex:111-112:**
> "A step rejects only when the 95% Clopper–Pearson interval of k/B lies below its Holm threshold. For a true null whose calibrated p value is uniformly distributed, this has probability at most 0.89 times the threshold under any rule for stopping at or before 1999 pseudo-experiments, including the budget extension. By the Holm argument, the familywise error rate of the ten decisions is therefore at most 0.89α ≈ 0.045, whatever B was reached. The values (k+1)/(B+1) are point estimates and carry no separate validity claim at a data-dependent B."

**VERDICT Q2.**
- **As is:** the Holm-with-determinacy description (paper_body.tex:805-818).
- **Text only:** the sentence above, plus one line on its assumption (exact calibration).
- **Computation:** none further. It ran locally (< 5 min CPU) and needs 0 node-h.

---

## Q3. How the nuisances are interpreted

- **Code.** Each experiment draws flux, model, detector, lateral and normalization values from their priors (`s5p_nullexp.py:127-132,316-317`; `s5p_joint.py:115-121`). One ensemble pools them (`s5p_joint.py:141-144`).
- **So the calibrated size is nuisance-averaged** (prior-predictive): P_{θ~π}(reject) ≤ α. It is not uniform over fixed θ.
- **The records say so.** A5 :43: "nuisance-AVERAGED (prior-predictive) calibration … NOT a uniform composite-null guarantee". REVIEW-20260927-…-confirmation.md:50 adds that the J-level composite null "is not calibrated uniformly".
- **The paper does not say so.** A `grep -n -i "averag|prior-predictive|uniform|composite"` over `paper_body.tex` and `sec_joint.tex` returns only unrelated hits. paper_body.tex:893 says "exact for the simulated null", where "simulated null" silently means the prior mixture. At the true fixed θ\*, the size can exceed α.
- **The κ construction** (max p over a finite variant set; `s5p_joint.py:228-258`) protects against two specific deterministic departures of the pseudo process from the data or target process:
  - the half-versus-full MC shift, as `c·D` along the null's bias direction (:187-208);
  - the sub-fine-grid residual, `±2δ_M1`.

  Each variant shifts **all** null draws by a fixed vector. The rule is therefore a sup-p over a finite composite null of exactly those shifted processes. It does not cover shifts in other directions, intermediate magnitudes (unless T is monotone along the direction), changes of null scale or shape, or the value of the prior-drawn nuisances. Its effect is large where it matters: if the true residual were +2δ_M1, the unshifted test's size at 0.05 would be 0.20–0.47 for the GENIE CV, MEC and GiBUU total tests (`stage7/joint/joint-evaluate.json`, `implied_size_of_unshifted_test`).

**VERDICT Q3.** **Text only.** State that the size is nuisance-averaged over the stated priors; κ is a sup over two named process shifts, not over nuisance values. No computation is needed for the methods claim. A uniform-over-θ statement would need a new design.

---

## Q4. Calibration fidelity

**(a) The metric V.**
- **Seeds.** The V pilot used seeds 965000–965199, and 194 products were used (A7 :56-62). Production seeds start at 1200000 and are disjoint (REVIEW-20260927-…-confirmation.md:21).
- **Independence is only conditional.** The pilot shares the MC events and the bank with production. Its process also differed: "GEANT detector bands from the bank, MinosEfficiency absent" (A7 :25).
- **V is fixed.** Its sha256 was frozen before any calibration and is enforced (`s5p_joint.py:273-277`; `s5p_seqstop.py:44`). V depends on no data, so in the repeated experiment (given the MC and the pilot) T is a fixed function. Size is unaffected; V only sets power (`s5p_inference.py:5-7`).
- **New observation.** If the production null covariance equalled V, then E[T_tot] under the Tune v1 null would be ≈ tr(W⁻¹W) = 109. The recorded median is 49.2, with SD 13.6 (`joint-evaluate.json`, MnvTune variant 0.0). So tr(W⁻¹C_prod) ≈ 50: V is roughly twice the production covariance. MinosEfficiency missing from the pilot would push the other way. I found no record explaining this. It affects power only.

**(b) Half versus full simulation.**
- **Mean.** D16 is 16 paired split keys, half minus quarter, measured in the **noise-free, nuisance-free** expectation process (`stage3/f4/D16-*.json`; A6 :27). Its component along the bias direction is 0–0.068 null SD (A7 :75-102; `prefreeze/units.json`), which is the "≈ 0.07 σ_null" of paper_body.tex:889. That is a mean only.
- **Variance and tails of T.** Not found (`grep` over the s5p records, the amendments, `sec_joint.tex` and corrections-20261008 for half×variance/covariance/tail/spread).
- **Indirect variance evidence.**
  - Stage 2: the MC split contributes about 33% of the pseudo-experiment functional variance (RECORD-20260927-s5p-stage2-exit.md:71).
  - A5 :43 calls the extra MC variance of the null "conservative in that respect".

  That conservativeness holds on average over MC realizations. It is not measured for T, and not in the tails.

**(c) Event reuse.**
- **Within an experiment:** A and B are disjoint, and so are C and D (`s5n_pseudo.py:128-151`).
- **Across experiments:** every pseudo-experiment re-splits the same MC (32.8M signal rows, `s5p_nullexp.py:92-93`) and the same background dump. The null draws are iid only **conditional on the MC**, and share its per-event response and truth sampling.
- **Unlike the data:**
  - each null draw resamples the MC split, including the truth noise of the half-B realization;
  - the data carry one fixed full-MC realization, while their events are independent of the MC.
- **Records.** Exchangeability of data and pseudo-data is explicitly **not** claimed (A5 :52). Other than that disclaimer, no record quantifies the effect of reuse on T: a `grep` for reuse / same MC / conditional on the MC / exchangeab over the s5p reviews and records finds only REVIEW-20260927-…-round1.md:131 on iid validation.

**(d) The lateral surrogate.**
- **Construction.** Additive `z·Δ_b`, with Δ from the real-data endpoint unfolds (`s5p_joint.py:108,118`).
- **The only recorded check is endpoint symmetry.** The correlation of up versus minus-down is −0.34 / −0.51 / −0.30 for BeamAngleX/Y and MuonResolution, which is noise-dominated: their shifts of 0.10–0.16% sit below the 0.23% rounding noise. It is 0.96 / 0.94 for the two muon-energy bands, at about 2% (A7 :69; `stage3/V/V-receipt.json`). The added noise is declared conservative (A6 :38).
- **Not found:** any comparison of the surrogate with an event-level lateral shift at the null truth, or of its additivity with the other nuisances. Δ is measured at the data's truth and then applied at G's.

**(e) Any recorded size check?**
- **None** of rejection rates under null pseudo-data processed like the data.
- **History.**
  - A5's T6 had 2 × 300 iid validation ensembles (A5 :52).
  - They were withdrawn because pseudo-versus-pseudo rejection is α by construction (A6 :23; `s5p_joint.py:26-29`). `s5p_inference.size` (:194-200) is called only in tests (`tests/test_s5p_inference.py:53`).
  - The size clause became "a report without a failing outcome" (A7 :31).
- **The "implied size" values** are rejection rates of shifted ensembles against unshifted ones: a sensitivity to the variants, not a size check.
- **A true "processed like data" check is not possible with recorded inputs.** It would need pseudo-data independent of the full unfolding MC, that is, an independent simulation sample, which paper_body.tex:479-481 lists as a new input.
- **Margins** (min over claim variants of (T_obs − median)/SD, `joint-evaluate.json`): 2.8 (NuWro shape, k = 1), 4.5 (GENIE CV shape), 4.9 (MEC shape), and 5.7–207 for the other seven. The decisions' exposure to fidelity is therefore concentrated in three shape tests.
- **Cheapest valid check (it can fail).**
  - **Design:** `s5p_nullexp.py --mc-fraction quarter` with nuisances on (allowed: only `--expectation` requires `--no-nuisance`, :285-286), at existing calibration seeds. Same pseudo-data and same draws (:316-321), so the T pairs are seed-matched.
  - **What it measures:** the MC-size dependence of the whole null distribution (location, scale, the 0.05/0.01 rejection rate of quarter-processed draws against the half ensemble). The half→full effect follows with c = ½ or 1.
  - **What it does not cover:** detector-model or real-data differences, which are irreducible conditions.
- **Per-experiment cost.**

  | basis | CPU node-h per experiment |
  |---|---|
  | production: 207.899 node-h / 8,600 submitted (7,400 calibration + 1,200 power; DELIVERY :102; table caption paper_body.tex:946-947) | 0.024 |
  | measured batches before the slowdown: 4.691 node-h / 200 (REPORT-20260930-…:30) | 0.0235 |
  | after the slowdown: about 6.1 node-h / 200 (DECISION-20261004 :74) | 0.031 |

**VERDICT Q4.**
- **As is:** "the metric sets power, the calibration sets size" (paper_body.tex:774-775).
- **Text only:**
  - (a) the pilot is conditionally independent and was run under a different detector-band set;
  - (b) only the mean half/full shift is measured;
  - (c) the null is conditional on the MC sample;
  - (d) the surrogate is validated only for endpoint linearity;
  - (e) no size check of the data process exists, and the validity statement is conditional (paper_body.tex:893-896 already says this; keep it and make it prominent).
- **Computations:**
  - 0 node-h: from the archive, compare V with the production covariance and measure the `xtrue` spread.
  - Paired quarter-MC check at the three nulls whose shape tests have margins under 5 SD (NuWro, GENIE CV, MEC), 200 seeds each: 600 × 0.024–0.031 ≈ **15–19 CPU node-h** (an upper estimate, since a quarter-MC unfold is cheaper).
  - All five nulls at 300 each, for an A5-style UCB ≤ 0.08 statement: 1,500 × ≈ 0.025 ≈ **37–46 node-h**.
  - Full regeneration (tier C): ≈ 208 node-h (DELIVERY :159-161).
