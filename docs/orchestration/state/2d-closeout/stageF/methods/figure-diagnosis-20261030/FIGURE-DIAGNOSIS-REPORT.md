# Figure and table diagnosis: report (2026-10-30)

The plan is [PLAN.md](PLAN.md), approved by the director. Its rules, prompts and tools were committed before any
rating. **Nothing in the paper or the note has been changed.** Every change below is a proposal for the director.

## 1. Result in brief

- **The paper's figures and tables are at the anchors' standard.**
  - Their mean scores match or exceed the three PRD anchors' on most dimensions.
  - Against its matched anchor item, each wins the pairwise comparison for gemini, 8 of 8. For sol they win 4, lose 3
    and tie 1.
- **The note's result figures are below it.**
  - They lose their pairwise comparison nearly throughout: gemini 10 of 11, the exception being Fig. 30; sol 8 of 8
    of those with a complete pair.
  - They score about 3.0 to 3.2 on every dimension.
  - Their measured text is the smallest of any group: a median minimum glyph height of 2.5 pt, against the anchors'
    4.0 to 6.3 pt.
  - Eight independent rater runs agree on the same fixes, nearly all STYLE: larger text, math-typeset labels instead of
    raw ASCII, slice labels and physical units, and no blank bands.
- **The note's tables are close to the anchors,** apart from their captions (D6).
- **Two figure–caption mismatches are real defects,** confirmed by inspection:
  - note Fig. 13's caption calls MINERvA Tune v1 orange, but it is drawn blue;
  - note Fig. 25's caption claims a feature of the high-W, high-E_avail corner that its 1D projections cannot show,
    and speaks of a band that is not drawn.
- **12 of 128 thirty-second takeaways were wrong.** Most misread a bias test or a descriptive number as a model test,
  or ranked χ² values across different ndf (§5).

## 2. Method as run

- **Population:** 32 of our floats (§1 of the plan) and 19 anchor items: 14 matched, plus 5 for calibration.
  - The anchors are arXiv 2504.06857v2 (A), 2002.12496v2 (B) and 2205.05084v2 (C). Their PDFs and crops are not in
    git.
  - Every crop was inspected visually. Six needed an override, each with its reason (`data/crops-override.tsv`).
- **Raters and accounts:**
  - **sol** (gpt-6.1-sol) ran on **codex-school** for every scored call. codex-school2 had reported its usage limit
    until 2026-11-04, and the director accepted the change. Each output records its account.
  - **gemini** (gemini-3.8-flash-high) ran through agy. Its first control calls produced nothing, because agy tried a
    shell command that headless mode denies. Its instruction now says to use the file viewer only. No permission was
    widened, and no score existed before the change.
- **Controls** (fixed rules, `tools/fig_score.py`):
  - **Vision probe:** both raters read the 8-digit number exactly, twice.
  - **Degraded figure** (paper Fig. 3, content at 50 % with a red-green palette): both raters flagged it in both reps,
    with D1 ≤ 2 and D3 ≤ 2, naming font size and palette (sol D1 2, D3 2; gemini D1 2, D3 1). Both raters' scores are
    therefore used.
  - **Duplicate** (paper Fig. 4 under a second id): the **noise floor is 2 points for each rater**. A single item's
    score can move by 2 between identical inputs. So no single-item score difference of 2 or less is read as a
    finding. The findings here rest on agreement across items, raters and reps.
- **Completeness:**
  - Absolute scoring is complete for both raters.
  - **sol's pairwise is partial: 39 of 64 calls.** codex-school ran out of credit partway through. The missing pairs
    are mostly the note's tables and three note figures; gemini's pairwise is complete. The figure study's image calls
    drained the account, which also stopped r22 Step 3's sol runs. That is recorded with Step 3.
- **Input defect, disclosed:** for note Fig. 25 only, the caption text given to the raters ran on into the following
  body paragraph. The crop override fixed the image box, not the caption bounds that the caption extractor read. The
  image the raters saw was correct.

## 3. Scores by group

The mean over items is given for each dimension, 1 to 5. Each item's score is the mean over raters of the median over
reps.

| group | kind | n | D1 legibility | D2 layout | D3 colour | D4 axes / headers | D5 comparison | D6 legend / caption | D7 30 s read |
|---|---|---|---|---|---|---|---|---|---|
| paper | figure | 4 | 3.81 | 3.69 | 3.44 | 3.94 | 3.94 | 4.31 | 3.81 |
| note | figure | 11 | 3.16 | 2.98 | 3.18 | 3.09 | 3.39 | 3.52 | 3.07 |
| anchor A | figure | 4 | 3.50 | 3.50 | 2.62 | 4.25 | 4.12 | 4.00 | 3.62 |
| anchor B | figure | 8 | 4.00 | 3.69 | 2.31 | 3.94 | 3.81 | 3.94 | 3.56 |
| anchor C | figure | 2 | 4.50 | 3.50 | 3.25 | 4.25 | 3.00 | 3.00 | 3.50 |
| paper | table | 4 | 4.50 | 3.38 | — | 3.94 | — | 3.25 | 4.06 |
| note | table | 13 | 4.54 | 3.48 | — | 3.31 | — | 3.04 | 3.65 |
| anchor A | table | 4 | 4.62 | 3.38 | — | 3.75 | — | 3.88 | 4.12 |
| anchor B | table | 1 | 4.50 | 3.00 | — | 4.00 | — | 3.00 | 4.00 |

**Measured printed text** (`data/text-size.tsv`, glyph-box heights from the PDF on each crop, figures only):

| group | figures measured | median of each figure's minimum | median of each figure's 10th percentile |
|---|---|---|---|
| paper | 4 | 3.15 pt | 5.63 pt |
| note | 11 | 2.48 pt | 5.39 pt |
| anchor A | 3 | 6.26 pt | 6.26 pt |
| anchor B | 16 | 4.41 pt | 5.05 pt |
| anchor C | 7 | 4.03 pt | 12.18 pt |

The smallest single glyph is in note Fig. 11 (0.83 pt). An anchor figure has one almost as small (C Fig. 7, 0.89 pt),
so one figure's minimum is not a finding by itself; the group medians above are.

**The anchors' colour scores are low (2.3 to 2.6).** Under the greyscale and colour-blindness renders, the raters
marked many published figures down too. D3 is the dimension on which our figures most often match or beat the anchors.

## 4. Pairwise against the matched anchor (`data/pairwise.tsv`)

A rater favours an item only if it picks it in both orders. Otherwise the result is a TIE.

| | sol (39 of 64 calls) | gemini (64 of 64) |
|---|---|---|
| paper, 8 items | ours 4, anchor 3, tie 1 | ours 8 |
| note figures, 11 | anchor 8 (3 without a complete pair) | anchor 10, ours 1 (Fig. 30) |
| note tables, 13 | anchor 2, tie 1 (10 without a complete pair) | ours 5, anchor 5, tie 3 |

## 5. Takeaway check (`data/takeaway-check.tsv`)

Each rater's one-sentence takeaway was checked against the item's caption and the text that discusses it: 87
CORRECT, 29 PARTIAL, 12 WRONG. The 12 WRONG fall into three kinds.

**A bias test or a descriptive number read as a model test:**
- paper Table II: "strongly excluded";
- note Tables 14, 15 and 18;
- paper Fig. 3: "within … uncertainties", where the text says "in about half of those cells" and the covariance fails
  its criteria;
- paper Fig. 1: overlapping correlated bands read as agreement, which the caption rules out.

**χ² ranked across different ndf:** two raters, on paper Table IV and note Table 16, called GiBUU best overall. Its
58/8 is 7.3 per degree of freedom, against GENIE CV's 109/16 at 6.8.
- The tables print χ² and ndf as pairs, under Joseph's DECISION-20261027.
- This is reported as a reading risk for Joseph, not proposed as a change.

**Misread numbers:** note Fig. 11 (mode count), note Table 17 (which predictions agree best).

## 6. The proposed changes (`data/changes.tsv`)

The raters' change lists were consolidated into 366 distinct changes and classified twice: by a lane classifier, and
by a fresh agent who did not see the first labels. They agreed on 354. Where they disagreed, the stricter class was
taken.

- **STYLE: 303.** Plot 130, LaTeX 122, caption wording 51.
- **CONTENT: 32.**
- **PROTECTED: 31.**

### The STYLE changes worth making first

These are ranked by the number of rater runs that proposed each, out of 8. All are in the note's 2D result figures,
whose producers are the `2d-unfolding` scripts that `make_figures.sh` runs at NERSC.

1. **note Fig. 13: resolve the colour mismatch** (8 of 8). Tune v1 is drawn blue but the caption says orange. This is a
   factual error, fixable by recolouring the line or by correcting the caption.
2. **Typeset axis, legend and colour-bar labels in math, not ASCII** (8 of 8): Figs. 11, 12, 13 and 14, and 7 of 8 for
   Fig. 8. Examples are `p_T (GeV/c)`, `MINERvA_Tune_v1` and `dσ/dpt`.
3. **Label every slice panel with its interval and an identifier, and give the y axes physical units with the scale
   factors defined** (8 of 8): Figs. 9 and 10.
4. **Remove blank bands and enlarge the panels into the space** (8 of 8): Figs. 9, 10 and 11.
5. **Enlarge tick labels, axis titles, legends and annotations to printed size** (7 to 8 of 8): Figs. 7, 8, 10, 11 and
   14. This matches the measured 2.5 pt median minimum.
6. **Panel labels and titles,** "(a) Our result" and "(b) Published data" (8 of 8): Fig. 14.
7. **"Pull" on Fig. 8's axes should read "standardized difference"** (8 of 8). The caption says it "is descriptive, not
   a pull".

**For the tables,** the most supported changes are LaTeX-only: a column header over note Table 8's first column (7 of
8), and a symbol key in its caption (7 of 8). Most other table changes concern rules, alignment and units in headers.

### CONTENT (32) and PROTECTED (31): not to be done without a ruling

**CONTENT, the most supported:**
- mode rank and eigenvalue annotations on note Fig. 12 (8 of 8);
- ratio or residual panels on note Figs. 9, 10, 13 and 25 (3 to 7);
- uncertainty bars on Fig. 13's data (6);
- a 2D or corner view supporting Fig. 25's statement (2).

**PROTECTED:**
- every request to print χ²/ndf, on paper Table IV and note Table 16 (Joseph's χ² format);
- changes to printed precision or notation (note Tables 6, 15 and 17);
- uncertainties on note Figs. 24 and 25, which the five-axis covariance does not support (it fails its acceptance
  limit);
- captions shortened by dropping qualifiers (note Tables 12 and 15, Figs. 9 and 14).

## 7. What a change would cost

- **The producers differ by figure.**
  - The note's 2D result figures come from `2d-unfolding` producers, which `make_figures.sh` runs at NERSC
    (`REPO=/pscratch/…`).
  - The sixteen-cell figures come from `nd-unfolding/fd_g_figures.py`, and VALUES-FIVED16 pins them ("2 figures equal
    their sources").
  - Paper Fig. 1 is a digest-pinned copy of a redraw (`make_figures.sh:190-200`).
- **No producer found:** the tracked tree does not reference the producers of paper Figs. 2 and 3
  (`paper_fig_bkg_residual`, `paper_fig_deformation`). Before any change to them, their producers must be located.
- **Fixes that need no producer:**
  - the Fig. 13 colour fix, if made on the caption side;
  - every LaTeX-only table change.
  Either would be a text change in the note or the paper, so it goes through the register-round rules.

## 8. Limits

- **Noise:** the 2-point floor is large on a 5-point scale. Single-item scores are not reliable alone, and the
  findings above rest on consistent agreement.
- **Recognition:** a rater may recognize a published anchor figure. This was not controlled.
- **Matching:** the anchors match our items by kind (`data/match.tsv`). Several of our kinds have no close published
  counterpart: eigenmode maps, and fake-data tables.
- **Coverage:** sol's pairwise is partial (§2).

## 9. Files

- `data/scores.tsv`, `pairwise.tsv`, `changes.tsv`, `takeaway-check.tsv`, `text-size.tsv`.
- The raters' replies are in `runs/`. The anchors' crops are not committed.
