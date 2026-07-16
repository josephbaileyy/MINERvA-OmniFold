# Statistical-validation repair — protocols, verdicts, status (Agent C)

Working tracker for the reassigned Agent-C mandate: repair the statistical-validation
claims (coverage, C2ST, correlated method comparisons). NOT a run receipt. Verified numbers
→ `../VALIDATION_LEDGER.md` at the commit gate; wording for the analysis note is handed to
Agent D (this agent does NOT edit `docs/analysis-note/`). Started 2026-07-16.

Global rules honored: predeclared truth/estimator/interval/seeds/partitions before expensive
jobs; do not rerun frozen central event loops; do not change central estimators to simplify
validation; do not remedy an invalid design with more replicas of it; preserve existing
outputs as diagnostics; exact manifests + estimator/seed fingerprints in every summary.

Estimator fingerprint used throughout (matches production): LightGBM GBDT, 5 iters, fixed
estimator seed 42 (`omnifold_loop(..., seed=42)`); reported bins = CV>0.

---

## Workstream 1 — COVERAGE

### Flaw (confirmed)
- 2D `2d-unfolding/uq/coverage_toys.py`: σ = `std(U;ddof=1)` and truth = `mean(T)` BOTH from
  the same toy ensemble; "coverage" = `frac(|U−mean(T)| ≤ σ)`. This is a standardized-pull
  self-consistency fraction (~0.68 by construction for a near-Gaussian ensemble), not
  frequentist coverage of an independent interval.
- FPS/ND `nd-unfolding/coverage_toy_nd.py` + `fps_extension_validation.py`: truth reference is
  independent (unfluctuated closure truth), but σ = `std(X;ddof=1)` is still same-ensemble, and
  the estimator seed is frozen (42) so the certified band excludes ML noise.
- Quoted: KNOWN_ISSUES #2; VALIDATION_LEDGER:236-244,422-428; OPEN_ITEMS #7; analysis-note
  app_statmethods.tex:1064-1070/1249/1269, sec_validation.tex:53-57, sec_fps.tex:75-77; RUN_LOG.

### Predeclared contract (fixed BEFORE looking at results)
- **Truth**: the closure truth vector `x_true` = the injected-feature (or nominal) generator
  truth histogrammed on `pass_truth`, completeness=1 — the same quantity each toy tries to
  recover. (Deterministic; independent of the toy fluctuations.)
- **Estimator**: production OmniFold (lgbm, 5 iter). Toys MUST include the noise sources the
  interval claims to cover: data Poisson + coherent MC Poisson + **ML/estimator seed varied
  per toy** (currently frozen — a predeclared fix so the coverage tests the published band,
  which includes C_ML).
- **Interval**: ±1σ where σ is **independently estimated**, two acceptable variants, both
  reported:
  - **(A) analytic**: σ_i = sqrt(diag(C_adopted)) from the adopted publication covariance
    (independent of the coverage toys) — tests whether the *published* interval covers truth.
  - **(B) split-ensemble**: partition toys into disjoint CALIBRATION (estimate σ) and
    EVALUATION (count containment) halves by predeclared seed parity — tests the toy
    procedure's own interval without circularity.
- **Statistic**: observed coverage c_i per bin = fraction of EVALUATION toys with
  |x_toy,i − x_true,i| ≤ σ_i; plus the aggregate over reported bins.
- **Uncertainty**: per-bin binomial errors are meaningful across independent toys, but the
  aggregate over bin--toy cells is not binomial because bins within a toy are correlated.
  Report the aggregate point value and, if useful, a toy-cluster conditional SE; do not use
  it as a global calibrated test because the calibration widths are themselves estimated.
- **Seeds/partitions**: EXISTING toys reused as EVALUATION (their seeds are the manifest);
  variant B splits by even/odd seed. No new toys generated under the circular design.

### Implementation plan
- New script `nd-unfolding/coverage_valid_nd.py` (does NOT touch coverage_toy_nd.py /
  fps_extension_validation.py / coverage_toys.py — those are preserved as the pull diagnostic):
  reads the existing toy `xsec_flat` stack + the adopted covariance ROOT + x_true; computes
  variant-A and variant-B containment diagnostics without a naive aggregate binomial error;
  writes a machine-readable JSON with
  estimator/seed fingerprints and the exact toy-id manifest.
- Pilot: run on the existing 2D (200) and FPS (200) toy stacks — reuse-only, no production.
- Only if variant-A/B disagree materially or ML-noise inclusion changes the verdict do we
  generate a NEW, valid toy ensemble with per-toy estimator seed (predeclared, small pilot first).

### Verdicts (per claim)
- `mean coverage 68.71%` (2D), `68.93%` (FPS): **RELABEL** the existing numbers as
  "standardized-pull / Gaussianity self-consistency diagnostic (⟨|r|⟩≈√(2/π))," NOT coverage.
  FPS can be replaced by a clearly labeled fixed-truth split-sample containment diagnostic.
  The existing 2D ROOT toys require a separate unfluctuated truth reference or a redesigned
  ensemble before any containment number is valid.
- ⟨|r|⟩ 0.794/0.792 vs √(2/π)=0.798: **RETAIN** as the pull diagnostic it is (correctly labeled).

---

## Workstream 2 — C2ST (unbinned goodness-of-fit)

### Flaw (confirmed, `nd-unfolding/unbinned_gof.py`)
- No cross-fitting: `w_pull` from a single full-sample `omnifold_loop` (:126-130) → each event's
  diagnostic weight comes from a model trained on that event.
- Classifier uses a single 50/50 split (held-out for the classifier, NOT for the weights).
- p-value = analytic Gaussian `z=(acc−0.5)/sqrt(0.25/n_eff)`, `2·sf(|z|)` (:90-93); NO
  permutation/null-pseudoexperiment calibration.
- Quoted: ND_STATUS:25; RUN_LOG:605-609; sec_validation.tex:42-51; sec_summary/sec_execsummary;
  LITERATURE_NOTES:274-277; OPEN_ITEMS:321; VALIDATION_LEDGER:418-421.

### Predeclared contract
- **Diagnostic (retain)**: AUC/accuracy of the discriminator (data-reco vs OmniFold-pushed MC)
  as a *training/descriptive* statistic. Report it with the "descriptive" label.
- **Inferential (repair)**:
  - **Cross-fit** the OmniFold weights: K-fold (K predeclared, e.g. 5); each event's push weight
    comes from an OmniFold model trained on the other K−1 folds. Evaluate the C2ST classifier
    only on held-out data with cross-fitted weights.
  - **Permutation/null calibration**: the test statistic (held-out AUC or accuracy) is calibrated
    against a null built by repeating the COMPLETE pipeline (cross-fit OmniFold + classifier) on
    label-permuted / null pseudoexperiments (data drawn from the OmniFold-pushed MC model, so the
    null hypothesis "data==unfolded MC" holds by construction). p-value = fraction of null
    statistics ≥ observed.
  - Predeclared seeds for folds, permutations, classifier.
- **Cost gate**: each OmniFold on the npz is O(minutes); cross-fit = K runs; null = N_perm full
  pipelines. Pilot with small N_perm (e.g. 20) to estimate cost; scale to N_perm≈200 only if the
  per-pipeline cost justifies it.

### Cost analysis (from existing timing: one OmniFold loop ≈ 10 min, per the bootstrap replicas)
- Cross-fit (K=5 folds, reusing `omnifold_loop`'s `train_frac`/`split_seed`: the held-out fold
  gets weights from a model not trained on it) ≈ 5 loops ≈ 50 min → **AFFORDABLE**.
- Permutation/null-pseudoexperiment calibration repeating the COMPLETE cross-fit pipeline:
  N_perm × K loops. Even N_perm=20 → 100 loops ≈ 17 h; N_perm=200 → ≈ 167 h → **UNAFFORDABLE**.
  A label-permutation that skips re-running OmniFold is NOT a valid calibration (the contract
  requires repeating the complete fitting+testing pipeline), so it is not a shortcut.

### Verdicts
- AUC/accuracy (0.501 unfolded, 0.535 prior): **RETAIN, RELABEL** as a descriptive diagnostic;
  **UPGRADE** to the cross-fitted held-out AUC (removes the weight-leak flaw (i)+(ii)) — affordable.
- `z=1.4, p=0.17, "statistically indistinguishable", PASS`: **REMOVE** the p-value and the
  "statistically indistinguishable" wording — a valid permutation/pseudoexperiment calibration is
  computationally unjustified (100s of full OmniFold pipelines), and the contract forbids
  approximating it. Report instead: cross-fitted held-out AUC (prior→unfolded) as a descriptive
  drop, with an explicit "no calibrated p-value; unbinned GoF is an open problem" limitation.
- Implementation constraint (found 2026-07-16): a CLEAN cross-fit is not achievable without a
  core change — `omnifold_loop`'s `train_frac` redraws the training subset FRESH PER STEP/ITERATION
  (`omnifold_nn_core.py:200`), so every event participates in training at some step; there is no
  fixed held-out fold. A proper cross-fit needs an additive `train_mask` (exclude a fold from ALL
  fits) in the core `omnifold_loop` — but the contract forbids changing the central estimator to
  simplify validation, and the inferential p-value is being REMOVED anyway (permutation null
  unaffordable). So the AUC is retained as a DESCRIPTIVE diagnostic (not inferential), and a clean
  cross-fit is flagged as the prerequisite for any FUTURE inferential revival (deferred — avoids a
  central-code change; no new compute needed for the verdict).

### WS2 = RESOLVED (verdict + wording; no core change, no unaffordable null). Wording for Agent D:
- KEEP: the descriptive C2ST AUC/accuracy — prior AUC ≈0.535 → unfolded AUC ≈0.501 (drop toward 0.5
  shows the unfolding removes the reco data–MC mismatch). Label it explicitly a DESCRIPTIVE unbinned
  diagnostic.
- REMOVE from the note (`sec_validation.tex:42-51`, `sec_summary`, `sec_execsummary`, ND_STATUS,
  RUN_LOG, LEDGER, LITERATURE_NOTES): the analytic p-values (`z=1.4, p=0.17`; `p≈5e-244`) and the
  phrase "statistically indistinguishable". Replace with: "The unbinned classifier two-sample test
  is reported as a descriptive diagnostic (held-out AUC drops from ≈0.535 pre-unfolding to ≈0.501
  post-unfolding); we do not quote a calibrated p-value — a valid null requires re-running the full
  (cross-fitted) OmniFold pipeline per pseudoexperiment (hundreds of unfolds), which is not
  computationally justified, and unbinned GoF calibration remains an open problem (Practical Guide,
  arXiv:2507.09582)."
- `unbinned_gof.py` preserved as-is (the AUC path is the retained diagnostic; its p-value fields are
  deprecated — do not quote).

---

## Workstream 3 — OmniFold/IBU and paper comparison

### Flaw (confirmed)
- Every same-data estimator comparison uses a single-side covariance or a naive sum, never the
  cross term `2·Cov(x_A,x_B)`:
  - `compare_ascencio_fullcov.py:185` `C_tot=C_ours+C_theirs` (independent-sum, no cross).
  - `compare_ascencio_fine.py:92-93` their-cov only (self-labeled "upper bound on tension").
  - `2d-unfolding/compare_to_paper_fullcov.py:107,228-231` single/summed cov (ours-vs-paper).
  - `2d-unfolding/ibu_1d_projection/plot_ibu_1d_proj_vs_omnifold.py` — qualitative overlay, NO
    covariance at all.
- **Scope clarification**: `eavail_generator_significance.py` / `eavailW_covariance.py` (NuWro
  15.6σ, GiBUU 22.4σ) are DATA-vs-THEORY (generators are point predictions) → the measurement
  covariance is the correct single covariance; the cross-covariance flaw does NOT apply. They
  carry a SEPARATE, already-disclosed concern (rank-deficient covariance + truncated-spectral /
  pseudoinverse treatment), out of this workstream's cross-covariance scope.
- Quoted: values.tex:25-26 (χ_paper 3.66, χ_combined 1.481); VALIDATION_LEDGER:309-320 (Ascencio
  1.68/2 p=0.432 PASS), :383-403 (paper); PLOT_GUIDE/AGENTS (IBU agreement).

### Predeclared contract
- **OmniFold vs OUR-OWN IBU** (reproducible → valid method test): run PAIRED replicas — the same
  data/MC Poisson bootstrap draws AND the same systematic universes — through BOTH estimators
  (production OmniFold and a RooUnfold/D'Agostini IBU we control on identical inputs/binning).
  Form `delta_r = x_OF,r − x_IBU,r`; `C_delta = Cov(delta_r)` directly (captures the cancelling
  shared fluctuations). Difference statistic = `delta_bar^T pinv(C_delta) delta_bar` with a
  PREDECLARED rank/pseudoinverse cut; p from the χ² with that rank (or a paired-bootstrap null).
- **OmniFold vs PAPER** (Ruterbories 2106.16210, external IBU-era pipeline): we CANNOT push
  paired replicas through the published pipeline → **do NOT publish a formal ours-vs-paper GoF
  p-value/χ²**. Retain the ratio and a descriptive distance with an explicit limitation
  statement (shared systematics + absent cross-covariance → the summed/single-cov χ² is an
  indicative distance, not a calibrated GoF).
- **Ascencio** (different observable/phase space): keep as the shape/qualitative cross-check it
  already is; the fullcov χ² is descriptive (independent-sum approximation) → limitation label.

### Verdicts
- `IBU and 2D OmniFold agree (method-blind, ≤2.5%)` qualitative overlay: **RETAIN** as
  descriptive; **REPLACE/UPGRADE** with the paired-`C_delta` method-difference statistic (new
  script) for a quantitative OF-vs-IBU test.
- Ours-vs-paper `χ²/ndf 3.66 / combined 1.481`: **RELABEL** as descriptive distance +
  ratio-to-paper with a limitation statement (no paired cross-covariance available); **REMOVE**
  any "GoF p-value / consistent-at-p" framing built on the summed covariance.
- Ascencio `1.68/2, p=0.432, PASS (consistent)`: **RELABEL** as an indicative shape-level
  distance (independent-sum caveat already in the script header); no formal p-value quoted.
- Generator significances (NuWro 15.6σ, GiBUU 22.4σ, …): the data-vs-theory construction does
  not need a method cross-covariance, but the current numbers use the candidate higher-dimensional
  covariance. **GATE** the numerical significances until the selection-complete covariance is
  adopted, then recompute with the declared rank/pseudoinverse treatment.

### WS3 = verdicts + wording DONE; paired-C_delta test is the remaining compute piece.
Wording for Agent D (relabel/remove — no compute needed):
- Ours-vs-paper `χ²/ndf 3.66` / `combined 1.481` (`values.tex:25-26`): **REMOVE** any calibrated
  GoF p-value / "consistent-at-p" framing; **RETAIN** as a descriptive distance + ratio-to-paper
  with: "the published paper (IBU-era) and this OmniFold result share the same MINERvA data and
  flux/detector systematics; without the (unavailable) OmniFold↔paper cross-covariance the summed
  covariance χ² is an indicative distance, not a calibrated goodness-of-fit."
- Ascencio `1.68/2, p=0.432, PASS (consistent)` (`compare_ascencio_fullcov.py`): **RELABEL** as an
  indicative shape-level distance (different observable/phase space + independent-sum covariance);
  drop the formal p-value/"PASS" from quotable status (the script header already flags "indicative,
  not rigorous").
- Generator significances: retain the data-vs-theory method, but withhold the present numerical
  significances until the selection-complete higher-dimensional covariance is adopted and the
  values are recomputed; disclose the declared rank/truncated-spectral/pseudoinverse treatment.
Implementation plan for the valid OmniFold-vs-OUR-IBU test (next compute chunk, 2D where an IBU
already exists — `2d-unfolding/ibu_1d_projection/`):
1. Predeclare seeds/manifest. For r=1..R: draw ONE paired data+MC Poisson bootstrap (and, in a
   second pass, ONE paired systematic universe); push the SAME draw through (a) production OmniFold
   2D and (b) our RooUnfold/D'Agostini IBU on identical inputs/binning.
2. `delta_r = x_OF,r − x_IBU,r`; `C_delta = mat_covariance(delta_r)` (captures cancelling shared
   fluctuations the summed cov misses). Difference statistic `delta_bar^T pinv(C_delta) delta_bar`
   with a PREDECLARED rank cut; p from χ²(rank) or a paired-bootstrap null.
3. Verdict then: quantitative OF-vs-IBU agreement (replaces the current qualitative "method-blind"
   overlay). Cost ≈ 2·R unfolds (R≈100–200) — modest on the 2D chain; pilot R≈20 first.

---

## WS1 pilot result — FPS (2026-07-16, reuse-only; `coverage_valid_nd.py` → `uq_fps/corrected/coverage_valid_fps.json`)
200 `cov_fps` toys, 266 reported bins, fixed closure truth from `of_inputs_fps.npz`, estimator seed 42.
- **Variant B (split-ensemble diagnostic):** containment **68.67%** (calib 100 / eval 100),
  bin-median 69.0% → consistent with the Gaussian reference in this fixed split.
- **Variant A (independent C_stat `uq_cov_stat_fps.root`):** 77.6%, bin-median 88% → the candidate
  stat band **conservatively over-covers** the closure-toy spread (data-stat > MC-closure-stat; expected,
  honest, not a defect).
- **Circular pull diagnostic (the OLD "68.9%" number):** frac 0.689, mean|r| 0.792 ≈ √(2/π)=0.798 —
  reproduced, confirming it is the Gaussianity/pull fraction, NOT frequentist coverage.
- **VERDICT (FPS coverage):** the ~68.7% value survives, but the claim is **REPLACED** with the
  variant-B point value via a non-circular split; the old number is **RELABELED** as a
  pull/Gaussianity diagnostic; variant-A conservative over-coverage is an added honest statement.

## WS1 pilot result — 2D (2026-07-16, reuse-only; withdrawn)
The 200 ROOT closure toys fluctuate both `hXSec2D` and `hTruthXSec2D`: the stored truth varies
in all 205 reported bins (maximum relative range 1.048) because the MC bootstrap multiplies
`w_truth`. Therefore the all-toy mean used in the attempted fixed-split calculation is not an
independent truth reference.
- **Circular pull diagnostic (OLD "68.71%"):** frac **0.6871**, mean|r| 0.794 — EXACT reproduction of the
  quoted number, confirming it is the same-ensemble pull fraction, not coverage.
- **VERDICT (2D coverage):** **WITHDRAW** the attempted 68.80% reinterpretation and quote no
  coverage/containment number. **RELABEL** the old `68.71%`/`⟨|r|⟩ 0.794`/`97.6%` as the
  pull/Gaussianity self-consistency diagnostic. A valid check needs an independently stored
  unfluctuated truth reference (or a redesigned ensemble).

## WS1 = FPS COMPLETE; 2D COVERAGE OPEN. Wording for Agent D:
- FPS split-sample truth-containment is reported as a diagnostic: **68.67%** (disjoint
  calibration/evaluation halves; fixed NPZ truth; nominal 68.27%). No aggregate binomial error
  is quoted because bins within a toy are correlated and the calibration widths are estimated.
- Quote no 2D containment number; the attempted 68.80% used a non-independent all-toy truth mean
  and is withdrawn.
- The former "coverage 68.71%/68.9%, ⟨|r|⟩≈0.79, 97.6% bins ≥65%" is a standardized-pull Gaussianity
  diagnostic (√(2/π)=0.798), retained under that label; it is NOT frequentist coverage.
- FPS extra (honest): the independently-estimated C_stat band conservatively over-covers the closure
  toys (77.6%), consistent with data-stat > MC-closure-stat.

## Status
- 2026-07-16: protocols + verdicts DONE; **WS1 FPS DONE, 2D COVERAGE OPEN** pending an independent
  unfluctuated truth reference or redesigned toys. WS2 verdict DONE: retain the
  existing held-out AUC only as descriptive, remove the analytic p-value, and defer any inferential
  revival until the core supports a fixed excluded fold and a full null calibration. WS3 wording
  DONE; the paired-`C_delta` OF-vs-our-IBU test is the remaining optional publication-grade compute
  piece.
- Preserved FPS covariance workstream (separate) continues autonomously; its coverage toys
  (`cov_fps/`, `fps_extension_validation.py`) are folded into WS1 as the pull diagnostic.
