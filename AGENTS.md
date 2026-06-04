# MINERvA-OmniFold Agent Context

## Project Scope
MINERvA-101 cross-section and OmniFold studies for muon kinematics:
- 1D **p_T** unbinned OmniFold (revalidated 2026-05-02 against playlist 1A;
  patched to the 2D contract; OmniFold-vs-IBU comparison plot regenerated.
  Legacy `Documents/` 2026-03-26 ROOTs remain superseded — diagnostic only)
- 1D binned OmniFold (debug campaign complete — closure verified, found
  equivalent to D'Agostini IBU)
- 2D **(p_T, p_||)** double-differential — current active campaign,
  reproducing arXiv:2106.16210. **Pipeline finalized at Phase 18.2
  (2026-05-18).**

## Current Campaign — 2D OmniFold

**Goal**: Reproduce arXiv:2106.16210 (Ruterbories et al., Phys. Rev. D 106,
032001) — MINERvA ME FHC d²σ/(dp_T dp_||) CC inclusive — with 2D unbinned
OmniFold in place of D'Agostini IBU. Validated on playlist 1A; full
12-playlist MEFHC production complete.

**Documentation convention — per-workstream mirror.** Each analysis workstream
keeps its own STATUS (dashboard) + RUN_LOG (append-only chronology) co-located in
its directory, prefixed by dimensionality (`2D_OMNIFOLD_*`, `3D_OMNIFOLD_*`).
Durable invariants live once in the 2D REFERENCE and are shared (the 3D driver
imports the 2D helpers). Deliverables (`docs/technote/`,
`docs/uq_statistical_methods.tex`) sit outside this triad.

**Authoritative docs (read these before touching the pipeline):**
- `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md` — 2D dashboard, current numbers, next actions.
- `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` — stable invariants and gotchas (shared 2D+3D).
- `2d-unfolding/2D_OMNIFOLD_RUN_LOG.md` — 2D append-only chronology of phases 1-18.2.
- `2d-unfolding/PLOT_GUIDE.md` — PNG reading guide.
- `3d-unfolding/3D_OMNIFOLD_STATUS.md` — 3D Eavail dashboard (Workstream C).
- `3d-unfolding/3D_OMNIFOLD_RUN_LOG.md` — 3D append-only chronology (C1→C2→C3).

**Headline numbers (Phase 18.2 MEFHC, 5-iter production):**
- σ_total = 3.073e-38 cm²/nucleon (paper: 3.039e-38; ours runs 1.12 % high).
- Strict-interior χ²/ndf vs paper (185 bins, full cov) = 3.549.
- All-reported-bins χ²/ndf (205 bins) = 3.565.
- Median bin ratio (ours/paper, strict interior) = 1.0084.
- Bins within 5/10/20 % of paper (185 strict interior) = 81.1 / 95.7 / 98.4 %.
- Global OmniFold input completeness c = 1.000000 (exact by construction).

**Defining properties of the Phase-18.2 pipeline:**
1. **Truth-tree-authoritative reco gate.** Event loop walks `mc_truth_denom`
   first to build a `(mc_run, mc_subrun, mc_nthEvtInFile)` key set, then
   walks reco and fills `mc_signal_reco` only when the key is in the set.
   Truth-only events are appended as native OmniFold miss entries.
2. **Bilateral upstream-dup dedupe.** Both loops dedupe on the same key
   (handles 1,102 truth + 7 reco duplicates from one upstream-double-filled
   AnaTuple, `MasterAnaDev_mc_AnaTuple_run00111353_Playlist.root`).
3. **By-construction completeness.** `mc_signal_reco` entries ==
   `mc_truth_denom` entries (32,849,103 each at MEFHC). The Phase-16 c
   division in `unfold_2d_omnifold_unbinned.py` becomes a no-op self-check.

**Residual disagreement.** The remaining ~3 χ²/ndf is dominated by
sub-2 % shape disagreement in the highest p_|| tails (paper / weighted
reaches 1.15 at 40-60 GeV/c). Attributed to a small reweighter-detail
effect at high E_ν. Method-blindness confirmed by IBU 1D-projection
cross-check (post-Phase-16): IBU and OmniFold-2D agree on the same inputs
to ~1.7 %, both reproduce paper to within ~1-2 %.

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
patched binary in the past; see `memory/project_build_source_path.md`).
Rebuild via `sbatch_build.sh`.

### Per-playlist event loop, then hadd
`runEventLoopOmniFold.cpp` picks ONE global playlist flux/calibration from
the first event's run number. **Never** feed it a combined MEFHC manifest
— it silently applies the first playlist's flux to all events and
corrupts 11/12 of the dataset. Run per-playlist, then `hadd`.

### 2D pipeline (canonical filenames; no phase tag suffix)
1. Per-playlist event loops via `2d-unfolding/sbatch_evloop_array.sh` (1B–1P
   as 11-task array; 1A run separately or via interactive shell). Outputs:
   `runEventLoopOmniFold_1{A..P}.root`.
2. `2d-unfolding/sbatch_hadd_MEFHC.sh` → `runEventLoopOmniFold_MEFHC.root`.
3. `2d-unfolding/sbatch_unfold_2d_MEFHC.sh` → runs
   `unfold_2d_omnifold_unbinned.py --use-weights --iters 5` →
   `2d_crossSection_omnifold_MEFHC_5iter.root`.
4. Plotting (see `PLOT_GUIDE.md` for the full list):
   `plot_2d_cross_section.py`, `plot_2d_paper_comparison.py`,
   `plot_2d_threeway_fig13.py`, `plot_efficiency_fig5_style.py`,
   `compare_to_paper_interior.py`, `compare_to_paper_fullcov.py`,
   `normalize_xsec_shape.py` + `plot_2d_paper_comparison_shape.py`.

### Flux
`runEventLoopOmniFold.cpp` does NOT write `pTmu_reweightedflux_integrated`.
Use `sbatch_runEventLoop_baseline_flux_array.sh` to regenerate per-playlist
baseline flux, then `combine_flux_MEFHC.py` to build the POT-weighted MEFHC
flux at `2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root`. The 2D
Python script embeds the flux histogram into its output for self-contained
auditing.

## 2D Python contract (must hold)
1. **Mask measured data to phase space** (0 ≤ p_T ≤ 4.5,
   1.5 ≤ p_|| ≤ 60) before step-1 training.
2. **Subtract background** to build a non-negative reco target;
   pass per-event `measured_weights` into `ohf.omnifold(...)`.
3. **Include signal fakes in the reco-side subtraction.** Fakes (reco in
   phase space, truth out) appear in `mc_signal_reco` but are filtered by
   `omnifold.py`'s `MC_pass_truth_mask`. Add their POT-scaled reco weights
   into `hBkgReco2D` so both measured and MC reco sides are fake-free.
   Under Phase 18.2 the truth-tree-authoritative reco gate makes this set
   empty in practice — `passesReco && !inPhaseSpace` is vacuous on MINERvA
   AnaTuples — but the code path is retained as a regression check.
4. **`hUnfold2D` is a truth-space event yield.** Fill with
   `step2_weights * truth_w_in`, not raw `step2_weights`.
5. **Divide by `hOFCompleteness2D`** (`hOFInputTruth2D / hOFTruthDenom2D`),
   not by absolute selection efficiency `hEff2D`. Under Phase 18.2 this
   ratio is ≡ 1 by construction; the division is a no-op self-check.
6. **Closure mode** (`--closure`) restricts pseudo-data to
   `pass_reco & pass_truth` and uses `sig["w_reco"]` as `measured_weights`
   when `--use-weights`. Sets completeness ≡ 1.
7. **Production sbatch must pass `--use-weights`** to match the 1A
   validation footing.

## Paper / ancillary comparison
- No HepData entry. Authoritative target: `2d-unfolding/minerva_paper_anc/`.
- Use `bin_mapping.txt`, **not** the axis labels on the ancillary TH2D
  (those are cosmetic rounding 0.075/0.325/0.475).
- `pzb=1` is first p_|| bin (1.5 < p_|| < 2.0 GeV/c).
- Paper reports 205 / 224 bins (19 diagonal bins with pt/p|| > tan 20°
  unreported); strict-interior comparison uses 185 bins.

## NERSC SLURM gotchas

### Running past the 3-hour interactive limit — use `alloc_run.sh`
The agent runs on the **login node** (start it inside `tmux`/`screen` so it
survives disconnects), NOT inside an salloc shell. An salloc shell dies at the
180-min `interactive` limit and would take the agent with it. Instead, dispatch
every compute command through the wrapper:
```bash
./alloc_run.sh '<command>'        # quote the whole command if it has pipes/&&/redirects
./alloc_run.sh --status           # show the shared allocation
./alloc_run.sh --end              # release it (scancel)
```
- It holds **exactly one** shared allocation (job-name `claude-hold`, guarded by
  a job-name check + `flock`), detached via `setsid` so it outlives the shell.
- It **reuses** that allocation across calls and **auto-requests a fresh one**
  when the previous 3-hour allocation has expired — so total wall-clock is
  unbounded while each underlying allocation stays ≤ 3 h.
- The command runs on the compute node via `srun --jobid=<JOB> --overlap`, from
  the repo root, with `setup_salloc_env.sh` already sourced (env chatter goes to
  stderr; the command's stdout stays clean).
- **Never** launch a bare interactive `salloc`/`source start_alloc.sh` for agent
  work, and never start a second holder — one allocation at a time. Tune with
  `ALLOC_HOLD_SECONDS` / `ALLOC_CPUS` / `ALLOC_JOB_NAME` if needed.
- **Leave the allocation running between commands.** Do NOT call `--end` just
  because a command finished — the next command reuses the live node, and
  tearing it down only to re-request one wastes queue time and compute on
  repeated start/stop churn. Only run `./alloc_run.sh --end` when the user
  explicitly says they're done / closing the session, or asks to free the node.
  Absent any such signal, keep it up; an idle allocation self-expires at the
  3-hour limit anyway, and the next dispatch transparently requests a fresh one.
- This is for interactive-style work that fits one node. Multi-node arrays /
  multi-hour walls still go through `sbatch` (see below).

- **Use the running interactive allocation when one exists, instead of
  submitting a new sbatch.** The regular and shared queues at NERSC
  routinely sit on `Priority` for several minutes to hours. If
  `squeue -u $USER` shows a live `interactive` job with time remaining,
  any task that fits inside that node (the build job, a short event-loop
  smoke, a single short-wall unfold, a Python analysis script) should
  run there via `srun --jobid=<INTERACTIVE_JOBID> --overlap -n 1
  --cpus-per-task=<N> bash -lc '...'`. **Cancel the equivalent queued
  sbatch** if you submitted one before noticing the interactive — running
  in two places leaks compute and risks output-file races. Reserve fresh
  sbatch submissions for jobs that don't fit a single interactive
  allocation (multi-node arrays, multi-hour walls, or work that needs to
  outlive your shell). The submit-vs-interactive decision is also
  documented in `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`.
- Do NOT combine `set -u` with `conda activate root_6_28`. The conda
  `deactivate-root.sh` hook references `CONDA_BACKUP_ROOTSYS` and aborts
  under nounset in a fresh batch shell.
- Export `PYTHONUNBUFFERED=1` so Python stdout flushes to `.out` live.
- Do NOT use `srun` inside 2D OmniFold sbatch scripts. Inherited
  `SRUN_CPUS_PER_TASK` from a live interactive allocation breaks nested
  srun. Bare `python ...` is the safe default. (The interactive-shell
  case is the opposite: `srun --jobid=<INTERACTIVE> --overlap` is the
  correct primitive for launching work onto the existing allocation.)
- Templates: `sbatch_unfold_2d_MEFHC.sh` (full-node 128 CPU regular QOS),
  `sbatch_iter_scan_2d.sh` (shared QOS 2 CPU).

## Runtime notes (2D)
| Task | Resource | Wall time |
|---|---|---|
| C++ event loop, one playlist | shared QOS, 1 task | ~2 h |
| Event loop, all 12 playlists | 11-task array | ~3-4 h (parallel) |
| hadd MEFHC | shared QOS | < 1 min |
| 2D OmniFold, 5-iter, 1A stats | shared QOS, 2 CPU | ~1.5 h |
| 2D OmniFold, 5-iter, full MEFHC | regular QOS, 128 CPU | ~19 h (≈3h50m/iter × 5) |

Iter-count: original pre-Phase-16 1A iter-scan showed 5-iter 0.08 % off
10-iter total xsec, so production uses 5. A Phase-18.2 re-scan is in
flight (job `53116867_[1,3,5,8,10]`) to confirm this still holds under
native miss handling.

## Patched code

### `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`
Phase-18.2 truth-tree-authoritative reco gate with bilateral key dedupe:
- `makeEventKey(run, subrun, nth)` packs the triplet into a `uint64_t`.
- `LoopAndFillUnbinnedMCTruthDenom` runs first; populates an
  `outTruthDenomIDs` set and `outTruthDenomCache` vector. Truth-side
  `seenKeys` dedupe (Phase 18.1) skips upstream double-fills.
- `LoopAndFillUnbinnedMCSelectedSignalReco` consults `truthDenomIDs` and
  fills `mc_signal_reco` only when `inPhaseSpace && key ∈ truthDenomIDs`.
  Reco-side `seenRecoKeys` dedupe (Phase 18.2) mirrors the truth-side fix.
- `AppendTruthOnlyMisses(sigOut, truthDenomCache, recoIDs)` writes one
  miss entry per truth-pass event whose key isn't in the reco set.
- Output ROOT carries `TParameter`s `hasTruthOnlyMisses`,
  `nTruthOnlyMisses`. Python pipeline reads them and emits a WARN if
  `c_global` deviates from 1.0 by >0.5 %.
- Writes 4 TTrees with both `p_T` and `p_||` branches per event.
- Does **not** write `pTmu_fiducial_nucleons` (hadd-corrupted: hadd sums
  `TParameter<double>` across inputs, inflating the detector-geometry
  constant 12×). Python uses the fixed tracker constant 3.2353e30.
- Environment flags: `MNV101_DISABLE_TRUTH_MISSES=1` falls back to legacy
  no-miss behavior; `MNV101_TRUTH_ONLY=1` short-circuits reco loops;
  `MNV101_DUMP_COMPONENTS=1` writes per-reweighter dump branches.

### `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:107`
`IsMinosMatchMuon()` patched (2026-04-25, Phase 11):
```cpp
virtual bool IsMinosMatchMuon() const {
  const std::string ok_branch = GetAnaToolName() + "_minos_trk_is_ok";
  return GetInt("isMinosMatchTrack") == 1 && GetInt(ok_branch.c_str()) == 1;
}
```
Replaces the educational stub `has_interaction_vertex==1`.

### Active 2D files
- **C++**: `runEventLoopOmniFold.cpp`, `cuts/MaxPtMu.h`,
  `util/Binning.h` (paper's 14 p_T × 16 p_|| edges).
- **Python**: `2d-unfolding/unfold_2d_omnifold_unbinned.py`,
  `plot_2d_cross_section.py`, `plot_2d_paper_comparison.py`,
  `plot_2d_paper_comparison_shape.py`, `plot_2d_threeway_fig13.py`,
  `plot_efficiency_fig5_style.py`, `plot_closure_2d.py`,
  `plot_iter_convergence.py`, `normalize_xsec_shape.py`,
  `compare_to_paper_{fullcov,interior}.py`, `combine_flux_MEFHC.py`,
  `diagnose_truth_shape_unweighted.py`, `compare_flux_to_paper_2019.py`,
  `verify_eff_fix_predicted_xsec.py`.
- **SLURM** (canonical, no phase suffix): `sbatch_build.sh`,
  `sbatch_evloop_array.sh`, `sbatch_hadd_MEFHC.sh`,
  `sbatch_unfold_2d_MEFHC.sh`, `sbatch_iter_scan_2d.sh`,
  `sbatch_runEventLoop_baseline_flux_array.sh`,
  `sbatch_finalize_MEFHC.sh`, `sbatch_validate_1A_corrected.sh`,
  `sbatch_download_playlist.sh`. Pre-Phase-18 sbatch scripts preserved
  in `2d-unfolding/archive_pre_phase18/` with git history.
- **Outputs**: `runEventLoopOmniFold_MEFHC.root`,
  `runEventLoopOmniFold_1{A..P}.root`,
  `2d_crossSection_omnifold_MEFHC_5iter.root` (production),
  `2d_crossSection_omnifold_1A_5iter.root`.
- **Manifests**: `2d-unfolding/playlist_manifests/1{A..P}_{MC,Data}.txt`.

### TTree schema
All TTrees carry both p_T and p_|| branches:
- `mc_truth_denom`: `MC` (p_T), `MC_pz` (p_||), `w_truth`
- `mc_signal_reco`: `sim`, `sim_pz`, `sim_pass`, `w_reco`, `MC`, `MC_pz`, `w_truth`
- `mc_background`: `sim_background`, `sim_background_pz`, `sim_background_pass`, `w_bkg`
- `data`: `measured`, `measured_pz`, `measured_pass`

Metadata (`TParameter<double>`): `mcPOTUsed`, `dataPOTUsed`.
Phase-17/18 additions (`TParameter<int>`/`<long>`): `hasTruthOnlyMisses`,
`nTruthOnlyMisses`. No `pTmu_fiducial_nucleons` (intentional — see hadd
note above).

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
patched 2026-04-30 to honour the 2D Python contract.

Patched-vs-patched 1A rerun (SLURM job 52271486, 2026-05-02) produced the
current valid outputs in `2d-unfolding/unbinned_1d_study/`:
`runEventLoop{OmniFold,Data,MC}.root`,
`pTmu_crossSection_omnifold.root` (5 iter, `--use-weights`),
`pTmu_crossSection.root` (D'Agostini IBU on the same selection),
`ptmu_gaussian_style_unbinned.pdf`. OmniFold and IBU agree at the QE
peak; OmniFold tracks data more flexibly at the spectrum tails.

The legacy `Documents/` 2026-03-26 ROOTs remain pre-MINOS-fix and are
diagnostic-only — do not quote against the paper.

**Pending 1D work** (deferred until after 2D campaign closes): apply the
same Phase-18 truth-tree-authoritative gate to the 1D pipelines
(`unbinned_1d_study/unfold_ptmu_omnifold_unbinned.py` and
`ibu_1d_projection/build_1d_ibu_inputs.py`). Both currently filter
`tru_ok` on the pT rectangle alone; neither reads `MC_pz`. With the
Phase-18 MEFHC ROOT pointed in, they inherit a clean c by construction;
the explicit gating tightening is still on the to-do list.

### 1D quick start
```bash
sbatch 2d-unfolding/unbinned_1d_study/sbatch_unfold_1d_unbinned_1A.sh
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
- `2d-unfolding/archive_pre_phase16/` — pre-Phase-16 outputs and plots.
- `2d-unfolding/archive_pre_phase18/` — Phase-16/17 era artifacts (postfix
  ROOTs, Phase-17 side-experiment ROOTs, superseded sbatch scripts and
  SLURM logs).
- `2d-unfolding/minerva_paper_anc/` — arXiv ancillary release.
- `2d-unfolding/playlist_manifests/` — per-playlist Data/MC file lists.
- `2d-unfolding/baseline_flux/` — per-playlist baseline-flux ROOTs (gitignored).
- `2d-unfolding/reference/` — reference papers (Ruterbories PDF + slide deck).
- `unbinned_unfolding/` — RooUnfold/OmniFold source + in-tree `build/`.
- `unbinned_unfolding/examples/` — reference OmniFold usage.

## Output hygiene
- Pre-Phase-18 outputs live under `archive_pre_phase16/` (pre-Phase-16) and
  `archive_pre_phase18/` (Phase-16/17 era). Never re-introduce phase-tagged
  filenames at the canonical level once the pipeline is finalized.
- Never leave invalidated outputs at canonical production paths once a
  corrected rerun is complete.

## Common failure modes
- Branch mismatch between writer and reader.
- Missing/invalid POT metadata in OmniFold ROOT inputs.
- Wrong binary on `$PATH` (build-tree shadowing the installed patched copy
  — Phase-18 hit this trap; see `memory/project_build_source_path.md`).
- Pre-patch event-loop outputs (before 2026-04-25 `IsMinosMatchMuon` fix,
  or before Phase-18.2 dedupe) used in paper comparisons.
- Pre-fix merged OmniFold ROOTs carrying summed `pTmu_fiducial_nucleons`
  metadata — treat as untrustworthy.
- Mixing UF/OF vs in-range conventions when comparing totals.
- Substituting the paper scalar `6.32e-8 /cm²/POT` for the
  flux-normalization term used by this code path (blows up xsec ~13.8×).
- PyROOT unavailable (`ModuleNotFoundError: ROOT`) — env not sourced.

## Notes for future agents
- **`LITERATURE_NOTES.md`** (repo root) holds the 2026-06-03 audit vs the 2025
  OmniFold literature (T2K arXiv:2504.06857; Practical Guide arXiv:2507.09582) and
  the MINERvA data-release catalogue. Verdict: no critical defects. New `uq/`
  diagnostics — `ensemble_mean_cv.py`, `bottom_line_test.py` (closure +
  data-prior modes), `classifier_calibration.py` (GBDT vs NN) — and
  `3d-unfolding/genie/compare_ascencio_eavail.py`. The technote open questions are
  resolved in `docs/technote/sec_openquestions.tex` (only the high-E_avail DIS-tail
  excess and publication precedent remain).
- **`docs/HIGHER_DIM_OMNIFOLD_DESIGN.md`** plans the next dimensional step (Phase 1:
  q3 as a 4th scalar axis, GBDT-native; Phase 2: a vendored NN/point-cloud track) and
  states the **GBDT→NN crossover criterion** (stay on LightGBM for ≲10 fixed scalar
  features; switch to NN only for variable-length point clouds). Design/hand-off only.
- The 2D campaign is **finalized at Phase 18.2**. Read the four
  `2d-unfolding/2D_OMNIFOLD_*` docs before changing the pipeline.
- Memory pointers under `~/.claude/projects/.../memory/MEMORY.md` capture
  rolling context. Verify referenced files still exist before acting on a
  memory.
- For physics results, do not use binned OmniFold output without upstream
  package fixes; use the unbinned path.
- Do binned work inside `2d-unfolding/binned_study/`, not at the top level.
