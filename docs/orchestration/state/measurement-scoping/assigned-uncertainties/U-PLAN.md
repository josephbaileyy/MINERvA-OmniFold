# U-PLAN: the five assigned-uncertainty options, costed, for Joseph (2026-10-26)

**By** session "2d test", for the director. This is item 6 of
`DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md`, which takes its options from the caveat study
(`state/2d-closeout/stageF/methods/caveat-study/REPORT.md` §6).
- **Scoping only: 0 node-h.** No job was submitted.
- **Repo reads:** origin/main at `a2dae50e`, then `6c89d07d` (C-RESP-SPEC merged, PR #365), plus the branches named
  where they are cited.
- **Cluster reads:** login37, 2026-10-25 23:14 to 2026-10-26 02:21 UTC. They were only:
  - `ls`, `sha256sum`;
  - one meta-only probe of 11 npz (`C-RESP-SPEC.md` §1.2);
  - a synthetic test run in a scratch clone.
- **Comparator texts:** the caveat study's blinded texts. Their sha256 match its committed `INPUTS.sha256`.
  - Two more texts from the study's working directory were added for the experiments' norms: 2004.05434, which the
    study measured and did not use, and 2310.06082, which it could not measure (caveat study §1). Their sha256 are in
    `receipts/texts.sha256`. The texts themselves are not committed, as in the study.
  - Every quote below was checked mechanically as a substring of its text, after whitespace is collapsed
    (`receipts/quotes-check.txt`).

**CITABLE FOR:**
- per option: the comparators' practice, quoted; which result the option would enter; the inputs, with their
  digests; the prescription choices with a recommendation; the cost from measured units; the value and risks;
- the ranking against the queued work.

**NOT CITABLE FOR:**
- any authorization, value, claim or printed wording. Each option needs Joseph's decision, then a declaration and a
  binding;
- the genre as a whole: the comparators were chosen to fit, not sampled (caveat study §8).

**Rules:** no claim changes, no printed wording and no κ change; no GPU; regular QOS; every job under 12 h; nothing on
CFS.

## 0. Answer

**Joseph's question: "if we report them on their own versus adding them into the other uncertainties, what is
typical?" Both.**
- Where a comparator assigns one, it is named in the uncertainty breakdown (P1, P2, P5, P6, 2004.05434). It is also
  in the total covariance that the comparisons use: P4, P5, P6 and 2004.05434 state the sum (§1, T0).
- **Fake-data studies are the exception.** The comparators use them as validation. A fake-data bias becomes an added
  uncertainty only when it is not negligible against the existing uncertainty: T2K's oscillation analysis (N1) has
  an explicit rule for this.
- **A background-subtraction non-closure is not assigned as an uncertainty** by any comparator measurement text
  searched (§1, T1). This corrects the caveat study's §6 row, which called it the "P4, P6 pattern".
- What P4 and P6 assign is a model-dependence term, which is option 2's pattern.

**The five options, by result.** For the 5D result, the director's expected path is that S1's (e) result on R00–R15
supersedes (a). That is expected, not decided: integration is its own step, and its wording is Joseph's.

| option | 5D (e), R00–R15 | (E_avail, W) map and other (a) products | 2D (f) | cost |
|---|---|---|---|---|
| 1 purity non-closure | **discharged by measurement**: F0's nominal max \|b\| is 0.07 % | **a decision only**: the bias is measured (EW29 −4.11 ± 0.10 %), with a rank-1 block on the 42 cells recommended if the map keeps its band | refined closure within 0.44 stat σ: nothing to assign | 0 |
| 2 regularization bias | already carried by C_model,5D (M2, κ = 1), as P4/P5 do. A fake-data term in N1's form is possible at 0 node-h. **Recommended: no new term now** (§3.2) | no (a) fake-data set at generator truths in the records read (§3.3). A (c) proxy costs ≤ 1.5 node-h. Not recommended | C_model,2D is reported beside the covariance already. A 3-truth (f) check costs ≤ 1 node-h. Optional | 0 to 1.5 |
| 3 hadronic response | **C_resp, at 0 node-h, from 11 existing unfolds.** The spec is merged (PR #365); its binding waits for Joseph's choice on Stage G's variant | not covered. It needs (a) re-unfolds on GPU-only tooling | zero by construction (inference from code) | 0; jitter add-on ≤ 1.25; joint tests ≈ 230–320 |
| 4 seed ensemble | **discharged by measurement**: the seed main effect is zero by construction (S1-DIRECTOR-RULINGS §2) | z-cv's seed pair. Each extra member is up to 304 task-hours of declared walls (upper bounds, not measurements), on GPU-only tooling. **Not runnable under the rules** | C08 is 0.048 % median: nothing to gain | — |
| 5 stat-band scaling | not applicable: stat is 0.24 % of a 6.74 % median total | **not recommended**: the miscoverage is residual bias, and the intervals are not too narrow (M2-RATEFAIL) | the quoted block is untested, but scaling is not the remedy | 0 |
<!-- absence-ok: 'the quoted block is untested' restates the paper's limitation item 1 (paper_body.tex:1228-1230: "The coverage of its statistical block and of the total has not been tested.") -->

**Ranking against the queue (§7).**
1. C_resp. It is cheap, it addresses the paper's most-restated caveat (12 / 13), and Stage G is being held for it.
2. The three discharges and the option-5 decision. These are wording only, and belong to the S1 integration step.
3. Option 2's decision on 5D. It is Joseph's.

Everything that costs node-h ranks below the review. MP1-A-full is the only option that would change the joint
tests, and it is not recommended now.

## 1. Typical practice, from the comparators

**Set P** is the caveat study's six PRD papers (P1–P6). **Set N** is its long documents (N1–N3; N2 and N3 are
detector papers and bear on none of the five options). Added for the experiments' norms:
- T2K CC0π on O and C, 2004.05434 (PRD 101, 112004);
- MicroBooNE GKI, 2310.06082.

The rows below are the quotes the handling rests on.

### T0. A named component, and the total

| doc | how | quote |
|---|---|---|
| P5 MINERvA low-recoil (2110.13372) | each source a covariance, summed; Fig. 6 breaks it down | "The covariance matrices for all sources of systematic uncertainty are summed" |
| P2 MINERvA inclusive 2D (2002.12496) | named breakdown; χ² with the covariance | "A breakdown of systematic uncertainties on the singledifferential cross sections is shown in Fig. 4." |
| P4 MicroBooNE QE-like (2301.03700) | per-source covariances summed; the breakdown is in the text and the supplement | "The resulting covariance matrices are summed together to estimate the relevant uncertainty from each source." |
| P6 T2K TKI (2102.03346) | breakdown by source; one covariance from toys | "Contributions from each source of systematic uncertainties are shown one by one" |
| 2004.05434 T2K CC0π | approximate breakdown; one covariance | "showing an approximate breakdown by error source." |

### T1. Background-subtraction non-closure

| doc | how | quote |
|---|---|---|
| P2 | none assigned; claimed small | "The small background contribution allows for an absolutely predicted background subtraction without introducing substantial model dependence." |
| P6 | none assigned; covered by existing parameters | "parameters, the fit can cover the bias in signal efficiency and background subtraction under extreme" |
| 2004.05434 | validated by fit quality; none assigned | "validation of the background subtraction and of the extracted result through an analysis of the goodness of fit" |
| P1, P4, P5, N1 | no non-closure assigned | — |

<!-- absence-ok: the row's claim is scoped to the texts searched; see the Search line below -->
Search: closure; non-closure; background subtraction; subtract; background in blind/{2504.06857,2002.12496,2301.03700,2110.13372,2102.03346,2101.03779,2004.05434,2310.06082}.txt @ a2dae50e

### T2. Model dependence of the unfolding

| doc | how | quote |
|---|---|---|
| P4 | an alternative-generator universe added to the covariance | "In order to account for potential biases due to the nominal MC modeling prediction used in the unfolding procedure" |
| P4 | as one universe | "matrices are constructed using Eq. 8 and a single universe (n = 1)." |
| P5 | the model difference is a named line, in the total | "MnvTune-v3 (Signal model, gray solid line in Fig. 6)." |
| P6 | ad hoc parameters sized from generators | "size of this uncertainty roughly double the largest variation in the efficiency seen from a wide variety of different generator predictions" |
| N1 T2K oscillation (2101.03779) | a fake-data bias becomes an uncertainty above a threshold | "If a simulated data bias is greater than 50% of the systematic uncertainty on a parameter then an additional uncertainty is added to the analysis to account for this." |
| N1 | as the quadrature sum | "The quadrature sum of the observed biases, 4.1 × 10−5 eV2 c−4 , was added as an additional uncertainty on ∆m232" |
| 2310.06082 MicroBooNE GKI | fake data checked against an uncertainty that includes an alternative-generator term | "The combination of these uncertainties covers the differences between the unfolded fake data points (black) and the alternative-generator theory results (orange)." |
| 2004.05434 | a generator difference as an added term | "therefore taken as a conservative additional uncertainty." |
| P2, P5, P6 | fake data used only to choose iterations or to validate | P2: "In these studies, the χ2 reached a minimum at 10 iterations."; P6: "bias is much smaller than the statistical uncertainty and" |

### T3. Hadronic or recoil energy response

| doc | how | quote |
|---|---|---|
| P5 | its own named line, from test beam, in the total | "The uncertainty in the detector energy response is divided into two uncertainties, hadronic energy and muon" |
| P5 | its source | "uncertainty is determined from hadron calorimetry data" |
| P2 | a named category; test-beam scale | "a charged-particle beam, was used to determine the absolute hadron energy scale and its uncertainty [23]." |
| P6, 2004.05434 | "detector" means secondary interactions, PID and efficiency; no calorimetric scale | P6: "The detector response (efficiency and resolution) is not perfectly modelled in the simulation." |

### T4. Training randomness

| doc | how | quote |
|---|---|---|
| P1 OmniFold on T2K simulation (2504.06857) | a named part of the budget, made negligible by ensembling | "The uncertainty budget shown in Fig. 8 also includes the contribution to the uncertainty from neural network training randomness" |
| P1 | how | "The unfolded results we have presented are the result of ensembling 5 trials of neural networks, which reduces the standard error to a level that is negligible relative to the systematic and statistical uncertainties involved with the data." |
| P2–P6, N1 | no estimator randomness | — |

<!-- absence-ok: scoped to the texts searched; N1's three hits are ensembles of fit universes and pseudo-experiments, not estimator training -->
Search: seed; seeds; ensembl; training random; initialisation; initialization in blind/{2002.12496,2205.05084,2301.03700,2110.13372,2102.03346,2101.03779}.txt @ a2dae50e

### T5. Scaling a band after a coverage study

**No comparator scales a statistical band after a coverage study.** The nearest analogues:
- N1's smearing is driven by a bias (T2 above). N1 builds its intervals with coverage by construction, which is not
  a band scale: "with exact coverage using the Feldman" (its interval method);
- 2004.05434 answers its regularisation caveat by reporting both results: "both regularised and unregularised results
  are reported."

<!-- absence-ok: scoped to the texts searched; Search line below -->
Search: coverage; inflat; scale factor; Feldman; smear in blind/{2504.06857,2002.12496,2301.03700,2110.13372,2102.03346,2101.03779,2004.05434,2310.06082}.txt @ a2dae50e

## 2. Option 1: the purity background-subtraction non-closure

**The caveat.** Paper :562-569: "biased by up to 4 % in simulation, about one quoted standard deviation in one
(E_avail, W) cell. This bias is not included in the quoted uncertainties." It is restated 7 times in the paper.
- **The measured configuration is (c),** the deterministic purity variant (Table II, :351).
- **It qualifies (a),** the purity-based 5D central value (:315-317), and the (E_avail, W) map drawn from it (:890).

**Typical practice (T1):** not assigned. The comparators keep the background small or claim it is covered.

**By result:**
- **5D (e), R00–R15: discharged by measurement.**
  - F0's nominal-truth row: max |b| 0.0007, from 40 experiments (FD-F0-REPORT §5.1). The closure floor is
    3.2 × 10⁻⁵ (§3.1, control 6).
  - The negative-weight treatment with refinement removes the purity mechanism (paper :577-581 for 2D; the deformation figure's caption,
    :672-673, gives 0.09 % for (e) at nominal).
  - Nothing to assign. The integration states it as a measured closure.
- **2D (f): nothing to assign.** The refined estimate lies within 0.44 statistical σ in every cell (paper :577-581).
- **(E_avail, W) map and the other (a) products: a decision only.**
  - **Input:** `state/s5c/d1/d1_summary.json`, sha256 `f5c802e3…`, group `split_F2`, 9 pseudo-experiments.
    - On the 42 map cells plus their sum, 30 of 43 functionals have |b| > 2 SE. The largest are EW29 −4.11 ± 0.10 %,
      EW11 −4.06 ± 0.14 % and EW23 −4.02 ± 0.09 %. The total is +0.30 ± 0.02 %.
    - On the J cells, 57 of 109 have |b| > 2 SE, with a maximum of J80 +2.73 ± 0.11 % (computed here from the
      receipt).

**Prescription choices for Joseph:**

| choice | options | recommendation and basis |
|---|---|---|
| form | (i) one fully correlated block b bᵀ, rank 1; (ii) diagonal b²; (iii) correct the central value by −b | **(i).** It is P4's single-universe form. The bias is one coherent, W-graded mechanism measured with z up to 45, and (ii) would discard that correlation. (iii) would change a printed central value from a (c) measurement, which is a transfer step (next row) |
| which b | the measured mean; or only the cells with \|b\| > 2 SE | **the measured mean.** Zeroing cells by a significance cut is a data-dependent choice, and the SE is small |
| transfer (c) → (a) | assume it; or measure it on (a) | **assume it, and state it.** (c) is (a)'s deterministic purity variant. Measuring (a) itself needs (a) pseudo-experiments, whose tooling is GPU (§5) |
| where it enters | the map's C_EW only; or also z-cv's 5D covariance | **C_EW only.** b is measured on projections, not on z-cv's 10,694 cells **(inference)** |

**Cost:** 0 node-h. A login-node builder maps d1's EW order onto the map's 7 × 6 C order, and needs code and review.

**What changes:**
- Paper: in Fig. 3(b)'s band, a named "background subtraction" line, and the sentence at :566 becomes the component's
  definition.
- Note: `sec_validation` closure-map and `sec_5d` map-band paragraphs.

**Value and risks.**
- Low if the map leaves the paper under item 5 of the decision (R-P9), and moderate if it stays with its z-cv band.
- Risk: a component in a covariance that already "does not meet the validation criteria of its specification"
  (:722-724) gains little.

## 3. Option 2: a model-dependence covariance for the residual regularization bias

**The caveat.** Paper :1241-1243: "No quoted uncertainty includes it, and the five-observable covariance omits it."
It is restated 10 times in the paper and 20 in the note.
- **The 74 %** is configuration (d) on the map cells, in the GiBUU-to-GENIE E_avail shape (:590 comment).
- **The 16–31 %** is (e), on three held-out shapes.

**Typical practice (T2):**
- **A generator-difference term in the total is the norm.** P4 adds an alternative-generator universe, P5 a "Signal
  model" line, P6 ad hoc parameters, and 2004.05434 a NuWro FSI difference.
- **Fake-data studies are validation** (P2, P5, P6, GKI).
- **N1 adds an uncertainty from a fake-data bias** above 50 % of the systematic, as the quadrature sum of the
  biases.

### 3.1 2D (f)

- **Already at practice.** C_model,2D = Σ s sᵀ is reported beside the four-block covariance and in a total (paper
  :515-533). That is P5's and P4's form.
- **Available, not needed:** a fake-data check of C_model,2D on (f)'s own bias.
  - PV-2D's closures were run on (a) only (PV-2D REPORT, the opening paragraph). There, C_model without its own vertex
    (the refined arm's shifts) reached (a)'s NuWro bias in 56.7 % of 127 cells (`pv2d/cmodel/REPORT.md:110-121`).
  - **Cost:** 3 (f) closures at about 0.122 node-h each, RE-2's 2D universe unit (S1-PLAN §2). That is 0.37 node-h,
    with a cap of 1.
  - **Value:** low-to-moderate. It is a 2D analogue of F0.

### 3.2 5D (e), R00–R15

**The inputs exist.**
- **The F0 readout:** committed `fd/readout/fd_f0_readout.json`, `6e7d718b…`, with per-cell b for 12 graded truths
  and 6 descriptive ones.
- **The per-experiment table:** `$P/fd-f0-20261025/fd_f0_experiments.npz`, `7384c651…`.
- **The 80 `f4` products:** on HPSS (FD-F0-REPORT §2).

**What F0 found.** The reported uncertainty, which already holds C_model,5D, does not reach the bias at the GiBUU-like
truths or at the q3 tilt. Joseph accepted that as a stated limitation on 2026-10-25 (decision item 1).
- A7 GiBUU: max |b| 0.36, χ²_16 = 246.75.
- Stage 0c GiBUU: p = 0.0031.
- q3: p = 5.6e-07.
- W3: p = 0.0027.

**Prescription choices for Joseph:**

| choice | options | recommendation and basis |
|---|---|---|
| add a term at all | (a) no: keep C_model,5D as the model term and the F0 limitation as stated; (b) yes: C_FD from the fake-data biases | **(a), now.** Three grounds follow below the table |
| if (b): form | N1: Σ_T b_T b_Tᵀ, the quadrature sum, one rank-1 term per truth; an envelope max_T \|b_T\| per cell, fully correlated; or N1's threshold, adding only truths whose bias exceeds 50 % of σ_total | the N1 quadrature form over a **declared** truth set (one truth per generator family, plus the q3 tilt), labelled "fake-data residual bias; not a calibrated bound" |
| if (b): beside or in | beside, with a second total; or folded in | **both**, the §0 answer: a named line and a second total C_total + C_FD |

**The grounds for (a):**
- **C_model,5D is already the term that comparable papers carry,** as P4's alternative universe and P5's "Signal
  model". Its positive control at NuWro passed on the 27 base cells, with thin margins (n 21, corr 0.790, slope
  0.683). The 16-cell readout is not powered (BUILD-REPORT).
- **C_FD built from F0's truths makes F0 uninformative.** A grade of a truth against a matrix containing that truth's
  own bias passes by construction. The independent test, F1, is skipped (decision item 3).
- **Adding it reopens a limitation Joseph accepted on 2026-10-25,** and it is dominated by GiBUU, whose 6–10 GeV/c sample
  lacks E_ν > 20 GeV (the C_model,5D GiBUU label).

**Cost:** 0 node-h for (b): a login-node builder on the committed readout, plus a declaration and a binding.

**What changes under (b):**
- Paper: a named line in the 5D breakdown; item 4 of the limitations (:1241) narrows.
- Note: `sec_5d`.
- **κ is untouched.**

**Value and risks.**
- High on paper: it would put the most-restated note caveat (20) into a quoted uncertainty.
- Real risks: circularity, double counting with C_model, and a large GiBUU-driven inflation, with A7 GiBUU's max |b| at 36 %
  and its |z| > 2 cells R02, R06 and R07 (FD-F0-REPORT §5.1).

### 3.3 The (E_avail, W) map and the other (a) products

**No (a) fake-data set at generator truths exists in the records read.** The 74 % is (d), and the 16–31 % is (e).
<!-- absence-ok: scoped to the records cited for the 74% and 16-31% (paper_body.tex:590 comment, VL151/VL154; OUTCOME-20260925-s5n-stage1-development-fail.md; s5e assess_receipt); no other (a) truth-change pseudo-experiment record was found by the Search line -->
Search: GiBUU; truth change; departure; pseudo-experiment; configuration (a) in docs/analysis-note/sec_5d.tex sec:val-departure and state/s5n, state/s5e, state/s5c @ a2dae50e

**Building one:**
- **On (a) itself:** needs its GPU launchers, so not under these rules (§5).
- **A (c) proxy:**
  - 4 truths × 20 pseudo-experiments on CPU. The unit is at most (e)'s measured pseudo-experiment, 0.0141 CPU node-h
    at 8 lanes of 32 CPUs, about 404 s each (FD-PLAN §5.1, Stage 0 job 60182677). (c) has no refinement, so it is
    cheaper **(inference)**.
  - That is about 1.1 node-h: 1 node, 8 lanes, 10 waves of about 404 s, limit 1:30, **cap 1.5**.
  - It carries the same (c) → (a) transfer as option 1.

**Not recommended.** The map's model dependence is the reason R-P9 lists it as a candidate to move to the note.

## 4. Option 3: a calorimetric hadronic-response band

**The caveat.** It is the paper's most-restated: 12 in the paper, 13 in the note.
- Paper :118-120: "whose detector model has no calorimetric recoil-response uncertainty".
- Paper item 8, :1256-1260.

**Typical practice (T3):** MINERvA's own papers carry it as a named line in the total. In P5 it is "hadronic energy",
from test-beam calorimetry; in P2 it is "Hadrons". It is standard for MINERvA recoil observables.

### 4.1 5D (e), R00–R15: C_resp, from existing products

**The inputs exist.** They are the 11 MP-1 S1 data unfolds:
- configuration R, 5 iterations, seed 42, the 400/31 refinement;
- each with the full 65,856-cell `xsec_flat`;
- proton, meson, EM, other and cross-talk at ±1σ of D1's sizes, plus a k = 0 unfold.

They are hashed and probed in [`C-RESP-SPEC.md`](C-RESP-SPEC.md) §1, merged as PR #365. Its binding is held until Joseph chooses whether Stage G carries the variant.

**The spec, in short:**
- per species, S1's lateral half-span (`s1_assemble.py:341`);
- the four primary species summed, with cross-talk beside them;
- C_total_resp = C_total + C_resp;
- builder `build_cresp.py` at `973142a7`, with 22 tests;
- **0 node-h.**

**Prescription choices for Joseph:**

| choice | options | recommendation and basis |
|---|---|---|
| adopt into the reported total | (a) a Stage G sensitivity variant only; (b) a named component in C_total | **(b), decided from C_resp's own readout (its σ per cell and trace share) before Stage G runs.** That is P5's form. Deciding after Stage G's χ² are seen would make the choice of matrix depend on the comparison. Stage G reports both matrices either way |
| species | four primary; or plus cross-talk | **four.** That is MP-1's frozen primary design, and MAT marks cross-talk "DO NOT USE" (`S0-PREP.md:239`) |
| sizes | D1: proton 3.5, meson 5, EM 3, other 20 % | **D1**, MP-1's documented source (`PLAN.md:505`). P5 derives its hadronic-energy term from test-beam calorimetry too |
| discreteness | single endpoints; or jitter-averaged endpoints | **single,** unless the descriptive curvature ratio on R00–R15 exceeds 0.2, MP-1's G3 tolerance, for a primary species. That rule is declared here, before the readout. Then the add-on of §4.2 is priced |

**What it does not cover** (spec §7):
- the joint tests' nulls;
- neutron and muon deposits;
- species, energy and resolution effects beyond a scale;
- (a)'s products;
- 2D, which is zero by construction (inference).

**What changes if adopted:**
- Paper: a "hadronic response" line in the 5D uncertainty table. Item 8 (:1256) narrows to the joint tests.
- Note: `sec_systematics` and `sec_5d`. `sec_joint`'s response condition (:617-690) is unchanged.

**Value:** the highest of the five, at 0 node-h. **Risk:**
- MP-1 read the em and other curvature on the J cells as estimator discreteness, so each half-span carries
  rounding-scale noise;
- on R00–R15 the curvature ratio shows how much.

### 4.2 Optional add-on: jitter-averaged endpoints

- **Inputs:** em and other already have jitter products (25 unfolds; `$P/measurement-paper/phase1/mp1/jitter/`). The
  add-on is proton, meson and cross-talk ±1σ × 5 jitter seeds: 30 unfolds.
- **Cost:** at MP-1's measured 0.997 node-h per 25 unfolds (5 nodes, 5 lanes), that is about 1.2 node-h. Packed 8 lanes
  on 1 node it is 4 waves × ≈ 720 s, about 0.8 node-h. **Cap 1.25** (1 node, 1:15).
- **When:** only under the rule above.

### 4.3 The joint tests: MP1-A-full

- **Cost:** about 230–320 CPU node-h, already priced (`phase1/mp1/S1-REPORT.md`, "MP1-A-full, priced"). Production
  alone is about 104 h wall at a 2-node cap, so many jobs, each under 12 h.
- **Not recommended now.** It is more than 50× the sum of this plan's caps (4.25 node-h). Its input-jitter finding means it would carry
  estimator structure into each null. The paper already states the rejections as conditional on the response.

### 4.4 Configuration (a)'s products and 2D

- **(a):** it would need species re-unfolds with (a)'s GPU tooling (§5), so not under these rules.
- **2D:** reconstructed p_T and p_∥ only, so a recoil scale moves nothing (spec §7; inference from code).

## 5. Option 4: a seed ensemble

**The caveat.** Paper item 5, :1244-1247: "rests on one seed pair". It is z-cv's, configuration (a)'s covariance:
s_proj = 6.1 % at offsets {0, 1200} (:727; note `sec_5d.tex:678-706`).

**Typical practice (T4):** P1 makes training randomness a named budget line and ensembles until it is "negligible
relative to the systematic and statistical uncertainties". Nobody else has estimator randomness.

**By result:**
- **5D (e): discharged by measurement.**
  - The seed main effect is zero by construction: full-sample binning and deterministic training, so 80 seed products
    are bitwise equal to seed 42's (S1-DIRECTOR-RULINGS §2).
  - C_seed = 0 is in C_e. The estimator's numerical variation is carried by set A (ruling item 3).
  - **This is P1's end state** ("negligible"), reached by construction rather than by ensembling.
- **2D (f): nothing to gain.** C08 is 0.048 % median over five seed settings (note `sec_results.tex:200`, `sec_systematics.tex:171-173`).
  P1's criterion is met.
- **(E_avail, W) map and z-cv: not runnable under the rules.**
  - **Unit:** each extra seed member is 304 task-hours of declared walls on 1-GPU + 32-CPU tasks
    (`COSTMODEL-20260911-z-pilot-and-scan.md:38`). These are declared upper bounds, not measurements. Measured
    `ElapsedRaw` would need a `sacct` read, which was not made here.
  - **GPU:** the launchers are GPU launchers (`:24-31`), and this plan carries no GPU.
  - **The pinned bands:** the 5 pinned lateral bands cannot move with the seed offset (`sec_5d.tex:710-714`).
  - **Recommendation:** none. If the map and its z-cv band stay, the limitation stays as printed. If the 5D result
    moves to (e), item 5 is replaced by the measured zero (S1-DIRECTOR-RULINGS §2, item 5).

**Cost:** 0, by discharge or by not running.

## 6. Option 5: statistical-band scaling

**The caveat:** "statistical intervals miscover under an about 10 % rate reduction" (Table I, :94; §V C, :614-635).
It is restated 4 times in the paper and 12 in the note.
- **The test:** configuration (c), statistical-only intervals, on the 153 integrals (`state/s5c/tier_s/interim_400.json`,
  `aa574c17…`).

**The diagnosis** (`stageF/methods/M2-RATEFAIL-DIAGNOSIS.md:7-15`):
- **The cause is residual bias:** +0.2 % at W 1.4–2.2, +0.4 % at 2.2–3, and +0.7–1.1 % at W ≥ 3. That is 1.3–2.6σ
  against intervals of 0.16–0.43 %.
- **The intervals are not too narrow.** Setting the spread equal to the half-width leaves coverage at 0.06–0.22.

**Typical practice (T5):** no comparator scales a statistical band after a coverage study. N1's added smearing comes
from a bias, which is option 2's form.

**Prescription choices for Joseph:**

| choice | options | recommendation and basis |
|---|---|---|
| scale | (a) no; (b) scale the statistical block by a factor fitted to coverage | **(a).** The diagnosis puts the fault in the mean, not the width. A width factor would fix a coverage number without the cause. The rule in the caveat study's §6 row also applies: "any choice needs its own coverage test" |
| the bias part | leave it as a validation finding; or route it to option 2 | **leave it.** At 0.2–1.1 %, it is far below each result's total: 5D (e) C_total median 6.74 % (S1-REPORT §6), and 2D 6.41 % (`values.tex:140`) |

**By result:**
- **5D (e):** statistical is 0.24 % of a 6.74 % median total (S1-REPORT §6), so scaling has no effect.
- **2D (f):** the quoted statistical block (0.676 %) has never had a coverage test of its own (paper :1228-1230). A
  test would be its own plan; it is not an assigned uncertainty.
- **An optional confirming test:** the diagnosis's own (tilt seeds with no background, and with the background × 0.9)
  is about 0.1–0.2 node-h (`M2-RATEFAIL-DIAGNOSIS.md:15`). It would name the source of the W-graded term in limitation
  item 3. **Cap 0.5.** It is not an assigned uncertainty.

## 7. Ranking against the queued work

**The queue:**
- Stage G: its declaration is on branch `5d-community/fd-g-20261025` at `7fd3688d`, and its binding is held for
  C_resp's variant;
- r18: the register round in progress;
- Joseph's and Ben's review;
- MINERvA review, which is Joseph's act.

| rank | item | node-h, expected / cap | value | when |
|---:|---|---|---|---|
| 1 | **C_resp on R00–R15** (option 3, §4.1) | 0 / 0 | high: the paper's most-restated caveat; MINERvA norm | **now**: bind and build before Stage G's binding (minutes on a login node) |
| 2 | **discharges:** options 1 and 4 for 5D (e), option 1 for 2D, option 5 not scaled | 0 / 0 | high for the text: three caveats become measured statements | in the S1 integration step, not r18 (it is the S1 result's wording) |
| 3 | **option 2, the decision on 5D (e)** (§3.2) | 0 / 0 | Joseph's | before Stage G runs, with C_resp's adoption: either changes the matrix Stage G uses |
| 4 | **option 1 for the (a) map** (§2) | 0 / 0 | low-to-moderate; void if the map moves to the note | after Joseph's R-P9 decision (item 5) |
| 5 | C_resp jitter add-on (§4.2) | ≈ 0.8 / 1.25 | conditional | only if the declared curvature rule fires |
| 6 | 2D (f) fake-data check of C_model,2D (§3.1) | 0.37 / 1 | low-to-moderate | after the review, if wanted |
| 7 | option-5 confirming test (§6) | 0.1–0.2 / 0.5 | names a source; no component | after the review, if wanted |
| 8 | (c) proxy for option 2 on the map (§3.3) | ≈ 1.1 / 1.5 | low; transfer caveat | not recommended |
| 9 | z-cv seed ensemble (§5) | GPU; up to 304 declared task-h per member | low | not runnable under the rules |
| 10 | MP1-A-full (§4.3) | ≈ 230–320 | moderate, for the joint tests only | not recommended now |

**Totals:**
- Ranks 1–4: 0 node-h.
- With every optional CPU item (5–8): **caps 4.25 CPU node-h** (1.25 + 1 + 0.5 + 1.5). Every job is 1 node and
  under 3 h, regular QOS, with no GPU and nothing on CFS.

**Against the queue:**
- Nothing here competes with Stage G or r18 for compute.
- Ranks 1–3 change the 5D result's uncertainty statement. So they should be decided before the review copy, so that
  Joseph and Ben read one version.

## 8. Unchanged

- No claim, printed wording, κ, cell or KNOWN_ISSUES disposition changes here.
- Every option needs Joseph's decision, then a declaration and a binding. C_resp's spec is the only one written, at
  the director's request.
- No GPU and no premium QOS. Nothing is submitted, deposited or tagged.
