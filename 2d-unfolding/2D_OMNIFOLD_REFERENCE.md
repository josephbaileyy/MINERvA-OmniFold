# 2D OmniFold Study — Reference Notes

Workflow invariants, recurring gotchas, and correctness contracts. Read
before launching jobs or trusting outputs.

---

## Environment setup

```bash
module load python
conda activate root_6_28
source OmniFold/unbinned_unfolding/build/setup.sh
source opt/bin/setup.sh
```

Canonical runtime binary: `opt/bin/runEventLoopOmniFold` (the path exported
by `opt/bin/setup.sh`). Do **not** call build-tree copies — duplicate
build-tree executables have silently shadowed the installed patched binary
in the past.

## SLURM script conventions

- Do **not** combine `set -u` with `conda activate root_6_28`. The conda
  `deactivate-root.sh` hook references `CONDA_BACKUP_ROOTSYS` and aborts
  under nounset in a fresh batch shell.
- Export `PYTHONUNBUFFERED=1` so Python stdout appears in the `.out` file
  during the run.
- **Do not use `srun`** inside 2D OmniFold sbatch scripts. On Perlmutter,
  inherited `SRUN_CPUS_PER_TASK` from a live interactive allocation breaks
  nested srun. Bare `python3 ...` is the safe default.
- See `sbatch_validate_1A_corrected.sh` and `sbatch_unfold_2d.sh` for the
  working template.

## Event-loop workflow

- `runEventLoopOmniFold.cpp` picks **one** global playlist flux/calibration
  from the first event's run number. **Never** feed it a combined MEHFC
  manifest — the tool silently applies the first playlist's flux to all
  events, corrupting 11/12 of the dataset.
  → Run per-playlist, then `hadd` outputs.
- `runEventLoopOmniFold.cpp` intentionally does **not** write
  `pTmu_fiducial_nucleons` because `hadd` sums `TParameter<double>`
  objects, inflating the detector-geometry nucleon constant by 12×. The
  Python extraction uses the fixed tracker-geometry constant 3.2353e30.
- Old pre-fix merged OmniFold ROOT files may carry summed
  `pTmu_fiducial_nucleons` metadata — treat as untrustworthy.
- `runEventLoop.cpp` (baseline histogram path) is where
  `pTmu_reweightedflux_integrated` is written;
  `runEventLoopOmniFold.cpp` does **not** write the flux histogram. Use
  `sbatch_runEventLoop_baseline_flux_array.sh` to regenerate per-playlist
  baseline flux files, then `combine_flux_MEHFC.py` to build the
  POT-weighted MEHFC flux (`baseline_flux/runEventLoopMC_MEHFC.root`).

## 2D Python unfolding contract

`Documents/unfold_2d_omnifold_unbinned.py` is the authoritative 2D unbinned
OmniFold extraction path. Required invariants:

1. **Mask measured data to phase space** (0 ≤ p_T ≤ 4.5, 1.5 ≤ p_|| ≤ 60)
   before step-1 training.
2. **Subtract background** — build non-negative reco-space target from
   `data − bkg` and pass per-event `measured_weights` into
   `ohf.omnifold(...)`.
3. **Include signal fakes in the reco-side subtraction.** Fakes
   (reco in phase space, truth out) appear in `mc_signal_reco` but are
   filtered by `omnifold.py`'s `MC_pass_truth_mask`. Add their POT-scaled
   reco weights into `hBkgReco2D` so both measured and MC reco sides are
   fake-free.
4. **`hUnfold2D` is a truth-space event yield.** Fill it with
   `step2_weights * truth_w_in`, not raw `step2_weights`.
5. **Do not divide `hUnfold2D` by `hEff2D`** when building `hXSec2D`.
   OmniFold returns an efficiency-corrected truth spectrum on the
   truth-selected sample. `hEff2D` is diagnostic only.
6. **Closure mode** must restrict pseudo-data to `pass_reco & pass_truth`
   and use `sig["w_reco"]` as `measured_weights` when `--use-weights` is
   on, matching the `MCreco_weights` footing.
7. **Full-stats sbatch must pass `--use-weights`.** The 1A validation runs
   use it; the production path must match.

## Flux and normalization

- The paper scalar `6.32e-8 /cm²/POT` is **not** the same quantity as the
  flux normalization term used by this code path. Substituting it blows up
  the total xsec by ~13.8×.
- Outputs embed `hFlux_pt` and `fluxSource` so later auditing doesn't
  depend on reopening an external ROOT file.
- Playlist-dependent flux differences are a ~0.2 % effect; not a dominant
  systematic.

## Paper / ancillary comparison

- No HepData entry. Authoritative target: `Documents/minerva_paper_anc/`.
- Use `bin_mapping.txt`, not the axis labels on the ancillary TH2D.
- `pzb=1` = first p_|| bin, 1.5 < p_|| < 2.0 GeV/c (the fragile low-p_||
  MINOS range-out regime).

## `IsMinosMatchMuon` fix (2026-04-25)

The upstream MINERvA-101 tutorial ships

```cpp
virtual bool IsMinosMatchMuon() const {
  return GetInt("has_interaction_vertex") == 1;
}
```

which is an educational stub: it's true for essentially every event in
the pre-selected AnaTuple. `CVUniverse.h:107` has been patched to

```cpp
return GetInt("isMinosMatchTrack") == 1 &&
       GetInt(GetAnaToolName() + "_minos_trk_is_ok") == 1;
```

This requires a MINOS-matched muon track with a passing MINOS fit.
AnaTuple branches verified on `MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root`:
`isMinosMatchTrack` (Int_t) ∈ {−1, 1}; `MasterAnaDev_minos_trk_is_ok`
(Bool_t) ∈ {0, 1}.

Any pre-patch event-loop outputs (`runEventLoopOmniFold_*.root` from before
2026-04-25) include the looser selection and must be regenerated before
they can be compared to paper numbers.

**Note**: this fix removed a real selection bug (background rate dropped
from ~10 % to 0.35 %, matching the paper's ~0.2 %), but the residual
low-p_|| sum-ratio gradient (0.6 at p_||=1.5–2 GeV/c rising to ~1.0
above p_||=20 GeV/c) **persists** after the fix. The gradient is not
caused by MINOS-match selection; it is most likely a MINOS geometric
acceptance / range-out efficiency that the MINERvA-101 tutorial path
does not implement.

## Output hygiene

- Preserve known-bad but diagnostically useful files under an explicit
  `archive_*/debug/` name before a rerun overwrites a canonical path.
- Never leave invalidated outputs at canonical production paths once a
  corrected rerun is complete.

## Documentation split

- `2D_OMNIFOLD_STUDY_STATUS.md` — dashboard, current state, next actions.
- `2D_OMNIFOLD_RUN_LOG.md` — append-only chronology.
- `2D_OMNIFOLD_REFERENCE.md` (this file) — stable invariants and gotchas.
- `PLOT_GUIDE.md` — PNG reading guide.
