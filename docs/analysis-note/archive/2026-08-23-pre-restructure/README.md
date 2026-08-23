# Frozen build — analysis note, primer and paper as they stood before the 2026-08-23 restructure

**These three PDFs are immutable. Do not edit, regenerate, or overwrite them.** They are the only
copy of the pre-restructure documents that exists anywhere: `.gitignore:12`
(`docs/analysis-note/main_*.pdf`) keeps the live build outputs out of version control, so rebuilding
the note at the live path destroys the artifact a reader was holding. That is why these are committed
here rather than left to be reproduced.

## What was frozen

| File | Pages | SHA-256 |
|---|---|---|
| `main_note.pdf` | 89 | `968d86c104591576edd6c04a1ddf6e3a30c0322ab092c3c51628638116dc30fc` |
| `main_paper.pdf` | 7 | `e11c497a1e4dbf5cae52a191e80aa66b64c2776cf2f579aaa4c52726af7acb3f` |
| `main_primer.pdf` | 5 | `0fb7d92b19b14dac7bd1dedfcf8e5f3f74a646a9d71261761bdf96a1e727b967` |

**Sources these were built from:** `d3a63bbc15300cb407263cfd6eeacd0ae8cfea31`.
`docs/analysis-note/` was clean against that commit when the copies were taken, and every
`main_note.pdf` mtime was later than every `*.tex` mtime, so the PDFs are that tree's build and not a
stale one. The same tree is tagged `evidence/analysis-note-pre-restructure-d3a63bbc`.

## Why the restructure happened

The note was carrying the campaign's audit trail inside its physics argument. Measured on
`d3a63bbc`, in text that reaches the reader:

- **16 reviewer-comment macros** (`\gk`/`\jrb`/`\bpn`) rendered in `main_note.pdf` and 0 in
  `main_paper.pdf` — including a reading bookmark (`sec_pet.tex:4`, `\bpn{left off here}`) and a
  ~250-word inline reply at `sec_experiment.tex:47`.
- **31 `\dead{}` struck values** scattered across three files, each with prose explaining its own
  retraction.
- **~3,150 words** of provenance and governance blocks — "the fork as it stood when this section was
  first written", "must not be edited into establishing", enumerations of LaTeX macro names, HPSS
  tape-durability receipts, verifier verdict JSON paths — roughly 9 of 89 pages.
- Quarantine vocabulary at a density no physics document sustains: "diagnostic" ×42, "gate" ×31,
  "struck" ×16, "candidate" ×13, "historical" ×14.

That material already had a canonical home in `docs/orchestration/INDEX-retracted-and-superseded-values.md`,
`VALIDATION_LEDGER.md` and `docs/OPEN_ITEMS.md`. The note was a second, drifting copy of it.

Structurally, two outside readers had already said so and their comments were still rendering:
`sec_experiment.tex:104` (GK, on interleaving generic method with MINERvA-specific plots and asking
for an Introduction–Methods–Data–Results spine) and `sec_results.tex:5` (GK, "I feel like section 4
already belongs in Results?"). `paper_body.tex` already implemented the requested spine.

**Nothing in the restructure was a physics correction.** No central value, covariance, closure
result or generator comparison changed. Numbers that were struck were deleted along with their
retraction prose rather than restated, and the reason each was struck is preserved in the retraction
index, not in the note.

## Recovering the pre-restructure sources

```bash
git show evidence/analysis-note-pre-restructure-d3a63bbc:docs/analysis-note/sec_pet.tex
git worktree add /tmp/note-old evidence/analysis-note-pre-restructure-d3a63bbc   # whole tree
```

To rebuild from those sources, in that worktree: `cd docs/analysis-note && ./build_all.sh`. The
rebuild will reproduce these page counts; it is not required to reproduce these bytes, because
`latexmk` embeds a build timestamp.

## Retention status

This directory is a frozen build artifact, not a document a session needs to read. It is outside the
`docs/orchestration/` inventory that `CONVENTION-document-retention.md` governs, so it takes no
`MANIFEST-overrides.tsv` row — per that convention's scope rule, a row here would be inert and would
add an `unused_overrides` warning. The convention's substantive rule is still honoured: nothing was
moved, renamed, or deleted to express retirement. The live build path is unchanged and these are
copies.
