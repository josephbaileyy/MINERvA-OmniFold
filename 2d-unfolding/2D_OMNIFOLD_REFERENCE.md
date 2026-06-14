# 2D OmniFold Study — Reference Notes

Workflow invariants, recurring gotchas, and correctness contracts. Read
before launching jobs or trusting outputs.

---

## Environment setup

From the repo root (`MINERvA-OmniFold/`):

```bash
source setup_salloc_env.sh
```

That script is self-locating: it loads the `root_6_28` conda env, sources
`unbinned_unfolding/build/setup.sh` (built in-tree), exports
`MINERVA_PREFIX=$REPO/MINERvA101/opt`, and sources
`MINERvA101/opt/bin/setup.sh`. No HOME paths involved.

## Archiving conventions

Stale logs and one-off artifacts that we keep for reference but don't want
in the active tree go to a dated archive directory at the OLD scratch root,
**outside the new repo**:

```
/pscratch/sd/j/josephrb/MINERvA101/archive_pre_migration_<YYYY-MM-DD>/
```

Rules:

- Active outputs (current `.root`, `.png`, recent job logs) live in
  `2d-unfolding/`.
- Once superseded, move job logs (`*_<jobid>.{out,err}`), throwaway dirs
  (`Doc_tmp/`, scratch scripts), and orphaned PDFs into a new dated
  `archive_pre_migration_*` (or `archive_<purpose>_*`) folder under the OLD
  scratch root.
- In-tree archives are gitignored via `2d-unfolding/archive_*/` (see
  `.gitignore`). Anything still in the OLD scratch tree is outside git
  entirely.
- Heavy intermediates (`runEventLoopOmniFold_*.root`, `evloop_work_*/`)
  are gitignored by the global `*.root` rule and `evloop_work_*/` rule;
  they may be copied into `2d-unfolding/` as needed without being tracked.

Canonical runtime binary: `opt/bin/runEventLoopOmniFold` (the path exported
by `opt/bin/setup.sh`). Do **not** call build-tree copies — duplicate
build-tree executables have silently shadowed the installed patched binary
in the past.

## SLURM script conventions

- **Interactive-first.** Before submitting an sbatch, check
  `squeue -u $USER` for a live `interactive` allocation with time left.
  NERSC's regular and shared queues routinely sit on `Priority` for
  minutes-to-hours; an existing interactive allocation can run the same
  work immediately. Use
  `srun --jobid=<INTERACTIVE_JOBID> --overlap -n 1 --cpus-per-task=<N>
  bash -lc '... ; source $REPO/setup_salloc_env.sh ; <command>'`
  to launch onto it. Work that fits this pattern includes: the C++
  build (`cmake --build && cmake --install`, ~5 min, 8-16 CPU), short
  1A event-loop smokes (~5-15 min, 8-128 CPU), individual unfold runs,
  Python analysis scripts. The interactive's full 128 CPU is available
  inside one node even if your `salloc` requested fewer — `srun
  --cpus-per-task=N` controls the slice. If you already submitted an
  sbatch and *then* realized the interactive is up, `scancel` the
  sbatch — leaving both running leaks compute and risks output-file
  races. Reserve sbatch for genuinely multi-node arrays, multi-hour
  walls, or work that must outlive the shell.
- Do **not** combine `set -u` with `conda activate root_6_28`. The conda
  `deactivate-root.sh` hook references `CONDA_BACKUP_ROOTSYS` and aborts
  under nounset in a fresh batch shell.
- Export `PYTHONUNBUFFERED=1` so Python stdout appears in the `.out` file
  during the run.
- **Do not use `srun`** inside 2D OmniFold sbatch scripts. On Perlmutter,
  inherited `SRUN_CPUS_PER_TASK` from a live interactive allocation breaks
  nested srun. Bare `python3 ...` is the safe default. (The interactive
  case is the inverse: `srun --jobid=<INTERACTIVE> --overlap` is the
  correct primitive when launching new work onto an existing allocation.)
- See `sbatch_validate_1A_corrected.sh` and `sbatch_unfold_2d.sh` for the
  working template.

## Event-loop workflow

- `runEventLoopOmniFold.cpp` picks **one** global playlist flux/calibration
  from the first event's run number. **Never** feed it a combined MEFHC
  manifest — the tool silently applies the first playlist's flux to all
  events, corrupting 11/12 of the dataset.
  → Run per-playlist, then `hadd` outputs.
- `runEventLoopOmniFold.cpp` intentionally does **not** write
  `pTmu_fiducial_nucleons` because `hadd` sums `TParameter<double>`
  objects, inflating the detector-geometry nucleon constant by 12×. The
  Python extraction uses the fixed tracker-geometry constant 3.2353e30.
- Old pre-fix merged OmniFold ROOT files may carry summed
  `pTmu_fiducial_nucleons` metadata — treat as untrustworthy.
- **`hadd` 100 GB TTree trap (large dump-all / `_universes_full` merges):**
  plain `hadd -f` ABORTS when the merged `mc_signal_reco`/`mc_truth_denom`
  trees exceed ROOT's default 100 GB `TTree::fgMaxTreeSize`. ROOT rolls over
  to a continuation file (`..._1.root`) mid-merge and the `TFileMerger`
  fatals: *"Output file ... has been deleted (likely due to a TTree larger
  than 100Gb)"* → SIGABRT (exit 134), leaving a ~94 GB partial **missing the
  `data` + `mc_background` trees** (they merge last). Hit on the 2D dump-all
  (~119 GB) and the 3D dump-all (~120 GB), same 94 GB signature both times.
  `hadd` has no flag to raise the limit, so use the Python `TFileMerger` that
  bumps `TTree::SetMaxTreeSize` to 300 GB instead:
  `uq/hadd_universes_full.py OUT INPUT...` (generic; serves 2D and 3D), wired
  in `sbatch_hadd_*_universes_full.sh` with `mem=64G`. The merge is fast-method
  (basket copy, I/O-bound, ~7 min for 120 GB). **Never** bare-`hadd` a
  `_universes_full` omnifile.
- `runEventLoop.cpp` (baseline histogram path) is where
  `pTmu_reweightedflux_integrated` is written;
  `runEventLoopOmniFold.cpp` does **not** write the flux histogram. Use
  `sbatch_runEventLoop_baseline_flux_array.sh` to regenerate per-playlist
  baseline flux files, then `combine_flux_MEFHC.py` to build the
  POT-weighted MEFHC flux (`baseline_flux/runEventLoopMC_MEFHC.root`).

## 2D Python unfolding contract

`2d-unfolding/unfold_2d_omnifold_unbinned.py` is the authoritative 2D unbinned
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

## Bootstrap-replica workflow (`--bootstrap-seed N`)

Per-event Poisson(1) weight bootstrap on data + MC jointly. Invariants:

1. **Two independent sub-RNGs per replica** —
   `np.random.default_rng(seed)` for data, `np.random.default_rng(seed +
   10_000_000)` for MC. Data-stat and MC-stat are independent variance
   sources; they must not share a draw or the covariance under-counts.
2. **MC reco and MC truth weights ride a single per-event MC draw.**
   `sig["w_truth"]` and `sig["w_reco"]` are multiplied by the *same*
   per-event Poisson factor — they're two views of the same MC event and
   must stay correlated within the event row. Using independent draws
   for w_truth and w_reco would smear out the migration matrix.
3. **`--bootstrap-seed` + `--closure` is coverage-toy mode only.**
   Closure mode copies `sig["w_reco"]` into `measured_weights` before
   the bootstrap multiply; adding independent data/MC Poisson draws
   intentionally breaks the strict closure identity. Use this only for
   pseudo-experiment coverage calibration, not for deterministic closure
   tests.
4. **Pin the GBT random_state too.** Each replica should pass both
   `--bootstrap-seed N` and `--seed N` so ML stochasticity is removed
   from the per-replica variance. The bootstrap variance and the
   seedscan variance are *separable* uncorrelated components only when
   each replica's GBT seed is pinned.
5. **CV unfold = omit the flag.** Don't pass `--bootstrap-seed 0` and
   call it the CV; seed=0 is a valid replica with a non-trivial Poisson
   draw. The CV is the unflagged run.

Driver: `uq/run_bootstrap_interactive.sh` runs N replicas inside an
existing interactive allocation, batched WIDTH-wide ×
(128/WIDTH)-threads. **Use WIDTH=1 on Perlmutter single-node interactive
allocations.** The 2026-05-19 contention lesson (sklearn HistGBT
bandwidth-bound at WIDTH≥2) has not been re-benchmarked for lgbm; even
though lgbm scales fine to 128 threads on a single MEFHC unfold,
WIDTH>1 packed onto one node is unmeasured. Until benchmarked, run
sequential at full node width.

Analyzer: `uq/analyze_uq.py` rolls N replica ROOTs into per-bin
mean/std, 205×205 covariance on paper-reported bins, and 1D pT/pz
projection covariances. The Cholesky PD check uses a small jitter
fallback because the covariance is rank-deficient by construction
whenever N ≤ n_reported (205); a meaningful PD test needs N >
n_reported or pooling across replica sets. Quote the 205 paper-reported
bins everywhere, not the full 14×16 grid.

## Universe-covariance workflow (`--universe BAND:IDX`)

Universe covariance is computed from per-universe deltas relative to a
matched CV unfold. The CV must use the same omnifile, estimator,
`--seed`, iteration count, `--use-weights` setting, and flux input as the
universe sweep; only `--universe` is omitted. Mixing an exact-GBT
production CV with lgbm universe outputs injects backend/seed baseline
differences into every paired systematic covariance.

For the full lateral+vertical MEFHC sweep:

- Universe sweep:
  `sbatch_unfold_2d_MEFHC_5iter_universes_full.sh` →
  `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_<BAND>_<IDX>.root`.
- Matched CV:
  `sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh` →
  `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`.
- Rollup:
  `sbatch_final_rollup_full.sh`, whose driver
  `uq/final_rollup_full.sh` refuses to run without the matched full-CV
  ROOT and archives any superseded baseline-mismatched full-rollup
  artifacts before writing replacements.
- Plots:
  `uq_universe_band_pt.png` and `uq_universe_band_pz.png` show grouped
  categories, not one line per universe band. Categories are Flux,
  Models, Normalization, Statistical, Hadronic response, and Muon
  reconstruction. The Statistical line appears when a bootstrap
  covariance is supplied to `analyze_universes.py`.
- Paper-Fig.-6/7-style fractional uncertainty projections are made with
  `uq/plot_uncertainty_fig6_7_style.py`. Unlike the quick grouped sigma
  diagnostic in `analyze_universes.py`, this script projects the full
  205x205 covariance exactly, `C_1D = P C_2D P^T`, before dividing by
  the reported-bin 1D central value. It writes
  `uq/universe_stage2_MEFHC_full/MEFHC_fig6_7_uncertainty_{pz,pt}.png`
  and a numeric summary text file. ML covariance is included in the
  total when available, but is drawn only when it exceeds the configured
  visibility threshold.

Pair bands use the MINERvA-101 sum-of-squares convention,
`0.5 * (delta_plus delta_plus^T + delta_minus delta_minus^T)`.
Multi-universe bands use sample covariance with `ddof=1`. Inverse-cov
diagnostics for an ours-only covariance are expected to be fragile when
finite universe ensembles underspan the 205 reported-bin space; quote
direct per-bin pulls and truncated-mode chi2 alongside any pseudo-inverse
chi2.

## Flux and normalization

- The paper scalar `6.32e-8 /cm²/POT` is **not** the same quantity as the
  flux normalization term used by this code path. Substituting it blows up
  the total xsec by ~13.8×.
- Outputs embed `hFlux_pt` and `fluxSource` so later auditing doesn't
  depend on reopening an external ROOT file.
- Playlist-dependent flux differences are a ~0.2 % effect; not a dominant
  systematic.

## Paper / ancillary comparison

- No HepData entry. Authoritative target: `2d-unfolding/minerva_paper_anc/`.
- Use `bin_mapping.txt`, not the axis labels on the ancillary TH2D.
- `pzb=1` = first p_|| bin, 1.5 < p_|| < 2.0 GeV/c (the fragile low-p_||
  MINOS range-out regime).

## `IsMinosMatchMuon` (current state; our edit 2026-04-25)

The upstream MINERvA-101 tutorial `main` now does a real MINOS match:

```cpp
virtual bool IsMinosMatchMuon() const {
  return GetIsMinosMatchTrack() == 1;
}
```

Our `CVUniverse.h:107` does the same `isMinosMatchTrack==1` match and adds the
`minos_trk_is_ok==1` fit-quality bit:

```cpp
return GetInt("isMinosMatchTrack") == 1 &&
       GetInt(GetAnaToolName() + "_minos_trk_is_ok") == 1;
```

(An early tutorial revision instead used `has_interaction_vertex==1`, an
educational stub true for essentially every event in the pre-selected
AnaTuple, which biased the low-p_|| cross section low. Our 2026-04-25 edit
predates the upstream tutorial's own fix; both now enforce the real match.)

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

**Fixability assessment (2026-06-10, KNOWN_ISSUES #5)**: the
`MINOSEfficiencyReweighter` (intensity-dependent data/MC matching
efficiency, few-%) IS already applied in our MnvTune stack
(`runEventLoopOmniFold.cpp:1113`) — far too small to explain the
gradient. The candidate was the official MasterAnaDev muon-quality
selection the tutorial path omits. Scoping found dead-time already in
the preCuts (`NoDeadtime(1)`) and `minos_trk_fit_pass` implied by the
patched IsMinosMatchMuon (100% of matched events), leaving
`minos_trk_quality==1` (23.5% of matched MC is quality-2) and the
curvature-significance cut.

**Diagnostic RESULT (2026-06-10, job 54280253,
`minos_quality_diagnostic.py` → `products/minos_quality_diagnostic.png`)
— quality cuts ACQUITTED.** Conditional efficiency of the added cuts
among base-selected events (1A AnaTuples, 1.66M MC / 158k data):
eff_data/eff_MC = 1.03–1.05 at p_MINOS 1–2.5 GeV/c vs 1.06–1.14 at
10–60 (quality and quality+curvature alike). Closing the 0.6→1.0
gradient needed ~1.67 at low p falling to 1.0 — the observed double
ratio is far too small and has the wrong shape. Data is uniformly MORE
efficient than MC for these cuts, so applying them cannot produce a
low-p_|| data deficit at all. (Side finding: `minos_trk_eqp_qp` is the
already-fractional q/p error — the /qp variant removes >99% of
high-momentum events and is the wrong reading.) The gradient therefore
remains attributed to MINOS acceptance/efficiency modeling upstream of
selection (or generator rate mismodeling); its net effect inside the
published phase space is bounded by the 2D paper reproduction (integral
ratio 1.011), and the FPS p_||<1.5 region carries tier-2 flagging.

## Output hygiene

- Preserve known-bad but diagnostically useful files under an explicit
  `archive_*/debug/` name before a rerun overwrites a canonical path.
- Never leave invalidated outputs at canonical production paths once a
  corrected rerun is complete.

## 3D OmniFold extension (Workstream C)

The 3D available-energy extension (`d³σ/(dp_T dp_‖ dE_avail)`) lives in the
sibling `../3d-unfolding/` and **reuses this contract**: its driver
`unfold_3d_omnifold_unbinned.py` does `import unfold_2d_omnifold_unbinned` and
calls the 2D helpers, so everything above — POT scaling, `TRACKER_FIDUCIAL_N_NUCLEONS`,
the `in_truth_phase_space` θ_μ<20° gate, the per-p_T flux convention, the
`hXSec2D` naming for `compare_to_paper_fullcov.py` — applies unchanged. 3D-only
invariants:

- **Eavail axis defs** (arXiv:2312.16631 Eq. 4): truth `GetEAvailableTrue()`,
  reco `NewEavail()` (tracker+ECAL ×1.17), added standalone to `CVUniverse.h`
  (the MAT calculator headers redefine `GetVertex()`). MeV→GeV in the branches.
- **Eavail binning catch bin**: the top edge must be large (default 100 GeV) so
  the Eavail-marginal captures the full recoil tail — `Σ_k xsec·ΔE_k = 2D` only
  if every truth event lands in a bin. A truncated top edge breaks the anchor.
- **CV-only**: the 3D driver does NOT carry the universe / alt-model / bootstrap
  machinery; that is the deferred 3D-UQ campaign.
- **`compare_to_paper_fullcov.py` from 3d-unfolding/**: always pass
  `--out-prefix`, or the default clobbers the tracked 2D `MEFHC_5iter_pull_full.png`.

Its own docs (mirroring this triad): `../3d-unfolding/3D_OMNIFOLD_STATUS.md`
(dashboard), `../3d-unfolding/3D_OMNIFOLD_RUN_LOG.md` (chronology),
`../3d-unfolding/README.md` (orientation + how-to-run).

## Documentation split

Per-workstream mirror (see AGENTS.md). **2D** (this directory):
- `2D_OMNIFOLD_STUDY_STATUS.md` — dashboard, current state, next actions.
- `2D_OMNIFOLD_RUN_LOG.md` — append-only chronology.
- `2D_OMNIFOLD_REFERENCE.md` (this file) — stable invariants and gotchas
  (shared with 3D; see § "3D OmniFold extension" above).
- `PLOT_GUIDE.md` — PNG reading guide.

**3D** (`../3d-unfolding/`): `3D_OMNIFOLD_STATUS.md`, `3D_OMNIFOLD_RUN_LOG.md`,
`README.md`. No separate 3D REFERENCE — invariants are shared here.
