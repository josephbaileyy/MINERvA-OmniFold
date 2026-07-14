# Slide-by-slide outline — 20 min + 5 min discussion

Time budget totals ~19 min of speaking to leave a buffer. Figure names refer to
`figures/` (see `figures-guide.md` for captions). Animation slots refer to
concepts in `animations-and-visuals.md`; the speaker will pick winners from the
generated candidates, so treat slots as reservations, not final choices.

## Act 1 — The problem (3 min, slides 1–3)

**Slide 1 — Title.** Speaker, affiliation, date. Subtitle carrying the
throughline, e.g. "Unbinned unfolding of MINERvA inclusive scattering data."

**Slide 2 — Framing (1 min).** Who I am; using the public MINERvA ME FHC
CC-inclusive data product. Set the contract explicitly: "I'll teach you
OmniFold, show it reproduces your published result, then show what it unlocks."

**Slide 3 — The dimensionality wall (2 min).** Every cross-section
measurement starts by freezing an observable and a binning; each added
dimension multiplies response-matrix bins until they starve of statistics.
- Figure: `minerva_unfolding_landscape.png` (where published MINERvA
  measurements sit in dimensionality).
- Animation slot: **A1 (dimensionality wall)** — motivates the method before
  naming it.

## Act 2 — Teach OmniFold (5–6 min, slides 4–7)

**Slide 4 — Anchor to what they know.** D'Agostini IBU with a response
matrix, drawn as they teach it. Then the key reframe: the response matrix is
just paired (truth, reco) simulated events, histogrammed. Unfolding = deciding
how much each simulated event should count.
- Animation slot: **A2 (bins dissolve into events)**.

**Slide 5 — The OmniFold iteration.** The two-step dance, one box diagram:
Step 1 — reweight simulation to match data at reco level (a learned per-event
weight = a likelihood ratio). Step 2 — pull those weights back to truth level
through the simulation's own (truth, reco) pairing. Iterate. Bin only at the
very end.
- Animation slot: **A3 (one OmniFold iteration / toy convergence movie)** —
  the deck's central animation.

**Slide 6 — Why this is not a black box.** With binned inputs and one
iteration structure, OmniFold *reduces exactly to D'Agostini IBU* — it is a
strict generalization of the method MINERvA already uses, with the histogram
removed. Learned weights come from gradient-boosted decision trees
(deliberately simple and robust), not a deep network.

**Slide 7 — What it buys.** The contrast that carries the whole talk: adding
an observable is *adding an input column*, not *multiplying response-matrix
bins*. Choose bins — and even observables — after unfolding.
- Animation slot: **A4 (bin at the end)**.

## Act 3 — Trust anchor: reproducing the published 2D result (4–5 min, slides 8–10)

**Slide 8 — The money slide.** Unbinned unfold of d²σ/(dp_T dp_∥), binned at
the end into the published binning, overlaid on the published MINERvA points.
- Figures: `MEFHC_5iter_fig13.png` (primary); slice views
  `MEFHC_5iter_xsec_paper_pt_slices.png` / `_pz_slices.png` as alternates.
- Animation slot: **A5 (reproduction reveal)** — published points first, then
  OmniFold result animates on, ratio panel revealed last.

**Slide 9 — Agreement quantified.** Per-bin pulls vs the published result
(`MEFHC_5iter_pull_full.png`). Takeaway: sub-1σ agreement across the plane.

**Slide 10 — Independent uncertainty budget (2D — cleared).** The budget was
rebuilt from scratch (flux, detector, model universes through the unfold) and
matches the published one. "I didn't reuse your machinery; I rebuilt it and
got your answer."
- Figures: `MEFHC_fig6_7_uncertainty_pt.png` / `_pz.png`.

## Act 4 — What higher dimensions reveal (5–6 min, slides 11–13)

**Slide 11 — Opening new axes.** Same events, more columns: add E_avail
(available energy), then q3, then W — a simultaneous 5D unfold. Built-in
cross-check: marginalizing back down reproduces the 2D anchor
(`eavail_marginal_vs_paper_pull_full.png`).
- Animation slot: **A6 (marginalization as validation)**.

**Slide 12 — Re-finding MINERvA's own physics.** The unfolded E_avail
spectrum vs generators: all underpredict at low recoil; Valencia 2p2h fills
the dip between QE and Δ. Their established low-recoil result, recovered by a
completely different method. Strongest physics-credibility slide — give it
room.
- Figures: `eavail_spectrum.png`, `mode_decomp_eavail.png`,
  `compare_mec_eavail.png` (choose 1–2, not all 3).
- Animation slot: **A7 (physics emerging with a new axis)**.

**Slide 13 — Something new.** The residual excess that 2p2h cannot explain
localizes at high E_avail *and* high W (the DIS corner); all four generators
(GENIE MnvTune, bare GENIE, NuWro, GiBUU) underpredict there. Shape-level
statement only — say "significance withheld pending corrected uncertainty
production."
- Figures: `excess_eavail_W.png`; `q3_excess_projection.png` or
  `model_comp_projections.png` as support.
- Animation slot: **A8 (localizing an excess)**.

## Act 5 — Outlook + summary (3 min, slides 14–15)

**Slide 14 — Where this goes (2 min, teaser tone).** Two beats, one slide:
(a) point-cloud transformer (PET) unfolding straight from calorimeter
clusters — toward unfolding raw-ish detector data (`pet_event_displays.png`);
(b) full-phase-space extension with muon cuts removed
(`fps_acceptance_MEFHC.png`). Framed as outlook, not finished precision
results.
- Animation slot: **A9 (point-cloud outlook)**.

**Slide 15 — Summary (1 min).** Restate the throughline in three bullets:
taught the idea, reproduced your result, opened new dimensions. Close with
the ask: guidance on projections the collaboration wants and on
publication-level validation. Invite discussion.

## Backup slides (unlimited; one topic each)

1. OmniFold algorithm equations + density-ratio interpretation (from
   `omnifold-primer.pdf`).
2. Backgrounds, fakes, misses, efficiency handling (`negweight_ratio_2d.png`).
3. Closure/validation suite + classifier calibration
   (`classifier_calibration.png`).
4. Regularization: iteration count + classifier capacity.
5. Seed/train-split variability (`seedscan_band_pt.png`,
   `seedscan_spread_2d.png`).
6. 2D covariance structure (`uq_corr_2d.png`, `uq_spread_2d.png`).
7. Uncertainty-status statement: what is cleared (2D), what is being
   regenerated (N-D budgets, significances), and why — honest and specific.
   Quarantined figures may appear here only, tagged "preliminary".
8. 5D control/corner plots (`control_corner.png`, `control_plots.png`).
9. PET details: cardinality, truth-cloud projections
   (`pet_cardinality_real.png`, `pet_cloud_projection_xsec.png`,
   `pet_vs_gbdt_absolute.png` — central values only).
10. FPS pilot: prior envelope + comparison (`fps_prior_envelope_MEFHC.png`,
    `fps_pilot_compare_MEFHC.png`), labeled preliminary.
