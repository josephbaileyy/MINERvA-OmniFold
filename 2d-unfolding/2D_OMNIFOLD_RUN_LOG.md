# 2D OmniFold run log

Condensed chronology. For live status see `2D_OMNIFOLD_STUDY_STATUS.md`;
for durable workflow invariants see `2D_OMNIFOLD_REFERENCE.md`.

The original day-by-day log (2400+ lines) was condensed 2026-04-25 into a
phase-by-phase summary that keeps what a new collaborator needs to
reproduce the work without re-encountering the same bugs.

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
