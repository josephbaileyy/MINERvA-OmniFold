# RESTYLE AMENDMENT 2: red for This work, and one style and one name per series (2026-10-31, paper rewrite lane)

**Status.** For the director to bind, with its code.
- **Done:** the code, its tests and the mutation receipt are committed (§4).
- **Not done:**
  - the dry run of the run driver, which needs the director's approval for dev draws on login37 (pending approval, §5);
  - the bound rerun;
  - Joseph's third look;
  - the install.

**Under:**
- `DECISION-20261031-joseph-restyle-second-look.md` (#613);
- the director's rulings of 2026-10-31 on this lane's diagnosis (§7).

The bound restyle ([DECLARATION.md](DECLARATION.md), [BINDING.md](BINDING.md)) and [AMENDMENT-1.md](AMENDMENT-1.md)
([BINDING-A1.md](BINDING-A1.md)) stand, except as amended here. Every change is in restyle mode only
(`--style restyle-2026-10`). With the option off, every producer still draws its committed figure (check 2, §4).

## 1. Why the styles differed (the diagnosis, reported before any change)

Read from the producers at `1c9df4f2e` and from the amendment-1 figures (`figs-a1/`).

1. **Tune v1 never carries an uncertainty.** No figure draws an MC statistical uncertainty, or any uncertainty, for
   Tune v1.
   - In fig13, the p_T and p_∥ projections and the two slice figures it is a bare step line:
     `plot_2d_threeway_fig13.py:209` (`stair_xy`), `plot_2d_cross_section.py:172` (`stairs`) and
     `plot_2d_paper_comparison.py:104` (`stairs`).
   - In `model_comp_projections` it is `ax.step(..., marker=technote_style.gen_marker(name))`
     (`compare_to_models.py:163-165`). That draws square markers at the bin centres, which read as data points with
     bars. This is what Joseph saw.
2. **The same figure draws the other two identities differently.**
   - Published is a black step line with circle markers (`gen_marker("data")`, `:156`). In fig13 it is black squares
     with error bars.
   - This work is a dashed step line with no markers (`:158`). In the other five series figures it is circles with error
     bars.
   - `compare_to_models` passes no uncertainty to this plot, so it draws projected central values only.
3. **The legend name.** `compare_to_models` labels the series with the model key, its underscores removed (`shown(name)`,
   `:148`, `:164`): "MINERvA Tune v1". The other four series figures print "GENIE 2.12.6 + MINERvA Tune v1".
4. **What the bars are.** This does not change, since no plotted number changes. It is a caption truth fix (§6).
   - **This work's bars,** in the three figures that draw them, are the cross-section histograms' bin errors: √(Σw²) of
     the reweighted simulated events (`make_th2d`'s `Sumw2`, `driver_p1.py:73-79`), combined with the completeness
     error (`driver_p1.py:1306-1316`). They are not the reported covariance.
   - **Published's bars** in fig13 are √diag of the published `StatOnlyCovariance` (`plot_2d_threeway_fig13.py:86-99`).
5. **A red outside the series.** `tension_spectrum` draws both curves in `#C44E52`, technote_style's first cycle colour,
   and its "90% of χ²" line in `#FF0000` (`diagnose_tension.py:282`, `:288-289`). With red meaning This work, a reader
   could take these curves for This work. They are the published TotalCov's eigen-spectrum and the cumulative χ² of the
   difference from the published result.

## 2. The palette

[palette.tsv](palette.tsv) must equal `restyle_2026_10.PALETTE` and `NEUTRAL`, and the self-test checks that it does.

| identity | colour | name | change |
|---|---|---|---|
| the published data | `#000000` | black | — |
| MINERvA Tune v1 (GENIE 2.12.6 + MINERvA Tune v1) | `#4C72B0` | blue | — |
| This work (OmniFold) | `#FF0000` | red | from vermillion `#D55E00` |
| no series identity: the tension spectrum's curves | `#404040` | dark grey | from `#C44E52` |
| no series identity: its 90 % reference line | `#808080` | mid grey | from `#FF0000` |

**Choosing the red.**
- **Method:** the minimum CAM02-UCS distance (colorspacious 1.1.2, Machado et al. CVD model at severity 100) to Tune v1's
  blue and to black, normally and under the three anomalies. The tool was a scratch `--target` install, kept out of
  git, and the script is in this lane's scratchpad (`a2-tools/reds.py`).
- **Reproduced first:** the method gives amendment 1's vermillion figures exactly: 57.7, 53.5, 48.1 and 59.4 against
  Tune v1, and 55.2, 54.0, 56.9 and 54.2 for Tune v1 against black.

| red | vs Tune v1: normal / deut. / prot. / trit. | vs black: normal / deut. / prot. / trit. | minimum |
|---|---|---|---|
| **`#FF0000`** (chosen) | 66.8 / 54.4 / 47.0 / 68.2 | 75.5 / 68.9 / 48.7 / 75.3 | **47.0** |
| `#E8000B` | 64.0 / 51.9 / 46.8 / 68.2 | 70.2 / 63.5 / 44.6 / 75.3 | 44.6 |
| `#E41A1C` (ColorBrewer Set1) | 61.8 / 51.4 / 43.9 / 67.3 | 68.9 / 63.1 / 44.2 / 74.3 | 43.9 |
| `#D62728` (matplotlib tab:red) | 58.4 / 48.2 / 41.0 / 65.2 | 65.4 / 59.7 / 42.3 / 70.5 | 41.0 |
| `#D55E00` (vermillion, amendment 1) | 57.7 / 53.5 / 48.1 / 59.4 | 68.1 / 67.1 / 56.2 / 70.2 | 48.1 |

- **Every red loses some protanopia separation** compared with vermillion. `#FF0000` keeps the most: 47.0 against 48.1.
- **Greyscale:** its lightness J′ is 60, against Tune v1's 49 (vermillion's was 59), so the greyscale gap is unchanged.
  Markers against a line carry the rest.
- **On the review sheets,** the committed fig13 and p_T, p_∥ projections drew Tune v1 in red (`#FF0000`; the slices'
  Tune v1 was `#9467BD`). So `sheets.py` prints on those three sheets that red means Tune v1 on the left and This work
  on the right.

**Recolour rows.** [recolour.tsv](recolour.tsv) keeps amendment 1's rows. It adds the tension spectrum's two rows, which
map to the two colours with no identity. The director's ruling called these "one declared recolour row". They are two
rows, one per colour, because the table maps one before colour per row.

## 3. One style and one name per series

[styles.tsv](styles.tsv) must equal `restyle_2026_10.LINESTYLE`, `MARKER` and `NAMES`, and the self-test checks that it
does.

| identity | drawn as | error bars | legend name |
|---|---|---|---|
| published | black filled squares, no line | where the figure has the published uncertainty (fig13) | Published (PRD 104, 092007) |
| this_work | red filled circles, no line | where the figure has them (fig13, the projections, the slices) | This work (OmniFold) |
| tune | a blue solid step line, no markers | none (the MC truth; no figure draws its uncertainty) | GENIE 2.12.6 + MINERvA Tune v1 |

**What changes in the producers** (restyle mode only):
- **`compare_to_models.py` (`model_comp_projections`):**
  - Published and This work are drawn as their markers with no line. They keep `ax.step` with `ls="None"`, so each
    line's data and drawstyle are those of the committed figure;
  - Tune v1 is a bare step;
  - every legend entry uses `NAMES`;
  - it draws no uncertainties. Adding them would add plotted numbers, which #613 excludes. Its caption says so (§6).
- **`plot_2d_threeway_fig13.py`, `plot_2d_cross_section.py` and `plot_2d_paper_comparison.py`:** their restyle labels
  come from `NAMES` (the same strings), and their styles are already the table's.
- **`diagnose_tension.py` (`tension_spectrum`):** the curves are `NEUTRAL["curve"]` and the 90 % line is
  `NEUTRAL["reference"]`, still dashed.
- **Not changed:** the colour maps (`RdBu_r`) of the four map figures (a colour map is not a series); the pull
  histogram's bars; the p_T and p_∥ projections' ratio-panel reference line, which stays dashed in Tune v1's blue (a
  reference line, not a series).

**[restyle.tsv](restyle.tsv), what each series line was.** It lists each figure's series lines as the committed
producers (base `bab87aeb3`) draw them: the before RGB, and the linestyle and marker as matplotlib 3.10.1 reports them,
each with the identity whose style it must take.
- **How it was derived:** from the base producers' draw calls (`git show bab87aeb3:2d-unfolding/<producer>`), and
  matplotlib's reported strings for each call pattern, measured locally.
- **Rows already in their identity's style** are kept, so that every series line is declared.
- **Error-bar caps** (markers `|` and `_`) are not series lines. They keep their style, and the recolour table recolours
  them.
- **Not yet checked against a capture:** the bound run's `compare.py` checks the table against the captured "before"
  arm, and so would the dry run (§5).

## 4. The checks, amended

`tools/`, committed with its tests:
1. **Check 3, restyled** (`compare.py --recolour recolour.tsv --palette palette.tsv --styles styles.tsv --restyle
   restyle.tsv`):
   - the items pair by a hash with the colour fields and the line-style fields (linestyle, marker, drawstyle) left out
     (`artists.py` "xhash"), equal bit for bit as a multiset per figure;
   - each paired item's colours must be as amendment 1's check requires;
   - an item the restyle table maps must take its identity's linestyle and marker;
   - every other item's linestyle, marker and drawstyle must stay exactly as it was. A drawstyle never changes.
2. **The names gate** (`names.py --gate --styles styles.tsv --other legend-other.tsv`, on all eleven after-figures):
   - every legend entry (`capture.py` writes `<figure>.legend.tsv`) must be an identity's name, or an entry
     [legend-other.tsv](legend-other.tsv) declares for its figure (only the tension spectrum's "90% of χ²");
   - each named figure must have a legend record.
3. **Unchanged:** amendment 1's named binning exception, the overlap gate and checks 2 and 4–7. Check 2 still requires
   the "off" arm to draw the committed figures pixel for pixel.
4. **Tests:**
   - `selftest.py` adds eight cases, both ways:
     - a step line restyled as declared (silent);
     - the wrong marker (fires);
     - an undeclared line-style change (fires);
     - a one-ulp value under the restyle (fires);
     - the same restyle under amendment 1's check, undeclared (fires);
     - "MINERvA Tune v1" in a legend (fires);
     - the full names (silent);
     - a named figure with no legend record (fires).
   - It also checks `palette.tsv` against `PALETTE` and `NEUTRAL`, and `styles.tsv` against `LINESTYLE`, `MARKER` and
     `NAMES`.
   - `MUTATION-RECEIPT.txt` adds six mutants: line styles not checked; the restyle table ignored; the data-only hash
     including the line-style fields; the names gate disabled; legend entries not captured; a named figure with no legend
     record passing. Amendment 1's label-hash mutant is re-anchored to the new `_item` signature.

## 5. The run

- **Command:** `run.sh bab87aeb3 <bound sha>`.
  - The run root is `/pscratch/sd/j/josephrb/2d-closeout-restyle-20261031/run-a2`, new (`run.sh`'s default). The first
    run's `run/` and amendment 1's `run-a1/` stay.
  - Login node only, 0 node-h, inputs read-only.
- **Outputs:** `run-a2/`, `figs-a2/` and `review-a2/`, beside the earlier runs' directories, which stay as the history.
- **Dry run:** pending approval. `RESTYLE_RUN_ROOT=<dev>/runtest-a2 run.sh bab87aeb3 <head>` needs the director's
  approval for dev draws, under the same terms as before. Its outputs would not be installed or committed. It is the
  first test of restyle.tsv against a real capture, and of the producers' restyle paths, which need ROOT and the inputs
  and cannot run locally.

## 6. Captions, for the install round (STEP4 part 2)

These are truth fixes, made with the install:
- **Note Fig. 13** (`sec_results.tex:160`, `model_comp_projections`). Its caption today reads "Projections of this
  measurement (dashed) and the published data (black); MINERvA Tune v1 (blue) lies below the data in the peak" (T1,
  #593). It must change with the figure:
  - this measurement is now red circles and the published data black squares;
  - Tune v1's name in the caption should be the full one;
  - add "Uncertainties are not drawn."
- **The primer's `MEFHC_5iter_fig13`** (`primer_body.tex:157`): T6's "red" → "blue" for Tune v1 stands. That caption
  names no colour for This work.
- **What the bars are** (§1 item 4):
  - **note Fig. 7** (fig13 and the projections): it does not say what the bars are. It should say: This work's bars are
    √(Σw²) of the reweighted simulation with the completeness error, not the reported covariance; Published's are √diag
    of its statistical-only covariance;
  - **note Fig. 9/10** (the slices): "Points carry statistical errors only" becomes the same precise statement.
- **Fig. 14** (T3, "the panels have no printed titles"): as before.
- **No other site names a colour for This work.** No caption in the note, the primer or the paper names "red", "orange"
  or "vermillion" for This work.
  <!-- absence-ok: `git grep -n -i -w -E "red|orange|vermillion|vermilion|blue|dashed|black|grey|gray" -- "docs/analysis-note/*.tex"` at 1c9df4f2e, comments excluded: the hits for these eleven figures are sec_results.tex:160 and primer_body.tex:157 only; the rest are hyperref colours, macros, and captions of other figures (eavailW_band, paper_fig1_validation, sec_3d, sec_pet, sec_fps, sec_experiment, sec_5d, app_history, app_codebase) -->

## 7. Rulings (the director, 2026-10-31)

- (i) **One style per identity everywhere**, as §3 gives it.
- (ii) **`model_comp_projections`** is restyled the same way, with the full name in its legend. Its caption says
  "Uncertainties are not drawn", and T1's "(dashed)" changes with it.
- (iii) **The red is `#FF0000`,** by the measurement: the best protanopia separation of the reds.
- (iv) **`tension_spectrum`:** the curves go to dark grey `#404040`, and the 90 % line to dashed mid grey `#808080`,
  with no identity. The colour maps stay.
- (v) **The bars caption truth fix** goes into the install round.
- (vi) **The sheet headers** say that red meant Tune v1 on the left of fig13 and the projections, and means This work on
  the right.
- (vii) **The checks:** the data-only hash, styles.tsv with the restyle table, the names gate, the size and overlap
  gates, two-way tests and new mutants.

## 8. After binding

1. The dry run, if approved, then the bound rerun into `run-a2`.
2. New sheets, `review-a2/`, for Joseph's third look.
3. Then the install (DECLARATION.md §5, with `figs-a2/`), with STEP4's T3, R and T6 and §6's caption fixes, in their
   own PR.
