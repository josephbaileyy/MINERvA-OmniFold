# design-talk — local mirror of the claude.ai/design deck (improved)

Local working copy of the Claude Design project
(claude.ai/design/p/61fbccfd-65d5-44bf-98c7-5831aa807b82), merged with the
best ideas from the sibling `sol-presentation/` per `../COMPARISON.md`, and
kept in sync with the cloud project via the design MCP.

Open `talk/index.html` in a browser (no server needed). `uploads/` is a
symlink to `../claude-design-package` so the white-plate backup figures
resolve; in the cloud project they are real uploads.

## What was merged (2026-07-13)

- **Animations**: the user-picked winners from the project's `anims/` review,
  ported to vanilla canvas JS in `talk/anims.js` — A1 variant 2 (three-panel
  ticker, own slide), A3 (central iteration animation, autoplay + beat
  step-through), A6 (variants 1 and 2, toggleable), A8 variant 1 (fan-out).
  Each autoplays on slide entry, parks on its static final frame for
  print/PDF, and has pause / beat / restart / final / scrub controls.
- **Pedagogy from sol-presentation**: classifier-as-ratio-estimator slide
  (w = p/(1−p)); response-matrix-vs-paired-events visuals; bins-multiply vs
  columns-add mini-graphics; validation-numbers grid (2D same-ensemble mean
  $|r|=0.794$ vs 0.798, explicitly not coverage; iterations 0.026 %, NN/GBDT 1.008,
  descriptive C2ST AUC 0.535→0.501 with no calibrated p-value); money-slide stat rail
  (1.011 / 1.006 / 94.1 %); honest χ²/ndf = 3.66 → 1.48 framing (+ backup
  B6b anatomy); MINERvA implementation backup B1b.
- **Dark figures**: main-act figures regenerated on the deck ground with
  `TECHNOTE_DARK=1` (gated block in repo-root `technote_style.py`;
  transparent figure ground, dark-validated generator palette) into
  `talk/figures-dark/`. Regenerate via the `make_figures.sh` invocations with
  `TECHNOTE_DARK=1`, then restore the canonical light outputs (the note's
  figure sync must never see dark versions). Backup figures stay white-plate.
  `pet_event_displays.png` has no generating script (ad-hoc product) and
  stays white-plate.

## Numbers provenance

All quoted numbers come from `docs/analysis-note/values.tex` and
`sec_validation.tex` (cleared 2D results only; N-D significances remain
withheld per the quarantine).
