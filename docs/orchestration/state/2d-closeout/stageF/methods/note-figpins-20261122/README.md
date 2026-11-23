# Figure pins, 2026-11-22: make_figures.sh reinstalls the figures the note prints

**Why.** The figure rounds of 2026-11-20/21 (note-figround-20261121, note-figround3-20261121, note-fig18-20261121)
installed their outputs straight into `docs/analysis-note/figures/` and recorded each installed sha256 in their
`runs/*/CHECKS.txt`. They did not update `make_figures.sh` (note-figround3-20261121/README.md defers it "for the
structural rewiring at the end"), so 12 live install lines still pinned the earlier draws: a rerun would have
reinstalled them over the figures the note prints. This record is that rewiring (the director's build_all pass,
rewrite into main, phase 1).

**What.** `figs/` holds a byte-identical copy of each of the 12 figures as committed in `docs/analysis-note/figures/`
at the integration branch (`figs/SHA256SUMS`). Each sha256 is the one its round's CHECKS file records as installed
(checked when the copy was made). `make_figures.sh` installs them with `install_current_fig`, after every earlier
install line, and each superseded earlier line is kept as a comment that points here. Nothing is redrawn: the
producers are the rounds' tools, named in their READMEs; this copy only lets a rerun reproduce their installed output.

| figure | sha256 (16) | installed by | record |
|---|---|---|---|
| `MEFHC_5iter_pull_full.pdf` | `9335a3e3037320c6` | `434fc800b` | `note-figround3-20261121/runs/fig3/CHECKS.txt` |
| `MEFHC_5iter_xsec_proj_pt.pdf` | `d27075c220081054` | `434fc800b` | `note-figround3-20261121/runs/fig2/CHECKS.txt` |
| `MEFHC_5iter_xsec_proj_pz.pdf` | `caa9286bfec8e7f2` | `434fc800b` | `note-figround3-20261121/runs/fig2/CHECKS.txt` |
| `generators_vs_unfolded_band_central.pdf` | `d030980eeba9ce29` | `e8225b2dd` | `note-fig18-20261121/runs/fig18/CHECKS.txt` |
| `MEFHC_5iter_xsec_paper_pt_slices.pdf` | `58e4d16ad6bc68f7` | `2a87ab740` | `note-figround-20261121/runs/stamp/CHECKS.txt` |
| `MEFHC_5iter_xsec_paper_pz_slices.pdf` | `4216003cfe47d376` | `2a87ab740` | `note-figround-20261121/runs/stamp/CHECKS.txt` |
| `control_corner.pdf` | `f077a7a9cb052cdc` | `2a87ab740` | `note-figround-20261121/runs/stamp/CHECKS.txt` |
| `control_plots.pdf` | `8910181e147c3251` | `2a87ab740` | `note-figround-20261121/runs/stamp/CHECKS.txt` |
| `eavailW_band.pdf` | `9e71e49361259663` | `2a87ab740` | `note-figround-20261121/runs/stamp/CHECKS.txt` |
| `eavail_marginal_vs_paper_pull_full.pdf` | `7f272d2639db72b2` | `2a87ab740` | `note-figround-20261121/runs/stamp/CHECKS.txt` |
| `mode_decomp_mec_eavail_central.pdf` | `b56f4d90b1047b8a` | `2a87ab740` | `note-figround-20261121/runs/stamp/CHECKS.txt` |
| `q3_excess_projection.pdf` | `2c836ace97c0c36d` | `2a87ab740` | `note-figround-20261121/runs/stamp/CHECKS.txt` |

`generators_vs_unfolded_band_central.pdf` was installed twice: by the stamp strip (7ea16ffd, note-figround-20261121)
and then by the Fig. 18 round (d030980e), which is the file committed now.

**Crops.** `make_figures.sh`'s absolute crops `paper_validation_residual.pdf` (of `MEFHC_5iter_pull_full.pdf`) and
`paper_eavailW_generators.pdf` (of `eavailW_band.pdf`) are no longer regenerated: no build includes either (the short
paper that did was retired on 2026-11-21), and the round-3 crop of `MEFHC_5iter_pull_full.pdf` (292.9 x 130.0 pt)
no longer has the canvas the crop's page-size guard requires (327.6 x 165.6 pt). Their committed files are unchanged.
`paper_joint_localization.pdf`, which the primer includes, is still cropped, with its guard.
