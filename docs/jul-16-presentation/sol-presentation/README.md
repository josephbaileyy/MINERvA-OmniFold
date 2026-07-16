# OmniFold with MINERvA open data — July 16 presentation

Self-contained 16:9 HTML deck for a 20-minute MINERvA collaboration talk plus
discussion. The main deck contains 14 slides and six backup slides.

## Present

Open `index.html` directly, or serve the directory locally:

```bash
cd docs/jul-16-presentation/sol-presentation
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

Controls:

- `→`, space, enter: advance one build or slide
- `←`, backspace: reverse one build or slide
- `N`: speaker notes
- `F`: fullscreen
- `Home` / `End`: first / final main slide
- `P`: browser print dialog

Click the leftmost 22% of the slide to go backward; click elsewhere to advance.
URLs are stable (`#1`–`#14`, then `#b1`–`#b6`).

## PDF fallback

`presentation.pdf` is a generated 14-page, 16:9 static fallback with every
build revealed. To export a revised deck, use the browser print dialog with
backgrounds enabled and margins disabled. Print CSS exports the 14 main slides
and omits backups and presentation controls.

## Content status

The main deck intentionally uses only:

- the finalized 2D result and its cleared uncertainty budget;
- current 4D/5D central values, closure and marginalization anchors;
- qualitative N-D shape observations without covariance significance;
- PET as a central-value/outlook topic without a precision comparison.

Backup slide B6 is date-stamped and must be refreshed against
`nd-unfolding/ND_OMNIFOLD_STATUS.md` immediately before the talk. Do not add
quarantined N-D/PET covariance totals or generator significances unless the
replacement artifact and its ledger/RUN_LOG/STATUS documentation land together
under the repository commit gate.

## Asset provenance

Presentation-safe analysis figures were rasterized at 180 dpi from the vector
PDFs in `docs/analysis-note/figures/`. Method diagrams and animations are native
HTML/CSS/SVG in this directory and require no network resources.
