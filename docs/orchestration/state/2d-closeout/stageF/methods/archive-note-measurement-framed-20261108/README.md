# Archive: the measurement-framed analysis note as of 2026-11-08

**What this is.** This is the last version of the companion analysis note written as the record of a measurement,
with the sixteen-cell five-observable cross section as its principal result. It was archived on Joseph's instruction,
before the note was reframed as the technical record of the methods-and-benchmark study
(`DECISION-20261108-joseph-note-framing-and-estimator-dependence.md`, item 2; #947, merged on main at `af73565048b2882efa1ea52f1d8a953902aceb31`). **It is the starting point for a return
to the measurement framing.** That is the director's reading of Joseph's "in case we are ever able to move back", recorded
in the decision; Joseph corrects it if he meant otherwise. The measurement-framed paper of 2026-11-06 is archived beside
it, in `../archive-measurement-framed-20261106/`.

**The source.** It is commit `b551b05fb020926296c659542eebc91f98ec6214` on main, the merge of #944, at 2026-11-08
09:56:55 −0800, under `docs/analysis-note/`. No note source changed on main between that commit and the decision's merge
(`git diff b551b05f af735650 -- docs/analysis-note` is empty).
`SOURCE-MANIFEST.tsv` lists every tracked file under that directory at that commit, 155 files, each with its blob sha.
The `archive/` subdirectory is excluded.
- Every input the note build read, as listed in `main_note.fls`, is a tracked file at that commit, apart from the
  build's own intermediates (`.aux`, `.bbl`, `.out`, `.run.xml`, `.toc`).
- The commit is in main's history, and main is never rewritten. That history is what keeps this archive's source
  durable. No tag was pushed, since tags are reserved to Joseph.

**The built file.** Built by the limitation-resolver lane in a detached worktree of that commit with
`PAR_GLOBAL_TEMP=<fresh dir> bash build_all.sh`, rc 0, with every gate passing (`RESULT :: PASS`, tree clean).
`build-log.txt` is the full log. Its "undefined references" warnings come from intermediate passes. The final pass
records no unresolved reference ("OK main_note.pdf written by this run; no unresolved references"), and the note's
extracted text contains no `??`.

| file | pages | sha256 |
|---|---:|---|
| `main_note.pdf` | 137 | `f6d7d80c9051925e3358258ed0351c376b5cc0fb5764064bd6a3c295ef92ff33` |

**The toolchain** (macOS, local): Latexmk 4.83, biber 2.19, and pdfTeX 3.141592653-2.6-1.40.26 (TeX Live 2024). PDF
bytes carry build timestamps, so a rebuild matches this one in pages and text, not byte for byte.

**To rebuild:**

```
git worktree add --detach <dir> b551b05fb020926296c659542eebc91f98ec6214
cd <dir>/docs/analysis-note
PAR_GLOBAL_TEMP=$(mktemp -d) bash build_all.sh
```

**What this archive is not.**
- It is not a submission, a deposit or a release. Nothing here is sent anywhere.
- It does not endorse the measurement framing. The evidence that led to the change is in
  `DECISION-20261106-joseph-methods-study-and-archive.md` and the publication-scope package
  (`../secondary-results/scope-decision-package-20261106/REPORT.md`, section 6).
- It predates round 1 of the note's currency audit (`../note-round1-20261108/AUDIT.txt`): the results that landed from
  2026-11-01 on, listed there, are not in it.
- The note's limitation statements stand as written in this version.
