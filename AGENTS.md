# MINERvA-OmniFold Agent Context

## Project Scope
MINERvA-101 cross-section and OmniFold studies for muon kinematics:
- 1D **p_T** unbinned OmniFold (revalidated 2026-05-02 against playlist 1A;
  patched to the 2D contract; OmniFold-vs-IBU comparison plot regenerated.
  Legacy `Documents/` 2026-03-26 ROOTs remain superseded — diagnostic only)
- 1D binned OmniFold (debug campaign complete — closure verified, found
  equivalent to D'Agostini IBU)
- 2D **(p_T, p_||)** double-differential — current active campaign,
  reproducing arXiv:2106.16210

## Current Campaign — 2D OmniFold (active)

**Goal**: Reproduce arXiv:2106.16210 (Ruterbories et al., Phys. Rev. D 106,
032001) — MINERvA ME FHC d²σ/(dp_T dp_||) CC inclusive — with 2D unbinned
OmniFold in place of D'Agostini IBU. Validated on playlist 1A; full
12-playlist MEHFC production complete.

**Authoritative docs (read these before touching the 2D pipeline):**
- `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md` — dashboard, current numbers, next actions.
- `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` — stable invariants and gotchas.
- `2d-unfolding/2D_OMNIFOLD_RUN_LOG.md` — append-only chronology.
- `2d-unfolding/PLOT_GUIDE.md` — PNG reading guide.
- Plan: `~/.claude/plans/purrfect-whistling-pelican.md` (historical; phases 1–4 done).

**Headline numbers (patched-MINOS MEHFC, 5-iter production):**
- Total xsec (paper bins, projection sum) = 2.285e-38 cm²/nucleon
  (paper: 2.74e-38; ours runs ~16.6 % low)
- Strict-interior χ²/ndf vs paper (185 bins, full cov) = 17.443
- Median bin ratio (ours/paper, strict interior) = 0.8968
- Residual: smooth low-p_|| gradient (~0.6 at p_||=1.5–2 GeV/c → ~1.0
  above p_||=20 GeV/c). Likely cause: MINOS geometric acceptance /
  range-out efficiency, NOT match selection.

**Most recent physics change (2026-04-25):** patched `IsMinosMatchMuon()` stub in
`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:107`. Fixed a real
bug (background dropped 48,750 → 1,256, matching paper's ~0.2 %; pass_reco
−9.6 %), but the low-p_|| gradient SHAPE is unchanged. See
`memory/project_minos_match_stub_fix.md`.

**Most recent full run (2026-04-26):** full MEHFC patched-MINOS event loop,
hadd, 5-iter OmniFold, and paper comparison completed. The run is
self-contained in the migrated tree at
`2d-unfolding/runEventLoopOmniFold_MEHFC.root` and
`2d-unfolding/2d_crossSection_omnifold_MEHFC_5iter.root`; the residual
low-p_|| deficit remains.

## Open work on the 2D campaign
- Investigate MINOS geometric acceptance / range-out efficiency
  modeling. The paper applies a dedicated correction in low p_||;
  the MINERvA-101 tutorial path does not. Audit
  `MinosMuonEfficiencyCorrection` vs the paper's published map.
- Re-run full MEHFC once the gradient is understood.

## 2D workflow

### Environment
From the repo root (`MINERvA-OmniFold/`):
```bash
source setup_salloc_env.sh
```
That self-locating script loads the `root_6_28` conda env, sources
`unbinned_unfolding/build/setup.sh` (built in-tree), exports
`MINERVA_PREFIX=$REPO/MINERvA101/opt`, and sources
`MINERvA101/opt/bin/setup.sh`.

Canonical runtime binary: `MINERvA101/opt/bin/runEventLoopOmniFold` (do
**not** call build-tree copies — they have silently shadowed the installed
patched binary in the past).

### Per-playlist event loop, then hadd
`runEventLoopOmniFold.cpp` picks ONE global playlist flux/calibration
from the first event's run number. **Never** feed it a combined MEHFC
manifest — it silently applies the first playlist's flux to all events
and corrupts 11/12 of the dataset. Run per-playlist, then `hadd`.

### 2D pipeline (playlist 1A or full MEHFC)
1. Per-playlist event loops via `2d-unfolding/sbatch_evloop_array.sh`
   (writes `runEventLoopOmniFold_1{A..P}.root`).
2. `hadd 2d-unfolding/runEventLoopOmniFold_MEHFC.root <per-playlist>`.
3. `2d-unfolding/sbatch_unfold_2d.sh` (1A) or
   `sbatch_unfold_2d_fullstats.sh` (MEHFC) → runs
   `unfold_2d_omnifold_unbinned.py --use-weights`.
4. Plotting: `plot_2d_cross_section.py`,
   `plot_2d_paper_comparison.py`,
   `compare_to_paper_interior.py`,
   `compare_to_paper_fullcov.py`.

### Flux
`runEventLoopOmniFold.cpp` does NOT write `pTmu_reweightedflux_integrated`.
Use `sbatch_runEventLoop_baseline_flux_array.sh` to regenerate per-playlist
baseline flux, then `combine_flux_MEHFC.py` to build the POT-weighted MEHFC
flux at `2d-unfolding/baseline_flux/runEventLoopMC_MEHFC.root`. The 2D
Python script embeds the flux histogram into its output for self-contained
auditing.

## 2D Python contract (must hold)
1. **Mask measured data to phase space** (0 ≤ p_T ≤ 4.5,
   1.5 ≤ p_|| ≤ 60) before step-1 training.
2. **Subtract background** to build a non-negative reco target;
   pass per-event `measured_weights` into `ohf.omnifold(...)`.
3. **Include signal fakes in the reco-side subtraction.**
   Fakes (reco in phase space, truth out) appear in `mc_signal_reco`
   but are filtered by `omnifold.py`'s `MC_pass_truth_mask`. Add their
   POT-scaled reco weights into `hBkgReco2D` so both measured and MC
   reco sides are fake-free.
4. **`hUnfold2D` is a truth-space event yield.** Fill with
   `step2_weights * truth_w_in`, not raw `step2_weights`.
5. **Do NOT divide `hUnfold2D` by `hEff2D`.** OmniFold returns an
   efficiency-corrected truth spectrum on the truth-selected sample.
   `hEff2D` is diagnostic only.
6. **Closure mode** restricts pseudo-data to `pass_reco & pass_truth`
   and uses `sig["w_reco"]` as `measured_weights` when `--use-weights`.
7. **Full-stats sbatch must pass `--use-weights`** to match the 1A
   validation footing.

## Paper / ancillary comparison
- No HepData entry. Authoritative target: `2d-unfolding/minerva_paper_anc/`.
- Use `bin_mapping.txt`, **not** the axis labels on the ancillary TH2D
  (those are cosmetic rounding 0.075/0.325/0.475).
- `pzb=1` is first p_|| bin (1.5 < p_|| < 2.0 GeV/c) — fragile MINOS
  range-out regime.
- Paper reports 205 / 224 bins (19 diagonal bins with pt/p|| > tan 20°
  unreported); strict-interior comparison uses 185 bins.

## NERSC SLURM gotchas
- Do NOT combine `set -u` with `conda activate root_6_28`. The conda
  `deactivate-root.sh` hook references `CONDA_BACKUP_ROOTSYS` and aborts
  under nounset in a fresh batch shell.
- Export `PYTHONUNBUFFERED=1` so Python stdout flushes to `.out` live.
- Do NOT use `srun` inside 2D OmniFold sbatch scripts. Inherited
  `SRUN_CPUS_PER_TASK` from a live interactive allocation breaks nested
  srun. Bare `python3 ...` is the safe default.
- Templates: `sbatch_validate_1A_corrected.sh`, `sbatch_unfold_2d.sh`.

## Runtime notes (2D)
| Task | Resource | Wall time |
|---|---|---|
| C++ event loop, one playlist | shared QOS, 1 task | ~3.5 h |
| Event loop, all 12 playlists | 11-task array | ~3.7 h parallel |
| 2D OmniFold, 5-iter, 1A stats | shared QOS, 2 CPU, 8 GB | ~1.4 h |
| 2D OmniFold, 5-iter, full stats | shared QOS, 4 CPU, 32 GB | ~20 h |

Iteration scan (1A): 5-iter is 0.08 % off the 10-iter total xsec —
production uses 5 iterations.

## Patched code

### `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:107` (2026-04-25)
```cpp
virtual bool IsMinosMatchMuon() const {
  const std::string ok_branch = GetAnaToolName() + "_minos_trk_is_ok";
  return GetInt("isMinosMatchTrack") == 1 && GetInt(ok_branch.c_str()) == 1;
}
```
Replaces the educational stub `has_interaction_vertex==1` (true for
essentially every event in the pre-selected AnaTuple). Pre-patch
event-loop outputs include the looser selection and must be regenerated
before they can be compared to paper numbers.

### `runEventLoopOmniFold.cpp`
- Writes 4 TTrees with both `p_T` and `p_||` branches per event.
- Does **not** write `pTmu_fiducial_nucleons` (was hadd-corrupted: hadd
  sums `TParameter<double>` across inputs, inflating the
  detector-geometry constant 12×). Python uses the fixed tracker
  constant 3.2353e30.

### Active 2D files
- C++: `runEventLoopOmniFold.cpp`, `cuts/MaxPtMu.h`,
  `util/Binning.h` (paper's 14 p_T × 16 p_|| edges).
- Python: `2d-unfolding/unfold_2d_omnifold_unbinned.py`,
  `plot_2d_cross_section.py`, `plot_2d_paper_comparison.py`,
  `plot_closure_2d.py`, `plot_iter_convergence.py`,
  `compare_to_paper_{fullcov,interior}.py`,
  `combine_flux_MEHFC.py`.
- SLURM: `sbatch_evloop_array.sh`, `sbatch_unfold_2d.sh`,
  `sbatch_unfold_2d_fullstats.sh`, `sbatch_iter_scan_2d.sh`,
  `sbatch_validate_1A_corrected.sh`,
  `sbatch_runEventLoop_baseline_flux_array.sh`,
  `download_playlist.sh` + `sbatch_download_playlist.sh`.
- Outputs: `runEventLoopOmniFold_MEHFC.root`,
  `runEventLoopOmniFold_1{A..P}.root`,
  `2d_crossSection_omnifold_MEHFC_5iter.root` (production),
  `2d_crossSection_omnifold_1A_corrected_*iter.root`,
  `2d_crossSection_omnifold_1A_minos_fix_5iter.root`.
- Manifests: `2d-unfolding/playlist_manifests/1{A..P}_{MC,Data}.txt`.

### TTree schema (after 2D extension)
All TTrees carry both p_T and p_|| branches:
- `mc_truth_denom`: `MC` (p_T), `MC_pz` (p_||), `w_truth`
- `mc_signal_reco`: `sim`, `sim_pz`, `sim_pass`, `w_reco`, `MC`, `MC_pz`, `w_truth`
- `mc_background`: `sim_background`, `sim_background_pz`, `sim_background_pass`, `w_bkg`
- `data`: `measured`, `measured_pz`, `measured_pass`

Metadata (`TParameter<double>`): `mcPOTUsed`, `dataPOTUsed`. No
`pTmu_fiducial_nucleons` (intentional — see hadd note above).

### Paper bin edges (authoritative; matches `bin_mapping.txt`)
```python
pt_edges = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]   # 14 bins
pz_edges = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # 16 bins
```
Phase space: θ_μ < 20°, p_T < 4.5 GeV/c, 1.5 < p_|| < 60 GeV/c.

## 1D unbinned baseline (revalidated 2026-05-02)
Status doc:
`2d-unfolding/unbinned_1d_study/UNBINNED_BASELINE_2026-03-26.md`
(SUPERSEDED → REVALIDATED block at the top). Production script
`2d-unfolding/unbinned_1d_study/unfold_ptmu_omnifold_unbinned.py` was
patched 2026-04-30 to honour the 2D Python contract (mask measured to
phase space, subtract bkg + fakes via per-event `measured_weights`, fill
`hUnfold` with `step2 * truth_w`, drop the `RooUnfoldOmnifold` wrapper
in favour of direct `ohf.omnifold(...)`).

Patched-vs-patched 1A rerun (SLURM job 52271486, 2026-05-02) produced
the current valid outputs in
`2d-unfolding/unbinned_1d_study/`:
`runEventLoop{OmniFold,Data,MC}.root`,
`pTmu_crossSection_omnifold.root` (5 iter, `--use-weights`),
`pTmu_crossSection.root` (D'Agostini IBU on the same selection),
`ptmu_gaussian_style_unbinned.pdf`. OmniFold and IBU agree at the QE
peak; OmniFold tracks data more flexibly at the spectrum tails.

Two nuisance bugs surfaced and were fixed in
`sbatch_unfold_1d_unbinned_1A.sh` and the plot script defaults:
(a) `ExtractCrossSection` segfaults in ROOT's `TFile::Close()` exit
handler **after** writing all outputs (the file is recoverable; sbatch
now `|| true`s and gates on `test -s`); (b) the binary writes
`pTmu_crossSection.root`, not the legacy `_clean.root` name.

The legacy `Documents/` 2026-03-26 ROOTs remain pre-MINOS-fix and are
diagnostic-only — do not quote against the paper.

### 1D quick start
```bash
sbatch 2d-unfolding/unbinned_1d_study/sbatch_unfold_1d_unbinned_1A.sh
```
or step-by-step:
```bash
cd 2d-unfolding/unbinned_1d_study
MANIFESTS=../playlist_manifests
runEventLoopOmniFold ${MANIFESTS}/1A_Data.txt ${MANIFESTS}/1A_MC.txt
runEventLoop ${MANIFESTS}/1A_Data.txt ${MANIFESTS}/1A_MC.txt
python3 unfold_ptmu_omnifold_unbinned.py \
  --omnifile runEventLoopOmniFold.root \
  --datafile runEventLoopData.root \
  --datahist pTmu_data --iters 5 --use-weights --verbose \
  --out pTmu_crossSection_omnifold.root
ExtractCrossSection 5 runEventLoopData.root runEventLoopMC.root || true
python3 plot_gaussian_style_ptmu_unbinned.py \
  --omnifold pTmu_crossSection_omnifold.root \
  --ibu pTmu_crossSection.root \
  --outpdf ptmu_gaussian_style_unbinned.pdf
```

## Binned OmniFold (complete, March 2026)
Status file: `2d-unfolding/binned_study/BINNED_PTmu_STUDY_STATUS.md`.
Workspace `2d-unfolding/binned_study/`. Three upstream bugs found in
`rymilton/unbinned_unfolding` 1D binned path
(`Hresponse()` axis mismatch; truth-axis uniformization; garbled
`_res` content), all fixed locally; closure unfolded/truth = 1.0001.
Binned OmniFold proven mathematically equivalent to D'Agostini IBU at
1 iteration; divergence at higher iter is GBT classifier
approximation, not algorithmic. Treat the binned path as a
cross-check, not a final result.

## Important directories
- `MINERvA101/MINERvA-101-Cross-Section/` — C++ event loops + baseline extraction.
- `2d-unfolding/` — production scripts, ROOT outputs, plots, control docs.
- `2d-unfolding/binned_study/` — binned debug workspace (frozen, complete).
- `2d-unfolding/minerva_paper_anc/` — arXiv ancillary release.
- `2d-unfolding/playlist_manifests/` — per-playlist Data/MC file lists for the event loop.
- `2d-unfolding/baseline_flux/` — per-playlist baseline-flux ROOTs (gitignored).
- `2d-unfolding/reference/` — reference papers (Ruterbories PDF).
- `unbinned_unfolding/` — RooUnfold/OmniFold source + in-tree `build/`.
- `unbinned_unfolding/examples/` — reference OmniFold usage.
- Legacy archive (outside repo, leave-in-place):
  `/pscratch/sd/j/josephrb/MINERvA101/Documents/archive_*` and
  `/pscratch/sd/j/josephrb/MINERvA101/archive_pre_migration_2026-04-26/`.

## Output hygiene
- Preserve known-bad but diagnostically useful files under
  `archive_*/debug/` (in the OLD scratch tree) before a rerun overwrites
  a canonical path.
- Never leave invalidated outputs at canonical production paths once a
  corrected rerun is complete.

## Common failure modes
- Branch mismatch between writer and reader.
- Missing/invalid POT metadata in OmniFold ROOT inputs.
- Wrong binary on `$PATH` (build-tree shadowing the installed patched copy).
- Pre-patch event-loop outputs (before 2026-04-25 `IsMinosMatchMuon` fix)
  used in paper comparisons.
- Pre-fix merged OmniFold ROOTs carrying summed `pTmu_fiducial_nucleons`
  metadata — treat as untrustworthy.
- Mixing UF/OF vs in-range conventions when comparing totals.
- Substituting the paper scalar `6.32e-8 /cm²/POT` for the
  flux-normalization term used by this code path (blows up xsec ~13.8×).
- PyROOT unavailable (`ModuleNotFoundError: ROOT`) — env not sourced.

## Notes for future agents
- The 2D campaign is **active**. Read the four `2d-unfolding/2D_OMNIFOLD_*`
  docs before changing the pipeline.
- Memory pointers under `~/.claude/projects/.../memory/MEMORY.md` capture
  rolling context (per-playlist event loop, hadd-fiducial-nucleons,
  edge-bin trust, MINOS-match stub outcome, NERSC `SRUN_CPUS_PER_TASK`).
  Verify referenced files still exist before acting on a memory.
- For physics results, do not use binned OmniFold output without upstream
  package fixes; use the unbinned path.
- Do binned work inside `2d-unfolding/binned_study/`, not at the top level.
- Legacy diagnostic-only files live in the OLD scratch archive (see
  "Important directories" above), not in this repo.
