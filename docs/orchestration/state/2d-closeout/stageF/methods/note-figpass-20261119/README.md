# The note's figure pass (cov2d, from 2026-11-19)

**Requested by** the director on 2026-11-19, from director-helper-3's deterministic quality counts
(`~/codex-reports/note-measurement/quality/deterministic-1acece939.md`) and the figure plumbing
(`~/codex-reports/note-measurement/figure-plumbing.md`).
- **Base:** origin/draft/note-round2-20261108 at `c3b4e8842`.
- **Scope:** presentation only. No datum, number or colour changes. A caption changes only where it names a panel's position.
- **Earlier records:** `note-figstyle-20261113/` and `note-figstyle-20261117/` stay unchanged; their `figs/` files are immutable. This record reuses their tools and dumps from their committed paths.

**Status:** in progress.

| chunk | figures | state |
|---|---|---|
| A1 | 17 (fig:eavail-marg), 23 (fig:q3excess) | Fig. 23 drawn again at its printed size; Fig. 17 split into its two panels at full width (LaTeX only; superseded by D) |
| A2 | width classes; text under 7 pt | three width classes in LaTeX; Figs. 33, 36 drawn again at printed size; Figs. 26, 27 with larger fonts |
| B | the duplicates (Figs. 7, 9, 10, 13; 20, 21), by Joseph's ruling of 2026-11-19 (DECISION-20261119b) | each series drawn once: Fig. 13 folded into Fig. 7, the mosaic's points into Figs. 9 and 10, Figs. 20 and 21 one figure |
| C | the Gemini graders' caption-match items (director, 2026-11-19) | Figs. 12, 18 captions; Figs. 19, 22 labels; Fig. 32 titles; Fig. 9 scaling clause; Fig. 15 label off the star |
| D | Fig. 17 (fig:eavail-marg) redrawn from the fetched input | one stacked figure at printed size, every text at least 10 pt; "pull" read as "standardized difference" |

## The method (two arms per redrawn figure)

- **Arm 0** runs the unchanged producer under the palette pass's `note-figstyle-20261117/tools/palette_run.py`, the
  recipe that drew the installed file. It must reproduce that file at the base:
  - byte-equal apart from the PDF creation date (`bytes_but_date.py`);
  - pixel-equal at 300 DPI (`raster.py`).
- **Arm 1** runs the same producer under `tools/layout_run.py`. This applies the same palette edits, then
  `tools/layout_lib.py`'s layout edits, once per figure, before its first save. Not one producer byte changes.
- **The layout edits** come from this record's tables:
  - **ticks frozen:** every axis keeps the major ticks and tick labels it drew;
  - **`layout.tsv`:** the canvas at its printed size, with every text size times a scale and raised to a floor;
  - **`ticks.tsv`:** a tick-label rotation;
  - **`boxes.tsv`:** each axes placed in a box, in inches. Without boxes, the figure gets `tight_layout()`.
- **The checks** (`tools/arms_layout.sh`, written to `runs/<family>/CHECKS.txt`):
  - arm 1 against arm 0 passes fig-restyle-20261031's `compare.py` with no restyle tables, so every data item's full hash must be equal: data, colours and line styles;
  - the multiset of drawn strings must be equal;
  - per arm: the canvas size, the smallest and median font size, and the text overlaps (capture_any.py's measure).
- **Install:** `tools/install_layout.py` copies an arm-1 PDF to `figs/` and the note. It comments out the old install
  line and adds an `install_layout_fig` line to make_figures.sh's "note-figpass-20261119" block.

## Chunk A1

### Fig. 23 (fig:q3excess), redrawn

- **Recipe:** `nd-unfolding/q3_excess_projection.py --from-arrays note-figstyle-20261113/runs/family5/dumps/q3_arrays.npz --print-style`.
  - It runs under matplotlib 3.10.8 (`figenv/mpl3108`), with the 11-13 fake-ROOT stand-in, as the palette pass did.
- **The new layout:** a 6.5 × 5.0 in canvas, printed at \textwidth, which is scale 1.0.
  - The ratio map is on its own row. Its column labels are horizontal, and its in-cell values are at 7 pt (5.5 pt before).
  - The q3 and E_avail marginals are on the row below, with horizontal tick labels.
  - Every text is at least 7 pt (floor 7.0, scale 1.0).
- **Checks** (`runs/q3/CHECKS.txt`):
  - arm 0 is EQUAL-BUT-DATE and 0 px against the installed file;
  - COMPARE :: PASS (7 data artists);
  - the 87 drawn strings are equal;
  - text overlaps go from 29 to 0 in the capture.
  - In the note PDF, quality_checks' overlapping strings for Fig. 23 go from 50 to 0.
- **Caption:** the panel positions change from "left / center / right" to "top / lower left / lower right". That
  sentence is the chunk's one caption hunk (one Grok read).
  - **The Grok read** (`~/codex-reports/note-measurement/reads/figpass-A1/grok/report.md`) passed the caption and
    Fig. 17. It found two unchanged body sentences in sec_3d that still named Fig. 23's old panels.
  - **The fix:** those pointers now read top, lower left and lower right (commit ed1dcb2f9).
  - **The re-read** (`reads/figpass-A1-r2/grok/report.md`) passed.

### Fig. 17 (fig:eavail-marg), LaTeX only

- **Why not redrawn:** its producer (`compare_to_paper_fullcov.py`) reads config (a)'s
  `3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root`, which is only on pscratch.
- **The layout:** the installed 864 × 360 pt canvas is split by `\includegraphics` trim into its two panels:
  - the grid panel, kept from x = 5 to 430 pt;
  - the distribution panel, kept from x = 430 to 858 pt.
- **How it prints:** each panel prints at scale 1.0 (it was 0.38). The distribution panel follows on the next page, in
  a continuation float that reads "Figure 17: continued, the per-bin differences in distribution." The figure keeps
  one number and one label.
- **Measured in the note PDF** (quality_checks):
  - the smallest word-like text is 8.0 pt (3.0 before), and the median is 10.0 pt (3.8 before);
  - the superscripts ("21" in 10²¹ POT) are 5.6 pt (2.1 before).
  - **Below 7 pt pending a producer re-render:** the superscripts.
- **freeze_checks' font check** allows a sans-serif font only on the pages of four named figures, Fig. 17 among them.
  It now also allows the page after fig:eavail-marg's label (`SANS_CONTINUED`), where the continuation prints.
- **The re-render's input fetch** is prepared but not run:
  - script: `~/cov2d-work/figfetch/fetch-3d-a.sh`, a read-only O_NOATIME copy of the one file;
  - pin: `0dd94830821576a3b060fae2d4a20564610c535ed06046cd1eb05cd11885dd59`
    (re1/RE1-AMENDMENT-DECLARATION.md:151; re1/run2/launch/re1_f_env.sh:2).
  - It waits for the director's go.

## Gates for chunk A1

- **Build:** rc 0, with 0 undefined references.
- **freeze_checks** (checks 1, 3, 5 and 7, base PDF at c3b4e8842, with an empty allow-list) passes:
  - the numbers diff finds 5565 tokens in each build, with 0 unexplained;
  - labels, fonts and accents pass.
- **quality_checks:**
  - figures with overlapping strings go from 4 to 3;
  - figures with a 10th-percentile text size under 7 pt go from 26 to 24, and those with a median under 7 pt from 18 to 17;
  - distinct printed widths go from 12 to 13, because Fig. 17's panels are new widths (chunk A2 sets the classes);
  - for Figs. 17 and 23, see above;
  - the count of figures with any text under 7 pt stays at 32, because the sub- and superscripts of both figures remain under 7 pt.

## Chunk A2: width classes and text under 7 pt

### Width classes (LaTeX only)

Every figure outside chunk B is printed at one of three widths:

| class | width | figures |
|---|---|---|
| full | `\textwidth` | 1, 2, 3, 12, 14, 15, 17 (both panels), 18, 19, 22, 23, 25, and the ones already there (26–36 except 35) |
| single | `0.7\textwidth` | 6, 8, 16, 24, 35 |
| two-panel / tall | `0.49\textwidth` per panel | 4, 5, 11 (pairs) |

- **What changed:**
  - 0.99, 0.97, 0.95, 0.92, 0.90 and 0.85 became full;
  - 0.62, 0.66 and 0.55 became single;
  - Fig. 24 (fig:eavailWexcess, a tall two-row figure) moves up to single (0.7), not down to 0.49, so its words print at 8 pt.
- **Not yet:** the figures of chunk B (7, 9, 10, 13, 20, 21) keep their widths until B re-lays them out.
- **Fig. 17:** both panels are at `\textwidth` (scale about 1.1).
- **Distinct printed widths** go from 13 (12 at the base) to 5: the three classes plus 0.62 and 0.85, both in chunk B.

### Figures drawn again with a 7 pt floor

Each is drawn at its printed size with `layout.tsv` (scale 1.0, floor 7 pt) and `boxes.tsv`.

- **Fig. 33 (fig:coverage-5d-paper, `m3_fig3_coverage`):**
  - recipe `docs/analysis-note/figures/methods_m3/fig_m3_coverage.py --repo <wt> --outdir <dir>`, under the laptop's base conda (matplotlib 3.10.1), the recipe of the installed file;
  - `ARM0=plain`, because the palette pass made no edit;
  - arm 0 is EQUAL (byte for byte) and 0 px against the installed file;
  - 12 data artists equal, 29 strings equal;
  - every font is at least 7.0 pt (5.8 before, median 6.4).
- **Fig. 36 (fig:bkg-residual-note, `m3_fig1_background`):**
  - same recipe, with arm 0 under the palette pass's text fix; arm 0 is EQUAL and 0 px against the installed file (figs-r2);
  - 17 data artists equal, 90 strings equal;
  - every font is at least 7.0 pt (5.5 before);
  - panel (a) is taller, so its title clears the E_avail bin labels (both are placed in axes fractions).
- **The overlap counts:** capture_any.py's legend overlaps in arm 1 come from that measure, not the figure. They do not show on the page, and quality_checks finds 0 overlapping strings in both figures in the note PDF.

### Figs. 26 and 27: cov2d's own producers, larger fonts

- **Why copies:** the originals in note-newfigs-20261118 are immutable MANIFEST rows. So `tools/make_fig_fived16_headline.py` and `tools/make_fig_runperiod_steps.py` are copies that change only:
  - the explicit font sizes: 7.4 to 7.6 pt, which were 6.6 to 7.2;
  - panel (b)'s lower y limit in Fig. 27, so its larger panel label clears the 1B bar;
  - the repository root depth and the default output (`figs-src/`, not committed).
- **What stays:** every input pin, check and identity assertion. Their `*_values.json` are byte-identical to the originals'.
- **The PDFs** carry no creation date (`97766f5c`, `4496bcf8`).
- **sec_fived16.tex's comments** naming the installed digests are updated; they do not print.

### Not changed, and why

| figure | under 7 pt | why not here |
|---|---|---|
| 1, 3, 15, 16, 19, 22–25, 30 | sub- and superscripts only (math text at 70 % of an 8–8.5 pt font) | a floor cannot lift them without enlarging every font; the width class already scales them up where it widens |
| 2 (fig:control-corner) | the r_MC / r_data subscripts | the same; a redraw at full width spread the corner grid apart for no gain |
| 6, 11, 12, 14 (tier 2) | tick labels at 5.5–6.1 pt (restyle_2026_10's sizes) | a local re-render is possible (inputs fetched on 2026-11-17, ROOT environment), but it is not cheap; candidates for a follow-up chunk |
| 18 (fig:calibration) | 3.2–4.0 pt | no producer (ISSUES.md:1292; the director ruled it is not recreated) |
| 28 (fig:fived16-modes) | 4.1–5.4 pt | pinned in make_values_fived16.py FIGURES; a redraw needs a new sidecar with K0–K8 passed |
| 34 (fig:joint5d-nulls) | legend at 6.0 pt | arm 0 does not reproduce the installed file on this laptop (90086 px differ; the arm64 / x86_64 draw difference recorded in note-figstyle-20261113's CHECKS-families3to6.txt) |
| 17 superscripts | 6.1 pt | the producer re-render (its own chunk; the input was fetched on 2026-11-19) |
| 7, 9, 10, 13, 20, 21 | — | chunk B |

### Gates for chunk A2

Base: the A1 build at ed1dcb2f9.

- **Build:** rc 0, with 0 undefined references.
- **freeze_checks** (checks 1, 3, 5 and 7, empty allow-list) passes:
  - the numbers diff finds 5540 tokens in each build, with 0 unexplained;
  - labels, fonts and accents pass.
- **quality_checks:**
  - figures with a 10th-percentile text size under 7 pt: 24 → 17;
  - figures with a median under 7 pt: 17 → 12;
  - distinct printed widths: 13 → 5;
  - figures with overlapping strings: 3, all unchanged here (Figs. 9 and 10 are chunk B; Fig. 27's one is the t̄ bar over its t);
  - figures with any text under 7 pt: 32, all from sub- and superscripts, with Fig. 18 and the chunk B and tier-2 figures as above.

## Chunk B: each data series drawn once

**The rule** (DECISION-20261119b, Joseph's words: "I just don't want there to be duplicates") comes with the
director's rulings (1) option (a), (2) option (i) and (3).
- **The method:** each figure is composed from the unchanged producers or pinned pickles in one process.
- **The checks:** every item of the installed figure must be present with an equal hash, and each added series must
  equal its source.

### Figs. 20 and 21 → one figure (fig:modedecomp; fig:mec labels it too)

- **The duplication** (palette pass's committed captures): Fig. 21's data line is Fig. 20's item for item (same
  hash). Its GENIE CV bars reach the top of Fig. 20's mode stack: the data − CV outline starts exactly there (relative
  difference 0).
- **The new series:** Fig. 21's only new series is the Valencia MEC addition.
- **The recipe:** `tools/compose_family4.py <note-figstyle-20261113/runs/family4/pickles> <out>`, under matplotlib 3.10.8.
  - It loads both pinned pickles through `restyle_family4.load()`, which checks the sha256, and changes no pickle byte.
  - It makes the palette pass's edits, then adds Fig. 21's six MEC rectangles to Fig. 20's axes, each a new
    Rectangle with the same geometry and style. The legend gains "+ Valencia MEC (2p2h)" after the modes.
  - Layout: `restyle_family4.restyle()`, unchanged, at full width (aspect 0.55, legend in 3 columns below).
- **Check** (`runs/f2021/CHECKS.txt`, `tools/check_compose.py`): CHECK-COMPOSE PASS. The 37 items are Fig. 20's 31
  plus Fig. 21's 6 MEC items, by full hash, and nothing else. Fig. 21's CV bars and data line are left out.
- **Caption:** the two captions merged. Every statement is kept: no 2p2h in the CV; Valencia 2p2h closes about half
  the low-E_avail gap (52 %); no 3D covariance; flux-repaired; the remainder in the enhancement region. The data − CV
  outline and the data points are now named (two grader F4 items).

### Figs. 7, 9, 10, 13 (fig:xsec, fig:ptslices, fig:pzslices; fig:model labels Fig. 7 too)

**The series**, from the producers and the committed captures:
- Fig. 7's projections and Figs. 9/10 draw the result and our simulation's truth (`hOFTruthDenom2D`, the prior).
- Fig. 13 draws the result, the published data, and MINERvA's published Tune v1 prediction from the ancillary file
  (`model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt`). That prediction is a different curve from the prior,
  under the same legend name: first p_T bin 1.362e-39 against 1.264e-39.
- Fig. 7's slice mosaic (`plot_2d_threeway_fig13.py`) draws the result, the published data with statistical-diagonal
  bars, and the prior, per slice.

**Recipe:** `tools/compose_tier2.py` under `note-figstyle-20261117/tools/remap_anc.py`, in the tier-2 ROOT
environment, with the inputs of the 2026-11-17 fetch (as the palette pass's tier 2).
- The four producers run unchanged in one process with the palette pass's restyle arguments. Their figures are held
  after the palette edits, not written.
- **(1) Fig. 13 into Fig. 7's projections.**
  - Fig. 13's This work equals the projection's (relative 3.4e-16 and 0), so the two share coordinates.
  - Fig. 13's published line is added as drawn. Its Tune v1 line is added dashed, as "Tune v1: published prediction".
  - The prior's entry becomes "Tune v1: our simulation (the prior)", and the ratio label "This work / prior".
- **(2) The mosaic into Figs. 9 and 10.**
  - Each of the 30 mosaic panels is matched to the slice panel whose This work points are proportional to its own: a
    constant ratio to 2.2e-16, which also pairs the bins.
  - The mosaic's prior, divided by that ratio, equals the slice panel's prior to 2.2e-16. So the mosaic draws the
    prior, not the ancillary curve, and nothing of it is lost.
  - Its published points and their statistical-diagonal bars, scaled by the panel's ratio, are added to Figs. 9 and 10.
    They include the unreported cells, as the mosaic drew them.
  - Each figure legend gains "Published (PRD 104, 092007)", and its prior entry names its source as in Fig. 7.
- **Checks** (`runs/tier2/CHECKS.txt`, `tools/check_tier2.py`, `runs/tier2/compose_tier2.json`): CHECK-TIER2 PASS.
  - **Projections:** 18 items = the installed 16 + Fig. 13's published line (equal full hash) + its Tune v1 line
    (equal xhash, restyled dashed).
  - **Slices:** every installed item is present with an equal hash. The 98 and 112 added items are all black (the
    published points), in every panel.
- **Not drawn now:** the mosaic (`MEFHC_5iter_fig13.pdf` stays installed, because the primer prints it) and Fig. 13
  (`model_comp_projections.pdf` stays installed and is included by nothing). Fig. 14 (`model_comp_ratio_maps`,
  ratios to the ancillary curve) is unchanged.
- **Captions:**
  - **Fig. 7:** it now names its two panels, every series and source, and the ratio panel. It keeps the bar
    statements, says the published data and prediction carry no uncertainties (Fig. 13's "Uncertainties are not
    drawn"), and points to Figs. 9 and 10 for the 2D cross section.
  - **Figs. 9 and 10:** "no published measurement is used" became "the panel χ²/n compares the result with the prior;
    the published points are shown for comparison and enter no statistic", as the director worded it. The
    statistical-diagonal bar statement moved from Fig. 7's old caption.
  - **Fig. 13's caption** is gone. Its claim (Tune v1 below the data in the peak) is Fig. 7's.

### Measured (base: the A2 head at 1f88c3d28)

- **Build:** rc 0, with 0 undefined references and no multiply defined label.
- **freeze_checks** (1, 3, 5, 7, empty allow-list) passes: 5511 = 5511 tokens.
- **quality_checks:**
  - 1b data-signal figure pairs go from 4 to 3. The pair Figs. 20/21 is gone.
  - The three left:
    - Figs. 9/10: the same result in its two slicings, both kept by the director's ruling;
    - Fig. 7 against Figs. 9 and 10: a projection's shape against single slices, one axes of four matched. It is not
      a redraw.
  - Content-signal pairs go from 11 to 7. Figures go from 36 to 34. Distinct printed widths go from 5 to 3, the three
    classes.
- **Grok:** one read on the caption and pointer hunks (`~/codex-reports/note-measurement/reads/figpass-B/grok/`).

### Pointers in files this lane does not own (routed, with the exact replacement)

The alias labels keep every reference resolving until the owners apply these. Then the aliases go.
- **P1, sec_results 6.1:** "Figure~\ref{fig:xsec} shows the unfolded … and its 1D projections." → the 1D projections,
  and Figs.~\ref{fig:ptslices}--\ref{fig:pzslices} slice by slice.
- **P2, sec_results 6.6:** \ref{fig:model} → \ref{fig:xsec}, "(dashed)" after "published ancillary files", and "the
  tune" → "that prediction".
- **P3, sec_results:** "Figures 9–10 compare … with simulated truth" gains "with the published points for comparison".
- **P4:** sec_3d's and app_history's \ref{fig:mec} → \ref{fig:modedecomp}.

## Chunk C: the graders' caption-match items

The Gemini figure graders ran at 1acece939 (`~/codex-reports/note-measurement/quality/1acece939/fig-*/issues.jsonl`).
Each item was checked against the PDF or the producer before any fix. Figure numbers below are those of 1acece939.

| item | verdict | fix |
|---|---|---|
| Fig. 12 (fig:tensionmodes) | real: the caption names two groups of three modes, not which panels | Panels follow diagnose_tension.py's χ²-contribution order. The tier-2 run's tension_report.txt gives lam_rank 23, 9, 118, 2, 79, 121 for (a)–(f). So the smallest-λ modes are (a), (b), (d) (λ/λmax 3.5e-9, 4.3e-10, 6.6e-11) and the moderate ones (c), (e), (f) (5.6e-5, 4.5e-6, 6.0e-5). The caption names them and the order. |
| Fig. 18 (fig:calibration) | real: the in-frame tags read "(a) pt", "(b) pz", "(c) eavail" (pdftotext) | no producer (ISSUES.md:1292). The caption says the tags denote p_T, p∥ and E_avail. |
| Fig. 19 (fig:3dmodels) | real: the producer prints a placeholder, `ylab + " (cm$^2$/.../nucleon)"` (re1/redraw_central_only_p3.py:147) | The units come from overlay_generators_band.AXES: cm²/(GeV/c)/nucleon for p_T and p∥, cm²/GeV/nucleon for E_avail. The producer strings are fixed (p3, p4), and the note figure's labels are fixed by `texts.tsv` on the pinned pickle (below). |
| Fig. 22 (fig:ascencio) | partly: the caption already maps the q3 intervals; the right panel has no y label (real) | The right panel takes the left's y label, and each panel prints its q3 interval above it (`labels.tsv`). The intervals follow compare_ascencio_fullcov.Q3_SUPER's populated columns, as the caption states. In p4's draw code, every panel now gets the label and the interval. |
| Fig. 32 (fig:gbdt-prior) | real: the panel titles say "\|bias\|" where the caption names the quantity the noise-free residual | The titles read "\|noise-free residual\|", the caption's own phrase (`texts.tsv`). Each title takes a third line so the panels do not collide. |
| Fig. 9 (fig:ptslices) | real (F4): "scaled" is not explained | One clause, from plot_2d_paper_comparison.py:91–96: each panel is divided by the largest value of the result and the prior in it, and the printed power of ten is 10^(−floor(log10 of that value)). |
| Fig. 15 (fig:landscape) | real (F2): the star overlaps its label | The label is moved 0.35 years left (`moves.tsv`). Every axes stays where the producer put it (boxes row −1). |
| Fig. 17 (fig:eavail-marg) | real: "pull" against "not formal … pulls" | In the Fig. 17 re-render chunk (the input was fetched on 2026-11-19). |
| Fig. 24 (fig:eavailWexcess) | check needed: the caption explains percentage shares the grader did not find | Routed to director-helper-3, owner of the §8 file. |

### How the figures were redrawn

No pinned input changed. The family-4 pickles are only read, each through `restyle_family4.load()`, which checks its
sha256 (the director's ruling).
- **Fig. 32 (`runs/gbdt/CHECKS.txt`):** `tools/arms_layout.sh` on `analyze.py --print-style` (matplotlib 3.11.2).
  - Arm 0 is EQUAL and 0 px against the installed file.
  - COMPARE PASS over all four gbdt figures.
  - The strings are equal after `texts.tsv`'s declared fixes. Text overlaps stay at 0.
- **Figs. 19 and 22 (`runs/f4fix/CHECKS.txt`):** `tools/arms_family4.sh`. Arm 0 is the palette pass's
  `palette_family4.py`, EQUAL-BUT-DATE and 0 px against both installed files. Arm 1 is `tools/fix_family4.py`.
  - **Labels:** `labels.tsv` is applied before the palette edits, so the added y label takes the power of ten as the
    left one does. That moves the right panel's "×10⁻³⁸" offset into its label and reprints its ticks as 1.2 … 1.5,
    the left panel's format. The check accepts exactly that move, and compares tick labels by value.
  - **Then:** the palette edits, `texts.tsv`'s fixes, and `restyle_family4.restyle()`, unchanged.
  - **Result:** every data item's full hash is equal (COMPARE PASS, 27 and 10 data artists), and the strings are
    equal after the declared edits.
- **Fig. 15 (`runs/land/CHECKS.txt`):** `ARM0=plain`.
  - Arm 0 is EQUAL and 0 px against the installed file.
  - COMPARE PASS (31 data artists). The strings are equal.
  - Its one capture overlap ("Pion production" against ν_e) is in arm 0 too.

### Producers fixed for any rerun

- `nd-unfolding/re1/redraw_central_only_p3.py` and `_p4.py`: the units per axis.
- `_p4.py`'s ascencio panels: the label and the q3 interval on every panel.
<!-- absence-ok: a scoping statement about this chunk's recipe (the figures come from the pinned pickles), not a claim that a result does not exist -->
- These scripts are not run here. The note figures come from the pinned pickles, which hold the drawn text, so the
  in-memory fixes above are what print.

## Chunk D: Fig. 17 redrawn from its input

- **The input** is config (a)'s 3D product `3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root`, copied read-only to the
  laptop on 2026-11-19.
  - The script was `~/cov2d-work/figfetch/fetch-3d-a.sh` (sha256 a067e07d…), run on the director's go, inside its window,
    under a clear fence.
  - Its sha256 is `0dd94830821576a3b060fae2d4a20564610c535ed06046cd1eb05cd11885dd59` on the node and on the laptop, the
    pin in re1/RE1-AMENDMENT-DECLARATION.md:151 and re1/run2/launch/re1_f_env.sh:2. The atime was unchanged.
  - RE-1 K3 read this file when it found the installed figure's values identical, with only the geometry differing.
- **Recipe:** `2d-unfolding/compare_to_paper_fullcov.py --ours <that file> --out-prefix <dir>/eavail_marginal_vs_paper`,
  unchanged, under `note-figstyle-20261117/tools/remap_anc.py`, in the tier-2 ROOT environment. These are RE-1 K3's
  arguments (re1/run2/launch/re1_f1.sbatch:23).
- **Arm 0** is the producer's default drawing. It no longer reproduces the installed 2026-07-03 PDF byte for byte
  (K3), so `INSTALLED_STRINGS=1` checks instead that every word and decimal value of the installed PDF's text appears in
  arm 0's drawn strings.
  - All do, including the annotation's 0.16, 0.83, 4.98 and the tag's 1.06.
  - The producer prints χ²/ndf = 4.981 and pull mean / rms 0.159 / 0.828, as in the installed figure and the note's text.
- **Arm 1** adds `layout_lib`'s edits:
  - a 6.5 × 7.5 in canvas, printed at \textwidth;
  - the grid panel and its colour bar above, the distribution below (`boxes.tsv`);
  - every text at least 10 pt (`layout.tsv`), so the superscripts print at about 7 pt;
  - `texts.tsv`: "pull" → "standardized difference", the caption's own term (the grader's F4 item), and "p_|| bin",
    "p_T bin" → $p_\parallel$ bin, $p_T$ bin.
- **Checks** (`runs/f17/CHECKS.txt`): COMPARE PASS (34 data artists, full hash). The strings are equal after the
  declared fixes. Text overlaps are 0.
- **In the note:** one float again, at \textwidth. The A1 continuation float is gone, and freeze_checks' SANS_CONTINUED
  (A1) is reverted: freeze_checks.py is byte-identical to director-helper-3's 201fb0037 version.
- **Measured (quality_checks):** smallest text 7.0 pt (the superscripts), word-like 10.0 pt, no text under 7 pt, no
  overlap.
- **Counts by chunk:** figures with any text under 7 pt go 30 (after B) → 29 (after C) → 28 (after D).
- **Fig. 22's one count:** figures with overlapping strings go 3 → 4 with C. The added one is Fig. 22, whose own
  label "$q_3\in[0.4,0.6)$ GeV" pdftotext splits at the ∈ glyph (extracted as "£"). It is one text, not two
  touching ones, and the page shows no overlap.

