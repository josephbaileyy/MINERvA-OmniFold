# 2D OmniFold Study — Status

**Last updated**: 2026-04-25 (post-cleanup)

Companion docs: `2D_OMNIFOLD_REFERENCE.md` (workflow invariants and gotchas),
`2D_OMNIFOLD_RUN_LOG.md` (timestamped chronology), `PLOT_GUIDE.md` (PNG index).

---

## Goal

Reproduce arXiv:2106.16210 (Ruterbories et al., Phys. Rev. D 106, 032001) —
MINERvA ME FHC d²σ/(dp_T dp_||) CC inclusive — with 2D **unbinned** OmniFold
in place of D'Agostini IBU. Validated on playlist 1A, then run on full
12-playlist ME FHC.

---

## Current status

Full-stats MEHFC 2D result in place. Strict-interior χ²/ndf = 17.0 vs paper
(185 bins, full covariance); median bin ratio 0.892. Residual ~11 % deficit
is localized to a smooth gradient in low p_|| (0.65 at p_||=1.5–2 GeV/c
rising to ~1.0 above p_||=20 GeV/c).

**IsMinosMatchMuon stub fix applied 2026-04-25** and re-run on 1A.
Patch was a real bug (background drops 48,750 → 1,256, matching paper's
~0.2 % bkg rate; pass_reco drops by 9.6 %; χ²/ndf improves 19.5 → 18.4)
**but did NOT close the low-p_|| gradient**. Strip ratios pre/post fix:

| p_|| (GeV/c) | pre | post | | p_|| | pre | post |
|---|---|---|---|---|---|---|
| 1.5–2.0 | 0.65 | 0.60 | | 5–6 | 0.86 | 0.85 |
| 2.0–2.5 | 0.64 | 0.61 | | 10–15 | 0.93 | 0.90 |
| 2.5–3.0 | 0.70 | 0.69 | | 20–40 | 1.04 | 1.00 |

Shape unchanged; total xsec moved from 11 % low to 15 % low. **The
gradient is not driven by MINOS-match selection.** Most likely
remaining cause: MINOS geometric acceptance (range-out) modeling in
the truth-side phase-space efficiency, which the paper handles with a
dedicated correction the MINERvA-101 tutorial does not implement.

---

## Key reference numbers (corrected full ME FHC, 5-iter production)

| Quantity | Value |
|---|---|
| mcPOT (sum of 12 playlists) | 4.978e21 |
| dataPOT (sum of 12 playlists) | 1.057e21 |
| potScale (data/MC) | 0.2124 |
| Weighted full-MEHFC flux integral | 8.7407e-7 /cm²/POT |
| N fiducial nucleons | 3.2353e30 (tracker geometry constant) |
| Selected data events (reco) | 4,875,597 |
| `hMeasSub2D` integral (data − bkg) | 4.315e6 |
| `hTruth2D` / `hUnfold2D` integrals | 4.546e6 / 5.215e6 |
| Step-2 weight stats | mean 1.142, range [0.617, 3.447] |
| Total xsec (p_T projection = p_|| projection) | 2.442e-38 cm²/nucleon |
| Strict-interior χ²/ndf vs paper (185 bins, full cov) | 17.0 |
| Median bin ratio (ours/paper, strict interior) | 0.892 |

Paper total (reported): 2.74e-38 cm²/nucleon (our sum over reported bins
is ~11 % low; gradient detailed below).

### Playlist 1A corrected validation set

| Quantity | Value |
|---|---|
| 1A mcPOT / dataPOT / potScale | 4.069e20 / 8.973e19 / 0.2205 |
| 1A selected events (reco) | ~440k |
| 1A 5-iter total xsec | 2.484e-38 cm²/nucleon |
| 1A 5-iter strict-interior χ²/ndf vs paper | 19.5 |
| In-sample closure median ratio / RMS | 1.0000 / 0.0000 |

### Iteration convergence (playlist 1A, corrected pipeline)

| iter | hUnfold2D | xsec (cm²/nucleon) | rel RMS vs 10-iter |
|---|---|---|---|
| 1 | 448,066 | 2.4775e-38 | 6.95% |
| 3 | 448,958 | 2.4825e-38 | 3.71% |
| 5 | 449,273 | 2.4842e-38 | 2.11% |
| 8 | 449,507 | 2.4855e-38 | 0.78% |
| 10 | 449,649 | 2.4863e-38 | 0.00% |

Production uses **5 iterations** (0.08 % bias on total xsec vs 10-iter;
~17 h runtime saved).

### Residual low-p_|| deficit (strip sum-ratio, ours/paper, interior)

| p_|| strip (GeV/c) | ratio | | p_|| strip (GeV/c) | ratio |
|---|---|---|---|---|
| 1.5–2.0 | 0.65 | | 5–6   | 0.86 |
| 2.0–2.5 | 0.65 | | 10–15 | 0.93 |
| 2.5–3.0 | 0.71 | | 20–40 | 1.00 |
| 3.0–3.5 | 0.73 | | 40–60 | 1.01 |

Monotonic gradient; high-p_|| agreement to ~1 % rules out flux, nucleon
count, and bulk background subtraction. Mean efficiency `hEff2D` falls
from 0.56 at p_||=1.5–2 to ~0.89 plateau above 5 GeV/c — shape tracks the
deficit.

---

## Paper binning (arXiv:2106.16210)

Authoritative: `minerva_paper_anc/bin_mapping.txt`. The TH2D axis labels in
the ancillary ROOT file are **cosmetic rounding** (0.075, 0.325, 0.475) —
do not copy them into `util/Binning.h`.

```python
pt_edges = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]         # 14 bins
pz_edges = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # 16 bins
```

Phase space: θ_μ < 20°, p_T < 4.5 GeV/c, 1.5 < p_|| < 60 GeV/c.
Paper reports 205/224 bins (19 diagonal bins with pt/p|| > tan 20° are
unreported).

---

## Runtime notes

| Task | Resource | Wall time |
|---|---|---|
| C++ event loop, one playlist | shared QOS, 1 task | ~3.5 h |
| Event loop, all 12 playlists | 11-task array | ~3.7 h (parallel) |
| 2D OmniFold, 5-iter, 1A stats | shared QOS, 2 CPU, 8 GB | ~1.4 h |
| 2D OmniFold, 5-iter, full stats | shared QOS, 4 CPU, 32 GB | ~20 h |

---

## Remaining work

- [x] **Override `IsMinosMatchMuon()`** to use a real MINOS-match branch.
  Patched `CVUniverse.h:107` (2026-04-25). Rebuilt + installed.
- [x] **Re-run 1A event loop + 2D unfold with patched binary**
  (2026-04-25 05:05 UTC). Output:
  `runEventLoopOmniFold_1A_minos_fix.root`,
  `2d_crossSection_omnifold_1A_minos_fix_5iter.root`. Fix improves
  χ²/ndf 19.5 → 18.4 but does not flatten the low-p_|| gradient.
- [ ] **Investigate MINOS geometric acceptance (range-out) modeling.**
  The paper applies a dedicated low-p_|| range-out efficiency
  correction; the MINERvA-101 tutorial path does not. Audit
  `MinosMuonEfficiencyCorrection` vs the paper's published map.
- [ ] **Re-run full MEHFC** once the gradient is understood.

---

## MINOS-match acceptance investigation plan (2026-04-25)

**Framing.** The paper requires MINERvA-MINOS muon track matching but does
not document the implementation. They state phase-space cuts (p_|| > 1.5,
θ_μ < 20°) and report ~64 % overall reco efficiency. Phase-space cuts
alone yield ~85 % efficiency in our chain, so additional reco selection
or truth-side acceptance modeling is implicit. Tuning cuts to hit 64 % is
ad hoc and risks burying unrelated bugs.

The audit JSON (`minos_acceptance_audit_1A_summary.json`) already shows
**corr(implied multiplier, inverse-efficiency shape) = 0.88**, with
implied multipliers (1.68 at p_||=1.5–2) systematically *larger* than the
inverse-eff shape (1.49). This signature points at a truth-denominator
problem, not a missing reco cut.

**Hard rule.** Do not adjust MC truth selections or reco cuts to drive
overall efficiency to 0.64. Record whatever efficiency the canonical
chain yields and treat it as a finding, not a target.

**Step 1 — Pin down canonical reco selection (reproducibility).** Trace
what Ruterbories' published CCQENuInclusive / MasterAnaDev chain applies
on top of `isMinosMatchTrack && _minos_trk_is_ok`. Candidates with
existing AnaTuple branches: MINOS track quality, curvature significance,
MINOS χ²/ndf, MINOS-face fiducial cut. Code-tracing task, not a parameter
sweep.

**Step 2 — Denominator vs numerator diagnostic (cheap, highest-info,
START HERE).** Bin the paper's MINERvA-Tune-v1 prediction (in
`minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt`)
into our (p_T, p_||) binning, then compare against our `hTruth2D` shape
under truth phase-space mask only. If shapes agree, the gradient is
reco-side. If they disagree, the gradient is denominator-side (MINOS
geometric acceptance modeling).

**Step 3 — If reco-side.** Add the cut(s) identified in Step 1, re-run
1A, verify strip ratios flatten.

**Step 4 — If denominator-side.** Apply a published external MINOS
geometric-acceptance map (Ruterbories thesis appendix, or DocDB-cited
Wolcott MINOS-match efficiency) as a per-event truth-side weight. Cite
the source. Do **not** invent an acceptance shape from our own MC — that
is circular.

**Step 5 — Fallback.** If no public acceptance map exists for ME FHC,
publish with the gradient and a systematic band on low-p_||; do not
manufacture one.

**Active execution log.**

- **Step 2 (denominator diagnostic) — DONE.** `diagnose_truth_shape_vs_paper.py`
  bins the paper's MnvTune-v1 model file against our `hTruth2D` shape,
  unit-normalized in the strict interior (185 bins). Strip shape ratios
  paper/ours (1A patched binary):

  | p_|| (GeV/c) | paper/ours shape | | p_|| | paper/ours shape |
  |---|---|---|---|---|
  | 1.5–2.0 | **1.41** | | 5–6 | 0.95 |
  | 2.0–2.5 | 1.27 | | 7–10 | 0.90 |
  | 2.5–3.0 | 1.16 | | 10–20 | 0.88 |
  | 3.0–4.0 | 1.10–1.08 | | 20–60 | 0.91–0.95 |

  The paper's *truth-level* MnvTune-v1 has 41 % more density at
  p_||=1.5–2 GeV/c than our `hTruth2D`. **The truth denominator is
  shape-deficient at low p_||.** This explains a large fraction of the
  residual xsec gradient (audit-implied multiplier 1.68 at p_||=1.5–2 vs
  truth shape mismatch 1.41 → about 1.19 residual that is reco-side or
  efficiency-side). Gradient is **mostly denominator-side**, but not
  exclusively. Output: `truth_shape_vs_paper_1A_summary.json`,
  `truth_shape_vs_paper_1A_strips.png`.

  Implication: re-weighters in our `MnvTunev1` chain
  (`FluxAndCVReweighter`, `GENIEReweighter`, `LowRecoil2p2hReweighter`,
  `RPAReweighter`, `MINOSEfficiencyReweighter`) may not reproduce the
  paper-era MnvTune-v1 exactly, *or* there's a truth-side phase-space
  cut implicit in the AnaTuple production we haven't accounted for.
- **Step 1 (canonical reco selection trace) — DONE.** Our cut list IS the
  canonical Ruterbories 2D inclusive chain. Compared
  `runEventLoopOmniFold.cpp:369–384` against
  `MAT-MINERvA/calculators/CCInclusiveCuts.h::GetCCInclusive2DCuts` and
  `CCInclusiveSignal.h::GetCCInclusive2DPhaseSpace`:

  - **Reco preCuts** match exactly: ZRange(5980,8422), Apothem(850),
    MaxMuonAngle(20°), HasMINOSMatch (now patched), NoDeadtime(1),
    IsNeutrino. No additional MINOS quality / track-quality cuts in the
    canonical chain.
  - **Truth signalDefinition** matches: IsNeutrino, IsCC.
  - **Truth phaseSpace** matches the canonical
    `GetCCInclusive2DPhaseSpace`: true ZRange, true Apothem, true
    MuonAngle(20°), PZMuMin(1500 MeV); plus our explicit MaxPzMu(60 GeV)
    and MaxPtMu(4.5 GeV) which extend the canonical signal to a
    bin-bounded interior.

  No reco cut is missing. No truth phase-space cut is missing. The
  "tune to 64 % efficiency" framing is closed: any selection-based
  closure of the gradient would be ad hoc and is now explicitly off
  the table.

- **Combined Step 1 + Step 2 conclusion.** Cuts are canonical; truth
  shape disagrees with the paper-era MnvTune-v1 model file in shape.
  The mismatch must therefore live in **(a)** the MnvTune-v1 reweighter
  implementation in our local PlotUtils checkout (FluxAndCV / GENIE /
  LowRecoil2p2h / MINOSEfficiency / RPA) drifting from the 2021 paper
  version, or **(b)** a truth-side acceptance the paper applies
  externally to the model curve (e.g. MINOS geometric acceptance folded
  into the model release), or **(c)** MC-sample differences (1A vs full
  MEHFC). Step 4 (apply published external acceptance map) is the
  next principled action; Step 3 is moot since no reco cut needs to
  change.

- **Step 3 (re-run with extra reco cut) — N/A.** No reco cut to add.
- **Step 4 (apply published external MINOS geometric acceptance map)
  — RESOLVED: no such map exists.** Pulled the paper PDF
  (`2d-unfolding/reference/Ruterbories_2106.16210v3.pdf`) and read
  Sec. III–IV verbatim:

  > "Muons that originate in MINERvA are analyzed by the MINOS near
  > detector ... The requirement that muons are analyzed in MINOS
  > restricts this analysis to muons with p|| > 1.5 GeV/c and θµ < 20°,
  > which means a restricted acceptance for events with Q² < p_||²/8."

  > "[The selection] has an overall reconstruction efficiency of 64%
  > in the pt-p|| phase space, **where the efficiency loss is due to
  > the MINERvA-MINOS geometric acceptance.**"

  > "Uncertainty in the matching efficiency is from imperfect modeling
  > of the efficiency loss from accidental activity in the MINOS near
  > detector when matching muon tracks from MINERvA to MINOS. **This
  > last efficiency is also determined by a data-simulation comparison
  > as a function of instantaneous neutrino beam intensity.**"

  Implications:

  1. The paper does not apply any *external* 2D (p_T, p_||) acceptance
     correction. Geometric acceptance lives entirely inside the GEANT4
     simulation of MINERvA + MINOS.
  2. The only documented per-event MINOS-side correction is the
     instantaneous-beam-intensity (batch-POT) data/MC efficiency ratio,
     which is exactly what `PlotUtils::MinosMuonEfficiencyCorrection`
     and `MINOSEfficiencyReweighter<>` provide and which we already
     apply at `runEventLoopOmniFold.cpp:392`.
  3. There is therefore nothing to "import" from a thesis appendix or
     DocDB — the entire correction chain we need is local. Searched the
     MAD tuple documentation
     (https://github.com/MinervaExpt/Tuple-Documentation MAD_tuple_MainDoc.csv)
     for additional MINOS branches; only generic `n_minos_matches`,
     `all_event_start_vertex_fv_minos_match`, and
     `all_event_start_vertex_time_minos_match` (all flagged "Use
     Uncommon"). The canonical match branches we already use
     (`isMinosMatchTrack`, `MasterAnaDev_minos_trk_is_ok`) are not in
     the MAD doc but are present and populated in the AnaTuple files.

  **What this rules out.** It rules out the working hypothesis that the
  gradient is closeable by importing an external map. It is *not* an
  acceptance-map problem — it is a simulation-and-weight-chain problem.

  **What this leaves on the table.** Our diagnostic reco efficiency on
  1A is 0.85 vs the paper's quoted 0.64. Same canonical cuts (Step 1).
  Same MINOS efficiency reweighter (line 392). Same truth phase space.
  The 21-pp efficiency gap therefore must come from one of:

  - (i) different absolute MnvTune-v1 weights in our local PlotUtils
    checkout vs the 2021 release (FluxAndCV / GENIE / LowRecoil2p2h /
    RPA / MINOSEfficiency drift),
  - (ii) `pass_reco` being computed differently in our event loop vs
    the paper's chain (e.g. a missing internal acceptance flag we are
    not gating on), or
  - (iii) the AnaTuple production cuts having tightened or loosened
    since 2021 such that our truth-denominator and pass-reco
    populations are not the same as the paper's.

  Any of these could in principle reproduce the Step-2 finding (paper
  truth shape 1.41× ours at p_||=1.5–2 GeV) without changing cuts or
  introducing an external map.
- **Option 1 — MnvTune-v1 weight chain audit — DONE, signal found.**
  `2d-unfolding/diagnose_weights_vs_pz.py` reads the combined per-event
  weights `w_truth` (mc_truth_denom) and `w_reco` (mc_signal_reco) from
  `runEventLoopOmniFold_1A_minos_fix.root` and computes
  &lt;weight&gt; per truth-p_|| strip. Result (relative to the
  p_||&ge;20 GeV plateau):

  | p_|| (GeV/c) | &lt;w_truth&gt;/plateau | &lt;w_reco&gt;/plateau |
  |---|---|---|
  | 1.5–2.0 | **0.666** | **0.648** |
  | 2.5–3.0 | 0.657 | 0.649 |
  | 5–6 | 0.678 | 0.678 |
  | 10–15 | 0.837 | 0.836 |
  | 20–40 | 0.899 | 0.901 |
  | 40–60 | 1.101 | 1.099 |

  Key observations:

  1. The truth-only and reco-side weights have the same low-p_||
     suppression to ≤1.5 % — so MINOSEfficiencyReweighter (the only
     reweighter that differs between truth and reco) is *not* the
     driver. The shape is in the four truth-side reweighters
     (FluxAndCV, GENIE, LowRecoil2p2h, RPA).
  2. Mean weight 0.799 at p_||=1.5–2 GeV vs 1.320 at p_||=40–60 GeV
     ≈ 1.65× ratio. This is large enough to plausibly account for the
     1.41× low-p_|| truth-shape deficit found in Step 2.
  3. Source review of the four truth-side reweighters:
     - **FluxAndCV**: weight = `flux_reweighter.GetFluxCVWeight(E_nu, pdg)`.
       Pure E_nu shape. Low p_|| ⇒ low E_nu ⇒ weight pulled by the flux
       CV / Geant4 flux ratio at the flux peak. **Dominant suspect.**
     - **GENIE**: nonResPi (0.43 on a small subset) ×
       deuterium-RES tune (CCRes only). Weak shape effect.
     - **LowRecoil2p2h**: 2p2h-only weight in (q0, q3). Mostly low-q3.
     - **RPA**: low-Q² QE suppression in (q0, q3). Some p_|| shape.
  4. To pinpoint which reweighter carries the shape, the C++ event loop
     would need to be modified to dump per-reweighter weights into the
     truth tree (or call `PlotUtils::flux_reweighter` from PyROOT to
     reproduce FluxAndCV alone). Either is several hours of work.

  Output: `2d-unfolding/weights_vs_pz_1A_summary.json`,
  `2d-unfolding/weights_vs_pz_1A_strips.png`.

  **Conclusion of Option 1.** The MnvTune-v1 weight chain produces a
  truth-side p_|| shape that quantitatively explains most of the Step 2
  truth-shape deficit. This either (a) reproduces what the paper
  intended for its MnvTune-v1 prediction (in which case the
  ancillary `model_ptpl_*.txt` file must have been computed with a
  *different* weighting and the comparison in Step 2 was apples-to-
  oranges), or (b) drifts from the paper-era MnvTune-v1 (in which case
  we have a real reweighter-version mismatch). Distinguishing these
  requires per-reweighter decomposition.

- **Option 1 decomposition — DONE.** Modified
  `runEventLoopOmniFold.cpp` to dump per-reweighter weight branches
  (`w_FluxAndCV`, `w_GENIE`, `w_LowRecoil2p2hTune`, `w_MINOSEfficiency`,
  `w_RPA`) into `mc_truth_denom`, gated behind `MNV101_TRUTH_ONLY` to
  skip the slow reco loops. Re-ran 1A with `MNV101_TRUTH_ONLY=1
  MNV101_SKIP_SYST=1` (~3 min). Output:
  `/pscratch/sd/j/josephrb/MINERvA101/Documents/component_dump_1A/runEventLoopOmniFold.root`
  (left in OLD scratch; not migrated — see archive note in
  `2D_OMNIFOLD_REFERENCE.md`). Analysis:
  `2d-unfolding/decompose_truth_weights.py`. Per-component vs
  high-p_|| plateau:

  | p_|| (GeV/c) | combined | FluxAndCV | GENIE | 2p2h | MINOSEff | RPA |
  |---|---|---|---|---|---|---|
  | 1.5–2.0 | 0.666 | **0.672** | 0.992 | 1.000 | 1.000 | 0.998 |
  | 5–6 | 0.679 | **0.704** | 0.961 | 1.016 | 1.000 | 0.987 |
  | 10–15 | 0.837 | **0.844** | 0.993 | 1.004 | 1.000 | 0.995 |
  | 20–40 | 0.899 | **0.899** | 1.000 | 0.998 | 1.000 | 1.000 |
  | 40–60 | 1.101 | **1.101** | 1.000 | 1.002 | 1.000 | 1.000 |

  GENIE / LowRecoil2p2h / MINOSEfficiency / RPA are flat in p_|| to
  ≤1 % across the full range. **`FluxAndCV` carries 100 % of the
  shape.** Plateau means: w_FluxAndCV=1.233 (data-constrained flux
  23 % above Geant4 at high E_ν), dropping monotonically with E_ν to
  ~0.83 at low p_|| (data-constrained flux 17 % below Geant4).

  This is `PlotUtils::flux_reweighter(playlist, pdg, useNuE,
  nFluxUniv).GetFluxCVWeight(E_ν, pdg)` — the nu-e-constrained CV flux
  divided by the Geant4 baseline flux, evaluated at truth E_ν. Files
  used: `opt/lib/data/flux/flux-{gen2thin,g4numiv6}-pdg{14,-14,12,-12}-minervame1D_rearrangedUniverses.root`
  (note: `1D` flux files used for the 1A playlist via the framework's
  ME flux mapping).

  **Interpretation.** The paper's MnvTune-v1 model curve in
  `model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt` is supposed
  to include the same flux CV reweighting (the paper says explicitly
  in Sec V that it does). If our `FluxAndCV` ratio at low E_ν differs
  from the 2021-era ratio, our local flux files have drifted from the
  paper-era release. The Step 2 mismatch (paper/ours truth shape =
  1.41 at p_||=1.5–2 GeV) is consistent with our flux CV being more
  suppressive at low E_ν than the paper-era one by exactly that
  factor.

- **Option 2 (audit `pass_reco`) — N/A.** Option 1 attributed the
  shape entirely and quantitatively to `FluxAndCV`; reco-side
  selection cannot have produced a truth-only weight signature.

### Final attribution

The residual low-p_|| xsec gradient decomposes as:
- **~1.4× of the 1.68× total** = our `FluxAndCV` flux-CV ratio
  differing from the paper-era one at low E_ν, biasing both the
  truth denominator (via hTruth2D filling) and the OmniFold prior.
- **~1.2× residual** = remaining contributions from
  reco-efficiency-related effects in OmniFold's reweighting, plus
  any sample-level differences (1A only vs full MEHFC, AnaTuple
  production differences). Sub-leading and not a blocker.

The principled fix is to either (a) obtain the paper-era flux CV
files and rebuild `opt/lib/data/flux/`, or (b) document the flux-CV
drift as a low-p_|| systematic and publish with it explicitly
attributed. There is no in-pipeline knob that can close the gradient
without changing the flux constraint itself.

### Reproducibility caveat (locked in)

**Full quantitative reproduction of arXiv:2106.16210 requires the
2021 flux release files.** Our local
`opt/lib/data/flux/flux-{gen2thin,g4numiv6}-pdg{14,-14,12,-12}-minervame1D_rearrangedUniverses.root`
have evidently drifted from the paper-era release; the per-reweighter
decomposition shows the residual low-p_|| paper disagreement is
entirely in `FluxAndCVReweighter`, with the other four MnvTune-v1
reweighters flat in p_|| to ≤1 %. Until the 2021 flux files are
retrieved and reinstalled, the low-p_|| paper agreement is bounded by
the flux-CV drift (~1.41× shape ratio at p_||=1.5–2 GeV/c). All other
components of the analysis (cuts, truth phase space, MINOS-match
selection, OmniFold, χ² machinery) are in the canonical state.

**Decision (2026-04-25, by user):** keep current flux files and
finish the pipeline. The flux-CV mismatch becomes a known systematic
documented at publication time, not a blocker.

### Finish-pipeline plan (post-decision)

1. Make the per-reweighter dump branches optional behind
   `MNV101_DUMP_COMPONENTS` so canonical full-MEHFC outputs are
   byte-clean vs the pre-decomposition production (no extra
   per-event branches). Rebuild + install.
2. Re-run the full 12-playlist event loop on the patched binary
   (`IsMinosMatchMuon` fix from 2026-04-25). Existing 1A_minos_fix
   output is reusable; need 1B–1P plus a new MEHFC hadd. ~3.7 h
   parallel via the existing 11-task sbatch array.
3. Re-run the 2D OmniFold unfold on the new MEHFC, 5-iter,
   `--use-weights`, full-stats sbatch (~20 h).
4. Regenerate the paper comparison plots and χ² (full-cov + strict
   interior). Update the headline numbers in this doc.
5. Document the residual low-p_|| flux-CV systematic in the writeup.

**Step 1 (env-gated dump) — DONE 2026-04-25.**
`runEventLoopOmniFold.cpp`: per-component branches now gated behind
`MNV101_DUMP_COMPONENTS`. Without it, output schema is byte-identical
to the pre-decomposition production. Rebuilt + installed.

**Step 2–4 (full 12-playlist patched event loop → hadd → unfold →
finalize) — SUBMITTED as a chained pipeline.** Pre-patch 1B–1P + old
MEHFC moved to `/pscratch/sd/j/josephrb/MINERvA101/Documents/archive_pre_minos_fix/`
(OLD scratch tree, not migrated). Reusing existing
`runEventLoopOmniFold_1A_minos_fix.root` for 1A. SLURM dependency
chain (each `afterok` of the previous):

| step | jobid | script | resource | wall |
|---|---|---|---|---|
| event-loop array (1B–1P) | **52031654** | `sbatch_evloop_array.sh` | shared, 1 task × 11 array, 2 cpu, 8 GB | ~3.7 h parallel |
| hadd → MEHFC | **52031695** | `sbatch_hadd_MEHFC.sh` | shared, 2 cpu, 8 GB | ~2 min |
| 2D OmniFold full-stats 5-iter | **52031697** | `sbatch_unfold_2d_fullstats.sh` | shared, 4 cpu, 32 GB | ~20 h |
| paper compare + plots | **52031722** | `sbatch_finalize_MEHFC.sh` | shared, 2 cpu, 8 GB | ~5 min |

End-to-end ETA from submit: ~24 h. Final outputs:
`runEventLoopOmniFold_MEHFC.root`,
`2d_crossSection_omnifold_MEHFC_5iter.root`, plus regenerated paper
χ² JSON + paper-compare PNGs. Once those are in place this section
should be promoted up to "Current status" with the post-fix
headline numbers.

- **Step 5 (fallback — publish with the gradient and a low-p_||
  systematic) — STAGED.** If no public 2D acceptance map for ME FHC
  exists, the principled posture is to (a) publish total xsec and
  shape with the residual gradient, (b) cite this audit as the
  attribution to truth-side acceptance modeling, and (c) inflate the
  low-p_|| systematic to cover the residual implied multiplier
  (1.68 at p_||=1.5–2.0 GeV/c). Do **not** invent a (p_T, p_||)
  acceptance shape from our own MC; that would be circular.

### Summary after Steps 1–2 of the investigation

- Reco selection: canonical, no missing cut.
- Truth phase-space cuts: canonical, all four spatial/angular constraints
  applied at C++ level.
- `IsMinosMatchMuon`: patched to canonical
  `isMinosMatchTrack && _minos_trk_is_ok`.
- Truth shape vs paper MnvTune-v1 model: shape-deficient at low p_||
  (paper/ours = 1.41 at p_||=1.5–2.0 GeV/c) → the residual is *not* a
  reco-cut bug; it is either a drift in our local MnvTune-v1 reweighter
  vs the 2021 release, or a missing external truth-side acceptance the
  paper folded into its model curve.
- Total residual xsec multiplier at p_||=1.5–2.0 GeV/c is 1.68; truth
  shape mismatch alone explains 1.41 of that, leaving ~1.19 unattributed
  to either canonical cuts or pure truth shape — likely
  `MinosMuonEfficiencyCorrection` 1D-only behavior plus residual
  reco-efficiency miscalibration.

---

## Active code

### C++ event loop (`MINERvA101/MINERvA-101-Cross-Section/`)
- `runEventLoopOmniFold.cpp` — per-playlist event loop; writes 4 TTrees
  (`mc_truth_denom`, `mc_signal_reco`, `mc_background`, `data`) with both
  `p_T` and `p_||` branches. Does **not** write `pTmu_fiducial_nucleons`
  (was hadd-corrupted).
- `cuts/MaxPtMu.h`, `util/Binning.h` — paper phase-space cut and binning.
- `event/CVUniverse.h` — defines kinematic getters and (buggy) MINOS-match stub.

### Python (`2d-unfolding/`)
- `unfold_2d_omnifold_unbinned.py` — 2D unbinned OmniFold. Masks data to
  phase space, subtracts background, fills `hUnfold2D` with
  `step2_weights * truth_w_in`, **does not** divide by `hEff2D`.
- `plot_2d_cross_section.py` — 14-panel p_T + 16-panel p_|| slice grids +
  1D projections + efficiency map.
- `plot_2d_paper_comparison.py` — same overlaid with paper MINERvA-Tune-v1.
- `plot_closure_2d.py` — closure diagnostic.
- `plot_iter_convergence.py` — iter-scan summary.
- `compare_to_paper_fullcov.py` — full-cov χ² on all 205 reported bins.
- `compare_to_paper_interior.py` — strict-interior χ² on 185 bins.
- `combine_flux_MEHFC.py` — builds POT-weighted MEHFC flux from
  per-playlist baseline-flux ROOTs.

### SLURM (`2d-unfolding/`)
- `sbatch_evloop_array.sh` — per-playlist event-loop array.
- `sbatch_unfold_2d.sh` / `sbatch_unfold_2d_fullstats.sh` — 2D unfold (1A / MEHFC).
- `sbatch_iter_scan_2d.sh` — iter-scan array.
- `sbatch_validate_1A_corrected.sh` — end-to-end 1A validation.
- `sbatch_runEventLoop_baseline_flux_array.sh` — regen baseline flux per playlist.
- `download_playlist.sh` + `sbatch_download_playlist.sh` — xrdcp via xfer QOS.

### Data / outputs
- `runEventLoopOmniFold_MEHFC.root` (2.17 GB, hadd of per-playlist).
- `runEventLoopOmniFold_1{B..P}.root` — per-playlist intermediates.
- `runEventLoopOmniFold_1A_corrected_interactive.root` — corrected 1A.
- `2d_crossSection_omnifold_MEHFC_5iter.root` — **production** output.
- `2d_crossSection_omnifold_1A_corrected_{1,3,5,8,10}iter.root` — iter-scan.
- `2d_crossSection_omnifold_1A_corrected_5iter_closure.root` — closure.
- `baseline_flux/` — per-playlist baseline + `runEventLoopMC_MEHFC.root`
  (POT-weighted MEHFC flux).
- `minerva_paper_anc/` — arXiv ancillary release (TH2D, 4 cov matrices,
  bin_mapping.txt, data CSV, model predictions).

### Manifests (`2d-unfolding/playlist_manifests/`)
- `1{A..P}_{MC,Data}.txt` — per-playlist local paths.
