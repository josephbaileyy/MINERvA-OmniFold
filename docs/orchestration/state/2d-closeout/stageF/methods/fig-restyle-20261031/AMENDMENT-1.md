# RESTYLE AMENDMENT 1: Fig. 13's labels, the pull figure's bins, and one palette (2026-10-31, paper rewrite lane)

**Status.** For the director to bind, with its code.
- **Done:** the code and its tests are committed. The dev draws ran under the director's approval of 2026-10-31,
  under the same terms as before; their outputs are never installed or committed. A dry run of the run driver passed
  (§5).
- **Not done:** the bound rerun, Joseph's second look and any install.

**Under:**
- `DECISION-20261031-joseph-restyle-review-and-palette.md` (#591);
- the director's rulings of 2026-10-31, which are (i) to (vi) of §7.

The bound restyle ([DECLARATION.md](DECLARATION.md), [BINDING.md](BINDING.md)) stands, except as amended here. Joseph
approved everything in his review that he did not mention.

## 1. What changes

The changes below apply in restyle mode only (`--style restyle-2026-10`). With the option off, every producer still
draws its committed figure (§4, check 2).

| figure | change | Joseph's point |
|---|---|---|
| `MEFHC_5iter_fig13` (note Fig. 7 top; the primer) | the p_T-axis grid gets headroom: y range 0–3.0 instead of 0–2.4, with the same ticks. Every slice label then clears the data. `overlap.py` found 43 overlaps over three panels in the bound run's figure (2 in the committed one), and 0 now | "the 1.50 in the top left box of the pT part overlaps the lines" |
| `MEFHC_5iter_pull_full` (note Fig. 8) | the histogram's bins are zero-aligned, with edges at multiples of 0.15, so that the dashed line at 0 falls on a bin edge | "why is the dotted line on zero not aligned?" |
| the five figures that draw the series (fig13; `_xsec_proj_pt`, `_pz`; `_xsec_paper_pt_slices`, `_pz_slices`; `model_comp_projections`) | one colour per series identity (§2) | "should we use consistent colors across plots?" |

**The pull figure's cause, reported before the fix** (the director's instruction). It is not a drawing bug: there is
no shifted axhline, no twin axis and no offset transform.
- **The line:** the dashed line is an `axvline` at exactly x = 0. The bound run's captured arrays give its data
  coordinates as [[0, 0], [0, 1]].
- **The bins:** `hist(pull, bins=30)` made 30 equal bins of width 0.1494 over the values' own range, −2.572 to 1.910.
- **Why it looked misaligned:** 0 fell inside the bin [−0.032, 0.117], a fifth of the way across, so the line cut a
  bar off-centre. The committed figure has the same feature.
- **The ruling:** the director ruled (a). The bin edges are presentation of the pull values, not reported numbers.

## 2. The palette, and what each series was

The palette is [palette.tsv](palette.tsv), equal to `2d-unfolding/restyle_2026_10.py` `PALETTE`. The self-test checks
that the two are equal.

| identity | colour | name |
|---|---|---|
| the published data | `#000000` | black |
| MINERvA Tune v1 (GENIE 2.12.6 + MINERvA Tune v1) | `#4C72B0` | blue (technote_style's Tune colour) |
| This work (OmniFold) | `#D55E00` | vermillion (Okabe–Ito) |

**Colourblind safety:**
- The minimum pairwise CAM02-UCS distance (colorspacious, severity 100) is 55.2 normally, 53.5 under deuteranomaly,
  48.1 under protanomaly and 54.2 under tritanomaly.
- In greyscale, Tune v1 and This work are close (lightness 49 and 59), so their markers and line styles carry the
  separation: Tune v1 is drawn as solid lines or steps, This work as markers with error bars, or dashed where it is a
  line.

**What each series was** ([recolour.tsv](recolour.tsv), measured from the bound run's `run/before/capture`):

| figure | This work | Tune v1 | published |
|---|---|---|---|
| `MEFHC_5iter_fig13` | `#1F77B4` | `#FF0000` | `#000000` (kept) |
| `_xsec_proj_pt`, `_pz` (including the ratio panel and its reference line) | `#000000` | `#FF0000` | — |
| `_xsec_paper_pt_slices`, `_pz_slices` | `#000000` | `#9467BD` | — |
| `model_comp_projections` | `#C44E52` | `#4C72B0` (kept) | `#000000` (kept) |

**Not recoloured:**
- the colour maps (`RdBu_r`) of the maps;
- the pull histogram's bars;
- the tension spectrum's curves.
None of them is a series identity.

**Other generators:** none appears in these eleven figures, so the palette names none. If it is ever extended,
`technote_style.py` maps "MEC" to the same `#4C72B0` as Tune.

## 3. Captions that name a colour

These are truth fixes in the note round (STEP4-PLAN.md), made with the install:
- **Note Fig. 13** (`fig:model`): STEP4's T1 already says "(blue)" (#593). That is the palette's name for `#4C72B0`, so
  T1 stands as written.
- **The primer's `MEFHC_5iter_fig13`:** "The red curve is MINERvA's tuned simulation (Tune~v1 …)" becomes "blue".
  This is STEP4's T6, a plan amendment the director accepted, recorded before its text.
- **Note Fig. 14:** T3 ("the panels have no printed titles"), as before.
- **No other caption** of Figs. 7–14 names a colour.

## 4. The checks, amended

`tools/`, committed with its tests:
1. **Check 3, recoloured** (`compare.py --recolour recolour.tsv --palette palette.tsv`):
   - each item's data, with the colour fields left out (`artists.py` "dhash"), must be equal bit for bit, as a
     multiset per figure;
   - for each paired item, a colour that the recolour table maps for that figure must become the palette's colour for
     its identity, at its own alpha;
   - every other colour must stay exactly as it was.
2. **The one binning exception, by name** (`--rebin MEFHC_5iter_pull_full.png`): that figure's `Axes.hist` patches
   (gid `restyle-hist`) are left out of check 3, and the values `hist` was given (`capture.py` "hist-input") stay in
   it, bit for bit. No other figure is excepted.
3. **The overlap gate** (`overlap.py --gate`, on all eleven after-figures): no text of a figure or its axes may cross
   a data line, an error bar, a marker or a patch outline, in display coordinates after drawing.
   - It was reported first, on the bound run's figures: fig13 only, 43 overlaps, against 2 in the committed figure.
     It is now a gate.
4. **Checks 2, 4–7 unchanged.**
5. **Tests:**
   - `selftest.py` has 31 cases, both ways. They include a recolour as mapped (silent), a palette colour wrong by one
     unit (fires), an unmapped recolour (fires), a one-ulp value under recolour (fires), zero-aligned bins with the
     figure named (silent) and not named (fires), a one-ulp hist value with the figure named (fires), a text on a line
     (fires) and none (silent), and `palette.tsv` against `PALETTE`.
   - `MUTATION-RECEIPT.txt`: the control passes and all 18 mutants are killed. Five are new: colours not checked, the
     recolour table ignored, the exception applied to every figure, hist values not recorded, and the overlap test
     disabled.

## 5. The run

- **Command:** `run.sh bab87aeb3 <bound sha>`. The "before" arm is the base's producers. The "after" arm is the
  amended restyle, so every colour and binning change is judged against the committed figures.
  - The run root is `/pscratch/sd/j/josephrb/2d-closeout-restyle-20261031/run-a1`, new; the first bound run's `run/`
    stays.
  - Login node only, 0 node-h, inputs read-only.
- **Outputs:** they come back as `run-a1/`, `figs-a1/` and `review-a1/` beside the first run's directories, which stay
  as the history.
- **Dry run** (dev, approved; outputs not installed or committed), `run.sh bab87aeb3 35eb9821` under
  `dev/runtest-a1`: `RUN CHECKS :: PASS`.
  - check 2: 22 of 22 pixel-equal;
  - checks 3–5: COMPARE PASS with the palette and the pull figure's exception;
  - check 6: 0 files in each arm;
  - check 7: 5.00–5.92 pt;
  - OVERLAP PASS.

## 6. Paper figures that share these series (for Joseph; nothing changes)

| paper figure | series | colours today |
|---|---|---|
| Fig. 1 (`paper_fig1_validation`) | This work, the published data, Tune v1 | `#C0392B` and others |
| `fd_g_fig_ratio` | the data, Tune v1, GENIE 2.12.10 CV, GENIE + MEC, NuWro, GiBUU | `#2A78D6`, `#EB6834`, `#1BAF7A`, `#4A3AA7` |
| `paper_fig_deformation` | generator deformations (GENIE MEC, NuWro, GiBUU/GENIE) | `#4A3AA7`, `#2A78D6`, `#1BAF7A` |

These figures use a palette of their own, which neither of the note's palettes shares.

## 7. Rulings (the director, 2026-10-31)

- (i) The pull figure takes option (a): zero-aligned bins of width 0.15, with the check's exception declared by name
  for this one histogram. The director tells Joseph the cause, and Joseph may veto.
- (ii) Dev draws are approved, under the same terms as before.
- (iii) The overlap check is approved: reported first, then a gate on all eleven figures.
- (iv) The palette is accepted: published black, Tune v1 `#4C72B0`, This work `#D55E00`, with markers and line styles
  carrying the greyscale separation.
- (v) T6 is accepted as a STEP4 plan amendment. The amended RGBA check is accepted, with its two-way tests and its
  extra mutants.
- (vi) The paper figures are recorded for Joseph. Nothing changes there.

## 8. After binding

1. The bound rerun.
2. New sheets, `review-a1/`, for Joseph's second look.
3. Then the install (DECLARATION.md §5), with STEP4's T3, R and T6, in their own PR.
