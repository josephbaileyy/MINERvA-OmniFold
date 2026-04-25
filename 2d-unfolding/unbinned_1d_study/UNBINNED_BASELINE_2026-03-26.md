# Unbinned baseline freeze note (2026-03-26)

## Purpose

This file freezes the current unbinned `pTmu` workflow so the binned OmniFold study can become the active campaign without losing the ability to return to the unbinned pipeline later.

The top-level `Documents/` unbinned files should now be treated as the read-only baseline unless a future task explicitly resumes the unbinned campaign.

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
python3 Documents/plot_gaussian_style_ptmu_unbinned.py   --omnifold Documents/pTmu_crossSection_omnifold.root   --ibu Documents/pTmu_crossSection_clean.root   --outpdf Documents/ptmu_gaussian_style_unbinned.pdf   --outpng Documents/ptmu_gaussian_style_unbinned.png
```

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
