# Stepped series on their bin edges: Fig. 5 fixed, every printed figure surveyed

The director's job of 2026-11-21, on the draft at e89694209:
- Fig. 5's marginals go on their real bin edges, with full-width end bins and ticks at the edges, checked with an edge
  check as for Fig. 2.
- Every other installed figure is checked for the same pattern: step(where="mid") over bin indices, or steps over
  centres.
- Fig. 2's "Published (PRD 104, 092007)" series is drawn steps-mid, and figfix's check_edges passed it. The director
  asked why.

## Fig. 5 (fig:q3excess)

- **Before:** the lower panels drew `step(range(n), r, where="mid")`, with ticks at the bin indices labelled by each
  bin's low edge.
  - Each tick sat at the centre of its bin's level, not at its left end.
  - The first and last bins were drawn half width.
- **The tool:** `tools/compose_q3_steps.py` runs the installed recipe, `note-q3fig-20261121/tools/compose_q3_labels.py`
  on the unchanged producer. compose_q3_labels' own edits and checks run first. Then:
  - Each bin i spans [i, i+1]. The line is redrawn steps-post through x = 0..n, with the last value repeated. The
    values are the drawn ones; nothing is recomputed.
  - The ticks are at 0..n. They read the n+1 bin edges from the producer's own arrays (`q3_e`, `ea_e` in
    `q3_arrays.npz`), formatted %.1f as the map's tick labels are.
  - The x labels lose ", low edge".
  - **Bin widths:** each bin keeps equal display width, as the map above does. The catch bins end at 100 GeV, so a
    physical axis would squeeze the other six bins into a few per cent of the panel.
  - **The E_avail panel:** its last label "100.0" crossed the canvas's right edge, so the panel is narrowed from the
    right by 0.1388 in. Its left edge stays fixed. The tool stops if any text lies outside the canvas.
- **The edge check** (`tools/edges.py`, below) fails before the fix on each panel's stepped line, and on ticks not at
  the edges. It passes after on both panels, ticks included.

### Checks (`runs/q3/CHECKS.txt`; `bash tools/run_q3_steps.sh <worktree> e89694209`, then INSTALL=1)

- **Arm 0** (the installed recipe) against docs/analysis-note/figures/q3_excess_projection.pdf at e89694209:
  EQUAL-BUT-DATE, 0 px.
- **Arm 1 against arm 0, captures:**
  - same 7 items in the same order;
  - only the two stepped lines (items 1 and 3) differ, in their drawing only: steps-mid x 0..6 becomes steps-post
    x 0..7, y is equal on all 7 bins, and the colours and line style are equal;
  - the map image, its colour scale and the reference lines are unchanged.
- **Strings:** arm 1 has 89, arm 0 87. The difference is the two x labels without ", low edge", plus each panel's
  last edge "100.0". Smallest font 7.0 pt; 0 text overlaps in the PDF.
- **Installed:** docs/analysis-note/figures/q3_excess_projection.pdf is arm 1's PDF, sha256 9fdd0f1c… (CHECKS.txt
  gives the full digest).
- **Caption:** no change needed. It names the panels ("Lower left and right show the q3 and E_avail marginals") and
  never mentions low edges.

## Why figfix's check_edges passed the "Published" series in Fig. 2

It passed correctly: that series draws no steps.
- The capture shows the series has linestyle "None", marker "s" and drawstyle "steps-mid". It is a marker-only line.
- In matplotlib 3.10.8, with no line style, a steps drawstyle draws nothing. The markers go on the data points
  whatever the drawstyle.
  - Measured through a renderer hook on `RendererPdf.draw_markers`: markers at x = [1, 4, 9] for data x = [1, 4, 9],
    with linestyle "None" or "-".
- In Fig. 2 those points are at the bin centres, which is right for published points.
- check_edges applies the step test only to lines with a visible line style. It tests other lines' points against the
  edges and centres, so this series passed.

The defect was in my first survey, which listed every line with a steps drawstyle whatever its line style. The
survey now lists only visible stepped lines.

The check is also tightened, in `tools/edges.py`, the general version used here (no compose_tier2 dependency):
- a marker-only line's points must be at the bin centres (figfix accepted edges or centres);
- a stepped line is judged by the path matplotlib draws (`STEP_LOOKUP_MAP`), not by its data;
- ticks can be checked against the edges and their labels.

Figfix's committed tool is not changed; its record stays as it ran.

## The survey (`tools/survey_steps.py`; `runs/survey/included.txt`, `runs/survey/all-captured.txt`)

**Method.**
- Take the 52 figure stems the note's .tex files include (commented-out lines counted too), and, with --all, every
  stem captured anywhere in the records (34).
- For each, the latest committed capture lists every visible stepped line with its x.
- The survey ran against the index at e89694209, before this lane's captures were tracked.
- For the 25 included figures with no capture, the producers were read by hand (grep for `.step(`, `steps-`,
  `drawstyle`, `where="mid"`, then the code).

| figure (printed in) | pattern | state |
|---|---|---|
| q3_excess_projection, Fig. 5 (note) | step(where="mid") over bin indices, both marginals | **fixed here** |
| MEFHC_5iter_xsec_proj_pt / _pz, Fig. 2 (note) | "Tune v1: published prediction" steps-mid over centres | fixed in note-figfix-20261120 (merged); the survey's capture predates it |
| pet_vs_gbdt (PET note, sec_pet) | `step(c, y, where="mid")` over the centres of unequal 4D edges (nd-unfolding/pet/pet_vs_gbdt.py:207-208) | **open**: inputs not on the laptop |
| pet_cloud_projection_xsec (PET note) | `step(range(n), ..., where="mid")` over bin indices, E_avail and W panels (nd-unfolding/pet/pointcloud_projection.py:357-376) | **open**: inputs not on the laptop |
| pet_cardinality_withremnant (PET note) | `step(x, f, where="mid")` over integer cardinalities 0..P (plot_event_displays.py:112-114). Centring on integer values is right for a discrete variable, but the first and last values are drawn half width | **open** (end bins only): inputs not on the laptop |
| excess_eavail_W, left panel | step over indices (excess_eavail_W.py:186-187) | not printed: the primer's paper_joint_localization crops the file to its two maps (make_figures.sh, pdfcrop --bbox '400 0 1152 331.2') |
| model_comp_projections | Tune v1 steps-mid over centres | not printed: folded into Fig. 2 (DECISION-20261119b) |

**Checked and clean.** Every other included figure:
- the captured ones have no visible stepped line;
- the uncaptured producers draw no steps, or draw them on edges: make_figs.py `stairs(…, edges)`, and
  plot_joint_null_distributions_physlabels.py `hist(bins=…, histtype="stepfilled")`;
- nn_vs_gbdt_full draws points joined by lines at the centres, not steps.

**The three open PET figures.**
- Their inputs are not on the laptop: of_inputs_pc*.npz, pet_weights*.npz, products/4d/xsec_4d_MEFHC_5iter_lgbm.root
  and runEventLoopOmniFold_PC_MEFHC_fullcloud.root.
- Redrawing them needs a cluster read of those inputs, or a `--dump-arrays`-style run of each producer. That is a
  go for the director.
- They are not redrawn from their PDFs, which would give values only to drawing precision.
