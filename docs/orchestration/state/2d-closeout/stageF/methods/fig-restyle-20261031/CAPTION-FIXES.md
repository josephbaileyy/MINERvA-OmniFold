# Two caption truth fixes, note Figs. 13 and 25: drafted for the next note round (2026-10-31)

**Status.** Drafted, not applied. Under
[DECISION-20261031-joseph-rater-account-figures-chi2-consult.md](../../../../../DECISION-20261031-joseph-rater-account-figures-chi2-consult.md)
item 4, these are corrected on the caption side as truth fixes in the next note round, with its ledger rows and agy's
agreement read. The base is origin/main `bab87aeb3`. Each claim below was checked against the producer and the
committed PDF, not against the raters' reports.

## Note Fig. 13 (`sec_results.tex`, `fig:model`, `model_comp_projections.pdf`)

**The defect.** The caption says "MINERvA Tune v1 (orange)", but the line is drawn blue.
- **The producer:** `2d-unfolding/compare_to_models.py` on `bab87aeb3` draws each model in `C{j+1}`, and Tune v1 is the
  only model (j = 0), so it is `C1`. This measurement is `C0`, dashed, and the published data are black.
- **The palette:** `technote_style.py` sets the colour cycle to `GEN_PALETTE` first. `GEN_PALETTE[1]` is `#4C72B0`,
  which `GEN_COLORS` labels "blue (GENIE + MINERvA Tune v1)".
- **The committed PDF** (`model_comp_projections.pdf`, sha256 `2c39fe21…`, the `make_figures.sh` pin) has two stroke
  colours: `#C44E52` (4 strokes) and `#4C72B0` (2 strokes). It has no orange.

**The fix (one word):**

```latex
before: MINERvA Tune v1 (orange) lies below the data in the peak.
after:  MINERvA Tune v1 (blue) lies below the data in the peak.
```

**Ledger row:**
- the colour is a presentation fact, homed at `L:technote_style.py`, whose `GEN_COLORS` names it in words;
- the restyle declaration keeps every series colour, so the fix stays true after the restyle (DECLARATION.md §2).

## Note Fig. 25 (`sec_eavailw.tex`, `fig:eavailWband`, `eavailW_band.pdf`)

**The defect.** The caption describes the corner of the 2D distribution as if the figure showed it. The figure does
not show it, and the caption also names a band that is not drawn.
- **What is drawn:** `3d-unfolding/genie/overlay_eavailW_band.py` (`c.Divide(2, 1)`) draws two 1D projections:
  - left, dσ/dE_avail;
  - right, dσ/dW;
  - in each, the data as points and each generator as a histogram with markers (`"HIST P SAME"`).
  No envelope or band is drawn.
- **Where the corner is shown:** the corner (E_avail ≥ 0.8 GeV, W ≥ 1.8 GeV) is a sum over 2D cells (`corner =
  np.outer(eav_hi, w_hi)`). Neither projection shows it.
- **The corner claim itself is true and printed in the body:** "All four external generators fall below the data in
  the high-$\Eavail$, high-$W$ corner." It is followed by data/generator = 1.14, 1.14, 1.16 and 1.61 in the corner
  (`sec:eavailw-band`).
- **"Unchanged":** the body says that 2p2h leaves the corner "essentially unchanged ($1.142\to1.139$)". The caption
  says "unchanged".

**The fix (proposed wording).** Every fact is kept. The corner statement is attributed to the section, not to the
panels, and "band" is replaced:

```latex
before: Unfolded $(\Eavail,W)$ cross section versus the four-generator band (GENIE~CV, GENIE$+$MEC, NuWro, GiBUU;
GENIE and NuWro flux-corrected, \S\ref{sec:3d-models}). Every generator lies below the data in the high-$W$,
high-$\Eavail$ corner --- GENIE and NuWro by about their overall normalization shortfall, GiBUU by more; adding 2p2h
leaves the corner unchanged because 2p2h populates low $W$.

after:  Projections of the unfolded $(\Eavail,W)$ cross section onto $\Eavail$ (left) and $W$ (right), with the
predictions of four generators (GENIE~CV, GENIE$+$MEC, NuWro, GiBUU; GENIE and NuWro flux-corrected,
\S\ref{sec:3d-models}). In the high-$W$, high-$\Eavail$ corner, which the projections do not resolve, every generator
lies below the data (\S\ref{sec:eavailw-band}) --- GENIE and NuWro by about their overall normalization shortfall,
GiBUU by more; adding 2p2h leaves the corner essentially unchanged because 2p2h populates low $W$.
```

**Ledger rows:**
- **left/right and points-and-histograms:** `L:3d-unfolding/genie/overlay_eavailW_band.py`, pinned at its sha, under
  the director's rule for code homes: a tracked file that states the fact in plain words. Its comments read "panel 1:
  dsigma/dEavail" and "panel 2: dsigma/dW".
- **the corner ratios:** `N:sec_eavailw.tex::In the corner ($\Eavail\ge\SI{0.8}{GeV}$, $W\ge\SI{1.8}{GeV}$), data/generator $=1.14$`.
- **"essentially unchanged":** `N:sec_eavailw.tex::leaving the corner essentially unchanged ($1.142\to1.139$)`.
- **What is not added:** no new number, generator or claim. The corner definition stays in the body only.

**For the round to decide.**
- **"(left)/(right)."** The restyle may add panel labels (a)/(b), which is diagnosis row note-fig-25.7. Fig. 25 is not
  among Figs. 7–14, so it is not in the restyle, and the caption keeps "left"/"right".
- **The paper.** `make_figures.sh:302` crops this figure to `paper_eavailW_generators.pdf`. No `.tex` file on
  `bab87aeb3` includes that crop, so no paper caption carries the defect. The only "orange" in a note caption, apart
  from Fig. 13, is `sec_experiment.tex:54`, which is outside the diagnosis's population and was not checked.
