# DECISION 2026-10-31 (later) — Joseph: the 2D figure restyle review, with two fixes and a consistent palette

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The bound restyle run
([`state/2d-closeout/stageF/methods/fig-restyle-20261031/`](state/2d-closeout/stageF/methods/fig-restyle-20261031/),
#586, #588) produced eleven before/after sheets. The director put them in front of Joseph at
`~/MINERvA-OmniFold-reads/fig-restyle-review-20261031/`.

Joseph's review, verbatim, in his own message:

> 2D figure restyle comments: fig 13: for the most part I like the change but the 1.50 in the top left box of the pT part overlaps the lines a little. pull full: in the right plot, why is the dotted line on zero not aligned? Things I didn't mention are good. Also, should we use consistent colors across plots? Like all the This work (OmniFold) are the same and all the Tune v1 etc.

sha256 of the text plus a final newline begins `462872068ac57206`.

## What is decided

1. **The restyle is approved,** except for the two figures below: "Things I didn't mention are good."
2. **Two fixes before the install:**
   - **Fig. 13 (`MEFHC_5iter_fig13`, the p_T part):** the "1.50" in the top-left box overlaps the lines. Move or resize
     the annotation so that it clears every line.
   - **`MEFHC_5iter_pull_full`, right panel:** the dotted reference line at zero is not aligned with zero. Find the
     cause and fix it so that the line sits at y = 0.
3. **Consistent colours across the figures,** as Joseph asked, with the director recommending it:
   - one colour per series identity across all the restyled figures: "This work (OmniFold)", MINERvA Tune v1, the
     published data, and each other generator;
   - measured today, the figures use different blues and reds for the same series. Fig. 13 uses #1f77b4 and red, and
     the model comparisons use #4C72B0 and #C44E52;
   - the palette should be colourblind-safe.

   This changes series colours, which the restyle declaration had held fixed (§2 "Not changed"). So it comes as an
   amendment that the director binds:
   - the declared palette as a table;
   - the RGBA check amended to compare each series' colour against that table, and its data arrays bit-for-bit as
     before;
   - every caption that names a colour updated as a truth fix in the same note round. Fig. 13's "(orange)" →
     "(blue)" fix is replaced by the palette's actual name.
4. **The install** follows the amendment's bound rerun and a second look by Joseph at the changed sheets.

## Not changed

- Every plotted number. Nothing is submitted, deposited or tagged.
