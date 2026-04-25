# Third-Party Code and Data Notice

This repository contains original analysis code plus selected modified files
derived from upstream research software. The top-level MIT license applies to
the original code and documentation in this repository. It does not relicense
third-party code, third-party data, published-paper ancillary files, or
external software that must be obtained from its original source.

## MINERvA 101 and MINERvA Analysis Toolkit

Upstream projects:

- MINERvA 101 Cross Section Tutorial:
  <https://github.com/MinervaExpt/MINERvA-101-Cross-Section>
- MAT:
  <https://github.com/MinervaExpt/MAT>
- MAT-MINERvA:
  <https://github.com/MinervaExpt/MAT-MINERvA>
- GENIEXSecExtract:
  <https://github.com/MinervaExpt/GENIEXSecExtract>
- UnfoldUtils:
  <https://github.com/MinervaExpt/UnfoldUtils>

The local working tree may contain full upstream clones under `MINERvA101/`
for building and running the analysis, but the outer repository tracks only
selected modified files in `MINERvA101/MINERvA-101-Cross-Section/`.

License status checked locally:

- `MINERvA101/MAT/LICENSE`: MIT License, copyright MinervaExpt.
- `MINERvA101/MAT-MINERvA/LICENSE`: MIT License, copyright MinervaExpt.
- `MINERvA101/GENIEXSecExtract/LICENSE`: MIT License, copyright MINERvA
  Experiment.
- `MINERvA101/MINERvA-101-Cross-Section/`: no license file was present in
  this local checkout at the time this notice was written.
- `MINERvA101/UnfoldUtils/`: no license file was present in this local checkout
  at the time this notice was written.

## RooUnfold-Based unbinned_unfolding

Upstream project:

- rymilton/unbinned_unfolding:
  <https://github.com/rymilton/unbinned_unfolding>

The local working tree may contain the full upstream package under
`unbinned_unfolding/`, but the outer repository tracks only selected modified
files under `unbinned_unfolding/python/`.

No license file was present in this local checkout at the time this notice was
written. The upstream README requests citation of:

- R. Milton et al., "Tools for Unbinned Unfolding", JINST 20 P05034 (2025).

## Published Paper Ancillary Files

The files in `2d-unfolding/minerva_paper_anc/` are small text ancillary files
used to compare this analysis to the published MINERvA result. They should be
cited to the corresponding publication or public source rather than treated as
original code from this repository.

## Non-Redistributed Files

Large generated outputs, ROOT files, plots, logs, local paper PDFs, and full
upstream working trees are intentionally excluded by `.gitignore`. Recreate or
obtain them from their documented sources.
