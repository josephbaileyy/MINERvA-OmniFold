# Animation & visual menu — generate candidates, speaker picks

Generate **2–3 stylistic variants** of each Tier-A concept (and Tier-B if
capacity allows). Variants can differ in visual metaphor, pacing, or layout —
not in physics content. Every animation must have a **static final frame**
that stands alone on a slide.

**Global color semantics (hold across every animation and figure-adjacent
graphic):** data = black points; unweighted simulation = one fixed cool color;
reweighted simulation = one fixed warm color; per-event weights encoded as
point size or opacity. Truth level vs reco (detector) level should be two
clearly distinct spatial zones (e.g. upper/lower plane) reused identically in
every animation.

Physics-accuracy note: these are *conceptual* animations on toy data — do not
fabricate axes/numbers that look like real results. Keep toy axes unlabeled or
generically labeled ("observable x"). Real results only come from `figures/`.

---

## Tier A — must generate (the deck depends on these)

### A1 — The dimensionality wall
*Slide 3. Purpose: motivate unbinned unfolding before naming it.*
Beats: (1) a healthy 1D response matrix, cells well-populated; (2) extrude to
2D — cell count multiplies, colors thin; (3) hint 3D — mostly-empty sparse
grid; (4) the grid dissolves and the same statistics reappear as a cloud of
individual events, comfortably dense. Tagline on final frame: "The events were
never the problem — the bins were."

### A2 — Bins dissolve into events (the D'Agostini bridge)
*Slide 4. Purpose: show OmniFold is their method with the histogram removed.*
Beats: (1) classic response-matrix picture: truth bins on one side, reco bins
on the other, arrows weighted by migration probability; (2) each arrow
dissolves into the individual paired (truth, reco) simulated events that
filled it, joined by faint pairing lines; (3) the bin edges fade away; the
pairing lines remain. Final frame: pure paired-event picture, caption "the
response matrix, before it was histogrammed."

### A3 — One OmniFold iteration → convergence (central animation)
*Slide 5, and reusable as the deck's visual motif.*
Toy setup: truth-level spectrum (e.g. a two-peak shape), smeared to reco
level; simulation drawn as paired dots (truth zone ↔ reco zone) with faint
pairing lines; data as black points at reco level only.
Beats per iteration: (1) *Step 1:* reco-level simulated dots re-size/brighten
so their ensemble morphs to match the data points — annotate "learn per-event
weights (a likelihood ratio)"; (2) *Step 2:* the weights visibly travel up the
pairing lines to the truth-level dots — annotate "pull weights back to truth
through the simulation's own pairing"; (3) loop arrow, repeat ×3–4 with
visibly shrinking corrections; (4) final frame: weighted truth-level ensemble
overlays the (revealed) true spectrum. A slider or step-through variant is
welcome as an alternative to autoplay.

### A4 — Bin at the end
*Slide 7. Purpose: the payoff of unbinned unfolding.*
Beats: one weighted truth-level event cloud stays fixed while, around it:
(1) one binning drops in as a histogram; (2) different bin edges replace it —
same events, new histogram, no re-unfold; (3) the axes rotate/swap to a
*different observable* and a histogram of that appears; (4) final frame: the
cloud in the center, three different histograms orbiting it. Caption: "one
unfolding, any histogram."

### A5 — Reproduction reveal
*Slide 8. Purpose: dramatize the trust anchor without editorializing.*
Beats: (1) show the published MINERvA points alone (recreate stylized markers,
or build around `figures/MEFHC_5iter_fig13.png`); (2) the OmniFold result
draws on top; (3) only then reveal the ratio/pull panel. Keep it dry — the
agreement is the drama.

---

## Tier B — strong candidates (generate if capacity allows)

### A6 — Marginalization as validation
*Slide 11.* A 3D event volume (p_T, p_∥, E_avail) collapses along E_avail
into the familiar (p_T, p_∥) plane, which then clicks into alignment with the
established 2D result. Caption: "every new dimension carries its own
cross-check."

### A7 — Physics emerging with a new axis
*Slide 12.* Start from the 2D (p_T, p_∥) projection; open the E_avail axis
like a drawer; the low-recoil region highlights; the 2p2h component fades in
to fill the dip between the QE and Δ peaks. Should visually echo
`figures/mode_decomp_eavail.png` so animation and real figure rhyme.

### A8 — Localizing an excess
*Slide 13.* A broad 1D data–simulation discrepancy resolves, as a second axis
(W) opens, into a compact highlighted region in the (E_avail, W) plane —
the DIS corner. End frame labeled "central-value observation; significance
pending corrected uncertainties." No fake significance numbers.

### A9 — Point-cloud outlook
*Slide 14.* Detector-style cluster display (echo
`figures/pet_event_displays.png`) → clusters lift into an unordered point
cloud → the cloud becomes one weighted event → several possible final
observables fan out. Short and visually distinct from the completed-results
sections (e.g. different background tint) so it reads as outlook.

---

## Tier C — optional garnish

### C1 — Smearing primer micro-animation
A single truth-level spike smears into a broad reco distribution (and a
dotted arrow back). 3-second build to set up Act 2 for non-experts; skip if
Act 2 already reads clearly.

### C2 — Recurring mini-motif
A tiny corner glyph of the A3 two-step loop (reweight ↘ pull-back ↖) reused
as a section marker whenever the method is being applied — visual continuity
without new motion.

### C3 — "One column, not a matrix" contrast card
Static or two-beat: left, response-matrix bins multiplying (2 → 4 → 8 …);
right, a data table simply gaining one more column per observable. The
contrast that carries the whole argument, as a single crisp graphic.

---

## Rejection criteria (what NOT to make)

- No animations that imply the ML "discovers" physics — the method reweights
  simulation; the physics claims come from the binned-at-the-end comparisons.
- No motion on results slides beyond the A5 reveal — real figures stay still.
- Nothing that requires video codecs to survive export; prefer stepped builds
  (native slide transitions) or embedded GIF/APNG with a static fallback.
