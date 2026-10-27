# DECLARATION G-FIGURES: the 5D integration's figures, from committed readouts (2026-10-27)

**By** the measurement session, for the director to bind.

**Under:**
- `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` (PR #408), item 2: the 5D result is
  integrated into the paper and the note, and every number comes from a committed readout.
- `DECISION-20261026-joseph-5d-generator-comparison-presentation.md`: option 1 in the paper (the table and a ratio
  figure), option 4 in the note (adding a figure of the cell-contrast modes that carry the χ², with each
  prediction's distance along them).
- The director's request of 2026-10-27, which sets the three figures and the requirements below.

**Sibling:** [`FD-DATA-PRODUCT-DECLARATION.md`](FD-DATA-PRODUCT-DECLARATION.md), in the same PR, declares the
committed data-product readout. It shares this declaration's deploy (§2.1).

**Declares:**
- a figure tool, `nd-unfolding/fd_g_figures.py`, and its tests;
- an independent checker of the tool's outputs, `nd-unfolding/fd_g_figures_check.py`;
- the exact argv, the controls, the sidecar schema and the stop rule;
- the layout, colour and ordering choices, for the director (§7).

**MEASURES:** nothing. The tool has not run on the committed readouts. It has drawn only synthetic readouts, in its
tests.
<!-- absence-ok: a scoping statement about this session's own work: the tool is new in this commit; its tests read the committed readouts for their digests, schemas, pin chain and constants only (CommittedPins) -->

**CANNOT AUTHORIZE:**
- running it: the director binds first;
- a caption, a reading, a claim or printed wording, which are Joseph's;
- installing a figure in `docs/analysis-note/**`, which is the paper rewrite lane's.

**CITABLE FOR:** what each figure will draw, from which keys, and what makes the tool stop.

**NOT CITABLE FOR:** any result, or any figure's appearance on the real readouts.

## 0. Summary

Three figures, each a vector PDF with a sidecar JSON:

| figure | for | draws | from |
|---|---|---|---|
| `fd_g_fig_ratio` | paper | each prediction's data/prediction ratio f/g on R00–R15, with the error bar (f/g)·σ/f, where σ/f = √diag(C_total + C_resp)/f; GiBUU on its own axis below the others, on its eight p∥ < 4.5 cells only, as points, with nothing of it above p∥ 4.5; each cell's box in a five-row key under the axes | Stage G's readout (`f`, `g`, `sigma_total_over_f`, `label`) and the H2 definition (`reporting_cells[].box`) |
| `fd_g_fig_modes` | note | for each of the four 16-cell predictions, the three G-DIAG modes that carry most of the χ²: each mode's 16 loadings, its relative σ, its share of the χ², and the prediction's distance along it, projection/σ, in σ units | G-DIAG's readout, reported comparison, `relative_to_f` (`top_modes`, `modes_by_chi2`) |
| `fd_g_fig_sens` (optional) | note | the reported χ² against α for the five families (interaction, flux, detector, lateral, and the joint family), one panel per prediction, with G-SENS's label | G-FOLLOWUP's and G-SENS2's `sens.records` and `sens.label` |

**The arithmetic.** There is no new statistic. The only arithmetic is for display:
- f/g, and (f/g)·σ/f, which carries the data's relative uncertainty onto each ratio;
- in the alternative form (§7 item 1), 1 + `g_over_f_minus_1` and 1 ± σ/f;
- projection/σ, whose square is the mode's recorded χ² (control K4).

**How every plotted number is tied to its key:**
1. **The plot model holds the whole figure:**
   - its size;
   - its axes: position, limits and ticks;
   - its legends;
   - one item per drawn artist, with its gid, its axes, its style, its values and the readout keys they came from.

   The model is the sidecar's `plotted`.
2. **`paint()` draws the model, and nothing else.**
3. **Control K6 reads the drawn figure back and requires it to be the model, before anything is written:**
   - every value, style and axes, and every legend handle against its own series;
   - no artist with ink outside the model: no axes title, no axis label the model does not hold, and nothing drawn
     on the figure itself;
   - nothing clipped;
   - every text on the page, no two texts overlapping, and no text over a drawn point, error-bar end or bar.
4. **The tests** recompute every drawn number from the synthetic readouts' keys, independently of the tool's model.
   They assert the read-back artists against those numbers, and assert the declared wording, colours, markers,
   offsets and line styles as literals (§6.3).
5. **The checker** (§2.3) re-derives every item of every real sidecar's model from the committed readouts by its own
   code, which imports nothing of the tool. It holds the declared names, axes and wording as its own literals. An
   item no rule visits fails. It reads the model, not the PDF; K6 ties the PDF's figure to the model.

**Style:** the article's. The tool imports `publication/release/figs/make_figs.py`'s `style()`, `COLORS` and
`PDF_META`; it does not copy them. The output uses serif type (DejaVu Serif, 8 pt base, with 5.8–7.5 pt ticks, keys
and legends), TrueType-embedded fonts and no creation date, so the same versions give the same bytes (K8).

**Cost:** 0 node-h, on a login node, with no Slurm job and nothing written to CFS. Synthetic runs take about 2 s.

**Stop rule:** any refusal, any non-zero exit, or a run past 1.25 × its projected wall is reported unrepaired.

## 1. Inputs

All six are committed, and each is pinned in the tool (`PINS`, control K0):

| input | path under `$T` = `docs/orchestration/state/measurement-paper/5d-community-20261024` | sha256 | schema |
|---|---|---|---|
| Stage G's readout | `fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` | `fd-g-readout/2` |
| G-DIAG's readout | `fd/readout/fd_g_diag_readout.json` | `680dc5ef9c40b1ab006657ce020c6acac7e891c68ce36850cf7a7dd2df278d88` | `fd-g-diag-readout/1` |
| G-FOLLOWUP's readout | `fd/readout/fd_g_followup_readout.json` | `cd82517afdfb1dc8383580c8a4c57e82d9b87864e75d28528cb35c4455f6e379` | `fd-g-followup-readout/1` |
| G-SENS2's readout | `fd/readout/fd_g_sens2_readout.json` | `0f6568aba032e5d9a85f945048494d8fccde3525bb45a1762d6f5d5aaf15b77f` | `fd-g-sens2-readout/1` |
| F0b's readout | `fd/readout/fd_f0b_readout.json` | `b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b` | `fd-f0b-readout/1` |
| the H2 definition | `nd-unfolding/pv-ladder/readouts/h2_definition.json` (repository root) | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` | `h2-definition/1` |

**Not read:**
- No covariance, prediction or data product: the S1 `.npz`, C_resp's `.npz` and the s5p predictions are not opened.
- **S1's and C_resp's readouts** are not read separately. The two σ the ratio figure needs are already in Stage G's
  readout: √diag(C_total)/f in its variant record and √diag(C_resp)/f in `extra_block.relative_sigma`. F0b's readout
  records the same two from a second producer, `fd_f0_regrade.py`, and control K2 checks them against it.

## 2. Exact commands

**Definitions:**
- `P=/pscratch/sd/j/josephrb`.
- `B=$P/fd-g-figures-20261027`. It does not exist yet (login24, 2026-10-27T08:17Z).
  <!-- absence-ok: `ls -d /pscratch/sd/j/josephrb/fd-g-figures-20261027` on login24 at 2026-10-27T08:17:52Z printed 'No such file or directory' -->
- `D=$B/deploy/<pin8>`: a clean clone of the binding commit.
- `T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024`.
- `PY` as for Stage G: `env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B` (Python 3.11.14, numpy
  1.26.4, matplotlib 3.10.8 on login24, 2026-10-26).

### 2.1 Deploy and tests (login node; shared with the data product)

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_g_figures.py nd-unfolding/fd_g_figures_check.py nd-unfolding/fd_data_product.py \
    nd-unfolding/tests/test_fd_g_figures.py nd-unfolding/tests/test_fd_data_product.py \
    publication/release/figs/make_figs.py nd-unfolding/fd_g_compare.py nd-unfolding/s1_assemble.py \
    nd-unfolding/s5p_stage1_inspect.py nd-unfolding/pv-ladder/readouts/h2_definition.json \
    $T/fd/readout/fd_g_readout.json $T/fd/readout/fd_g_diag_readout.json $T/fd/readout/fd_g_followup_readout.json \
    $T/fd/readout/fd_g_sens2_readout.json $T/fd/readout/fd_f0b_readout.json $T/s1/readout/s1_assembly.json \
    docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json \
    docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/CRESP-REPORT.md \
    docs/orchestration/state/s5p/stage1/stage1_inspect.json nd-unfolding/tests/test_fd_g_compare.py \
    $T/FD-G-FIGURES-DECLARATION.md $T/FD-DATA-PRODUCT-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_g_figures test_fd_data_product test_fd_g_compare > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:**
- HEAD equal to the pin;
- 0 porcelain lines before and after;
- the §8 digests and the sibling's;
- `tests rc=0` with "Ran 85 tests … OK", as in §6.4: 47 figure tests, 11 data-product tests and
  Stage G's 27, which both import from.

Anything else is a STOP.

### 2.2 The run (login node, after §2.1)

The figures named, the form and the GiBUU axis are the director's choices at binding (§7 items 1, 2 and 8). This argv
draws all three in the defaults:

```bash
cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_g_figures.py \
  --g-readout $T/fd/readout/fd_g_readout.json --g-diag-readout $T/fd/readout/fd_g_diag_readout.json \
  --g-followup-readout $T/fd/readout/fd_g_followup_readout.json --g-sens2-readout $T/fd/readout/fd_g_sens2_readout.json \
  --f0b-readout $T/fd/readout/fd_f0b_readout.json --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --figures ratio modes sens --ratio-form data-over-prediction --gibuu-axis separate \
  --out-dir $B/figures > $B/logs/figures.out 2> $B/logs/figures.err; echo "rc=$?" >> $B/logs/figures.out
```

- **Projected wall:** 60 s. That allows for matplotlib building its font cache on a node where it has none; the
  synthetic runs take about 2 s. The timeout is 75 s, 1.25 × that.
- **Exit codes:**
  - 0: every control passed and the figures and sidecars were written;
  - 1: a control refused, or an output already exists (nothing written);
  - 2: argparse: a missing input, an unknown or repeated figure, or an unknown form or axis;
  - 124: past the timeout.

  Any exit other than 0 is a STOP.
- **stderr** carries fontTools' "'created' timestamp seems very low" lines. These come from the TrueType subsetting
  of a PDF with no creation date, and are expected.

### 2.3 The independent check (login node, after §2.2)

```bash
cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_g_figures_check.py \
  --g-readout $T/fd/readout/fd_g_readout.json --g-diag-readout $T/fd/readout/fd_g_diag_readout.json \
  --g-followup-readout $T/fd/readout/fd_g_followup_readout.json --g-sens2-readout $T/fd/readout/fd_g_sens2_readout.json \
  --f0b-readout $T/fd/readout/fd_f0b_readout.json --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --figures-dir $B/figures > $B/logs/check.out 2>&1; echo "rc=$?" >> $B/logs/check.out
```

- It must end "OK: … 0 failed, 3 sidecars" with `rc=0`, or "1 sidecars" if only `ratio` is drawn.
- Anything else is a STOP. It writes nothing.

**What is committed** (the report's PR):
- `$B/figures/*.pdf` and `*.json`, as `fd/figures/`;
- the logs and step scripts under `fd/receipts-g-figures/`;
- ledger rows.

The paper rewrite lane installs the figures it uses into `docs/analysis-note/figures/`. This session does not edit
that tree.

**The results index:** a sidecar's `plotted` holds keys the index treats as metrics (`chi2`, for example). If the
sidecars enter its population, the index is regenerated in-branch under the director's standing ruling (a). Their
rows are display copies, under their own keypaths, so R5 does not mark them `same_as` the readouts' rows.

## 3. Controls

Every control runs before anything is written, and each refuses: exit 1, nothing written. A later figure's refusal
leaves nothing of an earlier one, because nothing is written until every figure has passed.

| control | checks | tests (each planted defect asserts its own clause) |
|---|---|---|
| **K0** | No output exists, PDF or JSON. Each input's sha256 is its pin, and its schema is the declared one | `test_k0_pin_and_schema`; `test_no_overwrite` (a JSON, then a PDF); `test_a_later_refusal_writes_nothing`; `Invocation` |
| **K1** | **The chain.** <ul><li>G-DIAG, G-FOLLOWUP and G-SENS2 ran on this Stage G readout.</li><li>G-FOLLOWUP ran on this G-DIAG readout.</li><li>G-SENS2 ran on, and references, this G-FOLLOWUP readout.</li><li>All five readouts ran on this definition and on Stage G's S1 product.</li><li>C_resp is adopted and named C_resp, and every readout ran on it.</li><li>Stage G holds the five predictions in order, with `fd_g_compare.PREDICTIONS`' labels and digests.</li><li>Every readout ran on the same five, and G-DIAG holds them in the same order.</li></ul> | `test_k1_each_clause` (22 sub-tests, one or more per clause and readout); `CommittedPins` |
| **K2** | **The data and its error bar.** <ul><li>f and σ/f are the same on every prediction's cells.</li><li>Each prediction's reported covariance is C_total + C_resp.</li><li>f and g are positive, and g/f − 1 is `g_over_f_minus_1`.</li><li>**The bar is C_total + C_resp:** σ² = σ(C_total)² + σ(C_resp)², from the variant (named C_total) and the extra block, to 10⁻¹⁰ relative. A σ that also held V_g would fail.</li><li>F0b's √diag(C_total + C_resp)/f and C_resp σ are the same, to 10⁻¹⁰.</li></ul> | `test_k2_the_error_bar_is_c_total_plus_c_resp`; `test_k2_f0b_and_the_data`; `test_k2_k3_each_clause` |
| **K3** | **The cells.** <ul><li>The definition reports exactly R00–R15.</li><li>GiBUU's cells are Stage G's p∥ < 4.5 cells, the definition's and `fd_g_compare.GIBUU_CELLS`.</li><li>Every other prediction is on all 16.</li><li>Each group of four cells shares its p_T and p∥ box.</li><li>On the model, every GiBUU point and bar is on its eight cells, and its points are unjoined.</li><li>No GiBUU mode is drawn.</li></ul> | `test_k3_gibuu_cells`; `test_k3_the_definition`; `test_k3_a_gibuu_point_drawn_above_4_5`; `test_k3_gibuu_joined_by_a_line`; `test_gibuu_has_nothing_above_p_parallel_4_5` (both forms, both GiBUU axes) |
| **K4** | **The modes.** <ul><li>G-DIAG recorded three top modes.</li><li>Each prediction has one reported comparison, on C_total + C_resp + V_g, with Stage G's χ².</li><li>`top_modes[k]` is `modes_by_chi2[k]`, on all 16 cells, with its σ, χ² and fraction.</li><li>The modes are in descending χ².</li><li>The loadings are unit, and signed so that the largest \|loading\| is positive.</li><li>(projection/σ)² is the mode's χ², to 10⁻¹⁰.</li></ul> | `test_k4_modes`; `test_k4_each_clause` (7 sub-tests) |
| **K5** | **The sensitivity.** <ul><li>Both readouts' reported matrix, label and α are G-SENS's.</li><li>G-SENS2's referenced families are G-FOLLOWUP's.</li><li>Each prediction and family has one record per α.</li><li>α = 0 is Stage G's reported χ², to 10⁻¹⁰, with its ndf and label, and no χ² is none.</li></ul> | `test_k5_sens`; `test_k5_each_clause` (7 sub-tests) |
| **K6** | **The drawn figure is the model.** <ul><li>The drawn gids are exactly the model's, and every artist with ink is a model item: no axes title, no axis label the model does not hold, nothing drawn on the figure itself.</li><li>The axes' positions and limits are the model's.</li><li>Each line, error bar, rectangle, bar, reference line and text is drawn as the model holds it: its values to 10⁻¹², its style, and its axes.</li><li>The tick labels and axis labels are the model's, and no other axes show x tick labels.</li><li>Each legend entry shows its own series' handle.</li><li>**On the model:** each prediction's labels, texts and bars sit in its own data's axes, and each legend entry names its own series.</li><li>**Layout:** nothing is clipped; every text, tick and axis labels included, lies on the page; no two texts overlap; no text covers a drawn point, an error-bar end or a bar.</li></ul> | `test_k6_each_drawn_kind` (13 sub-tests); `test_k6_style_and_axes`; `test_k6_legend_handles_reversed`; `test_k6_a_model_label_on_the_wrong_row`; `test_k6_a_missing_and_an_unmodelled_artist` (with review C's title, axis label and figure-level line); `test_k6_the_band_and_the_page`; `test_k6_clipped`; `test_k6_text_over_text_and_over_bars`; `test_k6_a_point_drawn_off_the_model`; `test_k6_an_error_bar_and_a_loading` |
| **K7** | **The labels.** <ul><li>The five names differ, and none starts another.</li><li>Every drawn name is the start of Stage G's label for it, ending where the label has a ";", "," or ":".</li><li>Its qualifiers are the declared ones, each a substring of that label.</li><li>Wherever Stage G's label carries "prior (not an independent prediction)", "C12 target; no correction to CH applied" or "p_parallel < 4.5 cells only", the drawn name carries it.</li><li>The sensitivity note is G-SENS's label.</li></ul> | `test_k7_labels` (swapped names, a truncated name, a missing qualifier, a wrong one, the note); `test_k7_each_clause` |
| **K8** | **The PDF.** <ul><li>It has no raster image, its fonts are TrueType-embedded, and no Type 3 font is used.</li><li>Drawing it twice gives the same bytes.</li></ul> | `test_k8_raster_and_bytes`; `test_k8_a_type3_font`; `test_rel_and_check_pdf` (each clause on bytes); `test_same_bytes_in_two_processes` |

## 4. What each figure draws

### 4.1 `fd_g_fig_ratio` (paper)

**Form (default `data-over-prediction`):**
- each prediction is drawn as points at f/g on its cells, from `predictions[name].f` and `.g`;
- each point has the error bar (f/g)·σ/f, from `sigma_total_over_f`;
- a line is drawn at 1, labelled "data / prediction".

**Form `prediction-over-data`** (`--ratio-form`):
- the points are at 1 + `g_over_f_minus_1`;
- the data is a grey box per cell, 1 ± σ/f, on every axes;
- the predictions have no error bar, and the axis label is "prediction / data".

**GiBUU's axis (default `separate`):**
- **`separate`:** two axes, 7.0 × 5.0 in. The upper axes holds the four 16-cell predictions. The lower holds GiBUU on
  its eight cells, with R04–R07 and R12–R15 left empty. Each has its own y range.
- **`shared`** (`--gibuu-axis`): one axes, 7.0 × 4.3 in, with all five predictions on it.

**Layout:**
- **The x axis:** the 16 cells, R00–R15, at equal widths, with labels under the lowest axes. Inside each cell, the
  five predictions sit at fixed offsets in Stage G's order: −0.3, −0.15, 0, +0.15 and +0.3.
- **The groups:** thin vertical lines separate R00–R03, R04–R07, R08–R11 and R12–R15, which share p_T and p∥.
- **The key:** five rows under the cell labels give each cell's p_T, p∥, E_avail, q₃ and W interval. Each row is
  labelled with its axis and unit.
  - An interval is printed "all" when it is the axis's full range in `s5p_stage1_inspect.FINE`, "< x" or "> x" when
    it touches one end, and "x–y" otherwise.
  - The edges are the definition's `reporting_cells[].box`.
- **The legend:** above the axes, in two columns: each prediction's short name and its Stage G qualifiers (§7 item 4).
- **The y range:** each axes' own, from its points and bars and the line at 1, padded by 6 % and rounded out to 0.05.
- **What is not drawn:** no χ² is printed, and V_g is not drawn (§7 items 1 and 10).

### 4.2 `fd_g_fig_modes` (note)

**The grid:** 4 rows × 3 columns, 7.0 × 7.5 in.
- **The rows** are the four 16-cell predictions, in Stage G's order: GENIE CV, GENIE + MEC, NuWro and MnvTune v1.
  Each row is headed by its name and qualifiers.
- **The columns** are ranks 1–3 by χ²: `modes_by_chi2[0..2]` of the reported comparison's `relative_to_f` record.
  They are headed "rank k by χ²".

**Each panel:**
- the mode's 16 loadings as bars, from `top_modes[k].loadings`;
- the y range −1.05 to 1.75, with ticks from −1 to 1, labelled on the first column only. The panel's two text lines
  sit above 1, where no loading reaches, and K6 checks they cover no bar;
- the zero line and the group separators;
- two lines of text, from `modes_by_chi2[k]`:
  - "mode m: x.x% of χ²";
  - "σ = y.yy%, distance ±z.zzσ", where σ is the mode's relative σ and the distance is projection/σ.

**The sign.** G-DIAG's residual is d = (f − g)/f, and each eigenvector is signed so that its largest |loading| is
positive. A positive distance means the data lie above the prediction along the mode's direction as signed.

### 4.3 `fd_g_fig_sens` (note, optional)

**The grid:** 3 × 2, 7.0 × 6.6 in. Five panels hold the predictions in Stage G's order, and the sixth holds the
legend and G-SENS's label.

**Each panel:**
- χ² against α at α = 0, 0.1, 0.25, 0.5 and 1, for the five families:
  - interaction, from G-FOLLOWUP;
  - flux, detector and lateral, from G-SENS2;
  - the joint family, from G-FOLLOWUP, dashed;
- its ndf under the axis, at the right (GiBUU's is 8);
- its name and qualifiers, on two lines above it;
- its own y range, padded by 12 % of the curves' span.

**The legend** is titled "family shrunk". Each entry is built from the readouts' `constants.families`: "interaction
alone" … "interaction + flux + detector + lateral (joint)". Beneath it is G-SENS's label, "descriptive sensitivity of
the reported χ², not an alternative result", from both readouts.

## 5. The sidecar, `fd-g-figure-sidecar/1`

One per figure, beside its PDF:

```text
schema, labels{what, not}, figure, file, pdf_sha256, pdf_bytes, controls_passed[K0..K8],
inputs_sha256{g_readout, g_diag_readout, g_followup_readout, g_sens2_readout, f0b_readout, definition},
code{sha256{fd_g_figures.py, make_figs.py, fd_g_compare.py, s1_assemble.py, s5p_stage1_inspect.py}, commit, clean},
versions{python, numpy, matplotlib}, argv, options{ratio_form, gibuu_axis},
plotted{figure, ..., figsize, axes[{rect, xlim, ylim, xticks, yticks, off}], legends[...],
        items[{gid, kind, source[keys], axes, style, values}]}
```

- `code.commit` is the checkout's `git rev-parse HEAD`.
- `code.clean` says whether `git status --porcelain` is empty for the five code files. Both are null outside a git
  checkout.
- `plotted` is the full plot model: every drawn number and string, with the keys it came from. ratio's also carries
  the cell key (each cell's box and its printed intervals). modes' carries each panel's mode, σ, projection,
  distance, χ² and fraction. sens' carries each curve.
- **The item kinds** are `line`, `yerr`, `rects`, `bars`, `ref`, `text`, `legend`, `ticks`, `xlabel` and `ylabel`
  (the module's docstring above `item()`).

No key `p` appears in `plotted`, and a test asserts this.

**stdout** prints:
- the PASS lines;
- one `[FIG]` line per figure, with its number of drawn items and its bytes;
- one `wrote` line per file, with its sha256.

## 6. Code and tests

### 6.1 `nd-unfolding/fd_g_figures.py` (new, 907 lines)

| part | what |
|---|---|
| constants | `PINS`, `SCHEMAS`, `ORDER` and `SIXTEEN` (from `fd_g_compare.PREDICTIONS`), `TOP`, `ALPHAS`, `FAMILIES`, `SHORT`, `QUALIFIERS`, `REQUIRED`, `DISPLAY`, `COLORS` (four from `make_figs.COLORS`), `MARKERS`, `OFFSET`, `FAMILY_STYLE`, `KEY_ROWS`, `MODES_YLIM` |
| inputs | `load` (K0), `check_chain` (K1) |
| models | `ratio_model` (K2, K3), `cells_key` and `interval`, `modes_model` (K4), `sens_model` (K5), with `item`, `at`, `guides`, `grid_rects` and `padded` |
| drawing | `paint`, the only drawing code, through `draw(name, model)` |
| checks on the drawing | `readback`, `check_panels` (K6), `check_gibuu` (K3), `check_labels` (K7), `render` and `check_pdf` (K8) |
| outputs | `code_record`, `sidecar`, and `run`, which writes `.partial` files and then uses `os.replace`, after every figure has passed |

It imports `fd_g_compare` (the predictions, their labels, GiBUU's cells, `Stop`, `report`), `s1_assemble`
(`sha256`, and through it the axes and `FINE` edges) and `make_figs` (the style). It calls no covariance function.

### 6.2 `nd-unfolding/fd_g_figures_check.py` (new, 320 lines)

It imports nothing of the tool. Its declared layout and wording are written out as literals: the five names with
their qualifiers, the offsets, the key labels, the y labels and the three ranks. It re-derives every item of each
sidecar in a directory:
- **ratio:**
  - each prediction's points: f/g (or 1 + `g_over_f_minus_1`) at its cells plus its offset;
  - GiBUU's cells, against the definition's p∥ < 4.5 boxes;
  - the error-bar ends, and the band;
  - every key interval, against the definition's boxes, with the full range taken from the boxes' union;
  - every name, against Stage G's label and against the declared name;
  - the model's form and GiBUU axis, against the run's `options`; each prediction's axes, and each error bar's
    against its series';
  - the axis labels, the key labels, the reference lines, the separators and the ticks.
- **modes:** exactly three ranks for each of the four 16-cell predictions; every bar against the loadings of the
  rank-k mode by χ², in its row's column k; every printed mode index, fraction, σ and distance, to its printed
  precision; each row label, the declared name, over its own rank-1 panel; each column header over its column.
- **sens:** every curve against the records sorted by α, with the joint family alone dashed, in its prediction's own
  panel; every ndf; every name; every family name; the note against G-SENS's label.
- **For each sidecar:** its PDF's sha256 and its inputs' sha256.

An item no rule visits fails. It exits 0 if every check passes and 1 otherwise.

### 6.3 `nd-unfolding/tests/test_fd_g_figures.py` (new)

All but `CommittedPins` run on `FigTree`: six synthetic readouts with the committed readouts' key layout, consistent
with one another as the committed ones are, and the committed H2 definition. The fixture's matrix name, label and α
are its own literals, so a change to the tool's constants is seen.

| class | what it shows |
|---|---|
| `EndToEnd` (13) | <ul><li>**The run:** all three figures and sidecars are written. The sidecars' PDF digest, byte count, five code digests, commit and `clean` are recomputed. No `.partial` is left, and no key `p` appears.</li><li>**ratio, every form and GiBUU axis:** every point, error-bar end and box is read back and asserted against f/g, (f/g)·σ/f, 1 + `g_over_f_minus_1` and 1 ± σ/f, recomputed from the readout's keys. The bar's square is the variant's plus C_resp's. Each series' colour, marker, axes and legend handle is checked against literals.</li><li>**GiBUU:** the drawn x positions are exactly its eight cells, as unjoined points, and no GiBUU mode is drawn.</li><li>**The key** against the definition's boxes, with the expected strings written out.</li><li>**modes:** every bar, colour and axes. Every printed mode index, fraction, σ and distance is parsed and asserted to its printed precision, and the format is matched.</li><li>**sens:** every curve, axes, ndf, label, legend entry and the note.</li><li>**The declared layout and wording:** the y labels per form; the key's five labels and their order; the offsets; the line styles; the legend orders and title; the y ranges.</li><li>**The style is the article's:** serif type, TrueType DejaVu Serif, no creation date, and the four colours `make_figs.COLORS`'.</li><li>**The same bytes in two separate processes.**</li><li>**No overwrite**, of a PDF or a JSON.</li><li>**Nothing written when a later figure refuses.**</li></ul> |
| `Controls` (29) | Each control K0–K8 refuses its planted defects, with its own clause and nothing written (§3). The table-driven ones plant one defect per clause, and `test_tolerances` plants a defect between each tolerance and a looser one |
| `Check` (2) | The checker passes on the tool's output in every form and GiBUU axis. It refuses 16 planted sidecar defects: a point, an error-bar end, a key string, a name, the loadings, a printed σ, a row label's panel, a curve, an ndf, an unchecked extra item, the PDF digest, an input digest, and review C's four: a name cut at a delimiter, ranks 2 and 3 swapped, GiBUU on the wrong axes, and a model whose form is not the run's |
| `Invocation` (2) | As written (`-I -B`, cwd outside `nd-unfolding`), the real pins refuse the synthetic readouts at K0 with no traceback. Argparse exits 2 on four bad argvs |
| `CommittedPins` (1) | The committed readouts' digests are `PINS`, their schemas are `SCHEMAS`, and K1 holds on them. Their constants (top, α, families, matrix name, label) are the tool's and the fixture's. Nothing is drawn from them |

### 6.4 Test counts and the mutation check

- **Locally** (2026-10-27: Python 3.12.2, numpy 1.26.4, matplotlib 3.10.1), the figure and data-product modules and
  Stage G's ran 85 tests, OK
  ([`fd/receipts-g-figures/declaration/tests-local.log`](fd/receipts-g-figures/declaration/tests-local.log)).
- **Review B's mutants:** review B's 95 mutants of the second version were re-run against this code
  ([`fd/receipts-g-figures/declaration/mutants.log`](fd/receipts-g-figures/declaration/mutants.log)):
  - 93 of the 95 still apply; the other two name code the rewrite removed;
  - **86 are killed;**
  - **7 survive, each equivalent or harmless:**
    - V02 and V20 are equivalent: g/f equals 1 + `g_over_f_minus_1` to about 10⁻¹⁶, and the loadings' dict order
      is the cell order;
    - V03 changes the band's width, which is cosmetic;
    - O03 creates the empty output directory before the checks;
    - O04 writes without `.partial`;
    - E10 and E11 are clauses that other checks already guarantee: no GiBUU mode can exist, since `SIXTEEN` excludes
      it, and GiBUU's error bars share its points' x, which are checked.

## 7. For the director

Each choice below has a default, which the declared argv and code draw. Items 1, 2 and 8 are argv choices at
binding. The others are a small amendment.

1. **The ratio's form.**
   - **(a) data/prediction (default):** each prediction's f/g, with the bar (f/g)·σ/f. This is the request read
     literally, and the article's 2D Fig. 3 labels its ratio "data / prediction".
   - **(b) prediction/data (`--ratio-form prediction-over-data`):** g/f, against a grey data band 1 ± σ/f. This shows
     the data's uncertainty once per cell rather than on five points, and uses Stage G's `g_over_f_minus_1` with no
     division.
   - **V_g** (σ_Vg/f: at most 1.27 % for the 16-cell predictions, and 2.2 % for GiBUU) is in the χ² matrix but not
     drawn in either form. Drawing it as a second bar is an amendment.
2. **GiBUU's axis.**
   - **(default) `separate`.** In Stage G's readout, GiBUU's f/g runs from about 1.18 to 2.10, and to about 2.4 with
     its bar. The 16-cell predictions' f/g runs from about 0.84 to 1.32 (review A's reading of the committed
     readout).
   - **`shared`.** A shared axis would be set by GiBUU and would squeeze the other four into its lower part.
   - **Alternatives:** a log axis, or five stacked panels.
3. **The colours.**
   - The four generators take the article's colours (`make_figs.COLORS`).
   - **MnvTune v1 takes a grey (`#6b6b6b`),** new here. Grey marks it as the prior.
   - **The markers** are o, s, ^, D and v, so the five can be told apart in greyscale.
   - **The note's other figures** use `technote_style.py`, whose palette differs: GENIE is red and Tune v1 blue. The
     5D note figures follow the article instead (item 7).
   - **The families** take five colours outside the generator palette, with the joint family dashed black.
4. **The labels.**
   - **The legend names** are the start of Stage G's labels: "GENIE 2.12.10 CV, no MEC", "GENIE 2.12.10 + Valencia
     MEC", "NuWro 21.09", "GiBUU 2019" and "MINERvA Tune v1". They differ from the article's 2D legend
     (`make_figs.LABEL`: "GENIE CV", "GENIE + MEC", …).
   - **The qualifiers** follow, verbatim from Stage G's label:
     - NuWro and GiBUU: "C12 target; no correction to CH applied";
     - GiBUU: "p_parallel < 4.5 cells only", without a unit;
     - MnvTune v1: "prior (not an independent prediction)".
   - **GENIE's "; CH"** is not drawn, so the C12 qualifier is the only target named.
   - **Two substitutions:** "C12" is drawn as ¹²C, and "p_parallel" as p∥.
   - The wording is Joseph's when he sees the figures. That includes the axis labels, "rank k by χ²", "x% of χ²",
     "distance", "family shrunk", the units, and the absence of G-SENS's label from the modes figure.
5. **The modes.**
   - **Three per prediction (default),** as G-DIAG recorded (its `top` constant). They carry 71–83 % of the χ² for
     three predictions and 54 % for NuWro; the fraction is printed in each panel.
   - **The alternative** is each prediction's own 50 % count: 2 modes for three predictions and 3 for NuWro.
   - **GiBUU** is not drawn, following "for each 16-cell prediction". A fifth row on its eight cells is an amendment.
   - **The σ basis differs:** a mode's σ is from the full reported matrix, V_g included, while the ratio's bar is
     √diag(C_total + C_resp) without V_g.
6. **The sensitivity figure** is optional, and drawn only if `sens` is named at binding (item 8). Its panels' y axes
   do not start at zero, and their scales differ.
7. **The style.** All three figures use the article's style (`make_figs.style()`), so a prediction is one colour
   across the 5D paper and note figures. Using `technote_style.py` for the two note figures is an amendment. The text
   is 5.8–7.5 pt at the printed width of 7.0 in.
8. **Which figures run.** The declared argv names all three. Naming only `ratio modes` drops the optional one.
9. **The ordering:**
   - predictions in Stage G's order (`fd_g_compare.PREDICTIONS`);
   - cells R00–R15, with key rows p_T, p∥, E_avail, q₃, W;
   - families interaction, flux, detector, lateral, then joint.
10. **No χ² on the ratio figure.** The table carries it. A diagonal-only bar beside a χ² of 58–330 can read as
    agreement, so the caption, which is Joseph's, may need to say the χ² uses the full covariance. Printing each
    prediction's χ²/ndf in its legend entry is an amendment.
11. **After the figures are seen.** No-overwrite is enforced, and the stop rule forbids reruns. Before binding,
    please say whether a cosmetic rerun after Joseph sees the figures is covered by this binding. That would be the
    same inputs, a code change by amendment, and a new `--out-dir`.
12. **The committed readouts' K2–K5:** the tests run them on synthetic readouts only. Building the models from the
    committed readouts draws nothing, but it computes the figures' numbers, so it is not done before binding. Review
    C restated K1–K5 on the committed readouts and found each relation well inside its tolerance. The real run's
    numbers are then checked twice: K6 ties the figure to its model, and the checker (§2.3) ties the model to the
    readouts.

## 8. Pinned bytes

Their sha256 at this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_g_figures.py` | `06233dd9ddafe19807e97b42a4f4047b989b8cd8511d47cb8f5ad29f85652b4c` (new) |
| `nd-unfolding/fd_g_figures_check.py` | `95cf26811993772063a9d64d862fcde041ec3321f1f69874b99034d88c17d341` (new) |
| `nd-unfolding/tests/test_fd_g_figures.py` | `fb3dcc86e01eb48aaf7bed36bf5f1f25d624e3a6216ba5fddecc892347172fd9` (new) |
| `publication/release/figs/make_figs.py` | `4e18c26681fc86dcfef2861c7c0126aa2df4839376d967b18f08a7d77664ee67` (unchanged) |
| `nd-unfolding/fd_g_compare.py` | `0a3c09cdf2e27821c488c8a0d783af1537714144cce5415c6cb226ec8096df1f` (unchanged) |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` (unchanged) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` (unchanged) |
| the six inputs | §1 |

## 9. Ledger, storage and stops

- **Ledger:** rows in `fd/LEDGER.tsv` for §§2.1–2.3. There is no Slurm job, so 0 node-h.
- **Storage:** `$B` holds the deploy clone (about 580 MB), the logs, the figures (about 100 kB of PDF, and 140 kB
  of sidecars on the synthetic readouts) and the data product. Nothing goes to HPSS or CFS.
- **Stops:** any STOP is reported to the director unrepaired. Nothing is rerun without the director.

## 10. Not changed

- Every readout, report, covariance and cell. The figures read the readouts and change none of them.
- `docs/analysis-note/**`. The paper rewrite lane installs the figures.
- No GPU and no premium QOS.
- Captions, the reading of any figure, claims, printed wording and publication are Joseph's.

## 11. Review dispositions

Three independent read-only reviews ran:
- **A** checked the first draft against the request and the records;
- **B** attacked the code with mutations in a mirror: 167 mutants on the first version, then 95 on the second;
- **C** reviewed the revised draft and its sibling, both tools and the receipts. Its two MAJOR findings were in the
  data product (the sibling's §10). For this tool it found the following.

| # | finding | disposition |
|---|---|---|
| A-M1 | K7 compared each name with the tool's own constant, so swapped names passed every control and test | K7 requires each name to be the start of Stage G's label, ending at a delimiter, and the five names to differ. The tests assert the names as literals. Swapped and truncated names refuse |
| A-M2 | K6 checked each gid's values but not its series or panel: reversed legend handles and misplaced row labels passed | The model carries each item's axes and style, and the legends. K6 checks each artist's style and axes and each legend handle against its own series. `check_panels` checks the model's placement. Both defects refuse |
| A-m1 | GiBUU joined by a line, and gid-less GiBUU-like points, passed | K3 requires GiBUU's points unjoined; K6 requires every artist with ink to be a model item |
| A-m2 | The real run's numbers were asserted only against the tool's own model | `fd_g_figures_check.py`, an independent re-derivation from the committed readouts, is §2.3 |
| A-m3 | §7 item 10 said the sidecars would be `same_as` rows | Corrected (§2.3): their keypaths differ, so they are not |
| A-m4 | The sidecar's code record omitted `s1_assemble.py` | Added; the test checks all five digests |
| A-m5 | The test receipt was gitignored and its rc empty | Force-added, regenerated with the exit status captured (zsh's `pipestatus` had left it empty) |
| A-m6 | Wording: "imports no covariance code", "8 pt", p∥'s lower edge, the 100 GeV caps as "the analysis range", a 5-minute projection | Corrected: "calls no covariance function"; the sizes stated; the key prints the edges and its rule (§4.1); the outer edges named as the grid's; 60 s projected |
| A-m7 | The mode's sign was given without d's | §4.2 gives d = (f − g)/f |
| A-§6 | GiBUU's f/g range squeezes a shared axis; text over bars; legend names versus the article's; σ basis; no χ²; reruns after viewing | GiBUU on its own axis by default (§7 item 2); the modes' text above 1 and checked by K6; §7 items 4, 5, 10 and 11 |
| B (v1, v2) | 98 survivors on v1, 75 on v2: the y label, overwriting a PDF, a write before a later refusal, the offsets, the dashed joint family, the legend order, the sidecar's digests, commit and bytes, and unexercised clauses of every control | Each has a planted defect or a literal assertion (§3, §6.3). The re-run's survivors are in §6.4 |
| B weak | The style test called `style()` itself; the fixture used the tool's constants; `rcParams` carry over between tests | The style is checked in the PDF the run wrote (DejaVu Serif, TrueType); the fixture's matrix name, label and α are literals; every run calls `style()` first |
| C-1 | A name cut at a delimiter ("GENIE 2.12.10 CV", dropping "no MEC") passes K7 and the checker's label rule | The checker holds the five declared names as literals and refuses any other; a planted cut refuses. K7 still accepts a cut at a delimiter |
| C-2 | An axes title, an axis label the model does not hold, and a figure-level line passed K6 | K6 refuses each; axis labels join the page and overlap checks. All three are planted |
| C-3 | The checker did not check axes, rank columns, distinct panels, the run's options, or exactly three ranks | Each is checked; four planted sidecar defects refuse (§6.3) |
| C-4 | K1's sub-test count (22, not 23); §2.1's digest list lacked the Stage-1 receipt and `test_fd_g_compare.py`; the logs are gitignored | Corrected; added, with `CRESP-REPORT.md`; the logs force-added |
| C-5 | The mutation receipt did not name the code it mutated | `mutants.log` gives the mutated file's sha256, and the mutants were re-run on this declaration's code |
