# 2D OmniFold run log — Phases 1–18.1 archive

Frozen 2026-05-21. This is the pre-2026-05-18 chronology of how the
Phase-18.2 production pipeline was reached: 18 numbered phases covering
the C++ event-loop extension, four rounds of bug attribution, the
Phase-15/16 truth-shape attribution chain that closed the σ/paper=0.752
puzzle, the Phase-17/18 native-miss + truth-authoritative-gate
re-architecture, and the two dedupe passes that made c=1 exact at MEHFC.

For everything from Phase-18.2 production unfold (2026-05-18) onward,
see `2D_OMNIFOLD_RUN_LOG.md`. For headline numbers and current state
see `2D_OMNIFOLD_STUDY_STATUS.md`.

---


## Phase 1 — C++ event-loop extension (2026-04-17)

Plan approved (`~/.claude/plans/purrfect-whistling-pelican.md`). Changes
to the existing 1D unbinned OmniFold pipeline to emit 2D:

- `runEventLoopOmniFold.cpp` — added p_|| branches to all 4 TTrees.
- `cuts/MaxPtMu.h` — truth-level p_T upper cut (MeV units, MINERvA
  convention).
- `util/Binning.h` — paper `ptmu_bins` and `pzmu_bins`.
- `phaseSpace` — `PZMuMin(1500)`, `MaxPzMu(60000)`, `MaxPtMu(4500)`.

First 1A event loop: mcPOT 4.07e20, dataPOT 8.97e19, pot_scale 0.2205.
TTree entries: truth_denom 2.65M, signal_reco 2.37M, background 260k,
data 498k.

## Phase 2–3 — First 2D OmniFold pass was 6× too large (2026-04-17 to 20)

Symptoms: `hUnfold2D = 2.82M`, total xsec 9.3e-32 cm²/nucleon (~6× paper).

Root causes found (all fixed):

1. **`hUnfold2D` filled with raw OmniFold ratios** instead of
   `step2_weights * truth_w_in`. The `step2_weights` output from
   OmniFold is a per-event *density ratio*, not a yield. Multiplying by
   the incoming truth weight recovers an event-count spectrum.
2. **Missing truth-weighted fill loop** — first version iterated over
   all MC truth events rather than only those passing truth selection,
   inflating the denominator.

After fix: 1A total xsec settled near 2.5e-38 cm²/nucleon (expected).

## Phase 4 — Production run + closure test (2026-04-21 area)

Closure (MC-as-data on 1A) ran to completion. Paper-comparison first
showed χ²/ndf ~7000; **decomposition proved the binning in `Binning.h`
was NOT buggy** despite the cosmetic axis-label rounding in the paper's
ancillary TH2D (`0.075`, `0.325`, `0.475`). Authoritative bin definition
is `minerva_paper_anc/bin_mapping.txt`.

A pull-decomposition showed the large χ² was dominated by ~15 bins on
the diagonal where `pt_hi / pz_lo > tan 20°` — these are the paper's
*unreported* bins. Masking to the 185 strict-interior bins brought
χ²/ndf down to order 100 and exposed a separate ~3 % normalization bias
and a low-p_|| strip pathology.

## Phase 5 — Flux audits and per-playlist event loops (2026-04-21 to 22)

- Paper scalar `6.32e-8 /cm²/POT` is **not** the flux term used by this
  path; substituting it blows up total xsec ~13.8×.
- `runEventLoopOmniFold` does not emit `pTmu_reweightedflux_integrated`;
  use `runEventLoop` (baseline) via `sbatch_runEventLoop_baseline_flux_array.sh`
  per playlist, then `combine_flux_MEHFC.py` to build the POT-weighted
  full-MEHFC flux (`baseline_flux/runEventLoopMC_MEHFC.root`).
- **Playlist-dependent flux variation audited at ~0.2 %** — not a
  dominant systematic.
- 2D OmniFold outputs now embed `hFlux_pt` + `fluxSource` so later
  auditing is self-contained.
- Efficiency heatmap axes flipped to (p_|| on x, p_T on y) to match
  paper Fig. 5.
- **Per-playlist event-loop array job** submitted and completed for
  1B..1P (1A already in place). Outputs `hadd`-merged into
  `runEventLoopOmniFold_MEHFC.root` (2.17 GB).

## Phase 6 — Post-production review: four P1 pipeline bugs (2026-04-22)

Review of the production code path uncovered four correctness bugs that
collectively invalidated the pre-fix MEHFC result:

1. **Double efficiency divide.** `hXSec2D = hUnfold2D / hEff2D / ...`
   even though OmniFold returns an efficiency-corrected truth spectrum
   on the truth-selected sample. Fix: drop the `/ hEff2D` step; keep
   `hEff2D` as a diagnostic only.
2. **Raw selected data (not data − bkg) fed into step-1.** The OmniFold
   measured-side training target must be background-subtracted. Fix:
   build non-negative reco-space target from `data − bkg` and pass
   `measured_weights` into `ohf.omnifold(...)`.
3. **No phase-space mask on measured data** before step-1 training.
   Fix: mask to `0 ≤ p_T ≤ 4.5` and `1.5 ≤ p_|| ≤ 60` before training.
4. **`hadd` summed `pTmu_fiducial_nucleons`** across 12 playlists,
   inflating the detector-geometry nucleon constant by 12× → xsec
   12× too small when the corrupted value was used. Fix: stop writing
   the TParameter from `runEventLoopOmniFold.cpp`; Python uses the
   fixed tracker-geometry value 3.2353e30 directly.

## Phase 7 — Second-pass remaining bugs (2026-04-23)

Pipeline review while corrected 1A rerun was in flight found four more:

5. **Signal fakes not subtracted on reco side.** Fakes (reco in phase
   space, truth out) live in `mc_signal_reco` but get filtered by
   `omnifold.py`'s `MC_pass_truth_mask`. Add their POT-scaled reco
   weights into `hBkgReco2D` so both measured and MC reco sides are
   fake-free.
6. **Full-stats sbatch missing `--use-weights`** (validated 1A sbatch
   used it). Patched `sbatch_unfold_2d_fullstats.sh`.
7. **Closure mode was unweighted** and included fakes in pseudo-data.
   Now restricts pseudo-data to `pass_reco & pass_truth` and uses
   `sig["w_reco"]` as `measured_weights` when `--use-weights` is on.
8. **`sbatch_unfold_2d.sh` had `set -u` + `srun`** (NERSC footguns).
   Rewrote to `set -eo pipefail`, `PYTHONUNBUFFERED=1`, bare `python`
   — matching `sbatch_validate_1A_corrected.sh`.

## Phase 8 — NERSC-specific pitfalls encountered (2026-04-22 to 23)

- **Wrong-binary foot-gun**: sbatch invoked the pre-fix installed
  `opt/bin/runEventLoopOmniFold` rather than the rebuilt binary. Fix:
  single canonical install path, ensure `make install` runs before
  re-submission. Pre-fix invalidated 1A outputs preserved at
  `archive_2026-03-production-cleanup/debug/*_invalid_wrong_binary_2026-04-22.root`.
- **`set -u` + `conda activate root_6_28`** aborts on
  `CONDA_BACKUP_ROOTSYS` unset in a fresh batch shell. Drop `set -u`.
- **`srun` inside Python unfold sbatch** broke on inherited
  `SRUN_CPUS_PER_TASK` from a parent interactive allocation. Use bare
  `python3`.
- **Priority queueing delays**: corrected 1A validation ran in an
  interactive allocation after an sbatch sat 6 h on `Priority`.

## Phase 9 — Corrected production runs (2026-04-24 to 25)

- **Corrected 1A validation** (2026-04-24 01:35 UTC, interactive on
  `nid004220`): event loop 16 m, 2D unfold 1 h 22 m. Total xsec
  2.484e-38 cm²/nucleon; strict-interior χ²/ndf 19.5; median ratio 0.89.
- **Corrected 1A closure** (2026-04-24 07:02 UTC): textbook
  in-sample result — median 1.0000, RMS 0.0000, 100 % within 5 %.
  `plot_closure_2d.py` ratio formula fixed (stale formula had a
  spurious `pot_scale` factor calibrated against the pre-fix buggy
  pipeline).
- **Corrected 1A iter-convergence** (2026-04-24 11:03 UTC): 5-iter within
  0.08 % of 10-iter on total xsec, 2.1 % per-bin shape RMS.
  `iter_convergence_1A_corrected.png` replaces the stale unweighted plot.
- **Corrected MEHFC fullstats** (2026-04-25 01:10 UTC, sbatch
  `51974026` on `nid004097`): ~28 h wall, 5 iters, data POT 1.057e21,
  MC POT 4.978e21. Total xsec from p_T projection = p_|| projection
  = 2.442e-38 cm²/nucleon (internal consistency ✓). Strict-interior
  χ²/ndf = 17.0 (185 bins, full cov); median bin ratio 0.892.

## Phase 10 — Residual ~11 % low-p_|| deficit localized (2026-04-25)

Strip-by-strip sum-ratio ours/paper on 185 strict-interior bins shows a
**monotonic gradient** from 0.65 at p_||=1.5–2 to 1.00 above p_||=20
GeV/c — not a uniform scale offset. This rules out flux normalization,
fiducial nucleon count, total POT, and bulk background subtraction
(all multiplicative). Three targeted audits:

1. **`hEff2D` vs p_||**: mean efficiency falls smoothly from 0.56 at
   p_||=1.5–2 to a 0.89 plateau above 5 GeV/c. Shape tracks the deficit.
2. **`pass_reco` definition**: reco cut at
   `runEventLoopOmniFold.cpp:372` uses `reco::HasMINOSMatch` which
   calls `CVUniverse::IsMinosMatchMuon()` at `event/CVUniverse.h:107`:
   ```cpp
   return GetInt("has_interaction_vertex") == 1;
   ```
   This is an educational stub — it does NOT enforce a real MINOS
   track-quality match. Admits events at low p_|| that the paper's
   full MINOS cuts would reject → truth-side efficiency denominator
   inflates → xsec biased low in exactly the observed pattern.
3. **`w_reco` composition**: model weights at
   `runEventLoopOmniFold.cpp:388-394` include `FluxAndCVReweighter`,
   `GENIEReweighter`, `LowRecoil2p2hReweighter`,
   `MINOSEfficiencyReweighter`, `RPAReweighter`. The MINOS-eff
   reweighter fires only on events passing the loose reco selection,
   so the issue is upstream pass_reco gating, not weight composition.

**Hypothesis, fix in progress**: override `IsMinosMatchMuon()` to check
the real MINOS-match branch in the AnaTuple (`has_minos_match_track`
or similar), or add a MINOS-quality cut alongside `HasMINOSMatch`.

## Phase 11 — IsMinosMatchMuon stub patched (2026-04-25)

Audited AnaTuple branches on `MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root`:

- `isMinosMatchTrack` (Int_t): 71 % of events have value 1 (matched),
  29 % have −1 (no match).
- `MasterAnaDev_minos_trk_is_ok` (Bool_t): of matched events, ~70 %
  have a passing fit (`trk_is_ok == 1`).
- `muon_is_minos_match_track` / `muon_is_minos_match_stub` are −1 for
  every event — these are placeholder fields in this ntuple and are
  **not** the right discriminator.

Patched `CVUniverse.h:107` to

```cpp
return GetInt("isMinosMatchTrack") == 1 &&
       GetInt(GetAnaToolName() + "_minos_trk_is_ok") == 1;
```

Rebuilt and installed `opt/bin/runEventLoopOmniFold`.

**Re-run 1A (2026-04-25 03:34 → 05:05 UTC)** in interactive allocation
`52023725`. Event loop 14 m, 5-iter unfold 1 h 17 m. Outputs:
`runEventLoopOmniFold_1A_minos_fix.root` (157 MB),
`2d_crossSection_omnifold_1A_minos_fix_5iter.root` (44 KB).

Effects of the patched MINOS-match cut:
- pass_reco: 1,964,015 → **1,774,756** (−9.6 %)
- pass_truth: 2,135,533 → 2,043,981 (−4.3 %)
- `hBkgReco2D`: 48,750 → **1,256** (now 0.35 % of data, matching the
  paper's ~0.2 % background rate — confirms the cut is now correctly
  separating signal from real backgrounds rather than misclassifying
  signal events as fakes)
- Total xsec: 2.484e-38 → **2.328e-38** cm²/nucleon (−6.3 %)
- Strict-interior χ²/ndf: 19.5 → **18.4** (slight improvement)
- Median bin ratio (interior): 0.89 → 0.90

**The fix is a real bug fix but does NOT close the low-p_|| gradient.**
Strip-by-strip sum ratios pre/post:

| p_|| | pre | post |
|---|---|---|
| 1.5–2.0 | 0.65 | 0.60 |
| 2.0–2.5 | 0.64 | 0.61 |
| 5–6     | 0.86 | 0.85 |
| 10–15   | 0.93 | 0.90 |
| 20–40   | 1.04 | 1.00 |

Shape preserved; everything dropped ~3–5 %. The gradient is therefore
**not driven by MINOS-match selection**. Most likely remaining
mechanism: MINOS geometric acceptance / range-out modeling — the paper
applies a dedicated efficiency correction at low p_|| that the
MINERvA-101 tutorial path does not. The `MINOSEfficiencyReweighter`
(`opt/include/PlotUtils/MINOSEfficiencyReweighter.h`) does apply a
momentum-dependent correction via `MinosMuonEfficiencyCorrection`, but
this is the muon-track-quality reweight, not the geometric acceptance
turn-on. Next step: audit how MINOS range-out is handled in our truth
denominator vs the paper.

## Phase 12 — Full MEHFC patched-MINOS production (2026-04-26)

The chained full-production rerun completed after the `IsMinosMatchMuon()`
patch: event-loop array 1B–1P, hadd with the existing 1A minos-fix output,
5-iter full-stats OmniFold, and paper comparison.

Current migrated-tree canonical outputs:

- `2d-unfolding/runEventLoopOmniFold_MEHFC.root`
- `2d-unfolding/2d_crossSection_omnifold_MEHFC_5iter.root`
- `2d-unfolding/baseline_flux/runEventLoopMC_MEHFC.root`

Latest unfolded-result checks:

- data POT / MC POT / pot scale: 1.057e21 / 4.978e21 / 0.212405
- selected data reco entries: 4,091,707
- `hMeasSub2D`: 4.07664e6
- `hTruth2D` / `hUnfold2D`: 4.33620e6 / 4.87974e6
- flux integral: 8.74068e-7 cm^-2/POT
- total xsec from p_T and p_|| projections: 2.285e-38 cm²/nucleon
- strict-interior comparison: χ²/ndf = 17.443, median ours/paper = 0.8968
- all reported bins: χ²/ndf = 20.605

Conclusion: the full patched-MINOS rerun is internally consistent and
independent of the old working tree for its active inputs, but it did not
fix the low-p_|| deficit. The remaining disagreement is still attributed
primarily to the flux-CV / paper-era flux-release mismatch documented in
the status file.

## Phase 13 — Final presentation plots and diagnostic framing (2026-04-27)

Generated final discussion plots in the migrated `2d-unfolding/` directory:

- `1A_iterscan_convergence.png` — rebuilt from the existing old-tree
  `2d_crossSection_omnifold_1A_corrected_{1,3,5,8,10}iter.root` files.
  Corrected pre-MINOS-fix 1A scan; supports the 5-iteration production
  choice (5 iter within ~0.08% of 10 iter in total xsec, ~2.1%
  per-bin RMS shape difference).
- `MEHFC_5iter_fig13.png` — Fig.-13-style full 2D slice overlay: paper
  data, OmniFold, and local MC truth. OmniFold is often closer to local MC
  truth than the paper data are, but that is not a proof of better
  unfolding because the local MC truth is not ground truth.
- `MEHFC_5iter_eff_fig5.png` — Fig.-5-style `hEff2D` map using a ROOT-like
  palette and white bins only where the bin is entirely outside
  θ_μ < 20° (`pT_low / p||_high > tan20`). The paper ancillary release does
  not provide the Fig. 5 efficiency map, so this remains qualitative.
- `MEHFC_5iter_truth_vs_paper_strips.png` — paper ancillary Tune-v1 model
  vs local MC truth shape per p_|| strip. Strip shape ratios paper/local:
  1.43 in p||=1.5-2.0, 1.29 in 2.0-2.5, falling below one at high p||.
- `1A_reweighter_decomp_strips.png` — per-reweighter component dump from
  `/pscratch/sd/j/josephrb/MINERvA101/Documents/component_dump_1A/`.
  Relative to the high-p|| plateau, `w_FluxAndCV` is 0.672 in the first
  p|| strip while GENIE, 2p2h, MINOS efficiency, and RPA are flat.
  Clearest internal evidence that the truth-shape mismatch is carried
  by `FluxAndCV`.

Current framing for advisor/reporting:

- The C++ selection, POT handling, binning, background subtraction,
  OmniFold weights, full-covariance comparison, and plotting machinery are
  in a final audited state.
- The MINOS-match tutorial stub was a real bug and is fixed, but it did not
  close the low-p|| gradient.
- The dominant discrepancy is already present in the truth-side model shape
  when comparing local MC truth to the paper ancillary Tune-v1 model.
- Selection efficiency is not ruled out as a subleading residual, especially
  because the paper does not release Fig. 5 numerically, but the available
  evidence points first to paper-era flux-CV release/version dependence.
- Exact quantitative reproduction of arXiv:2106.16210 requires the 2021
  flux-CV files or an explicit low-p|| flux/model systematic caveat.

## Phase 14 — MINERvA-101 tutorial MINOS patch delta (2026-05-02)

Question: after MINERvA-101 patched the tutorial stub to require
`isMinosMatchTrack == 1`, is our extra
`MasterAnaDev_minos_trk_is_ok == 1` requirement still a physics-relevant
difference?

Raw AnaTuple branch checks on playlist 1A show that the extra
`_minos_trk_is_ok` condition has **zero incremental impact after the 2D
reco selection**. The branch-level selection reproduced the 2D reco cut
logic with tracker `z`, tracker apothem, `muon_theta < 20 deg`,
`phys_n_dead_discr_pair_upstream_prim_track_proj < 1`, and negative
`MasterAnaDev_minos_trk_qp`.

Full 1A selected counts:

| sample | `isMinosMatchTrack == 1` | plus `_minos_trk_is_ok == 1` | delta |
|---|---:|---:|---:|
| Data | 346,768 | 346,768 | 0 |
| MC selected | 1,725,226 | 1,725,226 | 0 |
| MC signal (`mc_incoming == 14 && mc_current == 1`) | 1,721,126 | 1,721,126 | 0 |
| MC background | 4,100 | 4,100 | 0 |

The `ok` branch is not globally redundant: before the full reco cuts, there
are `isMinosMatchTrack && !_minos_trk_is_ok` events. On representative 1A
files, however, those events are removed by the tracker-apothem cut before
they can enter the selected sample:

| sample file | raw `track && !ok` | after tracker-z | after tracker-apothem |
|---|---:|---:|---:|
| Data run 6038 | 3,622 | 1,291 | 0 |
| MC run 110000 | 40,976 | 25,804 | 0 |

Conclusion: for the active 2D selection, the physics-changing tutorial fix
is the move from the educational `has_interaction_vertex == 1` stub to
`isMinosMatchTrack == 1`. Our stricter
`isMinosMatchTrack == 1 && _minos_trk_is_ok == 1` implementation remains
cleaner and defensible, but relative to the newly patched MINERvA-101
tutorial it is effectively a no-op for the selected 2D event sample.

## Phase 15 — Flux-CV file ruled out as the residual driver (2026-05-05)

While drafting outreach to the MINERvA collaboration to request the
paper-era flux-CV files, two questions came up: (a) are the local files
actually different from the paper-era release, and (b) if so, does the
difference predict the residual?

Inputs cross-checked. The local files are a CVS checkout of
`AnalysisFramework/Ana/MATFluxAndReweightFiles` from
`minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft`, with all per-playlist files
timestamped 2021-07-07 — i.e., one month after arXiv:2106.16210 was
posted. The CV histogram (`flux_E_cvweighted`) lives in the gen2thin
files; the Geant4 baseline (`flux_E_unweighted`) in the g4numiv6 files.
`FluxAndCVReweighter` returns the ratio at the event's E_ν.

Comparison against arXiv:1906.00111 (PRD 100 092001) ancillary release.
Ancillary file `MINERvA_Flux_pdg14_500MeVBins.csv` is the paper-era
nu-e-constrained ME FHC nu-mu CV flux that arXiv:2106.16210 cites in
its flux section. Wrote `compare_flux_to_paper_2019.py` which:

- Reads per-playlist data POT from
  `baseline_flux/runEventLoopData_<P>.root`.
- Maps 1A..1P to 3 unique flux files via the `playlistString()` table
  (1A..1F→1D, 1G/1L/1M→1M, 1N..1P→1N).
- POT-weights `flux_E_cvweighted` and `flux_E_unweighted` across the
  three unique files (1D 53.45 %, 1M 29.23 %, 1N 17.32 %).
- Compares against the 2019 ancillary CSV at bin centers.

Result. paper / local (POT-weighted MEHFC):

| E_ν (GeV) | paper / local | E_ν (GeV) | paper / local |
|---|---|---|---|
| 1.65 | 1.00 | 5.00 | 0.90 |
| 2.50 | 0.89 | 7.00 | 0.91 |
| 3.50 | 0.89 | 9.00 | 0.93 |

Roughly flat ~0.90 across the populated range. The 1.55 GeV (1.09)
and 1.65 GeV (1.00) entries are interpolation noise at the edge of the
paper's 1.0–1.5 GeV bin, not a real low-E_ν shape feature.

Cross-section algebra. Both the per-event `FluxAndCV` weight and the
integrated denominator come from the same `flux_E_cvweighted`
histogram — the per-event weight is `Phi_cv(E_ν)/Phi_g4(E_ν)`, and the
denominator is built by `FluxReweighter::GetIntegratedFluxReweighted`
which integrates `Phi_cv` directly (`MAT/PlotUtils/FluxReweighter.cxx`
lines 1305–1339). A flat scale `Phi_cv → α·Phi_cv` therefore scales
hUnfold2D, hSignal_truth_total, hSignal_truth_reco, and Phi_integrated
all by α; α cancels in dsigma = U/(eff·Phi·N). The actual ratio varies
between 0.87 and 0.93 over the populated range, so the cancellation is
near-exact with at most a few-% residual from the small E_ν shape
variation. **Adopting the 2019-release flux files would not move our
cross section in normalization or shape.**

Implications:

- The "local flux-CV files explain the 1.41× low-p_|| truth shape
  ratio" framing in the prior status doc was wrong.
  `decompose_truth_weights.py` correctly attributed the strip-by-strip
  gradient to the applied `FluxAndCV` weight column, but that does not
  imply the flux histogram itself is the cause — the gradient survives
  any flat rescaling of the histogram. The strip-by-strip ratio being
  identical between the combined truth weight and the FluxAndCV column
  says the kinematic correlation (low p_||(μ) ↔ low E_ν, where the
  nu-e constraint pulls the flux down) is being applied as designed;
  it does not say the flux file is bad.
- The residual ~16.6 % global xsec deficit and the low-p_|| shape
  gradient must come from a source upstream of the reweighter chain.
  The most parsimonious single-cause hypothesis is that the AnaTuple
  base MC sample was generated with a different GENIE version / 2p2h
  dial / non-resonant suppression than the sample arXiv:2106.16210
  ran on. Reweighters cannot recover a different base generation.
- The user's outreach email reframed accordingly: instead of "give me
  the paper-era flux files because they explain the residual," the ask
  becomes "I have ruled out the flux-CV files as the source; can you
  confirm the AnaTuple generator/tune config used for the paper, and
  whether the Open Data Product samples were generated with that same
  config?"

Outputs committed:

- `2d-unfolding/compare_flux_to_paper_2019.py` — comparison script.
- `2d-unfolding/MINERvA_Flux_pdg14_500MeVBins_arXiv1906_00111.csv` —
  the 2019 ancillary file, kept locally for reproducibility.
- `2d-unfolding/compare_flux_to_paper_2019.png` — overlay + ratio
  panels.
- `2d-unfolding/compare_flux_to_paper_2019.csv` — per-bin numerics.

## Phase 16 — Truth-shape attribution: efficiency denominator bug found and fixed (2026-05-08)

While preparing the slide-deck rewrite to ask the MINERvA collaboration
about generator-config provenance (Phase 15's hypothesis), the obvious
falsifying test had not yet been run: project the local *unweighted*
truth onto the (p_T, p_||) grid and compare to the paper's MnvTune-v1
ancillary. If the unweighted shape already disagreed at low p_||, the
generator-config story would be supported. If the unweighted shape was
fine and only the weighted shape disagreed, the reweighter chain would
be implicated. If both agreed, the disagreement we had been chasing
would be in something else entirely.

`diagnose_truth_shape_unweighted.py` reads `mc_truth_denom` directly
from `runEventLoopOmniFold_MEHFC.root` (32.85M entries — the canonical
Truth-tree efficiency denominator), projects it onto the paper grid
both unweighted and with the local MnvTune-v1 reweighter chain applied,
and shape-normalizes both inside the 185-bin strict interior for
comparison against the paper Tune-v1 model.

Result: `paper / weighted` is **0.99 – 1.00 across p_|| = 1.5 – 9 GeV/c**
and reaches 1.10 – 1.15 only in the highest p_|| tails (20 – 60 GeV/c)
which carry small fraction. The 1.43× low-p_|| feature seen in the
prior diagnostic against `hTruth2D` is **gone**. The local truth + local
MnvTune-v1 reweighter chain reproduces the paper's published MnvTune-v1
prediction to ~1 %.

Source of the prior false signal. The unfold script's `hTruth2D` is
filled from `mc_signal_reco` (24.46M entries — only events with a
reco-tree entry):

- `unfold_2d_omnifold_unbinned.py:475` loads `mc_signal_reco`. It does
  not load `mc_truth_denom`.
- Lines 663 – 665 fill `hTruth2D` from `sig` truth-pass events, i.e.
  the `mc_signal_reco` subset.
- `compute_efficiency_2d` (line 323) builds `hEffDen` from the same
  subset.

The 8.4M-event difference (32.85M – 24.46M) is preferentially at low
p_||: events at high muon angle / low forward momentum produce less
reconstructable activity in MINERvA, and the AnaTuple production drops
their reco-tree entries. So the `mc_signal_reco` subset is depleted at
low p_||, which is what `hTruth2D` was reporting.

Cross-section consequence (the actual bug). The cross-section formula
`σ = hUnfold2D / (Φ · N · POT · dpT · dp_||)` had `hEff` deleted at the
top of `extract_cross_section_2d` (line 371), with the docstring
claiming OmniFold's step-1 miss regression absorbed the efficiency
correction. That is partially true: step-1 miss regression handles
events with `pass_reco = False` that are *present in the OmniFold
input*. The `mc_signal_reco` tree contains both reco-passing
(`sim_pass = true`) and reco-failing (`sim_pass = false`) truth-pass
events, so OmniFold's miss regression handles the within-input misses
correctly. What it cannot handle are truth events absent from the input
entirely — the 8.4 M events in `mc_truth_denom` that have no reco-tree
entry at all.

Result: `hUnfold2D` represents inferred truth-level data over the
`mc_signal_reco` truth-pass subset only. The cross section computed
without an external rescaling is therefore low by exactly the
*input-completeness* deficit, preferentially at low p_||. Numerical
check:

- N(`mc_signal_reco` truth-pass) / N(`mc_truth_denom`)
  = 24.46M / 32.85M = **0.745**
- σ_total(ours) / σ_total(paper) = 2.285e-38 / 3.039e-38 = **0.752**

The agreement is at the 1 % level.

The right correction is therefore the OmniFold *input completeness*
ratio, **not** the standard absolute selection efficiency
ε = (`sim_pass = true` events) / (all truth events). Dividing by the
absolute ε would over-correct, because OmniFold has already absorbed
the within-input selection inefficiency through miss regression
(verified numerically: dividing by ε ≈ 0.6 gives 1.25× paper, 25 % too
high; dividing by completeness ≈ 0.745 gives 0.989 × paper, ~1 %
agreement).

Definitions, all in the unfold output:

- `hEff2D` = `hEffNum` / `hEffDen` = absolute selection efficiency,
  diagnostic only (used by `plot_efficiency_fig5_style.py` for paper
  Fig. 5 comparison). `hEffNum` keeps the standard meaning
  (`sim_pass = true` events), and `hEffDen` is now the canonical
  `mc_truth_denom` denominator.
- `hOFCompleteness2D` = `hOFInputTruth2D` / `hOFTruthDenom2D`, where
  `hOFInputTruth2D` is mc_signal_reco truth-pass events (regardless of
  `sim_pass`) and `hOFTruthDenom2D` is `mc_truth_denom`. This is the
  fraction of truth events that OmniFold sees. Cross-section formula
  divides by it.

Fix implemented in `unfold_2d_omnifold_unbinned.py`:

1. New helper `collect_truth_denom_arrays` reads `mc_truth_denom` and
   returns truth_pt / truth_pz / w_truth arrays (POT-scaled, binning-
   range-filtered).
2. `main()` loads the `mc_truth_denom` tree alongside the existing
   `mc_signal_reco` / `mc_background` / `data` trees (skipped in
   `--closure` mode for self-consistent closure behavior).
3. `compute_efficiency_2d` accepts an optional `truth_denom` argument;
   when given, fills `hEffDen` from `mc_truth_denom` instead of from
   the `mc_signal_reco` truth-pass subset. Same numerator semantics
   (selection-passing events, weighted by `w_reco`) so `hEff2D` is
   still a paper-Fig.-5-comparable selection efficiency.
4. New `compute_omnifold_completeness_2d` builds the input-completeness
   correction `hOFCompleteness2D = hOFInputTruth2D / hOFTruthDenom2D`.
5. `extract_cross_section_2d` now divides by `hOFCompleteness2D` per
   bin. Empty-completeness bins safely emit zero.
6. In `--closure` mode, `hOFCompleteness2D` is set to 1.0 in every bin
   to preserve the legacy in-sample closure behaviour (synthetic data
   lives in the same subset as training, so no scale-up is appropriate).
7. New diagnostic histograms (`hOFCompleteness2D`, `hOFInputTruth2D`,
   `hOFTruthDenom2D`) added to the output. Existing `hTruth2D`,
   `hEffNum`, `hEffDen`, `hEff2D` retained with unchanged or
   well-documented semantics.
8. Docstring of `extract_cross_section_2d` corrected — the claim that
   step-1 miss regression handles all efficiency was incomplete.

Verification (`verify_eff_fix_predicted_xsec.py`): apply the post-fix
formula to the existing pre-fix `hUnfold2D` and rederived ε from
`mc_truth_denom`. Predicts post-fix σ_total = **3.006e-38 cm²/nucleon
vs paper 3.039e-38 (ratio 0.989)**. Per-strip post/paper ratios:

| p_|| (GeV/c) | pre/paper | post/paper |
|---|---|---|
| 1.5–2.0  | 0.572 | ~1.14 |
| 2.0–2.5  | 0.635 | ~1.14 |
| 5.0–6.0  | 0.849 | ~1.05 |
| 20–40    | 0.984 | ~1.03 |

Low-p_|| residual collapses from 0.57× to ~1.14×, high-p_|| from 0.98×
to 1.03×. The remaining ~5–14 % residual at low p_|| is consistent
with the small (≤ 1 %) shape disagreement in `paper / weighted` plus
unfold-stage detail; it does not have the dramatic gradient we were
chasing.

What this overturns:

- "Local flux-CV files explain the residual" (Phase 14) — already
  ruled out in Phase 15, still ruled out.
- "AnaTuple generator-config mismatch explains the residual"
  (Phase 15) — ruled out in Phase 16. Local truth shape with
  MnvTune-v1 applied agrees with the paper to ~1 %.
- "The per-reweighter `FluxAndCV` column is the carrier of the
  low-p_|| gradient" (Phase 12 – 13) — the column ratio is still
  numerically what was measured, but it described the per-reweighter
  shape on the `mc_signal_reco` subset, not a physical low-p_||
  pull. With the proper denominator, the reweighter chain is
  reproducing the paper MnvTune-v1 prediction in shape.

What does **not** change:

- MINOS-match selection patch (Phase 11) — still a real fix that
  reduced background rate from ~10 % to 0.35 %.
- Iter-scan convergence (5-iter is fine) — still valid.
- Flux normalization, nucleon count, POT bookkeeping, paper binning —
  all still correct.

Re-run pending. The committed `2d_crossSection_omnifold_*.root` outputs
were produced before this fix and have the ~24.8 % global deficit and
the low-p_|| shape gradient. Re-running the unfold with the fix should
collapse both. Plan: re-run on 1A first (cheapest closure check), then
on full MEHFC if 1A behaves.

Outputs committed:

- `2d-unfolding/diagnose_truth_shape_unweighted.py` — full-stats
  unweighted-vs-weighted-vs-paper truth-shape diagnostic.
- `2d-unfolding/truth_shape_unweighted_MEHFC_summary.json` — per-strip
  numerics (paper / unweighted, paper / weighted, weighted / unweighted).
- `2d-unfolding/truth_shape_unweighted_MEHFC_strips.png` — overlay +
  ratio panels.
- Updated `2d-unfolding/unfold_2d_omnifold_unbinned.py` — denominator
  fix (`compute_omnifold_completeness_2d` + completeness division in
  `extract_cross_section_2d`), see the source for the changes
  summarized above.
- `2d-unfolding/verify_eff_fix_predicted_xsec.py` — applies the
  post-fix formula to the stored pre-fix `hUnfold2D` to predict
  post-fix totals without re-unfolding. Confirmed σ_total/paper =
  0.989 globally and strip ratios within ~5–14 % across p_||.

### Working-directory cleanup (2026-05-08)

After the post-fix unfold (job 52729573) was launched, the working
directory was cleaned up while the rerun was in flight.

**Archived to `archive_pre_phase16/`** (preserved for pre/post comparison):
- `2d_crossSection_omnifold_MEHFC_5iter.root` — pre-fix MEHFC unfold.
- `2d_crossSection_omnifold_MEHFC_5iter_shape.root` — pre-fix self-
  normalized shape ROOT.
- `2d_crossSection_omnifold_1A_minos_fix_{1,3}iter.root` — patched-MINOS
  1A iter-scan ROOTs.
- All `MEHFC_5iter_*.png` plots derived from the pre-fix MEHFC ROOT
  (xsec slices, projections, pull maps, fig13, eff_fig5, eff_heatmap,
  truth_vs_paper_strips, shape variants). These describe the 0.752 ×
  paper state and will be regenerated from the post-fix output.
- `1A_reweighter_decomp_strips.png` — the per-reweighter `FluxAndCV`
  decomposition strip plot. Numerically still correct but its
  interpretation (FluxAndCV "carries" the low-p_|| gradient) is
  superseded — the gradient was an artifact of the wrong denominator,
  not a physical pull from any reweighter.

**Deleted** (findings preserved in this run log; scripts are
re-derivable from the run log description if ever needed):
- Phase-8/10 MINOS-acceptance diagnostic scripts:
  `audit_minos_acceptance_correction.py`,
  `diagnose_minos_acceptance_2d.py`,
  `minos_acceptance_1A_summary.json`,
  `minos_acceptance_audit_1A_summary.json`. Their finding (a missing
  MINOS geometric-acceptance correction was *not* the residual driver)
  is documented in Phase 10 – 11.
- Phase-12 weights-vs-pz scan: `diagnose_weights_vs_pz.py`,
  `weights_vs_pz_1A_summary.json`. Finding (combined w_truth has
  low-p_|| dip carried entirely by FluxAndCV column) was the
  motivation for Phase 13 and is documented there.
- Phase-13 per-reweighter decomposition: `decompose_truth_weights.py`,
  `decompose_truth_weights_1A_summary.json`. Finding
  (FluxAndCV column matches the strip ratio) is documented in
  Phase 13. The script is re-derivable from a `MNV101_DUMP_COMPONENTS`
  build.
- Phase-13/14 truth-shape diagnostic: `diagnose_truth_shape_vs_paper.py`,
  `truth_shape_vs_paper_1A_summary.json`,
  `truth_shape_vs_paper_MEHFC_5iter_summary.json`. This was the
  diagnostic that produced the 1.43× low-p_|| feature on `hTruth2D`
  (mc_signal_reco subset). Phase 16 supersedes it with
  `diagnose_truth_shape_unweighted.py` which runs on the canonical
  `mc_truth_denom` denominator. The 1.43× number is preserved in
  this run log along with the explanation of why it was an artifact.
- `SLIDES_OUTLINE.md`, `SLIDES_NEW_DRAFT.md` — outreach drafts framed
  around the flux-CV (Phase 14) and generator-config (Phase 15)
  hypotheses, both now superseded. Outreach is paused pending the
  post-fix re-run; if a new deck is needed the content can be
  regenerated from this run log + the status doc.
- Old SLURM logs: `finalize_MEHFC_52031722.{out,err}`,
  `unfold2d_full_52031697.{out,err}`.
- `__pycache__/`.

### Post-fix re-run results (2026-05-09)

Job 52729573 (`unfold2d_postfix`) finished after ~18 h 43 m on shared QOS
nid004108 and wrote `2d_crossSection_omnifold_MEHFC_5iter_postfix.root`.
OmniFold-internal sanity numbers from the run:

- step1 / step2 weights count: 24,394,265 (matches `mc_signal_reco`
  truth-pass).
- step2 weight stats: sum 2.735e7, mean 1.1212, range [0.7383, 3.5332]
  (identical to pre-fix — the fix is downstream of OmniFold).
- `hOFInputTruth2D` integral 4.3362e6, `hOFTruthDenom2D` integral
  5.7796e6 → global completeness c = 4.3362 / 5.7796 = **0.7503**.
  Matches the predicted 24.46M / 32.85M = 0.745 to ~1 %.
- σ_total from p_T projection = σ_total from p_|| projection =
  **3.055e-38 cm²/nucleon**. Paper total 3.039e-38 → σ/paper =
  **1.0049**, vs predicted 0.989. Both projections agree to all reported
  digits, so the closure between p_T- and p_||-projected totals survives
  the fix.

Plots regenerated from the post-fix output (all 14 production PNGs in
`PLOT_GUIDE.md`):

- `MEHFC_5iter_xsec_{pt,pz}_slices.png`,
  `MEHFC_5iter_xsec_proj_{pt,pz}.png`, `MEHFC_5iter_xsec_eff_heatmap.png`
  (`plot_2d_cross_section.py`).
- `MEHFC_5iter_xsec_paper_{pt,pz}_slices.png`
  (`plot_2d_paper_comparison.py`).
- `MEHFC_5iter_pull_full.png` (`compare_to_paper_fullcov.py`),
  `MEHFC_5iter_pull_interior.png` (`compare_to_paper_interior.py`).
- `MEHFC_5iter_fig13.png` (`plot_2d_threeway_fig13.py`),
  `MEHFC_5iter_eff_fig5.png` (`plot_efficiency_fig5_style.py`).
- Shape ROOT regenerated as
  `2d_crossSection_omnifold_MEHFC_5iter_postfix_shape.root`
  (`normalize_xsec_shape.py`); shape comparison plots
  `MEHFC_5iter_xsec_paper_{pt,pz}_slices_shape.png`,
  `MEHFC_5iter_pull_interior_shape.png`
  (`plot_2d_paper_comparison_shape.py`).

χ²/ndf vs paper, post-fix (TOTAL covariance from the ancillary):

| Metric | Bins | χ²/ndf | χ² / ndf |
|---|---|---|---|
| Absolute, all reported     | 205 | **3.289** | 674.20 / 205 |
| Absolute, strict interior  | 185 | **3.188** | 589.71 / 185 |
| Shape, all reported        | 204 | **3.269** | 666.85 / 204 |
| Shape, strict interior     | 184 | **3.160** | 581.45 / 184 |

Pre-fix the same quantities were 17.4 (185 strict interior) and 20.6
(205 reported). Pull mean / RMS on the 205 reported bins (full cov) is
**−0.001 / 0.565** — pulls are now centered with sub-σ scatter.

Per-bin ratio collapse on the strict-interior 185-bin set, ours/paper:

- median = **1.0049**, mean = 1.0000
- 5 % window: **82.7 %** of bins agree to within 5 % of paper (was ~0 %
  in low-p_|| pre-fix).
- 10 % window: 94.6 %.
- 20 % window: 98.4 %.

The strip-by-strip σ/paper gradient that ranged 0.572 (1.5–2 GeV/c) to
0.984 (20–40 GeV/c) pre-fix is gone. χ² as a function of p_||-min cut on
the strict interior:

| p_|| ≥ (GeV/c) | N bins | χ² | χ²/ndf | median ratio | %<5% |
|---|---|---|---|---|---|
| 1.5 | 185 | 589.71 | 3.188 | 1.0049 | 82.7 % |
| 2.0 | 179 | 543.26 | 3.035 | 1.0031 | 83.8 % |
| 2.5 | 171 | 461.21 | 2.697 | 1.0037 | 84.2 % |
| 3.0 | 162 | 408.87 | 2.524 | 1.0034 | 84.0 % |
| 3.5 | 152 | 397.07 | 2.612 | 1.0053 | 82.9 % |
| 4.0 | 141 | 371.43 | 2.634 | 1.0053 | 81.6 % |

Low-p_|| bins no longer dominate the comparison. Residual χ²/ndf ≈ 3 is
still above unity but is approximately p_||-flat — consistent with
small ≤ few-% shape mismatches in the high-p_|| tails seen in the
truth-shape diagnostic, plus possibly the near-singular flux-only
covariance representation (`flux_only` χ²/ndf comes back at 9.6e7,
unchanged from pre-fix; this is an ancillary-file representation issue,
not a numerical issue with the cross section).

What this confirms:

- The Phase 16 diagnosis was correct. Predicted σ/paper = 0.989 vs
  measured 1.0049 is a 1.6 % discrepancy attributable to the predictor
  using strip-averaged completeness as a global scalar; the per-bin
  completeness used by the actual unfold has small (~1 %) finer
  structure that the predictor smoothed over.
- The only remaining shape discrepancy with the paper is a sub-2 %
  effect concentrated in the highest p_|| tails (p_|| > 10 GeV/c),
  consistent with the `paper / weighted` ≈ 1.05 – 1.15 in those bins
  reported by `diagnose_truth_shape_unweighted.py`. Not a low-p_||
  pathology any more.

Outreach to the MINERvA collaboration is no longer needed — there is
no missing-input hypothesis to ask about. The remaining discrepancy is
within paper-level shape disagreement that the truth-shape diagnostic
already characterized.

Phase 16 closed.

### Phase-16 follow-up: IBU 1D-projection cross-check, post-fix (2026-05-10)

Re-ran the advisor-requested 1D IBU on a 1D projection of the same
2D OmniFold inputs to confirm that the Phase-16 fix is method-blind.
Found that `build_1d_ibu_inputs.py` had the **same** input-completeness
bug as the 2D unfold pre-fix: it filled the efficiency denominator (and
the 2D truth yield used for the per-p_|| harmonic-mean flux) from
`mc_signal_reco` truth-pass events (24.5M) rather than from
`mc_truth_denom` (32.85M). A literal repeat of the cross-check would
therefore have reproduced the pre-fix story for both legs and looked
"consistent" while both were wrong by the same factor.

Patched `build_1d_ibu_inputs.py` analogously to the 2D fix:

- Pulled the eff_den and 2D truth-yield fills out of `fill_signal`.
- Added new `fill_truth_denom` that reads `mc_truth_denom` and fills
  `eff_den["pTmu"]`, `eff_den["pZmu"]`, and `h2d_truth` with `w_truth`.
- Loaded `mc_truth_denom` alongside the existing
  `data` / `mc_signal_reco` / `mc_background` trees.
- Default `--xsec-2d` switched to the postfix file.

Pipeline re-ran interactively (build ~2 min, IBU 5-iter ~seconds, plot
~seconds):

- `mc_truth_denom` kept = 32,849,236 (matches the 2D unfold).
- `mc_signal_reco` eff_num = 20,940,810; eff_num integral 1.745e7 /
  eff_den integral 2.721e7 → global ε ≈ 0.641 (proper absolute
  selection efficiency on the canonical denominator).
- IBU 5-iter wrote `pTmu_crossSection.root` and
  `pZmu_crossSection.root`; libMAT cleanup segfault at exit is the
  documented benign issue, the unfolded outputs flush before it.

Three-way comparison (IBU on 2D-projection vs OmniFold-2D 1D-projected
vs paper TH2D 1D-projected), integrals over reported bins:

| Axis | Paper | OmniFold-2D 1D-proj | IBU-on-2D-proj |
|---|---|---|---|
| p_T  | 3.039e-38 | 3.054e-38 (1.005) | 3.003e-38 (0.988) |
| p_|| | 3.039e-38 | 3.055e-38 (1.005) | 2.965e-38 (0.976) |

Both methods reproduce the paper to ≤ 2.5 % and agree with one another
to ~1.7 %. The Phase-16 input-completeness correction is method-blind;
the third row of the README's interpretation table ("2D OmniFold doing
something IBU isn't") is ruled out.

Also confirms that the IBU pipeline is a usable independent
cross-check going forward, now that its build-script Phase-16 bug is
fixed.

Plots regenerated:
- `2d-unfolding/ibu_1d_projection/MEHFC_5iter_ibu_1d_proj_pt.png`
- `2d-unfolding/ibu_1d_projection/MEHFC_5iter_ibu_1d_proj_pz.png`

Files modified:
- `2d-unfolding/ibu_1d_projection/build_1d_ibu_inputs.py` — see fix
  description above.
- `2d-unfolding/ibu_1d_projection/plot_ibu_1d_proj_vs_omnifold.py` —
  default `--omnifold-2d` switched to postfix file.
- `2d-unfolding/ibu_1d_projection/sbatch_ibu_1d_projection.sh` — same
  default switch.
- `2d-unfolding/ibu_1d_projection/README.md` — Phase-16 update note at
  top, method section updated to describe the `mc_truth_denom` read.

## Phase 17 — Replace c correction with native OmniFold miss entries (in progress, 2026-05-14)

### Motivation

After sending Ben the post-Phase-16 slide deck (`reference/MINERvA with
OmniFold.pdf`), he correctly pointed out that OmniFold *should* be able
to handle truth-without-reco events natively via step-2 miss
regression — and asked whether the c correction is applied per-bin (it
is; `hCompleteness.GetBinContent(ix, iy)` in
`extract_cross_section_2d`, even though the slide formula shows a
single c).

The reason the c correction is needed *in the current pipeline* is not
an OmniFold limitation but an input-construction one: the
`LoopAndFillUnbinnedMCSelectedSignalReco` walk in
`runEventLoopOmniFold.cpp` iterates over the AnaTuple Data/reco tree
(`options.m_mc`), so the 8.4M fiducial-truth events that have **no
reco-tree entry at all** never enter `mc_signal_reco` — OmniFold
cannot reweight events it never sees. The within-input misses
(`sim_pass = false`, `sim = -9999` entries) are fed correctly; the
truth-only misses (no AnaTuple reco entry) are not.

The plan is to add the truth-only miss entries to the OmniFold input
during the event loop. Once those are in, OmniFold's step-2 miss
regression handles them natively and the per-bin c correction becomes
redundant (modulo a closure check).

### Design (open)

The implementation question is how to avoid double-counting. If the
Truth-tree walk simply writes every truth-pass event to
`mc_signal_reco` as a miss entry, the ~24.46M truth-pass events that
already have a reco-tree entry get duplicated.

Three options sketched, none yet committed:

- **(A) Event-ID matching.** Build a hash set of
  `(mc_run, mc_subrun, mc_nthEvtInFile)` from the reco-tree walk
  (these branches exist on the AnaTuple — confirmed by
  `MINERvA101/GENIEXSecExtract/src/XSecLooper.cxx:422-424`). During
  the truth-tree walk, write a miss entry only for truth-pass events
  whose ID is **not** in the set. This is the cleanest design and
  keeps `mc_signal_reco` as the single OmniFold input tree.
- **(B) Separate `mc_truth_only_miss` tree.** Truth walk writes all
  truth-pass events to a new tree; Python concatenates them with
  `mc_signal_reco` after deduplicating on event ID. Same matching
  cost; just splits the work between C++ and Python.
- **(C) Approximate — no event ID.** Cannot be made exact; would need
  a sampling step that introduces a bias of order the matching error.
  Rejected.

Working assumption: **(A)** with `(mc_run, mc_subrun, mc_nthEvtInFile)`
as the join key. Need to confirm that all three branches are present
on both the Truth tree and the AnaTuple reco tree of the playlists we
use, and that the triplet is unique within a playlist.

### Implementation status (2026-05-14, code committed pending validation)

Option (A) — event-ID matching on `(mc_run, mc_subrun, mc_nthEvtInFile)` —
implemented in `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`:

- New `makeEventKey(run, subrun, nth)` packs the triplet into a `uint64_t`
  for fast hash-set lookup.
- `LoopAndFillUnbinnedMCSelectedSignalReco` takes an optional
  `std::unordered_set<uint64_t>* outRecoIDs`; when non-null, every event
  written to `mc_signal_reco` gets its event-ID inserted.
- `LoopAndFillUnbinnedMCTruthDenom` takes optional `(sigOut, recoIDs)`;
  when both non-null, the loop re-binds `mc_signal_reco`'s branches to
  local variables and, for each truth-pass event whose ID is **not** in
  `recoIDs`, appends a miss entry (`sim=-9999`, `sim_pass=false`,
  `MC=truth_pT`, `MC_pz=truth_pz`, `w_truth=truth_w`,
  `w_reco=truth_w` as proxy). Returns the count of miss entries appended.
- `main()` reorders so the reco walk runs **before** the truth walk so
  the ID set is populated before the truth walk consumes it. Mode is
  on by default; `MNV101_DISABLE_TRUTH_MISSES=1` falls back to legacy
  behaviour. `MNV101_TRUTH_ONLY` continues to short-circuit reco loops
  and (for safety) suppresses the miss-append.
- Two new `TParameter`s are written to the output ROOT file:
  `hasTruthOnlyMisses` (int 0/1) and `nTruthOnlyMisses` (long).
- Build verified clean; binary installed to both
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/bin/runEventLoopOmniFold`
  and `/pscratch/sd/j/josephrb/MINERvA101/opt/bin/runEventLoopOmniFold`.

Pipeline-side change in `2d-unfolding/unfold_2d_omnifold_unbinned.py`:
reads the two new TParameters, prints a status line, and emits a `[WARN]`
if `hasTruthOnlyMisses=1` but `c_global` deviates from 1.0 by >0.5 %
(would indicate a matching bug). The c-division code path is unchanged;
when c ≈ 1 it becomes a no-op, so legacy and Phase-17 inputs both work.

#### Source-tree fix (2026-05-14)

The CMake build dir at
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MINERvA-101-Cross-Section/build`
previously had `CMAKE_HOME_DIRECTORY` pointing at the older standalone
clone at `/pscratch/sd/j/josephrb/MINERvA101/...` (via the
`/global/homes/j/josephrb/MINERvA101` symlink) and
`CMAKE_INSTALL_PREFIX` pointing at the standalone's opt dir, so
edits in the canonical tree had to be mirrored to the standalone
before rebuilding. Fixed by:

1. `mv build build.standalone-shadow.bak` (kept as rollback).
2. Fresh `cmake -S /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MINERvA-101-Cross-Section
   -B build -DCMAKE_INSTALL_PREFIX=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt`
   after `source $MINERVA_PREFIX/bin/setup_MAT_IncPions.sh` (env was
   already pointing at canonical).
3. `make -j16 && make install` installed all targets into canonical
   opt/. Generated `setup_MAT_IncPions.sh` in canonical opt/bin now
   defaults `PREFIX` to canonical.

Standalone clone at `/pscratch/sd/j/josephrb/MINERvA101/` is now
orphan (no build references it). Its opt/bin was sync'd with the new
binary for safety in case any unmonitored script still resolves the
`/global/homes/j/josephrb/MINERvA101` symlink. Future cleanup: delete
the standalone clone entirely once we've gone a few weeks without
anything referencing it.

### Next steps when resuming

1. ~~Confirm event-ID triplet uniqueness~~ — implementation chose Option
   (A) and the build is clean; left to runtime to surface any matching
   bugs (the pipeline `[WARN]` will fire if `c_global` ≠ 1).
2. ~~Implement Option (A)~~ — done (this section).
3. ~~Update `unfold_2d_omnifold_unbinned.py`~~ — done (flag-aware logging
   + WARN if c deviates from 1).
4. Re-run event loop on playlist 1A as a closure check (cheapest), then
   on full MEHFC if 1A behaves. Use the existing
   `sbatch_evloop_array.sh` (which already points at the production
   binary). The new run should print
   `Captured N unique event IDs from mc_signal_reco.` and
   `Appended K truth-only miss entries to mc_signal_reco.` in the log.
5. Re-run unfold (`unfold_2d_omnifold_unbinned.py`); verify
   `c_global ≈ 1.0` (no WARN), and that σ_total and per-bin agreement
   match the post-Phase-16 numbers (3.055e-38 cm²/nucleon, χ²/ndf = 3.289).
   If they match, the c correction and the native-miss approach are
   equivalent. Future cleanup can then drop the c-correction code path
   entirely.

### Outreach status

Outreach to Callum / MINERvA collaboration remains unnecessary
(unchanged from Phase 16 closeout). The Phase-17 work is an internal
pipeline cleanup, not a new physics question.

### Email exchange with Ben (2026-05-14)

For the record, the agreed plan came out of an email thread:

- JB sent the post-Phase-16 slide deck explaining the c correction.
- BN: "OmniFold should be able to handle these events — those that
  have truth but not reco. Are you doing this c correction binned?"
- JB confirmed the c is per-bin and clarified that the issue is the
  8.4M events with no reco-tree entry are absent from the OmniFold
  input entirely, then proposed adding them as miss entries during
  the event loop — which is the Phase 17 plan above.

## Phase 18 — Truth-tree-authoritative reco gate (2026-05-14)

### Motivation

The Phase 17 1A re-run gave `c_global = 1.0170` after the Python
truth-pass-gate tightening (was 1.018 before). The 1.7% residual was
inconsistent with the by-construction `c=1` Phase 17 was supposed to
deliver.

Initial hypothesis: the C++ fill condition
`if(inPhaseSpace || passesReco)` was admitting reco-pass-truth-PS-fail
"fakes" to `mc_signal_reco`. A patch tightened the condition to
`if(inPhaseSpace)` and routed signal-truth-but-PS-fail events to
`mc_background`. Result: byte-for-byte identical to the Phase-17 ROOT —
`mc_signal_reco = 2,730,616`, `mc_background = 4,277`, `nTruthOnlyMisses
= 681,612`. The "fakes" don't exist in this dataset: MINERvA's reco
selection (`isMCSelected`) enforces vertex / angle / p‖ cuts at least as
strict as the truth `CCInclusive2DPhaseSpace`, so the set
`passesReco && !inPhaseSpace` is empty.

### Real cause

Per-AnaTuple-file diagnostic (run 110000) showed every reco-tree entry's
`(mc_run, mc_subrun, mc_nthEvtInFile)` IS present in the Truth tree of
the same file. But:

- mc_signal_reco's reco-loop captured **2,049,004 unique IDs**, of which
  only **2,000,655** appear in mc_truth_denom. **48,349 captured IDs
  (≈1.8% of mc_signal_reco) have no matching truth-denom entry.**
- The 48,349 ARE in the truth tree; they fail
  `michelcuts.isEfficiencyDenom(*truthCV, ...)` but pass
  `michelcuts.isEfficiencyDenom(*recoCV, ...)` for the same physics
  event.
- The cuts depend on `mc_primFSLepton` (`GetThetalepTrue`, `GetPlepTrue`)
  and `mc_vtx` (`GetTrueVertex`). For events with secondary muons (e.g.
  CC-numu with a pion-decay daughter muon) the matched track can pick up
  the daughter and the cuts evaluate differently between reco-tree and
  truth-tree AnaTuple branches. Magnitude ~1.8% is consistent with the
  secondary muon rate in CC-numu inclusive at MINERvA-ME energies.

### Fix — option 2 (truth-tree-authoritative gate)

In `runEventLoopOmniFold.cpp`:

- New `TruthDenomEntry` struct (cached per-event `{MC, MC_pz, w_truth,
  key}`) so miss-append can iterate the cache instead of re-walking the
  truth tree.
- `LoopAndFillUnbinnedMCTruthDenom` no longer does inline miss-append; it
  now optionally populates `outTruthDenomIDs` (set) and
  `outTruthDenomCache` (vector). Return type changed from `long` to
  `void`.
- New `AppendTruthOnlyMisses(sigOut, truthDenomCache, recoIDs)` writes
  the miss entries from the cache.
- `LoopAndFillUnbinnedMCSelectedSignalReco` gains a
  `const std::unordered_set<uint64_t>* truthDenomIDs = nullptr` parameter
  and gates `out->Fill()` on `inPhaseSpace && truthAgrees`.
- `main()` orchestration reordered: truth-denom → reco → miss-append →
  background → data (was: reco → truth-denom → background → data).

The fakes-routing patch from earlier in the day is kept — vacuously
correct, no cost.

### Validation on 1A (2026-05-14)

Event-loop rerun produced `runEventLoopOmniFold_1A_phase18.root` with
`mc_signal_reco = mc_truth_denom = 2,682,267` entries by construction.
5-iter unfold gave:

- `[CHECK] global completeness c = 1.0000` (vs 1.0170 previously)
- `hOFInputTruth2D integral = hOFTruthDenom2D integral = 486328`
- σ_total (p_T) = σ_total (p_||) = 3.052 × 10⁻³⁸ cm²/nucleon
- `hBkgReco2D` integral 1,788 → 9,782 (+8 k weighted; the 48 k "Set E"
  reco-fakes are now correctly subtracted from data instead of polluting
  the response)
- `pass_reco` 1,774,756 → 1,729,050 (cleaner response pool)

σ_total agrees with the Phase-16 production (3.055 × 10⁻³⁸ cm²/n) to
0.1%, so the c-correction was masking a sub-percent shape bias whose
integral effect happened to be small.

### Build-system trap (resolved 2026-05-14)

`runEventLoopOmniFold.cpp` previously existed at two paths on disk and
the first attempted rebuild silently used stale code (wasted a 1A run).
Fixed by reconfiguring `build_MINERvA101/` with `CMAKE_HOME_DIRECTORY`
and `CMAKE_INSTALL_PREFIX` rooted in `MINERvA-OmniFold/`. `make install`
now lands the binary directly in `MINERvA-OmniFold/MINERvA101/opt/bin/`
where SLURM scripts read it — no more manual `cp`.
`build_GENIEXSecExtract/` and `build_MAT-MINERvA/` were reconfigured the
same way. Pre-migration workspace at `/pscratch/sd/j/josephrb/MINERvA101/`
is now unreferenced and safe to delete.

## Phase 18.1 — Truth-side dedupe (2026-05-15)

### Symptom

First Phase-18 MEHFC chain (52983620 evloop array, 52983621 hadd, 52983622
unfold) ran successfully for evloop+hadd; the unfold timed out at 6 h
during iteration 1. Pre-resubmit audit of the merged ROOT revealed
`mc_signal_reco = 32,849,138` vs `mc_truth_denom = 32,849,236` — a
**98-entry deficit** of Phase-18's by-construction identity.

### Diagnosis

Per-playlist breakdown of the merged ROOT showed the entire deficit lives
in 1E (11/12 playlists hit exact equality). Direct key-collision scan of
1E's source AnaTuples found:

| File | Truth entries | Within-file dup keys |
|---|---|---|
| `MasterAnaDev_mc_AnaTuple_run00111353_Playlist.root` | 549,196 | **1,102** |
| Each of the other 50 1E files | clean | **0** |

Multiplicity histogram: 28,114,936 keys appear once, **1,102 keys appear
exactly twice, no higher multiplicities, zero cross-file collisions.**
`(mc_run, mc_subrun, mc_nthEvtInFile)` is globally unique except for
those 1,102 doubled entries in one file — almost certainly an upstream
re-tupling/concatenation artifact (output appended instead of
overwritten). Of the 1,102 raw duplicates, ~98 pairs survive
`isEfficiencyDenom` *and* have a reco match — exactly the observed
deficit.

### Implication beyond OmniFold

`mc_truth_denom` is the efficiency denominator. The 1,102 duplicates have
been silently inflating the 1E efficiency denominator in *every* prior
analysis using this AnaTuple. Effect: ~3×10⁻⁴ in 1E, ~3×10⁻⁵ in MEHFC —
below MINERvA systematics but a real bias. **AnaTuple-producer flag
candidate.**

### Fix

`LoopAndFillUnbinnedMCTruthDenom` in `runEventLoopOmniFold.cpp` now
maintains a local `seenKeys` set and skips Fill + cache-push + ID-insert
when the `(mc_run, mc_subrun, mc_nthEvtInFile)` key is already seen. WARN
log emits the skip count.

### Re-run

Chain submitted 2026-05-15 (53012899_4 evloop 1E, 53012900 hadd, 53012901
unfold). Unfold scancelled at 9h31m (had reached only iter 2) and
resubmitted as 53034070 with 24h wallclock. Completed 5 iters; σ_total =
3.073e-38, χ²/ndf = 3.549 (185 strict interior, full cov). WARN logs
confirmed 1,102 duplicate truth keys skipped.

## Phase 18.2 — Reco-side mirror dedupe (2026-05-18)

### Symptom

Verification of the Phase-18.1 MEHFC ROOT: `mc_signal_reco = 32,849,110`
vs `mc_truth_denom = 32,849,103` — a **7-entry surplus** the other way.
`c_global` printed as 1.0000 (rounded) but the underlying ratio was
1.00000025 (5 ppm above unity). The 192 of 205 bins ≠ 1.0 confirmed it
was not a print-format artifact.

### Diagnosis

The Phase-18.1 fix deduped the truth-denom loop but did not mirror the
fix on the reco loop. The same `run00111353_Playlist.root` double-fill
that produced 1,102 truth duplicates also produced reco-tree duplicates.
After `isEfficiencyDenom` + reco match, 7 of those reco duplicates survive
to `mc_signal_reco.Fill()` twice — hence the +7 surplus.

### Fix

`LoopAndFillUnbinnedMCSelectedSignalReco` in `runEventLoopOmniFold.cpp`
gets the same `seenRecoKeys` dedupe pattern as the truth-denom loop:

```cpp
// Phase 18.2: mirror the truth-denom dedupe (Phase 18.1) on the reco side.
std::unordered_set<uint64_t> seenRecoKeys;
long nDupRecoSkipped = 0;
// ... key compute moved outside the truthAgrees gate ...
if(inPhaseSpace && truthAgrees) {
  if(!seenRecoKeys.insert(key).second) { ++nDupRecoSkipped; continue; }
  out->Fill();
  if(outRecoIDs) outRecoIDs->insert(key);
}
// after loop:
if(nDupRecoSkipped > 0)
  std::cout << "  WARN: skipped " << nDupRecoSkipped
            << " duplicate-key reco entries (upstream AnaTuple double-fill).\n";
```

### Re-run chain

Submitted 2026-05-17 with afterok dependency chain (so the user could
release the interactive shell):

- `53095454` build_phase18p2 — 23s, Phase-18.2 binary installed to
  `opt/bin/runEventLoopOmniFold`.
- `53095457_4` evloop_phase18 (1E only) — 2h07m. WARN logs confirmed
  exactly `skipped 133 duplicate-key truth entries` and `skipped 7
  duplicate-key reco entries`.
- `53095459` hadd_MEHFC_phase18 — 24s. Produced 2.0 GB
  `runEventLoopOmniFold_MEHFC_phase18.root`.

Post-rebuild verification:
- `mc_signal_reco = mc_truth_denom = 32,849,103` exactly.
- `c_global = 1.000000` to sub-ppm precision.

(Note: only 1E needed re-evloop — the truth/reco duplicates are entirely
in `run00111353_Playlist.root` which is in playlist 1E. Other 11
playlists' Phase-18.0/18.1 ROOTs are bit-equivalent to a Phase-18.2 re-run
because their input has no duplicates.)

