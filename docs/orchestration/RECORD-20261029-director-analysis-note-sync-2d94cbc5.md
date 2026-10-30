# RECORD: the standalone Analysis-Note repository synced to main 2d94cbc5 (2026-10-29)

**By** the paper-tighten lane, as director, at Joseph's request ("Sync now (Recommended)", 2026-10-29). It follows
the procedure in [`HANDOFF-20260928-s5p-analysis-note-sync.md`](HANDOFF-20260928-s5p-analysis-note-sync.md) §"Next
synchronization". **CITABLE FOR:** which canonical commit the standalone mirrors, and the checks made. **NOT
CITABLE FOR:** any physics number, claim or readiness. Nothing is submitted, deposited or tagged.

- **Source:** `docs/analysis-note/` at canonical `main` `2d94cbc5efbd2d6372eabc7ae6116e0454d915df`.
- **Before:** the standalone's 151 synced files were byte-identical to canonical `eb743270`, the 10-27 sync. The one
  Overleaf commit since, `9a93d43`, changed only `test_build_all.py`'s mode. So no edit made in Overleaf needed carrying
  back.
- **Copied:** 36 files changed or added, and 1 deleted (`result_status_rows.tex`). After the copy, every file of main's
  `docs/analysis-note/` compared equal by `cmp`, and the pushed tree compared equal again after a fresh `git archive`.
- **Builds:** `bash build_all.sh` rc 0 in both trees, at note 126, paper 11, primer 15, PET note 26 and records 58 pp.
  The Overleaf target `latexmk -jobname=output main_paper.tex` gave rc 0 and 11 pp in both. `pdftotext` of all six
  PDFs is identical between the canonical and standalone builds.
- **Heads:** standalone `https://github.com/josephbaileyy/MINERvA-OmniFold-Analysis-Note` `main` =
  `35d037e272fb89aa40bd9b7703ab3be762bf0dff`. It is a fast-forward from `162f82f`, through the sync commit `aaa9637`
  and a follow-up that restores `test_build_all.py`'s executable mode, which the first commit did not stage.
- **Next sync:** after the r22 rounds (`DECISION-20261029-joseph-register-rounds-reopen.md`). Start from base
  `2d94cbc5`.
