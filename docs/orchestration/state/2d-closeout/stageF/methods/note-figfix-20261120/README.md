# Figure fixes for the rewrite (cov2d, 2026-11-20)

The director relayed two figure jobs from Joseph on 2026-11-20. Both are off the note branch, and no note text
changes here.
- **(b) Fig. 2** (`fig:xsec`, `MEFHC_5iter_xsec_proj_pt` / `_proj_pz`): done in this record. See below.
- **(a) fig:eavailWband** (`eavailW_band.pdf`): done in this record. It is redrawn from the repaired generator
  predictions, fetched on the director's go, with a generator/data ratio panel under each marginal. The installed
  figure had drawn pre-repair predictions, a defect in the current note as well. See "Item (a)" below.

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

## Item (a): fig:eavailWband from the repaired predictions, with ratio panels

**The defect found.** The installed `eavailW_band.pdf` drew pre-repair generator predictions, so it did not show what
its caption and the text state. RE1-REPORT §4 had recorded that it "does not reproduce from its stated inputs".
- **Its inputs.** It came from
  `overlay_eavailW_band.py --from-arrays note-figstyle-20261113/runs/family5/dumps/band_arrays.npz --print-style`.
  Those arrays were dumped on 2026-11-15 from `/pscratch/.../MINERvA-OmniFold/3d-unfolding/genie/*_xsec_eavailW.root`
  (sha256 b0161329…, 99a3ec76…, 86b3da58…, 2461bdfd…; `connect-family5.session.txt`).
- **The text's inputs.** The text, the caption claim and the article use the s5p stage-7 repaired, flux-corrected
  files (sha256 debaf83e…, 1098e912…, d7d46a0c…, b430ddc6…; the release `fig_arrays.npz.manifest.json`).
- **The data.** Both use the same data, `excess_eavail_W.root` 751bb859.
- **What disagreed.** From the old arrays:
  - corner data/generator was 1.535, 1.579, 1.563 and 1.609, where the text prints 1.14, 1.14, 1.16 and 1.61;
  - at 1.4 ≤ W < 1.8 GeV, GENIE CV and GENIE + MEC were 7.8 % and 7.2 % above the data, where the caption claims
    9–12 %.

**The fetch** (the director's go of 2026-11-21, window to 2026-11-21T02:48:52Z):
- **Scope.** Exactly the four files
  `/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/stage7/genfig/3d-unfolding/genie/{genie_cv,genie_mec,nuwro_cv,gibuu_cv}_xsec_eavailW.root`.
- **Fence.** tier3-design acked at 01:19:09Z that none of its jobs or holds touch the path. My own fence check found
  no cluster process.
- **How.** One `ssh -o ControlPath=none saul.nersc.gov 'python3 -'`, with the reader on stdin (`runs/eavailw/
  remote_read.py`). It read each file with O_NOATIME and printed it. Nothing was written on the cluster, and nothing
  was computed there. <!-- absence-ok: describes this fetch's own procedure (a stdin reader that only prints), not a result -->

- **Result.** ssh rc 0 at 01:19:53Z on login38. Each file's atime was unchanged.
- **Verification.** Each local copy's sha256 equals its line in the committed
  `state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt`. The copies are committed in `runs/eavailw/inputs/`, with
  the fetch record in `runs/eavailw/fetch.json` and `connect.sh`.

**The producer.** `tools/make_fig_eavailW_ratio.py` runs in figenv/rootmpl3108, because PyROOT reads the four files.
- **Data.** `data2d` from `band_arrays.npz`, whose generator arrays are not read. The producer requires the npz's
  sha256 to equal the family5 run's `out/band_arrays.npz` line, and that run's data input line to name 751bb859.
- **Generators.** `hXSec_eavailW` from the four committed files, each held to the archive's sha256, on axes equal
  to the analysis edges.
- **Marginals.** Computed as `overlay_eavailW_band.py` computes them, drawn without the catch bins as before.

**Checks before drawing.** The producer refuses on any failure, and every check passed.
1. Against the repaired run's committed log (`state/s5p/stage7/generator-context/eavailW_band_s5p_repaired-log.txt`),
   at its printed precision:
   - each generator's line is reproduced exactly (total, data total, ratio, corner sums, corner data/gen 1.142, 1.139,
     1.160 and 1.607);
   - all 6 rows of its dσ/dW table are reproduced.
2. Against `values.tex`: `\genieWmidLo` = 9 and `\genieWmidHi` = 12 are the min and max of GENIE CV (+9.39 %) and
   GENIE + MEC (+11.79 %) above the data at 1.4 ≤ W < 1.8 GeV, within half a printed unit.
3. The data: the 751bb859 provenance chain holds, and the data totals and W table match the log under check 1.

After drawing, every stairs, point and ratio read back from the artists equals the computed values, and no font is
under 7 pt.

**The figure.**
- E_avail (left) and W (right) marginals, each with a generator/data ratio panel underneath, in Fig. 2's layout:
  linear upper panels in 10⁻³⁸ cm²/GeV/nucleon, and a dashed line at 1 in the ratio panels.
- Same series, labels, colours and markers as the installed figure. Central values only: no uncertainty is drawn,
  as before.
- The upper panels are now linear from zero, where they were log scale over three decades. Their units are in the
  axis labels.
- The caption is unchanged here. It still holds: GENIE and NuWro are now the flux-corrected predictions it names.
  Pass 2 may describe the ratio panels.

**Outputs.**
- `docs/analysis-note/figures/eavailW_band.pdf`, which replaces the installed file. It has no creation date, and two
  runs give byte-identical PDF and values files.
- `runs/eavailw/eavailW_band_values.json`: every plotted number, the inputs' digests and the checks.
- `runs/eavailw/CHECKS.txt`.
