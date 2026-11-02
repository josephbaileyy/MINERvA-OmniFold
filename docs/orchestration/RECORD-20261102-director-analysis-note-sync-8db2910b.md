# RECORD: the standalone Analysis-Note repository synced to main 8db2910b (2026-11-02)

**By** the paper-tighten lane, as director.

**Why.** Joseph asked: "can you update the overleaf too" (2026-11-02). The procedure is
[`HANDOFF-20260928-s5p-analysis-note-sync.md`](HANDOFF-20260928-s5p-analysis-note-sync.md) §"Next synchronization".

**CITABLE FOR:** which canonical commit the standalone mirrors, and the checks made.

**NOT CITABLE FOR:** any physics number, claim or readiness.

Nothing is submitted, deposited or tagged.

## What was synced

- **Source:** `docs/analysis-note/` at canonical `main` `8db2910ba78d3e80116bbaadcf7009689018683e`.
- **The standalone before the copy.** At `35d037e2`, with no Overleaf commit since the 10-29 sync. Every synced file was
  byte-identical to canonical `2d94cbc5`, apart from the standalone's own `.gitignore`, `AGENTS.md` and
  `archive/`. Nothing needed carrying back.
- **Copied.** 54 files changed between `2d94cbc5` and `8db2910b` (62 commits), with none added or deleted.
  - After the copy, every file of canonical's tree compared equal by `cmp`, including
    `archive/2026-08-23-pre-restructure/`.
  - The two file sets are equal, apart from the standalone-only files above.

## Builds

**Canonical**, in a fresh worktree at `8db2910b`:
- `bash build_all.sh` gave rc 0: note 133, paper 12, primer 15, PET note 26 and records 59 pp.
- The Overleaf target, as `latexmk -pdf -jobname=output main_paper.tex`, gave rc 0: 12 pp, 0 undefined references,
  and `pdftotext` identical to `main_paper.pdf`.
- **A note on the command.** The plain `latexmk -jobname=output main_paper.tex` of the earlier records ran in DVI
  mode here (no latexmkrc) and stopped on a PDF figure (rc 12). Overleaf compiles with pdfLaTeX, so `-pdf` is the
  faithful target. The handoff's command should read `-pdf` from now on.

**Standalone,** a build copy of the synced tree:
- The Overleaf target gave rc 0, at 12 pp.
- `pdftotext` of all six PDFs (note, paper, primer, PET note, records, output) is identical to the canonical build's.
- `bash build_all.sh` gave **rc 1**, from one containment check. The failure is specific to the standalone:
  - **The check.** It reads `CONTEXT_EXEMPT[('main_note', '6.86')]`, which #665 re-pointed to
    `../orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e/rerun1/chain/chdefs/with/figures/fd_g_fig_modes.json`.
  <!-- absence-ok: a measured path check on the standalone clone (the file is outside docs/analysis-note), not a claim that a result does not exist -->
  - **Why it fails.** That path lies outside `docs/analysis-note/`, so it does not exist in the standalone, and the
    check reports the exemption as stale.
  - **Canonical passes, and the PDFs are unaffected.** The fix is in canonical: the check must resolve its sources
    inside the note tree, or SKIP as its other repository-dependent checks do. It is commissioned to the paper lane.
    Overleaf runs only the latexmk target.

## Heads (from `git ls-remote` after the push)

- Standalone `https://github.com/josephbaileyy/MINERvA-OmniFold-Analysis-Note` `main` =
  `92c282411b09e71931144be589cc4d8f911fe185`. This is a fast-forward from `35d037e2`, by the sync commit alone.
- **For Overleaf to show it,** Joseph pulls from GitHub in the Overleaf project's GitHub menu.

**Next sync:** after the Section IV and quadrant round (#690 items 1–2). Start from base `8db2910b`.
