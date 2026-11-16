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

## The director's rulings on the pass-B flags, 2026-11-15 (rows E3, E4)

Base: this file at `8b4758e46`. Both go in Joseph's batch as ES wording approved by the director.

| id | base line | old text | new text | source |
|---|---|---|---|---|
| E3 | ES :38, Table 1's $C_Z$ row | "Technical diagnostic of estimator-seed sensitivity only." | "Used only for the estimator-seed sensitivity diagnostic (§eavailw-adopted), whose seed-sensitivity measurements use two companion covariances, and for the attribution of its per-source decomposition (§uq-combine)." The restrictions that follow are unchanged. Pass 1 of the read failed a first wording that also listed "the scale of the seed shifts of central values (§eavailw-map)": sec_5d.tex:344 says items 1, 2 and 4 (item 4 is the seed-shift comparison that sec_eavailw.tex:118 points to) use the two companion covariances, and only item 3 describes this file. | ruling 1: the body's uses, sec_5d.tex:294, :344–360, sec_systematics.tex:160 |
| E4 | ES :6 | "Superseded configurations and changed tests that bear on the released results are listed in App.~…, with what had been seen when each change was made." | "Superseded configurations, changed tests and consequential choices made after results were seen that bear on the released results are listed in App.~…, with what had been seen when each was made, where the note states it." (the qualifier matches App. I's opening, I1 of history-cuts/app_devhistory.md) | ruling 3; app_devhistory.tex:8 |

## Meaning read

See sec_validation.md, rows V3–V9: one read covers E1, E2, V3–V9 and §3's C7 (reads/es-v3-pass*.txt).

**Meaning read of the rulings (codex-school gpt-6.1-sol, high, read-only; rows E3, E4, T9, I10, I11 together, records attached):** pass 1 FAIL on E3 only (its first wording listed the seed-shift scale, which sec_5d.tex:344 assigns to the companion covariances); pass 2, E3 revised, OVERALL PASS with no FAILs and no NEEDED item lost. reads/rulings-pass1.txt, reads/rulings-pass2.txt.

## Cutdown, 2026-11-16 (lane/note-cutdown-20261116)

**Under** Joseph's go for the cutdown (DECISION-20261116-joseph-paper-batch.md at main `99aefd3f0`, sixth answer,
items 29, 33 and 34: a methods study; §12 reduced to one paragraph with its caveat; the note is cut down now under the
2026-11-13 history rule) and the editor's brief of the same day.

**The rule:** as at the head of this file.

**Base:** `sec_execsummary.tex` and `sec_summary.tex` at `8342963c16d74bc10d740e5637d602300557e53a`. Line numbers are
the base's. Every removed passage stays in the commit history at that sha and line, which is its ledger home.

| id | base line | words cut | disposition | old text | new text | home of the content | why not NEEDED |
|---|---|---|---|---|---|---|---|
| K1 | sec_execsummary.tex:82 | 20 | shortened | "A methodological finding concerns the standard covariance, which sums single-source systematic matrices, each with all other sources nominal, and so omits nonlinear cross-source response terms. No two-dimensional comparison of a joint throw with the block sum is reported. Where a five-dimensional construction stores the joint mean shift separately, that norm is not quoted (\S…uq-combine)." | "The standard covariance sums single-source systematic matrices, each with all other sources nominal, and so omits nonlinear cross-source response terms. No two-dimensional comparison of a joint throw with the block sum is reported (\S…uq-combine)." | The dropped sentence's content prints at sec_systematics.tex §4.5 ("the stored mean-shift norm is not quoted"); the dropped words "A methodological finding concerns" at 8342963c1:sec_execsummary.tex:82 | Both disclosures are kept: what the block sum omits, and that no two-dimensional comparison is reported. The opening words announced a finding the paragraph does not report. The five-dimensional norm sentence states that a number is not quoted; §4.5 says the same where the construction is described. |
| K2 | sec_execsummary.tex:84 | 56 | cut to ledger | "A preliminary extended-fiducial study removes the truth-muon cuts and keeps the fiducial volume and MINOS-based selection. It puts about 6% of the scalar 2D rate in newly acceptance-supported cells (part of tier 1, an acceptance-supported central estimate rather than a qualified measurement) and about 28% in low- or zero-efficiency cells (tier 2, extrapolated from the prior; \S…fps)." | cut | Table `tab:result-status`, row "Extended-fiducial study" (same file: the cuts removed, the selection kept, tier 1 about 6% and tier 2 about 28%, "preliminary exploratory study … with no finalized cross section"); sec_fps.tex (tier definitions; "Neither tier is a completed measurement"); 8342963c1:sec_execsummary.tex:84 | The paragraph repeats the status table's row. Decision item 33 reduces §12 itself to one paragraph, and that paragraph keeps the tier definitions and their status. |
