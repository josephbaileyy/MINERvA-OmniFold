# Brief for Claude Design — MINERvA collaboration talk, July 16, 2026

## The job

Build a **20-minute talk (+5 min discussion), 16:9 slide deck (~14–16 content
slides + backups)** following `outline.md`, and — separately — **generate
multiple candidate animations and visuals** from the menu in
`animations-and-visuals.md`. For each animation concept, produce 2–3 stylistic
variants where sensible; the speaker will review all candidates and pick
favorites before the deck is finalized. Prioritize the Tier-A animations first.

## Speaker and audience

- **Speaker:** Joseph Bailey, graduate researcher. An *outsider* to the MINERvA
  collaboration, presenting to them for the first time, using their public
  ME FHC CC-inclusive data product.
- **Audience:** the MINERvA neutrino-scattering collaboration. They built the
  detector and published the flagship measurement this work reproduces. They
  know traditional unfolding deeply (D'Agostini iterative Bayesian unfolding,
  binned response matrices, their MAT/MnvH1D framework). Most have **never
  heard of OmniFold** or ML-based unbinned unfolding.
- **Stated goal:** teach the core OmniFold idea, establish trust by reproducing
  the published 2D result, then show what higher-dimensional event-level
  unfolding unlocks. It does NOT have to cover everything in the analysis note.

## The throughline (the one sentence the audience should leave remembering)

> Learn weights on events instead of filling a response matrix; recover the
> published MINERvA result; then use the same idea to open dimensions that
> were previously difficult to measure together.

## What's in this package

| Item | What it is |
|---|---|
| `README.md` | This brief. |
| `outline.md` | Slide-by-slide outline with time budget, figure assignments, and animation slots. |
| `animations-and-visuals.md` | The menu of animation/visual concepts to generate candidates from. |
| `figures-guide.md` | One-line caption + intended slide + usage flag for every figure. |
| `figures/` | Final result figures (PNG, rendered from the note's vector originals). Safe to use anywhere in the deck. |
| `figures-quarantined-backup-only/` | Figures whose uncertainty/significance content is under regeneration. **Do not place these on main slides.** See rules below. |
| `analysis-note.pdf` | The full analysis note — the source of truth for all physics content, numbers, and terminology. |
| `omnifold-primer.pdf` | A shorter pedagogical primer on the method — the best source for the "teach OmniFold" section's language and level. |

## Hard content rules

1. **Numbers only from sources.** Every number on a slide must come from
   `analysis-note.pdf`, `omnifold-primer.pdf`, or a figure in `figures/`.
   Never invent, estimate, or "typical-value" a physics number. If a slide
   wants a number the sources don't provide, leave a clearly marked
   `[SPEAKER: number]` placeholder.
2. **The uncertainty quarantine.** Parts of the N-dimensional uncertainty
   budget are being regenerated after a methodology fix. Concretely:
   - Central values, closure tests, marginalization cross-checks, and
     *shape-level* statements ("the excess concentrates at high E_avail and
     high W") are fine and encouraged.
   - The **2D uncertainty budget is cleared** (it independently matches the
     published one) — use it freely.
   - Do **not** quote any 3D/4D/5D uncertainty budget, any covariance-based
     significance (no "Nσ" for the high-E_avail/W excess), or any PET-vs-GBDT
     *precision* comparison. Where the narrative wants one, write
     "significance withheld pending corrected uncertainty production" — this
     honesty is deliberate and audience-appropriate.
   - Figures embodying quarantined content are segregated in
     `figures-quarantined-backup-only/`. They may appear only in backup
     slides, each carrying a visible "uncertainty under regeneration —
     preliminary" tag.
3. **Speak the audience's dialect.** Use their terms: "D'Agostini IBU",
   "response matrix", "low-recoil excess", "Valencia 2p2h", "E_avail"
   (available energy), "ME FHC". Avoid ML jargon where a physics phrase
   exists (say "learned per-event weight," not "classifier logits").
4. **Credibility ordering is non-negotiable.** The 2D reproduction comes
   before any new result. Never present a new claim before the corresponding
   trust anchor.
5. **Tone:** confident, concrete, modest. No hype words ("revolutionary",
   "game-changing"). The results carry the talk.

## Design rules (from the speaker)

- **Visual restraint:** two or three memorable animations reused as recurring
  motifs beat motion on every slide.
- **One conceptual change per click/build.** Use builds to steer attention.
- **Every animation needs a static final frame** that works if playback fails,
  in a PDF export, or in backup slides.
- **Color semantics are global and never change:** data, unweighted
  simulation, and reweighted simulation each get one fixed color/identity for
  the entire deck (suggestion: data = black points, unweighted simulation =
  gray/blue, reweighted simulation = orange/red — but pick a palette and hold
  it). Weights may be encoded as point size or opacity, consistently.
- Slide count discipline: ~14–16 content slides for 20 minutes. Backups are
  unlimited.
- The provided figures are matplotlib output with axis labels sized for a
  document; when a figure carries a slide, add a large plain-language takeaway
  title above it (e.g. "Same data, same answer as the published analysis").

## Discussion-period backups to prepare (5 min Q&A)

One backup slide each: prior/model dependence; regularization (iteration count
+ classifier capacity); backgrounds/fakes/misses/efficiency handling;
uncertainty propagation status (the honest quarantine statement); GBDT-vs-NN
cross-check; classifier calibration (`figures/classifier_calibration.png`).
