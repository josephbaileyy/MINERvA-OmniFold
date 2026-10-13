# Reviewer brief: inelastic high-region validation proposal

**Date 2026-10-12. Branch `study/inelastic-high-region-20261011`. Prepared, not sent.** Choosing and contacting
reviewers is Joseph's decision. This brief authorizes no compute and adopts nothing.

## 1. What you are asked to assess

A concrete, unexecuted proposal ([`REPORT.md`](REPORT.md) §11, with §8 V2). It asks whether the high-E_avail /
high-W residual and the 1.4–1.8 GeV feature can be told apart from detector response and attributed to physics.

The study's verdict is **INCONCLUSIVE** under a frozen rule. That verdict, its numbers and its rule are not under
review.

**Please assess the proposal; do not restart the literature search.** Cite outside work only where it changes the
proposal.

Read:
- REPORT §1 (verdict);
- §5.3 (response and estimator limits);
- §6.2 (FSI channel signs);
- §11.1–11.5 (inventory, hypotheses, closure, outcomes, cost);
- §11.6 (GENIE v3 inventory).

Independence:
- Neither reviewer should be an author of this memo.
- The generator reviewer should be outside the GENIE tune authors.

## 2. Questions by role

### A. MINERvA hadronic-response expert

**A1. Species-branch semantics.**
- Do the MC branches `blob_recoil_E_{tracker,ecal,…}_{p,meson,em,other,lown,midn,highn,xtalk,mu}` hold truth-matched
  visible energy by species, in the calibration that `recoil_E` uses?
- Do they sum to the tracker/ECAL totals that the event loop reads?
- What does `_mu` hold, and does it double count with the muon-fuzz subtraction?
- Are the `part_response_recoil_allNonMuonClusters_*_err` shifts absolute or fractional?
- Is the A_r construction in §11.1 correct?

**A2. Calibration sizes and correlations.**
- Are MAT's defaults the right sizes at E_avail ≥ 0.8 GeV and above the 2 GeV/c test-beam reach?
  - π± 5%;
  - EM 3%;
  - proton 3.5%;
  - neutron 25 / 10 / 20%;
  - other 20%.
- What correlations should hold between species and across energy?
- Which in-situ constraints exist in the collaboration (Michel electrons, π⁰ mass, proton dE/dx)?
- Is the coherent ±4% scale that has been tested (W2B) a useful reference?

**A3. Neutron treatment.**
- Truth E_avail excludes neutrons, but reconstructed recoil contains neutron-induced energy.
- Are the low/mid/high split and its sizes adequate?
- Should GEANT_Neutron rate weights be varied jointly with them?
- Is excluding cross-talk, as MAT advises, right here?

**A4. Matched signal/background propagation.**
- Is it correct to shift background rows with the signal and to recompute the per-reco-cell purity?
- How does this interact with the s5c high-W purity bias?
- Can you confirm that no reco cut reads the recoil?
- Are the matched/mismatched closure design and the MC half-split in §11.3 sound?

**A5. Family scope and acceptance.**
- Which untested detector routes listed in §11.3 matter most?
- Which interactions should the linear-approximation checks cover?
- What recovery criterion counts as adequate resolution?

### B. Independent nuclear-theory / generator expert

**B1. Channel-dependent FSI signs.**
- Check the §6.2 table: the ΔA per channel for our A convention, the separation energies and the de-excitation
  bookkeeping.
- Can the net sign in region C be estimated from GENIE's per-hadron fates?
- Should that tabulation precede any detector work?

**B2. Realistic injected departures.**
- Are D₁–D₃ (§11.3) realistic in form and size?
  - D₁: a 02_11b-type re-partition;
  - D₂: `Fr*` absorption and charge exchange at ±1σ;
  - D₃: −15% at 1.4–1.8 GeV.
- Which are physically anchored, and which are stress tests only?
- Propose replacements where needed, for example formation zone, π⁰ fraction in hadronization, or the high-W DIS
  shape.

**B3. The most informative official GENIE comparison.** Section 3 sets out the options and the controls.
- Which configuration, or which pair, best tests the 1.4–1.8 GeV feature?
- Do G18_10a's 02_11b inelastic values equal G18_02a's? This was not checked.
- Are AR23_20i's inelastic values equal to G18_10a_02_11b's? This was agent-read only.

**B4. Scope of the inclusive-rate invariance (§5.1).** Is treating FSI as a normalized post-vertex kernel at fixed
primary dynamics adequate for region C?

## 3. What a GENIE v3 comparison can and cannot attribute

The configurations with ready splines are v3.04.00 G18_10a_02_11b and AR23_20i. Each differs from our GENIE 2.12.10
CV in several components at once:
- the nuclear model (LFG rather than RFG);
- the QE and MEC models;
- the resonance model (Berger–Sehgal rather than Rein–Sehgal);
- the FSI model (hN rather than hA);
- the inelastic tune.

AR23_20i differs again in its QE, MEC and nuclear choices (not re-checked here). A comparison against either
**tests a complete prediction**. It does not isolate the inelastic tune, and it does not test the G18_02a values
emulated in REPORT §6.1.

**Controls needed for attribution.** All are proposed; none is authorized.

| Control | Isolates | Status |
|---|---|---|
| C1. G18_02a_00_000 against G18_02a_02_11b, same version | the inelastic tune within one comprehensive model | 00_000 splines ready on CVMFS; 02_11b splines must be built (cost unmeasured). A G18_10a_00_000 pair would also serve, but its splines are not in the owner's listing |
| C2. G18_10a_02_11b against AR23_20i | the non-inelastic components, **if** their inelastic parameters are equal (B3) | both ready |
| C3. A truth decomposition of every prediction in M and C, by mode (QE / MEC / RES / SIS / DIS), W_gen and FSI fate | which component moves (model labels, not observed mechanisms) | from the gst; no extra generation |
| C4. A pipeline match to the GENIE 2.12 products: same flux to 100 GeV, CH mixture, signal definition (our E_avail; neutrons and kaons excluded), phase space and converter. Re-converting the existing GENIE 2.12.10 CV gst must reproduce the committed product | the converter, not physics | one conversion |
| C5. Both the absolute ratio and the normalization-removed ratio | whether a total-rate change appears as shape after normalization | reduction only |
| C6. Generator statistics set by the 10⁴-event pilot, so that the per-W statistical error in M stays below the feature | statistical artifacts | pilot |
| C7. A reweighting of the tune's parameters within one v3 configuration, if GENIE ReWeight knobs exist for them (B3) | the tune itself, at fixed everything else | to be confirmed by the reviewer |

## 4. What to return

- A short written answer to each numbered question.
- For each stage, one of **proceed**, **modify** (with the changed sizes, departures or controls) or **do not proceed**:
  - V1, the §11 screening study;
  - V2, the GENIE v3 comparison.
- Any error found in the cited sections.

Costs, for context (REPORT §11.5, all [A]; the units are not interchangeable):

| Item | Unit | Estimate |
|---|---|---|
| V1 sensitivity | billed CPU node-h | ≈ 6–9.5 |
| V1 closure | billed CPU node-h | ≈ 5–10 |
| V1 linear-approximation checks | billed CPU node-h | ≈ 8–23 |
| Calibrated validation | billed CPU node-h | order 10² |
| V2, per configuration | core-h | 1.5–15, after a pilot of ≤ 0.2 |

A favorable review launches nothing. Each stage needs Joseph's own authorization.
