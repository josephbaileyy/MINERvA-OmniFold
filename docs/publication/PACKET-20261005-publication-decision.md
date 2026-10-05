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

**Hold the numerical headline now. Recommend a specialist-journal article (Phys. Rev. D class) as the target, and
do not pursue the PRL Letter unless two proposed studies come back favorably.**

The work has genuine methodological novelty. To our knowledge it is the first unbinned unfolding of neutrino data,
and the first with five simultaneous observables, where earlier data measurements reach three (§5.1).
- **The hold** waits on three committed handoffs that do not yet exist (§3).
- **The article** would present the validated unbinned five-observable unfolding, its measured limitations, and
  the calibrated joint generator tests as a conditioned result.
- **The PRL case fails today on its own criteria** (PLAN §4–§5):
  - The principal result rejects five predictions, including MINERvA Tune v1. The published 2D measurement on the
    same data already rejects Tune v1 (χ²/ndf = 33.0), and its abstract says the data "are not well modeled by
    several generator predictions".
  - Nothing yet shows that the joint information adds discrimination.
  - The declared nuisance model omits a recoil-energy response band, and published MINERvA recoil analyses
    include one (§5.4). A common omitted effect would reject every null in the same way, and here every null is
    rejected.

None of this impugns the arithmetic: 712 of 712 recomputed rows agree. It concerns what the arithmetic means.

## 2. Routes considered

| route | requires | assessment |
|---|---|---|
| **A. PRL joint-inference Letter** (PLAN) | Joseph's scope change; AGREE; certified rejections; response adequacy; a joint-information demonstration; importance | **Not recommended now.** It becomes defensible only if W1 shows joint-only discrimination for at least one prediction **and** W2 shows the rejections survive a published-size recoil-response variation. Even then, the predictions are 2016–2021 generator versions, and modern versions are untested. |
| **B. Specialist article (PRD class)** | Joseph's scope change and journal decision; the same handoffs for the inference section | **Recommended.** Its demonstrated content (L1–L12) is a complete, citable methods-and-validation result. The inference enters with its conditions in the body. If the recovery or the verification goes against it, the article survives with that section narrowed. |
| **C. Scientific hold** | — | **The current state of the numerical headline.** It is legitimate and terminal if the recovery leaves rejections uncertified, the verification disagrees, or W2 overturns them. Route B without the inference then remains available. |

**Why B is the strongest defensible route.**
- Its claims are the ones the record already supports.
- Its length lets the conclusion-relevant limitations sit beside the results: the coverage failure, the 74%
  regularization bias at high W, the response condition, and the covariance exception. In a Letter they would be
  compressed into End Matter.
- It needs no new compute to be defensible. W2 is still recommended before the inference is presented as a
  statement about generator physics.

## 3. Dependencies before the numerical headline (re-measured 2026-10-05T23:25Z)

| # | dependency | owner | state now | notification |
|---|---|---|---|---|
| D1 | The extended comparer, independently reviewed, returns AGREE on the unchanged outputs (`b9604502…` etc.), and the joint result is recorded | `gbdt independent` → `gbdt worker` | Extension at `02df81e6` is **not reviewed** ("its review is running"). Nothing recorded. | Both acknowledged; one line to `pub` per event. |
| D2 | Lost-seed recovery: Phase 0, determinism PASS, recovery, resolution (PROCEDURE §5), recompute cross-check (§6) | `gbdt worker`; `gbdt independent` for §6 | Review 3 returned READY WITH CHANGES, nothing blocking. Revision 4 applies it (`61cad10d`, 40 controls). **Nothing submitted.** | As above. A determinism FAIL is to be reported. |
| D3 | Joseph's disposition of how the resolution enters the claims | Joseph | Comes after D2 (`gbdt worker`, 2026-10-05). | `gbdt worker` relays it. |
| D4 | The Stage-7 approved claim text and the four final fields (`CHECKLIST-20261001` §4) | `gbdt worker` | Not started. | As above. |
| D5 | The 2D coverage outcome merged into main (VL168) | 2D lane (`2d`) | Committed on `study/2d-coverage-test-20261005` `80862878`; not on main. | Poll (§8). |

**Fallback poll (read-only), if a notification does not arrive:** handoff §4.

## 4. Demonstrated facts against proposed claims

**Demonstrated** (committed, with an independent check where the governing contract requires one):
- The 2D reproduction to 1.11% (ratio 1.0111) and the 6.87% construction (L1, L2).
- The statistical-band fixed-truth undercoverage of that construction (L3, on its branch).
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

**Proposed, not yet claimable:** I1–I4, the joint incompatibility and its labels (each waits on D1–D4).
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
- MnvTune's failure at ME low recoil. Ascencio's χ² values and our 2D χ²/ndf = 33.0 already show it.

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
- The published 2D comparison already excludes Tune v1 decisively.
- So the new physical information is in the external-generator tests and in the shape tests. There the proxy
  distances are 3–26 null SDs, and NuWro shape (k = 1) is the closest.

A referee will ask what is learned beyond "older generators fail". The honest answer today is a calibrated method
plus a conditioned rejection, which is a specialist-journal contribution.

### 5.3 Value of the joint information

**Not demonstrated.** No matched lower-dimensional test exists. The PLAN requires that the comparative claim be
omitted in that case (§4). Because Tune v1 already fails decisively in 2D, joint-information value could only be
shown by a prediction that a matched marginal test does **not** reject while the joint test does. W1 (§6) measures
exactly that from existing products, with no new pseudo-experiments.

### 5.4 Detector-response adequacy

**Not established, and it may change the conclusion.**
- Amendment 7 states as a claim condition that "there is no recoil-energy-scale band in the analysis's systematic
  set … so hadronic-response completeness is not established".
- The calibration draws the three GEANT hadron-interaction reweights and MinosEfficiency only.
- MINERvA's own published recoil analyses carry a separate **test-beam-derived hadronic energy response**
  uncertainty, in addition to the GEANT reweights. These passages were verified in the source text (literature
  §4):
  - The ME E_avail–q3 measurement (Ascencio *et al.*, PRD 106, 032001): *"The hadronic energy uncertainty varies
    throughout the distribution and rises to 10% at high 0.9 < q3 < 1.2 GeV. The input uncertainty is determined
    from hadron calorimetry data taken with a test beam detector."*
  - Our own 2D reference, 2106.16210, evaluates *"the detector response to hadrons … using shifts determined by in
    situ measurements of a smaller version of the detector in a test beam"*, separately from the GEANT
    inelastic-cross-section variations.

Three reasons the gap may matter:
1. A data/simulation difference in recoil response is common to all five nulls, because they share the detector
   simulation and the unfolding.
2. Such a difference would push every observed statistic upward together, which is the observed pattern.
3. The arithmetic verification cannot detect it ("Agreement verifies the calculation from the products, not the
   calibration", recompute report).

How the PM-1 ruling (`DECISION-20260919…` §4–§5) applies:
- Generic precedent is "supporting context, not proof".
- The ruling forbids inventing a hadronic-energy shift.
- It requires that a concrete identified omission be brought back with its affected observable and a proposed
  remedy. **This packet does that:**
  - **Omission:** a recoil-energy or particle-response variation.
  - **Affected observables:** E_avail, q3 and W, all through q0.
  - **Remedy:** W2 below, with δ taken from the published MINERvA source rather than chosen here.

**Alternative zero-compute route:** send the prepared collaborator question. It is an external message, so it
needs Joseph's authorization. Silence would not settle it.

## 6. Proposed additional scientific work (proposed only; NOT executed)

### W1: matched lower-dimensional comparison (value of joint information)

- **Decision answered:** does the joint 5D test reject any prediction that the same calibrated test, restricted
  to a lower-dimensional projection of the same cells, does not?
- **Quantity:**
  - Projections: P_ptpl (onto p_T × p∥) and P_eW (onto E_avail × W) of the 109 (GiBUU 72) J cells.
  - For each of the 10 tests, the same total and shape statistics on P·F against P·μ_G, with metric P V Pᵀ +
    diag(P Var(μ_G) Pᵀ).
  - The same claim rule (max over the process-shift and M1 variants), against the same frozen calibration
    products with the same per-draw seeds. That gives 20 marginal tests.
- **Inputs:** the frozen production products and design only (`404446eb…`, V `35979ef7…`). No new
  pseudo-experiment, unfold or allocation.
- **Resource cap:** login-node CPU ≤ 2 core-hours. Reads only; writes to a new namespace outside
  `$NS/runs/prod/`. Zero billed node-hours.
- **Criteria, fixed now:**
  - A prediction G shows **joint-only discrimination** if its frozen 5D test is rejected (as recorded after D1–D4)
    and **both** of its marginal tests (total or shape, as matched) have a claim p ≥ 0.05 with determinacy.
  - Otherwise there is no joint-information claim for G.
  - The marginal tests are report-only. They do not enter the Holm family and change no frozen decision.
- **Disclosure:** data-informed (the 5D outcomes were seen). It is reported as a post-hoc secondary analysis.
- **Independent check:** the recompute lane, or a fresh reviewer's own code, reproduces the 20 marginal p-values
  exactly.
- **Terminal rule:**
  - One run. No other projections are selected after the result.
  - If no prediction qualifies, the joint-information claim is omitted permanently for this paper, and route A
    is closed.
  - If at least one qualifies, the claim is stated for those predictions only, with the disclosure.
- **When:** after D1, so that it reads recorded outputs.

### W2: recoil-response sensitivity of the rejections (detector-response adequacy)

- **Decision answered:** does a recoil-energy response variation of the published MINERvA size remove any of the
  10 rejections?
- **Quantity:**
  - Two real-data unfolds (R, 5 iterations, the frozen settings) with the simulation's reconstructed q0 scaled by
    (1 ± δ), with E_avail, q3 and W recomputed from the scaled q0.
  - One nominal re-run as a reproducibility control. It must reproduce `data_b-_j-.npz` (`fb5cc679…`) under the
    procedure's determinism criterion.
  - For each of the 10 tests, T_obs(±δ) against the **frozen** null ensemble, with the claim rule.
  - δ is taken from a published MINERvA response uncertainty, pinned in the authorization rather than chosen by
    this lane. The proposed source is the **hadronic-energy response input of Ascencio *et al.*, PRD 106,
    032001** (the ME E_avail–q3 analysis), which is derived from the test beam of Aliaga *et al.*, NIM A 789, 28.
    Its per-particle input values are not yet read (literature §4, UNVERIFIED).
  - If the source specifies per-particle response, use per-particle scaling where the inputs carry truth-particle
    energy fractions. Otherwise report a single-scale version, labelled as a simplification.
- **Mechanism:** the existing lateral-endpoint machinery (`s5p_numerics.py --construction data`, as for the five
  muon-side bands in `s3-latunfold-tasks.tsv`). The measured cost of ten such endpoints was 1.25 CPU node-hours
  for the unfolds plus 2.18 for the dumps (amendment 6 `budget`).
- **Resource cap:** **4 CPU node-hours** on `m3246`, including one retry. There is no GPU. It sits in a separate
  ledger, not the s5p verification/repair reserve. Wall clock is about one day.
- **Criteria, fixed now:**
  - A rejection is **robust to the recoil variation at δ** if, at both +δ and −δ, its claim p against the frozen
    null ensemble stays below its frozen Holm threshold.
  - Otherwise it is **not robust at δ**.
  - This is a deterministic sensitivity, not a calibrated nuisance. It moves the data, not the null, so "robust"
    means "not removed by this variation". It does not mean "response model complete".
- **Terminal rule:**
  - One δ and one run.
  - If any rejection is not robust, every claim about that prediction is narrowed to "not robust to a recoil
    response variation of the published size", and route A is closed.
  - If all are robust, the condition is reported as tested at δ, and the amendment-7 completeness caveat still
    stands.
  - No second δ is chosen after the result.
- **Independent check:** the recompute lane's evaluator on the two shifted products.
- **Constraint:** this needs Joseph's explicit authorization. It is new cluster compute, and the PM-1 ruling
  forbids inventing a shift, so the authorization must name the published source of δ.

**Not proposed:** tests of modern generator versions; a calibrated re-production with a response band (~200 node-h,
like s5p itself); any measurement-successor work. These belong to the separate successor proposal and are not
needed for route B.

## 7. Exact approval wording requested (one batch)

Joseph, please answer with any subset. Each item is independent.

> **(1) Scope and journal.** "For publication, the target is a specialist-journal article (PRD class), not a
> PRL Letter. Completion of the separate full measurement uncertainty product is NOT a prerequisite for this
> article. The measurement branch remains NOT ADMITTED / NOT READY, and every artifact grade and exception
> condition is preserved. The 2026-09-01 retention of uncertainties before publication is modified for this
> article only."

> **(2) Hold.** "The numerical headline stays on hold until the joint result is recorded after AGREE, the
> lost-seed resolution and its independent cross-check are committed, and I have disposed of how the resolution
> enters the claims."

> **(3) W1.** "Authorize W1 as specified in PACKET-20261005 §6: login-node only, ≤ 2 core-hours, report-only,
> after D1."

> **(4) W2.** "Authorize W2 as specified in PACKET-20261005 §6: ≤ 4 CPU node-hours on m3246, separate ledger,
> δ = the hadronic-energy response input of Ascencio et al., PRD 106, 032001 (test beam: Aliaga et al., NIM A 789,
> 28), as read from that source and recorded before the run, one run, report-only."

> **(5) Collaborator question (optional alternative or complement to W2).** "Send
> QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md to <named collaborator>."

> **(6) Manuscript work.** "After (1), the publication lane may edit the paper sources for the article in its own
> branch, coordinated with the note owners, without changing the numerical headline before (2) is met."

If (1) is declined, uncertainties remain a publication prerequisite, and the outcome is a **scientific hold** for
every route. That hold is legitimate and terminal for this preparation effort.

## 8. Review

One fresh independent read-only review: `REVIEW-20261005-independent.md`. Its findings and their resolution are
recorded there.
