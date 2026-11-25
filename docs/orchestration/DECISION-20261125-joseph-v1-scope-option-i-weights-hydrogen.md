# DECISION 2026-11-25 — Joseph: arXiv v1's scope, option (i) with saved central weights, the old-edge comparisons, the 5D bias block, and Gemini Hydrogen

**Recorded by** the director. It adds to `DECISION-20261124b-joseph-b-design-185-bias-block-old-namespace.md`. Joseph
gave every item below directly to the director, in the director's session, on 2026-11-24 and 2026-11-25 (Pacific).
Quoted words are Joseph's. Correspondence with Ben is not quoted here; where Joseph acts on it, only his own decision
is recorded.

## 1. The pT grid: option (i), and the central weights are saved

- **Option (i) continues.** Our analysis grid keeps its pT edges (0.07 / 0.33 / 0.47 GeV/c). Comparisons with the
  published result use the published edges (0.075 / 0.325 / 0.475), from the central value unfolded on those edges
  (`docs/orchestration/state/ibu-chi2-20261123/tier1/`, regenA, A2 and A3). Joseph on 2026-11-24: "okay I think we need
  to do (i) but can we price (ii) and I will bring it to Ben? we can keep doing (i) for now."
- **(ii), the full 2D redo on the published edges, is deferred** until the high-p‖ efficiency question is resolved, so
  the redo happens once. Its price is in `ibu-chi2-20261123/grid-price/README.md` (about 177 CPU node-h for the
  products in use).
- **The central-value per-event weights are saved and are to be published** with the result, as the unbinned central
  value. The writer is limitation-resolver's lane; it runs only under a director binding.
- **COVFIX's §9 stop** (adopting (ii) before the first spend) is not triggered.

## 2. The comparisons that stay on our edges

Three kinds of χ²-vs-published values come from other estimators or from Q_R and stay on our pT edges, next to an
our-edges value of the refined result (`\chiPaperOurEdges`): the purity-era distances (`\chiPaperPurity`, the
LightGBM-seed range and the HistGBT value at appC), the exact-split distance (`\chiPaperExact`) and appA's Q_R distance.
Joseph: "eh its fine for now, maybe list it as something to tidy up later". They are listed in
`ibu-chi2-20261123/regenA/README.md`'s Deferred tidy-up section, with KNOWN_ISSUES row 103.

## 3. arXiv v1's scope

Joseph: "yes the grid sentences look good. and lets try to fit in the first three items", on the director's list.
v1 aims to include:
- the central-value comparisons with the published result on the published edges, with Joseph's wording, and short
  statements of the open threads (the slight difference in setup from the published result, the open high-p‖
  efficiency question, and the shape difference, with possible sources, under investigation);
- the central-value per-event weights (§1);
- the IBU bias readout (IBUB, Ben's (a));
- the 5D fluctuation block: **V_F is adopted** into the reported 16-cell covariance, with A1 §4's caveat stated (the
  factor measures the toy spread relative to LL5D's rebuilt reference block). The 5D bias block C_b is **not**
  adopted; it is reported descriptively, since it does not span the observed deviations at the held-out tunes
  (`blocks5d-20261124/RECEIPT.md`).

These are **not** in v1 and continue for v2: COVFIX (the 2D bias block), the blind tune replay (PG), the full 2D redo on
the published edges, and the covariance-dependent comparisons on the published edges (regenA part B). Posting, the
Zenodo deposit and every outward act remain Joseph's.

## 4. Earlier decisions recorded here

- **"yes build the 5D bias block"** (2026-11-24). Built under B5D-BINDING-2 (#1320); record merged in #1321.
- **Gemini Hydrogen** (2026-11-24): "note we should also use hydrogen for all of our gemini runs now that it is
  available." agy reads use `gemini-4-hydrogen-high`, and `gemini-4-hydrogen-xhigh` for blocking or adversarial reads.

**CITABLE FOR:** what Joseph decided, and when. **NOT CITABLE FOR:** any number, any note wording, or any claim about the
results.
