# 3D OmniFold (Eavail) run log

Append-only chronology of Workstream C — the available-energy 3D extension of
the 2D unbinned OmniFold measurement. Newest entries at the bottom of each
dated section. For headline numbers and current state see
`3D_OMNIFOLD_STATUS.md`; for orientation + how-to-run see `README.md`; for
durable workflow invariants (shared with 2D) see
`../2d-unfolding/2D_OMNIFOLD_REFERENCE.md` (§ "3D OmniFold extension").

---

## 2026-05-29 — C1: Eavail branches in the event loop

Added the third axis to `runEventLoopOmniFold.cpp`. Truth
`MC_eavail = GetEAvailableTrue()/1000` (GeV; arXiv:2312.16631 Eq. 4 — Σ proton
KE + Σ π± KE + Σ π⁰/γ total E, excludes n/μ); reco `sim_eavail` /
`sim_background_eavail` / `measured_eavail` = `NewEavail()/1000` (tracker+ECAL
×1.17). Both accessors added **standalone** to `event/CVUniverse.h` rather than
via `#include` of the MAT calculators, because `LowRecoilPionFunctions.h`
redefines `GetVertex()` (conflict at `CVUniverse.h:116`). Branch availability
verified in the MasterAnaDev tuples (`blob_recoil_E_*`, `muon_fuzz_*`,
`mc_FSPart*` present in BOTH MC and data; the spline `recoilE_SplineCorrected`
is absent — confirming `NewEavail` as the correct reco estimator). Build +
single-file smoke passed (truth med 0.95 GeV, reco 0.66 GeV, no NaN, misses
−9999). Committed `8ca52cc`.

## 2026-05-30 — C1: 12-playlist re-run + hadd

`sbatch_evloop_array_3d.sh` (SLURM 53601666, array 1-12, shared QOS,
non-destructive → `runEventLoopOmniFold_3D_{1A..1P}.root`). All 12 COMPLETED,
no log errors; `hadd` → `runEventLoopOmniFold_MEFHC_3D.root` (2.8 GB).
Full-stats Eavail sanity: truth mean 1.93 GeV (0→92 GeV DIS tail), matched reco
1.15 GeV, data 1.54 GeV; `sim_eavail`=−9999 for the 12.35M/32.85M truth-signal
events failing reco (8.99M of those are the Phase-17 truth-only-miss appends).

## 2026-05-30 — C2: 3D driver

`unfold_3d_omnifold_unbinned.py` — eavail-aware 3D TTree readers, 3-column
feature `column_stack`, and `xsec_3d.py` for extraction / Eavail-marginal / 1D
projections. Reuses the 2D driver's flux/POT/nucleon/phase-space-gate helpers
via `import unfold_2d_omnifold_unbinned`; **CV-only** (the universe /
alt-model / bootstrap machinery is the deferred 3D-UQ campaign). Default Eavail
edges `[0,0.1,0.2,0.4,0.8,1.5,3.0,100]` GeV — the 100-GeV **catch bin is
required** so the Eavail-marginal captures the full CC-inclusive recoil tail and
equals the 2D result (Σ_k xsec·ΔE_k = 2D only if every truth event lands in a
bin). Marginal written as TH2D `hXSec2D` so `compare_to_paper_fullcov.py --ours`
is drop-in. Smoke (2 iter): c=1.0000, 3D integral ≡ marginal integral
(2.905e-38). Committed `685ffce`.

## 2026-05-30 — C3: full-stats unfold + Eavail-marginal anchor

Ran `unfold_3d_omnifold_unbinned.py` on the full MEFHC omnifile (5 iter lgbm,
seed 1, `--use-weights`) — ~14 min on the interactive node (256 CPU), c=1.0000.
Output `xsec_3d_MEFHC_5iter_lgbm.root`.

- **Eavail spectrum physical**: dσ/dE_avail falls monotonically 2.19e-38
  (low-recoil [0,0.1] peak) → 6.8e-41 (catch bin).
- **Normalization anchor PASS**: marginal total σ +0.95 % vs paper; 3D integral
  ≡ marginal integral; per-bin marginal/2D ratio median 1.0016.
- **Shape anchor ELEVATED**: marginal vs paper full-cov χ²/ndf = **4.98**
  (stat-only 12.48) vs frozen 2D 3.66 (default) / 2.65 (lgbm-CV); ~4.4 % per-bin
  scatter. Genuine reweighting effect, not a normalization/pipeline bug.

Cleanup: the bare `compare_to_paper_fullcov.py` call clobbered the tracked 2D
pull plot via its default out-prefix; restored from git, regenerated the 3D one
as `eavail_marginal_vs_paper_pull_full.png`. Committed `2cb4cde`, `69f0958`.

## 2026-05-30 — C3: reweight closure (PASS)

Added `--closure` / `--closure-reweight-eavail` to the 3D driver (commit
`27564a8`). CV self-closure is exact (degenerate — pseudo-data == MC reco).
Full-stats **Eavail-reweight closure**: injected a +30 % Gaussian bump in
*truth* Eavail (center 0.3 GeV, σ 0.15) into the pseudo-data; OmniFold recovers
it (step2 mean weight 1.048 ≈ injected 1.0485). Residuals (unfold/truth-ref):
**Eavail-marginal median 0.9999, std 0.0006, max\|dev\| 0.0021**; 3D-bin std
0.032; Eavail-1D 0.963–1.025. Output `closure_3d_MEFHC_eavail_bump.root`.

**Conclusion.** The marginal closes to 0.06 % — ~70× tighter than the 4.4 %
data-vs-2D scatter — so that scatter (and the χ²=4.98) is real data↔MC structure
the Eavail axis exposes, NOT a method bias. Workstream C framework validated
end-to-end. Committed `c73ce30`. Deferred: full 3D systematic-UQ campaign.

## 2026-05-31 — GENIE truth-generation scaffold + first model overlay (genie/)

Built `genie/` to generate truth-level GENIE events and compare to the unfolded
3D result (no detector sim needed — comparison is at truth level). Scaffold
committed `87cd16e`; see `genie/README.md`. Env solved without a container:
GENIE 2.12.10c from CVMFS via UPS `-H` SL7-flavor override + a 4-lib compat shim
(glibc forward-compat on SLES15). Two bring-up bugs fixed: the MINERvA flux is a
`PlotUtils::MnvH1D` GENIE reads as integral-zero → convert to plain TH1D
(`make_flux_for_genie.py`); reduced the 850 MB spline file to the C12+H1 subset
(`reduce_splines.sh`, 4 MB).

First result (2M base-CV events, 8 parallel gevgen × 250k ~9 min, hadd'd):
1.48M CC, 938k in phase space; flux-averaged ⟨σCC⟩/nucleon = 3.98e-38 cm²;
total-in-PS 2.52e-38 vs unfolded 3.08e-38. **GENIE 2.12 CV tracks the data
shape on (pT, p‖, Eavail) but runs ~10-18 % low in normalisation**
(`genie_vs_unfolded.png`) — expected base-CV behaviour before the MINERvA
Tune v1 reweights.

## 2026-05-31 — GENIE Stage B: MINERvA Tune v1 3D prediction

Done the robust way rather than reimplementing the tune reweights on gevgen
events: the analysis MC already carries the full Tune v1. `mc_truth_denom`'s
`w_truth` = flux CV × RPA × low-recoil 2p2h × non-res-π suppression
(mean 0.83 ≠ 1). `model_tune_xsec3d.py` bins the truth weighted by `w_truth` and
normalises with the unfold's flux/POT/nucleon machinery (completeness = 1, since
a model prediction needs no efficiency correction) → `model_tunev1_xsec3d.root`.
**Validation gate PASSED**: reproduces the shipped ancillary
`model_ptpl…Tune_v1.txt` to 0.01 % in normalisation (σ_tot/data 0.9125 vs
shipped 0.9124); χ²(ours vs shipped)/ndf = 1.57 (MC-stat-limited, not a model
difference); data-vs-tune χ²/ndf 33.0 for both. Totals-in-PS: base CV 2.52e-38,
Tune v1 2.71e-38, unfolded 3.08e-38 (tune raises GENIE ~7 %, still ~12 % low).

Three-way overlay `genie_tunes_vs_unfolded.png` (base CV + Tune v1 + unfolded):
on (pT, p‖) the tune barely moves GENIE; on **Eavail** the tune acts at low
recoil (RPA suppresses the QE peak, Tune v1 below base CV in the lowest bin) yet
still underpredicts the data there — the model-discrimination the 3D axis
enables.

## 2026-05-31 — Independent generator: NuWro 21.09

Added NuWro (first non-GENIE generator). From CVMFS via the same UPS `-H` SL7
trick + compat shim (+ libxxhash from conda). Bring-up gotchas, all solved:
(i) **e20:debug** build — the prof build segfaults inside the flux-driven
test-event phase on SLES15 forward-compat; (ii) `nuwro_home/{bin,data}` symlink
dir (NuWro's `<bin>/../data` lookup breaks under the UPS layout); (iii) flux
hist x-axis in GeV, range-restricted [0.5,50] GeV to avoid an edge crash.
`nuwro_to_flat.C` reads the event-class tree (in NuWro's ROOT 6.22) → flat obs
tree; `nuwro_to_xsec3d.py` (conda) normalises by the per-event weight
(= flux-avg σCC/nucleon). Target C12 (~92 % of CH; documented). 2M events
(8×250k parallel, ~5 min): ⟨σCC⟩/nucleon 3.72e-38, total-in-PS 2.34e-38.

Four-way overlay `generators_vs_unfolded.png`: totals-in-PS NuWro 2.34 <
GENIE CV 2.52 < Tune v1 2.71 < unfolded data 3.08 (×1e-38). All three track the
(pT, p‖) shape; on **Eavail** both NuWro and Tune v1 suppress the low-recoil QE
peak below GENIE CV (RPA/nuclear effects), and the data sits above all three at
lowest Eavail. Remaining follow-ups: NEUT/GiBUU (one reader each), full 3D
systematic UQ.

## 2026-05-31 — FSI dial variation (FrInel_pi): putting a number on open question #2

Scaffolded a truth-level GENIE FSI-dial variation pass (motivated by the
uq_statistical_methods open question #2: MAT leaves `FrInel_pi` — the pion
inelastic FSI knob — commented out). FSI reweighting is applied to the *same*
2M CV gevgen events (no regeneration): `grwght1p -s FrInel_pi -t 3 --min-tweak
-1 --max-tweak 1` per shard (`run_fsi_reweight.sh` / `run_parallel_fsi.sh` fan
out over the 8 `work_p*/gntp.*.ghep.root`), then `fsi_variation_xsec3d.py`
applies the per-event weights (weight-tree `eventnum` == gst `iev`) and rebuilds
d³σ at each dial. FSI conserves total CC σ, so each dial is normalised by its
own weighted CC sum → the dial=0 column reproduces CV **exactly** (built-in
closure; verified weights ≡ 1.000 at 0σ, ~45 % of events reweighted at ±1σ).

**Result (full 2M, 938,600 in-PS): FrInel_pi is a sub-percent effect here.**
Total σ-in-PS shifts ±0.03 % at ±1σ; the d σ/dE_avail shifts are ≤ 0.74 %
(largest in the 0.10–0.20 GeV E_avail bin), ~0.1–0.4 % elsewhere. So the data's
~10–18 % low-E_avail excess **cannot** be absorbed by pion-inelastic FSI within
its ±1σ band — excluding `FrInel_pi` (as MAT does) is well justified for this
observable. Files: `genie/genie_fsi_FrInel_pi_xsec3d.root` (+ `_summary.txt`).
Note: available energy is fairly robust to *inelastic* rescattering (which
conserves energy); pion **absorption** (`FrAbs_pi`, removes a π → nucleons) is
the FSI knob most likely to move E_avail and is the natural next dial — the
scaffold takes any GSyst dial name as an argument.

## 2026-06-02 — Full 3D systematic-UQ campaign + generator goodness-of-fit

The deferred systematic campaign (Gaps 1–4 of `3D_SYSTEMATIC_UQ_PLAN.md`),
completed end-to-end.
- **Driver**: `unfold_3d_omnifold_unbinned.py` gains `--universe BAND:IDX` and
  `--flux-universe-file` (lateral detector bands swap pT/pz only, E_avail
  invariant; the Flux band divides by Φ_u).
- **Production**: dump-all event loop → 300 GB-tree Python hadd
  (`sbatch_*_universes_full`, `sbatch_hadd_3d_universes_full.sh`); a 187-universe
  sweep (`uq_3d/universes_full_list.txt`) + 10-seed ML seedscan as sbatch arrays.
- **Rollup**: `uq_3d/analyze_universes_3d.py` + `build_bootstrap_cov_3d.py` →
  combined covariance **C_syst+C_stat+C_ML** at
  `uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root` (√tr 5.724e-39,
  median 10.4 %/bin, **Flux-dominated, same band ordering as 2D**, rank 247/1431).
- **Generator GoF** (`genie/overlay_generators_band.py`,
  `genie/compare_3d_fullcov.py`): project the 1431-bin cov onto each 1D axis
  (J C Jᵀ, machine-precision self-check) → ~6 %/axis band; full-3D
  **truncated-spectral** ours-only χ² (never raw-pinv a rank-247 cov). All three
  generators (GENIE CV, Tune v1, NuWro) excluded at p≈0; diagonal χ²/ndf
  Tune-v1 4.8 ≪ GENIE-CV 34 ≈ NuWro 36 — **Tune-v1 best**.
- **Stat block resolved** (`2D_VALIDATION_FOR_3D.md` open item): data/MC-split
  bootstrap (200+200) closes (data 77 % / MC 23 %); C_data/paper StatOnly = 0.356
  → our data-stat error is genuinely smaller (OmniFold efficiency), not a bug;
  use our own combined cov for the ours-only χ². (Commit `56126b3`.)

## 2026-06-03 — FrAbs_pi FSI dial: also sub-percent

Ran `FrAbs_pi` (pion absorption — the FSI knob most likely to move E_avail)
through the existing reweight machinery. **Peak dσ/dE_avail shift 0.82 %** in the
lowest [0,0.10] GeV bin; total in-PS σ ±0.02 % at ±1σ — the same sub-percent
scale as `FrInel_pi`. **Both pion-FSI dials are thus ruled out** as the cause of
the 7–15 % low-E_avail data excess; it points to the initial-state/nuclear model
(2p2h/MEC, RPA). (`genie/README.md`; commit `dbc57c3`.)

## 2026-06-03 — GiBUU 2019 as the 4th generator (native Perlmutter build)

Added GiBUU 2019 (NOvA CVMFS) to the generator comparison, **running natively on
Perlmutter (no container)**. `setup_gibuu.sh` documents the 5 cleared blockers
(ROOT/libgfortran libs, libstdc++ GLIBCXX ordering, writable buuinput mirror
keeping the `.bz2` sentinels, short symlink for Fortran filename truncation).
- `sbatch_gibuu_mefhc.sh`: 80-task seeded array → `work_gibuu_arr/task*/FinalEvents.dat`.
- `gibuu_to_xsec3d.py`: parse FinalEvents.dat → d³σ/(dpT dp‖ dE_avail); muon ID 902,
  FS hadrons perweight≠0, E_avail matches `GetEAvailableTrue()`. **Normalize by the
  number of files** (perweight already carries 1/numEnsembles), NOT numEnsembles.
- `work_gibuu/gibuu_mefhc_numu.job`: physics config (CC νμ, C12, all channels).

**Results (1.9M events, 914k in-PS)**: flux-avg ⟨σ_CC⟩/nucleon 3.61e-38, in-PS
2.22e-38. Integrated E_avail **−21.9 % vs data (4.1σ, most deficient of the four)**;
diagonal χ²/ndf 32.4 (≈ GENIE-CV/NuWro; Tune-v1 best 4.8); worst on the full-3D
truncated-spectral χ² (23.5 % of residual outside the rank-247 subspace).
`overlay_generators_band.py` / `compare_3d_fullcov.py` rerun with all four
generators. (Commit `971fdb5`; memory `gibuu-native-perlmutter`.)

## 2026-06-03 — 2p2h is the right shape+size for the low-E_avail excess (mode decomposition)

`genie/mode_decomp_eavail.py`: the base GENIE CV has **no MEC** (mec==0 for all
1.48M CC events), so 2p2h would be *added*, not reweighted. Decomposed the
committed CV dσ/dE_avail by interaction mode (exact: per-bin mode count-fraction ×
CV bin value) and overlaid the unfolded data. **The deficit is the 2p2h
signature**: bin [0.10,0.20) +3.9σ, [0.20,0.40) +2.3σ, QE-dominated [0,0.10)
already matches (+0.8), mid bins ±0.4. 57 % of the deficit is at E_avail ≤ 0.4 GeV
(the QE–Δ dip). Closing the integrated −7.2 % needs a 2p2h ~43 % of the QE rate
(62 % locally) — standard empirical/Valencia-MEC size, vs the sub-percent FSI
dials. Bin [1.50,3.00) is a separate +2.2σ high-E_avail DIS-tail excess (not
2p2h). (`genie/mode_decomp_eavail.{py,png}`; commit `dd7e327`.)

## 2026-06-03 — Confirm 2p2h fills ~half the low-E_avail dip (regenerate GENIE with Valencia MEC)

Regenerated the GENIE CV with empirical 2p2h enabled (`--event-generator-list
Default+CCMEC` via a new `GEVGEN_LIST` hook in `run_gevgen.sh`;
`sbatch_gevgen_mec.sh` = 2M events). **Normalization subtlety**
(`genie_mec_to_xsec3d.py`): the Nieves-Simo-Vacas MEC channel is in the spline but
ABSENT from the gspl2root tot_cc graph (mec_cc==0), so normalize by the non-MEC CC
count — anchoring QE+RES+DIS+COH to the known tot_cc and letting MEC add on top by
1/(1−f_mec), f_mec=2.87 %. **Result** (`compare_mec_eavail.py`): MEC lands in the
QE–Δ dip — [0,0.10) +0.8→−0.04σ, [0.10,0.20) +3.9→+2.85, [0.20,0.40) +2.3→+1.0.
MEC fills **46 % of the data–CV gap in the dip** (E_avail ≤ 0.4) and 27 % of the
integrated deficit (−7.2 % → −5.2 %). Full-3D truncated χ²/ndf 1512 → 1145 (−24 %;
`compare_3d_fullcov_mec.png`) — real but still ≫ Tune-v1 (131), which layers
MINERvA's empirical low-recoil 2p2h enhancement + RPA on stock Valencia MEC. The
high-E_avail [1.5,3.0) excess is untouched (a DIS-tail issue). **Conclusion: the
low-recoil excess is the 2p2h signature; stock Valencia 2p2h is real but
under-strength for MINERvA low-recoil**, unlike the sub-percent pion-FSI dials.
(Commit `790aee8`.)

## 2026-06-03 — Disk cleanup: reclaimed ~547 GiB of re-derivable intermediates

Repo scratch trimmed 860 GB → ~313 GB. **Deleted** (all gitignored and
re-derivable; the merged MEFHC omnifiles and every distilled `*_xsec3d.root` /
covariance product were kept):
- 3D: the aborted-hadd `…_MEFHC_3D_universes_full.partial_20260601_*.root`
  (94 GiB) + the empty `…_full_1.root` stub; the 12 per-playlist
  `…_3D_1{A..P}_universes_full.root` (120 GiB); `genie/work_gibuu_arr/` (142 GiB)
  plus `genie/work_p*/ work_mecseed*/ work_nuwro_*/ work_gibuu/ work_mec_smoke/`
  scratch and `genie/genie_mefhc_cv.gst.root` (raw GENIE event tree); `smoke/*.root`.
- 2D (full detail in `../2d-unfolding/2D_OMNIFOLD_RUN_LOG.md`): the 64 GiB
  non-"full" `…_MEFHC_universes.root`, the 12 per-playlist
  `…_1{A..P}_universes_full.root` (119 GiB), `universe_smoke/*.root`, stray
  root-level job logs.

**Regen path** if ever needed: per-playlist omnifiles via the 12-playlist
event-loop array → merge with `uq/hadd_universes_full.py` (SetMaxTreeSize merger,
**not** bare hadd — memory `hadd-100gb-tree-limit`); GiBUU via `setup_gibuu.sh`;
GENIE work dirs via the `gevgen` scripts in `genie/`. The combined covariance
`uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root` and all kept merged
inputs are unaffected.
