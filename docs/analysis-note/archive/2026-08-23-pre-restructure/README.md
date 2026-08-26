# Frozen build — analysis note, primer and paper as they stood before the 2026-08-23 restructure

**These three PDFs are immutable. Do not edit, regenerate, or overwrite them.** They are the only
copy of the pre-restructure documents: `build_all.sh` writes `main_note.pdf`, `main_paper.pdf` and
`main_primer.pdf` at the repo root, and `.gitignore` keeps those live outputs unversioned, so
rebuilding destroys the artifact a reader was holding.

## What was frozen

| File | Pages | SHA-256 |
|---|---|---|
| `main_note.pdf` | 89 | `968d86c104591576edd6c04a1ddf6e3a30c0322ab092c3c51628638116dc30fc` |
| `main_paper.pdf` | 7 | `e11c497a1e4dbf5cae52a191e80aa66b64c2776cf2f579aaa4c52726af7acb3f` |
| `main_primer.pdf` | 5 | `0fb7d92b19b14dac7bd1dedfcf8e5f3f74a646a9d71261761bdf96a1e727b967` |

These bytes are **byte-identical** to the copy committed in the analysis repository at
`docs/analysis-note/archive/2026-08-23-pre-restructure/`, verified with `cmp` at
sync time. That repository is the authority for the sources; the tag
`evidence/analysis-note-pre-restructure-d3a63bbc` there points at the tree these were built from
(`d3a63bbc` for the note sources, archived under commit `c73be5e1`).

## Why the restructure happened

The note was carrying the campaign's audit trail inside its physics argument. Measured on the frozen
build, in text that reaches the reader:

- **16 reviewer-comment macros** (`\gk`/`\jrb`/`\bpn`) rendered in `main_note.pdf` and 0 in
  `main_paper.pdf` — including a reading bookmark (`\bpn{left off here}`) and a ~250-word inline
  reply in `sec_experiment.tex`.
- **31 `\dead{}` struck values**, 12 of them in physics sections, each with prose explaining its own
  retraction.
- **~3,150 words** of provenance and governance blocks — "the fork as it stood when this section was
  first written", "must not be edited into establishing", enumerations of LaTeX macro names, tape
  durability receipts, verifier verdict paths — roughly 9 of 89 pages.

Two outside readers had already said so, and their comments were still rendering: `sec_experiment.tex`
(on interleaving generic method with MINERvA-specific plots, asking for an
Introduction–Methods–Data–Results spine) and `sec_results.tex` ("I feel like section 4 already
belongs in Results?"). `paper_body.tex` already implemented the requested spine, so the restructure
followed it: uncertainty *construction* stays with method, the measured *budget* moved to Results, and
the recoil-point-cloud material was consolidated out of the Validation section.

**Nothing in the restructure was a physics correction.** No central value, covariance, closure result
or generator comparison changed. Struck values were deleted together with their retraction prose
rather than restated; why each was struck is preserved in the analysis repository's retraction index,
not in the note.

Four defects *were* found and fixed while restructuring, and none of them originated in it: a claim
asserting a fork resolved that the governing record had retracted on a type mismatch; a dropped
`INSUFFICIENT` label that still stands; a dropped warning guarding a receipt pointer the note makes;
and one symbol, `C_stat`, silently denoting two different covariance objects ~150 pages apart.

## Rebuilding the pre-restructure sources

The sources are not in this directory — only the built PDFs. Recover them from the analysis
repository:

```bash
git -C <analysis-repo> worktree add /tmp/note-old evidence/analysis-note-pre-restructure-d3a63bbc
cd /tmp/note-old/docs/analysis-note && ./build_all.sh
```

That reproduces these page counts. It will not reproduce these bytes: `latexmk` embeds a build
timestamp.

## Note on this repository

This repo is a flat, note-only mirror: sources at the root rather than under `docs/analysis-note/`,
with its own history and periodic content syncs from the analysis repository. It is not a subtree, so
`git log` here shows sync commits rather than the upstream per-change history — read the analysis
repository for that.
