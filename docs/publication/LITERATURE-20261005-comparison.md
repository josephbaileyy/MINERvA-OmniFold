# Literature comparison for the publication decision (2026-10-05)

**CITABLE FOR:**
- what the cited works did;
- the exact sentences that support each comparison;
- the limits of the search.

**NOT CITABLE FOR:**
- a priority claim stronger than "to our knowledge, within the searched literature";
- anything marked UNVERIFIED.

**Method:**
- A background research agent searched arXiv (abstract API queries), INSPIRE, the APS author pages, the MINERvA
  publication and open-data pages, and the web, and returned verbatim quotations.
- This lane re-verified the load-bearing quotations against the source text:
  - the raw arXiv API abstracts of 2106.16210, 2504.06857, 2405.20041 and 2108.12376 (verified verbatim);
  - the extracted full text of 2106.16210, 2110.13372 and 1511.05944 for the detector-response passages (verified).
- Rows the lane did not re-verify are marked "agent-reported".
- Limits: arXiv and web indexes only. No internal notes, full conference proceedings or non-indexed theses.
  Collider results after mid-2025 were not systematically searched.

## 1. OmniFold and its applications

| work | what it did | dim | basis |
|---|---|---|---|
| Andreassen, Komiske, Metodiev, Nachman, Thaler, *OmniFold*, PRL 124, 182001 (2020), arXiv:1911.09107 | introduces the method; simulated LHC jet substructure | high-dim, simulation | agent-reported |
| Huang, Cudd, Kawaue, Kikawa, Nachman, Mikuni, Wilkinson, PRD 112, 012008 (2025), doi:10.1103/sp1f-n9k2, arXiv:2504.06857 | *"demonstrates OmniFold's application to a neutrino cross-section measurement for the first time using a public T2K near detector simulated dataset, comparing its performance with traditional approaches using a mock data study"* | 6 (μ + p), **simulation only** | **verified** (arXiv API) |
| H1, PRL 128, 132002 (2022), arXiv:2108.12376 | lepton-jet correlation on data; *"an unbinned machine learning algorithm OmniFold, which considers eight observables simultaneously in this first application"* | 8 | **verified** |
| ATLAS, PRL 133, 261803 (2024), arXiv:2405.20041 | *"a simultaneous measurement of twenty-four Z+jets observables"*, *"presented unbinned as a dataset of particle-level events"* | 24 | **verified** |
| CMS minimum-bias event shapes, PRD 112, 112006 (2025), arXiv:2505.17850 | *"None of the models investigated is able to satisfactorily describe the data."* | 8 | agent-reported |
| H1 jet substructure (PLB 2023); LHCb Z-tagged jets (PRD 2023); ATLAS track functions (PLB 2025); STAR (proceedings) | further real-data unbinned results | 4–10 | agent-reported, via the survey arXiv:2507.09582, Table 1 |
| Canelli *et al.*, *A Practical Guide to Unbinned Unfolding*, arXiv:2507.09582 | survey: real-data unbinned results from ATLAS, CMS, H1, LHCb and STAR, *"as well as a study on highly realistic simulation from one accelerator-based neutrino experiment, T2K"* (covers mid-2021 to mid-2025) | — | agent-reported |

**Search result:** no posted or published unbinned (OmniFold or other ML) unfolding of **real** neutrino data was
found. Neither the arXiv `all:OmniFold` query (15 entries) nor the MINERvA publication page shows one.

## 2. Multi-differential neutrino measurements on data (for dimensionality and generator tests)

| work | observables | dim | unfolding | generator statement |
|---|---|---|---|---|
| MINERvA, Ruterbories *et al.*, PRD 104, 092007 (2021), arXiv:2106.16210 (**our 2D reference**) | p_T, p∥ (inclusive, ME) | 2 | binned D'Agostini, 10 iterations | *"The results are not well modeled by several generator predictions using a variety of input models."* (**verified**, arXiv API). Compared with GENIE (2.12.6 variants), NuWro, GiBUU (2019 and 2021), NEUT. Table I gives the standard χ² over 205 d.o.f. for 17 variants. Read from the full text and **verified** by this lane: Tune v1 6786, GENIE 2.12.6 8241, GiBUU v2019 5800, GiBUU v2021 5594, NuWro SF 5151, NuWro LFG 3789; the range over all variants is 3789–12345. |
| MINERvA, Rodrigues *et al.*, PRL 116, 071802 (2016), arXiv:1511.05944 | E_avail, q3 (LE low recoil) | 2 | binned, 4 iterations | the established low-recoil excess (agent-reported) |
| MINERvA, Ascencio *et al.*, PRD 106, 032001 (2022), arXiv:2110.13372 | E_avail, q3 < 1.2 GeV (ME) | 2 | binned, 2 iterations | χ² over 44 d.o.f.: MnvTune-v1.2 963, v3 1101, NuWro SF 9982 (agent-reported) |
| MINERvA, Ruterbories *et al.*, PRL 129, 021803 (2022), arXiv:2203.08022 | p_T, p∥, ΣT_p (QE-like) | **3** | binned | *"the first measurement of the triple-differential cross section for νμ quasielastic-like reactions"* (agent-reported) |
| MicroBooNE, PLB 870, 139939 (2025), arXiv:2307.06413 | E_ν (or E_vis), cos θ_μ, P_μ (inclusive) | **3** | Wiener-SVD | *"in tension with all model CV predictions"* (agent-reported) |
| NOvA, arXiv:2603.06718 (2026) | ν̄_μ CC inclusive | **3** | binned | *"the first measurement of the triple-differential muon antineutrino charged-current inclusive cross section"* (agent-reported) |
| NOvA, PRD 107, 052011; T2K, PRD 98, 012004 and 032003 | inclusive and CC0π | 2 or more | binned | NOvA *"a clear discrepancy between the data and each of the tested predictions"* (agent-reported) |

**Search result:** the highest dimensionality found on unfolded neutrino data is **3**. No 4D or 5D neutrino
measurement was found. No neutrino paper read applies pseudo-experiment calibration through the full chain or
multiplicity-controlled rejection. They report covariance χ², "tension" or "not well modeled".

## 3. What this implies for novelty (the packet §5.1)

**Defensible, within the search limits above:**
- "To our knowledge, the first unbinned unfolding of neutrino-scattering **data**." The prior neutrino OmniFold
  work is a simulation study (row 2), so this is a data-application claim, never a first-use-in-neutrino-physics
  claim (PLAN §5).
- "The highest number of simultaneously unfolded observables in a neutrino cross-section analysis (five); earlier
  data measurements reach three." This must be stated with the correlated-observables caveat: q3, W and E_avail
  share q0.
- The calibrated joint test differs in kind from covariance χ² comparisons. Its calibration runs the full chain,
  with sequential Monte Carlo stopping and Holm control. A priority claim for it should be omitted. It is
  methodological and harder to bound by search, so describe it without "first".

**Not novel:**
- That several generators fail to describe MINERvA inclusive data. The 2D reference already reports it, including
  strong disfavour for every family our nulls belong to (Table I, §2).
- That MnvTune misdescribes ME low recoil. Ascencio's χ² values and our own 2D χ²/ndf = 33.0 already show it.

**Comparator for importance:** the collider precedents went to PRL (H1 2022, ATLAS 2024). Each delivered a
measurement with full uncertainties (and, for H1, a first physics observable). The present work has **no qualified
uncertainty on its 5D measurement**, because the measurement branch was not admitted. Its physics result is a
conditioned rejection of predictions that are already disfavoured in lower dimensions. That is the main reason the
packet recommends a specialist journal.

## 4. Detector response in MINERvA's published E_avail analyses (for packet §5.4); all verified in source text

- **2106.16210:** *"Uncertainty in the detector response to hadrons is evaluated using shifts determined by in
  situ measurements of a smaller version of the detector in a test beam [37]. Uncertainties in inelastic
  interaction cross sections for particles in the detector material are independently varied based on
  data-Monte Carlo differences between GEANT particle cross sections and world data on neutrons …, pions …, and
  protons …"*
- **2110.13372 (ME E_avail–q3, the closest analogue):** *"The uncertainty in the detector energy response is
  divided into two uncertainties, hadronic energy and muon reconstruction uncertainty … The hadronic energy
  uncertainty varies throughout the distribution and rises to 10% at high 0.9 < q3 < 1.2 GeV. The input
  uncertainty is determined from hadron calorimetry data taken with a test beam detector [18]."*
- **1511.05944:** *"Test beam constraints on calorimetry and Birks' suppression for MINERvA scintillator are used
  to tune the simulation and set the uncertainty on the single-particle response"*. It also says the flux
  uncertainty *"is the next largest, followed by hadronic and muon energy scales."*
- **Test beam:** Aliaga *et al.*, NIM A 789, 28 (2015), arXiv:1501.06431, already cited in
  `app_statmethods.tex`. Its abstract (**verified**, arXiv API): *"Overall the data are well described by a
  Geant4-based Monte Carlo simulation of the detector and particle interactions with agreements better than 4%,
  though some features of the data are not precisely modeled."* Ascencio *et al.* does not state its input value;
  it says only that the input *"is determined from hadron calorimetry data taken with a test beam detector"*.

**Reading:** MINERvA's published recoil analyses carry a **test-beam-derived hadronic (recoil) energy response
uncertainty**, separate from the GEANT inelastic cross-section reweights. Our declared nuisance model has the
reweights (and MinosEfficiency) but not the response band. Amendment 7 states this itself: *"no recoil-energy-scale
band"*. Under the PM-1 ruling this precedent is "supporting context, not proof of completeness". It is the concrete
omission, with an affected observable (E_avail, q3, W through q0), that the ruling requires to be brought back with
a proposed remedy (packet §6, W2).

**UNVERIFIED:** per-particle input values (proton, pion, neutron, EM) as applied in those analyses. W2's
authorization must take δ from a named source read at that time.

## 5. PRL requirements (APS author pages, fetched 2026-10-05; agent-reported, re-read before use)

- **Core length:** *"Letters (length limit: 3750 words)"*, about four journal pages between the abstract and the
  Acknowledgments.
- **End Matter:** *"up to two pages of appendices or other content—called End Matter … End Matter does not count
  against the core length limit."*
- **Justification:** *"a 100-word compelling justification for why their paper meets Physical Review Letters's
  criteria."*
- **Data availability:** *"All published articles must include a Data Availability Statement (DAS)."*
- **Word equivalents** (length guide):
  - single-column equations: 16 words per row;
  - single-column figures: (150 / aspect ratio) + 20;
  - double-column figures: 300 / (0.5 × aspect ratio) + 40;
  - single-column tables: 13 + 6.5 per line.
- **Not found:** the PRL abstract length limit.

## 6. Version notes for the manuscript

- MINERvA Tune v1 is GENIE **2.12.6**-based (2106.16210: *"version 2.12.6"*, agent-reported; the Letter agrees).
  The external GENIE nulls are GENIE **2.12.10** CV and MEC (`design.json` null names).
- The NuWro **21.09** version string is not in 2106.16210, which used two NuWro models of its own. Cite our sample's
  own configuration record, not the paper.
