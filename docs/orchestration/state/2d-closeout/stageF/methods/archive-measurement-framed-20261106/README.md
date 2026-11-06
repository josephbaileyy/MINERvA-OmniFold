# Archive: the measurement-framed paper as of 2026-11-06

**What this is.** This is the last version of the paper written as a measurement, with the 5D multi-observable table as
its headline. It was archived on Joseph's instruction when the working target changed to a methods and benchmark study
(`DECISION-20261106-joseph-methods-study-and-archive.md`). Joseph is taking both options to Ben, so this framing has
to stay retrievable exactly as it was.

**The source.** It is commit `3bd6e3ce30438936ebbe3f1697bff6b91c108685` on main, the merge of #827, at 2026-11-06
08:00:58 −0800, under `docs/analysis-note/`. `SOURCE-MANIFEST.tsv` lists every tracked file under that directory at that
commit: 155 files, each with its blob sha. The `archive/` subdirectory is excluded.
- Every input the paper build read, as listed in `main_paper.fls`, is a tracked file at that commit, apart from the
  build's own intermediates (`.aux`, `.bbl`, `.out`).
- The commit is in main's history, and main is never rewritten. That history is what keeps this archive's source
  durable. No tag was pushed, since tags are reserved to Joseph.

**The built files.** Built by the director in a detached worktree of that commit with `PAR_GLOBAL_TEMP=<fresh dir> bash
build_all.sh`, rc 0. `build-log.txt` is the full log. Its "undefined references" warnings come from intermediate passes: the final-pass `main_paper.log` and `main_note.log` have none, and the paper's extracted text contains no `??`.

| file | pages | sha256 |
|---|---:|---|
| `main_paper.pdf` | 13 | `ee9d6047219be996619d6bfed42bcbe51efe219b4f438dcf9b6638592ccc056c` |
| `main_note.pdf` | 136 | `bd16034cfb562717815e6a65d2ea7f324227103a4b9c512cdb1367504afd8e6e` |

**The toolchain** (macOS, local): Latexmk 4.83, biber 2.19, and pdfTeX 3.141592653-2.6-1.40.26 (TeX Live 2024). PDF
bytes carry build timestamps, so a rebuild matches this one in pages and text, not byte for byte.

**To rebuild:**

```
git worktree add --detach <dir> 3bd6e3ce30438936ebbe3f1697bff6b91c108685
cd <dir>/docs/analysis-note
PAR_GLOBAL_TEMP=$(mktemp -d) bash build_all.sh
```

**What this archive is not.**
- It is not a submission, a deposit or a release. Nothing here is sent anywhere.
- It does not endorse the measurement framing. The evidence that led to the change is the publication-scope package
  (`../secondary-results/scope-decision-package-20261106/REPORT.md`, section 6).
- The paper's existing limitation statements stand as written in this version.
