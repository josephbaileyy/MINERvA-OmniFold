# M4: the definitions a PRD reader needs, taken from code and records

All citations are at `origin/main` `c5aa0e90`. `P:` means `docs/analysis-note/paper_body.tex`. `CVU` means
`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h`. `EL` means `.../runEventLoopOmniFold.cpp`.
`u2d` means `2d-unfolding/unfold_2d_omnifold_unbinned.py`. `und` means `nd-unfolding/unfold_nd_omnifold_unbinned.py`.

The MAT and MAT-MINERvA headers that implement the cuts (`CCInclusiveCuts.h`, `CCInclusiveSignal.h`,
`TruthFunctions.h`, `MaxPzMu.h`, `util/GetFluxIntegral.*`) are **not in this repository**. Their content
is cited from records that read the cluster checkout (MAT-MINERvA `50d76314`, MAT `35097b65`). Those
citations are second-hand.

---

## 1. Signal definition and fiducial volume (truth)

- **Interaction:** a νμ (`SetAnalysisNuPDG(14)`, EL:1700) charged-current interaction
  (`truth::IsNeutrino`, `truth::IsCC`, EL:1717-1718). These read `mc_incoming` and `mc_current` (CVU:376-378).
  There is no restriction on interaction channel or final state.
- **Fiducial volume (truth vertex):** tracker `5980 < z < 8422 mm`, hexagon apothem `850 mm` (EL:1708, 1720-1721).
- **Muon phase space** (EL:1737-1740):
  - θμ < 20°
  - p∥ > 1.5 GeV/c (`PZMuMin(1500)`)
  - p∥ < 60 GeV/c (`MaxPzMu(60000)`)
  - pT ≤ 4.5 GeV/c (`MaxPtMu`, `<=`; `cuts/MaxPtMu.h:23`)
  - pT is `p sinθ` and p∥ is `p cosθ` (CVU:71-79), in GeV/c.
- **Python mirror:** the Python truth gate (`u2d:54-67`, `in_truth_phase_space`) uses inclusive bounds
  `0 ≤ pT ≤ 4.5`, `1.5 ≤ p∥ ≤ 60` and `atan2(pT,p∥) < 20°`. It cannot re-apply the vertex cuts (`u2d:58-61`).
- **Env flag:** setting `MNV101_FULL_PHASE_SPACE` drops the muon cuts (EL:1728-1735). That is the FPS
  study, not the publication signal.
- **Truth-W NaN rows:** the 5D truth denominator also drops rows whose truth W is non-finite (`und:333-335`;
  see §3).
- **Target and nucleon count:** the target is the tracker fiducial volume (polystyrene scintillator, CH).
  - The count is `N = 3.2352943296224835e30` nucleons (`u2d:44`), from
    `PlotUtils::TargetUtils::GetTrackerNNucleons(5980, 8422, isMC=true, 850)` (comment at `u2d:41-43`).
  - It is hard-coded because `hadd` sums the per-playlist `TParameter` (EL:1908-1913; `2D_OMNIFOLD_REFERENCE.md:90-93`).
  - The same constant normalizes data, so the `isMC=true` geometry is used for data too.
- **Background** (EL:1447-1456): any reco-selected MC event that is not (signal **and** in phase space).
  - Genuine background: other flavour, wrong sign, NC, and out-of-fiducial-vertex events.
  - "Fakes": CC νμ events whose true muon is outside the phase space.
  - Both are POT-scaled and removed from the data target. The purity or negative-weight treatment is at P:175-194.
- **Paper and note coverage:**
  - P:119-121 says only that the signal, fiducial volume and selection "follow Ref. [MINERvA:2021owq]". The
    paper gives no angle or momentum limits, no fiducial numbers, no nucleon count and no background definition.
  - The note states all of them at `sec_experiment.tex:33-66`.
  - **For PRD self-containment, the paper needs the θμ/p∥/pT limits, the fiducial box, N and the background/fake split.**

## 2. Reconstructed selection (EL:1710-1715, MAT `preCuts`)

1. Reco vertex in `5980 < z < 8422 mm` (`reco::ZRange`).
2. Reco vertex inside the 850 mm apothem (`reco::Apothem`).
3. Reco θμ < 20° (`reco::MaxMuonAngle(20)`).
4. MINOS-matched muon with a passing fit: `isMinosMatchTrack==1 && <tool>_minos_trk_is_ok==1` (CVU:107-115).
5. Dead time `phys_n_dead_discr_pair_upstream_prim_track_proj ≤ 1` (`NoDeadtime(1)`; CVU:131-133).
   Per the record `.../playlist-spread-20261014/scripts/intensity.py:11-12`, this is `PlotUtils::Maximum`, i.e. `≤1`.
6. μ⁻ charge from MINOS curvature, `minos_trk_qp < 0` (`reco::IsNeutrino`; CVU:380-382; same record).

Python reco window:
- Data rows must have `measured_pass` and finite observables, with reco `0 ≤ pT ≤ 4.5` and `1.5 ≤ p∥ ≤ 60` GeV/c (`und:479-488`).
- In 5D the injected background and data side are also restricted to the binned range on every axis (`und:906-916`).

Paper and note coverage:
- The paper says only "a tracker vertex and a MINOS-matched muon" (P:158-159).
- The note lists items 1–6 at `sec_experiment.tex:47-53`.
- Neither states the reco window, the dead-time threshold or the charge-sign cut numerically.

## 3. The five observables

Units: GeV. Code works in MeV and divides by 1000 at EL:587-591 (truth) and EL:1176-1180 (reco).

| | Truth (EL:587-591) | Reco (EL:1176-1180, 1589-1593) |
|---|---|---|
| pT | `p_true sinθ_true` (CVU:71-74) | `p sinθ` (CVU:61-64) |
| p∥ | `p_true cosθ_true` (CVU:76-79) | `p cosθ` (CVU:66-69) |
| E_avail | `GetEAvailableTrue` (CVU:361-374) | `NewEavail` (CVU:185-193) |
| q3 | `Getq3True` (MAT) | `RecoQ3` (CVU:208-218) |
| W | `GetTrueExperimentersW` (CVU:396-410) | `RecoW` (CVU:227-240) |

**Muon and angle sources.**
- Reco muon: p from `leptonE`/`minos_trk_p`, angle from `muon_thetaX/Y`, sign from `minos_trk_qp`
  (`.../q2-opendata-20261014/triage/REPORT.md:35-38`).
- Which axis the truth θ (`GetThetalepTrue`) is measured from (beam or detector z) is **not established
  in any record found**. It matters for the truth W relation below.

**E_avail, truth** (CVU:361-374). The sum runs over `mc_FSPart` (post-FSI):
- γ: total E.
- π⁰: total E.
- π±: `E − 135 MeV`.
- p (2212 only): `E − 938.27 MeV`.
- Everything else counts zero: n, e±, K, p̄, hyperons, μ.

**The 135 MeV term** is the π⁰ mass, not mπ± = 139.57. So each charged pion contributes its kinetic energy
plus 4.57 MeV.
- Effect relative to 139.57: 439/65,911 = 0.666% of events change truth bin; the worst bin moves +1.049%
  (`docs/EAVAIL_DEFINITION.md:89-101`).
- It is not assessed against the covariance (`:118`).
- **Generator parity:** the "six-site" list (`EAVAIL_DEFINITION.md:135-141`) is CVU:364, four generator
  converters and `nd-unfolding/pet/pointcloud_projection.py:51`. All carry 135. The GENIE converter mirrors
  CVU exactly (`3d-unfolding/genie/genie_to_xsec3d.py:42-57`). The 5D build reports 0 mismatches in a
  20,000-event GENIE parity check (`docs/orchestration/state/s5p/gen5d/README-gen5d-build.md:44-49`).
- So every prediction uses the identical (uncorrected) definition. §6 below confirms this per generator.

**E_avail, reco** (CVU:185-193): `1.17 × [(blob_recoil_E_tracker − μfuzz_tracker) + (blob_recoil_E_ecal − μfuzz_ecal)]`.
- The muon-fuzz plane ranges are at CVU:168-183.
- There is no clamp at zero.
- It does **not** use the `recoil_E` q0 that feeds q3 and W.

**q3, truth.** MAT `Getq3True = calcq3(GetQ2True, EnuTrue, ElepTrue)`, giving `q3 = sqrt(mc_Q2 + (Eν−Eμ)²)`
(`README-gen5d-build.md:50-58`).
- `mc_Q2` was measured equal to the exact lab-frame `−(k−k′)²`, to 2.2e-10, in a MasterAnaDev tuple (same lines).
- So truth q3 is the exact |q⃗| from the generator's own four-vectors.

**W, truth** (CVU:385-410): `W = sqrt(M² + 2M(Eν−Eμ) − Q²_exp)`.
- `Q²_exp = 4EνEμ sin²(θ/2)` is **massless** (CVU:389, 392-394). It is not the `mc_Q2` used by q3.
- The mass M is the struck-nucleon mass:
  - `M_n = 939.56536` MeV if `mc_targetNucleon==2112`.
  - `M_p = 938.272013` MeV if `mc_targetNucleon==2212`.
  - Otherwise (e.g. 2p2h nucleon-pair codes) `M = (1.5M_n + M_p)/2.5 = 939.048` MeV (CVU:39-44, 95-97, 397-404).
- There is no binding-energy term, and the nucleon is taken at rest.
- When W² < 0, `TMath::Sqrt` returns NaN. Those rows are dropped as "bad" from both the truth denominator
  and the signal truth (`und:333-335`, `und:355-358`).

**q3 and W, reco** (CVU:208-240). Both use the **same** `q0 = <tree>_recoil_E`, the full calorimetric
transfer (not E_avail). With Eμ, p and θ from the muon:

    Eν = Eμ + q0
    Q² = max(0, 2Eν(Eμ − p cosθ) − mμ²),   where mμ² = Eμ² − p²
    q3 = sqrt(Q² + q0²)
    W  = sqrt(max(0, M̄² + 2M̄q0 − Q²)),    where M̄ = 939.048 MeV (average mass; reco has no nucleon id)

**Algebra (derived from the code, not computed).** Substituting Q² = q3² − q0² into W gives

    W_reco² = (M̄ + q0)² − q3_reco²

This holds whenever the W² clamp does not fire, including when the Q² clamp fires (then q3 = q0).
- `p cosθ = p∥` exactly (CVU:66-69 uses the same getters). So q3² = q0² + 2q0(Eμ − p∥) + 2Eμ(Eμ − p∥) − mμ².
- That is strictly increasing in q0 ≥ 0, so (pT, p∥, q3) fixes q0, and therefore W.
- **At reco level, W is an exact function of (pT, p∥, q3), apart from the two clamps.**
- E_avail reco comes from a different estimator, so it is not functionally tied to the others.

**At truth, under a stated assumption.** Assume the neutrino direction coincides with the axis of θ_true.
- Then q3² = Eν² − 2Eν p∥ + p², so `Eν = p∥ + sqrt(q3² − pT²)`.
- The other root is excluded because Eν ≥ Eμ > p ≥ p∥.
- With q0 = Eν − Eμ, W is then fixed by (pT, p∥, q3) and M.
- The massless-vs-exact Q² mismatch does not break this: both are deterministic in (Eν, p, θ).

What does break it:
- (i) The per-event choice of M (M_n, M_p or M̄; ≈1.3 MeV spread).
- (ii) Any angle between the true neutrino direction (which enters `mc_Q2`) and the θ axis. This is unverified.
- (iii) NaN rows.

**Fermi motion and binding do not break the relation.** The experimenters' W assumes a free nucleon at
rest. They make W differ from the true hadronic invariant mass, not from (pT, p∥, q3).

Measured residual: none.
- `docs/orchestration/state/measurement-paper/EVIDENCE-MAP-20261019.md:258-267` says **"The residual check is not run"**.
- The "fixed to within tens of MeV" wording (cited there from PLAIN-LANGUAGE-PASS2-REPORTS) is unmeasured.

**Paper and note coverage for §3:**
- P:131 gives W with a generic "Q²" and "struck-nucleon mass".
- P:132-142 gives E_avail and the 135 MeV effect.
- P:142-150 describes reco E_avail and says reco q3 and W "share information".
- The paper gives **no q3 formula** (P:130 says only "from the generator") and **no reco formulas**.
- The note gives the reco formulas (`scalar_kinematics.tex:1-19`, input at `sec_3d.tex:92`), truth E_avail
  (`sec_3d.tex:47-67`) and truth/reco W (`sec_eavailw.tex:21-25`).
- Neither states that the truth W uses the massless Q², that reco W² = (M̄+q0)² − q3², or the value and weighting of M̄.

## 4. Cross-section extraction

Formula (`nd-unfolding/xsec_nd.py:14, 54-83`; 2D form `u2d:1207-1275`):

    dⁿσ/∏dx_a = U · 1e4 / (c · Φ · N · POT · ∏_a Δx_a)

The result is in cm² per axis unit per nucleon. The 1e4 converts Φ from m⁻² to cm⁻².

- **U:** the unfolded truth-level yield, histogrammed with `np.histogramdd` over the fine grid.
- **c (completeness):** the unfolded input truth over `mc_truth_denom`, per bin (`und:1080-1086`).
  - The event loop appends truth-only misses (EL:680-915, "Phase 17/18"), so c ≡ 1 by construction.
  - The note gives c = 1.000000 at ME FHC (`sec_experiment.tex:88-89`; `sec_method.tex:249-253`).
  - Detector inefficiency is corrected inside OmniFold's miss regression, not by a separate ε.
- **Φ:** the integrated flux per pT bin, from `runEventLoopMC_MEFHC.root:pTmu_reweightedflux_integrated`
  (`u2d:1381-1384`, `load_flux_bins` `u2d:129-145`). It is broadcast over every other axis.
  - It is written by `runEventLoop.cpp:481` (`util::GetFluxIntegral`) and POT-combined over the 12
    playlists (`2D_OMNIFOLD_REFERENCE.md:110-115`).
  - Value: **Φ = 6.243343e-4 m⁻²/POT (= 6.243e-8 cm⁻²/POT), the same in every pT bin.** It is the integral
    over **0–100 GeV** of the νμ `flux_E_cvweighted` after the ν-e constraint, POT-averaged over playlists
    (`docs/orchestration/state/s5p/gen5d/README-gen5d-fluxfix.md:43-49, 74`).
  - Flux universes divide by their own Φ_u (`u2d:148-175`, `flux_integral_universes_MEFHC.root`).
- **N:** 3.2352943e30 (§1).
- **POT:** `dataPOTUsed` from the omnifile (`u2d:116-126`); 1.057e21 (note `sec_method.tex:257`).
- **Bin width:** the product of all D widths, including the 100-GeV catch bins.

Paper and note coverage:
- P:180-182 says only "dividing by integrated flux, target count, and bin width".
- No Φ value, energy range, N, POT-in-formula, c or units appear (units appear only in results, e.g. P:256).
- The note has the formula, N and POT (`sec_method.tex:243-262`), but not the Φ value or the 0–100 GeV range.

## 5. Grids, J cells, GiBUU domain, supported masks

- **Fine 5D grid**, C order (pt, pz, eavail, q3, W):
  - pT: 14 bins and p∥: 16 bins (`u2d:31-35`, the binning of arXiv:2106.16210).
  - E_avail `[0,.1,.2,.4,.8,1.5,3,100]`, q3 `[0,.2,.4,.6,.8,1.2,2,100]`, W `[0,1.1,1.4,1.8,2.2,3,100]` (`und:97-119`).
  - Total 65,856 cells (`docs/orchestration/state/s5c/contract.json:72`).
  - Hard-coded copies are checked at `nd-unfolding/project_cov_nd.py:46-57` and `nd-unfolding/s5p_stage1_inspect.py:38-44, 251`.
- **Fine-grid reported support:** `x_cv > 0`, giving 10,694 cells (`nd-unfolding/unified_throw_cov.py:346`;
  `nd-unfolding/z_statistics.py:39-49`).
- **J:** the coarse 3⁵ "H3" level (`nd-unfolding/s5c_partition.py:9-15, 35`).
  - Edges are the fine edges nearest weighted-MC tertiles (`:45-52`):
    - pT `[0,.55,.85,4.5]`
    - p∥ `[1.5,3.5,6,60]`
    - E_avail `[0,.4,1.5,100]`
    - q3 `[0,1.2,2,100]`
    - W `[0,1.4,2.2,100]`
    - Sources: `s5p_stage1_inspect.py:45-46`; `contract.json:76-106`.
  - Level rule: the finest level with marginal purity and stability ≥ 0.5 on every axis.
  - Support rule: expected reco signal **and** truth weight at data POT both ≥ 1000 (`contract.json:74-75`;
    `SUPPORT_MIN` `s5p_stage1_inspect.py:49, 270-276`).
  - This gives the 109 cells listed at `contract.json:108-218`.
  - The 25 unsupported cells with signal (0.47% of signal) stay in the total. A re-count from
    `state/s5c/b1/partition_scan_2.json` reproduces 109 and 25.
- **GiBUU domain:** the J cells with p∥ < 6 GeV/c (coarse pz index ≤ 1): 32 + 40 = **72**.
  - Declared at `docs/orchestration/state/s5p/contract-amendment-5-joint-test-design.json:34` and
    `contract-amendment-7-production-admission.json:9`.
  - Code: `nd-unfolding/s5p_joint.py:5, 217, 358`; `s5p_recompute.py:372-374`.
  - The reason is the 20 GeV GiBUU cut (`KNOWN_ISSUES.md` 82).
- **Other supported sets:** H2 has 27 of 32 cells and EW has 39 of 42, by the same rule
  (`docs/orchestration/state/s5p/stage1/stage1_inspect.json`).
- **Paper coverage:**
  - The fine grid (P:753-754) and the J edges and counts (P:757-763; macros in `values_inference.tex:14-15`) agree with the code.
  - The paper **never defines "supported"** (the ≥1000 rule) or how the J edges were chosen.
  - The note has the rule at `app_statmethods_nd.tex:72-76`.

## 6. Generator predictions

The externals are built by `3d-unfolding/genie/gen_to_xsec5d.py` ("G5") and then flux-repaired. The receipts
are `docs/orchestration/state/s5p/gen5d/README-gen5d-build.md` and `README-gen5d-fluxfix.md`. There is no NEUT
or MnvTune v4 prediction.

| G | Version | Target | Flux / Eν range | Events (gen → in grid) |
|---|---|---|---|---|
| MnvTune v1 | GENIE 2.12.6 with Tune v1 weights (EL:1745-1750) | tracker (N above) | the analysis Φ | analysis MC truth |
| GENIE CV | 2.12.10c, no MEC | CH (C12 0.9225 / H1 0.0775 by mass) | non-PPFX `flux_E_unweighted`, 0–50 GeV; reweighted to φ_t and supplemented with 50–100 GeV samples | 2.0M → 938,141 |
| GENIE+MEC | 2.12.10c `Default+CCMEC` (Valencia) | CH | as GENIE CV | 2.0M → 960,128 |
| NuWro | 21.09.1 | **C12 only** | 0.5–50 GeV; reweighted and supplemented as GENIE CV | 2.0M → 1,261,997 |
| GiBUU | 2019 | **C12 only** | its own PPFX-like `MINERvA_MEflux.dat`, with jobcard `Enu_upper_cut = 20`; per-event reweighted to φ_t below 20 GeV (σ × 0.9966) | 80 runs → 910,378 |

**Flux repair** (`KNOWN_ISSUES.md` 83; `README-gen5d-fluxfix.md:36-60`):
- The per-event weight is `r(E) = (φ_t(E)/Φ_t)/φ_s(E)`.
- Φ_t is the same 0–100 GeV integral the data use (§4).
- The GiBUU cut stays: 5.2% of σ_CC lies above 20 GeV (`README-gen5d-fluxfix.md:140-148`; `KNOWN_ISSUES.md` 82).
- This is the reason for the 72-cell domain.

**Observables in the generator code:**
- **E_avail:** identical to CVU, including 135 MeV. Sources: G5 C++ define at :88-98; `genie_to_xsec3d.py:42-56`;
  `nuwro_to_flat_5d.C:64-67`; `gibuu_to_xsec3d.py:110-116`.
  - GiBUU has 3,481 in-PS events with E_avail < 0 (off-shell nucleons). These are dropped from every GiBUU
    histogram (`README-gen5d-build.md:110-112`).
- **q3:** `sqrt(|k−k′|²)`, written as `Q² = |k−k′|² − q0²` plus `q0²` (G5:114-120). This is the same object
  as `Getq3True`.
  - For GiBUU, k is assumed to be `(0,0,Eν)` (G5:299).
- **pT and p∥:** the muon components relative to the generator's neutrino axis (+z).
- **W:** `sqrt(M_n² + 2M_n q0 − 4EνEμ sin²(θ/2))` with **fixed M_n = 0.939565** and W = 0 when W² ≤ 0
  (`gen_to_xsec_eavailW.py:46-61`; `gibuu_to_xsec_eavailW.py:87-93`; `nuwro_to_flat_5d.C:72-78`; G5:295-298).
  - This is **not** the analysis W (see the inconsistencies below).
  - Both use the massless Q².

**Signal (G5:526-528):**
- CC νμ, `0 ≤ pT ≤ 4.5`, `1.5 ≤ p∥ ≤ 60` and `atan2(pT,p∥) < 20°`. This is the same Python gate as `u2d:54-67`.
- There is **no vertex cut**, which is not applicable to a generator.

**Normalization:** each prediction is d⁵σ in cm²/nucleon/(GeV/c)²/GeV³ (G5:523), per nucleon of its own target.
- **GENIE CV:** `⟨σ_CC⟩_t,<50 = ∫₀⁵⁰ φ_t σ_CC/Φ_t = 4.1829e-38 cm²`. Here σ_CC is the (C12+H1) `tot_cc` divided
  by 13 (`gen5d_flux_reweight.py:70, 180-191`). It is distributed by `Σ_bin r/Σ_CC r`.
- **GENIE+MEC:** divides by `Σ_nonMEC r`.
- **NuWro:** `Σ w_e r_e/N_total` (`README-gen5d-fluxfix.md:53-60`).
- **GiBUU:** `Σ perweight/80 × 1e-38` (`gibuu_to_xsec3d.py:139`).
- **MnvTune v1:** the analysis MC truth passed through the same `extract_cross_section_nd`, with the same Φ, N
  and POT (`nd-unfolding/s5p_mc_truth_pred.py:1-10, 40-50`).

**Mapping onto J (`nd-unfolding/s5p_joint.py:61-80`).**
- Row c of U holds the fine-cell volumes of the fine cells whose centre lies in J cell c. Every J edge must be a
  fine edge (`s5p_stage1_inspect.py:85-88`).
- The prediction is μ_G = U·xsec_flat, the cell-integrated σ in cm²/nucleon. Its variance is U²·sumw2.
- So **all five predictions use the same fine grid and the same U**. The data side reaches J the same way.
- Within-cell shapes in the null pseudo-data are MnvTune's (amendment 5 :37).

**Paper coverage:**
- P:162-171 gives versions, targets, the flux repair and the 20 GeV GiBUU cut.
- P:745-747 lists the five predictions.
- The paper omits: the 0–50/0.5–50 GeV generation ranges, that the predictions are per nucleon of CH versus C,
  the fixed-M_n W, and that the predictions use the same observable code (or how it differs).

---

## Inconsistencies found

1. **W mass convention differs between analysis and predictions.**
   - The analysis truth W uses the struck-nucleon M (M_n/M_p/M̄) and is NaN when W² < 0 (CVU:396-410). NaN rows
     are dropped (`und:333-335`).
   - The four external predictions use a fixed M_n and set W = 0 when W² ≤ 0, so those events land in W ∈ [0,1.1)
     (`gen_to_xsec_eavailW.py:46-61`).
   - Measured effect: 1,438/938,141 (GENIE CV), 1,449/960,128 (MEC) and 1,757/1,261,997 (NuWro) events change W
     bin; 29–37 events are NaN under CVU (`README-gen5d-build.md:60-77`). It was kept deliberately (`:76-77`).
   - GiBUU is not evaluable.
   - P:131 states only "struck-nucleon mass", which is true of the analysis and false of the predictions. The
     paper does not say the predictions differ.
2. **Two Q² conventions.**
   - Truth q3 uses the exact `mc_Q2 = −(k−k′)²`.
   - Truth W uses the massless `4EνEμ sin²(θ/2)` (CVU:389-394).
   - Reco q3 and W use the exact, mass-including Q² (CVU:213-215, 232-234).
   - P:131 and `sec_eavailw.tex:22` write W with an unqualified "Q²". The same issue was flagged at
     `DESIGN-20260911-endpoint-B-generator-comparison-test.md:466-470`.
3. **Truth θ axis unverified.**
   - Generators measure pT, p∥ and θ about the true neutrino direction (+z).
   - The analysis uses MAT `GetThetalepTrue`, whose reference axis (beam-corrected or detector z) is not in the
     repo or any record found.
   - Analysis truth q3 uses the true neutrino vector via `mc_Q2`.
   - If the θ axis is not the neutrino direction, the analysis truth (pT, p∥) and the generators' differ by that
     tilt, and truth W is no longer an exact function of (pT, p∥, q3) (§3).
4. **Targets differ.**
   - The data and MnvTune are per tracker nucleon (CH plus the MC geometry, `isMC=true`).
   - GENIE is per (C12+H1)/13.
   - NuWro and GiBUU are per C12 nucleon: no hydrogen, so no free-proton contribution.
   - The paper says "on carbon" (P:165-166) but does not state the per-nucleon consequence.
   - Separately, `sbatch_nuwro_mefhc.sh:15` comments "numu-on-CH" while the configuration is C12.
5. **The truth denominator drops truth-W-NaN rows, but the signal definition does not.** The 5D truth sample is
   therefore not exactly the §1 signal (`und:333-335`). The effect is O(10) events per million in generator
   samples. It is not measured on the analysis MC in any record found.
6. **Note wording.**
   - `sec_5d.tex:171` calls J "109 supported **fine** joint cells". J is the coarse 3⁵ partition.
   - `sec_3d.tex:226-228` says GiBUU uses "the same flux and phase space", which `:248-251` and `KNOWN_ISSUES.md`
     82 contradict.
7. **Paper omissions blocking self-containment (not contradictions):**
   - Muon kinematic limits and fiducial box (§1).
   - The full reco cut list and window (§2).
   - Truth and reco q3 formulas, and reco W with M̄ = (1.5M_n+M_p)/2.5 (the note says only "average nucleon mass", `sec_eavailw.tex:25`).
   - The algebraic dependence `W_reco² = (M̄+q0)² − q3²` and the truth analogue.
   - Φ = 6.243e-4 m⁻²/POT over 0–100 GeV, N = 3.2353e30, POT and c ≡ 1 in the extraction formula.
   - The ≥1000 support rule and the J-edge rule.
   - That every prediction is binned by the same fine-grid-to-J map.
8. **The truth-W residual is unmeasured.** No record measures how far truth W departs from the (pT, p∥, q3)
   relation (`EVIDENCE-MAP-20261019.md:267`). The "tens of MeV" wording elsewhere has no measurement behind it.
