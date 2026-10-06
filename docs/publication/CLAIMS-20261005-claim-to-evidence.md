# Claim-to-evidence table for the publication decision (2026-10-05)

**CITABLE FOR:** which candidate publication claims rest on committed evidence, which are conditional on named
pending handoffs, and which are unsupported and must be omitted or separately studied.
**NOT CITABLE FOR:** any physics number. Every number below is transcribed from the routed record, which remains
the authority. The table records, adopts and grades nothing, and changes no frozen claim.

**Baseline:** `origin/main` `61cad10d` (measured 2026-10-05T23:25Z; it was `895a622c` when this lane started, and only the recovery procedure changed in between). The 2D
coverage outcome is read from branch `study/2d-coverage-test-20261005` at `80862878`, which is **not yet merged into
main**. The independent recompute is read from branch `s5p-parallel-recompute-20260928` at `02df81e6`.

**Status vocabulary:**
- **DEMONSTRATED**: committed evidence with its required ledger, status and independent check, quotable within the
  stated scope.
- **CONDITIONAL**: the products exist, but a named required handoff is pending, so the claim cannot be quoted yet.
- **UNSUPPORTED**: no evidence would carry the claim as worded. Omit it, narrow it, or run the proposed study
  (packet §6).
- **STALE**: deliverable text that committed evidence now contradicts.

## A. Candidate inference claims (the proposed Letter headline)

The test family is amendment 7 `claims.family`: for each of five predictions G, H0(G) is the **simple fine-grid
hybrid null**. The true cross section equals G on the fine 5D grid, with MnvTune v1's shapes and G's finite-MC
fine-cell fluctuations below it. There are two tests per G (total and shape-only), 10 in all, under Holm with
determinacy at α = 0.05. The domain is the 109 supported J cells, and for GiBUU the 72 with p∥ < 6 GeV/c. The
estimator is candidate **R** (5 iterations), which is **not** the production central-value estimator in the current
Letter.

| # | Claim as it would be worded | Status | Evidence now | What it waits on / why |
|---|---|---|---|---|
| I1 | Under the declared calibration model, the data are jointly incompatible with each of the five predictions (MnvTune v1, GENIE 2.12.10 CV, GENIE 2.12.10 + MEC, NuWro 21.09, GiBUU 2019); all 10 tests are rejected at familywise α = 0.05. | **RECORDED; not certified** | **Recorded** in `RECORD-20261005-s5p-joint-5d-inference-result.md` (`9b26b8c3`, origin/main): all 10 rejected, from `joint-evaluate.json` `b9604502…`. The independent recompute's extended comparer is **AGREE, 1379/1379, 0 discrepancies** (`466b427b`, report §8; extension review APPROVE). | (1) DONE. (2) Lost-seed resolution, in progress. **Today no rejection is certified, and every one reads "can change"**: under `worst_all_missing`, p = 0.025–0.041 and none is rejected (`missing-sensitivity.json` `f48e16ef…`). (3) Joseph's disposition of how that resolution enters the claims. (4) The Stage-7 approved wording (`CHECKLIST-20261001` §4). |
| I2 | Monte Carlo p-values: (k + 1)/(B + 1), with k = 0 for 9 tests (B = 1343–1751) and k = 1 for NuWro shape (p = 2/1752). | **RECORDED; not certified** | Record `9b26b8c3` §2; the recompute agrees (AGREE). | Same as I1. Report with the finite resolution and the CP interval, never as p = 0 or a Gaussian significance (`CHECKLIST` §4, forbidden phrasings). |
| I3 | Each rejection is robust to the sub-fine residual at κ = 3. | **RECORDED**, report-only label | `robust-labels.json` `206655f9…`: all 10 robust (A7-VS ruling). | Same as I1. The label is report-only under `RULING-20260929-s5p-A7-robustness-flag.md`. |
| I4 | Power at the MnvTune null meets the T6 target for the W3 and D5 alternatives (shape power 1.000 at 0.005) and misses it for W2 (0.231). | **RECORDED**, context only | `joint-evaluate.json` `power` (recorded at `9b26b8c3`); every power set is incomplete. | Under amendment 7, power is reported only beside a **non-rejection**. Every primary decision is a rejection, so power is context, not a claim condition. It must not be used to argue sensitivity to interaction mechanisms in general (PLAN §4). |
| I5 | The joint five-observable test adds discrimination beyond lower-dimensional comparisons. | **UNSUPPORTED** | No matched lower-dimensional test exists. The published 2D comparison already disfavours every family tested: 2106.16210 Table I gives χ² over 205 bins of 6786 for Tune v1, 8241 for GENIE 2.12.6, 5800 for GiBUU 2019 and 3789–5151 for NuWro. This repository's recomputation for Tune v1 is χ²/ndf = 33.04 (data) and 26.49 (our unfold) (`2d-unfolding/receipt_model_chi2_2d.json`, VERIFIED-NUMERIC 2026-08-11). | Omit it. W1 (packet §6) can support only the scoped claim "beyond matched coarse projections of the same cells", never "beyond published lower-dimensional results". |
| I6 | The rejection identifies a localized (high-E_avail, high-W) discrepancy or a nuclear mechanism. | **UNSUPPORTED** | The tests are global total and shape statistics over 109 (72) cells. | A global rejection does not localize (PLAN §4). Localization stays descriptive, with the caveats of row L8. |
| I7 | The rejections are robust to plausible detector-response mismodelling. | **UNSUPPORTED** | Amendment 7 `conditions_stated_with_every_claim` item 2: *"there is no recoil-energy-scale band in the analysis's systematic set … so hadronic-response completeness is not established"*. The collaborator question (`QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md`) is **PREPARED, NOT SENT**. | State the condition in the Letter itself, or run proposed study **W2** (packet §6). This gap may change the conclusion; see packet §5.4. |
| I8 | First calibrated simultaneous 5D goodness-of-fit test of neutrino generators on unfolded data. | **UNSUPPORTED** as a priority claim | `LITERATURE-20261005-comparison.md` §1–§3: no real-data unbinned neutrino unfolding was found; the highest data dimensionality found is 3; the only neutrino OmniFold work is a T2K simulation study (PRD 112, 012008). | Supportable, within the search limits: "to our knowledge, the first unbinned unfolding of neutrino data", and five simultaneous observables against a previous maximum of three. Do not claim priority for the test procedure. "First use of OmniFold in neutrino physics" is excluded (PLAN §5). |
| I9 | A five-dimensional cross-section measurement with qualified total uncertainties. | **UNSUPPORTED**; contradicted by the record | The measurement branch is **NOT ADMITTED** (amendment 4; `RECORD-20260927-s5p-stage2-exit.md`). `publication_readiness` is NOT READY under the authorization *"whatever the joint result"* (`CHECKLIST-20261001` §4). | Not claimable under any route considered here. It is not acquired by a change of journal (PLAN §10). |

## B. Claims in the current Letter (`docs/analysis-note/paper_body.tex` at `61cad10d`)

| # | Claim (Letter line) | Status | Evidence | Note |
|---|---|---|---|---|
| L1 | The 2D integrated σ is 1.11% above the published total (ratio 1.0111); 205 bins; χ²/ndf 3.66 against the published covariance (`:51–58`). | **DEMONSTRATED** | `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md:50–56`; `AGENTS.md` row "2D central value … VALIDATED". | It validates the estimator on shared data and is not an independent comparison; the Letter already says so. |
| L2 | The standalone 2D uncertainty construction gives a 6.87% median against the paper's 6.86% (`:58–61`). | **DEMONSTRATED**, as a construction | 2D status `:22,56`; ledger. | **"its coverage is untested" (`:61`) is INCOMPLETE:** the combined construction's coverage is still untested, but its statistical band has now failed a fixed-truth test (L3). |
| L3 | (Missing from the Letter) The 2D statistical band (VL162) undercovers a fixed truth: C2 = 0.912 against a window [0.928, 0.972]; FAIL-undercoverage, independently reproduced. | **DEMONSTRATED** on its branch; **not on main** | `OUTCOME-20261005-2d-fixed-truth-coverage-fail.md` (`80862878`), ledger VL168 on that branch. | The test covers the VL162 statistical band only, not the systematic or combined budget and not 5D coverage. The Letter must state it once the branch merges. |
| L4 | The central value (scikit-learn) and the covariance (LightGBM) are not estimator-matched (`:42–46`). | **DEMONSTRATED** disclosure | 2D reference. | Keep it. An inference Letter adds a third estimator (R) and must name it in each figure (PLAN §4). |
| L5 | The 3D/4D/5D marginal normalizations agree at 1–2%, and an injected E_avail closure passes (`:95–99`). | **DEMONSTRATED** | `AGENTS.md` rows "3D central value…" and "Scalar 4D/5D central values and closures", both VALIDATED; `nd-unfolding/ND_OMNIFOLD_STATUS.md`. | It tests signal reweighting only and not the background subtraction; the Letter says so. |
| L6 | Background bias reaches 4% at the highest W; regularization bias reaches 74% at high W under a GiBUU/GENIE shape and 16–31% for other shapes; none of it is in the quoted uncertainties (`:100–116`). | **DEMONSTRATED** limitation | VL149, VL151, VL152; `KNOWN_ISSUES` 75, 77. | It bears directly on L8: the largest regularization bias is in the region where the Letter localizes its excess. |
| L7 | All four generators underpredict at low E_avail; Valencia 2p2h fills 52% of the gap below 0.4 GeV (`:140–149`). | **DEMONSTRATED** central value | VL159, VL160 (VL160: *"fills 52% of the E_avail ≤ 0.4 GeV gap"*; 63% is the integrated-deficit share). | No significance. |
| L8 | A central-value excess over MnvTune is localized at high E_avail and high W (`:155–160`, the abstract). | **DEMONSTRATED as a central value only**; no significance | The figure `paper_joint_localization` is cropped from `excess_eavail_W.pdf` (`docs/analysis-note/make_figures.sh:178–180`), whose producers are `3d-unfolding/genie/gen_to_xsec_eavailW.py` and `overlay_eavailW_band.py`. VL156–VL158 cover the external-generator comparisons (L9), not this MnvTune excess, so no ledger row for it was identified. | It is descriptive. No approved test establishes the localization, and the same region carries the largest measured regularization bias (L6). It cannot be the headline of an inference Letter. |
| L9 | The external generators lie below the data overall (ratios 1.07–1.39) and at high W; GiBUU lacks E_ν > 20 GeV (`:181–194`). | **DEMONSTRATED** central value | VL156–VL161; `KNOWN_ISSUES` 82. | |
| L10 | A covariance is adopted under exception, and no significance is quoted because s_proj = 6.145% exceeds the 5% bound (`:223–251`). | **DEMONSTRATED** | VL142–VL144; adoption record §4 (the four travelling measurements); 2026-09-20 and 09-21 corrections. | The inference must **not** be derived from this covariance (PLAN §5). If the Letter keeps it, its four measurements travel with it. |
| L11 | Hadronic-response completeness is not independently validated (`:253–258`). | **DEMONSTRATED** disclosure | `DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md` §5 wording. | For an inference Letter this disclosure is no longer peripheral; see I7. |
| L12 | PET is diagnostic and method development (`:262–266`). | **DEMONSTRATED** status | `AGENTS.md` (ruling 2026-08-20); `DECISION_RECORD-pet-final-design.md` (`NO_ELIGIBLE_DESIGN`). | Keep it, or drop PET from the Letter. |
| L13 | Acknowledgment: "the data products used in this study [were made] publicly available" (`main_paper.tex`). | **INCOMPLETE** | The inputs are MINERvA OpenData (`2d-unfolding/download_playlist.sh`: `/pnfs/.../persistent/OpenData/MediumEnergy_FHC`). | The open-data terms require citing DOI 10.15484/3022562 and NIM A743 130 (2014). The DOI is absent from `technote.bib` (see the release inventory). |

## C. Derived context for the decision (this lane; descriptive; not a recorded result)

These were computed by this lane from the `joint-evaluate.json` copy (`b9604502…`), which was pending when computed
and recorded at `9b26b8c3` since. They are Gaussian
proxies on skewed null distributions, used only to inform the route decision. They must not be quoted as
significances. The reviewer reproduced them independently.

The null medians and SDs of the **shifted** variants are fields that the independent recompute did not output and
so did not verify (recompute report §3). Only the c = 0 median and the c = 0 SD, up to its ddof convention, were
compared.

| null | T_total obs | null median (most conservative claim variant) | null SD | proxy distance | T_shape obs | proxy distance |
|---|---:|---:|---:|---:|---:|---:|
| MnvTune v1 | 2852 | 49 | 13.6 | ≈ 207 SD | 631 | ≈ 40 SD |
| GENIE CV | 1813 | 583 | 67.3 | ≈ 18 SD | 1086 | ≈ 4.5 SD |
| GENIE MEC | 1647 | 473 | 44.4 | ≈ 26 SD | 869 | ≈ 4.9 SD |
| NuWro 21.09 | 7427 | 6407 | 177.9 | ≈ 5.7 SD | 9660 | ≈ 2.8 SD |
| GiBUU 2019 | 2867 | 1925 | 91.9 | ≈ 10 SD | 4013 | ≈ 6.1 SD |

**Reading:**
- In the recorded result (`9b26b8c3`), every test is rejected, and none is certified against the lost draws.
- The analysis's own tuned simulation, drawn with every declared nuisance, sits about 200 null SDs from the data in
  the total statistic and about 40 in shape, so most of its excess is normalization-like.
- The external nulls are strongly non-central (λ = 318–6,344, amendment 7 `prefreeze_measurements`), because the
  calibration simulates the estimator's pull toward the prior. Their observed statistics sit only 2.8–26 null SDs out.
- NuWro shape, the only k = 1 test, is the closest to its null.
- A **common** omitted effect, such as a recoil-energy response difference between data and simulation, could move
  all five statistics. To first order, ΔT ≈ 2dᵀW⁻¹(F−μ) + dᵀW⁻¹d, so the effect can go either way per test.
- The published muon-kinematics comparison (2106.16210 Table I, which includes hadronic-response systematics)
  independently disfavours the same families. That is partial evidence that the rejections are not purely a
  response artefact.
- The open question is mainly the five-dimensional **shape** content along the hadronic axes (I7; packet §5.4,
  W2).

## D. Status update, 2026-10-06 (after D1–D4, W1, W2; supersedes the I-row statuses above)

| # | status now | evidence |
|---|---|---|
| I1 | **DEMONSTRATED, under the stated conditions** | Recorded at `9b26b8c3`; independent recompute AGREE 1379/1379 (`466b427b`); lost-seed resolution certified per Joseph's D3, "Certified, margin disclosed" (`538739ff`), with all five disclosures; Stage-7 approved wording (`cbd075e7`, `sec:joint5d`) |
| I2 | **DEMONSTRATED** | As I1. The finite-resolution p-values (k + 1)/(B + 1) are never zero. |
| I3 | **DEMONSTRATED, report-only label** | Robust at κ = 3 in the frozen, (a) and (b) readings |
| I4 | **DEMONSTRATED, context only** | Stage-7 power sentence |
| I5 | **OMITTED, terminal** | W1 (`22a004e7`, reproduced `09718448`): no (G, t) qualifies |
| I6 | **UNSUPPORTED, omitted** | Global statistics only |
| I7 | **NARROWED: not removed by an exploratory ±4% variation; completeness not established** | W2 (`940d84aa`; independent check `9ffc4ddd`). The amendment-7 condition stands. |
| I8 | **"To our knowledge, the first unbinned unfolding of neutrino data"**, with no priority claim for the test | Literature file §3 |
| I9 | **NOT CLAIMED** | The article states "not a measured cross section" |
| L2/L3 | **PENDING the VL170 rebuild** | Joseph adopted VL170 (`af24a101`). The rescoring is merged (`5aab2d6d`). The rollup is pending from the 2D lane. |
