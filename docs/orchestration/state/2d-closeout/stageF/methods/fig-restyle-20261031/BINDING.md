# Binding: the restyle of the note's 2D result figures (Figs. 7–14) (2026-10-31)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261031-joseph-rater-account-figures-chi2-consult.md` (#574), item 2.

**Binds** [`DECLARATION.md`](DECLARATION.md), merged in PR #579. Its file sha256 begins `8c71209c9f4d0a66`. That
includes the producers' off-by-default `--style restyle-2026-10` option, the helpers in
`2d-unfolding/restyle_2026_10.py` and the checks in `tools/`.

**AUTHORIZES:**
- exactly one bound run, `run.sh bab87aeb3 a2f2394d3d0cb59381ea6957673b6d75185becd6`, on a Perlmutter login node at
  0 node-h, in two clean deploys under `/pscratch/sd/j/josephrb/2d-closeout-restyle-20261031/`;
- committing its `run/` outputs and the new `figs/`, and building the review sheets.

**CANNOT AUTHORIZE:**
- installing the restyled figures into the note. That waits for Joseph's visual review of the sheets, and then
  follows §5;
- any change to a plotted number, a colour or marker of a data series, a caption or any other text;
- writes to `$A`, CFS or HPSS;
- a rerun after a failed check.

## 1. What the director checked at the PR head `03c3efc6`

- `selftest.py`, locally: **SELF-TEST :: PASS**, 20 cases. The size gate is among them: a 3.5 pt toy label fails the
  4.0 pt floor and is named, and the same label at 5.0 pt passes. The width scale of 0.5 makes a dropped scaling
  detectable.
- The mutation receipt: 13 of 13 checker mutants killed, including the inverted floor and the unit scale.
- The `2d-unfolding/` diff is the off-by-default option and its helper module, 7 files.
- The dev-draw evidence, reported by the lane and never installed:
  - with the option off, 11 of 11 figures are pixel-equal to the committed copies;
  - with the option on, the arrays, RGBA, reports, logs and inputs are all equal;
  - nothing was written under `$A`.

## 2. Rulings recorded in §6

1. G rows are re-pointed, with old and new digests in `DIGESTS.tsv`. Part C's copies stay.
2. The primer's `MEFHC_5iter_fig13` is in scope.
3. The floor is 4.0 pt, aiming at about 5.
4. **The size gate is `textsize.py`,** on drawn font sizes scaled to printed width. The `figdiag` re-crop is a record
   only, since its pdftotext boxes misread matplotlib Type 3 text (`SIZE-MEASURES.tsv`).
5. Figs. 9–10 carry no physical units: each panel is scaled to its own maximum, and printing those maxima would be a
   CONTENT change.
6. Captions made stale by the restyle (Fig. 14's "no printed titles") and Fig. 13's colour go into the next note
   round, as truth fixes.
7. The review sheets: one page per figure, old on the left and new on the right, at printed width.

## 3. Conditions

- **Order:** the run follows §4, with check 2 (the before arm is pixel-equal) first. Any failed check stops the
  sequence, and the run comes back unrepaired.
- **The run's outputs** come as a PR with the review sheets. The director shows Joseph the sheets before any install.

The run may start once this record is on `main`.
