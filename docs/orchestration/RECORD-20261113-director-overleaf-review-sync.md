# RECORD: the standalone Analysis-Note repository synced to a review snapshot for Ben (2026-11-13)

**By** the paper-tighten lane, as director, at Joseph's request.

**Authorization.** Joseph's words, verbatim:

> you can sync the overleaf, only ben and I have access to it.

(`111dffa1d8dd9fde`, the sha256 of the text plus a final newline). It was the first line of his message, which went on to
paste the note loop's report and ask for the latest note.

**What was synced.** A local review merge, never pushed to MINERvA-OmniFold:
- the base is main `07d780ed`;
- merged into it: the methods-paper draft #977 (`draft/methods-short-20261109` at `91b0af8e`) and the note draft #952
  (`draft/note-round2-20261108` at `4836da13`);
- two conflicts were resolved:
  - `MANIFEST-overrides.tsv`, as a union of both sides;
  - `make_values_fived16.py` LISTED_CLAIMS: the paper's anchor was taken from #977 and the note's from #952.
- After the merge, `make_values_fived16.py --check` gave PASS (4258 values), and `--self-test` gave PASS.

**The copy.**
- All 216 tracked files of `docs/analysis-note/` were copied into the standalone. After the copy, every file compares
  equal by `cmp`.
- The standalone-only files were kept: `.gitignore`, `AGENTS.md` and `archive/`.
- No standalone file was deleted, because no canonical file is missing there.

**Builds:**
- Canonical: paper 19 pp, Supplement 38 pp and note 143 pp, each with 0 undefined references or citations.
- Standalone copy, in a separate build directory: the same three, with `pdftotext` identical to the canonical build.

**Head.** Standalone `main` is `453a67bcd1749b84308ae57a178ea7008e97fa42` (from `git ls-remote`), a fast-forward from
`3d96c939`. Joseph pulls it in Overleaf from the GitHub menu.

**What this is not.**
- Not a merge of #977 or #952. Both remain drafts.
- Not a publication, submission or deposit. The Overleaf project is shared only between Joseph and Ben.
- The next sync starts from base `07d780ed` plus the two draft heads named above.

Nothing is submitted, deposited or tagged.
