# Interaction-model studies for MINERvA ME-FHC: synthesis of the Valencia and high-region studies

Research synthesis for Joseph Bailey · 12 October 2026

> **Research extension, not the adopted analysis.** This document and the two studies it summarizes sit outside the
> adopted MINERvA-OmniFold measurement. They change no central value, uncertainty, covariance, gate, ledger row, claim,
> article, note or primer, and they are not a publication uncertainty product. This synthesis authorizes nothing:
> no compute, generation, fit, unfolding, covariance, adoption, external contact, or promotion of study code into the
> production pipeline. Joseph retains every scientific and publication decision.

**Labels.** **[Study]** a result recorded by one of the two frozen studies (quoted, not re-derived); **[Current]** a
current governing record on `main`; **[Proposed]** work this synthesis or a study proposes, none of it authorized;
**[Assumption]** an unmeasured input; **[Unresolved]** an open issue. Numbers are quoted from the linked records; this
synthesis computed nothing.

## 0. Provenance

| Object | Exact identity |
|---|---|
| Base | remote `main` `f30370cdfa868d8b8c31d46fd4d5c8f1d90af856` (re-fetched 2026-10-12) |
| Valencia study | `study/valencia-feasibility-20261011` at head `cbbc29e20d0f9a3098e7290c6146d023d745af9b` (latest corrected commit: terminal disposition, REPAIR.md §R6–R7) |
| High-region study | `study/inelastic-high-region-20261011` at head `caf95593cfaeb1a09d2533dc013048491a3109cc` (latest corrected commit: second close-out and reviewer brief) |
| Both studies' merge base | `3892e769043cddebfd58ec19e1ab1a567eb01784` |
| Predecessor memo | [`MINERVA-MODEL-IMPROVEMENT-MEMO-20261011.md`](MINERVA-MODEL-IMPROVEMENT-MEMO-20261011.md), committed byte-for-byte on this branch; SHA-256 `4f3da639aa816eae1b097b5dd1b44695a218e1ac25213d32b5309053213a4e22`, matching the digest frozen in the Valencia plan before computation |

Both study histories are merged into this research branch unchanged; their directories are byte-identical to the heads
above. Evidence links below are relative to this branch.

- Valencia: [`PLAN.md`](../orchestration/state/valencia-feasibility-20261011/PLAN.md),
  [`REPORT.md`](../orchestration/state/valencia-feasibility-20261011/REPORT.md),
  [`REVIEW.md`](../orchestration/state/valencia-feasibility-20261011/REVIEW.md),
  [`REPAIR.md`](../orchestration/state/valencia-feasibility-20261011/REPAIR.md).
- High-region: [`PLAN.md`](../orchestration/state/inelastic-high-region-20261011/PLAN.md),
  [`REPORT.md`](../orchestration/state/inelastic-high-region-20261011/REPORT.md),
  [`REVIEW.md`](../orchestration/state/inelastic-high-region-20261011/REVIEW.md),
  [`REVIEWER-BRIEF.md`](../orchestration/state/inelastic-high-region-20261011/REVIEWER-BRIEF.md),
  [`literature/LIT-REPORT.md`](../orchestration/state/inelastic-high-region-20261011/literature/LIT-REPORT.md).

**This synthesis's own setup** ([campaign review](../orchestration/CAMPAIGN-REVIEW-20260929.md) §1). Owner: one
documentation session. Decision answered: how to package the two completed studies as a research extension, and which
single next decision they leave for Joseph. Terminal condition: a local commit on this branch. Compute and review
budget: zero; per Joseph's instruction there is no review campaign, so this synthesis is a same-session,
**unreviewed** summary. [`CURRENT_WORK`](../CURRENT_WORK.md) contains no model-study item, so nothing here competes
with the routed queue.

## 1. Bottom line

1. **Neither study establishes an improvement to an interaction model.** Both ended **INCONCLUSIVE** under rules frozen
   before computation. Neither compared a new or corrected model against our data with an uncertainty model. **[Study]**
2. **Valencia.** The corrected (2025) Valencia multinucleon calculation could not be run: there is no public
   implementation. Only its 2020 predecessor was benchmarked. Its tensor contraction is checked, but only under a table
   encoding the authors have not confirmed. The CPU launcher's aggregate guarantee is incomplete. **[Study]**
3. **High region.** After the overall rate is removed, the high-E_avail / high-W corner keeps a residual of
   +0.6% to +6.7%. That residual is comparable to a ±4% recoil-response shift and is localized in no single factor.
   Against GENIE CV, its sign also reverses: −2.7% in the non-overflow cells and +9.4% in the overflow cells.
   Response, estimator and physics explanations
   remain unseparated. **[Study]**
4. **The most specific lead is outside the corner.** GENIE overshoots the data at intermediate W (1.4–1.8 GeV). That
   feature is the largest normalization-independent one, and the one response scale tested barely moves it. It merits
   a comparison with **existing, official** generator configurations, not a new model. **[Proposed]**
5. **Single prioritized next decision (§7):** whether to commission the two independent reviews prepared in
   [`REVIEWER-BRIEF.md`](../orchestration/state/inelastic-high-region-20261011/REVIEWER-BRIEF.md). The first stage
   they would clear is the existing-model intermediate-W comparison. **[Proposed]**

## 2. What each study actually tested

| | Valencia feasibility pilot | High-region inelastic investigation |
|---|---|---|
| Question | Can the corrected Valencia 2p2h/3p3h calculation be implemented and costed for ME-FHC? (memo candidate 1) | After rate, shape and energy coverage are separated, does the high-E_avail / high-W residual point to an inelastic-physics change? |
| What ran | NuWro 25.11.1 with the **2020 predecessor** tables (`mec_kind=6`), ¹²C, MEC only, NuWro transport; an independent tensor integrator; benchmarks frozen before running | Reductions of **existing** products only: the 5D LightGBM central value, Tune v1, GENIE 2.12.10 CV and +MEC, NuWro 21.09, GiBUU 2019; a factor decomposition; one first-order GENIE-tune emulation on existing GENIE 2.12 events; a literature review |
| What did not run | The corrected model (unavailable); detector response; any comparison with data | Generation, detector simulation, fits, unfolding, covariance, any use of the adopted 5D covariance or s5p p-values |
| Resources | 242.8 core-s (0.067 core-h) and 7,900 events, against caps of 10 core-h and 10,000 events; repair under a separate 300 CPU-s allowance | 1,100.9 core-s against a 7,200 core-s cap (900 of it is one crashed run charged its full cap) |
| Review | One fresh read-only review and one correction pass. Then one bounded repair, one targeted review and one correction pass. The 2026-10-12 terminal disposition (REPAIR §R6) was a documentation pass, not reviewed | One fresh read-only review and one correction pass. Then a close-out with one targeted review and one correction pass. The 2026-10-12 second close-out was a documentation pass, not reviewed |
| Verdict | **INCONCLUSIVE**, blocked on one named external input (REPORT §1) | **INCONCLUSIVE** under PLAN §6; GO not reached (REPORT §1) |

All reviewers came from the same model family as the owners. Neither study had independent domain validation.

## 3. Why neither establishes a new model improvement

- **Valencia.** No corrected-model number was computed (REPORT §9). The pilot measured the predecessor's cost,
  support, statistics and bookkeeping, not agreement with data. The predecessor's own benchmarks against its
  publication are **UNVALIDATED** (B1 −5.5%, B2 +16.3%). Its VA-interference part is about 12% low under the declared
  encoding. A corrected-versus-predecessor comparison could therefore not be read at the ≲10% level for
  antineutrino- or VA-sensitive quantities (REPORT §1, §4).
- **High region.** The frozen rule reached neither GO nor NO-GO. The decomposition is a descriptive accounting
  identity, not a causal separation. A partition discrepancy is not established by the available checks (§5). The only
  independently constrained inelastic change found (GENIE v3 `G18_02a_02_11b`) fails the Δ-region check in a
  first-order emulation, and that emulation is explicitly **not** a test of the tune (REPORT §1, §5.2–5.3, §6.1). The
  study recommends against developing or fitting a new inelastic model from this region.
- **Common to both.** No uncertainty construction, significance or calibrated test was used. The memo's own
  conclusion stands: the evidence "does not presently justify inventing a new interaction model"
  ([memo](MINERVA-MODEL-IMPROVEMENT-MEMO-20261011.md), Conclusion).

## 4. Valencia: what was checked, what is missing, what is not guaranteed

**Checked contraction [Study].** The VA-interference sign is now fixed from the authors' conventions: metric,
ε₀₁₂₃ = +1, lepton tensor, V−A current, W = W_s + iW_a. It replaces the earlier choice made from the sign of the
integrated interference. Checks C1–C7 all pass (REPAIR §R1):
- the lepton tensor agrees with an explicit Dirac trace to 4×10⁻¹⁶;
- the code equals the full complex contraction;
- the interference reverses with W12 and with the beam;
- NuWro's transcribed expression agrees to 1.2×10⁻¹⁴;
- no committed number changed (C7).

**The qualification.** The contraction is verified **under the declared table encoding W12 = Im W¹²**. NuWro's code
and GENIE's reader corroborate that encoding; the authors do not state it. B1 and B2 therefore stay UNVALIDATED.
Under that encoding the ν̄/ν ratio is 0.276 against the published 0.225 (REPORT §1, §4; REPAIR §R6).

Further benchmark findings [Study] (REPORT §4):
- B3, B4 (NuWro versus the integrator): PASS. B5: a numerical FAIL that is physically negligible.
- NuWro's structure-function expression has a lepton-mass error worth −0.31% (ν) and −1.1% (ν̄) at 1 GeV.
- 3p3h events lose 2.0–3.2 MeV at the primary vertex.

**Missing corrected-model inputs [Study]** (REPORT §8). The 2025 correction has no tables, code or ancillary files. The
2026 exclusive study ran inside NEUT with no availability statement, and an open NuWro pull request adds empty 2025
files only (REPORT §3). A faithful corrected-model pilot needs:
1. corrected channel-resolved tensor tables (pp, np, pn, 3p3h; ¹²C, ¹⁶O; Re Σ_Δ^eff = 0, −50, +30 ρ/ρ₀ MeV),
   ideally with the 2020 tables regenerated by the same code;
2. the authors' conventions, including confirmation of the W12 encoding;
3. matched ν and ν̄ benchmark values;
4. for E_avail, which depends on the final-state nucleons, the exclusive sampler or distributions sufficient to
   re-fit NuWro's parametrized sampler.

Inclusive tables alone would allow inclusive evaluation and reweighting within NuWro's nucleon model. They would not
give the corrected nucleon sharing that moves E_avail (REPORT §6). An **unsent** draft request is in REPAIR §R7.
Sending it is external contact, which only Joseph can authorize.

**Incomplete launcher guarantee [Study]** (REPAIR §R6; REPORT §2, §9). The repaired `code/pilot_run.py` makes
reservations durable and lock-protected, and it bounds a single-process job while the launcher lives. **Aggregate CPU
enforcement is not fixed:**
- an orphaned job that ignores SIGXCPU is unbounded: check L9b's orphan used 3.07 s against a 2.5 s reservation;
- a launcher killed between `Popen` and the start record leaves no live-orphan refusal (documented, not tested);
- L9b's `pass` and the file's `all_pass` record detection, not enforcement.

`pilot_run.py` is therefore unsuitable wherever a guaranteed aggregate CPU cap is required. A future run would need a
separately validated arrangement; REPAIR §R6 names the guarded scheduler path, which is not validated for this
workload. The completed pilot's measured charges stand, because its runs were sequential and charged as the measured
CPU of waited children.

## 5. High region: rate, shape, overflow, and the unresolved attribution

Region C is E_avail ≥ 0.8 GeV and W ≥ 1.8 GeV. It holds **44.0% of the measured cross section**; it is not a
sparse tail (REPORT §4.1). All ratios are data/prediction.

**Rate [Study]** (REPORT §4.2):
- The overall rate difference dominates: R_total − 1 = 7–15% for the complete-support predictions.
- The published 2D measurement already shows it against Tune v1 (1.118), with no hadronic axis involved.
- GENIE 2.12.10 matches world inclusive σ/E within 1–2% above 9 GeV, so a uniform ~11% inclusive increase at
  5–20 GeV would conflict with NOMAD and MINOS. Those data do not constrain redistributions at fixed σ(E_ν).
- The rate's origin is **unresolved**: flux normalization, efficiency, target count, or the cross section below 5 GeV.
  It is not, by itself, a motivation for an inelastic change.

**Shape [Study]** (REPORT §1, §4.2, §4.4, §5.2):
- The normalization-removed corner residual ρ_C − 1 is +2.85% (GENIE CV), +6.65% (GENIE + MEC) and +0.62% (NuWro).
- The conditionals P(W ≥ 1.8 | A ≥ 0.8) and P(A ≥ 0.8 | W ≥ 1.8) agree with the complete-support predictions within
  3.7%.
- No decomposition factor holds two thirds of the residual. The largest common step is muon shape (+1.7% to +2.9%).
  That step is the published inclusive (p_T, p_∥) shape discrepancy, not a new hadronic-axis finding.
- GENIE + MEC's larger ρ_C comes from MEC strength in the normalizing total; its corner ratio equals GENIE CV's. This
  is a post-hoc observation, outside the rule.

**Overflow [Study]** (REPORT §4.3, §5.2, §5.4):
- Overflow cells (A ≥ 3 or W ≥ 3 GeV) hold 43–50% of each prediction's corner.
- Against GENIE CV, the whole normalization-independent corner surplus is in the overflow cells: the residual is −2.7%
  in the non-overflow cells and +9.4% in the overflow cells.
- In GENIE, 28.9% of the overflow corner and 46% of W ≥ 3 come from E_ν ≥ 20 GeV, so the high-energy flux-tail shape
  competes there.
- The support-complete domain S20 holds only 6.0% of the measured corner. That is a conservative sufficient
  condition, not GiBUU's physical coverage. On its complete support GiBUU is 22% (overall) and 44% (S20 ∩ C) below the
  data, so its deficit is not only the 20 GeV cap.

**Unresolved response and estimator attribution [Unresolved]** (REPORT §5.3, §6.3, §11.1, §11.3):
- *Response.* A coherent ±4% recoil scale moves ρ_C by 3.7–4.0%, the transfer step by ±0.033 and W ≥ 3 by ±0.07.
  This is a **degeneracy in size**. It neither establishes a detector cause nor excludes interaction physics.
- *What the ±4% is.* It is a probe of plausible size, not a calibrated band. No calorimetric response universe
  exists, no response-varied null exists, and species, neutrons and resolution were not varied. A species-dependent
  family is possible only on the simulated-response side, through a new event-loop pass: the MC AnaTuples carry
  per-species branches, but no stored product keeps them.
- *Partition.* **A partition discrepancy is not established by the available checks.** The 5–10% A|t differences at
  W ≥ 1.8 lie inside the scale of the measured departure residuals and prior dependence of the estimators tested
  (REPORT §5.3).
- *Recovery evidence, and what it does not cover.*
  - The historical 5D "injected-W" closure was effectively a **null test**: its bump was centred at W = 0.3 GeV,
    below physical W, with mean factor 1.0000. It supplies no W-shape recovery evidence
    ([`AGENTS.md`](../../AGENTS.md), scalar 4D/5D row; [`ND_OMNIFOLD_STATUS.md`](../../nd-unfolding/ND_OMNIFOLD_STATUS.md),
    5D central cross-section row).
    *Update 2026-10-13:* a corrected, predeclared 5D injected-W closure (bump at W = 1.23 GeV, mean factor 1.053)
    passed narrowly in the W marginal only: ratio 0.180 against a 0.20 threshold, with joint (E_avail, W) cells in the
    peak column 2–9% low ([`VALIDATION_LEDGER.md`](../../VALIDATION_LEDGER.md) VL176;
    [outcome](../orchestration/OUTCOME-20261013-5d-injected-w-closure-pass.md)). It is marginal W-bump recovery
    evidence only and does not bear on the generator-shaped departures below.
  - Later departure/recovery diagnostics exist, **under a different estimator**. In s5n, family `N` (the F2
    LightGBM estimator with the `negweight-refined` background) did not follow a generator-anchored E_avail shape
    departure: median |residual| 9.7%, max 74.1% ([`VALIDATION_LEDGER.md`](../../VALIDATION_LEDGER.md) VL151;
    [s5n outcome](../orchestration/OUTCOME-20260925-s5n-stage1-development-fail.md);
    [`dev_receipt.json`](../orchestration/state/s5n/stage1/dev_receipt.json)). Separately, the s5p data-side prior
    dependence is recorded in VL155 and [`KNOWN_ISSUES.md`](../../KNOWN_ISSUES.md) 77.
  - The proposed estimator R (400 trees / 31 leaves with refinement; the W2B estimator) has recovery measurements
    only for three **other** generator departures (s5e assessment A4: median 6.2/1.9/5.7%, max 31/16/24%;
    VL154).
  - Recovery of the **proposed departures** with the proposed estimator R remains **unmeasured**. These are the
    `02_11b`-type re-partition, the `Fr*` FSI change and the −15% change at 1.4–1.8 GeV (REPORT §11.3).
- *Prior closure allowance withdrawn.* The second close-out withdrew the recorded s5n/s5c biases as a closure
  allowance for new departures. Each departure's own truth recovery must be measured first, with estimator
  attenuation kept separate from response mimicry (REPORT §11.3).

## 6. Why the intermediate-W feature merits an existing-model comparison

The band M = 1.4 ≤ W < 1.8 GeV holds 18.5% of the data (REPORT §4.2, §5.2).

| Prediction | ρ_M | ln ρ, 1.4–1.8 GeV | ln ρ, 1.8–2.2 GeV |
|---|---:|---:|---:|
| Tune v1 (prior) | 0.886 | −0.121 | +0.031 |
| GENIE 2.12.10 CV | 0.823 | **−0.195** | **−0.086** |
| GENIE + MEC | 0.838 | — | — |
| NuWro 21.09 | 0.967 | −0.034 | −0.091 |
| ±4% recoil shift of the same quantity | — | −0.011 / +0.009 | −0.013 / +0.010 |

"—" marks a value the study did not tabulate. ρ_M is from REPORT §4.2; the per-W logarithms and shifts are from §5.2.

The case for a comparison rests on the following points. Points 1–4 are **[Study]** results; point 5 is this
synthesis's argument.

1. **It is the largest normalization-independent feature.** In cell-integrated terms, GENIE's M overshoot is three
   times its corner surplus (REPORT §4.3, §5.2).
2. **The tested response scale barely moves it.** The shift is ±0.01 against −0.195, whereas in the corner it is
   comparable to the residual. This is the only tested robustness: species-dependent response and prior leakage into
   the unfolded (q3, W) were not tested (REPORT §5.2 item 4).
3. **Existing, independently constrained physics speaks to it.** GENIE labels M as 51% RES and 47% "DIS", which
   includes the non-resonant background below W_cut (REPORT §5.4). The GENIE v3 H/D tune changes exactly those
   parameters, R^1π, S_RES and W_cut, from bubble-chamber data rather than from ours (REPORT §6.1). Tune v1 already
   carries a partial non-resonant reduction (×0.57) and overshoots less. That is consistent with the direction but not
   shown to cause it.
4. **No usable prediction exists yet; generation appears feasible at the estimated cost.** No official GENIE v3
   prediction tests the feature for ME-FHC ν on CH without new generation (REPORT §11.6). Ready CVMFS splines exist
   for v3.04.00 `G18_10a_02_11b` and `AR23_20i`, and the existing converter applies. The estimate is a ≤ 0.2 core-h
   pilot, then 1.5–15 core-h per configuration [Assumption]. **GENIE v3 throughput is unmeasured**; the pilot exists
   to measure it (REPORT §8, §11.7; §8 below).
5. **It answers a bounded question with published models.** Does an official modern configuration remove the M
   overshoot without damaging the Δ region or the rate? That question needs no new model, no detector code and no
   unavailable input.

**Limits that travel with it [Study/Unresolved]** (REPORT §6.1, §6.4, §7, §11.6;
[`REVIEWER-BRIEF.md`](../orchestration/state/inelastic-high-region-20261011/REVIEWER-BRIEF.md) §3):
- **Not blind.** M has been inspected, so a comparison is a screen on central values, not falsification. The
  proposed screen, written after the data were seen, flags a configuration that overshoots the Δ bin
  (|ln ρ| > 0.10) or worsens R_total by more than 3%, and passes one that brings |ln ρ_M| below 0.10 without either.
- **The emulation pulls the other way.** The first-order emulation of the tune lowers the Δ-region prediction by 24%,
  where GENIE CV already matches the data. It also turns the corner contrast negative.
- **Complete predictions only.** `G18_10a_02_11b` and `AR23_20i` also change the nuclear, QE/MEC, resonance and FSI
  models, so a difference tests a complete prediction. Attributing it to the inelastic tune needs a same-model control
  pair: `G18_02a_00_000`, with ready splines, against `G18_02a_02_11b`, whose splines must be built.
- **The same-exposure SIS measurement disagrees in direction.** At 1.5 < W < 2 GeV and Q² ≥ 1 GeV², it prefers less
  non-resonant reduction, the opposite direction to `02_11b`. The kinematics differ. The target contrast is CH
  against `02_11b`'s H/D bubble-chamber tuning data; the MINERvA SIS analysis and ours both use the hydrocarbon
  tracker. That sample also shares events with ours (REPORT §6.4).

## 7. The single prioritized next decision

**Decision for Joseph [Proposed]:** whether to commission the two independent reviews specified in
[`REVIEWER-BRIEF.md`](../orchestration/state/inelastic-high-region-20261011/REVIEWER-BRIEF.md), as recommended by
[`REPORT.md`](../orchestration/state/inelastic-high-region-20261011/REPORT.md) §11.7:
- a MINERvA hadronic-response reviewer;
- an independent nuclear-theory/generator reviewer.

They would be asked first to clear, modify or stop V2, the existing-model intermediate-W comparison (§6), and then
the response screening study (V1).

- **Cost:** zero compute. Choosing reviewers outside the project may involve contact, which only Joseph can authorize.
  The brief is prepared and has not been sent.
- **Why first:** every execution path depends on choices the studies could not make independently. These are the
  response sizes and correlations, the meaning of the species branches, which departures are realistic and what
  counts as adequate recovery, and which GENIE comparison can be attributed to what.
- **What it does not do:** a favorable review authorizes nothing. V2, V1 and any calibrated validation would each need
  Joseph's separate authorization.

**Why this ranks above the Valencia author request (this synthesis's judgment) [Proposed].** The Valencia path depends
on a third party. Even a full answer to the inclusive items yields inclusive evaluation and within-NuWro reweighting,
not the corrected nucleon sharing that E_avail needs. Any physics use would still need independent validation
(Valencia REPORT §6, §12). The intermediate-W path uses existing official models and available inputs. The Valencia
request remains a ready, unsent option (REPAIR §R7): it is deferred, not rejected.

## 8. Corrected cost estimates

All figures below are planning estimates: extrapolations or assumptions, not certified bounds. None is authorized.
**Core-hours and billed CPU node-hours are different units and are not added together.**

| Work | Earlier figure | Corrected figure | Unit | Basis |
|---|---|---|---|---|
| Valencia table-route MEC generation, four configurations, 1% per E_avail bin | — (the memo had none for this route) | ≈ 0.25; ≈ 0.74 with a ×3 Kish margin [Assumption] | core-h | measured predecessor throughput, ≤ 0.13 ms/event, extrapolated linearly (Valencia REPORT §7) |
| Matched full-model NuWro baseline | — | 4.7–237 | core-h | 8.5 ms/trial measured; unweighting factor 1–50 assumed (REPORT §7) |
| Faithful corrected **exclusive** generation | 83–833 at an assumed 0.1–1 CPU-s/event (memo, "Follow-up") | **unknown**: no sampler is available | — | REPORT §1, §7 |
| Detector-level predictions | 8,333 per 3 M events at an assumed 10 CPU-s/event (memo) | **unknown**; the assumption stands, unmeasured | core-h | REPORT §7 |
| High-region V1 screening: sensitivity + closure + linear-approximation checks | "≈ 5 CPU node-h" (8 endpoints only; no control, jitters, closure or null) | ≈ 6–9.5 + 5–10 + 8–23 = **≈ 19–42** [Assumption] | billed CPU node-h | extrapolated from W2B's measured 1.898 node-h for 3 endpoints (High-region REPORT §11.5) |
| Calibrated response validation (response-varied nulls) | — | order 10² (~200) [Assumption] | billed CPU node-h | publication packet estimate, unmeasured (REPORT §11.5) |
| V2 GENIE v3 comparison, `G18_10a_02_11b` and `AR23_20i` | — | ≤ 0.2 pilot; then 1.5–15 per configuration [Assumption] | core-h | assumed 5–50 ms/event; the pilot measures it (REPORT §8, §11.7) |
| V2 attribution control | — | +1.5–15 for `G18_02a_00_000`; `G18_02a_02_11b` splines unmeasured | core-h | REPORT §8; REVIEWER-BRIEF §3 |
| Independent reviews (§7) | — | zero compute | — | REPORT §11.7 |

## 9. Historical 2D-status statements, superseded

The memo and the studies were written against the 2D record of 2026-10-09 to 2026-10-11. The 2D record has since
changed. **The frozen study results are not edited.** The table below states what governs now. No number in either
study's verdict depends on the 2D central value or covariance. The 2D measurement enters only as context, through the
published 2D versus Tune v1 comparison.

| Where (historical) | Statement then | Governs now **[Current]** |
|---|---|---|
| Memo, "Repository baseline" and "Uncertainty and inference conditions"; [claims matrix](../publication/CLAIMS-20261005-claim-to-evidence.md) §H, rows L2/L4 (2026-10-09) | The quoted 2D central value is the exact-split scikit-learn estimator with an unpinned seed. The 6.87% budget is a LightGBM seed-42 construction (6.83% against the exact-split denominator). The covariance transfer is unmeasured | Since 2026-10-11 the quoted central value is the LightGBM seed-42 matched universe CV, `E_U` (`4f5a1b6d…`); exact-split is a labelled cross-check ([decision](../publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md); [`VALIDATION_LEDGER.md`](../../VALIDATION_LEDGER.md) VL173; [`KNOWN_ISSUES.md`](../../KNOWN_ISSUES.md) 88, "estimator mismatch resolved"). The seed-1 statistical band / seed-42 systematic pairing (`P07`) is still **unresolved**. Claims-matrix §H predates this decision; on this point the decision record and the ledger govern |
| Memo, same paragraph | 2D median relative budget 6.87% | **6.09%** (VL175, adopted 2026-10-12): Flux with MAT's ν-e+IMD constraint weights and MINOS divided by its own flux (KI 95–96); integral σ 4.23%; combined χ²/ndf 0.994 ([decision](../publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md); [`AGENTS.md`](../../AGENTS.md), 2D uncertainty row). The decision states that the remaining Stage C work (KI 93, KI 94, beam-angle laterals, G1/G2, P07, KI 85) may change it again |
| Memo, same paragraph | The 2D agreement with the published total, about 1.1%, is central-value reproduction, not a calibrated likelihood | The integral ratio for `E_U` is 1.0112. The paper-covariance χ²/ndf is 2.654 for `E_U` and 3.661 for the exact-split cross-check (VL173). The 3.66 is one seed setting: a reseeded exact-split run gives 3.565 (VL174). The memo's caution about likelihoods stands |
| Memo, same paragraph | VL170 statistical coverage untested; VL162 failed | **Unchanged.** VL170 remains the statistical block inside VL175, coverage not re-tested; KI 85 is open and deferred until after the publication package |
| Memo, same paragraph | The May universe path has different truth inputs and a common offset | **Still open**: KI 93; the July sweep is provisional (2026-10-12 decision, "What is not changed") |
| Memo, "Repository baseline" | The latest integration record reports no successful XR scientific fit | XR was integrated on 2026-10-12: central reproductions pass and X1 versus X0 `P09b` fails. VL174 is a measurement taken at integration; no claim, gate or re-quote changed (VL174; [CATALOG](../orchestration/CATALOG.md)) |
| High-region REPORT §4.2 | "this analysis's 2D gives 1.130 (ours/paper 1.011)" against Tune v1 | That figure is the **exact-split cross-check**: it was computed from `fig_arrays.npz` `72394a2b…`, which carries the exact-split curve (2026-10-11 decision, disclosure 6). The quoted `E_U` ratio to the published result is 1.0112 (VL173). Ours/Tune v1 for `E_U` was not recomputed here. The study's ρ(p_T) uses published/Tune v1 only and is unaffected |
| High-region REPORT §9 | 2D statistical band ~0.5% per bin (VL170) | **Unchanged**: VL175 rebuilt only the Flux and MINOS blocks |

The 3D injected-shape closure the memo cites remains valid. For 5D, the "injected-W" closure was effectively a null
test and supplies no W-shape recovery evidence ([`AGENTS.md`](../../AGENTS.md); §5); the high-region close-out
already reads this at `f30370cd`. *Update 2026-10-13:* the corrected 5D test passes narrowly in the W marginal only
(VL176; §5).

## 10. Assumptions and unresolved issues

**Assumptions [Assumption]:**
- Every cost in §8 except the measured throughputs.
- The ×3 Kish margin.
- The NuWro unweighting factor of 1–50.
- GENIE v3 throughput of 5–50 ms/event.
- Throughput transfers from one Apple M1 Pro core to cluster nodes.
- Corrected Valencia tables would share the predecessor's format.
- The ±4% probe and the 4.1% species-weighted figure: size comparisons, not calibrated bands.
- The placeholder response sizes and the placeholder closure interval [0.5, 1.5].

**Unresolved [Unresolved]:**
- The W12 table encoding.
- The corrected-model inputs and exclusive sampler.
- Aggregate CPU enforcement for `pilot_run.py`.
- The origin of the overall rate difference.
- Response versus estimator versus physics in region C.
- Recovery of the proposed departures with the proposed estimator R (§5).
- GENIE v3 generation throughput.
- The net FSI sign for our E_avail (REPORT §6.2).
- Whether G18_10a's `02_11b` inelastic values equal G18_02a's (REVIEWER-BRIEF §3).
- GiBUU above 20 GeV and its two-pion background.
- The high-energy flux-shape uncertainty above 20 GeV.
- Whether the AnaTuple species branches mean what their names say.
- 2D `P07` and KI 85 (§9).

**Proposed, none authorized [Proposed]:**
- The two reviews.
- V2 and its attribution control.
- V1 screening.
- Calibrated validation.
- The Valencia author request.
- Any independent validation of a corrected Valencia implementation.

## 11. What this document is not

- It is not a model improvement, a measurement, or a publication uncertainty.
- It is not a re-evaluation of either study. The verdicts, numbers and frozen rules are quoted, not changed.
- The study code under each study's `code/` directory, including `pilot_run.py`, stays research code. It is not part
  of, or promoted into, the production pipeline.
- It is not an instruction to contact anyone. Both draft communications, REPAIR §R7 and REVIEWER-BRIEF, are unsent.
