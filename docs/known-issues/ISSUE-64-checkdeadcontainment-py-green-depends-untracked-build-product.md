# ISSUE-64 — checkdeadcontainment.py's green depends on an UNTRACKED build product, so a reported exit 0 cannot be mapped to a sha — the same class as row 60(1)

**Severity:** MEDIUM. **Status:** OPEN. **Index row:** `KNOWN_ISSUES.md` row 64. **Updated:** 2026-09-22.

Moved here from the index on 2026-09-22 (self-round 52), text unchanged, because `KNOWN_ISSUES.md`
is an index and not a copy: its own header says so, it was compacted to 8,720 B at `1f714b7f` to
obey that, and this lane had grown it from 65,681 B (at `177af61b`) to 96,816 B, almost all of it in these thirteen rows.

## Detail

**MEASURED 2026-09-22.** Run at HEAD in a checkout without built PDFs it returns **exit 1**, `RESULT :: FAIL`, sole cause *"main_note.pdf absent … PDF stage did not run"*; `docs/analysis-note/main_*.pdf` is gitignored at `.gitignore:12`. With `--source-only` it returns **exit 0**, `RESULT :: PASS`. A session that happens to have built the note locally reports green; a clean checkout of the same sha reports red. Commit `472c1e64` cites *"check_dead_containment exit 0 (RESULT :: PASS)"* alongside *"Each status read directly, none through a pipe"* — the status was read correctly, but the **tree was not named**, which is precisely what row 60's own CHECK requires. **CHECK:** cite this gate as `--source-only exit 0`, or as `exit 0 with PDFs built`, and never as a bare `exit 0`.
