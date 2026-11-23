# Note figure redraw (2026-11-23): Figs. 7, 8, 9, presentation only

**Requested** as a delegated task on branch `rh/figs-b4-s3-20261123` (cut from origin/main b9d9962f7, plus 13f9d6a5b; a peer
commit ca639f8b9 landed on the branch during the work and touches only `sec3_twod.tex`).
**Scope:** presentation only. Every plotted value stays bit-equal. Nothing is installed: no `.tex`, no
`docs/analysis-note/figures/`, no `make_figures.sh`, no registry changes. Nothing was committed.
**Status (round 4, 2026-11-23):** the reviewer chose 7 D, 8 D and 9 R. Each is polished as Joseph asked and saved as
variant P in `figs/variants/<name>_P.{pdf,png}` (see "Round 4" below). All three are drawn and checked. Round 3's R and D
files and round 2's `figs/*.pdf` are unchanged. Nothing is installed, and the captions still need edits.

| note figure | label | installed file (sha256) | redrawn file (sha256) |
|---|---|---|---|
| 7 | fig:bkg-residual-note | paper_fig_bkg_residual.pdf (1c673272…) | figs/paper_fig_bkg_residual.pdf (a44a8562…, with the post-round-2 legend names; 4d0823e8… before them; round 1 433f7802…) |
| 8 | fig:coverage-5d-paper | paper_fig_coverage.pdf (e1c3a180…) | figs/paper_fig_coverage.pdf (7f338947…; round 1 ddcaba4b…) |
| 9 | fig:fived16-headline | fived16_headline.pdf (97766f5c…) | figs/fived16_headline.pdf (b93ab947…; round 1 A e405b248…, B 1f66d2fe…, now in runs/f16/figs-round1/) |

The full digests are in `figs/SHA256SUMS`. The PNG previews are at 150 dpi beside the PDFs. `figs/before/` holds 150-dpi PNGs of the installed files.

## Recipe (current: round 4)

```
bash tools/run_arms.sh <worktree> <bkg|cov|f16> P     # -> runs/round4/<fig>/CHECKS.txt, figs/variants/<name>_P.{pdf,png}
bash tools/run_arms.sh <worktree> <bkg|cov|f16> <R|D> # round 3's variants -> runs/round3/<fig>_<V>/ (redraws them; not rerun in round 4)
(cd figs/variants && shasum -a 256 *.pdf > SHA256SUMS)
```
Round 3's tools are in `runs/round3-tools/`. Round 2's recipe (`run_arms.sh <worktree> <fig>`, two arguments) is in `runs/round2-tools/`.

- **Layout of the record:** `tools/` holds the current (round 4) tools; round 2's and round 3's are copied byte for byte
  into `runs/round2-tools/` and `runs/round3-tools/`. Round 1's tools are copied byte for byte into
  `runs/round1-tools/` (with SHA256SUMS). Round 1's runs stay in `runs/<fig>/`, and its Fig. 9 A/B files are in
  `runs/f16/arm1/out/` and `runs/f16/figs-round1/`. The sections below "Round 2" describe round 1.

- **Environment:** the laptop base conda, `/Users/josephbailey/miniconda3`: Python 3.12.2, matplotlib 3.10.1,
  numpy 1.26.4. This is the environment that drew the installed files.
  - Each run uses `env -i`, BLAS threads 1, and a temporary HOME and MPLCONFIGDIR (deleted after the run).
  - Each run goes under `note-figstyle-20261117/tools/capture_palette.py`, which records every data artist.
- **Inputs:** only committed files, each held to the sha256 pin in its producer:
  - d1_summary f5c802e3…, s5n dev_receipt 1ef4096c…, tier_s interim_400 aa574c17…, fd_data_product_cpl d6752d2c…;
  - for the J decoding, s5c contract.json d54fd7c9….
- No remote host was contacted.

## Method (two arms, as note-figpass-20261119)

- **Arm 0:** the unchanged producer, run as the installed file was made (note-figpass-20261119 arm 1):
  - Fig. 7: `note-figpass-20261119/tools/layout_run.py` with the palette and layout edits, on
    `docs/analysis-note/figures/methods_m3/fig_m3_background.py`;
  - Fig. 8: the same wrapper with `LAYOUT_PALETTE=0`, on `fig_m3_coverage.py`;
  - Fig. 9: `note-figpass-20261119/tools/make_fig_fived16_headline.py`, run plainly.
  - Each arm-0 PDF is compared with the installed file by `bytes_but_date.py` and by `raster.py` at 300 dpi.
- **Arm 1:** this record's copies in `tools/`. Each draws its own layout and writes `<stem>_data.json`, which holds
  every plotted point by functional or cell name.
  - The copies are `fig_m3_background.py`, `fig_m3_coverage.py` and `make_fig_fived16_headline.py`.
  - `m3_common.py` is copied unchanged.
  - The copies keep every input pin, every `mc.check` line and the fived16 identity check. The identity check is
    generalized so that a cell may be drawn by any of several errorbar artists, but each cell exactly once.
- **`tools/jgrid.py`:** decodes J\<c\> into five coarse bins.
  - **Axis order:** `nd-unfolding/s5c_coverage.py:30`.
  - **Flat index:** `s5c_coverage.py:55-59`, `np.ravel_multi_index` over (3,3,3,3,3), C order.
  - **Edges:** `docs/orchestration/state/s5c/contract.json:73-108`, `measurement.partition_J`.
  - **Its check, `verify()`:** it rebuilds `s5c_coverage.reported_functionals(contract)` and asserts, for each of the
    109 rows J\<c\>, that the fine cells the row integrates are exactly the fine cells whose centres lie in the
    decoded box.
- **`tools/check_data.py`:** pairs every marker point with its bar in each arm's capture.
  - **Naming:** arm 0 points are named by the original producer's x rule, arm 1 points by the dump.
  - **Asserts:**
    - the same set of names in both arms;
    - y, both bar ends and the caps are bit-equal (float64 bytes);
    - arm 0 equals the receipts' numbers;
    - the arm 1 dump equals arm 1's artists;
    - the filled/open state.
  - It also lists every non-data artist per arm and their difference.

## What changed

- **Fig. 7:**
  - Panel (a) has a broken y axis: a main range from −1 to 2 %, and a strip from −4.4 to −3.2 % that holds the six
    highest-W purity points. Each point is drawn once, in the range that holds it and its bar whole (asserted).
  - Refinement squares are filled when |t| > 3.6 and open otherwise, where t = mean_rel/se_rel of the s5n
    `grid.C3_nominal` (`s5n_analyze_dev.py:62-69`). The legend says so.
  - Panel (b) groups the cells in 9 (p_T, p_∥) blocks with alternate blocks shaded. The p_T ranges are above the axis
    and the p_∥ ranges below it. The total is set apart by one slot and a separator.
  - The canvas is 6.5 × 5.75 in.
- **Fig. 8:**
  - **Panel (a):** the 42 (E_avail,W) cells, with the E_avail labels and W-bin ticks of Fig. 7(a), and their sum set apart.
  - **Panel (b):** the 109 joint cells in Fig. 7(b)'s blocks, and the total.
  - Unchanged: the markers, the filled/open rule, the nominal and threshold lines, the four legend entries and the title string.
  - The dotted dividers are gone.
  - The canvas is 6.5 × 4.95 in.
- **Fig. 9 A:**
  - It keeps the box table, with the row headers in words.
  - Alternate columns are shaded through the table.
  - The four quadrants are separated by gaps, thin rules and their headers; the quadrant shading is dropped so that
    the column shading reads.
  - Dotted guides run from each point's lower bar end to its column.
  - The canvas is 6.5 × 3.95 in.
- **Fig. 9 B:**
  - Marker shape gives W: circle for any, up-triangle for > 1.8 GeV, down-triangle for < 1.8 GeV.
  - Marker fill gives E_avail: solid for < 0.8 GeV, a light tint for any, open for > 0.8 GeV.
  - The two encodings have two compact legends.
  - Only the q3 row of the table remains.
  - The quadrant shading is kept, and the canvas is 6.5 × 3.6 in.
- **Every figure:** every text is at least 7.0 pt at the printed width. Each is included at `\linewidth` = 6.5 in, so
  it prints at scale 1.0. Mathtext sub- and superscripts print at 70 % of their font, as in the figure pass.

## Checks (runs/\<fig\>/CHECKS.txt)

| fig | arm 0 vs installed | data points bit-equal | names identical | arm 0 = receipt | fonts < 7 pt |
|---|---|---|---|---|---|
| 7 | EQUAL (bytes), raster 0 px | 304 (purity + refined × 152) | yes (EW_all_ones not plotted in either) | 304/304 | 0 |
| 8 | EQUAL (bytes), raster 0 px | 306 (68 % + 95 % × 153); filled/open equal | yes | 306/306 | 0 |
| 9 | EQUAL (bytes), raster 0 px | 16 per variant (f, bar ends, caps) | yes | 16/16 | 0 |

- **Fig. 7 fail marking:**
  - panel (a) has 29 of 42 filled, panel (b) 60 of 110 (59 J and the total);
  - the unplotted EW_all_ones has |t| ≤ 3.6;
  - 29 + 60 + 0 = 89 = the receipt's `n_abs_t_gt_crit` (asserted in the producer and in check_data).
- **Fig. 8 filled points:**
  - panel (a): 18 at 68 % and 17 at 95 %;
  - panel (b): 33 at 68 % and 25 at 95 %;
  - totals 51 and 42, as the `mc.check` lines.
- **Numbers files:**
  - the cov numbers file is byte-identical between the arms;
  - the fived16 `fived16_headline_values.json` is byte-identical between the arms;
  - the bkg numbers file keeps arm 0's six entries and adds the fail-count check.
- **Decoration-only differences:**
  - Fig. 7: arm 0's dotted total divider becomes solid separators, plus the E_avail rules on the strip and two break-mark lines.
  - Fig. 8: two dotted dividers become the separators and panel (b)'s reference lines.
  - Fig. 9 A: 16 guides and 3 quadrant rules.
  - Fig. 9 B: none.
  - **Not recorded by the capture:** shading spans and rectangles, which are drawn in blended axes coordinates.
- **Text overlaps** are capture_any.py's box measure, as in the figure pass. They all lie between neighbouring legend
  entries or between a legend title and its entries; none shows on the page (PNG previews).

## Decisions and constraints

- **Nothing installed:** installing a chosen file needs an `install_*` line in `make_figures.sh` and the caption edits
  in the report. Both are outside this task.
- **Fig. 7's filled squares mark |t| > t_crit only.** The receipt's criterion (`s5n_analyze_dev.py:146-149`) also fails a
  functional with 3 < |t| ≤ 3.6 and |mean pull| > 0.5. J7 and J26 meet that second clause and are drawn open.
  The figure therefore says "|t| > 3.6", not "fails the criterion".

## Round 2 (2026-11-23): the outside reviewer's suggestions

- **Source:** `codex-reports/note-measurement/figredraw-20261123/ask-codex/REPORT.md`; Joseph approved the changes
  listed in the round-2 brief. Same rules and the same two-arm method as round 1. Arm 0 and every data check were
  rerun at worktree HEAD ca639f8b9, in the same environment (Python 3.12.2, matplotlib 3.10.1, numpy 1.26.4).

### What changed

- **Fig. 7 (`tools/fig_m3_background.py`):**
  - **Legend:** one entry per method: "purity-based subtraction (9 experiments)" and "negative-weight refinement
    (60 experiments)". "Unbinned" is dropped, following the brief's wording.
  - **Key:** a separate key on the right, titled "refinement squares:", with a filled square for $|t|>3.6$ and an
    open square for $|t|\leq3.6$.
  - **Removed:** the text block "$t$ = mean residual / its standard error; $t_{\rm crit}=3.6$ of the nominal closure
    criterion".
  - **Canvas:** 6.5 × 5.55 in (was 5.75).
  - **Unchanged:** the ranges, the points and the marking. The main range is −1.0 to 2.0 % and the strip −4.4 to
    −3.2 %, so −3.2 to −1.0 % is omitted. Panel (b) runs from −2.5 to 3.2 %.
- **Fig. 8 (`tools/fig_m3_coverage.py`):**
  - **Removed:** the header sentence "signal rate lowered by about 10%, weak $E_{\rm avail}$ slope: upper bound below
    threshold for 51 (68%) and 42 (95%) of 153".
  - **Legend:** two columns (68 % blue, 95 % red), each with four entries: the open point, the filled point,
    "nominal coverage 0.68/0.95 (solid line)" and "test cutoff 0.66/0.94 (dashed line)".
  - **Lines:** the cutoff dash is longer, (4, 2.5) instead of (3, 2), so it reads at print size.
  - **Unchanged:** points, bars, the fill rule, panels and canvas (6.5 × 4.95 in).
- **Fig. 9 (`tools/make_fig_fived16_headline.py`):** one figure built from variant A, written as `fived16_headline.pdf`.
  - **Kept:** the four quadrant headers, the three dividers through the table, and the three cut rows with their word
    headers.
  - **Removed:** the dotted stems and the alternating column shading.
  - **Shading:** one light shade (0.93, as in the installed figure) on the 1st and 3rd quadrants. It runs from the
    axis edge or divider to the next divider and continues through the table.
  - Variant B is dropped. The canvas is 6.5 × 3.95 in.
- **`tools/check_data.py`:** f16 compares the single file with arm 0 and asserts that all 16 markers share one style.
  bkg and cov are unchanged.
- **`tools/run_arms.sh`:** runs go to `runs/round2/<fig>/`, and f16 installs one file.

### Checks (`runs/round2/<fig>/CHECKS.txt`)

| fig | arm 0 vs installed | data points bit-equal | arm 0 = receipt | dump = artists | fonts < 7 pt | marking counts |
|---|---|---|---|---|---|---|
| 7 | EQUAL (bytes), raster 0 px | 304/304 | 304/304 | 304/304 | 0 (min 7.00) | filled (a) 29/42, (b) 60/110, unplotted 0; 89 = receipt |
| 8 | EQUAL (bytes), raster 0 px | 306/306, filled/open equal | 306/306 | 306/306 | 0 (min 7.00) | filled (a) 18 / 17, (b) 33 / 25 (68 % / 95 %) |
| 9 | EQUAL (bytes), raster 0 px | 16/16 (f, bar ends, caps) | 16/16 | 16/16 | 0 (min 7.00) | — |

- **Removed strings:** `pdftotext` finds none of them in the delivered PDFs.
- **Decoration differences from arm 0:**
  - Fig. 7: the same set as round 1.
  - Fig. 8: the same set as round 1.
  - Fig. 9: only the 3 quadrant dividers; round 1's 16 guides are gone.
- **Text overlaps:** Fig. 7 has none. Fig. 8 has 7, all between neighbouring legend entries in capture_any.py's box
  measure, and none is visible in the PNG.

### Caption facts checked in the producers (for the caption edits; no .tex edited)

- **Fig. 7, $t$ and $t_{\rm crit}$:**
  - $t$ = mean_rel/se_rel per functional of `grid.C3_nominal`, over 60 experiments (`nd-unfolding/s5n_analyze_dev.py:62-69`).
  - `T_CRIT = 3.6  # contract C3: two-sided 0.05/153 Bonferroni` is at `nd-unfolding/s5n_analyze_dev.py:35`, not :34.
    The two-sided normal quantile at 0.05/153 is 3.593.
  - The criterion's second clause (3 < |t| ≤ 3.6 and |mean pull| > 0.5; :146-149) is not drawn. J7 and J26 meet it and
    are drawn open. A caption should therefore say "|t| > 3.6", not "fails the criterion".
- **Fig. 8, bars:**
  - `ax.vlines(x + dx, lo, hi)` at `docs/analysis-note/figures/methods_m3/fig_m3_coverage.py:87`, with lo, hi =
    lcb, ucb at :43.
  - The bounds are one-sided Clopper–Pearson, `nd-unfolding/s5c_coverage.py:161-164` via
    `nd-unfolding/s5c_samplesize.py:25-30`. Each is at α = 0.05/459, where 459 = 153 functionals × 3 truths
    (`s5c_coverage.py:147`, asserted at `fig_m3_coverage.py:34`).
  - Coverage = hits/400 (`fig_m3_coverage.py:43`). A hit is |f̂ − truth| ≤ σ (68 %) or ≤ 1.96σ (95 %), at
    `s5c_coverage.py:101-102`.
- **Fig. 8, fill:** `bad = hi < THR[l]` at `fig_m3_coverage.py:84`, drawn filled at :90, with THR 0.66/0.94 at :25. The
  fill means the upper confidence bound is below the cutoff, which confirms the reviewer's reading.
- **Fig. 8, lines:** nominal levels at `fig_m3_coverage.py:26` and :85 (solid); cutoffs at :25 and :86 (dashed).

## Round 3 (2026-11-23): two variants per figure (R refined, D redesign)

- **Sources:** the outside reviewer's two turns, `codex-reports/note-measurement/figredraw-20261123/ask-codex2/REPLY1.md`
  (its redesigns, from the note alone; variant D) and `REPLY2.md` (its suggestions on round 2's figures; variant R).
  The rules, the two-arm method and the environment are those of rounds 1–2 (Python 3.12.2, matplotlib 3.10.1, numpy 1.26.4).
- **Tools:** round 2's tools are copied byte for byte into `runs/round2-tools/` (with SHA256SUMS). This includes the
  post-round-2 legend names in `fig_m3_background.py` ("deterministic purity control (9 pseudo-experiments)",
  "low-capacity negative-weight refinement (60 pseudo-experiments)"), which both variants keep. Each producer in
  `tools/` takes `--variant R|D`. `tools/overlaps.py` is new (see Checks).
- **Worktree:** the branch moved during the runs, ca639f8b9 → 2c0a2a261 → 61cea68ac, through a peer's note-text commit
  and a merge of origin/main. None of the inputs changed: no receipt, record, contract, `nd-unfolding/s5c_coverage.py`,
  `project_cov_nd.py`, installed figure or figure-pass tool. Every input is held to its sha256 pin, and arm 0 is EQUAL at each head.

### What each variant draws

- **Fig. 7 R** (`figs/variants/paper_fig_bkg_residual_R.pdf`, 6.5 × 5.55 in): round 2, plus the following.
  - In panel (a), the last W bin of each E_avail block is labelled "≥3", and that column is lightly shaded through both
    ranges. The x label ends "shaded: W ≥ 3 GeV".
  - Panel (b) has the annotation "up to 14 standard errors", with a leader line to the refinement square of J88.
  - Asserted: J88 is the argmax of |t|; |t| = receipt `grid.C3_nominal.max_abs_t` = 14.421456021984215 (14.42 to 2 d.p.);
    "14" is floor(max_abs_t).
- **Fig. 7 D** (`…_D.pdf`, 6.5 × 5.65 in):
  - **Panel (a)** is two E_avail–W heatmaps: purity control on the left, refinement on the right.
    - Each heatmap is titled with its legend name and labelled with its bin edges, as Fig. 6 is.
    - The edges are asserted equal to `nd-unfolding/project_cov_nd.py` AXIS_EDGES.
    - EW\<k\> = (E_avail bin k // 6, W bin k % 6) is asserted by `jgrid.verify_ew()` against `s5c_coverage.reported_functionals`.
    - Both use one shared, zero-centred PuOr_r scale (±4.5 %, the smallest half-step above the largest |residual|) with one colour bar.
    - The signed residual is printed in every cell (7 pt, 2 decimals, true minus sign). The refinement value is bold
      where |t| > 3.6 (29 of 42 cells).
  - **Panel (b)** and the legend are round 2's.
- **Fig. 8 R** (`paper_fig_coverage_R.pdf`, 6.5 × 4.95 in): round 2 without the solid nominal-coverage lines and their
  two legend entries. The dashed cutoffs 0.66/0.94 stay. "51/153 failures (68%)" and "42/153 failures (95%)" are printed
  in bold above the two legend columns. Both counts are computed from the receipt and asserted equal to the mc.check
  counts and to 51/42.
- **Fig. 8 D** (`…_D.pdf`, 6.5 × 4.75 in):
  - **Rows:** one row per level, (a) 68 % and (b) 95 %, on the same 0–1 axis. Each heading carries its count, e.g.
    "(a) 68% intervals: 51/153 failures (upper bound below 0.66)".
  - **Sections:** each row has three: the 42 projection cells, the 109 joint cells, and "sum, total".
  - **Order:** within the projection and joint sections, points are ordered by the upper Clopper–Pearson bound
    (stable sort), so the filled points lead.
  - **Marks:** the dot is the empirical coverage, and the bar runs from the lower to the upper bound. A point is filled
    when its upper bound is below the dashed cutoff, which is labelled "test cutoff 0.66/0.94".
  - **Axis:** x is the rank within the section.
  - Each point's name, rank and axes are in `m3_fig3_coverage_data.json`.
- **Fig. 9 R** (`fived16_headline_R.pdf`, 6.5 × 4.21 in): round 2, plus the following.
  - Log axis 2.5–65, with ticks labelled 3, 5, 10, 20, 50 and no minor labels.
  - R04 and R14 carry "49.0" and "49.6": three significant figures of f from the record, asserted. They are asserted to
    be the two largest central values.
  - The quadrant headers move above the axes. The new range puts R04/R14 where the headers were drawn, and the shading
    and dividers continue through the header band.
- **Fig. 9 D** (`fived16_headline_D.pdf`, 6.5 × 3.47 in):
  - **Grid:** a 2 × 2 grid of horizontal dot-and-whisker panels. Rows are p_T 0–0.7 / 0.7–4.5 and columns are
    p_∥ 1.5–4.5 / 4.5–60, each panel headed by its ranges.
  - **Axis:** a shared linear axis, f from 0 to 60 (10⁻⁴⁰ cm²/nucleon), with light gridlines at every 10.
  - **Row labels:** each row reads the region ID (bold), then its E_avail, q_3 and W cuts in three columns headed once
    per panel. Rows are in Table order, top to bottom.
  - **Footnote:** "cuts: E_avail and W in GeV, q_3 in GeV/c; 'any' = the whole axis".

### Checks (`runs/round3/<fig>_<V>/CHECKS.txt`; every run PASS)

| variant | arm 0 vs installed | data bit-equal (by name) | names identical | extra checks | fonts < 7 pt | overlaps / off canvas |
|---|---|---|---|---|---|---|
| 7 R | EQUAL bytes, raster 0 px | 304/304 points (y, bar ends) | yes | marking 29+60+0 = 89 = receipt; annotation J88, 14.42 | 0 | 0 / 0 |
| 7 D | EQUAL bytes, raster 0 px | 220/220 points (b); 84/84 heatmap colour values = arm 0 y; 84/84 printed = fmt(arm 0 y) | yes (220 + 84 = 304) | bold = \|t\| > 3.6 84/84; shared clim (−4.5, 4.5); 89 = receipt | 0 | 0 / 0 |
| 8 R | EQUAL bytes, raster 0 px | 306/306, filled/open equal | yes | printed counts 51, 42 = receipt | 0 | 0 / 0 |
| 8 D | EQUAL bytes, raster 0 px | 306/306, filled/open equal | yes | ucb non-decreasing in all 4 sorted sections; ranks 1..n; counts 51, 42 | 0 | 0 / 0 |
| 9 R | EQUAL bytes, raster 0 px | 16/16 (f, bar ends, caps) | yes | labels 49.0, 49.6 = 3 s.f. of arm 0 y | 0 | 0 / 0 |
| 9 D | EQUAL bytes, raster 0 px | 16/16 (x = arm 0 y; x bar ends, caps) | yes | — | 0 | 0 / 0 |

- **Not drawn in Fig. 7 D:** the 84 panel-(a) error bars. The heatmaps draw the value only; the error stays in the dump
  and is checked against arm 0's bar ends. This is the only data array shown in arm 0 and not drawn in arm 1, in any
  variant.
- **`tools/overlaps.py` (new):**
  - It runs each producer again, draws the canvas once at the PDF save, and measures every drawn text on that one
    renderer, giving overlaps (> 0.5 px both ways) and text off the canvas. Off-canvas text fails an arm-1 run.
  - capture_any.py's measure (still printed) reads extents without drawing the canvas, and reported 26 spurious pairs
    for Fig. 7 D: heatmap numbers against the figure legend.
  - The new measure caught two real defects, fixed before delivery: Fig. 9 R's headers 1.4 px past the top edge, and
    Fig. 9 D's footnote touching an x label.
  - It also shows that the installed Fig. 8 (arm 0) has its header sentence 1.5 px past the right edge. Round 2 removed
    that sentence.
- **Decoration differences** (lines, meshes, colour bar; listed per run in CHECKS.txt):
  - 7 D: two heatmap meshes and the colour bar in place of the panel-(a) reference lines.
  - 8 R: no solid nominal lines.
  - 8 D: one dashed cutoff per section.
  - 9 D: grid lines.
- **`figs/SHA256SUMS` (round 2) was stale for `paper_fig_bkg_residual.pdf`** (regenerated in round 4; see "Round 4"): it listed 4d0823e8…, but the file is now
  a44a8562… after the post-round-2 legend-name change (07:42). It was left as found.

### Judgement calls

- **7 R:** the "≥3" tick labels sit close to the next block's "1". Text boxes do not overlap, and the block rule and
  shading separate them. Font size stays at 7 pt.
- **7 D:** numbers are printed in every cell (7 pt fits). The |t| > 3.6 marking in the refinement map is bold type: the
  map has no squares to fill, and this keeps round 2's marking. PuOr_r is used rather than red–blue, so the map colours
  are not read as the method colours (blue = purity, red = refinement) of panel (b). Fig. 6 itself is red–blue.
  - Panel (b) has no "14 standard errors" callout: the brief says panel (b) stays round 2's, and REPLY1 also suggests one.
- **8 D:** no cell identity is drawn, by design. The x axis is rank, and names are in the dump.
- **9 D:** on the linear 0–60 axis (1.55 in wide), 10 of the 16 full bars (2σ) are shorter than the 4-pt marker:
  R02, R03, R05, R06, R07, R08, R10, R11, R13 and R15 (1.0–3.8 pt). Mostly only their caps show. That is the cost of
  the requested linear axis; Fig. 9 R's log axis shows every bar.

## Round 4 (2026-11-23): polish of the reviewer's choices (variant P)

- **Source:** the reviewer's third turn, `codex-reports/note-measurement/figredraw-20261123/ask-codex2/REPLY3.md`. It
  chose 7 D, 8 D and 9 R (its fig7_A, fig8_B and fig9_B), and Joseph asked for its polish. Each polished figure is
  variant P of its producer: 7 P and 8 P start from D, and 9 P starts from R. The rules, method and environment are
  those of rounds 1–3.
- **Tools:** round 3's tools are copied byte for byte into `runs/round3-tools/` (with SHA256SUMS). In `tools/`:
  - each producer takes `--variant P`;
  - `run_arms.sh` takes P and writes `runs/round4/<fig>/`;
  - `check_data.py` checks P with its base variant's checks, plus a check of the callout's arrow tip;
  - `fig_m3_background.py`: R's callout code moved into a function shared by R and P, and its dump also records the
    arrow tip.
  - **Regression:** the edited tools redraw all six round-3 R/D PDFs EQUAL to `figs/variants/*_{R,D}.pdf` (bytes but the
    date). The round-3 files were not rerun or overwritten, and their PDF and PNG sha256 are unchanged.
- **Worktree:** HEAD dc01e1464 throughout. Every input is held to its sha256 pin.

### What changed

- **Fig. 7 P** (`figs/variants/paper_fig_bkg_residual_P.pdf`, 6.5 × 5.42 in; D was 5.65): variant D, plus the following.
  - **Legend moved into panel (b):** the method legend (purity circle, refinement square) and the filled/open key are
    gone from the top of the figure. They are now one boxed legend at the upper right of panel (b), where the circles
    and squares are drawn. Its third row reads "refinement squares: filled |t| > 3.6, open |t| ≤ 3.6".
    - The box is white with a thin grey edge, so the block shading and the p_T divider do not run through the text.
    - Asserted after drawing: no panel-(b) point or bar end lies under the legend.
  - **Panel (a) unchanged:** the heatmaps keep their own titles and the colour bar.
  - **Callout:** "up to 14 standard errors" at the largest-|t| joint cell, with a leader line to its refinement square
    (round 3 R's code).
    - Asserted in the producer: J88 is the argmax of |t|; |t| = receipt `grid.C3_nominal.max_abs_t` = 14.421456021984215;
      "14" = floor(max_abs_t).
    - Asserted by check_data.py: the arrow tip is the drawn J88 refinement square, (35.17, y bit-equal to arm 0's).
  - **Layout:** the canvas is 0.23 in shorter (no legend band on top), and panel (b) is 0.23 in taller (1.85 in). Its y
    range (−2.5 to 3.2 %) is unchanged.
- **Fig. 8 P** (`paper_fig_coverage_P.pdf`, 6.5 × 4.62 in; D was 4.75): variant D with one compact key on one line, in
  place of D's six entries (open and filled per level, plus the cutoff and the bar):
  - filled circle and square: "upper bound below the cutoff (fails)";
  - open circle and square: "not below";
  - vertical bar: "lower to upper confidence bound";
  - dashed line: "test cutoff".
  - The two rows' headings carry the level colours (blue 68 %, red 95 %). The key is asserted to fit the canvas width.
- **Fig. 9 P** (`fived16_headline_P.pdf`, 6.5 × 4.21 in, as R): variant R with the plot area starting at 1.2 in instead of
  1.0 in. The cut-row labels now end clear of the first quadrant's shaded band.
  - Asserted after drawing: each label ends at least 0.06 in left of the band.
  - Measured gaps: hadronic energy 0.33 in, momentum transfer 0.15 in, hadronic mass 0.42 in. At R's 1.0 in,
    "momentum transfer" reached 0.05 in into the band.

### Checks (`runs/round4/<fig>/CHECKS.txt`; every run PASS)

| variant | arm 0 vs installed | data bit-equal (by name) | names identical | extra checks | fonts < 7 pt | overlaps / off canvas |
|---|---|---|---|---|---|---|
| 7 P | EQUAL bytes, raster 0 px | 220/220 points (b); 84/84 heatmap colour values = arm 0 y; 84/84 printed = fmt(arm 0 y) and drawn | yes (220 + 84 = 304) | bold = \|t\| > 3.6 84/84; shared clim (−4.5, 4.5); 29 + 60 + 0 = 89 = receipt; callout J88, \|t\| = max_abs_t, tip = J88's square | 0 | 0 / 0 |
| 8 P | EQUAL bytes, raster 0 px | 306/306, filled/open equal (51, 42 filled) | yes | ucb non-decreasing in all 4 sorted sections; printed counts 51, 42 = receipt | 0 | 0 / 0 |
| 9 P | EQUAL bytes, raster 0 px | 16/16 (f, bar ends, caps) | yes | labels 49.0, 49.6 = 3 s.f. of arm 0 y; row-label room ≥ 0.06 in | 0 | 0 / 0 |

- **Overlaps:** the overlaps column is `tools/overlaps.py` on one drawn canvas. capture_any.py's undrawn measure, still
  printed, reports 4 pairs in 7 P and 2 in 8 P (legend rows and the callout against neighbours). These are the known
  spurious kind (see Round 3). overlaps.py finds none.
- **Not drawn in Fig. 7 P:** as in 7 D, the 84 panel-(a) error bars. They stay in the dump and are checked against arm 0.
- **`figs/SHA256SUMS` regenerated:** `paper_fig_bkg_residual.pdf` 4d0823e8… → a44a8562…; the other two lines are unchanged.
  Before re-pinning, `runs/round2-tools/fig_m3_background.py` (its own SHA256SUMS OK) was rerun, and its PDF is EQUAL
  (bytes but the date) to `figs/paper_fig_bkg_residual.pdf`. So a44a8562… is round 2's figure with the later legend
  names. `figs/variants/SHA256SUMS` now also lists the three P PDFs.
- **Captions (not written, no .tex edited):**
  - 7 P needs t defined in the caption (REPLY3).
  - 8 P's caption should say that the bar's upper end is the multiplicity-adjusted bound the test uses, and that each
    interval level is ranked on its own (REPLY3).
  - 9 P's caption should lead with "Illustrative sixteen-cell result" and keep the definition of the C_rep whiskers
    (REPLY3).

## What is committed (2026-11-23, at install)
Committed: `tools/`, `figs/` (the installed three, `variants/`, `before/`), every round's `CHECKS.txt`, the round 1-3
tools (`runs/round*-tools/`) and round 4's full run outputs (`runs/round4/`), the run that drew the installed files.
Rounds 1-3's arm outputs (captures, PDFs, data dumps) are not committed: they are intermediate drafts, each
reproducible with its round's tools and `run_arms.sh`, and their data dumps would otherwise enter the results index as
duplicate receipts. A local copy is at `~/codex-reports/note-measurement/figredraw-20261123/runs-uncommitted/`.
The final Fig. 9 adds an R07 label (3.21, asserted against the record and the caption's \fvval{f-R07}) to round 4's P.
