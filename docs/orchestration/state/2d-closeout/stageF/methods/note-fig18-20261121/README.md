# Fig. 18 (fig:3dmodels) redrawn with generator/data ratio panels (2026-11-21)

**By** the `cov2d` session. **The request:** the director's Fig. 18 request of 2026-11-21. Joseph approved the
suggestions through the rewrite helper. **Base:** the rewrite head `0deadb6a6` (rewrite/journal-voice-20261121).

**What was wrong:**
- The figure read compressed. p_T ran to 4.5 GeV/c and p∥ to 60 GeV/c, so the peaks filled the left fifth of each panel.
- The panels were tall and narrow, and the two-line y labels took almost as much width as the plots.
- Each generator had both a thick step line and markers.
- The caption's claim is about ratios, which the figure did not show.

## What changed (`tools/compose_fig18.py`)

**No data changed.** The arrays are read from the installed recipe's own figure. That recipe is
`note-figpass-20261119/tools/fix_family4.py`: the pinned pickle `720a350e…`, loaded only through
`restyle_family4.load()`, which checks its sha256. Before drawing, the tool checks two things:
- each generator's steps equal its marker line;
- the data line equals its duplicate and sits at the bin centres.

The new figure is drawn with `note_print_style`, at \textwidth (6.5 × 4.03 in, printed at scale 1.0):
- **Ratio panels:** generator / data under each panel, labelled "gen. / data" as in Fig. 19, with a dashed line at 1.
  - The three ratio panels share one y range (−0.075 to 1.582), so they can be compared with each other.
  - GiBUU's p∥ ratio is 0 above 20 GeV/c. Its prediction is zero there, since its sample ends at E_ν = 20 GeV, as the
    text above the figure says.
- **Styles:** the generators are thin step lines only (1.0 pt, no markers); the data are points.
- **Axes:**
  - p_T is drawn on 0–2.5 GeV/c. The [2.5, 4.5) bin is left off; it holds 0.82% of the data's p_T integral (arithmetic
    from the pickle's values).
  - p∥ is on a log axis over its full range, 1.5–60 GeV/c, with no bin left off.
  - E_avail keeps its installed range, 0–3 GeV.
- **Labels:** one-line y labels with the units. The power of ten is an axis-top multiplier (×10⁻³⁸, ×10⁻³⁹, ×10⁻³⁸),
  checked against the expected exponent per panel.
- **Legend and stamp:** one legend above the panels. No stamp.

After drawing, the tool runs these checks, and any failure stops it before a file is written:
- every step, point and ratio is read back from the artists and must equal the source arrays bitwise;
- no two drawn texts overlap, and all lie on the canvas;
- no axes' text comes within 2 px of another axes. A copy with `wspace` 0.18 fails this check on four labels, so the
  check fires;
- the legend covers no axes.

## Checks (`tools/run_fig18.sh`; `runs/fig18/CHECKS.txt`): RUN-FIG18 PASS

- **Arm 0** is the installed recipe.
  - `fix_family4.py` is EQUAL-BUT-DATE against `note-figpass-20261119/figs/generators_vs_unfolded_band_central.pdf`.
  - `strip_stamp.py` on that committed figpass file reproduces the installed file (`7ea16ffd…`) byte for byte.
  - The stripped arm 0 differs from the installed file only inside /CreationDate and the trailer /ID (64 bytes, 0
    outside). pikepdf computes the /ID from the content, date included.
- **Data unchanged, read from the two captures.** This check is independent of the tool's own readback, and it is PASS.
  - Every arm-1 step height equals arm 0's value for that generator and bin.
  - Every data point equals arm 0's.
  - Every ratio step equals arm 0's generator / data.
  - All are bitwise, in all three panels. The one bin left off is p_T x = 3.5.
  - A copy of the arm-1 capture with one NuWro step changed by 1e-7 (relative) fails it.
- **Strings.**
  - Gone: the stamp and the three two-line y labels.
  - Added: the three one-line labels, the three multipliers and "gen. / data".
  - No stamp text remains.
- **Overlaps.**
  - The PDF's own word boxes (pdftotext -bbox) have no overlapping pair. The four touching pairs are subscripts at their
    base glyph ("p"/"T", "E"/"avail").
  - The capture's PDF count, 2 → 3, is reported but is not a gate. It is the misreading described in
    note-figround-20261121/README.md: after a PDF save it measures the y labels with the screen renderer's metrics.
- **The page:** the note built with latexmk to 63 pages with no LaTeX errors. Fig. 18 sits on p. 48, which it now
  fills to about two thirds.
- **build_all:** rc 1 at this branch and rc 1 at the base `0deadb6a6`, with identical FAIL lines (309 each, the
  structural records gates).

The installed file is `docs/analysis-note/figures/generators_vs_unfolded_band_central.pdf`, sha256 `d030980eeba9ce29dfa40c03baf426e41b9fb489cdb559651202cce94788e62c`.

**Not changed here:**
- `make_figures.sh`'s `install_layout_fig` line for this figure still pins the figpass file. Rounds 2 and 3 left their
  pins the same way, for the structural rewiring the director agreed.
- The caption. It now has to describe the ratio panels and the axes, and the ratios bear on its claim. The proposal
  went to the director for Joseph (below). The claim was not reworded here.

## The caption: what the ratio panels show (for Joseph, via the director)

The ranges are over the drawn bins, from `runs/fig18/compose_fig18.json`:

| gen. / data | p_T (13 bins) | p∥ (16 bins) | E_avail (6 bins) |
|---|---|---|---|
| GENIE-CV | 0.763–1.057 | 0.535–0.965 | 0.738–1.008 |
| Tune-v1 | 0.767–1.116 | 0.677–0.943 | 0.814–1.007 |
| NuWro | 0.778–1.507 | 0.662–0.951 | 0.793–0.926 |
| GiBUU | 0.334–0.833 | 0.000–0.807 | 0.645–1.016 |

The caption says "The generator predictions follow the muon-momentum shapes … more closely than the available-energy
shape." On the drawn bins, every generator's ratio spans a narrower range in E_avail than in either p_T or p∥.

| max − min of gen. / data | p_T | p∥ | E_avail |
|---|---|---|---|
| GENIE-CV | 0.293 | 0.431 | 0.270 |
| Tune-v1 | 0.348 | 0.266 | 0.193 |
| NuWro | 0.728 | 0.289 | 0.133 |
| GiBUU | 0.499 | 0.807 | 0.371 |

These ranges include the momentum tails, which hold a few percent of the rate, and they carry no uncertainty: the 3D
result has no reported covariance. Read either way, the ratio panels do not show the momentum shapes followed more
closely. The claim is Joseph's to keep, qualify or replace.
