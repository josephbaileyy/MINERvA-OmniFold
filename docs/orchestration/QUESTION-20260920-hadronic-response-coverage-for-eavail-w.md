# QUESTION 2026-09-20 — for a knowledgeable MINERvA collaborator: does the included detector-variation set cover hadronic response for this `(E_avail, W)` measurement?

**CITABLE FOR:** the text of the question, the band inventory it is asked against, and the fact that
it is **prepared and not yet sent**.
**NOT CITABLE FOR:** any answer, any claim that the treatment is complete or incomplete, or any
reopening of PM-1.

**STATUS: PREPARED, NOT SENT.** Sending it is outward-facing. Nothing below has been transmitted to
anyone outside this repository, and no answer exists.

Required by [`DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md`](DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md)
§5, which specifies the question's wording. Recorded here so it exists as an artifact rather than as
an intention.

---

## 1. The question, in Joseph's own words from the ruling

> Do the included GEANT reweights and other detector variations cover the hadronic-response
> uncertainties needed for this `E_avail` and `W` measurement, and which variations, if any, are
> missing?

## 2. The context a collaborator needs to answer it, and nothing more

**The measurement.** MINERvA ME-FHC inclusive charged-current muon-neutrino cross sections,
unfolded with unbinned OmniFold on five simultaneous observables
`(p_T, p_∥, E_avail, q₃, W)`, with results reported in the `(E_avail, W)` plane. `E_avail` and `W`
are both built from reconstructed hadronic energy: `q₀ = <tree>_recoil_E` and
`W = √(M² + 2·M·q₀ − Q²)` (`CVUniverse.h:227-235`).

**How the 45 covariance bands split.**

| set | n | how implemented | names |
|---|---|---|---|
| **A — lateral** | **5** | shifted reconstructed kinematics; rebuilt with **selection-complete active-universe event loops**, so events crossing into or out of the selection are counted | `BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS` |
| **V — vertical** | **13** | event weights, inflated through `D_Z` | `2p2h`, `CCQEPauliSupViaKF`, `FrAbs_pi`, `FrElas_N`, `HighQ2`, `LowQ2`, `MaCCQE`, `MaRES`, `MFP_N`, `MvRES`, `Rvn2pi`, `Rvp2pi`, `Flux` |
| **R — residual** | **27** | event weights | includes the four this question is about — **`GEANT_Neutron`, `GEANT_Pion`, `GEANT_Proton`, `MinosEfficiency`** — alongside `AGKYxF1pi`, `AhtBY`, `BhtBY`, `CV1uBY`, `CV2uBY`, `EtaNCEL`, `FrAbs_N`, `FrCEx_N`, `FrCEx_pi`, `FrElas_pi`, `FrInel_N`, `FrPiProd_N`, `FrPiProd_pi`, `MFP_pi`, `MaNCEL`, `NormDISCC`, `NormNCRES`, `RDecBR1gamma`, `Rvn1pi`, `Rvp1pi`, `Theta_Delta2Npi`, `VecFFCCQEshape`, `__Normalization_flat` |

**The four bands at issue are applied as reweights**, not as shifted kinematics: `w_reco_GEANT_*`,
and `MinosEfficiency` through `MINOSEfficiencyReweighter` (`runEventLoopOmniFold.cpp:70`,
instantiated into `MnvTunev1` at `:1749`). That is why they sit outside the kinematic replacement.

**Upstream documentation the analysis relies on**, per the ruling's *"support the treatment with the
applicable upstream documentation where available"*: the test-beam GEANT hadron-response measurement,
Aliaga *et al.*, NIM A **789** 28 (2015), `arXiv:1501.06431`, already cited in the note's
statistical-methods appendix.

## 3. What is asked, sharpened — three sub-questions a yes/no cannot answer

1. Do `GEANT_Neutron`, `GEANT_Pion` and `GEANT_Proton` span the hadron-interaction uncertainties
   relevant to **reconstructed recoil energy** in this detector configuration, or are they a subset
   of a larger recommended set?
2. Are there detector-response variations that affect `E_avail` or `W` and are **not** in the
   45-band inventory above — for example anything applied at the level of calorimetric response,
   clustering or particle-response tuning rather than as a named reweight?
3. For any variation named in answer to 1 or 2: does a standard ME-FHC implementation of it exist
   that an analysis can apply, or would it have to be constructed?

## 4. ⚠ WHAT MAY **NOT** BE DONE WITH THE ANSWER, per the ruling

- **Silence is not an answer and does not reopen anything.** *"Lack of a collaborator response does
  not reopen PM-1 or require a new methodology campaign."*
- **A general answer is not a result for this measurement.** *"Generic precedent is supporting
  context, not proof of completeness for this measurement."*
- **A concrete identified omission must come back with its affected observable and a proposed
  remedy** — that is the only route by which an answer changes the analysis.
- **No uncertainty may be invented from this.** The ruling *"does not authorize inventing a
  hadronic-energy shift or adding an arbitrary uncertainty."*
- **The treatment may not be described as negligible, conservative, complete or deficient** without
  evidence for that description, and **no limitation may be claimed to be largest at high
  `E_avail` or high `W`** merely because those observables involve hadronic energy. That inference
  was withdrawn by the ruling's §4 and is not revived by asking this question.

## 5. Why this is being asked at all, stated so it is not read as doubt about PM-1

PM-1 is **accepted by decision, with a historical-input provenance limitation**. The evidence
establishes **how** these four bands are implemented and therefore why they are outside the
five-band kinematic replacement. It does **not** establish that the set of hadronic-response
variations included is the complete set this measurement needs — and the ruling's §4 is explicit
that weight-only implementation **does not prove** that all relevant response variations are
represented. This question addresses that second thing, which no amount of re-reading the
implementation can settle.

**Co-Authored-By: Claude Opus 5 (1M context)**
