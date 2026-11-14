# History restructure, the executive summary (sec_execsummary.tex) and §13 (sec_summary.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13, and the
director's ruling (A) of 2026-11-14 (recorded in sec_5d.md). The ES wording below is the director's approved text of
2026-11-14.

**Referee:** for §13 it gave "5–10%, Compress. Summarize conclusions and unresolved limits; avoid repeating adoption
history."

**Base:** `docs/analysis-note/sec_execsummary.tex` and `sec_summary.tex` at `4a997b89d`. Line numbers are the base's.

## The changes

| id | base line | old text | new text | ledger home |
|---|---|---|---|---|
| E1 | ES :6 | "It holds the full development history and diagnostics to which the paper and Supplement point." | "It holds the diagnostics to which the paper and Supplement point. Superseded configurations and changed tests that bear on the released results are listed in App.~\ref{app:devhistory}, with what had been seen when each change was made." The director dropped a proposed last clause pointing to the repository's records: NoteRecords2026 is not posted (UNRELEASED-SUPPORT.md lists it). Neither the paper nor the Supplement says the note holds the "full development history" (`git grep -i 'development history'` on draft/methods-short-20261109 finds none). | 4a997b89dcsummary.tex:6 |
| E2 | ES :34 | "the injected-$\Eavail$ closure is configuration~(a), has no predeclared threshold, and does not extend to (e)" | "… has no threshold specified before it ran, …" ("predeclared" spelled out; no new timing) | 4a997b89dcsummary.tex:34 |

**§13: no change.** It summarizes the conclusions and limits. Its one timing clause, "fixed before any production
pseudo-experiment or observed statistic" (:10), names its object, and it does not repeat adoption history. Its release
paragraph (:38) belongs to App. G's pass.

**Left for Joseph, by the director's ruling:** main_note.tex:135, the AI-use statement's "predeclared criteria". It is
Joseph's disclosure wording.

**Numbers and keys:** `numdiff.py` on the base and new ES: none removed or added; value keys and macros unchanged.

## Meaning read

See sec_validation.md, rows V3–V9: one read covers E1, E2, V3–V9 and §3's C7 (reads/es-v3-pass*.txt).
