# Binned study run layout

Use one directory per executed study run under `Documents/binned_study/runs/`:

- `runs/YYYY-MM-DD_label/`

Each run directory should contain at minimum:

- `command.txt`
  - exact command line used
- `summary.md`
  - short run summary with toggles, normalization checks, and verdict
- `stdout.log`
  - terminal output if captured
- `outputs/`
  - ROOT files and plots from that run

Required summary fields:

- iteration count
- engine choice
- weight mode choices
- key integrals: `hDataReco`, `hBkgReco`, `hMeasSub`, `hTruthSel`, unfolded
- `response.Htruth()` and `response.Hmeasured()` checks
- ratio of `data-bkg` to response measured
- ratio of `data-bkg` to unfolded
- verdict: `reproduced old failure`, `changed behavior`, `promising`, or `invalid run`

Keep the run directories append-only so the study history remains auditable.
