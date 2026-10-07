# Publication decision packet: MINERvA-OmniFold (2026-10-05)

**CITABLE FOR:**
- the recommended publication route and why;
- the separation between demonstrated facts and proposed claims;
- the dependencies that must land before the numerical headline is finalized;
- two proposed, unexecuted scientific studies, each with its quantity, cap, criteria and terminal rule;
- the exact approval wording requested from Joseph.

**NOT CITABLE FOR:**
- any physics result, grade, adoption or readiness;
- authorization of compute, release, deposit, tag, external message or submission.

Nothing in this packet was executed beyond reading committed products and the literature.

**Owner:** publication-preparation lane (`pub`), worktree `MINERvA-OmniFold-publication-20261005`, branch
`docs/publication-decision-20261005`, based on `origin/main` `61cad10d` (measured 2026-10-05T23:25Z).
**Authority:** Joseph's 2026-10-05 instruction. It authorizes this packet, routine local analysis of existing
products, literature research and one fresh independent read-only review. It authorizes no new cluster compute,
adoption, deposit, tag, external message or submission.
**Governing plan:** `PLAN-20261005-prl-joint-inference-publication.md` (copied here; sha256 `c8b950d6…`).
**Companion files:**
- `CLAIMS-20261005-claim-to-evidence.md`
- `LITERATURE-20261005-comparison.md`
- `OUTLINE-20261005-manuscript.md`
- `RELEASE-INVENTORY-20261005.md`
- `REVIEW-20261005-independent.md`
- `HANDOFF-20261005-publication-preparation.md`

**Campaign-review choice (CAMPAIGN-REVIEW-20260929 §1):**
- **Decision answered:** which publication route the evidence supports, and what blocks it.
- **Useful terminal results:** a recommendation, or a scientific hold.
- **Owner and reviewer:** this lane owns the packet. One fresh read-only reviewer (Opus 5.5 subagent in an
  isolated worktree) reviews it. Astra High was not available in this session.
- **Budget:** at most two review/repair cycles and no compute.

---

## 1. Recommendation in one paragraph

**Hold the numerical headline now. Recommend a specialist-journal article (Phys. Rev. D class) as the target. Do
not pursue the PRL Letter: the two proposed studies (W1, W2) are necessary to reopen it, but not sufficient.**

The work has genuine methodological novelty. To our knowledge it is the first unbinned unfolding of neutrino data,
and the first with five simultaneous observables, where earlier data measurements reach three (§5.1). The five are
correlated: E_avail, q3 and W share the recoil energy.
- **The hold** waits on three committed handoffs that do not yet exist (§3).
- **The article** would present the validated unbinned five-observable unfolding, its measured limitations, and
  the calibrated joint generator tests as a conditioned result.
- **The PRL case fails today on its own criteria** (PLAN §4–§5):
  - The recorded result (`9b26b8c3`, after AGREE) rejects all 10 H0(G) tests, including MINERvA Tune v1. **No
    rejection is certified against the lost draws**; the resolution (D2) is in progress.
  - The published 2D measurement on the same data already disfavours these generator families strongly. Its
    Table I gives χ² over 205 bins of 6786 for Tune v1, 8241 for GENIE 2.12.6, 5800 for GiBUU 2019 (the same
    version as our null) and 3789–5151 for NuWro; our recomputation for Tune v1 is χ²/ndf = 33.04. Its abstract
    says the data "are not well modeled by several generator predictions".
  - Nothing yet shows that the joint information adds discrimination.
  - The declared nuisance model omits a recoil-energy response band, and published MINERvA recoil analyses
    include one (§5.4). A common omitted effect **could** move every null's statistic. The published muon-kinematics
    comparison, which is largely insensitive to hadronic response, independently disfavours the same families.
    So the concern bears chiefly on what the five-dimensional **shape** information adds along the hadronic axes,
    not on whether these generators fail at all.

None of this impugns the arithmetic: 712 of 712 recomputed rows agree (comparer verdict INCOMPLETE, pending its
extension). It concerns what the arithmetic means.

## 2. Routes considered

| route | requires | assessment |
|---|---|---|
| **A. PRL joint-inference Letter** (PLAN) | Joseph's scope change; AGREE; certified rejections; response adequacy; a joint-information demonstration; importance | **Not recommended.** W1 and W2 are necessary for this route, but not sufficient. W1 can show only discrimination relative to matched **coarse** projections, not value beyond the published 205-bin 2D measurement, which already disfavours every family tested. A PRL case would also need an importance argument that the evidence does not now supply. The predictions are 2016–2021 generator versions, and modern versions are untested. Reopening this route is Joseph's call after W1 and W2, not an automatic consequence of them. |
| **B. Specialist article (PRD class)** | Joseph's scope change and journal decision; the same handoffs for the inference section | **Recommended.** Its demonstrated content (L1–L12) is a complete, citable methods-and-validation result. The inference enters with its conditions in the body. If the recovery or the verification goes against it, the article survives with that section narrowed. |
| **C. Scientific hold** | — | **The current state of the numerical headline.** It is legitimate and terminal if the recovery leaves rejections uncertified, the verification disagrees, or W2 overturns them. Route B without the inference then remains available. |

**Why B is the strongest defensible route.**
- Its claims are the ones the record already supports.
- Its length lets the conclusion-relevant limitations sit beside the results: the coverage failure, the 74%
  regularization bias at high W, the response condition, and the covariance exception. In a Letter they would be
  compressed into End Matter.
- It needs no new compute to be defensible. W2 is still recommended before the inference's **shape** results are
  presented as a statement about generator physics along the hadronic axes.

## 3. Dependencies before the numerical headline (re-measured 2026-10-05T23:42Z at `origin/main` `87256e75`)

| # | dependency | owner | state now | notification |
|---|---|---|---|---|
| D1 | The extended comparer, independently reviewed, returns AGREE on the unchanged outputs (`b9604502…` etc.), and the joint result is recorded | `gbdt independent` → `gbdt worker` | **DONE.** The extension review is APPROVE; the compare gives **AGREE, 1379/1379 rows, 0 discrepancies** (`466b427b`, recompute branch, report §8). The joint result is **recorded** on main: `RECORD-20261005-s5p-joint-5d-inference-result.md` (`9b26b8c3`). All ten are rejected and robust (κ = 3), with missing-seed status "can change", not certified. Both were verified from the committed files at 2026-10-05T23:53Z. | Both acknowledged; one line to `pub` per event. |
| D2 | Lost-seed recovery: determinism PASS, recovery, resolution (PROCEDURE §5), recompute cross-check (§6) | `gbdt worker`; `gbdt independent` for §6 | Procedure revision 5 (`51648245`, 41 controls). **Phase 0 PASS** (`15a32b0e`). **Determinism array 59397841 submitted** (`87256e75`, 4.0 node-h reserved from verification_repair). Recovery not yet submitted. | As above. A determinism FAIL is to be reported. |
| D3 | Joseph's disposition of how the resolution enters the claims | Joseph | Comes after D2 (`gbdt worker`, 2026-10-05). | `gbdt worker` relays it. |
| D4 | The Stage-7 approved claim text and the four final fields (`CHECKLIST-20261001` §4) | `gbdt worker` | Not started. | As above. |
| D5 | The 2D coverage outcome merged into main (VL168) | 2D lane (`2d`) | Committed on `study/2d-coverage-test-20261005` `80862878`; not on main. | Poll (§8). |

**Fallback poll (read-only), if a notification does not arrive:** handoff §4.

## 4. Demonstrated facts against proposed claims

**Demonstrated** (committed, with an independent check where the governing contract requires one):
- The 2D reproduction to 1.11% (ratio 1.0111) and the 6.87% construction (L1, L2).
- The fixed-truth undercoverage of the 2D **statistical** band, VL162 (L3, on its branch). The combined 6.87%
  construction's coverage remains untested.
- The 3D–5D anchors and closures (L5).
- The measured background and regularization biases (L6).
- The low-E_avail deficit and the 2p2h fill (L7).
- The descriptive high-E_avail/high-W central-value excess over Tune v1 (L8, no significance).
- The external-generator shortfalls (L9).
- The covariance adopted under exception, with s_proj = 6.145% against the 5% bound (L10).
- s5p **production reached terminal**, and its four frozen outputs exist with digests.
- The independent recompute reproduces 712/712 compared rows with 0 discrepancies, under a comparer verdict of
  INCOMPLETE.
- The missing-seed sensitivity reads **"can change" for all 10 tests**.

**Recorded but not yet claimable as a headline:** I1–I4, the joint incompatibility and its labels. They have been
recorded since `9b26b8c3`, with the missing-seed status "can change". The headline still waits on D2–D4.
**Not supported, to be omitted unless studied:**
- I5, joint-information value (W1);
- I6, localization or mechanism;
- I7, response robustness (W2);
- I8, priority;
- I9, a complete measurement.

## 5. The four questions asked

### 5.1 Novelty

See `LITERATURE-20261005-comparison.md` §3. Within the searched literature (arXiv and web indexes):

**Real, defensible novelty (methodological):**
- "To our knowledge, the first unbinned unfolding of neutrino-scattering **data**." The only neutrino OmniFold
  paper (PRD 112, 012008, 2025) is a T2K **simulation** study, so a "first use in neutrino physics" claim stays
  excluded.
- Five simultaneous observables, where the highest dimensionality found on unfolded neutrino data is three
  (MINERvA QE-like 2022, MicroBooNE 2025, NOvA 2026). This needs the correlated-observables caveat.
- A full-chain, calibrated joint test with multiplicity control, unlike the covariance-χ² comparisons used
  elsewhere. Describe it without "first".

**Not novel:**
- Generator failure on these data. 2106.16210 already reports it.
- MnvTune's failure on these data: at ME low recoil (Ascencio's χ² over 44 bins) and across the muon-kinematics
  plane (2106.16210 Table I; our recomputation χ²/ndf = 33.04).
- The other families' failure in 2D. Table I disfavours GENIE 2.12.6, GiBUU 2019 and NuWro comparably strongly:
  χ²/ndf 40.2, 28.3 and 18.5–25.1 respectively, against 33.1 for Tune v1.

**Importance comparator:** the collider OmniFold PRLs (H1 2022, ATLAS 2024) each delivered a measurement with full
uncertainties. This work's 5D measurement has **no qualified uncertainty**, because the measurement branch was not
admitted. That gap, not a lack of methodological novelty, is what weakens a PRL case.

### 5.2 Physical consequence

What the frozen outputs would establish, if D1–D4 land favorably:
- The ME-FHC inclusive data are jointly incompatible with each of five specific predictions on a 109-cell
  five-observable grid, under the declared null and nuisance model.

What they would not establish:
- which kinematic region or mechanism is responsible (a global statistic);
- anything about current generator versions;
- a measurement.

The predictions tested are GENIE 2.12.10 (CV and MEC), MINERvA Tune v1 (GENIE 2.12.6-based), NuWro 21.09 and
GiBUU 2019.

The consequence is limited further by the shape of the evidence (claims table §C, descriptive):
- The tuned analysis simulation is about 200 null SDs from the data in the total statistic and about 40 in shape.
- The published 2D comparison already disfavours Tune v1, GENIE 2.12.6, GiBUU 2019 and NuWro strongly (§1).
- So any new physical information is in the five-dimensional **shape** tests. There the proxy distances are
  2.8–6.1 null SDs for the external nulls, and NuWro shape (k = 1) is the closest.

A referee will ask what is learned beyond "older generators fail". The honest answer today is a calibrated method
plus a conditioned rejection, which is a specialist-journal contribution.

### 5.3 Value of the joint information

**Not demonstrated.** No matched lower-dimensional test exists, and the PLAN requires that the comparative claim
then be omitted (§4). The published 205-bin 2D comparison already disfavours every family tested, so
joint-information value **against published lower-dimensional results** is not on offer from these predictions.

W1 (§6) answers a narrower question from existing products: does the 5D test reject anything that the same
calibrated test on matched 3×3 **coarse** projections of the same cells does not? A positive W1 supports only that
scoped statement.

### 5.4 Detector-response adequacy

**Not established, and it may change the conclusion.**
- Amendment 7 states as a claim condition that "there is no recoil-energy-scale band in the analysis's systematic
  set … so hadronic-response completeness is not established".
- The calibration draws one flux universe, all 34 interaction-model bands, the three GEANT hadron-interaction
  reweights, MinosEfficiency, and the five muon/beam lateral bands through a linear surrogate. **None of these is a
  recoil or calorimetric response band.**
- MINERvA's own published recoil analyses carry a separate **test-beam-derived hadronic energy response**
  uncertainty, in addition to the GEANT reweights. These passages were verified in the source text (literature
  §4):
  - The ME E_avail–q3 measurement (Ascencio *et al.*, PRD 106, 032001): *"The hadronic energy uncertainty varies
    throughout the distribution and rises to 10% at high 0.9 < q3 < 1.2 GeV. The input uncertainty is determined
    from hadron calorimetry data taken with a test beam detector."*
  - Our own 2D reference, 2106.16210, evaluates *"the detector response to hadrons … using shifts determined by in
    situ measurements of a smaller version of the detector in a test beam"*, separately from the GEANT
    inelastic-cross-section variations.

Why the gap may matter, and what bounds it:
1. A data/simulation difference in recoil response is common to all five nulls, because they share the detector
   simulation and the unfolding.
2. It **could** move every observed statistic, but not necessarily upward. To first order,
   ΔT ≈ 2dᵀW⁻¹(F−μ) + dᵀW⁻¹d, and the first term's sign depends on how the shift d aligns with each residual.
3. The arithmetic verification cannot detect it ("Agreement verifies the calculation from the products, not the
   calibration", recompute report).
4. **Partial counter-evidence:** the published muon-kinematics comparison (2106.16210 Table I), which includes its
   own hadronic-response systematics, independently disfavours the same families. The concern is therefore chiefly
   about the five-dimensional **shape** conclusions along E_avail, q3 and W. It is a real gap, but not an
   undecidable one.

How the PM-1 ruling (`DECISION-20260919…` §4–§5) applies:
- Generic precedent is "supporting context, not proof".
- The ruling forbids inventing a hadronic-energy shift.
- It requires that a concrete identified omission be brought back with its affected observable and a proposed
  remedy. **This packet does that:**
  - **Omission:** a recoil-energy or particle-response variation.
  - **Affected observables:** E_avail, the primary calorimetric quantity, and q3 and W through the recoil energy.
  - **Remedy:** W2 below, with a δ taken from a published MINERvA number (§6), which Joseph is asked to accept
    or replace.

**Alternative zero-compute route:** send the prepared collaborator question. It is an external message, so it
needs Joseph's authorization. Silence would not settle it.

## 6. Proposed additional scientific work (proposed only; NOT executed)

### W1: matched coarse-projection comparison (value of joint information, scoped)

- **Decision answered:** does the 5D test reject any prediction that the same calibrated test, restricted to
  matched 3×3 coarse projections of the same J cells, does not? This is **not** a comparison with published
  lower-dimensional measurements (§5.3).
- **Quantity:**
  - Projections: P_ptpl onto (p_T, p∥) and P_eW onto (E_avail, W), each a 9×109 sum over the dropped axes of the
    supported J cells (9×72 for GiBUU).
  - For each of the 10 tests, the same total or shape statistic, with total matched to total and shape to shape.
    It is computed on P·F against P·μ_G, with metric P V Pᵀ + diag(P Var(μ_G) Pᵀ).
  - **Variants:** each 109-dimensional variant vector is projected, never rebuilt in the projected metric. They
    are the process-shift vector S(c) for c ∈ {0, ½, 1}, from the frozen `s5p_joint.shift_vector` in 109
    dimensions, and the M1 shifts ±2 δ_M1. Under D2 reading (b), the frozen S is projected. Under reading (a), S is
    recomputed by the frozen `shift_vector` on the union ensemble, as the procedure does, and then projected.
  - The claim p is the largest over the projected variants, with the per-draw seeds of the frozen products. That
    gives 20 marginal tests (10 tests × 2 projections).
- **Inputs:** the frozen production products and design only (`404446eb…`, V `35979ef7…`), plus the recovered
  products from D2 under its own report-only labelling. No new pseudo-experiment, unfold or allocation.
- **Resource cap:** login-node CPU ≤ 2 core-hours. Reads only; writes to a new namespace outside
  `$NS/runs/prod/`. Zero billed node-hours.
- **Criteria, fixed now:**
  - For a prediction G and a test type t (total or shape), the 5D test shows **discrimination beyond the matched
    coarse projections** if three things hold:
    - its 5D t-test is rejected as recorded after D1–D3;
    - **both** of its projected t-tests (P_ptpl and P_eW) have claim p ≥ 0.05;
    - that holds under the D2-resolved ensemble, both (a) the union and (b) the frozen-S reading.
  - Otherwise there is no such claim for (G, t).
  - The marginal tests are report-only. They do not enter the Holm family and change no frozen decision.
- **Disclosure:** data-informed (the 5D outcomes were seen). It is reported as a post-hoc secondary analysis.
- **Independent check:** the recompute lane, or a fresh reviewer's own code, reproduces the 20 marginal p-values
  exactly.
- **Terminal rule:**
  - One run. No other projections are selected after the result.
  - If no (G, t) qualifies, the joint-information claim is omitted permanently for this paper.
  - If any qualifies, the scoped claim is stated for those (G, t) only, with the disclosure.
- **When:** it may run after D1 and D2, so that it reads recorded outputs and a resolved missing-seed state. Its
  criterion is applied only after D3, the disposition of the resolution.

### W2: recoil-response sensitivity of the rejections (detector-response adequacy), in two gated steps

- **Decision answered:** does a recoil-response variation of a published MINERvA size remove any of the 10
  rejections?
- **δ, proposed for Joseph to accept or replace:**
  - δ = **0.04**, applied as a single coherent scale on the simulation's reconstructed calorimetric recoil energy.
  - **Source:** Aliaga *et al.*, NIM A 789, 28 (2015), arXiv:1501.06431. Its abstract (verified via the arXiv API)
    says the test-beam data agree with the Geant4 simulation of the calorimetric response "with agreements better
    than 4%".
  - **Status of this number:** it is an overall statement of data/simulation agreement, not a stated uncertainty.
    It covers test-beam protons, pions and electrons at 0.35–2.0 GeV/c. Neutrons and higher-momentum recoil
    particles, which matter at high W, lie outside that range. It is used here as a sensitivity size, and it is
    **not** MINERvA's per-particle response prescription. Ascencio *et al.* applies a
    test-beam-derived input whose values that paper does not state, so the per-particle values remain unread.
  - **Why single-scale:** the existing dumps carry (p_T, p∥, E_avail, q3, W) only, with no q0 and no
    truth-particle energy fractions, so per-particle scaling cannot be done from them.
  - Accepting this δ is Joseph's ruling under PM-1, which forbids the lane from inventing a shift.
- **W2a: implementation, review and costing.**
  - **Code:** a new recoil-response universe in the event loop (`runEventLoopOmniFold.cpp`). It scales the
    reconstructed calorimetric recoil by (1 ± δ) per simulated event, then derives E_avail, q0, q3 and W from the
    scaled recoil, coherently for signal and background. The lateral dump and real-data unfold
    (`s5p_input_dumps.py lateral`; `s5p_numerics.py --construction data`) are reused unchanged.
  - **Gate:** the code gets one independent read-only review before any production use.
  - **Cost measurement:** δ = 0 and ±δ on one playlist.
  - **Cap:** ≤ 1 CPU node-hour.
  - **Output:** a measured per-playlist cost for W2b.
- **W2b: the run**, approved separately with W2a's measured cost.
  - Two full real-data unfolds (R, 5 iterations, frozen settings) at ±δ, plus one δ = 0 control.
  - **Control criterion:** the δ = 0 product reproduces `data_b-_j-.npz` (`fb5cc679…`) bitwise. If the code path
    legitimately differs, the control instead passes only if both of these hold:
    - every one of the 10 claim p-values at δ = 0 lies within the range that `joint-evaluate.json`
      `observed_jitter_p` records for that test over the 20 committed real-data rounding jitters. The range is a
      single value for 9 tests and 2/1752–3/1752 for NuWro shape;
    - the Holm decisions at δ = 0 equal the frozen decisions.

    A per-cell envelope is not used: a correct product would fail it by chance. A control FAIL stops W2b and is
    reported.
  - **Hard ceiling:** 8 CPU node-hours for W2a and W2b together, on `m3246`, in a separate ledger outside the s5p
    reserve.
  - The amendment-6 basis of 1.25 + 2.18 node-hours excludes the event-loop step, so it is not the estimate.
- **Criteria, fixed now:**
  - Compute T_obs(±δ) for all 10 tests against the **frozen** null ensembles with the claim rule, then re-run
    `s5p_inference.holm_determined` on each sign's 10 claim p-values.
  - A rejection is **robust to the recoil variation at δ** if it is rejected under both signs. Otherwise it is
    **not robust at δ**.
  - **Limitation, stated with the result:** the variation moves the data and not the null. For strongly
    non-central nulls (λ = 318–6,344) the size of that approximation is unmeasured. "Robust" means "not removed by
    this data-side variation". It does not mean "response model complete".
- **Terminal rule:**
  - One δ and one run of W2b.
  - Any non-robust rejection narrows every claim about that prediction to "not robust to a 4% recoil-response
    variation".
  - If all are robust, the condition is reported as tested at δ, and the amendment-7 completeness caveat stands.
  - No second δ after the result.
  - If W2a's review or cost gate fails, W2 stops, and the response condition is stated without a sensitivity.
- **Independent check:** the recompute lane's evaluator on the two shifted products.
- **When:** after D2, so that the frozen null ensembles and their missing-seed state are final.

**Not proposed:** tests of modern generator versions; a calibrated re-production with a response band (~200 node-h,
like s5p itself); any measurement-successor work. These belong to the separate successor proposal and are not
needed for route B.

## 7. Exact approval wording requested (one batch)

Joseph, please answer with any subset. Each item is independent.

> **(1) Scope and journal.** "For publication, the target is a specialist-journal article (PRD class), not a
> PRL Letter. Completion of the separate full measurement uncertainty product is NOT a prerequisite for this
> article. The s5p measurement branch remains NOT ADMITTED, and s5p's `publication_readiness` stays NOT READY as
> recorded under its own authorization. That authorization's "publication completion requires the joint result and
> all retained claims to qualify" continues to govern s5p's own completion, not this article. This article's
> readiness is a separate record. Every artifact grade and exception condition is preserved. The 2026-09-01
> retention of uncertainties before publication is modified for this article only."

> **(2) Hold.** "The numerical headline stays on hold until five things are done: the joint result is recorded
> after AGREE; the lost-seed resolution and its independent cross-check are committed; I have disposed of how the
> resolution enters the claims; the Stage-7 claim wording and final fields are committed; and the 2D coverage
> outcome is on main."

> **(3) W1.** "Authorize W1 as specified in PACKET-20261005 §6: login-node only, ≤ 2 core-hours, report-only,
> after D1 and D2."

> **(4) W2.** "Accept δ = 0.04 as a single coherent recoil-response scale (source: Aliaga et al., NIM A 789,
> 28, 'agreements better than 4%'), as a labelled simplification. Authorize W2a as specified in PACKET-20261005
> §6: code, one independent review, a one-playlist cost measurement, ≤ 1 CPU node-hour on m3246, separate ledger.
> W2b needs my separate approval at W2a's measured cost, within an 8 CPU node-hour ceiling for W2a and W2b
> together."

> **(5) Collaborator question (optional alternative or complement to W2).** "Send
> QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md to <named collaborator>."

> **(6) Manuscript work.** "After (1), the publication lane may edit the paper sources for the article in its own
> branch, coordinated with the note owners, without changing the numerical headline before (2) is met."

If (1) is declined, uncertainties remain a publication prerequisite, and the outcome is a **scientific hold** for
every route. That hold is legitimate and terminal for this preparation effort.

Items (3) and (4) are recommended but not required for route B. Without them, the article omits the
joint-information claim and states the response condition without a sensitivity.

## 8. Review

One fresh independent read-only review, of `d9a75393`: ACCEPT WITH CHANGES (1 blocking, 6 should-fix, 12 notes).
Every finding was resolved in repair cycle 1. The cycle-2 focused re-check of `407c351f` returned ACCEPT WITH
CHANGES (1 should-fix, 5 notes); all were applied. Two cycles is the budget, so no further review is planned. See
`REVIEW-20261005-independent.md`.
