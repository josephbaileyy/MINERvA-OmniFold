# Figure fixes for the rewrite (cov2d, 2026-11-20)

The director relayed two figure jobs from Joseph on 2026-11-20. Both are off the note branch, and no note text
changes here.
- **(b) Fig. 2** (`fig:xsec`, `MEFHC_5iter_xsec_proj_pt` / `_proj_pz`): done in this record. See below.
- **(a) fig:eavailWband**: not done yet. A ratio panel would show that the installed figure draws stale generator
  inputs. The finding is under "Item (a)" below.

## Item (b): Fig. 2's published Tune v1 prediction on the projection's edges

**The fault.**
- `note-figpass-20261119/tools/compose_tier2.py` adds Fig. 13's "Tune v1: published prediction" line to the
  projections as drawn.
- That line is `compare_to_models.py`'s `ax.step(ctr, y, where="mid")` through the bin centres.
- With unequal bins, a mid-step changes value half-way between neighbouring centres, not at the bin edges. It also
  starts and ends at the first and last centres.
- So the dashed steps did not line up with the bins. In p_T, the step between the 2.0 and 3.5 centres changed at 2.75,
  where the bin edge is 2.5.
- The values are the published ancillary prediction, one per projection bin. They are unchanged.

**The fix.** `tools/compose_fig2_edges.py` runs `compose_tier2.py` unchanged. Only its final save is wrapped, as
`compose_slices_markers.py` wraps it. For each projection:
1. It reads the projection's edges from its own prior histogram (the StepPatch that `plot_2d_cross_section.py` draws
   on the result's binning).
2. It runs the new edge check, `check_edges`, on the figure as composed. The check must fail there, on the
   published-prediction line only, or the run stops. So the check is shown to detect the fault.
3. It redraws that line, keeping its object, style, label, z-order and values, as `steps-post` on the edges.
   Before the change, the line must hold one value per bin centre.
4. It runs `check_edges` again on both axes (the upper panel and the ratio). The check must pass.

`check_edges` requires every data series in the axes to share the projection's edges:
- StepPatches have exactly the edges.
- Errorbar points sit at the centres, with half-bin x half-widths.
- Lines drawn as steps change value and end exactly on the edges.
- Other lines and markers sit on edges or centres.

**Recipe.**
- Run as chunk B and the markers run did: `capture_palette.py <capture> note-figstyle-20261117/tools/remap_anc.py
  <anc> tools/compose_fig2_edges.py <xsec.root> <anc> <out>`.
- Environment: `figenv/rootmpl3108` (ROOT 6.40.04, matplotlib 3.10.8, numpy 1.26.4), with BLAS threads 1.
- Inputs: the read-only fetch of 2026-11-17 (`xsec.root` a5c13fc3 and `cov_ptpl_minerva_inclusive_6GeV.root`
  6c6dce72).

**Checks** (`runs/fig2/CHECKS.txt`, `tools/check_fig2_edges.py`, `runs/fig2/compose_fig2_edges.json`):
CHECK-FIG2-EDGES :: PASS.
- Arm 0 (`compose_tier2.py` unchanged) reproduces the installed projections. The PDFs are EQUAL-BUT-DATE, and its
  capture hashes equal the committed `note-figpass-20261119/runs/markers/capture/arm1` hashes (18 items each).
- In arm 1, 17 of 18 items per figure are equal to arm 0's. The one that differs is the published-prediction line, and
  only in its drawing:
  - its drawstyle goes from steps-mid to steps-post;
  - its x goes from the 14 (p_T) or 16 (p_par) bin centres to the 15 or 17 edges;
  - its y is equal on every bin, with the last value repeated (the post-step convention);
  - its colours are equal.
- Every drawn string and font size is equal.
- The edge check fails before the fix on that line only, and passes after on both axes of both figures.

**Installed.** `docs/analysis-note/figures/MEFHC_5iter_xsec_proj_pt.pdf` and `_proj_pz.pdf` are arm 1's outputs.
Their digests are in CHECKS.txt; the PDFs carry a creation date, as the installed ones did. The slice figures from
this run are not installed: the markers run's versions stay.

## Item (a): fig:eavailWband draws pre-repair generator predictions (not yet redrawn)

The text and caption claims do not hold for the arrays the installed figure draws. A ratio panel made from those
arrays would show the mismatch, so the figure was not redrawn.
- **The installed figure's inputs.** The figure is `eavailW_band.pdf`
  (`overlay_eavailW_band.py --from-arrays note-figstyle-20261113/runs/family5/dumps/band_arrays.npz --print-style`).
  Its arrays were dumped on 2026-11-15 from
  `/pscratch/.../MINERvA-OmniFold/3d-unfolding/genie/{genie_cv,genie_mec,nuwro_cv,gibuu_cv}_xsec_eavailW.root`
  (sha256 b0161329…, 99a3ec76…, 86b3da58…, 2461bdfd…; `note-figstyle-20261113/runs/family5/connect-family5.session.txt`).
- **The text's inputs.** The text, the caption claim and the article use the s5p stage-7 repaired, flux-corrected
  predictions, `s5p-20260926/stage7/genfig/3d-unfolding/genie/*_xsec_eavailW.root`
  (sha256 debaf83e…, 1098e912…, d7d46a0c…, b430ddc6…; `publication/release/figs/_data/fig_arrays.npz.manifest.json`;
  `state/s5p/stage7/generator-context/`).
- **The data.** Both use the same data, `excess_eavail_W.root` 751bb859. The dumped data equal the repaired run's
  totals and every W-marginal bin (`state/s5p/stage7/generator-context/eavailW_band_s5p_repaired-log.txt`).
- **What disagrees.** From the dumped arrays:
  - the high-E_avail, high-W corner gives data/generator 1.535, 1.579, 1.563 and 1.609, where the text prints 1.14,
    1.14, 1.16 and 1.61;
  - at 1.4 ≤ W < 1.8 GeV, GENIE CV/data − 1 = 7.8 % and GENIE + MEC/data − 1 = 7.2 %, where the caption's claim is
    9–12 %.
  The repaired run's log gives the printed numbers: corner 1.142, 1.139, 1.160 and 1.607, and W-bin ratios 1.094 and
  1.118.
- **Background.** This is the gap that `RE1-REPORT.md` §4 recorded: "the committed eavailW_band.pdf does not reproduce
  from its stated inputs".
- **Next step.** Draw the figure, ratio panels included, from the repaired files. They are archived on CFS
  (`/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/stage7/genfig/3d-unfolding/genie/`, sha256 pinned in
  `state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt`). Fetching them is a connect, so it needs the director's go.
