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

## Second sync, 2026-11-02 (later): main 58fa0b89

**Why.** Joseph's decision (`DECISION-20261102-joseph-695-quadrant-wording-and-merge.md` item 4) calls for a re-sync after #695.

**The standalone before the copy.** At `92c28241`, with no Overleaf edit since the first sync.

**What was copied.** 6 files changed between `8db2910b` and `58fa0b89`, and none were added or deleted:
- `paper_body.tex`, `sec_fived16.tex` and `values_fived16.tex` (the quadrant sentence and Section IV, #695);
- `make_values_fived16.py`;
- `check_dead_containment.py` and `test_build_all.py` (the standalone containment fix).

Each file compares equal to canonical by `cmp`.

**Builds.**
- **Canonical,** in a fresh worktree: `build_all.sh` gave rc 0, and `latexmk -pdf -jobname=output main_paper.tex` gave rc 0.
- **Standalone copy:** `build_all.sh` gave **rc 0**, with paper 13, note 134, primer 15, PET note 26 and records 59 pp.
  The containment false STALE is gone. The Overleaf target gave rc 0 at 13 pp.
- **Text.** `pdftotext` of all six PDFs is identical between the canonical and standalone builds.

**Head.** Standalone `main` = `88f2547bf2a75b6ed2e0cc4d88684e955761e46f` (from `git ls-remote`), a fast-forward from
`92c28241`. Joseph pulls it in Overleaf from the GitHub menu.

**Next sync:** after the next paper round. Start from base `58fa0b89`.

## Third sync, 2026-11-03: main 3a012f70

**Why.** Joseph's decision (`DECISION-20261103-joseph-711-merge-and-rp9-reprice.md` item 1) calls for a re-sync after
#711.

**The standalone before the copy.** At `0674662`. One Overleaf commit since the second sync, `8670899` ("Updates from
Overleaf"), changed only the mode of `test_build_all.py` (100755 to 100644), not its content. Nothing needed carrying
back.
- Every synced file compared equal by `cmp` to canonical `58fa0b89`, apart from the standalone's own `.gitignore`,
  `AGENTS.md` and `archive/`.

**What was copied.** 7 files changed between `58fa0b89` and `3a012f70`, and none were added or deleted:
- `paper_body.tex`, `sec_5d.tex` and `sec_fived16.tex`;
- `figures/fd_g_fig_modes.pdf` and `figures/fd_g_fig_ratio.pdf`;
- `make_values_fived16.py` and `check_sec4_receipts.py`.

Each compares equal to canonical by `cmp`.

**Builds.**
- **Canonical,** in a fresh worktree at `3a012f70`: `build_all.sh` gave rc 0, with note 135, paper 12, primer 15,
  PET note 26 and records 59 pp. `latexmk -pdf -jobname=output main_paper.tex` gave rc 0: 12 pp and 0 undefined
  references or citations.
- **Standalone copy:** both commands gave rc 0, with the same page counts.
- **Text.** `pdftotext` of all six PDFs (the five, plus `output.pdf`) is identical between the canonical and
  standalone builds.

**Head.** Standalone `main` = `4384f02284da4706dd513c7339fd1d8c423fa159` (from `git ls-remote`), a fast-forward from
`0674662`. Joseph pulls it in Overleaf from the GitHub menu.

**Next sync:** after the next paper round. Start from base `3a012f70`.

## Fourth sync, 2026-11-03 (later): main 1d94b68a

**Why.** Joseph's decision (`DECISION-20261103-joseph-731-restore-and-merge.md` item 2) calls for a re-sync after #731.

**The standalone before the copy.** At `4384f022`, with no Overleaf commit since the third sync.

**What was copied.** 6 files changed between `3a012f70` and `1d94b68a`, and none were added or deleted:
- `paper_body.tex`, `sec_5d.tex`, `app_codebase.tex` and `records_estimators.tex`;
- `check_sec4_receipts.py` and `test_check_sec4_receipts.py`.

Each compares equal to canonical by `cmp`.

**Builds.**
- **Canonical,** in a fresh worktree at `1d94b68a`: `build_all.sh` gave rc 0, with note 136, paper 11, primer 15,
  PET note 26 and records 59 pp. `latexmk -pdf -jobname=output main_paper.tex` gave rc 0: 11 pp and 0 undefined
  references or citations.
- **Standalone copy:** both commands gave rc 0.
- **Text.** `pdftotext` of all six PDFs is identical between the canonical and standalone builds.

**Head.** Standalone `main` = `0b29b02cccbf11591ccf1f94d998d0b5321ac970` (from `git ls-remote`), a fast-forward from
`4384f022`. Joseph pulls it in Overleaf from the GitHub menu.

**Next sync:** after the next paper round. Start from base `1d94b68a`.
