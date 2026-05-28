# Unbinned baseline freeze note (2026-03-26)

## SUPERSEDED — 2026-04-30 → REVALIDATED 2026-05-02 → PHASE-16 PATCHED 2026-05-10

**Do not quote results from the frozen 2026-03-26 ROOT files against the
paper.** The 2D campaign uncovered bugs that were also present in the 1D
unbinned path, and the frozen outputs additionally predate the
`IsMinosMatchMuon` patch. The current valid baseline lives in
`2d-unfolding/unbinned_1d_study/` (post-patch, regenerated 2026-05-02);
see "Revalidated baseline" below.

Issues that invalidated the frozen 1D outputs:

1. **Pre-MINOS-fix event loop.** Frozen ROOT files were generated before
   the 2026-04-25 `CVUniverse.h:107` patch; selection used the educational
   stub (`has_interaction_vertex==1`), so the background fraction is ~10 %
   instead of the paper's ~0.2 %.
2. **No measured-side background subtraction inside OmniFold.** Step-1
   measured input was the raw data array with unit weights; `data − bkg`
   was only used for a downstream histogram rescale.
3. **Signal fakes leaked.** `omnifold.py` drops `~pass_truth` events from
   MCreco before training, but fakes remained in measured. The 2D contract
   adds fake reco yields into `hBkgReco` so both sides are fake-free — the
   1D path did not.
4. **`hUnfold` was filled with raw `step2_weights`** (a truth-side density
   ratio) instead of `step2_weights * truth_w_in` (event-count units).
5. **No phase-space mask on the measured array** — only `measured_pass`
   and a generic `|pT|<1e3` guard.

`unfold_ptmu_omnifold_unbinned.py` was patched on 2026-04-30 to apply all
five fixes (mask measured to `[pt_lo, pt_hi]`; add fakes into bkg; build
per-event `measured_weights = max(0, data−bkg)/data`; call
`ohf.omnifold(...)` directly with those weights; fill `hUnfold` with
`step2 * truth_w`). The historical `RooUnfoldOmnifold().UnbinnedOmnifold()`
wrapper call was replaced with the same direct helper used in the 2D path.

## Revalidated baseline (2026-05-02, playlist 1A)

SLURM job 52271486 (`sbatch_unfold_1d_unbinned_1A.sh`) reran the full
patched-vs-patched pipeline on playlist 1A. OmniFold + binned event loops
+ unfold + IBU all completed; only the comparison-plot step had to be
rerun by hand because of two unrelated nuisances (now fixed in the
sbatch + plot defaults):

- `ExtractCrossSection` segfaults inside ROOT's `TFile::Close()` exit
  handler **after** writing all outputs (the file is recoverable; 4
  MnvH1D keys present). The sbatch now wraps step 4 with `|| true` and
  gates on `test -s pTmu_crossSection.root` instead of the binary's
  exit code.
- The binary writes `pTmu_crossSection.root`, not the
  `pTmu_crossSection_clean.root` name carried over from the old
  freeze-doc convention. Both the sbatch and `plot_gaussian_style_ptmu_unbinned.py`
  default `--ibu` now use the actual filename.

Current valid 1D unbinned outputs (live in
`2d-unfolding/unbinned_1d_study/`, **not** in the legacy `Documents/`
folder):

- `runEventLoopOmniFold.root`, `runEventLoopData.root`, `runEventLoopMC.root`
  (post-MINOS-fix selections; signal fakes folded into `hBkgReco`)
- `pTmu_crossSection_omnifold.root` (patched 1D unbinned OmniFold,
  5 iterations, `--use-weights`)
- `pTmu_crossSection.root` (D'Agostini IBU on the same patched selection;
  4 MnvH1D keys recovered after the ROOT exit-handler segfault:
  `backgroundSubtracted`, `unfolded`, `crossSection`, `simulatedCrossSection`.
  The plot script reads `crossSection`)
- `pTmu_*.png` (24 stock MINERvA IBU diagnostic plots from
  ExtractCrossSection: data, BackgroundSum, backgroundSubtracted,
  unfolded, efficiency, efficiencyCorrected, crossSection,
  simulatedCrossSection — each plus `_uncertaintySummary` and
  `_otherUncertainties` variants)
- `ptmu_gaussian_style_unbinned.pdf` and `.png` (eff-corrected
  comparison plot; legend entry "Reco data (bkg sub)" is the
  background-subtracted reco data, "IBU (MINERvA, eff-corr) stat"
  is the efficiency-corrected IBU result derived from `crossSection`,
  "OmniFold (unbinned)" is `hUnfoldTruthSel`)

OmniFold-vs-IBU comparison is now done in **efficiency-corrected truth
space**. Earlier the comparison plot read IBU's `unfolded` MnvH1D, which
is **pre-efficiency-correction** (data-yield in truth bins) — but
OmniFold's `hUnfoldTruthSel` is **post-efficiency-correction** (the
step-2 weights × truth_w_in inherently absorb the response and bring you
to truth space). Dividing both by `hTruthSel` then produced an
OF/IBU ratio that visually looked like "OmniFold = scaled IBU" — that
"scale" was just `1/efficiency(pT)`, the muon-tracker acceptance curve
(min ~0.77 in the QE region, ~1.0 at edges).

Fix (2026-05-02): `plot_gaussian_style_ptmu_unbinned.py` now reads IBU's
`crossSection` MnvH1D (which encodes `efficiencyCorrected / flux /
nucleons / dpt`) and multiplies bin-by-bin by binwidth so the units
match the per-bin event-yield convention used by every other histogram
in the plot.

Phase-16 follow-up (2026-05-10): the 1D unbinned OmniFold pipeline had
the same input-completeness bug found in the 2D unfold
(`2D_OMNIFOLD_RUN_LOG.md` Phase 16). `unfold_ptmu_omnifold_unbinned.py`
read `mc_signal_reco` only — never `mc_truth_denom` — so the
efficiency-corrected unfold lived on the OmniFold-input truth subset
(2.05M events) rather than the canonical truth phase space (2.68M).
Effect: OmniFold low by c ≈ 0.77 globally for 1A. IBU was unaffected
because `ExtractCrossSection` consumes the binned event loop's
canonical hEffDen.

Patch (2026-05-10):
- Added `collect_truth_denom_arrays` in `unfold_ptmu_omnifold_unbinned.py`,
  reading `mc_truth_denom` directly with the same conventions as the
  2D path's `collect_truth_denom_arrays`.
- New histograms in the unfold output: `hOFTruthDenom`,
  `hOFCompleteness = hTruthSel / hOFTruthDenom`, and
  `hUnfoldTruthSel_completeness_corrected = hUnfoldTruthSel /
  hOFCompleteness`. The original `hUnfoldTruthSel` is preserved for
  diff-checking against the historical artifact.
- `plot_gaussian_style_ptmu_unbinned.py` prefers the corrected
  histogram, falling back to the bare `hUnfoldTruthSel` with a warning
  for pre-Phase-16 inputs.

Sanity log from the patched 2026-05-10 unfold (1A, iters=5,
`--use-weights`):
- `mc_truth_denom` kept = 2,682,267 (matches the unbinned event loop)
- `mc_signal_reco` truth-pass kept = 2,048,993
- `hTruthSel` integral = 3.750e5; `hOFTruthDenom` integral = 4.863e5
  → global completeness c = **0.7712** (1A nominally similar to MEFHC's
  0.7503; matches 2.05M / 2.68M = 0.764 raw to ~1 %)
- `hUnfoldTruthSel` (pre-correction) = 4.223e5
- `hUnfoldTruthSel_completeness_corrected` = 5.501e5 (ratio post/pre
  = 1.303 = 1/c, exactly as expected)
- `signal fakes added to bkg = 6`, `data-bkg/unfolded ≈ 0.847`

In the post-Phase-16 comparison plot (`ptmu_gaussian_style_unbinned.png`),
both OmniFold and IBU sit on the canonical truth phase space — IBU via
runEventLoop's hEffDen, OmniFold via the per-bin completeness divide.
Density-normalized, the two unfolders now overlap exactly in the ratio
panel, with the same 0.78 → 1.17 → 1.0 ramp vs local MC truth across
p_T. That shape is the data/MC residual, not a method or pipeline
artifact, and matches what the 2D campaign sees on the same playlist.
**No bug in the unfolder**; the residual ratio shape is genuine
data/MC-truth disagreement.

The legacy `Documents/` 2026-03-26 ROOTs are kept as historical
diagnostic state only — do not regenerate from them and do not compare
them against the paper.

## Purpose (historical)

This file froze the unbinned `pTmu` workflow so the binned OmniFold study
could become the active campaign without losing the ability to return to
the unbinned pipeline later.

The top-level `Documents/` unbinned files were treated as the read-only
baseline. They are now archived state and must be regenerated before reuse.

## Frozen file manifest

### Unbinned scripts and documentation
- `Documents/unfold_ptmu_omnifold_unbinned.py`
- `Documents/plot_gaussian_style_ptmu_unbinned.py`
- `Documents/ptmu_closure_iteration_study.py`
- `Documents/PTMU_CLOSURE_ITERATION_STUDY.md`
- `Documents/Physics_191_PRL.pdf`

### Current top-level ROOT outputs and figures
- `Documents/runEventLoopOmniFold.root`
- `Documents/runEventLoopData.root`
- `Documents/runEventLoopMC.root`
- `Documents/pTmu_crossSection_omnifold.root`
- `Documents/pTmu_crossSection_clean.root`
- `Documents/ptmu_gaussian_style_unbinned.pdf`
- `Documents/ptmu_gaussian_style_unbinned.png`

## Canonical commands to resume later

**Note (2026-05-02):** The commands below operated on the legacy
`Documents/` paths and are kept for historical reference only. To run
the **current revalidated pipeline**, use the sbatch script in this
directory:
```bash
sbatch 2d-unfolding/unbinned_1d_study/sbatch_unfold_1d_unbinned_1A.sh
```
or the equivalent step-by-step quick-start in the top-level `AGENTS.md`
section "1D unbinned baseline (revalidated 2026-05-02)". Read those
before running anything below.

### Rebuild OmniFold inputs
```bash
runEventLoopOmniFold Doc_tmp/1A_Data.txt Doc_tmp/1A_MC.txt
```

### Rebuild baseline MINERvA inputs
```bash
runEventLoop Doc_tmp/1A_Data.txt Doc_tmp/1A_MC.txt
```

### Run production unbinned OmniFold
```bash
python3 Documents/unfold_ptmu_omnifold_unbinned.py   --omnifile Documents/runEventLoopOmniFold.root   --datafile Documents/runEventLoopData.root   --datahist pTmu_data   --iters 5   --use-weights   --verbose   --out Documents/pTmu_crossSection_omnifold.root
```

### Rebuild the baseline MINERvA cross section
```bash
ExtractCrossSection 5 Documents/runEventLoopData.root Documents/runEventLoopMC.root
```

### Rebuild the unbinned comparison plot
```bash
python3 Documents/plot_gaussian_style_ptmu_unbinned.py   --omnifold Documents/pTmu_crossSection_omnifold.root   --ibu Documents/pTmu_crossSection.root   --outpdf Documents/ptmu_gaussian_style_unbinned.pdf   --outpng Documents/ptmu_gaussian_style_unbinned.png
```
*(Note: pre-2026-05-02 versions used `pTmu_crossSection_clean.root` and
read IBU's `unfolded` histogram. The script now defaults to
`pTmu_crossSection.root` and reads the `crossSection` MnvH1D for
apples-to-apples efficiency-corrected comparison.)*

### Resume the closure and iteration study
```bash
python3 Documents/ptmu_closure_iteration_study.py   --omnifile Documents/runEventLoopOmniFold.root   --datafile Documents/runEventLoopData.root   --datahist pTmu_data   --iterations 1,2,3,4,5,6,7,8   --train-split even   --stress-mode nominal   --tag nominal
```

## Frozen scope and current meaning
- This baseline captures the **production unbinned OmniFold path**.
- The closure script currently implements a **signal-only split-sample closure test in event-count units**.
- The top-level unbinned files are preserved so the study can later return to:
  - stressed closure runs
  - iteration-choice justification for the unbinned path
  - measured-side background-subtraction extensions
  - uncertainty-propagation extensions
  - direct binned vs unbinned comparison once the binned campaign is understood

## Resume here later

When the binned campaign is complete enough to compare methods again, start by checking:
- whether the binned workflow can reproduce and then explain the historical normalization failure
- whether the binned path becomes useful for uncertainty studies even if it still needs physics validation
- whether the unbinned closure study should be extended beyond signal-only event-count tests

Until that handoff happens, the active day-to-day campaign is the binned study tracked in `Documents/BINNED_PTmu_STUDY_STATUS.md`.
