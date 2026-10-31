# Figure and table diagnosis: plan (approved by the director, 2026-10-30)

**Why.** Every rater so far has read `pdftotext` output only, so nothing has judged the figures' and tables' layout,
legibility or visual quality (Joseph, via the director, 2026-10-30). This study judges them against the three PRD
anchors already used for P1, and lists the changes that would bring each one to the anchors' standard.

**Scope and status.** It is diagnosis only. No figure, table, caption or producer changes until the director has the
report and rules. It runs in parallel with Step 3 (the note round), and shares no files with it.

## 1. What is judged (the population)

| set | items | source |
|---|---|---|
| **Paper figures** | 4 | every `\includegraphics` in `paper_body.tex`: `paper_fig1_validation`, `paper_fig_bkg_residual`, `paper_fig_deformation`, `fd_g_fig_ratio` |
| **Paper tables** | 4 | every `table`/`table*` in `paper_body.tex` (lines 56, 167, 202, 242 at `e33a1ab0`) |
| **Note main-result figures** | 14 | every `\includegraphics` in `sec_results.tex` (11), `sec_eavailw.tex` (2) and `sec_fived16.tex` (1): the sections that report a result. The diagnostic sections (`sec_5d`, `sec_3d`, `sec_systematics`, …) are out. |
| **Anchor figures and tables** | 35 figures, 5 tables (by caption count; confirmed when cropped) | arXiv 2504.06857v2 (A), 2002.12496v2 (B), 2205.05084v2 (C), the versions of `rater-calibration/REPORT.md` §1 |

- Note tables are out unless you want them; the paper's four tables are the ones a PRD reader sees.
- **Your call:** is "main-result figures" the 14 above, or a narrower set, for example the note figures that the paper
  reuses or cites?

## 2. Rendering (fixed, scripted)

`tools/render_regions.py` writes one PNG per item, at **300 DPI and printed size**. A figure is cropped from its PDF
page, not rendered from its source file, so the rater sees what the reader sees: the page's scale, the caption, and
the column or two-column width.

- **Crop boxes.**
  - For our two PDFs, the box comes from the float's position in the build. A `\pdfsavepos` probe is used if
    `pdftotext -bbox` caption anchors prove ambiguous.
  - For the anchors, boxes come from the caption anchors of `pdftotext -bbox`, with a manual box only where those fail.
  - Every box is recorded in `crops.tsv` (document, page, box, caption's first words), with the sha256 of the source
    PDF and of the PNG.
- **Variants given to the rater with each figure:**
  - the colour render;
  - a greyscale render (`magick -colorspace Gray`);
  - a deuteranopia simulation, from a cited implementation (colorspacious, Machado et al. 2009) or none. I write no
    colour matrix from memory.
- **Measured, not rated: printed text size.** For our figures and the anchors', `pdftotext -bbox` on the cropped
  region gives the printed height of every vector text glyph.
  - The report gives the minimum and median printed point size per figure, and the anchors' distribution beside ours.
  - A raster figure, whose text cannot be measured this way, is reported as such.
- **Copyright.** The anchors' PDFs and PNGs stay in scratch and are not committed. The repository gets the crop boxes,
  digests, scores and quotes, so anyone with the arXiv PDFs can reproduce the crops.

## 3. The raters

- **GPT:** `codex exec -i <png>` on codex-school2 (gpt-6.1-sol, read-only), the account `run_x.sh sol2` uses.
  `codex exec --help` lists `-i, --image`.
- **Gemini:** agy (gemini-3.8-flash-high) has no image flag. It may be able to open a PNG in its workspace with its
  own tools, and that is unknown.
- **A vision probe comes first,** for each rater: a PNG of a random 8-digit number drawn in a figure-like plot. A rater
  that does not return the number exactly, twice, is not used.
  - If agy fails, the study runs on GPT only, and the report says so. I would not substitute an unlisted account.
- **Inputs per call:** the item's PNGs, the rubric prompt and the caption text. Our items and the anchors' are
  presented the same way, one item per call, in a shuffled order, with no document names. A reader of PRD may still
  recognize a published figure; this is not controlled.

## 4. The rubric (prompt F1, fixed before any score)

Each dimension is scored 1–5, with each level defined in the prompt, as P1's are. Every score below 4 must name the
visible element at fault.

1. **Legibility at printed size:** font sizes, line weights, marker sizes, as printed.
2. **Layout and panel organization:** panel order and labelling, shared axes, whitespace, aspect ratio.
3. **Colour:** distinguishable in colour, in greyscale and under the deuteranopia simulation; no rainbow palette for
   ordered data.
4. **Axis labels and units:** every axis labelled with its quantity and unit, with tick labels readable.
5. **Comparison with the cited predictions:** whether the data and each prediction are distinguishable and directly
   comparable, for example on a ratio or residual panel or a shared scale.
6. **Legend:** placement, obstruction of data, consistency with the caption.
7. **30-second read.**
   - The rater writes, in one sentence, the main result it takes from the figure, given about 30 seconds.
   - It also rates the ease of doing so.
   - I check that sentence against the paper's own statement of the result, with a fact probe as in the ledgers. A
     wrong takeaway counts as a finding even when the rated ease is high.
8. **Against the anchors:** see the pairwise step below.

The reply ends with **CHANGES**: specific, numbered changes, each naming the element and what to do (for example
"increase the tick-label font of panel (b) to match the axis labels").

**Tables** take the same render. Their dimensions 1, 2, 4, 6 and 7 are adapted:
- legibility;
- rules and alignment (decimal alignment, grouping);
- units and headers;
- whether the caption makes the table self-contained;
- the 30-second read.

### The pairwise step (dimension 8)

- Before any score, each of our 22 items is matched to the anchor item of the same kind, recorded in `match.tsv`. The
  kinds are: data against predictions, ratio or residual panels, a 2D map, closure or validation, a χ² or results
  table.
- **The pairwise prompt F2** asks which of the two better meets PRD's standard on each of dimensions 1–7, and which
  changes would close the gap. It is blind, and run in both orders.

## 5. Controls (each must behave, or the run is void)

- **Planted degraded figure (must be flagged).** `paper_fig_deformation` is re-rendered with:
  - its content scaled to 50 % inside the same box, which halves every font and line weight;
  - its palette remapped to a saturated red/green pair.

  It enters the population under an anonymous id. To pass:
  - legibility ≤ 2 and colour ≤ 2 from each rater;
  - its CHANGES name font size and palette.

  Neither model is told a control exists.
- **Duplicate (consistency).** One of our figures enters twice under two ids. Its two score sets should agree within 1
  on every dimension. The disagreement is reported as the rater's noise floor, and smaller differences between items
  are not read as findings.
- **The vision probe** (§3).

## 6. Classification of each proposed change

Each change in CHANGES is classified by two classifiers working independently: this lane and a fresh agent with no
history. Where they disagree, the stricter class wins.

- **STYLE:** done by the producer's options or `technote_style.py` through `make_figures.sh`, or by LaTeX alone (width,
  `figure` against `figure*`, placement). Every plotted value stays the same.
- **CONTENT:** needs a number, curve, band or panel not currently computed or plotted, for example a ratio panel that
  needs a new computation, or a prediction not yet drawn.
- **PROTECTED:** would change what a figure or table says, or text that a protection holds. That includes:
  - a held caption sentence;
  - the FROZEN and gate-bound phrases;
  - Joseph's presentation decisions: the χ² table prints χ² with its ndf and only the shape-only companion
    (`DECISION-20261027-joseph-chi2-table-format.md`); the paper's generator-comparison table and ratio figure
    (`DECISION-20261026-joseph-5d-generator-comparison-presentation.md` item 1); no diagonal-only χ² (item 3);
  - DECISION-20261025's "no … figure meaning changes".

**A cost note for STYLE:** `make_figures.sh` runs its producers at NERSC (`REPO=/pscratch/…`). Before costing any
STYLE change, I will establish which producers run locally from committed inputs.

## 7. Size and output

- **Size, as approved** (§8): `data/jobs.tsv` holds 302 calls, plus 4 probe calls.
  - Absolute scoring, 174 calls:
    - our 32 items and the 2 controls, 2 raters × 2 reps: 136;
    - the 14 matched anchors and the 5 calibration anchors, 2 raters × 1: 38.
  - Pairwise, 128 calls: 32 items × 2 raters × 2 orders.
- **Report:** `FIGURE-DIAGNOSIS-REPORT.md` gives:
  - per item: scores (§8 rule 4), the measured text sizes against the anchors', the takeaway check and the classified
    CHANGES;
  - the controls' results;
  - a ranked list of the STYLE changes worth making first.

Nothing is changed before the director rules on the report.

## 8. The director's answers (2026-10-30), and what the tools implement

1. **Note population:** every figure in `sec_results`, `sec_eavailw` and `sec_fived16`, as proposed. The **note's
   result tables join**: every table in the same three sections.
   - Counted per float environment (`tools/figdiag.py items`), this gives **32 of our items**: the paper's 4 figures
     and 4 tables, 11 note figure environments and 13 note tables.
   - The anchors give 40 items: A 12 figures and 4 tables, B 16 figures and 1 table, C 7 figures.
2. **Anchors: matched items only,** plus 5 unmatched anchor figures scored as a calibration of the rubric's scale.
   - `data/match.tsv` pairs each of our 32 with an anchor item of the same kind, fixed before any score. 14 distinct
     anchor items are matched.
   - `data/calibration.tsv` holds the 5, chosen by the rule fixed on 2026-10-30: of the anchor figures that are not
     matched, the lowest-numbered 2 from A, 2 from B and 1 from C.
3. **GPT-only is acceptable** if agy fails the vision probe. The report says so, and no unlisted account is
   substituted.
4. **The degraded control must pass** for a rater before that rater's real scores are used (`tools/fig_score.py`,
   rule 2, both reps).
5. **The anchors' PDFs and crops stay out of git.** The repository holds their digests and crop boxes
   (`data/items.tsv`, `data/crops.tsv`, `data/renders.tsv`).
6. **The report comes to the director** before any figure or table changes.

## 9. Files

- `tools/figdiag.py` does the inventory, crops, renders, measured text sizes, captions, the planted control and the
  probe image.
  - Crop failures that the visual inspection of every crop found are fixed in `data/crops-override.tsv`, with the
    reason for each (6).
- `tools/fig_jobs.py` writes the job list (`data/jobs.tsv`). `tools/fig_runs.py` and `tools/run_vision.sh` run it.
  `tools/fig_score.py` holds the rules of §3 and §5.
- The prompts are `prompts/F1.prompt.txt` (figures), `F1T.prompt.txt` (tables), `F2.prompt.txt` (pairwise) and
  `PROBE.prompt.txt`.
- The colour-blindness renders use colorspacious 1.1.2's sRGB1+CVD model, deuteranomaly at severity 100: Machado et
  al. 2009, as that library implements it. It is installed outside git and pointed to by `FIGDIAG_PYLIB`.
