# Slide outline — "MINERvA with OmniFold: Generator Comparisons + Higher Dimensions"

**Purpose:** a *leave-behind* deck for my advisor (he reads it; I am not presenting).
Because there is no narration, each slide carries enough text to stand on its own. Build in
Google Slides; figure paths are relative to the repo root. Honest-framing notes (in
*italics*) are guidance for me — trim or keep as you like.

Arc: recap → background (physics + papers) → 3D → 3D physics → 4D → validation → status/asks.

---

## Slide 1 — Title
**MINERvA with OmniFold: Generator Comparisons + Higher Dimensions**
- [name], [date]
- One-line framing: *Unbinned OmniFold reproduces the published 2D inclusive cross section, and — for the first time at MINERvA — extends it to 3 and 4 simultaneous observables, where it independently recovers MINERvA's known low-recoil (2p2h) physics. The headline is the method; the physics it recovers validates it.*

---

## Slide 2 — Since last time
*Catches him up from our last conversation (the 2D UQ, before the flux fix).*
- **Last time:** the 2D uncertainty study had a flux-normalization error, so the agreement with the paper was partly accidental.
- **Now fixed:** OmniFold's combined median per-bin uncertainty is **6.87%** vs the published **6.86%** — a like-for-like match, and the residual χ²/ndf = 3.66 is understood (a correlated low-pT shape difference + a ~1-unit GBDT-regularization band).
- **Headline since then:** extended the measurement to **3D (+E_avail)** and **4D (+q3)** — the first 3- and 4-observable unbinned unfolds of MINERvA data — and ran a four-generator comparison that **independently recovers MINERvA's known low-recoil (2p2h) deficit** (Rodrigues 2016, Ascencio 2022), confirming the method finds real physics.
- *Takeaway: the 2D foundation is now solid; the new work is the higher-dimensional extension.*

---

## Slide 3 — Background: the physics (for context)
*He is not familiar with the low-recoil / 2p2h literature — this slide makes slides 6–7 readable.*
- **What we measure:** the νμ charged-current *inclusive* cross section in the MINERvA medium-energy NuMI beam (⟨Eν⟩ ≈ 6 GeV) on hydrocarbon.
- **The observables we add:**
  - **E_avail (available energy):** the visible hadronic energy (protons + charged pions' KE + EM energy; neutrons and the muon excluded). It tracks energy transfer to the nucleus.
  - **q3 (three-momentum transfer):** the magnitude of momentum transferred. Together, **(E_avail, q3) is the plane in which quasi-elastic (QE), two-particle-two-hole (2p2h), and resonance (RES) processes physically separate.**
- **The "2p2h" issue, in one line:** beyond single-nucleon QE, neutrinos can knock out **two nucleons at once (2p2h / meson-exchange currents)**, filling the dip in available energy between the QE and Δ-resonance peaks. MINERvA first saw this excess at low recoil (Rodrigues 2016, arXiv:1511.05944) and absorbed it into an *empirical* tune; generators still struggle to predict it from first principles.
- *Takeaway: the interesting physics lives in the hadronic recoil (E_avail, q3) — exactly what extra OmniFold dimensions give us.*

---

## Slide 4 — Background: the method & the two key papers
- **OmniFold (unbinned):** an ML unfolding that iteratively reweights simulation to data using classifiers. Its defining advantage: **adding an observable is just adding an input feature** — no migration matrix, no binning penalty. Traditional (D'Agostini) unfolding cannot practically do >2 correlated observables, which is why no MINERvA measurement has.
- **The published result we reproduce — Ruterbories *et al.*, PRD 104 092007 (arXiv:2106.16210):** the 2D inclusive d²σ/(dpT dp∥) at ⟨Eν⟩ ≈ 6 GeV. This is our validation anchor and the only published data we compare to bin-for-bin so far.
- **The low-recoil reference — Ascencio *et al.*, PRD 106 032001 (arXiv:2110.13372):** measures d²σ/(dq3 dE_avail) at low q3 — the modern 2p2h probe. *Our 4D result is built to compare to this directly (see asks).*
- *Takeaway: we reproduce one published measurement (Ruterbories) and are positioned to compare to a second (Ascencio).*

---

## Slide 5 — 3D extension (+E_avail): first 3-observable unfold at MINERvA
**Figures:** `3d-unfolding/minerva_unfolding_landscape.png` (left), `3d-unfolding/eavail_spectrum.png` (right)
- Every prior MINERvA differential measurement (N=30) unfolded **at most 2** kinematic variables, all with binned methods. This is the **first simultaneous 3-observable unfold** (left figure).
- The unfolded available-energy spectrum d σ/dE_avail (right) falls monotonically from 2.2×10⁻³⁸ cm²/GeV/nucleon at the low-recoil peak into the high-E_avail tail — the expected inclusive shape.
- **Validation:** marginalizing the 3D result back over E_avail reproduces the frozen 2D result — total σ to **+0.95%**, median per-bin ratio **1.0016** — and an injected-shape closure passes, so the new axis carries real information, not method bias.
- *Takeaway: the extra dimension is trustworthy (it recovers 2D) and the spectrum is physical.*

---

## Slide 6 — 3D physics: recovering the known low-recoil (2p2h) deficit with a new method
**Figures:** `3d-unfolding/genie/generators_vs_unfolded_band.png` (main); optional inset `3d-unfolding/genie/compare_mec_eavail.png`
- We compare to **four generators we produce ourselves** at truth level (GENIE 2.12, MINERvA Tune v1, NuWro 21.09, GiBUU 2019). *(No published 3D data exists — this is the comparison.)*
- **On muon kinematics (pT, p∥) all four track the data shape** and differ only in normalization — they are *not* distinguishable. **E_avail is the discriminating axis:** all four **under-predict the data at low available energy**, by 7–22% integrated (GENIE CV −7%, Tune −10%, NuWro −15%, GiBUU −22%).
- **This is the well-established MINERvA low-recoil/2p2h deficit, not a new discovery** — first isolated by Rodrigues *et al.* 2016 (the effect the empirical MINERvA tune was built to absorb) and mapped in (q3, E_avail) by Ascencio *et al.* 2022. We confirm it: pion FSI dials move the spectrum <1% (can't explain a ~10% excess), it localizes to the **QE–Δ dip** (E_avail 0.1–0.4 GeV: +3.9σ, +2.3σ), and turning on Valencia 2p2h fills ~half the gap (inset).
- *Takeaway: the point here is **methodological** — a new unbinned unfold independently recovers MINERvA's established low-recoil 2p2h physics, as a by-product of unfolding muon kinematics + E_avail. Recovering known physics validates the method.*

---

## Slide 7 — 4D extension (+q3): does the excess have momentum-transfer structure?
**Figure:** `nd-unfolding/q3_excess_projection.png`
*This is the slide where the plot needs explaining (he's reading it cold).*
- First **4-observable** unfold (pT, p∥, E_avail, q3). The figure is the **data ÷ GENIE-CV ratio** of the 4D result, shown three ways (red = data above prediction, blue = below):
  - **Right panel (E_avail marginal): a closure check.** It reproduces the 3D low-recoil excess (1.21 at lowest E_avail → ~1.0 in the dip → 1.2 in the DIS tail) — confirms the 4D unfold is consistent with 3D.
  - **Left panel (E_avail × q3 map): the new result.** The data–prediction discrepancy is **not flat in q3** — the excess grows toward higher q3, while GENIE over-predicts the low-q3 / moderate-E_avail cells. *This structure is invisible to a muon-only or fixed-q3 measurement — it is the reason to go to 4D.* (Blank cells are kinematically forbidden.)
  - **Center panel (q3 marginal):** integrated over E_avail, q3 alone is mild — you *need* the joint (E_avail, q3) view.
- **Systematics:** a 187-universe covariance on the 4D grid; **model-dominated** (2p2h and axial-mass uncertainties lead; flux drops to ~3%) — unlike the flux-dominated 2D/3D budgets, because q3 is precisely the model-discriminating variable. The **combined stat+ML+syst 4D budget is now complete** (median 13.5%/bin, rank 264/4830); stat and ML are negligible against the model systematics, so the conclusions are unchanged.
- *Honest note (keep or drop): this map is at central-value level and the base GENIE has no 2p2h, so read it as where the discrepancy lives, not a per-cell significance map.*

---

## Slide 8 — Why don't the extra dimensions change the muon-kinematics (pT, p∥) result?
**Figure:** `3d-unfolding/eavail_marginal_vs_paper_pull_full.png` (per-bin pull on the 14×16 (pT, p∥) grid)
*A natural reader/referee question: adding E_avail and q3 reshapes the recoil result but the muon-kinematics result barely moves — why?*
- **OmniFold reweights the full joint distribution.** It learns one weight w(pT, p∥, E_avail, q3) over **all four observables at once** — it does *not* unfold the muon kinematics separately. So the extra dimensions *do* feed back into pT/p∥; nothing is held fixed.
- **The muon-kinematics result comes out close to 2D for a physical reason:** the data↔simulation **discrepancy lives in the hadronic recoil (E_avail), not the muon kinematics.** On (pT, p∥) the generators already match the data shape and the muon momentum/angle are well reconstructed (the data-vs-reco classifier is nearly blind, AUC ≈ 0.54). The corrections OmniFold applies are in the recoil; projected back onto pT/p∥ they largely average out. Marginalizing 3D→2D recovers the 2D total σ to **+0.95%** (median per-bin ratio 1.0016).
- **But it is *not* untouched — the extra axis leaves a measurable, physical fingerprint:** a **~4.4% per-bin scatter** appears in the (pT, p∥) marginal relative to the pure-2D unfold (figure; marginal-vs-published χ²/ndf rises to 4.98 from the 2D 3.66). A closure test confirms this scatter is **genuine data↔MC structure the extra dimension exposes**, not a method artifact.
- **Takeaway — this is a *result*, not a limitation:** the stability of pT/p∥ across 2D→3D→4D says the recoil discrepancy (the 2p2h excess) **roughly factorizes from the muon kinematics**. The new physics shows up where data and models actually disagree — in E_avail and its q3 structure — which is exactly where the unfold concentrates its corrections.

---

## Slide 9 — Method validation
**Figure:** `nd-unfolding/pet_vs_gbdt.png` (PET vs GBDT 4D shape overlay); optionally the C2ST/calibration diagnostics.
- **Unbinned goodness-of-fit (binning-free):** a classifier-two-sample test cannot tell data from the *unfolded* simulation — accuracy 0.50, p = 0.17 (vs accuracy 0.52, p ≈ 10⁻²⁴⁴ *before* unfolding). The unfold genuinely removes the data↔MC mismatch.
- **Scalar NN cross-check:** a keras-MLP OmniFold run on the same scalar 3D inputs reproduces the GBDT result within the ML band (total ratio 1.008; median projection differences about 0.7--1.4%).
- **Point-cloud transformer (PET):** unfolding on the **raw per-hadron point cloud** (the real non-muon recoil clusters) reproduces the scalar-GBDT 4D shape to **2.3–3.9%/bin** (figure). *Shape-only, on a 2M-event subsample — a method/representation robustness check, not an independent physics result.* (An earlier attempt used the wrong, mostly-empty `ExtraEnergyClusters_*` branch and was discarded.)
- *Takeaway: the result is robust to the goodness-of-fit definition, the classifier family (GBDT / MLP / transformer), **and** the input representation (engineered scalars vs. raw point cloud).*

---

## Slide 10 — Status & what I need from you
- **Done:** 2D (reproduces published), 3D (+ 4-generator comparison + 2p2h diagnosis), 4D q3 (full **combined stat+ML+syst budget complete**, median 13.5%/bin, + the (E_avail, q3) structure), PET point-cloud cross-check, technote updated.
- **In flight:** nothing blocking — the 4D analysis is fully assembled. (The only open compute would be optional full-statistics reruns if we decide to push the point-cloud track.)
- **Asks:**
  1. **Can you help me get the Ascencio low-q3 data release** (PRD 106 032001 / arXiv:2110.13372, d²σ/(dq3 dE_avail))? Our 4D result is ready for a **bin-identical comparison to their published measurement** — a method validation (does unbinned OmniFold reproduce their binned 2p2h result?), the direct analogue of the 2D-vs-published win. It's the one thing I'm blocked on.
  2. **How far should I push the point-cloud track?** PET already reproduces the scalar GBDT on the real clusters (slide 9). Options: keep it as a method appendix, or aim it at a *new* hadronic observable (would need reconstruction-level particle ID work). Your call on scope.
  3. *(optional)* There's a **+2.2σ excess in the high-E_avail (DIS-tail) bin** the 2p2h story doesn't touch — worth investigating now, or park it?

---

### Figure inventory (all exist in the repo)
| Slide | Figure |
|---|---|
| 5 | `3d-unfolding/minerva_unfolding_landscape.png`, `3d-unfolding/eavail_spectrum.png` |
| 6 | `3d-unfolding/genie/generators_vs_unfolded_band.png`, `3d-unfolding/genie/compare_mec_eavail.png` |
| 7 | `nd-unfolding/q3_excess_projection.png` |
| 8 | `3d-unfolding/eavail_marginal_vs_paper_pull_full.png` |
| 9 | `nd-unfolding/pet_vs_gbdt.png` (PET vs GBDT 4D shape overlay); optionally C2ST / classifier-calibration diagnostic |

*Optional 2D-generator figure if you want a normalization-only contrast on slide 6 or background: `2d-unfolding/model_comp_projections.png` (GENIE Tune ~9% low on the muon kinematics).*
