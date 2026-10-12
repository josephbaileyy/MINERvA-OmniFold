# Literature report: is a constrained inelastic-physics improvement motivated for the ME-FHC 5D "corner" excess?

Compiled 2026-10-11 from four parallel read-only research lanes. The lane notes, with fuller quotes, are in this
directory: `laneA123.md`, `laneA456E.md`, `laneB.md`, `laneCD.md`. Downloaded texts are in `pdfA/` and `dl/`.
Nothing was written to any git repository and no one was contacted.

**Tags.**
- [VERIFIED-READ]: the passage was read, either in the arXiv HTML, in pdftotext of the arXiv PDF, or in source code.
  Quotes from HTML pages fetched through the summarising fetch tool are near-verbatim. Quotes from pdftotext and from
  code are exact.
- [SEARCH-SNIPPET]: seen only in a search result or abstract listing.
- "PREPRINT": no journal reference was found.

**Context numbers** (from the brief, not re-measured here):

| Prediction | Corner data/pred | Total data/pred | Corner/total |
|---|---|---|---|
| GENIE 2.12.10 CV | 1.142 | 1.110 | 1.029 |
| GENIE 2.12.10 + MEC | 1.139 | 1.068 | 1.066 |
| NuWro 21.09 | 1.160 | 1.153 | 1.006 |
| GiBUU 2019 | 1.607 | 1.386 | 1.159 |

The corner is E_avail >= 0.8 GeV and W >= 1.8 GeV. The GiBUU sample is cap-limited at 20 GeV.

---

## ID corrections (several IDs in the brief point to other papers) [VERIFIED-READ]
- arXiv:0812.4543 is NOMAD *quasi-elastic* (EPJC 63, 355, 2009). The NOMAD inclusive paper is **arXiv:0711.1183**, PLB 660 (2008) 19.
- arXiv:0911.2310 is a cosmology paper. MINOS inclusive is **arXiv:0910.2201v2** (26 Mar 2010), PRD 81, 072002.
- arXiv:1607.00704 is the MINERvA **NuMI flux** paper (Aliaga et al., PRD 94, 092005). The LE inclusive-vs-E_nu result
  is **DeVan et al., arXiv:1610.04746v1** (15 Oct 2016), PRD 94, 112007.
- arXiv:2609.22662 **exists**. It is Diurba, Dytman, King, Liu, "Benchmarking Nucleon Production in Hadron Interactions
  Relevant for GeV-scale Neutrino Experiments" (v1 19 Sep 2026, v2 23 Sep 2026, PREPRINT).
- "Zazueta 2023 ME DIS nuclear targets" was **not found**.
  - Searches covered: an arXiv API query (abs:MINERvA AND "deep inelastic", 8 hits) and the MINERvA publications page
    (2021+).
  - Zazueta's 2022 first-author paper is the nu-e flux constraint, arXiv:2209.05540.
  - Theses and talks were not searched.

---

## A. Inelastic rate / RES-SIS-DIS matching

### A1. GENIE v3 bare-nucleon tune: Tena-Vidal et al., arXiv:2104.09179v2 (20 Apr 2021), PRD 104, 072009 (2021) [VERIFIED-READ, pdftotext]

**Model (Eq. 1, Sec. II).** Below W_cut the model is RES plus nonresonant background (NRB). The NRB is the BY/KNO DIS
cross section times R_ij multiplicity weights. At W >= W_cut the model is DIS only. Quote: "The nominal value is set to
Wcut = 1.7 GeV/c2".

**Defaults (Table III, stated to be the GENIE v2 nominal values).**
- W_cut 1.7, allowed range [1.5, 2.3].
- R^vp_CC1pi 0.10, R^vp_CC2pi 1.00, R^vn_CC1pi 0.30, R^vn_CC2pi 1.00.
- S_RES 1.0.
- S_DIS (DIS-CC-XSecScale) 1.032, with prior 1 +- 0.05.

**Data (Sec. IV.A, Table II).**
- H2 and D2 bubble-chamber data from ANL 12FT, BNL 7FT, FNAL 15FT and BEBC.
- Channels: CC inclusive, CCQE, CC1pi, and CC2pi (ANL only).
- 169 points. Points with E_nu < 0.5 GeV are removed, and a 15% systematic is added.
- The fit also floats per-experiment flux nuisances (Table VII). For example f_BEBC(nu_mu) = 0.86 +- 0.03 (G18_02a).
  The bubble-chamber normalisations are therefore only known to about 10-15%.

**Global fit (Table VI).** Values are G18_02a, with G18_01a in brackets.

| Parameter | G18_02a (G18_01a) | v2 default |
|---|---|---|
| W_cut | **1.81** (1.94) | 1.7 |
| R^vp_CC1pi | **0.008**, fixed (0.06) | 0.10 |
| R^vp_CC2pi | 0.94 (1.1) | 1.00 |
| R^vn_CC1pi | **0.03** (0.14) | 0.30 |
| R^vn_CC2pi | **2.3** (2.8) | 1.00 |
| S_RES | **0.84** (0.89) | 1.0 |
| S_DIS | **1.06** (1.03) | 1.032 |

**Tension between datasets.**
- Sec. VI.A, Table V: an inclusive-only fit gives W_cut 1.52 (at its edge). An exclusive-only fit gives W_cut 2.00
  (pinned at its maximum) and R^vn_CC2pi = 3.19.
  - Quote: "This is a tension between exclusive and inclusive datasets as the inclusive prefer a lower value in that
    Eν region" (1-10 GeV).
- Sec. V.C, on the S_DIS prior: without it, "the SIS region data would prefer much higher cross-section values for the
  DIS contribution".

**Effect on the cross section (Sec. VI.B).**
- "...this translates into a decrease of both νµ and ν̄µ CC inclusive cross section in the 0.5-10 GeV region, see Fig. 8".
- At higher energies the cross section "has barely changed".
- The decrease is "driven mainly by one pion production data".
- **No percent change at 5-20 GeV is quoted.**
- Fig. 6: chi2 against all inclusive data (including NOMAD, MINOS, CCFR, SKAT) is 119/143 for the G18_02a default and
  95.2/143 for the inclusive tune.

**Net vs v2.**
- DIS above W_cut: +2.9% (1.062213/1.032; the code value is in A2).
- The 1.7-1.81 GeV slice moves from DIS into RES+NRB, where the NRB 1pi is nearly zeroed and S_RES = 0.84.
- So the 02_11b tune **lowers 1.4-1.8 and raises W >= 1.81 by about 3%**.

### A2. Official GENIE 3.x tunes [VERIFIED-READ, GENIE-MC/Generator master @ 1fed28f2, 2026-10-08]

**02_11b values in code.** `config/G18_02a/G18_02a_02_11b/CommonParam.xml` has:
- DIS-CC-XSecScale 1.062213, RES-CC-XSecScale 0.838730, Wcut 1.809.
- HMultWgt vp-m2 0.008, vp-m3 0.943, vn-m2 0.0308, vn-m3 2.338.

**Later tunes carry the same inelastic parameters.**
- AR23_20i, AR23_20i_01_00x, AR25_20i, N24_20i_02_11b and G24_20i_06_22c all carry **identical** DIS/RES scales, W_cut
  and R_ij.
- The AR23 README says pion-production parameters "are taken from the G18_10a_02_11b tune".

**G24_20i_06_22c** (Li et al., TKI tune, arXiv:2404.08510v3, PRD 110, 072016 (2024)) changes only nuclear and FSI
parameters:
- FSI-Nucleon-FracAbsScale 0.250
- FSI-Nucleon-FracPiProdScale 2.05
- FSI-NeutralPion-MFPScale 0.221
- FSI-Pion-FracCExScale 0.257
- SRC fraction 0.151

These shift the hadronic energy partition (see B).

**CC0pi nuclear tune** (arXiv:2206.11050v3, 17 Oct 2022, PRD 106, 112001):
- "The SRES parameter is the only SIS parameter included in the CC0π tune".
- Table V gives S_RES 0.84-0.86.
- It makes **no DIS change**.

**Release notes.** v3.4.0 (10 Mar 2023) adds AR23; v3.6.0 (10 Jan 2025) adds N24 and G24. None reports a DIS or high-W
renormalisation beyond 02_11b.

**Conclusion.** No official GENIE 3.x tune changes high-W/DIS inclusive normalisation beyond the roughly +3% of the
H/D tune 02_11b.

### A3. Bodek-Yang-Xu: arXiv:2108.09240v2 (1 Oct 2021), "Submitted to EPJC", PREPRINT (no journal ref on INSPIRE) [VERIFIED-READ, PDF]

Proceedings: arXiv:2203.01867.

**Baseline.** Sec. 1/14: "The current (2016) version of the GENIE neutrino generator is using the NUINT04 version of the
model", which assumes axial = vector ("Type I").

**Sign of the change.**
- Sec. 11.1: Type I "underestimates the neutrino cross section at low Q2".
- Type II is adopted, with an axial valence K-factor (Q2+0.054)/(Q2+0.18) (Eq. 51; = 0.3 at Q2 = 0) and a sea
  K-factor (Q2+0.41)/(Q2+0.75) (Eq. 47).
- 30% of the Type I/Type II difference is taken as the axial uncertainty (Sec. 11.2).

**Size (Table 5, 40 GeV, isoscalar Fe).**

| sigma/E (1e-38 cm2/GeV) | Type I | Type II | World average | Change |
|---|---|---|---|---|
| nu | 0.656 | 0.674 | 0.675 | **+2.7%** |
| nubar | 0.311 | 0.327 | — | +5.1% |

**No table at 5-20 GeV.** Only the Fig. 17 curves exist, and they were not digitised.

**Share of sigma_tot by W region (Table 4, nu-Fe).**

| E_nu | W > 1.8 | 1.4 < W < 1.8 |
|---|---|---|
| 3 GeV | 25.2% | 31.3% |
| 5 GeV | 48.1% | 22.2% |
| 10 GeV | 72.8% | 13.4% |
| 40 GeV | 90.4% | 6.5% |

**Status in GENIE.** GENIE-MC/Generator PR #465 "Bodek Yang Model Update" was MERGED on 2026-10-03 (merge commit
a8c093ca).
- It adds BY21StrucFunc / BY21DISNuclearModel and a "BY2021" option.
- The option is commented out in G18_10a/ModelConfiguration.xml.
- It is **absent from release R-3_06_02**.
- It is not the default anywhere, and no validation numbers have been published.

**Sign.** The nu inelastic cross section goes **up**, concentrated at low Q2, by about 3% in sigma_tot at high E.

### A4. Inclusive sigma/E at 3-20 GeV [VERIFIED-READ unless noted]

**NOMAD** (arXiv:0711.1183, PLB 660, 19).
- Isoscalar C. Normalised to the >40 GeV world average "(0.677 ± 0.014)Eν".
- Table 3, sigma/E (1e-38 cm2/GeV): 0.763 ± 0.038 @6.5 GeV; 0.716 @9.5; 0.706 ± 0.026 @10.5; 0.698 ± 0.025 @16.2;
  0.700 ± 0.025 @18.7.

**MINOS** (arXiv:0910.2201v2, PRD 81, 072002).
- Fe, isoscalar-corrected. Normalised to 0.675 at 30-50 GeV.
- Table III: 0.708 ± 0.032 @5.89; 0.722 @7.97; 0.699 ± 0.043 @10.45; 0.691 @13.43; 0.708 ± 0.020 @16.42;
  0.689 ± 0.016 @19.87.

**MINERvA LE** (DeVan, arXiv:1610.04746, PRD 94, 112007; GENIE 2.6.2).
- The flux is normalised "such that the extracted inclusive charged-current cross section matches the world average
  between 9 and 12 GeV" (NOMAD, 3.6%).
- **So it cannot test the absolute 9-12 GeV generator normalisation.**
- Conclusion: the total cross sections "agree with the genie simulation ... within their uncertainties".

**GENIE v3 tune, Fig. 8a** (visual read, not digitised). The v2-like G18_02a default (S_DIS 1.032) sits at about
0.72-0.75 at 5-10 GeV, which is at or slightly *above* NOMAD/MINOS.

**PDG 2025, Ch. 52** (Zeller, rev. Aug 2025).
- World average sigma/E = 0.677 (nu), 0.334 (nubar), in 1e-38 cm2/GeV.
- No generator curve.
- No MINERvA ME inclusive-vs-E_nu paper is listed.

**T2K INGRID** (arXiv:1509.06940, PRD 93, 072002) covers 1.1-3.3 GeV only. **ArgoNeuT** (arXiv:1404.4809, PRD 89,
112003) is at <E> 9.6 GeV and gives differential results only. Both are [SEARCH-SNIPPET] and not useful for the 5-20
GeV normalisation.

**Verdict.** There is **no evidence that GENIE 2.12-type models under-predict isoscalar sigma/E at 5-20 GeV by ~10%**.
World data sit at 0.69-0.76 with 2-5% errors, and the v2 default matches them or is slightly high.

**The ME flux constraint is the most decision-relevant item in A4.**
- arXiv:1906.00111v4 (PRD 100, 092001), Sec. VII: the nu-e constraint shifts the "predicted neutrino flux between 2 and
  20 GeV ... down by 9.6%".
- arXiv:2209.05540v1 (PRD 107, 012001), Sec. VII: the combined nu-e + IMD constraint is "lowering the neutrino flux
  predictions", with the uncertainty going from 7.6% to 3.3%.
- **A uniform ~10% excess in the total (1.110) is the size of this flux shift.** Which flux the unfolding uses is a
  first-order question (see Implications).

**Not accessed.** The ME low-nu thesis (R. Fine, FERMILAB-THESIS-2020-14) was blocked by Cloudflare. No published ME
sigma(E_nu) paper was found.

### A5. Generator changes after NuWro 21.09 / GiBUU 2019

**NuWro** (github.com/NuWro/nuwro releases and `params.txt`) [VERIFIED-READ].
- Tag nuwro_21.09: `res_dis_cut = 1600`, `mec_kind = 3`.
- NuWro_25_03 and master:
  - `res_kind = 2 //the new hybrid model` (Ghent Hybrid, arXiv:2405.05212v4, JHEP 12 (2024) 141)
  - `res_dis_cut = 1900`, with blending from 1600 to 1900 MeV
  - `mec_kind = 6`
- Releases 25.03 and 25.11 change the SPP model, MEC and the spectral function. **No release note mentions DIS, PYTHIA or
  hadronisation.**
- The 1.6-1.9 GeV population therefore changes relative to 21.09, which straddles our W = 1.8 boundary. No
  total-rate-change number is published.

**GiBUU 25p1** (Yan et al., arXiv:2507.20539v2, accepted to PRD per the lane; no journal ref confirmed) [VERIFIED-READ].
- Sec. II.A: "DIS sets in at W = 2 GeV". For 2-3 GeV the rate is Bosted-Christy with Pythia final states; above 3 GeV
  it is Pythia only.
- The background structure function is scaled by 2(T+1) (Eq. 1). In version 2025, T is split into T1 (one-body) and
  T2 (2p2h), with defaults T1 = T2 = 1.
- Sec. IV: "The newly introduced 2πBG". By contrast, the 2016 GiBUU paper (arXiv:1605.09391, PRC 94, 035502, Sec. II.B)
  says the neutrino 2pi background is absent "because of the absence of any experimental information".
- **Fig. 5a** against MINERvA LE inclusive:
  - T1 = 1 gives chi2 = 7.8/15.
  - **T1 = 0 gives chi2 = 164.6/15**, about 30% low at 5-10 GeV (visual).
  - Quote: "MINERvA data in Fig. 5a strongly favor T1 = 1 over T1 = 0 ... (2 < Eν < 30 GeV), pion background and SIS
    contributions play a major role".
- **Inference, not verified.** The GiBUU 2019 sample may lack the 2pi background or have T = 0. That would explain much
  of its 1.386 total deficit independently of the 20 GeV cap. **Check the 2019 jobcard.**
- The GiBUU hepforge release notes were blocked by bot protection.

### A6. Sajjad Athar & Morfín: arXiv:2006.08603v1 (13 Jun 2020), J. Phys. G 48, 034001 (2021) [VERIFIED-READ]

- Abstract: SIS-to-DIS transition studies "have hardly begun".
- Sec. 4.3: GENIE estimates "the sum of non-resonant pion as well as multi-pion resonant production with this
  extrapolation from DIS".
  - "There is unfortunately very limited experimental data to compare with their predictions in this low-Q2, low-W
    region".
  - A "smooth extrapolation of the strength in the DIS region tends to overshoot the model predictions for the strength
    in the SIS region".
- Sec. 4.4: Fig. 27 shows NEUT 5.4.0, GENIE 2.12.10 and NuWro 18.02.1 disagreeing for 6 GeV nu-Fe.
  - Only "restricted studies by MINERνA ... (W ≤ 1.8 GeV)" exist, "and nothing for the interesting transition to DIS at
    even higher W".
  - Duality "is roughly observed for the average nucleon ... but ... not ... for neutrons and protons individually".
- **No numerical double-counting estimate is given.** The double-counting risk is structural: BY-extrapolated NRB is added
  on top of RES below W_cut.

---

## B. Hadronisation, energy partition, FSI at high W

### B1. AGKY retune: Tena-Vidal et al., arXiv:2106.05884 (v1 10 Jun 2021, v2 2 Dec 2021), PRD 105, 012009 (2022) [VERIFIED-READ]

**Inputs.**
- Fitted only to *averaged charged multiplicity* from FNAL 15ft and BEBC, on H2 and D2, nu and nubar (Tables 3, 4, 8).
- **No pi0 or energy data are fitted.**
- The KNO-to-PYTHIA transition (2.3-3.0 GeV) is fixed.

**Parameter changes (Table 7, 2010 → 2021 global).**
- Lund a 0.30 → 1.53 ± 0.13
- Lund b 0.58 → 1.16 ± 0.09
- alpha_nun -0.20 → 1.75
- The D2-only fit gives alpha_nun -0.58 ± 0.07.

**H vs D tension.**
- Global chi2 goes 486 → 242 for 109 dof (p = 4e-12).
- Sec. VIII: the global tune "underpredicts the deuterium data at the PYTHIA region".

**Effects.**
- Sec. VIII: "increase of the averaged charged multiplicity for W² > 10 GeV²/c⁴".
- The implied rise of <n_pi0> "is incompatible with the data, as demonstrated in Fig. 20" (BEBC D2, Sec. VII.3).
- Sec. VII.4 / Fig. 23: "an increase of CC inclusive cross section is observed, for both νµ and ν̄µ" in the SIS region.
  - 2pi production goes up while 1pi barely changes.
  - "the agreement with inclusive and νµ CC π+π− data is lost".
  - The tune is "more appropriate at higher energies where the contribution of the SIS region is not relevant".
  - **No percentage is given.**

**Release.** GENIE v3.2.0 as G18_02a_03_330 (global) and G18_02a_03_320 (D2-only), built on G18_02a_02_11a.

**Typo to avoid quoting.** Eq. 2 is <n> = 1.5<n_ch>, but the text says "<n_ch> ∼ 0.5<n_π0>", which is almost certainly
inverted.

**Missing.** Nothing is said about the pi0-vs-charged energy fraction or about visible energy.

### B2. FSI model comparisons

**Diurba, Dytman, King, Liu, arXiv:2609.22662v2 (23 Sep 2026), PREPRINT** [VERIFIED-READ].
- Setup: GENIE v3.4.2 with hA2018, hN2018, INCL++ 5.2.9.5 and Geant4 Bertini. Probes are single pi±, pi0, p and n with
  T = 0.05-2 GeV on C, O, Ar and Fe.
- **Eq. 1 E_vis** (proton KE + meson and photon total energy, neutrons excluded) **is our E_avail construction.**
  **CORRECTED 2026-10-11 (close-out, owner re-opened the PDF): it is not.** Eq. (1) uses total energies for π±
  and kaons; our A uses π± kinetic energy, π⁰ total energy and no kaons (`docs/EAVAIL_DEFINITION.md`). The paper's
  nucleon counts use a 5 MeV/nucleon threshold (30 MeV in Tables I–II). See REPORT §6.2.
- Table 1, pi+ on 40Ar at 239 MeV, absorption (mb):

  | Data | hA2018 | hN2018 | INCL++ | G4 Bertini |
  |---|---|---|---|---|
  | 101.7 ± 6.3 | 118.0 | 69.2 | 96.9 | 120.8 |
- Model behaviour:
  - hN2018 shows "negative energy bias and the highest average number of nucleons produced at energies greater than
    0.50 GeV".
  - There is "an unphysical population of interactions with more visible energy than the energy of the incident
    hadron" (Sec. IV, Fig. 10).
- Against MINERvA CC0pi (AR23): "similar agreement with data" across the hadron models.
- **It gives no fraction of omega lost at omega ≈ 1-5 GeV**; the bias sizes are only in Figs. 1, 2 and 10, which were not
  read numerically.

**Dytman et al., arXiv:2103.07535v2 (9 Sep 2021), PRD 104, 053006** [VERIFIED-READ].
- A transparency study focused on T <= 1 GeV. Quote: "formation time/zone effects are included in DIS events, therefore
  not included in the main results".
- Fig. 18 (pions to 4 GeV, formation length removed): "this is an indication that the formation length derived from
  neutrino data is not needed to describe data".
- No neutron-energy-loss number is given.

**Liu, Munteanu, Dolan, arXiv:2511.03964v3 (17 Apr 2026)** [VERIFIED-READ]. DUNE flux on Ar.
- "Changing the FSI model varies the number of (anti)neutrino events with more than 10% relative bias by about 30%
  (20%)".
- The bias is "primarily driven by the amount of the interaction energy carried away by neutrons".

**Friedland & Li, arXiv:1811.06159v3, PRD 99, 036009 (2019)** [VERIFIED-READ]. GENIE + FLUKA on Ar.
- "at neutrino energies of 3-4 GeV the average hadronic energy becomes approximately equipartitioned between ... p, n, π+
  and π0".
- Ar has N/Z ≈ 1.2, so the neutron share is larger than in CH.

**Golan, arXiv:1402.1608v1 (7 Feb 2014)** [VERIFIED-READ]. On old generator versions, NuWro's formation zone
"significantly decreases a number of re-interactions and it results lower energy loss ... The highest energy loss is
predicted by NEUT".

**Not found.** No model-comparison number for the fraction of omega going to neutrons and binding at omega ≈ 1-5 GeV on
carbon.

### B3. Formation zone

**GENIE** (manual arXiv:1510.05494) [VERIFIED-READ].
- Quote: "free step ... formation time of 0.342 fm/c according to the SKAT model". The formation length is
  f_z = p c tau0/m (Eq. 9.6), applied to all DIS hadrons.
- The reweight knob is ±50% (Table 9.2).
- A snippet quotes 0.523 fm/c; which value is current is unresolved [SEARCH-SNIPPET].

**NuWro** (Golan, Juszczak, Sobczyk, arXiv:1202.4197, PRC 86, 015505) [VERIFIED-READ].
- The Ranft model is used for DIS, with tau fixed from NOMAD backward pions.
- There is a "smooth transition" from Delta propagation at W ~ 1.6 GeV.
- The paper notes that GENIE applies the formation zone also to RES-region NRB events.

**GiBUU** (arXiv:1303.6677v2) [VERIFIED-READ].
- In the resonance region tau = 1/Gamma.
- In SIS/DIS the prehadron cross section rises linearly in time, tuned to attenuation data at "about 10 to 200 GeV".
- In E665 μ-Pb (PRC 101, 014617), the prescription changes the neutron multiplicity by up to about 2x [SEARCH-SNIPPET].

**Not found.** No paper quantifies the formation-zone effect on visible energy at W > 1.8 on C.

**Sign.** A longer formation zone means fewer reinteractions, so less omega goes to neutrons and binding and the visible
fraction is higher.
**CORRECTED 2026-10-11 (close-out):** this holds only channel by channel. Fewer π± absorptions into pp, fewer
neutron-induced proton knockouts and less π± → π⁰ exchange each *lower* our A; the net sign is not determined
(REPORT §6.2 table).

### B4. MINERvA constraints on hadronic partition

**Test beam, arXiv:1501.06431v2 (8 Apr 2015), NIM A 789, 28-42 (2015)** [VERIFIED-READ in lane B; the journal ref is
from the MINERvA publications page].
- Beam: p, pi± and e at 0.35-2.0 GeV/c. **No neutrons.**
- "within 4% averaging the points up to 1.0 GeV, and 3% from there up to 2.0 GeV".
- Absolute scale "up to 4.2%".
- Protons and pions "4%"; electrons similar.

**All MINERvA neutrino pion measurements cut on W, so none reaches the corner** [VERIFIED-READ].

| Paper | Channel | W cut | Result |
|---|---|---|---|
| McGivern, arXiv:1606.07127, PRD 94, 052005 | CC pi± | W < 1.8 | data below some generators by 1-2 sigma |
| Altinok, arXiv:1708.03723, PRD 96, 072003 | CC pi0 | W_exp < 1.8 | — |
| Granados, arXiv:2605.24224 (PREPRINT, 2026) | CC1pi+ | W < 1.4 | discrepancies up to 15% (muon) and 20% (pion) |

**Neutron measurements** are antineutrino, low recoil only.
- Elkins, arXiv:1901.04892v2, PRD 100, 052002: q3 < 0.8. The simulation "overpredicts the number of candidates by 15%".
- Olivier, arXiv:2310.17014v2, PRD 108, 112010: multi-neutron production at low E_avail disagrees with models.

**Not found.**
- A MINERvA multi-pi0 measurement.
- Any W > 1.8 hadronic-composition measurement.
- A neutrino E_avail measurement on C/Fe/Pb.
- The nearest is Klustová et al., arXiv:2604.07091v2 (7 Oct 2026, PREPRINT): nubar inclusive vs p_T on C/CH/Fe/Pb, with
  "significant discrepancies in the pT dependence".

---

## C. Response / estimator

### C1. Hadronic calorimetric response uncertainty, ME era

**Ruterbories et al., arXiv:2106.16210v4 (2 Nov 2022), PRD 104, 092007 (2021)** [VERIFIED-READ].
- Sec. V gives no per-species values: "Uncertainty in the detector response to hadrons is evaluated using shifts
  determined by in situ measurements".
- Recoil does not enter the observables, only the low-recoil (<800 MeV) muon-scale fit.
- The dominant uncertainties are the muon energy scale (1%), flux ("below 4% for almost all the phase space") and target
  count (1.4%).

**Ascencio et al., arXiv:2110.13372v2 (25 Jul 2022), PRD 106, 032001** [VERIFIED-READ].
- Sec. VI: "The hadronic energy uncertainty varies throughout the distribution and rises to 10% at high 0.9<q3<1.2 GeV".
- No per-species values are given.

**Per-species values in the MINERvA toolkit**: MAT-MINERvA `utilities/ParticleResponseDefaults.h` @ 5bf46c53 [VERIFIED-READ, code].

| Species | Fractional uncertainty |
|---|---|
| Proton | **3.5%** (4 / 3.5 / 3% for low / mid / high T) |
| Meson (pi±) | **5%** |
| EM (pi0, gamma, e) | **3%** |
| Neutron | 25 / 10 / 20% |
| Other | 20% |
| Muon | 2.4% |

**LE precedent** (DeVan, arXiv:1610.04746) [VERIFIED-READ].
- Proton 10%, meson 5%, EM 3%, neutron 15%. These come from an older simulation (footnote 4).
- "At high ν, where the majority of the recoil energy is carried by charged and neutral pions, the uncertainty
  approaches 6%".

**Reading.** E_avail at high W is mostly pi± and pi0, so the response uncertainty on it is **about 3-5%**. See the
Implications for how this maps into corner migration.

---

## D. MINERvA SIS/DIS selections and overlap

### D1. SIS: Lozano et al., arXiv:2503.20043v1 (25 Mar 2025); published PRD 114, 072001 (2026), DOI 10.1103/vq38-kmxq

The journal reference is from the INSPIRE API; the journal text was not read. The rest is [VERIFIED-READ, arXiv HTML].

**Data.** ME NuMI. nu mode 1.06e21 POT, nubar 1.12e21 POT. Active-tracker CH, 5.48 t fiducial (modules 27-80, apothem
850 mm). Playlists are not named.

**Selection (Sec. IV.2).**
- 2 < E_mu < 20 GeV, theta_mu < 20°, MINOS-matched.
- **1.5 < W_reco < 2 GeV**. Definition I has no Q2 cut; **definition II adds Q2 >= 1 GeV2**.
- No pion requirement and no hadron veto.
- W = sqrt(M2 + 2M E_had - Q2), with calorimetric E_had "includ[ing] corrections ... to compensate for the loss of
  detectable energy due to final state interactions, neutral particles". This is a total-omega estimator, not E_avail.
- Selected nu events: 617,953 (I) and 174,089 (II). Purity 65.8% / 52.9%.

**Truth signal.** CC on CH with the same W/theta/E_mu cuts; Q2 >= 0 (I) or >= 1 (II).

**Generators compared.**
- GENIE 2.12.6 untuned; MINERvA Tune v1; Tune v2; and "v2 minus nonres-pion reduction".
- GENIE 3.0.6 G18_02a_02_11a and G18_10a_02_11a.
- NEUT 5.4.1, NuWro 19.02, GiBUU 2021.
- The paper describes Tune v1 as "MINERvA Tune v2 without the reduction in pion production at low Q²".

**Results.**
- Sec. VII.1.2: "the underpredictions of Tune v2 compared to data are significant and growing" with Q2 and p_T.
- Sec. VII.3: the deficit persists "even with the nonresonant subtraction removed" and is tied to the GENIE DIS Q2
  dependence (Tune v2 is about 75% DIS in this window).
- Sec. VIII recommends that "the large reduction in nonresonant pion production in MINERvA tunes be modified". Without
  that reduction, GENIE 2.12.6 is "considerably superior at high Q²".
- GiBUU 2021 and NEUT overpredict at low Q2. NuWro 19.02 is "mildly underpredicting".
- chi2/ndf:

  | Fit | Model | Q2 | p_T | p_par | x |
  |---|---|---|---|---|---|
  | Def I, nu | Tune v2 | 4.8 | 4.0 | 14.1 | — |
  | Def I, nu | GENIE 2.12.6 | 18.7 | 14.7 | 18.2 | — |
  | Def II, nu | Tune v2 | 4.8 | 4.5 | 7.3 | 3.6 |
  | Def II, nu | v2 minus nonres-pion reduction | 1.9 | 2.5 | 7.3 | 0.5 |

- **No numeric data/MC ratios appear in the text**; they are only in Figs. 9-13. The direction of the untuned GENIE
  2.12.6 disagreement is therefore not stated in the text I read.

**Overlap.** The data are the **same ME FHC exposure and tracker CH with the same MINOS-matched, theta < 20° muon
selection** as an inclusive tracker analysis. The SIS sample is effectively a W-slice subset and **is not statistically
independent** of our sample. This is an inference; playlist lists were not compared.

### D2. DIS

**Mousseau et al., arXiv:1601.06313v3 (30 Sep 2016), PRD 93, 071101 (2016)** [VERIFIED-READ, pdftotext].
- LE beam, 3.12e20 POT. GENIE with BY2003 + GRV98LO.
- Signal: Q2 >= 1, W >= 2 GeV, 5-50 GeV.
- **Table I sideband scale factors (stat only):**

  | Target | High-W / low-Q2 template (W_gen > 2, Q2_gen < 1) | Low-W template (W_gen < 2) |
  |---|---|---|
  | CH | **1.57 ± 0.02** | **0.94 ± 0.01** |
  | C | 1.58 | 0.90 |
  | Fe | 1.58 | 0.99 |
  | Pb | 1.36 | 0.95 |
- Quote: "The data tend to prefer a higher background rate at low Q2".
- The absolute flux uncertainty is about 20%, so the result is reported as ratios only.
- **The pattern (data far above GENIE at W > 2 / low Q2, slightly below at W < 2) has the same signs as our corner vs
  1.4-1.8 pattern.**
- Caveat: these are reco-template fit factors and may absorb migration.

**ME DIS nuclear-target paper: not found** (see the ID corrections).

**ME tracker DIS proxy** (Ruterbories, arXiv:2106.16210v4, Sec. VI / Fig. 14) [VERIFIED-READ].
- "At pt >> 0.85 GeV/c the Monte Carlo prediction consistently underpredicts the data by 10-25%".
- This region is "dominated by the 'True DIS' process for p∥ > 6 GeV/c".
- "Poorly understood neutrino DIS nuclear effects could contribute to the underprediction".
- In contrast: "For p∥ between 3 and 15 GeV and low values of pt, the cross section is overpredicted".
- Table 1 chi2 (205 dof): Tune v1 6786, GENIE 2.12.6 8241, NuWro LFG 3789 (best), GiBUU 2019 5800.
- **Same exposure as our sample.**

### D3. Ascencio ME low-recoil, high-q3 region

- "The measurement region is limited to q3 < 1.2 GeV" [VERIFIED-READ].
- For a stationary nucleon, W^2 <= M^2 + 2M q3 = 3.13 GeV2, so **W <= 1.77 GeV**. This is our arithmetic. The
  measurement **cannot reach the corner** but overlaps the 1.4-1.8 region.
- At high E_avail: "NuWro goes from overestimating the data to systematically underestimating it", and the modified
  GENIE models are "close to the data" [VERIFIED-READ].
- The chi2 appendix was not read.

### D4. Inclusive sigma vs E_nu from MINERvA

- **LE:** DeVan, arXiv:1610.04746. The 9-12 GeV level is an input, not a test (see A4).
  - The eta factors of 0.925-0.958 (nu) mean the low-nu data prefer a lower low-nu cross section than GENIE 2.6.2.
- **ME:** no sigma(E_nu) paper was found.
  - Bashyal et al., arXiv:2104.05769v5, JINST 16 P08068: the low-nu fit finds "the energy scale of muons reconstructed
    in the MINOS detector is shifted by 3.6%", with flux parameters inside the prior band [VERIFIED-READ abstract].
- **There is no MINERvA statement that data/GENIE exceeds 1 at 5-20 GeV in sigma(E_nu).**

---

## E. Elementary data

**sigma(nu n)/sigma(nu p), CC.**
- BEBC D2 (Allasia et al., NPB 239, 301, 1984): 2.10 ± 0.08 ± 0.22.
- BNL 7-ft D2 (Baker et al., PRD 25, 617, 1982): 1.95 ± 0.10 at about 3.7 GeV, with sigma_n/E = 1.07, sigma_p/E = 0.54
  (1e-38). "Above 1.6 GeV the data are consistent with the quark-parton model".
- Both are [SEARCH-SNIPPET / OSTI abstract]. **R ≈ 2.**

**CH implication.** CH has "a 15% excess of protons over neutrons" (DeVan) [VERIFIED-READ]. With R = 2, the per-nucleon
DIS rate on CH is about 0.974 × isoscalar (our arithmetic). Generators include this already, so it is not a source of a
+10% excess.

**MINERvA hydrogen** (Cai et al., Nature 614, 48 (2023)). This is nubar p → mu+ n quasi-elastic only (axial radius
0.73 ± 0.17 fm) [SEARCH-SNIPPET]. **It does not constrain inelastic W > 1.8.**

**H/D inelastic data** (ANL, BNL, BEBC, FNAL 15ft) enter only via the GENIE v3 tune (A1) and AGKY (B1). Their fitted
flux nuisances of 0.86-1.2 mean the inelastic normalisation is only known to about 10-15% from these data.

---

## Implications

Our observed pattern, data/pred:
- Corner 1.14-1.16 (GENIE/NuWro).
- Total 1.07-1.15.
- 1.4 < W < 1.8: GENIE *above* data by about 9-12%.
- Corner excess beyond the uniform normalisation (corner/total): only +0.6% (NuWro) to +6.7% (GENIE+MEC).

### (i) Expected sign of each candidate's effect

The table gives the change in the *prediction*. "+" raises the prediction, i.e. moves data/pred toward 1 when data/pred > 1.

| Candidate | Corner | Total | 1.4<W<1.8 | Muon kinematics | Source |
|---|---|---|---|---|---|
| GENIE 02_11b H/D tune (S_DIS 1.032→1.062, S_RES 0.84, W_cut 1.81, R^1pi → ~0) | + (~3%) | − at <10 GeV, ≈0 above | **−** (right direction) | shifts weight to low-nu/high-Q2 inelastic; less RES-like | A1, A2 |
| BYX 2021 axial update | + (~3%, low-Q2 weighted) | + (~3%) | + via NRB (wrong direction for GENIE) | more low-Q2 → lower p_T muons | A3 |
| Larger generic DIS scale (fit to our corner) | + | + (W>1.8 is 50-73% of σ at 5-10 GeV) | + if R_ij × DIS NRB scales with it (wrong direction) | broad; high-Q2 high-p_T up (matches Ruterbories 10-25% deficit) | A1, D2 |
| Undo the Tune v1 nonres-pion reduction | + (W 1.8-2 slice) | + | + (wrong direction for 1.4-1.8 vs untuned GENIE) | high-Q2 up (Lozano prefers it) | D1 |
| AGKY 2021 hadronisation tune | + (more pions → more E_avail; SIS rate up) | + (SIS) | + (wrong direction; breaks CC pi+pi−) | small | B1 |
| Weaker FSI / longer formation zone / less neutron share | **+ (migration in E_avail at fixed ω)** — *CORRECTED 2026-10-11: sign channel-dependent, net not determined (REPORT §6.2)* | **0** | 0 in rate (E_avail-shape only; for a factorized post-vertex kernel at fixed primary dynamics, REPORT §5.1) | **0** | B2, B3 |
| Flux normalisation (nu-e/IMD constrained flux −9.6%) | data up uniformly (if used) | data up uniformly | data up uniformly (wrong direction there) | uniform | A4 |
| Detector hadronic response 3-5% (pi±, EM) | ± migration across E_avail = 0.8 and (if reco-omega) W = 1.8 | 0 | small ± | 0 | C1 |

**Key reading.**
1. The *uniform* part of the excess (about 7-15%) is degenerate with flux normalisation. It is not distinctive of
   inelastic physics, and world inclusive sigma/E data give no motivation for a 10% inelastic increase (A4).
   *CORRECTED 2026-10-11 (close-out): σ/E limits a rate change, not a redistribution in (Q², W) or between channels at
   fixed σ(E) (REPORT §4.2).*
2. The *shape* part (corner/total 1.006-1.067) is the size of the 02_11b DIS change (+3%), the BYX change (+3%) and the
   E_avail response systematic (3-5% scale, which migrates events at the 0.8 GeV edge).
3. Only the 02_11b-type re-partition (DIS up a little, RES/NRB down) has the right sign in all three regions
   simultaneously (corner +, 1.4-1.8 −, total ≈ flat or slightly −). It is already an official, H/D-constrained
   parameter set, so it is the most defensible "constrained" option.
   *Superseded in REPORT §6.1: the first-order emulation is wrong-signed at 1.8–2.2 GeV and in the Δ bin, and is not a
   GENIE v3 prediction.*
4. Two independent MINERvA observations point the same way (data above GENIE at high W):
   - Mousseau (LE): high-W/low-Q2 sideband ×1.57 vs low-W ×0.94.
   - Ruterbories (ME): high-p_T True-DIS region 10-25% above Tune v1.
   - Lozano SIS (ME, 1.5 < W < 2): Tune v2 under-predicts, more so at high Q2.
   - The Ruterbories and Lozano results share our exposure.
5. GiBUU 2019 should be excluded from any inelastic-normalisation inference. It is cap-limited, and GiBUU's own 2025
   paper shows the pre-2025 treatment (no 2pi background / T1 = 0 variant) is about 30% low at 5-10 GeV against MINERvA
   inclusive.

### (ii) Double-counting risks

- **Same events as external constraints.** Lozano SIS (D1) and Ruterbories inclusive (D2) use the same ME FHC tracker
  exposure and muon selection. Using them to "motivate" or fit a correction, then comparing to our unfolded data, is not
  an independent check, and joint fits need the shared-event covariance.
- **The DIS scale also moves the NRB.**
  - In GENIE the W < W_cut NRB is the DIS cross section × R_ij.
  - A DIS normalisation applied without adjusting R_ij also raises 1.4-1.8, where GENIE already overshoots.
  - Changing W_cut moves strength between RES+NRB and DIS (Athar-Morfín's structural double-counting issue).
  - Whether GENIE 2.12's DIS-CC-XSecScale also scales the NRB was **not verified in code**; check this.
- **Tuning on top of tunes.** 02_11b already absorbed the H/D inelastic data and was pulled by the S_DIS prior toward the
  NOMAD/MINOS inclusive level. Adding a further DIS scale fit to MINERvA re-uses the inclusive normalisation those priors
  encode.
  - AGKY (built on 02_11a) and the 02_11b R_ij both change SIS multiplicity/rates and are **not separable**.
  - BYX overlaps 02_11b's S_DIS, which was fit against the old BY.
- **Flux.** If the unfolding already uses the nu-e/IMD-constrained flux, the ~10% downward flux shift is already in the
  data. A uniform inelastic scale would then partially duplicate or mask a flux effect. Determine which flux the 5D
  result uses before attributing any uniform excess to physics.
- **Response vs physics.** An E_avail scale error (3-5%) and an FSI/visible-fraction change produce the *same* signature
  (corner up, total unchanged, muon unchanged).
  - Correcting the prediction for FSI while also carrying the response systematic in the data covariance is fine.
  - Tuning FSI to absorb what is a response bias is not.
- **MINERvA Tune v1's 2p2h/RPA** was fit at q3 < 1.2 (W < 1.77; Ascencio/Rodrigues). It does not reach the corner but
  overlaps 1.4-1.8, so inelastic changes there interact with the 2p2h tune's fitted strength.

### What could not be accessed or quantified
- Numeric values that exist only in figures were not digitised:
  - GENIE tune Fig. 8 (5-20 GeV % change)
  - AGKY Fig. 23 (% SIS increase)
  - BYX Fig. 17 (Type I vs Type II at 5-20 GeV)
  - Lozano Figs. 9-13 (data/MC ratios)
  - 2609.22662 Figs. 1, 2, 10 (energy bias)
- Not read: the R. Fine ME low-nu thesis (Cloudflare block) and the GiBUU hepforge release notes (bot protection).
- Journal-version texts were not read for Lozano (PRD 114, 072001) or the test-beam paper (NIM A 789, 28).
- No ME DIS nuclear-target paper was found.
- No paper quantifies the omega fraction lost to neutrons/binding at omega ≈ 1-5 GeV on carbon, or the formation-zone
  effect on visible energy at W > 1.8 on carbon.
