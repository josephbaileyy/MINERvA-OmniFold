# 2D OmniFold run log (active)

Chronology of the active phase of the analysis, starting from
Phase-18.2 production unfold (2026-05-18) — i.e. once the pipeline was
frozen and analysis-side work (uncertainty quantification, paper
comparison) became the focus.

For Phases 1–18.1 (how we got to Phase-18.2), see
`2D_OMNIFOLD_RUN_LOG_ARCHIVE.md`. For current headline numbers and
state see `2D_OMNIFOLD_STUDY_STATUS.md`.

---

## 2026-05-18 — Pipeline finalization

### Filename canonicalization

With Phase 18.2 ratified as the production pipeline, the `_phase18` and
`_phase18p2` filename suffixes were dropped in favor of canonical names.
The transition:

- All 12 per-playlist ROOTs: `runEventLoopOmniFold_{1A..1P}_phase18.root` →
  `runEventLoopOmniFold_{1A..1P}.root`.
- Merged MEHFC: `runEventLoopOmniFold_MEHFC_phase18.root` →
  `runEventLoopOmniFold_MEHFC.root` (2.0 GB).
- xsec outputs: `2d_crossSection_omnifold_MEHFC_phase18_5iter.root` →
  `2d_crossSection_omnifold_MEHFC_5iter.root`. Same for 1A.
- SLURM scripts: `sbatch_build_phase18.sh`, `_evloop_array_phase18.sh`,
  `_hadd_MEHFC_phase18.sh`, `_unfold_2d_MEHFC_phase18.sh` → drop suffix,
  edit internals (job-name, output/err, OMNIFILE, XSEC_OUT, WORKDIR,
  FINAL).

Pre-Phase-18 collidable files moved to a new `archive_pre_phase18/`:

- Pre-Phase-16 ROOTs (Apr 25 originals of `MEHFC.root`, `1M.root`,
  `1N.root`).
- Phase-17 side-experiment ROOTs and the `_phase17_tightgate` sbatch
  script.
- Superseded sbatch scripts (`git mv` preserved history): pre-Phase-16
  `evloop_array.sh`, `hadd_MEHFC.sh`, `unfold_2d.sh`,
  `unfold_2d_fullstats.sh`, Phase-16 `unfold_2d_fullstats_postfix.sh`.
- 36 superseded SLURM `.out/.err` files from chains 52729573, 52973620,
  52983620-_622, 53012899-_901.

Also cleaned:

- 25 empty work directories (13 `evloop_work_*_phase18/`, 12
  `baseline_flux/work_*/`) — CWDs from past array jobs.
- 3 interactive-shell `.log` files (`evloop_1A_phase18.log`,
  `evloop_1A_fakes-routed.log`, `unfold_1A_phase18.log`) moved to archive.
- 3 stale `.pid` files (interactive run leftovers) deleted.
- `validate_1A_phase17_work/` (held a single stale log) archived.

Live audit trail of 8 `.out/.err` files left in `2d-unfolding/`:
`unfold_MEHFC_phase18_53034070.*` (Phase-18 production unfold whose
numbers are in the current STATUS table) plus the four Phase-18.2 chain
logs (`build_phase18p2_53095454`, `evloop_phase18_4_53095457`,
`hadd_MEHFC_phase18_53095459`).

### MEHFC Phase-18.2 unfold

Submitted as job `53116554` (24h wallclock, regular QOS, 128 CPU). Reads
canonical `runEventLoopOmniFold_MEHFC.root`, writes canonical
`2d_crossSection_omnifold_MEHFC_5iter.root`. Expected delta vs Phase-18.1
production (job 53034070) is sub-ppm because the 7 deduped reco entries
are 0.2 ppm of MEHFC.

### 1A iteration-convergence re-scan

The original 5-iter production choice was justified by a pre-Phase-16 1A
iter-scan. Phase 18 changed the OmniFold input substantially (+33%
training events, native miss handling), so a Phase-18.2 1A iter-scan was
submitted as job `53116867_[1,3,5,8,10]` in parallel (shared QOS, 2 CPU,
6h walltime each). Will produce `2d_crossSection_omnifold_1A_{1,3,5,8,10}iter.root`.
Result will replace the iteration-convergence table in STATUS.

### Documentation refresh

`2D_OMNIFOLD_STUDY_STATUS.md` compressed from 712 lines to 264. The
verbose phase-by-phase narrative was replaced with a single
"How we got here" summary table pointing at this run log. Headline
metric table, χ² vs p_||-min table, paper binning, runtime notes, and
code/data inventory retained (with all paths updated to canonical
filenames). This entry is the last item in the active-history section of
the run log; everything older is archival.

## 2026-05-19 — Uncertainty work + HistGBT estimator port

### ML-stochasticity seed scan

Advisor (2026-05-19): the existing χ²-vs-paper uses the paper's
covariance, so any uncertainty that differs between the two methods is
*excluded* by construction. Next step is to characterize
method-dependent uncertainties; the most distinct is the stochastic
nature of the ML training.

Plumbed `--seed N` into `unfold_2d_omnifold_unbinned.py`. When set, the
three sklearn GBDT estimators (step-1 classifier, step-2 classifier,
step-1 miss regressor) take `random_state = N, N+1, N+2` respectively,
threaded through to `ohf.omnifold(...)` via
`classifier{1,2}_params={"random_state": ...}` and
`parameter_format="dict"` (so the C++ TMap-string converter is skipped
on Python dict inputs). With `--seed` unset, behavior is unchanged
(falls back to sklearn's `np.random` global state — natural cross-process
variation).

New sbatch `sbatch_unfold_2d_MEHFC_5iter_seedscan.sh`:
`--array=1-10`, 128 CPU, 24h walltime each, outputs to
`seedscan/2d_crossSection_omnifold_MEHFC_5iter_seed${N}.root`. Submitted
as job 53180443; PENDING `Reserved for maintenance` (will dispatch on
or after 2026-05-27T06:00 UTC).

Analyzer at `seedscan/analyze_seedscan.py`: loads N trial ROOTs, emits
total-σ mean±std, per-bin std/mean (full 205 and strict-interior 185),
shape-only spread, 14×16 rel-spread heatmap, and pT/pz band plots.

### 8-iter MEHFC unfold queued

For the iter-convergence cross-check (advisor wanted to see how 5 vs 8
look). New sbatch `sbatch_unfold_2d_MEHFC_8iter.sh`, 36h walltime, 128
CPU; output `2d_crossSection_omnifold_MEHFC_8iter.root`. Job 53159240
PENDING `Reserved for maintenance`, will dispatch on or after
2026-05-27T06:00 UTC.

### HistGBT estimator port

sklearn `GradientBoostingClassifier` is single-threaded; the 128-CPU
production allocation has only one core actually working through the
~19h unfold. Sklearn ships `HistGradientBoostingClassifier` — same
gradient-boosting algorithm but with 256-quantile histogram-based
splits and OpenMP parallelism. Drop-in replacement; sklearn 1.8.0
already installed.

`unbinned_unfolding/python/omnifold.py`:

- Imported `HistGradientBoosting{Classifier,Regressor}`.
- Added `estimator="exact"` kwarg to `omnifold(...)`. `exact` branch is
  unchanged. `hist` branch builds
  `HistGradientBoosting{Classifier,Regressor}` with matched defaults
  (`max_iter=100`, `max_leaf_nodes=8` ≈ depth 3, `learning_rate=0.1`)
  and any caller-supplied params overriding those.
- Raises on unknown values for `estimator`.

`unfold_2d_omnifold_unbinned.py`:

- Added `--estimator {exact,hist}` (default `exact`).
- Threaded `estimator=args.estimator` into the `ohf.omnifold(...)` call.

### HistGBT 1-iter MEHFC smoke (interactive 53179085)

Ran via `srun --jobid=53179085 --overlap -n 1 --cpus-per-task=32` with
`OMP_NUM_THREADS=32` and `--seed 1 --iters 1 --estimator hist`.
Wallclock **355 s** (vs ~3h50m per iter for exact GBT → ~40× per-iter
speedup; pure-training ratio closer to 80× after subtracting the
~3 min one-shot I/O). End-of-iter sanity:

- step2 sum=3.718e+07, mean=1.1317 (exact 5-iter: 3.719e+07, 1.1321).
- hUnfold2D integral=6.55827e+06 (exact 5-iter: 6.56409e+06; 0.09%
  lower at 1 iter, expected).
- c = 1.0000 (by-construction, independent of estimator).
- Total σ from p_T = 3.071e-38 cm²/nucleon (paper 3.039e-38, exact
  5-iter 3.073e-38; 0.07% below exact's 5-iter answer).

### HistGBT 1A iteration-scan vs exact

Ran `--estimator hist --seed 1` at `--iters {1,3,5,8,10}` on the 1A
playlist in the interactive, sequential. Total **387 s** for all five
points (per-iter HistGBT 1A training cost ~7 s on 32 threads). Outputs
to `histgbt_iter_scan/2d_crossSection_omnifold_1A_{i}iter_histgbt.root`.

Comparison plot `histgbt_iter_scan/1A_iterscan_convergence_hist_vs_exact.png`
overlays the exact-GBT 1A iter-scan (already in the parent dir) and
HistGBT companion. Per-bin shape RMS vs each estimator's own 10-iter
asymptote:

| iter | exact GBT | HistGBT |
|---|---|---|
| 1 | 5.00% | 2.43% |
| 3 | 2.53% | 1.16% |
| 5 | 1.54% | **0.86%** |
| 8 | 0.55% | 0.67% |
| 10 | 0 (ref) | 0 (ref) |

HistGBT converges ~2× tighter through iter 5; 5-iter HistGBT shape
stability ≈ 7-iter exact GBT. Total-σ asymptotes agree to **0.04%**
(exact 10-iter = 3.0529e-38, hist 10-iter = 3.0516e-38) — within
expected ML-noise budget for two distinct GBDT implementations (256-bin
quantization, different tie-breaking).

### 5-iter MEHFC HistGBT validation (interactive 53179085)

Ran `--iters 5 --use-weights --estimator hist --seed 1` on the full
MEHFC input via `srun --jobid=53179085`. Wallclock **1053 s
(17m33s)** vs the exact-GBT 5-iter production at 69,523 s → **66×
speedup measured** (pure-training ratio ~79× after I/O amortizes).

Output: `histgbt_smoke/2d_crossSection_omnifold_MEHFC_5iter_histgbt.root`.

Sanity vs exact 5-iter production:

| | Exact 5-iter | HistGBT 5-iter |
|---|---|---|
| Total σ | 3.073e-38 | 3.073e-38 ✓ (4 sig figs) |
| σ / paper | 1.0111 | 1.0111 ✓ |
| hUnfold2D | 6.56409e+06 | 6.5627e+06 (−0.02%) |
| step2 sum | 3.719e+07 | 3.718e+07 |
| step2 mean | 1.1321 | 1.1317 |
| c | 1.0000 | 1.0000 |

The 0.04% 1A 10-iter asymptotic gap does not survive to MEHFC at the
production iter count. Validation #16 closed.

### Directory cleanup (2026-05-19)

Removed superseded artifacts whose findings are already in this run log
or STATUS:

- ROOTs: `2d_crossSection_omnifold_MEHFC_5iter_postfix{,_shape}.root`
  (Phase-16 era, replaced by canonical Phase-18.2 files).
- SLURM logs in 2d-unfolding/ root: the Phase-18 / Phase-18.2 build /
  evloop / hadd / unfold / iter-scan / IBU chain `.out/.err` (8 jobs).
  All corresponding ROOT outputs are preserved; numbers are in STATUS.
- Phase 15/16 attribution one-offs: `compare_flux_to_paper_2019.py`
  + `.csv` + `.png`, `diagnose_truth_shape_unweighted.py` +
  `truth_shape_unweighted_MEHFC_*`, `verify_eff_fix_predicted_xsec.py`,
  `plot_minos_fix_bkg_fraction.py` +
  `MEHFC_5iter_minos_fix_bkg_fraction.png`,
  `MINERvA_Flux_pdg14_500MeVBins_arXiv1906_00111.csv`.
- `__pycache__/`.

Sources for the deleted .py files remain recoverable via
`git log --all --follow -- 2d-unfolding/<file>`.

### Next steps

- Cancel queued exact-GBT seedscan 53180443 and resubmit on HistGBT.
  Per-trial budget should drop from 24 h to ~30 min walltime, 32 CPU
  (not 128).
- After 10 trials land, run `seedscan/analyze_seedscan.py` for the
  ML-noise envelope (advisor's headline ask).
- Decision on going beyond HistGBT (LightGBM / XGBoost CPU or GPU) is
  deferred — only worth the port effort if either the per-bin spread
  comes back atypical or the analysis grows past ~5D.

### Ideal HistGBT trial configuration (lesson, 2026-05-19)

Two attempts to parallelize trials on a single interactive node both
hit memory-bandwidth contention:

| Config                | Per-trial slowdown vs 32-thread baseline | Source              |
|-----------------------|------------------------------------------|---------------------|
| 4-wide × 32 threads   | ~8× slower                               | earlier attempt     |
| 2-wide × 64 threads   | ~4.5× slower (~16 min/iter vs 3.5 min)   | this session, killed at iter 2 |

Per-process `ps` confirmed `OMP_NUM_THREADS=64` ran at ~2820% CPU
(~28 cores effective per process) on the 2-wide × 64 run — half the
requested threads were spinning on memory access. Histogram-build in
HistGBT is memory-bandwidth bound, not core-bound, so packing more
processes onto one node always loses.

**Validated single-trial baseline:** 32 threads, dedicated node (sbatch),
5-iter MEHFC HistGBT in 17m33s (1053 s). This is what the seedscan
sbatch array uses (`--cpus-per-task=32`).

**Ideal seedscan path:** sbatch array, one dedicated node per task.
*Not* parallel inside a shared interactive — serial-only on interactive
(1 trial at a time, 32+ threads). Whether 64 or 128 threads on a
dedicated single trial gives any gain over 32 is unmeasured; sklearn
HistGBT typically caps scaling at ~16–32 threads per fit, so don't
assume "more cores = faster" without a one-trial benchmark first.

Interactive 53194994 batch 1 (seeds 10 & 9) was killed at iter 2 of 5
after 33 min when this slowdown was confirmed. No ROOTs lost — sbatch
array 53192001_[5-10] still queued; same pinned seeds → identical
outputs when it dispatches. Tasks 53192001_[2-4] cancelled (those seeds
already on disk from pre-exit interactive batch).

## 2026-05-20 — Seedscan complete (n=10)

sbatch array 53192001 cleared overnight while priority opened up before
the 2026-05-20T06:00 UTC maintenance window. Per-task elapsed: 17m–18m
for tasks 1, 5, 6, 7, 8; task 9 took 22m59s (likely background-noise
neighbor on the dedicated node; identical pinned-seed output still); task
10 finished 03:18 UTC. All ten seed ROOTs on disk.

`analyze_seedscan.py` on n=10 (per-bin stats over the **205
paper-reported bins**; 19 paper-unreported cells dropped):

| Metric | Value |
|---|---|
| Total σ | 3.0728e-38 ± 2.2e-42 cm²/nucleon |
| **Total-σ rel spread** | **0.007%** |
| Per-bin median rel spread | **0.36%** |
| Per-bin p84 | 0.74% |
| Per-bin max | 1.87% |
| 1D pT / p∥ median rel spread | 0.13% / 0.15% |

Going n=4 → n=10 moved the headline numbers within rounding (0.008%
→ 0.007% total, 0.36% → 0.36% per-bin median), so the envelope is
converged. Comparison against the paper's reported uncertainty
(computed from the ancillary release total cov + per-bin
total_uncertainty column, both restricted to the 205 reported bins):

| Quantity                       | ML seedscan | Paper (ancillary) | ML / paper |
|--------------------------------|-------------|-------------------|-----------|
| Total σ rel uncertainty        | 0.007%      | 4.61%             | ~0.15%    |
| Per-bin median rel uncertainty | 0.36%       | 6.86%             | ~5%       |
| Per-bin p84 rel uncertainty    | 0.74%       | 9.16%             | ~8%       |

ML stochasticity is **subdominant** to the paper's reported uncertainty
on every comparison — not a leading uncertainty in this method.

Plots: `seedscan/seedscan_spread_2d.png` (rel-spread heatmap, no
strict-interior overlay), `seedscan_band_pt.png`, `seedscan_band_pz.png`.

## 2026-05-21 — 8-iter retargeted to HistGBT; working tree trimmed

**Exact-GBT 8-iter (53159240) cancelled at iter 3/8 after 15 h.** The
original sbatch was queued behind the 2026-05-20 maintenance reservation
and dispatched 2026-05-21 04:20 UTC; at the time of cancel it had
completed iters 0–2 with iter 3 in progress (~5 h/iter on the regular
QOS node, ETA ~25 h still to go). Cancelled now that HistGBT is
1:1-validated against exact (Task #16) so the long exact run is
redundant.

**`sbatch_unfold_2d_MEHFC_8iter.sh` rewritten** to HistGBT, seed=1, 32
CPU, 1 h walltime. Seed=1 matches `seedscan/...seed1.root` so the 5-iter
→ 8-iter delta is measured at fixed ML stochasticity (no estimator and
no random-seed confound).

**Dispatched into interactive 53256254** instead of sbatch, since the
interactive shell on `nid004147` was idle and the regular queue was
sitting on Priority. Invocation:
`srun --jobid=53256254 --overlap -n 1 --cpus-per-task=128 bash -lc '... --estimator hist --seed 1 --iters 8 ...'`.
Log: `unfold_MEHFC_8iter_interactive_20260521_130853.log`; output:
`2d_crossSection_omnifold_MEHFC_8iter.root` (writes on iter-8
completion). Start 20:08 UTC; HistGBT 5-iter at 32 CPU was 17m33s, so
the 128-thread 8-iter is expected ~20–25 min.

**Working-tree cleanup ahead of uncertainty work.** 93 → 66 entries in
`2d-unfolding/`:

- Deleted 16 completed slurm logs (`unfold_MEHFC_seed{1,5,6,7,8,9,10}_53192001.{out,err}`
  and `unfold_MEHFC_8iter_53159240.{out,err}`).
- Moved 1A iter-scan deliverable to `archive_pre_phase18/iter_scan_1A/`:
  the five `2d_crossSection_omnifold_1A_{1,3,5,8,10}iter.root` ROOTs,
  `1A_iterscan_convergence.png`, `sbatch_iter_scan_2d.sh`,
  `plot_iter_convergence.py`, and the `histgbt_iter_scan/` subdir.
- Moved `histgbt_smoke/` and `sbatch_unfold_2d_MEHFC_histgbt_smoke.sh`
  to `archive_pre_phase18/histgbt_smoke/`.
- Untouched: `runEventLoopOmniFold_MEHFC.root`, `baseline_flux/`,
  `seedscan/`, all current analysis scripts, and the production 5-iter
  MEHFC ROOT — i.e. everything the running 8-iter or the upcoming
  uncertainty pass needs.

**Next:** when 8-iter ROOT lands, diff vs `seedscan/...seed1.root` on
the 205 paper-reported bins (total σ shift, per-bin median ratio, χ²/ndf
vs paper). If the iter-count delta is small compared to the seedscan
envelope (0.007 % total, 0.36 % per-bin median), the convergence
question is closed and the analysis pivots to stat + systematic
uncertainties — bootstrap on the data for stat, MnvH2D vertical
universes from `runEventLoopOmniFold_MEHFC.root` for syst.
