# DESIGN: a 5D CC-inclusive measurement whose uncertainty includes model dependence (2026-10-23)

**By** the measurement session, under [`ASSIGNMENT.md`](ASSIGNMENT.md) and
[`DECISION-20261023-joseph-r8-r9-and-5d-scoping.md`](../../../DECISION-20261023-joseph-r8-r9-and-5d-scoping.md) item 3.
No compute. Every number is either read from a committed record, or is arithmetic on such numbers and labelled
**(arithmetic)**. Reasoning beyond the record is labelled **(inference)**.

**CITABLE FOR:**
- what a 5D measurement with a model-dependence term would need, on the record;
- a proposed construction and calibration of that term;
- a staged plan with proposed pass rules and costs, offered for declaration;
- a proposed stop condition;
- the decisions this leaves to Joseph (§11).

**NOT CITABLE FOR:**
- any measured result, coverage or uncertainty;
- any authorization: every stage needs its own DECLARATION and BINDING, and the rules here are proposals for those
  declarations;
- any change to T1–T7, the reporting definition or the endpoint, which are Joseph's;
- any claim.

**Inputs.** Paths are relative to `docs/orchestration/` unless they begin `docs/` or `nd-unfolding/`.
- main `177bf84b`:
  - `state/gpu-timing-20261023/REPORT.md`;
  - the s5p record and its amendments;
  - MP4-A, D-ID, KI 98, gbdt §9–§10;
  - the register-PRD corpus notes.
- The validation lane's scoping memo `state/measurement-scoping/SCOPING.md` (cited "S:"). Reviewed at PR #279's
  `4f3a067d`; byte-identical on main.
- The IBU-1 report `state/2d-closeout/stageF/methods/ibu1/REPORT.md` (cited "I:"). Reviewed at PR #277's `ef11a551`;
  byte-identical on main.

**Name collision.** "T1" and "T2" name both the frozen targets and D-ID's truth grids (`PLAN.md:366-367`). Here T1–T7
are always the targets; the grids are written "grid T1" and "grid T2".

## 0. Answer in brief

**The route.**
- Measure RD1, the 109 J cells, under configuration (e).
- Add a model-dependence component built from the data's prior-variation shifts (s5p study P), scaled by one constant κ.
- Calibrate κ by leaving one departure out at a time.
- Validate it at newly declared truths.
- Build an (e) covariance. Then test the coverage of statistical + model intervals, pooled first and per-functional
  last.
- This reopens a route the record lists as **Closed**: "prior dependence carried as an uncertainty component"
  (`state/measurement-paper/PLAN.md:385`; S:118). It reopens it only through target changes that Joseph would make
  (§6).

**Why the frozen targets cannot be met at the current reconstructed information.**
- The unscaled envelope h already has medians of 12.0% (J), 9.6% (H2) and 13.4% (EW)
  (`RECORD-20260927-s5p-stage2-exit.md:129-131`). T2 caps the model component at 5%; T1 asks for a 10% total.
- h is not a bias bound: |shift| ≥ |bias| holds in only 52–78% of cells
  (`state/s5p/contract-amendment-6-review1-repairs.json:44`).

**What is most favourable on record is RD2 (H2) without the contaminated vertex D1.**
- There h's median is 4.28%, under T2's 5% component cap (`amendment-6:17`).
- But RD2 also fails T2's recovery clause under R: |bias|/|departure| is about 0.33 at GiBUU and W3 and 0.31 at q3,
  against 0.25 (§1). So RD2 passes T2 only if Joseph changes that clause (§11).
- D1 is contaminated by the GENIE flux defect: KNOWN_ISSUES row 83, OPEN
  (`REVIEW-20260927-s5p-round1-stage2-exit-and-joint-design.md:115, :119`).
- Re-deriving D1 is a cheap lever that this design adds (Stage 0c).

**Decisive cheap tests first.**
- **Stage 0, 0 node-h.** Products already on pscratch decide whether a κ calibrated on some generator families covers the
  bias at a family it never saw. They also decide whether the generators stay separable with that term in the covariance.
- **Stage 0c, about 0.64 CPU node-h.** Re-derive D1 and the GiBUU fold. Only this five-fold run is binding.
- **Stage 1, R10.** The validation lane's reconstructed-information test. It must report before any GPU stage, as the
  criterion record requires.

**Expected outcome (inference; no quantitative basis).**
- Keeping T1 at 10%, Stage 0b's model-term bar is 10% − 1.4% = 8.6%, since the half-width is at least u_f + 1.4%
  (`amendment-6:17`). For M1 on J that needs κ* ≤ 0.72 against the full-h median of 12.0%, or a smaller h after the D1
  repair. M2's u_f is at least M1's, so its bound is tighter.
- The record's per-vertex fractions (§2.1) measure something else:
  - each vertex's own shift against its bias;
  - over all cells;
  - with B0 bias.
- So they do not predict the family-held-out coverage of Stage 0a, in either direction.
- The design states no expected J verdict. H2's component is the one figure on record under its cap (4.28% without D1),
  but H2 still needs the recovery-clause change.

**Full programme, if every stage passes** (arithmetic from the GPU timing, §5):
- Stress tests: about 11–14 GPU node-h.
- (e) covariance: about 25–28 GPU node-h, plus inputs not yet priced.
- Pooled coverage pilot: about 321 GPU node-h.
- Pooled 400-per-truth test: 2,570–5,141 GPU node-h.
- Per-functional test: **28,299 GPU node-h**, 66% of the 42,727.4 left on 2026-10-23.
- All GPU-pool use is Joseph's and Ben's decision (S:150).

**Stop condition** (§9). Stop if Stage 0 fails after the D1 repair and R10 fails. A missing R10 verdict holds the plan
rather than releasing it.

## 1. Estimand and reporting definition

**The three definitions** (`state/s5p/contract-amendment-1-use-case-and-targets.json:47-49`):
- **RD1:** the 109 supported J cells (`:47`). This is the only joint-5D definition at the analysis granularity. Joseph
  keeps the joint-5D endpoint as the long-term objective (`DECISION-20261019-joseph-methods-first-and-measurement-compute.md:36-39`).
- **RD2:** H2, 27 supported cells of a 2⁵ partition, also joint in 5D (`:48`).
- **RD3:** EW, 39 supported (E_avail, W) cells, "joint_5d false" (`:49`).
- **Shared rules:** support needs reco signal and truth-selected weight both ≥ 1000 at data POT (`:50`). The unfolding
  domain stays the full fine grid (`:51`).

**The predeclared selection has already been applied.**
- The rule: "RD1 is selected if it meets T1, T2, T3 and T5; otherwise RD2 if it does; otherwise RD3 alone"
  (`amendment-1:54`).
- At development resolution it gave: "RD1 fails T1 and T2, RD2 fails T2 (and T1), so RD3 is the fallback, and RD3 fails
  T1" (`state/s5p/contract-amendment-4-stage2-decisions.json`, `reporting_selection`; `stage2-exit:139`).
- So proposing RD1 again means re-applying that rule under targets Joseph has changed. That is his decision (§11).

**RD2 is where the record is most favourable.**
- Without D1, H2's h median is 4.28% (`amendment-6:17`).
- Amendment 6 says RD1 (≥ 12.6%) and RD3 (≥ 11.3%) fail T1 without D1. It makes no such statement about RD2.
- RD1 and RD2 fail T2 through W3's recovery ratio (`amendment-6:17`). That ratio is B0's M at k = 5, M_H2 0.314
  (`stage2-exit:80-83`).
- Under R, H2's recovered-fraction medians are 0.671 (GiBUU), 0.751 (W1), 0.887 (W2), 0.672 (W3) and 0.688 (q3)
  (`state/s5p/stage1/stage1_inspect.json`, `departures.<truth>.H2.recovered_fraction_median`). So r ≈ 0.33, 0.25,
  0.11, 0.33 and 0.31 **(arithmetic)**.
- T2 applies at each alternative (`amendment-1:39`), so RD2 fails its recovery clause under R as well.
- EW and H2 widths are about 2.5–3.5% at grid T1, but "widen … to ≈ 20–30% at T2: the coarse grid hides within-cell
  freedom" (`state/next-preparation-20261009/d-id/REPORT.md:424-425`).
- But PLAN leaves "whether RD2 alone counts as 'coarser'" to Joseph (`PLAN.md:443-444`). Coarser or selected
  functionals are excluded as an endpoint change (DECISION-20261019 §1a, `:36`).
- This design states both readings and prices both.

**Not proposed, because each is an estimand change for Joseph:**
- identified functionals: 5/109 J at grid T2 (`d-id/REPORT.md:576`);
- an A_c report, which "changes the estimand to A_c·t" (`PLAN.md:389`).

**Reported as now:** the fine-grid central value (65,856 cells, shape [14,16,7,7,6],
`state/2d-closeout/stageF/methods/RE1-REPORT.md:23-30`).

## 2. The model-dependence uncertainty

### 2.1 What exists

**h, from s5p study P.**
- **Construction.** The real data were unfolded under R, which is configuration (e), with the MC truth prior reweighted
  to each of five vertices at amplitude 1 (`state/s5p/contract-amendment-3-stage2-supplement.json:9`):
  - D1: GiBUU/GENIE E_avail;
  - D2 = W1: NuWro/GENIE E_avail;
  - D3 = W2: GENIE MEC/CV (E_avail, W);
  - D4 = W3: NuWro/GENIE (pT, p∥, E_avail);
  - D5: the anchored NuWro/GENIE q3 | (E_avail, W).
- **Definition.** h_f = max_k |shift_k,f|. shift is the vertex-k data unfold over the CV-prior data unfold, minus 1
  (`state/s5p/stage3/envelope-receipt.json`, `definition`).
- **Its own scale, s = 1, is "the smallest envelope the vertices allow"** (`stage2-exit:124`). That is a contract floor,
  not a calibration.
- **Size.** Medians 12.0 / 9.6 / 13.4% and 90th percentiles 38.6 / 22.5 / 39.2% (J / H2 / EW). GiBUU dominates, in 60 of
  109 J cells (`stage2-exit:129-131`). Without D1: 11.25 / 4.28 / 9.90% (`amendment-6:17`).

**D1 is contaminated.**
- GENIE/MnvTune is 0.51 at E_avail > 3 GeV, "which inflates the D1 GiBUU/GENIE vertex that dominates h". The
  disposition was to "re-derive gen5d, the ratios and D1 before any calibration ensemble"
  (`REVIEW-20260927-s5p-round1-stage2-exit-and-joint-design.md:115, :119`).
- KNOWN_ISSUES row 83 is OPEN. Its update says the predictions were repaired by an exact per-event reweight
  (`KNOWN_ISSUES.md`, row 83).
- The s5e GiBUU departure truth is built from the same ratio **(inference from row 83's scope, "the contaminated
  s5n/s5e departure")**.

**The shift tracks minus the bias, but not cell by cell.**
- Correlations: 0.92 for W3; 0.73 / 0.94 for W2 (J / EW). Slopes: 1.12 for W3; 0.92 / 0.99 for W2
  (`stage2-exit:99-107`).
- Amendment 6 withdrew "empirical, slightly conservative bound". |shift + bias| / |bias| has a median of 0.30–0.52, and
  |shift| ≥ |bias| holds in only 52–78% of cells. "h is evidence that T1/T2 fail, not a per-cell bias bound"
  (`amendment-6:44`).
- Per-vertex J fractions are 0.697 (d1), 0.780 (d2), 0.706 (d4) and 0.578 (d3). d5 has no bias source
  (`envelope-receipt.json`, `linearity`).

**Those fractions use B0 bias, not R bias.**
- For d1, d2 and d4 the bias sources are B0 Asimov traces (`k_b0_gibuu`, `k_b0_w1`, `k_b0_w3`). d3 uses the s5e W2
  pseudo-experiments (`envelope-receipt.json`, `bias_sources`).
- B0 is configuration (d), whatis `d-N-B0`, defined at `state/s5n/contract.json:20`. It is a different estimator from
  (e).
- The R biases at the same departures are s5e's assessment ensembles: 20 each at eavail_gibuu, q3, W1, W2 and W3, plus
  40 nominal. They are in `/pscratch/sd/j/josephrb/s5e-20260925/runs/cand/assess/`, listed 2026-10-23 and dated
  2026-09-26 (receipt `state/s5e/cand/assess_receipt.json`).
- Under R, J recovers a median 0.36–0.86 of the departures (`amendment-1:39`). So r = |bias| / |departure| is about
  0.14–0.64 **(arithmetic)**.

### 2.2 Proposed construction (two forms; the declaration picks one)

**M1, diagonal.** u_f = κ · h_f, added to the half-width. This is the form T1's accounting used
(`stage2-exit:133-134`).

**M2, correlated.** C_model = κ² Σ_k s_k s_kᵀ: one two-point component per vertex k, fully correlated across cells. Its
diagonal is u_f = κ · (Σ_k s_k,f²)^½.
- This is the corpus's form for a named model component: H1's generator swap, and ATLAS's prior and hidden-variable
  components (§7).
- A χ² against a prediction sees the shift directions as correlated nuisances.

**κ is the one free constant.** It is calibrated, may be below or above 1, and is never set by hand.
- κ_q(S, h') is the smallest κ for which at least a fraction q of the (truth, cell) pairs in a truth set S satisfy
  |b_f| ≤ κ · h'_f.
- The pairs counted are those with departure > 1%, as in T2.
- b is the R bias at that truth: the mean over its ensemble.
- q = 0.68, and separately 0.95.

### 2.3 Calibration and held-out validation

**Calibration folds, grouped by generator family.** Holding out a single vertex would leave its generator in the
envelope. Leaving out D2 (W1), for example, keeps D4 and D5, both NuWro/GENIE. So the unit held out is a whole family:

| family | vertices removed from h when held out | R bias folds scored |
|---|---|---|
| NuWro | D2, D4, D5 | W1, W3, q3 |
| GENIE MEC | D3 | W2 |
| GiBUU, after Stage 0c | D1 | GiBUU (re-derived) |

- The q3 fold is s5e's q3_given_eavail_w at a = 0.3 (`state/s5e/contract.json:71-72`). It is assigned to the NuWro
  family through D5, the anchored NuWro/GENIE q3 ratio (`amendment-3:9`) **(inference)**.
- Before Stage 0c only two families are usable, and D1 is excluded throughout. That two-family run is provisional and
  decides nothing. The three-family run after Stage 0c is binding.

**The transfer test** (Stage 0a). For each held-out family F:
- Build h^(−F) from the data shifts of the vertices outside F.
- Set κ^(−F) = κ_0.68(the other families' folds, h^(−F)).
- Score c_F, the fraction of F's (fold, cell) pairs with departure > 1% and |b_f| ≤ κ^(−F) · h^(−F)_f.
- This asks the question that matters: does an envelope calibrated on some generators cover the bias for a generator it
  never saw? **(inference)** Every future model comparison is such a case.
- For 95% intervals, the model part uses κ_0.95, calibrated the same way.

**No held-out truth remains in the record.**
- Every s5p physical alternative was run, and its results read:
  - W1–W3 are "observed and … development alternatives here, never withheld truths" (`state/s5p/contract.json:22`);
  - GiBUU and q3 are s5e development truths (`state/s5e/contract.json:71-72`);
  - D5 and P1r–P3r were run in the pilot and in production (`amendment-7:33`).
- The four full-5D hybrid generator truths are not fresh either. The joint test simulated R pseudo-experiments at each
  of them, "pseudo-data at G's truth, background, refinement, R, statistic" (`stage2-exit:151-153`). That gave B =
  1,343–1,751 each (`RECORD-20261005-s5p-joint-5d-inference-result.md:44-53`).
- A withheld truth "is never run, reweighted onto a product or inspected before the admission record"
  (`state/s5p/contract.json:57`).
Search: withheld; held-out; held out in docs/orchestration/state/s5p/*.json and docs/orchestration/*s5p* @ 2bf101d1

**So Stage 2's validation truths must be newly declared, before any is run, in two disjoint sets:**
- a stress set of 6–8, run in Stage 2;
- a coverage set of 4–8, withheld until Stage 4. Once Stage 2 inspects a truth it is no longer withheld
  (`state/s5p/contract.json:57`), and T4 needs "every fresh validation truth point" (`amendment-1:41`).
- If R10 passes, Stage 2 also needs a departure in the added variable's own truth correlate, before any coverage claim
  (S:344-345).

| candidate | built from | sub-cell structure | caution |
|---|---|---|---|
| GENIE interaction-model band reweights (the 34 vertical bands, `amendment-7:15`), or FSI / MnvTune-component reweights | event-level weights | yes | gbdt §10 names exactly these as "an untouched physical departure", and adds: "The loader reads no such weights; whether the file carries any is unobserved" (`state/next-preparation-20261009/gbdt/REPORT.md:449`). The joint test drew every band as a nuisance per experiment (`amendment-7:22`), so whether a declared band amplitude counts as untouched must be checked in the declaration |
| new tilts along pT, p∥, q3 or W | the fine grid | no | the existing tilt is `eavail_tilt` (I:30), along E_avail, which D1 and D2 span. Its OmniFold residual is small: J median 0.143% (I:76-80) |

**What still has no test:** dependence on structure finer than a cell from a generator other than GENIE.
- A construction is on record. Greif's §6.4.1, the form ATLAS uses, reweights "the *alternative* generator's
  **particle level** to match the nominal generator's **particle level**" and swaps that sample in as the unfolding MC
  (`BRIEF-20260901-greif-fps-thesis-implications-for-pet.md:194-197`;
  `state/2d-closeout/stageF/methods/register-prd-study/notes/2405.20041.md`).
- It needs an event-level alternative-generator sample in the analysis MC's space. MP-2's event-level reweights to the
  generators are not established: "No generator is established" for GENIE CV, GENIE MEC, NuWro or GiBUU
  (`state/measurement-paper/phase1/mp2/S2-CLOSURE-SUMMARY.md:18-21`).
- The GENIE band reweights test it only within GENIE's model space **(inference)**.
Search: hidden variable; hidden-variable; event-level reweight; established in docs/orchestration (git grep -i) @ 177bf84bb960

## 3. Can the model-dependence term shrink?

**The inverse problem sets the term, not the classifier (inference).**
- D-ID: at K = 5 "the GBDT leaves about the residual an exact binned response iteration leaves". GiBUU 9.5% against
  8.3%, W1 5.4% against 5.4%, W3 5.6% against 4.9% (`d-id/REPORT.md:436-440`). Branch C holds in J, EW and H2 (`:514`).
- IBU-1, median J residual, IBU / OmniFold: GiBUU 7.300 / 9.508%, W1 5.560 / 5.988%, W3 5.034 / 5.395% (I:76-80).
  - Its verdict is UNRESOLVED only because the tilt truth allows "mixed" (I:22, I:37-38).
  - IBU's own corrected coverage at 400 seeds is 0.000 at GiBUU, W1 and W3 (I:152-163).
  - On real data, IBU and (e) differ by a median 4.75% per J cell (I:168-173). That is a cheap empirical estimate of
    estimator dependence.
- PLAN draws the same conclusion: "the classifier is not the bottleneck" (`PLAN.md:387`).

**Levers that did not move the term, or are not routes:**
- more iterations or capacity: 3–8% (`amendment-4:9-15`);
- a transferred bias correction, which did not transfer (`PLAN.md:386`);
- FBU, "never tried" and "not a route" (`PLAN.md:390`).
- Positivity changed MP4-A's prior-free OSB widths by a median ratio of 0.9983 (`phase1/mp4a/REPORT.md:92-93`). That
  measures width, not the model term.
- For scale, the prior-free OSB floor is a J median of 28.59% (`mp4a/REPORT.md:19-27`). It is what an interval without
  any prior information costs.

**Levers on record that could shrink the term:**

*(a) Re-derive the contaminated D1* (Stage 0c).
- D1 dominates h in 60 of 109 J cells. Dropping it gives J 11.25% and H2 4.28% (`amendment-6:17`).
- A repaired D1 would land somewhere between dropping it and keeping it **(inference)**.

*(b) More reconstructed information (R10).*
- MP4-A §6a splits every reco bin at its midpoint on each axis: 113,062 occupied cells against 10,499. That moves the J
  noise-free, signal-only floor at grid T2 from a median of 0.2866 to 0.1083, and p90 from 1.1716 to 0.3157
  (`mp4a/REPORT.md:109-112, :123`). The report calls this "the edge of T1" (`:135-138`).
- Its caveats include the same finite MC and a noise-free case, and: "T2, the bias/prior target, is a separate failure
  that (c) does not address" (`:140-150`, `:144`).
- R10 tests both width and residual (S:277-312):
  - (i) 2× and 4× refinement;
  - (ii) a sixth reco axis;
  - split-half responses and a null variable.
- Its rule requires the floor to reach T1 or halve, **and** the J median |r_IBU(K = 5)| to fall by **at least** a third
  at ≥ 3 of 4 departures (S:332-339). The residual clause is the model-term clause.
- The smallest passing cut, carried over to h (an unrecorded mapping, **inference**), takes J from 12.0% to about 8%.
  Larger cuts are not excluded.
- After a pass, S requires a departure in the added variable's own truth correlate before any coverage claim
  (S:344-345), because added information can import bias (S:265). Stage 2 carries this.
- Cost, as S estimates it: (i) about 2–10 local core-h; (ii) about 1–3 CPU node-h of extraction, then 2–10 core-h
  (S:318-326, labelled estimates there).
- R10 is the validation lane's test. This design uses its verdict as Stage 1 and does not run it.

*(c) A prior-informed estimator.* D-ID's branch C "does not exclude estimators that use prior information"
(`d-id/REPORT.md:551-552`). The model term is exactly the budget such an estimator must carry, so it is not a separate
lever **(inference)**.

Search: R10; unbinned information; D1; constraint loophole; prior information in docs/orchestration/state/measurement-scoping/SCOPING.md, docs/orchestration/state/measurement-paper/PLAN.md, docs/orchestration/state/next-preparation-20261009/d-id/REPORT.md @ 177bf84b

## 4. The central-value estimator and its covariance

**Proposed: configuration (e)** (`e-R-joint-test`): N/B0 with the Stay-Positive refinement at 400 trees and 31 leaves
(`state/s5e/contract-amendment-3-candidate-R-and-assessment.json:26`).

**For (e):**
- **The model-term evidence is for (e).** Study P's shifts are R data unfolds (`amendment-3:9`), and the s5e ensembles
  are R. Choosing (a) would mean redoing both under (a).
- **Background.** (e) removes the nominal background bias by "> 80% in every worst cell" (S:179). (a) uses purity
  subtraction (`docs/analysis-note/sec_method.tex:240-241`).
- **Consistency.** The joint tests use (e)'s data unfold (`DECISION-20261023-joseph-5d-a-and-register-round.md:30-31`).
- **Numerics.** T3 is met in s5p: spread median 0.2%, max 0.62%, against a total σ ≥ 6% (`stage2-exit:52-53`).
  - s5p study N found the data-rounding component ABSORBED by R's data bootstrap: "about 37% of the data bootstrap
    variance on J is rounding noise" (`stage2-exit:44-46`).
  - s5e's A3 had found that a float32-ulp perturbation of the real data moves the functionals by 0.78 data-σ (median)
    and 2.58 (max). S still lists s5e item 1 open, at about 6.3 CPU node-h (S:186).
  - The data σ is 1.57× the pseudo σ (`stage2-exit:47-50`).

**Against (e):**
- **No covariance yet.** 5D central values "stay configuration (a) for now … until an (e) covariance exists"
  (`DECISION-20261023-joseph-5d-a-and-register-round.md:30-31`).
- **Departure coverage.** (e)'s statistical intervals fail at every departure. Pooled 68% coverage is 0.0235 / 0.0186 /
  0.0252 / 0.157 / 0.0173 at GiBUU / q3 / W1 / W2 / W3, against 0.680 at nominal (n = 40)
  (`state/s5e/cand/assess_receipt.json`, `points/*/pooled_cov68`).
- **The scoping memo's advice.** It is unqualified: "do not plan a coverage campaign under configuration (e)" (S:381).
  It also recommends that a paper "state statistical coverage where tested" (S:391-393).
- **This design departs from both.** It proposes coverage tests of (e) plus a calibrated model term. They come only after
  Stage 0, the D1 repair and R10, and only at small scale before any large campaign.
- The memo's stated reason is that IBU-1's arm N reads consistent at every truth, so "On arm N the pattern is the
  inverse-problem-limited one" (S:230-234, S:382). That is bias a background treatment cannot remove. The model term is
  meant to be the width that carries it, and Stage 0 tests whether it can **(inference)**.

**No (e) covariance exists** (`DECISION-20261023-joseph-5d-a-and-register-round.md:8-10`). RE-1 built none
(`state/2d-closeout/stageF/methods/RE1-SPEC.md:7-10`).
Search: configuration (e); (e) joint-test estimator; (e) joint-test estimator; joint-test estimator; R (s5e candidate); R (s5p baseline_estimator); configuration 1 = R; R = paper configuration (e); s5e candidate R = the joint-test estimator; --candidate R; --candidate R (contract implementation); refinement 400 trees, 31 leaves; refinement 400/31; 400-tree, 31-leaf Stay-Positive refinement; s5p data unfold @ 2bf101d15c7f

**Building one** follows the adopted (a) design, z-cv:
- Assembly: C = D(Σ_V C_b)D + Σ_R C_b + Σ_A L_b + C_stat + C_ML on the 10,694 reported cells
  (`docs/analysis-note/sec_5d.tex:584-596`).
- 187 universe unfolds (`docs/analysis-note/sec_systematics.tex:570`), mostly the 100-universe PPFX flux band
  (`docs/analysis-note/app_statmethods.tex:196-198`).
- 100 bootstrap replicas (`nd-unfolding/Z_BUILD_PACKET.md:350`).
- In all, 288 data unfolds (`gbdt/REPORT.md:423-424`).

**The R-path universe infrastructure exists.**
- `s5p_universe.py`, `s5p_input_dumps.py` and `s5p_assemble.py` were "built, not run" for measurement production
  (`stage2-exit:171`).
- s5p's null experiments drew, per experiment under R, one PPFX flux universe, every one of the 34 interaction-model
  bands and the four weight-only detector bands (`amendment-7:15, :22`).
- Ten real-data lateral R unfolds exist (`state/s5p/s3-latunfold-tasks.tsv`).
- Stage 3a starts from these.

| item | value | source |
|---|---:|---|
| (e) data unfold, float64 | 648.0435 s (n 70; mixed tasks) | `state/s5p/stage2/stage2_receipt.json`, `costs` |
| data / pseudo ratio | 2.2044 against float32 pseudo (293.973 s); 1.9103 against float64 pseudo (339.244 s) | **(arithmetic)** |
| GPU node-h per data unfold, G2 × 4 | 0.0546–0.0630 | **(arithmetic; assumes the ratio carries to GPU nodes)**: 0.028559 × 1.9103 to × 2.2044 |
| 288 data unfolds, admitted (× 1.25 / 0.8) | **24.6–28.3 GPU node-h** | **(arithmetic)** |
| the same at today's CPU C0 speed | 15.9–18.4 CPU node-h | **(arithmetic)**: 648.0435 × (533.0555 / 339.244 to / 293.973) / 28,800 × 288 × 1.5625 |
| the recorded CPU estimate at September speed | ≈ 10.1 node-h "after inputs exist; inputs **unpriced**" | `gbdt/REPORT.md:450` |
| a comparable (a) construction (598 unfolds, laterals) | 12.3 CPU + 13.2 GPU (+ ≈ 2.6 CPU) node-h; its "GPU" arms ran LightGBM on CPU | `FEASIBILITY-20260925-s5c-scalar5d-measurement-and-inference.md:23` |
| a 10,694² float64 matrix | ≈ 915 MB (z-cv.npz is 890,500,272 B) | `COSTMODEL-20260911-z-pilot-and-scan.md:76`; `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md:111-116` |

## 5. Validation: stress tests and coverage, priced

**Unit cost.** G2 × 4, an (e) pseudo unfold costs 0.028559 GPU node-h = 411.2535 / 3600 / 4
(`state/gpu-timing-20261023/REPORT.md:22-23, :74`). With §9's × 1.25 packing and / 0.8 reserve, the admitted cost is
0.0446234 per unfold **(arithmetic)**.
- The figure was measured on 2026-10-23, so it already includes today's slowdown: about 1.4× the September record on both
  node types (`gpu-timing REPORT.md:79-80`). The cause is not identified (`:35`).
- Any CPU figure priced from 293.973 s is about 1.4× optimistic (`:109-110`).
- Like the gbdt table, these figures exclude sample construction, identity work, retries and review
  (`gbdt/REPORT.md:426`).

**Unfolds per experiment (U).** A statistical + model interval needs:
- the central unfold;
- B = 30 bootstrap replicas (§9's statistical-only recipe);
- the five prior-vertex unfolds, which give that experiment's own shifts.

That makes U = 36. If the model term were fixed once from the data shifts, U = 31. This design recomputes it per
experiment, so that the tested procedure is the frozen one **(inference)**.

**The director's figures, reconstructed (inference).** The assignment gives "pooled 400 per truth, about 2,600–7,600
GPU node-h; per-functional, about 28,300" (`ASSIGNMENT.md:34-35`), without their assumptions.
Search: 28,300; 7,600 GPU; pooled 400 in docs/orchestration (git grep -F) @ 2bf101d1
- U = 36 reproduces the per-functional figure: 4 cases × 4,404 experiments × 36 × 0.0446234 = **28,299 GPU node-h**.
  4,404 is the J sizing for 4 cases (`gbdt/REPORT.md:412-413`).
- At the same U the pooled cost is 642.58 per truth. 4 truths give 2,570 and 12 give 7,711, close to the quoted
  range. The truth counts are inferred, not recorded.
- At U = 31 the per-functional figure is 24,369, the GPU-timing table's value (`gpu-timing REPORT.md:123-128`).

| test | size | U | GPU node-h, admitted | storage at 183,905 B per product |
|---|---|---:|---:|---|
| stress (bias) ensemble, per truth | 40 experiments | 1 | 1.785 | 7.4 MB |
| pooled coverage pilot, per truth | 40 | 36 | 64.26 | 265 MB |
| pooled test, per truth | 400 | 36 | 642.58 | 2.6 GB |
| per-functional, J, 4 cases | 17,616 | 36 | **28,299** | 117 GB in full, or 553 MB as J summaries |

All of the above is **(arithmetic)**.

**About the sizing:**
- 4,404 is sized at the gbdt proposal's bounds: ≥ 0.63 (I68) and ≥ 0.92 (I95) per functional, at familywise 0.05,
  with 0.80 assurance at exactly nominal coverage. "The bounds are proposals" (`gbdt/REPORT.md:408-413`).
- T4's bounds are 0.60 and 0.90 (`amendment-1:41`). Re-sizing at those would likely need fewer experiments
  **(inference)**. Stage 6's declaration must re-size.
- "A pooled pass cannot certify a failing functional" (`amendment-1:41`). A pooled test can still refuse cheaply. At
  n = 40 the binomial SE of a 0.68 coverage is 0.074 per functional, and s5e's departure coverages were 0.017–0.157
  **(arithmetic)**.

**Systematics are outside the coverage tests.**
- Throwing the 187 universes per experiment would make U ≈ 223, about 6.2× the per-functional figure: roughly 175,000
  GPU node-h, beyond the pool **(arithmetic)**.
- The scoping memo recommends carrying "systematics as quoted blocks without a coverage claim" (S:391-393). This design
  follows that for systematics, while still coverage-testing the statistical + model interval (§4).
- T4 as written asks for total intervals (§6).

**Pools and the clock.**
- `m3246_g` had 42,727.4 node-h left at 2026-10-23 05:31 UTC (`state/gpu-timing-20261023/ASSIGNMENT.md:16`).
- The group draws about 990 a day (`state/measurement-scoping/iris-20261023.txt`; S:134). It drew about 860 a day as of
  10-19 (DECISION-20261019 §1b). At those rates the pool runs out between 2026-12-05 and 2026-12-11, whatever this
  project does **(arithmetic)**.
- The per-functional test is 66% of what was left on 10-23.
- The CPU pool had 2,288.5 left (S:133), under the director's half-pool rule (S:138). At today's C0 speed the
  per-functional test would cost 17,616 × 36 × 0.018509 × 1.5625 = 18,340 CPU node-h, beyond that pool
  **(arithmetic)**.
- Any use of `m3246_g` is Joseph's and Ben's decision (S:150).
- The wall time of a large GPU campaign depends on how many GPU nodes run at once, which this design does not measure.
- **Storage.** Products go to pscratch first. Durable copies go to HPSS (161 GiB free, the R9 route,
  `DECISION-20261023-joseph-r8-r9-and-5d-scoping.md:13`), never CFS (DECISION-20261019 §1b).

## 6. Targets: which the route meets, and what would have to change

| target (`amendment-1`) | on this route | what Joseph would have to decide |
|---|---|---|
| **T1** total width: median ≤ 10%, p90 ≤ 25% (`:38`) | **RD1 and RD3 not met** at the current reco: the half-width is ≥ h_f + 1.4%, so RD1 ≥ 12.6% and RD3 ≥ 11.3% even without D1 (`amendment-6:17`). At a calibrated κ, the width moves with κ (κ < 1 allowed). **RD2: open.** h without D1 is 4.28% | keep T1, which sets Stage 0b's model-term bar at 8.6%; or set a new width W before Stage 0 runs, never after, giving a bar of W − 1.4% |
| **T2** bias control: \|bias\|/\|departure\| median ≤ 0.25, and model component median ≤ 5% (`:39`) | **not met** at RD1 (component 12.0%; 9.6–13.4% across RD1–RD3, `stage2-exit:136-138`). RD2's component could meet 5% after the D1 repair. The recovery clause fails under R on J (r ≈ 0.14–0.64, `amendment-1:39`) and on H2 (r ≈ 0.33 at GiBUU and W3, §1) | replace the 5% cap with a validated-coverage requirement on the model term (Stages 2 and 4–6), and decide whether the recovery clause stays a target or becomes reported information |
| **T3** numerical (`:40`) | met in s5p (`stage2-exit:52-53`), with the rounding absorbed (`:44-46`); S still lists s5e item 1 open (S:186) | — |
| **T4** coverage: total 68% and 95% at every functional and fresh truth point, Clopper–Pearson Bonferroni lower bounds ≥ 0.60 / 0.90 (`:41`) | the route's aim, for statistical + model intervals only (§5) | restrict "total" to statistical + model, with systematics as covariance blocks |
| **T5** per-functional pull SD in [0.80, 1.25] (`:42`) | at risk: EW41 1.06–1.41 (`amendment-6:45`). RD1's selection needs T5 (`:54`) | none; Stage 4 reports it and Stage 6 tests it |
| **T6 / T7** joint test and p-values (`:43-44`) | executed: all ten H0(G) rejected. T6 power met for P1 and P2, not P3 (0.231) (`RECORD-20261005-s5p-terminal-evaluation-pending-verification.md:129, 135`). Every decision is currently "can change" (`:107`) | — |

**Would the result still distinguish the generators users care about?**
- T1's own justification says a band wider than 10% "cannot distinguish the named generators and is not a precision
  result" (`amendment-1:38`).
- The differences that matter are J medians of 3.7% (GENIE MEC/CV, (E_avail, W)), 7.7% (NuWro/GENIE 3D), 10.0% (NuWro
  E_avail) and 16.0% (GiBUU E_avail) (`amendment-1:10`). The GiBUU figure carries the D1 flux contamination
  **(inference)**.
- **Per cell.** With a model term near h's J median (12.0%), only GiBUU's difference exceeds one half-width in a typical
  cell **(arithmetic)**.
- **Jointly, the question is open (inference).**
  - The vertices are generator directions, so M2 is correlated along exactly those directions.
  - Where R recovers a fraction 1 − r of a departure D, the unfolded difference is (1 − r)·D, against a bias-sized term
    of about r·D.
  - Under R on J, r ≈ 0.14–0.64, so (1 − r)/r ≈ 0.56–6.1 **(arithmetic)**.
  - Stage 0b measures this directly.
- **The joint test answers a different question.** It rejects each H0(G) on data. Its null is simulated through R, so
  "the estimator's bias under G is part of the simulated null" and its validity "does not rest on the measurement's
  bounded model component" (`stage2-exit:151-153`).
  - It is "NOT CITABLE FOR: A measurement" (`RECORD-20261005-s5p-joint-5d-inference-result.md:12-13`).
  - A measurement would add a cross section with an uncertainty usable for comparisons that test did not make, which is
    where the model term bites **(inference)**.

## 7. Comparison with community practice

**The corpus.** It holds 12 papers:
- MINERvA 2106.16210, 2110.13372 and 2002.12496;
- T2K 2004.05434 and 2102.03346;
- MicroBooNE 2301.03700 and 2310.06082;
- the Wiener-SVD method paper, 1705.03568;
- OmniFold on T2K, 2504.06857;
- ATLAS 2405.20041;
- H1 2108.12376;
- 2205.05084.

The per-paper notes are in `state/2d-closeout/stageF/methods/register-prd-study/notes/`. The corpus "was chosen, not
sampled" and is not citable for physics (`register-prd-study/REPORT.md:20-25`). It is used here only for what practice
looks like.

**How the corpus handles model dependence.** It is "a quantity or an object, not a caveat", in four recipes
(`REPORT.md:129-141`):
- **A named component, defined by its procedure.**
  - H1: "the difference in the result when unfolding with Rapgap and with Djangoh".
  - MINERvA 2110.13372: the MnvTune-v1.2 to v3 difference.
  - ATLAS: the prior and hidden-variable components, "the dominant contributor for many observables".
- **An object handed to users.** MicroBooNE's A_c is to "be applied to any independent theoretical prediction". The
  Wiener-SVD method paper explains why: "one can avoid including the bias due to unfolding in the final uncertainties"
  (`REPORT.md:134-136`).
- **A fake-data study followed by a decision.** MINERvA 2106.16210 chose 10 iterations this way.
- **A concession plus mitigation.** T2K reports regularised and unregularised results.

**How it validates.**
- Model components in the notes are one- or two-point differences.
- Validation is fake-data closure on a few alternatives, judged by χ², a p-value, or whether the stated uncertainties
  "covered the difference". MicroBooNE 2310.06082 uses the last (`notes/2310.06082.md:14`). ATLAS reports every
  closure p-value passing except one observable at 0.038 (`notes/2405.20041.md`).
- The committed notes record neither of these, in any of the 12 papers:
  - a pseudo-experiment coverage test of reported intervals;
  - a calibrated envelope or a quantitative per-bin bias bound.

Search: coverage; pull; undercover; envelope; bias bound; per-bin in docs/orchestration/state/2d-closeout/stageF/methods/register-prd-study/notes/ @ 2bf101d1

**Where this design is stricter.** Its model term is calibrated to a stated coverage. It is validated at newly declared
truths, and its intervals are coverage-tested.

**Where it is looser or no stricter.**
- Systematics are carried without a coverage claim, as in the corpus.
- It has no cross-generator hidden-variable component (§2.3).
- Its validation truths are reweights of one MC.

**A version at the community standard** would include:
- an (e) central value with an (e) covariance (Stage 3: about 25–28 GPU node-h plus the 3a inputs);
- an M2 component at κ = 1 from the five vertices, after the D1 repair;
- fake-data closure at the record's departures;
- no coverage test.
<!-- absence-ok: lists the content of a proposed alternative design, not a claim that a result does not exist -->

Its intervals' coverage at departures is untested. Stage 0 is the cheapest test of it. Statistical-only (e) coverage
there is 0.017–0.157 (§4). Whether to publish at that standard, below the frozen T1–T7, is Joseph's call.
Search: configuration (e); (e) joint-test estimator; joint-test estimator; R (s5e candidate); --candidate R; refinement 400/31; s5p data unfold @ 2bf101d15c7f

## 8. The staged plan (cheapest first; rules proposed for each stage's declaration)

**General rules.**
- Each stage needs its own DECLARATION and BINDING. The rules below are proposals for those declarations, written before
  any of their results exist.
- **Outcomes are binary.** A stage either PASSES or STOPS. A STOP is reported to the director, and nothing downstream
  runs without a new decision.
- **Two exceptions, set now:**
  - the provisional two-family run of 0a and 0b never stops anything, and 0c runs whatever it gives;
  - Stage 1's gate is "R10 has reported". An R10 STOP does not block Stage 2 if the binding Stage 0 passed (§9).
- **R10 must report before any stage that uses the GPU pool.** The criterion record says "The cheap tests (IBU-1; the
  reconstruction-information test R10 …) come first" (`DECISION-20261023-joseph-gpu-test-and-campaign-criterion.md:24-25`,
  the director's record of item 3).
- **The pscratch purge clock.** Stages 0 and 0c read pscratch products dated 2026-09-26. Under NERSC's scratch purge of
  files not accessed for 8 weeks (NERSC policy, not a repository record), they are at risk from about 2026-11-21.
  - Stage 0 should run before then, or its inputs should be copied to HPSS first **(arithmetic)**.

| stage | decisive test | proposed rule: PASS (anything else STOPS) | cost | unlocks |
|---|---|---|---|---|
| **0a** calibration transfer | §2.3's family-held-out test, on J; H2 and EW also reported. Provisional on two families; binding on three after 0c | separately for M1 and M2, on J: c_F ≥ 0.60 at every held-out family (T4's per-functional bound), **and** coverage pooled over families ≥ 0.68 | 0 node-h. Local; reads the seven study-P data unfolds (`prior_R5fix_{CV,prior_d0..d5}.npz`) and the 140 s5e R assessment products | 0b |
| **0b** usefulness | κ* = κ_0.68(all usable folds, h). Covariance: C_stat from s5p's R data bootstraps (`runs/s2/num/data`, study N1) + C_model(κ*), dropping each generator's own vertex when scoring it + the (a) z-cv systematics projected to J (an approximation, labelled). Expected Δχ², shape-only and total, between each available stage-1 pair's R-unfolded mean and nominal | J median u_f ≤ W − 1.4% (8.6% with T1 kept) **and** expected shape-only Δχ² ≥ 9 for ≥ 2 of the available pairs | 0 node-h. Local; z-cv read once, about 0.9 GB | 0c (provisional run); Stage 1 (binding run) |
| **0c** D1 repair | re-derive the D1 ratio from the flux-repaired GENIE prediction (KI 83; GiBUU itself "was not rebuilt", `state/s5p/gen5d/README-gen5d-fluxfix.md:139`); one study-P data unfold; rebuild the GiBUU R ensemble at that truth (20 experiments); then rerun 0a and 0b on three families (binding) | as 0a and 0b | on CPU nodes at today's C0 speed: 0.0408 × 1.5625 for the data unfold + 20 × 0.0289 ≈ 0.64 CPU node-h, plus the local ratio rebuild (REVIEW:119 asks to "re-derive gen5d, the ratios and D1"; unpriced) **(arithmetic)** | the binding Stage 0 verdict. **H2 gets its first fair test here** |
| **1** R10 (the validation lane's) | as declared there (S:277-339) | gate: R10 has reported, by S:332-339 unchanged | ≈ 2–10 core-h + ≈ 1–3 CPU node-h (S:318-326, S's estimates) | on PASS: redo Stage 0 with the added information (the s5e ensembles and the seven study-P unfolds with the new features; development run ≈ 2.3 CPU or ≈ 4.5 GPU node-h, S:341-343; the data unfolds are not priced there), then Stage 2. On STOP: Stage 2 at the current information, if the binding Stage 0 passed |
| **2** held-out stress | declare the stress set (6–8) and the withheld coverage set (4–8) before any is run (§2.3); after an R10 pass, include a departure in the added variable's truth correlate; 40-experiment R bias ensemble at each stress truth | at every stress truth, ≥ 0.68 of J cells (departure > 1%) with \|b_f\| ≤ u_f, with κ* frozen | 1.785 GPU node-h per truth, ≈ 10.7–14.3, + truth construction, unpriced ("event-loop production if weights are absent", `gbdt/REPORT.md:449`) | 3a |
| **3a** (e) universe inputs | from `s5p_universe.py` / `s5p_input_dumps.py` (`stage2-exit:171`), build the per-universe 5D inputs for (e) | the 187 universe inputs match (a)'s universe set by name and count, and a CV-universe unfold equals the central product bitwise | priced in its declaration (`gbdt/REPORT.md:450` calls the inputs unpriced) | 3b |
| **3b** (e) covariance | 288 data unfolds, assembled as z-cv (§4) | the assembled matrix is PSD and passes z-cv's construction checks; per J cell, C_stat's σ against an independent comparator, s5e's 40 nominal R pseudo-experiments' spread × the recorded data/pseudo σ ratio 1.57 (`stage2-exit:47-50`; labelled approximate), has median ratio in [0.80, 1.25] | ≈ 24.6–28.3 GPU or ≈ 15.9–18.4 CPU node-h (§4) | 4 |
| **4** pooled pilot | the statistical + model interval at U = 36, at 4 truths from the withheld coverage set plus nominal, 40 experiments each; T5 at nominal reported | pooled 68% coverage ≥ 0.60 and 95% ≥ 0.90 at every truth | 64.26 per truth; ≈ 321 GPU node-h | 5, and Joseph's criterion |
| **5** pooled test | 400 experiments per truth, at 4–8 truths of the withheld set not inspected in Stage 4, or newly declared | one-sided 95% Clopper–Pearson lower bound on pooled coverage ≥ 0.60 (68%) and ≥ 0.90 (95%) at every truth | 2,570–5,141 GPU node-h | 6 |
| **6** per-functional | J, 4 cases, re-sized at T4's bounds; T5 per functional | T4 and T5 as Joseph amends them (§6) | ≤ 28,299 GPU node-h at the gbdt sizing | the measurement |

**Joseph's GPU-campaign criterion.**
- His words: "I feel like we would only want to use this many GPU hours if we reasonably believe this will result in a
  measurement-quality paper" (`DECISION-20261023-joseph-gpu-test-and-campaign-criterion.md:11`).
- The record's reading: a campaign that would "most likely confirm a failure already measured at small scale does not
  meet it". "Today the record does not meet it", citing s5e's 0.017–0.157 (`:22-24`).
- **Proposal, for Joseph:**
  - Stages 0–1 need no GPU (0c runs on CPU nodes).
  - Stages 2–4 are small (about 14, 28 and 321 GPU node-h). Whether they count as "this many GPU hours" is his call.
  - Stages 5 and 6 should be proposed only if Stages 0–4 have passed, so that the small-scale measurement the criterion
    asks about is in the record.

## 9. What would make the 5D measurement not worth pursuing (falsifiable)

**Stop, and record a negative scoping verdict at the current reconstructed information, for every reporting definition
that fails, if both hold:**
1. **The binding (three-family) Stage 0 STOPS after the D1 repair (0c).** That is, either:
   - (0a) a κ calibrated on the other families covers less than 0.60 of the bias at some held-out family, or pooled
     coverage is below 0.68; or
   - (0b) the calibrated term's J median exceeds W − 1.4% (8.6% with T1 kept), or fewer than 2 generator pairs keep an
     expected shape-only Δχ² ≥ 9.
2. **R10 STOPS by its own rule** (S:332-339), or it passes and Stage 0 still stops when rerun with the added information.

**If R10 has not reported:** after a binding Stage 0 STOP, the plan holds and the director is told; after a binding
PASS, Stage 2 waits for R10. A missing R10 verdict never releases a GPU stage.
**If the binding Stage 0 PASSES and R10 STOPS:** the plan continues at the current information (Stage 2).

**Also stop:**
- at any STOP in Stages 2, 3a, 3b, 4 or 5;
- if Stage 3a finds that universes cannot be produced for (e) (`gbdt/REPORT.md:450`);
- if Stage 2 cannot declare disjoint stress and coverage sets from untouched domains. This is gbdt §10's own stop rule,
  "NO UNTOUCHED VALIDATION DOMAIN" (`gbdt/REPORT.md:449`).

**What a stop would mean (inference).** No construction on record turns model dependence into a validated uncertainty
small enough to resolve the generator differences the measurement exists for. The joint-5D inference
(`RECORD-20261005-s5p-joint-5d-inference-result.md`) remains the 5D physics result, and H2 or EW reporting stays
descriptive, unless Joseph changes the endpoint (§1).

## 10. What this design does not do

- It runs nothing. Stage 1 belongs to the validation lane.
- It does not size Stage 6 at T4's bounds, price Stage 3a, or price the Stage 2 truth construction.
- It has no cross-generator hidden-variable construction (§2.3).
- It does not explain today's 1.4× slowdown (`gpu-timing REPORT.md:35`).
- It changes no claim, target or endpoint.

## 11. Decisions for Joseph (through the director)

1. **Reporting definition.**
   - RD1 again, which re-applies `amendment-1:54` under changed targets.
   - Or RD2, which is the contract's predeclared fallback, but PLAN asks whether it counts as "coarser" (§1).
2. **T1:** keep it (Stage 0b's bar is then 8.6%), or fix a new width W before Stage 0 runs (§6).
3. **T2:** replace the 5% component cap with a validated-coverage requirement. Decide whether the recovery clause stays
   a target (§6). RD1 and RD2 both fail it under R (§1).
4. **T4:** restrict "total" to statistical + model, with systematics as covariance blocks (§5, §6).
5. **Reopening the closed route** "prior dependence carried as an uncertainty component" (`PLAN.md:385`), which items
   2–4 imply.
6. **GPU-pool use with Ben:** Stages 2–4 are about 360 GPU node-h; Stages 5–6 up to about 33,000. Decide whether
   Stages 2–4 are small enough to precede the criterion (§8).
7. **The community-standard alternative** (§7): publish below T1–T7, without coverage tests.
8. **Whether M1 or M2** is declared. This design recommends M2, because it keeps the shift directions for χ²
   comparisons.
