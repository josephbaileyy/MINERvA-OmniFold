# Revised research discussion with Ben

The [October 11 visual revision](../visual/README.md) is the latest version and incorporates the second feedback round.

Revised 10 October 2026 in response to Joseph’s slide questions. Evidence is pinned to inspected remote-main commit `ced3a8db5a8db544436c1f9cf635a8ce79ae73ad`, which is newer than the original presentation’s snapshot. The original presentation is retained in the parent directory.

## Deliverables

- [Editable PowerPoint](MINERvA-OmniFold-Ben-revised.pptx): 24 main slides plus 10 backups, with complete speaker notes and source references.
- [Slide PDF](MINERvA-OmniFold-Ben-revised.pdf): all 34 slides; slide 4 uses the animation’s final static frame.
- [Speaker script PDF](Speaker-script-revised.pdf): 43 pages, including a timed route, backup narration, technical references and glossary.
- [Editable speaker script](Speaker-script-revised.md).
- [Answers and note/paper suggestions](Questions-and-note-suggestions.pdf): every feedback question addressed in 26 grouped answers, followed by seven concrete editorial recommendations.
- [Animation](omnifold-iteration.gif): conceptual six-frame OmniFold iteration sequence, also embedded in slide 4.
- [Structured slide content](presentation-content.json), [answers](questions-and-suggestions.json) and [glossary](glossary.json) support later revision.

The main slide numbering is preserved. Delivery remains an estimated 28 minutes plus two minutes of discussion; the longer answers and backups are outside that route. Rehearsal is still needed to set actual pacing.

## What changed

The script defines closure and coverage before use, explains the continuing 2D estimator-pairing and coverage questions, distinguishes additional physics information from more recorded coordinates, and interprets the seed-sensitivity and grid-refinement numbers. The muon-only non-rejection is now on slide 17. PET slides quantify the historical mismatch, explain interval coverage rather than event classification, and distinguish measured costs from forecasts. Three backups address 2D history, independent information and additional events.

The note/paper recommendations recognize the disclosure corrections already committed upstream. They propose clearer claim boundaries, a validation table, shared-input equations, separation of model and algorithm limitations, safer historical plot labeling, and a scoped cost table. No analysis-note or paper source was modified, and no scientific campaign was started.

## Animation provenance

Recovered from `evidence/prepublication-2026-08-20-0b329e8a:docs/jul-16-presentation/visual-prototypes/presentation-grade/exports/04-algorithm/sequence.gif`. This is the archived July presentation prototype; its identity as the exact collaboration-meeting asset is not established. It illustrates the algorithm with toy events. It is not evidence that every analysis passes closure or coverage.

## Verification

All 34 slides were rendered, and the exported PowerPoint was reopened and rendered again with no pixel differences from the authoring renders. Package, layout and font-policy checks passed without findings. Every script was checked against the corresponding PowerPoint notes; all 76 distinct source references resolve to committed paths or stated external sources. The main timings total 1,680 seconds. PDF text fits within page bounds, and rendered pages were visually inspected. The embedded GIF matches the archived bytes.

Native Microsoft PowerPoint playback and font rendering were not tested. The slide PDF is a stable static viewing copy. These are presentation and provenance checks, not independent scientific verification.
